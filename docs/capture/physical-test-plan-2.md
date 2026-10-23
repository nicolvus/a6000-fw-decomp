# Plan de pruebas físicas 2 (P13–P20) — lecturas nuevas a partir de S329–S343

Estado: **ninguna se ha ejecutado**. Complementa [physical-test-plan.md](physical-test-plan.md) (P1–P8) y las propuestas P9–P12 de [S402](s402-physical-test-mapping.md). Todas son **de solo lectura** salvo P21 (opcional, riesgo medio-alto). Reglas comunes: las de `physical-test-plan.md` §0 (backup NVRAM antes, solo RAM, disparo remoto, parar ante reinicio).

Conversión usada en S64: dirección virtual del firmware `0x43xxxxxx` = física `0x83xxxxxx` (`0x43edf684` → `0x83edf684`). Los registros MMIO ya son direcciones físicas.

**Ya hecho antes (no repetir):** S64 forzó el campo Silent `0x83edf8bc` (`0→1→0`) y comparó 4 MB de RAM; `camera_drivemode_override.py` ya escribió drive mode `0x37`/`0x38`.

## P0 — Preparación (obligatoria, ~20 min)

1. `python3 scripts/senser_backup_dump.py`; verificar el volcado y guardarlo en `analysis/camera-dumps/`.
2. **Comprobar que `senser_readmem.py` llega a MMIO:** leer primero 4 bytes de una RAM conocida (`0x83e9bd50:4`), luego 4 bytes de `0xfc02a00c`. Si la segunda lectura cuelga o reinicia: **parar**, restaurar, y tachar P13–P15 (no es un fallo de la cámara, es un límite de la herramienta).
3. Línea base: `done <bytes>` de un disparo remoto en mecánico (`tools/remote-shutter/`).

## Pruebas (de menor a mayor riesgo)

### P20 — Registro de la cámara durante un ciclo de disparo
- **Objetivo:** ver si la cámara emite en `dmesg`/logs las trazas de los módulos decodificados (S181–S200, S500–S617: `[CAM_FUNC_MGR]`, `[IMAGING_CAP]`, `[SDF]`…).
- **Método:** por telnet, `dmesg` y los logs que existan, antes/durante/después de 3 disparos remotos y de un cambio de menú.
- **Resultado útil:** si las trazas salen, se tiene una vista temporal del flujo sin tocar nada. Si no salen, queda descartado como fuente.
- **Riesgo:** bajo.

### P18 — Gates del estado IMX210 en ejecución
- **Pregunta (S300):** `+3` (`[obj+3]&2`) y `+6` (`[obj+6]&0x20`) no tienen escritor estático. ¿Cambian en ejecución?
- **Método:** leer `0x83f72d00:0x20` (objeto `0x43f72d02`) en reposo, en live view, con medio pulsado y durante un disparo remoto; repetir con tipo de obturador/drive distintos.
- **Éxito:** algún bit de `+3`/`+6` cambia ⇒ hay productor en ejecución (DMA, otro módulo). **Si no cambia:** refuerza que son constantes de configuración.
- **Riesgo:** bajo.

### P13 — Bloque DFE/CISIF en ejecución
- **Pregunta (S338/S341):** el registro `0xfc02a00c` recibe la máscara u16 que sale de T1/T2/T3. ¿Qué valor tiene y cuándo cambia?
- **Método:** leer `0xfc02a000:0x20` en reposo, live view, medio pulsado, durante el disparo; anotar el valor por estado.
- **Comparar con S341:** la A6000 usa solo máscaras `0xf00`/`0xfff` (sin ceros). Si se ve una máscara distinta, el modelo está incompleto.
- **Riesgo:** bajo-medio (lectura de MMIO; ver P0.2).

