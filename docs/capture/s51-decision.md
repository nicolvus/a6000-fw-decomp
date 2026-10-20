# S51 — decisión SÍ/NO sobre exposición totalmente electrónica

19-10-2026. Plan y criterios prerregistrados: [`analysis/s51/PLAN.md`](../../analysis/s51/PLAN.md).
Claude (Opus 5.5) hizo T1; Codex (gpt-5.6-terra, esfuerzo medio) hizo T2 y T3: [informe Codex](s51-codex-t2-t3.md).
Todo es estático: no se ejecutó, modificó ni flasheó firmware, y no se usó la cámara.

## Respuestas

| | Pregunta | Respuesta | Tipo de NO |
|---|---|---|---|
| **A** | ¿Hay una ruta de exposición totalmente electrónica demostrada? | **NO** | falta de demostración |
| **B** | ¿Hay evidencia suficiente para diseñar ya un parche funcional y justificable? | **NO** | falta de demostración |
| **C** | ¿Está demostrado que el hardware lo hace imposible? | **NO** | no hay prueba de imposibilidad |

**A — evidencia.**
- La configuración «electrónica» (`CURTAINMODE 0xce` → `C+0x94/95` → modo `0..7`) no gobierna el sensor (T1 = NO, abajo).
- En la ruta de foto fija identificada, el cierre de la 2ª cortina no tiene ninguna guarda que dependa de un flag configurable (T3 = NO, Codex: `0x43b5e2b0`→`0x4398f9a4`, `1<<bit` en `0xf2910048+banco*0x100`; guardas `captura+0x74f` y `43ae7648`).
- No se ha identificado un fin electrónico de exposición (T2: no se conoce el significado de ID1/100/101).

**B — evidencia.** Un parche tendría que suprimir el evento de 2ª cortina y apoyarse en un fin de integración por
filas cuyo registro y efecto no conocemos. No hay base para elegir qué escribir ni para predecir el resultado (imagen
quemada o sobreexpuesta, error de secuencia o bloqueo). Diseñarlo ahora sería una conjetura, no un parche justificable.

**C — evidencia.** Nada de lo analizado excluye un fin electrónico por filas en el IMX210. La lectura electrónica por
filas existe (LiveView/vídeo, `SetRead` con tabla por drive_mode). El inicio electrónico existe como función del
producto (EFCS); esto es documentación del producto, no evidencia estática de esta sesión. Que no haya obturador
global no impide un obturador rodante electrónico.

## T1 (Claude) — ¿el modo `0..7` / B / G llega a `ModeRsvParam`/`C_Imager`? **NO** (VERIFICADO)

| Paso | Evidencia | Estado |
|---|---|---|
| Lectores de `[0x43eefb1c+0x60]` | 40 referencias PIC, todas en `0x43841bf8..0x43842440`; fuera del selector `0x43842158` solo hay un getter, `0x43842404` | VERIFICADO (índice PIC; GOT 0) |
| Getter | Un único llamador, `0x4383f784`, que copia el modo a `0x43eedecc` | VERIFICADO (bl directo; sin punteros literales a `0x43842405`) |
| Lectores de `0x43eedecc` | `0x4384031c`: si modo 1, o 3 con flag, emite eventos (`0x43aef28a`→`0x437b0390`, mensaje tipo 3/0x22). `0x43841070`: escribe el registro `0x4383fb6c` (`+0x6d`=modo; si modo==5, `+0x6e/+0x70` con clamp `0x43aebe32`) y `cap+0x3b` | VERIFICADO (LLVM + REA) |
| Consumidores del registro | Búferes `0x43ea5b4c`/`0x43eee770`. Nadie lee `+0x6d` en las 7 funciones que usan el búfer. `+0x6e/+0x70` solo los lee el serializador `0x438e2b98` (8 bytes big-endian, mismo patrón que los exportadores de estado de S50). `0x437b0810` copia otros campos | VERIFICADO |
| Llamadas al imager | `SetMode=0x436d62e4`, `SetExposure=0x436d6320`, `SetRead=0x436d6398` (identificadas por sus cadenas de log). La captura los llama en `0x438c79bc/79fc/7a40` | VERIFICADO |
| Origen de `ModeRsvParam` | `0x43795a60(cap+0x4d0, cap+0x4d4, cap+0x4d5)`. `cap+0x4d0` es el **drive_mode** del imager | VERIFICADO |
| Origen del drive_mode | Lo fija `0x437f7ff4` a partir de `cap+0x4b70`, `cap+0x1e0`, `cap+0x6c8`, `0x43affd86` (`cap+0x75c`), `0x43a12c64` y un override de depuración `[global+0x86]`. `0x437f7ef6` lo cambia de `0x0b→0x37` y `0x35→0x38` si `cap+0x73a==0`; `cap+0x73a` sale de `+0x2ae/2b0/2b4` del bloque `cap+0x1198`, que `0x43841070` no escribe | VERIFICADO (barrido de stores + REA) |

Conclusión: el modo `0..7` no alcanza ningún argumento de `SetMode/SetExposure/SetRead`. Se descarta
`CURTAINMODE`/`C+0x94` como base de un parche. Límite: no se siguieron los receptores de los mensajes que emite
`0x437b0390`, y el índice PIC es heurístico.

Dato colateral (sin semántica): el override `[global+0x86]` permite forzar cualquier drive_mode en la captura. Es la
palanca de software que existe sobre el modo del sensor, pero se desconoce qué significa cada drive_mode
(`0x0b,0x0c,0x17,0x2f,0x35,0x37,0x38,0x01`).

## Rutas descartadas
`CURTAINMODE 0xce`/`C+0x94/95`/modo `0..7` como control del sensor (T1). `0xb6` (S50). Bypass `+74f` (S50, que T3
reafirma). Un flag de serie que omita la 2ª cortina en foto fija (T3). Asignar significado a ID1/100/101 por analogía (T2).

## Bloqueadores concretos
1. **Mapa de registros IMX210** que relacione ID1/ID100/ID101 (y los drive_mode) con reset, transferencia o lectura
   por filas. No hay documento público legítimo; Sony lo entrega bajo registro/NDA.
2. Como alternativa, una **traza pasiva** de la interfaz serie de control del sensor en una A6000 propia: capturar las
   tramas en vídeo, foto con EFCS activado y foto con EFCS desactivado, y comparar qué IDs/bytes cambian. Requiere
   cámara, abrirla y la autorización del propietario; no requiere modificar firmware.
3. Enlace banco/bit `0xf2910048` → P4E (`2ND_CURTAIN_MG`): PARCIAL. No cambia la decisión.

## Decisión operativa
**Detener el desarrollo del parche** y no abrir otra sesión estática larga: ninguna prueba estática accesible puede
cambiar A o B, porque lo que falta es la semántica eléctrica del sensor. La única prueba que puede cambiar la
decisión es la **traza pasiva autorizada** (bloqueador 2) o el datasheet (bloqueador 1). Retomar solo con uno de los dos.

## Recursos e integridad
- Claude: unos 45 min de trabajo. Codex: unos 6 min de reloj (su informe dice «~55 min»; no cuadra con el log).
- Una sola sesión REA compartida: arranque en frío de 485 s y pico de 2,5 GB de RSS. Codex no llegó a usarla
  (terminó antes de que estuviera lista) y la cerró Claude. Ghidra histórico no se usó.
- `sha256sum -c analysis/s50/shared/sha256-initial.txt`: 1490/1490 OK.
