# S607 — `[CAM_CMD]`: módulo de traza de comandos de cámara exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**6 trazas · 6 sitios (regla PIC estricta) · ~3 funciones emisoras · 0 muertas.** Detalle + datos: [JSON](../../analysis/s607_cam_cmd/cam_cmd.json).

## Qué es

`[CAM_CMD]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 6 mensajes del **gestor de comandos de cámara (Capcon / Camera::Function)** que procesa la cola de eventos/comandos, transiciones de estado, path selector y mode sequencer. La sigla **SÍ tiene base textual**: `CAM` → cámara; `CMD` → **C**o**M**man**D** (comando). El módulo subyacente es `Capcon` / `CapconExec` / `Camera::Function::CapconEventQueue` / `ExecHandlerBase` (ver RTTI en A7S).

## Las 6 trazas (vaddr → texto corto)

```
0x43caeb10 [CAM_CMD]: Warning! Now rocessing... req[%d]
0x43caeb3d [CAM_CMD]: Error! Can't Transfer Request cur_state[%d] req[%d]
0x43caeb7d [CAM_CMD]: Error! s_path_selector SetupTable cur_state[%d] req[%d]
0x43caebc1 [CAM_CMD]: Error! s_request is NULL!
0x43caebe6 [CAM_CMD]: Error! s_mode_sequencer SetupTable [%d]->[%d]
0x43caec20 [CAM_CMD]: Error! CheckReturnAllModlueResponse
```

## Hallazgos con dirección

- **Función principal**: máquina de estados de comandos (`cur_state`, `req`) con validaciones de transferencia, path selector y mode sequencer.
- **Variables de estado**: `s_path_selector` (tabla de setup por estado), `s_mode_sequencer` (tabla de setup por transición), `s_request` (puntero a petición actual).
- **Path selector**: `SetupTable` indexado por `cur_state` y `req`; error si configuración inválida.
- **Mode sequencer**: `SetupTable` para transiciones `[%d]->[%d]`; error si configuración inválida.
- **Validaciones**: `s_request` NULL check; `CheckReturnAllModlueResponse` (typo: "Modlue" → "Module").
- **Logger dual (patrón S177/S179/S603/S604/S605/S606)**: la fw3.21 **duplica** la traza: nueva con prefijo `[CAM_CMD]: ` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`. Ejemplo: en offset `+0x2c` carga string con prefijo y en `+0x32` llama `bl 0x43902718` con string original.
- **Longitud del prefijo**: 11 B (`[CAM_CMD]: `) → fija (igual que S605/S606).
- **Typo**: "Modlue" en "Module" — presente en los tres firmware.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAM_CMD]` | **6** | **0** | **0** |
| núcleo sin prefijo (`Warning! Now rocessing...`, `Error! Can't Transfer...`, etc.) | 0/6 como literal autónomo | **6/6** (sin prefijo) | **6/6** (sin prefijo) |
| prefijo alternativo A7S (`[CAMERA_MAIN_FC]`, `[CAM_UTIL]`, etc.) | 0 | **otros módulos** | **otros módulos** |
| código equivalente (Capcon, s_path_selector, s_mode_sequencer) | `0x43cbdxxx`… | **sí** | **sí** |

→ **Cambio de *logging*, no de código.** El gestor de comandos Capcon **existe igual** en los tres firmware (mismas 6 cadenas núcleo, mismas variables `s_path_selector`, `s_mode_sequencer`, `s_request`, mismo typo "Modlue"). Lo propio de la fw3.21 de la A6000 son **las 6 trazas con prefijo `[CAM_CMD]: `** y la **duplicación** con logger global `0x43902718`. En A7S/A6300 las 6 cadenas existen **sin prefijo** (inician directamente con "Warning!" / "Error!").

**Longitud del prefijo fija:** 11 B (`[CAM_CMD]: `) → no variable.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **cola de comandos y transiciones de estado de captura**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 6/6 cadenas `[CAM_CMD]: ` confirmadas en `0x43caeb10`–`0x43caec20`.
- 6/6 núcleos idénticos en A7S fw3.20 (`0x770e9b`–`0x770f74`) y A6300 fw2.01 (mismos offsets relativos).
- 0/0 en A7S y A6300 para token `[CAM_CMD]`.
- Scripts: `analysis/s607_cam_cmd/` (pendiente) · Tests: `tests/test_s607_cam_cmd.py`.
