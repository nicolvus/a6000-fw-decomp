# Plan de pruebas físicas (pendientes) — obturador electrónico A6000

Estado: **ninguna de estas pruebas se ha ejecutado**. Cada una requiere autorización expresa del usuario en el momento de lanzarla. Se redacta el 21-10-2026 a partir de S64, S70 y S71 (`analysis/s101_shutter_type/block238/`, `analysis/s101_shutter_type/pending/report.md`). Conclusión vigente que estas pruebas podrían cambiar: **S51 (no parchear)**; A7S es la referencia con Silent.

## 0. Reglas comunes (obligatorias)

| Regla | Detalle |
|---|---|
| Backup previo | `python3 scripts/senser_backup_dump.py` y verificar el volcado antes de tocar RAM de captura. Guardar bajo `analysis/camera-dumps/` (binarios fuera de Git; solo README y SHA256SUMS). |
| Recuperación probada | `scripts/senser_backup_restore.py` por service mode. El reflasheo del mismo fw 3.21 se rechaza (`Invalid version`), así que **no hay vuelta atrás por firmware**. |
| Prohibido | `CameraSequence`, callbacks de obturador, escrituras persistentes (NVRAM/flash), instalar APK sin avisar (escribe en `/data`), reflashear. |
| Solo RAM | Escrituras por `dd`/`/dev/mem` en bucle de 20 ms con restauración al final (`scripts/camera_bisect_fields.py`, `camera_shutter_matrix.py`). Esperar a que acabe el bucle antes de restaurar. |
| Disparo | Remoto, por quien ejecuta la prueba: app `tools/remote-shutter/` (`CameraEx`, HTTP `:8080`), cámara en `192.168.1.29` (telnet/adb). No pedir al usuario que dispare salvo que no exista el método. |
| Criterio objetivo | No basta el oído. Además del sonido, registrar: tipo leído de RAM, `done <bytes>` del disparo, y la prueba de imagen de P7. |
| Parada | Reinicio, pérdida de conexión, objetivo sin arrancar u obturador atascado ⇒ **parar**, restaurar backup, anotar en `docs/capture/` y no repetir sin plan nuevo. Antecedente: S64 (2026-10-20) dejó la cámara sin arrancar tras `CameraSequence`. |
| Registro | Un apartado fechado por prueba en un informe `docs/capture/` nuevo; actualizar `knowledge/CURRENT.md`; commit y push. |

## 1. Pruebas, de menos a más riesgo

### P1 — Observación pasiva de `G+0x808` (sin escribir)

- **Objetivo:** saber qué ajuste de la cámara mueve `([G+0x808]&7)`, el selector del tipo de mecanismo (`0x4379316a`).
- **Método:** leer `0x83e9bd50` (`G+0x808`, `G=0x83e9b548`) y `0x83e9bccc` (`G+0x784`, tipo) cada ~200 ms mientras se recorre el menú: tipo de obturador (mecánico/EFCS), modo de disparo, modo silencioso si lo hubiera, Drive. Usar `scripts/senser_readmem.py`/telnet; no escribir nada.
- **Esperado:** `G+0x808` = 0 en reposo (valor de la imagen). Un cambio indica el ajuste que lo gobierna.
- **Riesgo:** bajo. **Prerrequisito de P2–P4.**

### P2 — Forzar `G+0x808` = 1 sin disparar

- **Método:** `BASE=0x83e9b548 scripts/camera_bisect_fields.py 1 0x808` sin `SHOOT`, o escritura directa de `1` en `0x83e9bd50`; leer `0x83e9bccc`.
- **Hipótesis (S71, inferencia):** tipo pasa de 0 a **2** (`v=1`); con `v=2..6` el tipo es **1**; el resto, **0**.
- **Éxito:** se observa el cambio de tipo. **Fallo informativo:** no cambia ⇒ el selector `0x4379316a` no se ejecuta fuera de la ruta de captura o la instantánea se regenera (anotar cuándo).
- **Riesgo:** bajo-medio (RAM viva, S64 forzó 10 campos vecinos; una combinación provocó un reinicio no reproducido).

### P3 — Forzar `G+0x808` = 1 con disparo remoto

- **Método:** igual que P2 con `SHOOT=1`, un disparo; después valores 2, 3 y 7 (cada uno en disparo aparte).
- **Medir:** `done <bytes>`, tipo leído antes/después, P7 sobre la imagen.
- **Riesgo:** medio (toca la ruta de captura). Parar ante cualquier reinicio.