### P14 — Qué mide cada canal `w0`
- **Pregunta (S340):** la función de 6 casos lee un registro por canal; el significado está NO_VERIFICADO.
- **Método:** leer `+0x30` o `+0x24` (según el caso, ver S340) de `0xf3122300`, `0xf3122200`, `0xf3123300`, `0xf3123200`, `0xfc0a3100`, `0xfc0a4100` en reposo, live view y disparo. Una lectura por estado y canal.
- **Éxito:** un canal que cambie con el disparo o con el live view indica su función (contador, estado, estado de lectura).
- **Riesgo:** bajo-medio (MMIO).

### P15 — Interfaz `0xf292b000..8`
- **Pregunta (S339):** identidad NO_VERIFICADA; 3 registros de 12 bits.
- **Método:** solo leer `+0` (el único de lectura según S339) en los mismos estados que P13. Nada de escribir `+4`/`+8`.
- **Riesgo:** medio (bloque no documentado). Hacerla solo si P13 va limpia.

### P16 — Segunda matriz: ¿tiene productor en ejecución?
- **Pregunta (S328):** `0x43e80160` (A6000) está a cero y sin escritor estático; el segundo bucle no ejecuta salvo productor en ejecución.
- **Método:** leer `0x83e80160:0x40` al arrancar, tras cambiar drive mode, tras disparar y tras entrar/salir de menú.
- **Éxito:** se llena ⇒ hay productor; sigue a cero ⇒ confirma que no ejecuta.
- **Riesgo:** bajo (RAM).

### P19 — Latencia y ráfaga con y sin EFCS (criterio objetivo, sin riesgo)
- **Método:** con disparo remoto, medir tiempo entre petición y `done <bytes>` y fotogramas por segundo en ráfaga, con obturador mecánico y con EFCS (menú). 10 repeticiones cada una.
- **Valor:** diferencia medible sin interpretar sonido; complementa P7 y P8.
- **Riesgo:** bajo.

### P17 — Línea base de P7 antes de nada (imagen)
- **Método:** hélice/ventilador y LED con flicker, 1/250, 1/1000, 1/4000, mecánico y EFCS, **antes** de cualquier escritura. Guardar con hash.
- **Valor:** es el criterio con el que se juzga cualquier prueba posterior (P2/P3/P8).

### P21 — (Opcional, riesgo medio-alto) Modo fuera del vocabulario de la A6000
- **Pregunta (S324/S333):** el setter de la A6000 rechaza modos `> 0x47` (`0x4e`/`0x4f` no existen en su vocabulario de 13 códigos).
- **Método:** `camera_drivemode_override.py` con `0x4c` y `0x4e`, un disparo cada uno, **solo si P0–P19 fueron limpias**.
- **Esperado:** rechazo sin efecto. Un efecto visible (sonido o imagen distinta) sería un hallazgo grande.
- **Riesgo:** medio-alto (toca el pipeline de captura; antecedente S64). Parar ante cualquier reinicio y restaurar backup.

## Orden para mañana

`P0 → P20 → P18 → P16 → P13 → P14 → P15 → P17 → P19 → P21 (opcional)`

Lecturas primero, MMIO después y solo si P0.2 fue limpia. Cada prueba se detiene si la anterior no es limpia. Tiempo orientativo: 3–4 h sin P21.

## Qué cambiaría cada resultado

| Resultado | Consecuencia |
|---|---|
| P18: `+3`/`+6` cambian | Hay productor en ejecución; reabre la búsqueda de escritores (B). |
| P13: la máscara real difiere de `0xf00`/`0xfff` | El modelo de S341 está incompleto; corregir. |
| P14/P15: un canal responde al disparo | Se identifica su función (sin identidad hasta hoy). |
| P16: se llena | Hay productor en ejecución de la segunda matriz. |
| P19/P17: diferencia EFCS reproducible | Criterio objetivo para P8; sin diferencia, EFCS no cambia el comportamiento medible. |
| P21: efecto con `0x4e` | S51 pasa a revisión. Rechazo: confirma el límite de código. |

## Registro

Un apartado fechado por prueba en un informe nuevo `docs/capture/` (`physical-test-results-<fecha>.md`) con valores leídos, hash de volcados y estado de la cámara; actualizar `knowledge/CURRENT.md`; commit y push.