### P4 — Forzar el tipo directamente (`G+0x784`)

- **Método:** escribir `2` en `0x83e9bccc` durante un disparo remoto, con y sin P3.
- **Pregunta:** ¿Darwin A6000 acepta tipo 2 (valida 1/2/3, S52) y el paquete CAIF cambia? Comprobar si `pkt[+0x12]` mantiene el bit `0x20` (A6000 lo descarta, S53).
- **Riesgo:** medio-alto; solo tras P2/P3 sin incidencias.

### P5 — Traza pasiva en el bus (analizador lógico)

- **Objetivo:** confirmar que el mensaje mss-async hacia Darwin y las señales de cortina se comportan como describe S53–S55.
- **Método (solo lectura):** analizador lógico en `GPIO_9`/P4C (CN4900) y `MSS_SO_DWN` durante (a) foto mecánica y (b) foto con EFCS activado. Medir ID del mensaje, polaridad, flanco y relación con `P4C←0`.
- **Éxito:** distinguir si el host cambia algo en EFCS que no cambia en mecánico; es el dato que falta para el punto «consumidor de P4C».
- **Riesgo:** bajo para el equipo, **requiere abrir la cámara**: valorarlo aparte.

### P6 — ¿Puede el service shell leer el MCU Darwin o su bootloader?

- **Objetivo:** el bootloader `0x0–0x41ff` del FM3 no está en el firmware (S70). Ver si algún comando de lectura del shell de servicio de S62 (`serviceshell`/`updatershell`: `RMEM`, `PULL`, `BK*`) llega a Darwin.
- **Método:** empezar solo por comandos de lectura documentados; no usar `PUSH`/`BK` de escritura. Registrar qué espacios de direcciones responden.
- **Riesgo:** medio (service mode); backup NVRAM previo obligatorio.

### P7 — Prueba objetiva de obturación electrónica (imagen)

- **Objetivo:** sustituir el oído por un criterio medible.
- **Método:** fotografiar (a) una hélice/ventilador girando o un patrón de barras en movimiento y (b) una luz LED con flicker a 1/1000 s o más rápido, en mecánico y en cada ajuste probado. Un obturador de cortina con exposición completa por sensor produce *rolling shutter* (inclinación) o bandas de flicker distintas del obturador mecánico a velocidades altas.
- **Éxito:** diferencia reproducible entre configuraciones. Guardar RAW/JPEG con nombre y hash; los JPEG no traen maker note útil (S64).

### P8 — `+0x210` = 1 («disparo múltiple»)

- **Antecedente:** S64: 4/4 disparos con sonido múltiple y un solo JPEG por petición.
- **Método:** repetir contando fotogramas en la tarjeta y con P7; comparar con el ajuste EFCS del menú (alternar y diferenciar el bloque de ajustes por volcado).
- **Pregunta:** ¿es el EFCS (cortina delantera electrónica) o una ráfaga? Resuelve el significado de `+0x210`.

## 2. Orden recomendado

`P0 (backup + recuperación)` → `P1` → `P2` → `P7` (línea base) → `P3` → `P8` → `P4` → `P6` → `P5`.

Cada paso se detiene si el anterior no es limpio. P1, P2 y P7 son los de mayor información por riesgo.

## 3. Qué cambiaría cada resultado

| Resultado | Consecuencia |
|---|---|
| P2/P3: el tipo pasa a 2 y el obturador cambia (P7) | Abre vía real: el interruptor está en `G+0x808`; faltaría el origen del ajuste. S51 pasaría a revisión. |
| P2: el tipo cambia, el obturador no | El tipo 2 en A6000 no basta (coherente con S53: Darwin descarta el bit `0x20`). La limitación sigue en el MCU. |
| P2: el tipo no cambia | `0x4379316a` no es la ruta de captura real o la instantánea se regenera; revisar `0x43792a0c`. |
| P4: reinicio | Documentar, restaurar, descartar el tipo forzado directo. |
| P5/P6: Darwin no recibe el bit | Confirma que el límite es del MCU; sin bootloader no se puede cerrar más. |

## 4. Fuentes

`docs/capture/s64-silent-ram-nvram-test.md` (procedimientos y resultados previos), `docs/capture/rea-tema3-cortinas-darwin.md` (traza pasiva), `docs/capture/s62-pmca-injection.md` (service shell), `analysis/s101_shutter_type/block238/block238_consumers.md`, `analysis/s101_shutter_type/pending/report.md`, scripts `scripts/camera_*.py` y `scripts/senser_*.py`, `tools/remote-shutter/`.
