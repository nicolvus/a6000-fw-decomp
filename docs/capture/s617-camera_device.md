# S617 — `[CAMERA_DEVICE][DET_DIR]`: módulo de timers de dispositivo de cámara exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**3 trazas · 3 sitios (regla PIC estricta) · ~1 función emisora · 0 muertas.** Detalle + datos: [JSON](../../analysis/s617_camera_device/camera_device.json).

## Qué es

`[CAMERA_DEVICE][DET_DIR]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 3 mensajes del **módulo de dispositivo de cámara (CAMERA_DEVICE) con sub-módulo de directorio de detección (DET_DIR)** que valida operaciones de timer OSAL (alloc/set/free). La sigla **SÍ tiene base textual**: `CAMERA_DEVICE` → dispositivo de cámara; `DET_DIR` → **DET**ection **DIR**ectory / **DET**ector **DIR**ectory (directorio de detección); `osal_*_timer` → **OSAL** (Operating System Abstraction Layer) timer API.

## Las 3 trazas (vaddr → texto corto)

```
0x43cf724e [CAMERA_DEVICE][DET_DIR][osal_alloc_timer] %x
0x43cf727c [CAMERA_DEVICE][DET_DIR][osal_set_timer] %x
0x43cf72a8 [CAMERA_DEVICE][DET_DIR][osal_free_timer] %x
```

## Hallazgos con dirección

- **Triple prefijo jerárquico**: `[CAMERA_DEVICE][DET_DIR]` — módulo padre `CAMERA_DEVICE` + sub-módulo `DET_DIR`. Longitud total: 24 B (`[CAMERA_DEVICE][DET_DIR]`).
- **API de timers OSAL**: 3 operaciones básicas — `alloc` (asignar), `set` (configurar), `free` (liberar). Cada una emite el código de retorno/error en hex (`%x`).
- **Logger dual (patrón S177/S179/S603–S616)**: la fw3.21 **duplica** la traza: nueva con prefijo `[CAMERA_DEVICE][DET_DIR]` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Estructura CAMERA_DEVICE**: en fw3.21 aparece como módulo con sub-módulo `DET_DIR` para gestión de timers de detección.
- **Prefijo fijo**: 24 B (`[CAMERA_DEVICE][DET_DIR]`) → no variable.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAMERA_DEVICE][DET_DIR]` | **3** | **0** | **0** |
| núcleos `osal_*_timer` | 3/3 con prefijo `[CAMERA_DEVICE][DET_DIR]` | **3** (prefijos `Spinal`/`CapMgr`/`TRK`) | **3** (prefijos `CapMgr`/`TRK`) |
| código equivalente (`osal_*_timer`) | `0x43cf724e`… | **sí** | **sí** |

→ **Cambio de *logging*, no de código.** La API de timers OSAL para detección **existe igual** en los tres firmware (mismas 3 funciones `osal_alloc/set/free_timer`). Lo propio de la fw3.21 de la A6000 son **las 3 trazas con prefijo `[CAMERA_DEVICE][DET_DIR]`** y la **duplicación** con logger global `0x43902718`. A7S usa prefijos `Spinal`/`CapMgr`/`TRK`; A6300 usa `CapMgr`/`TRK`.

**Longitud del prefijo jerárquico fija:** 24 B (`[CAMERA_DEVICE][DET_DIR]`) → no variable.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **timers OSAL para directorio de detección**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 3/3 cadenas `[CAMERA_DEVICE][DET_DIR]` confirmadas en `0x43cf724e`–`0x43cf72a8`.
- 3/3 núcleos `osal_*_timer` idénticos en A7S (prefijos `Spinal`/`CapMgr`/`TRK`) y A6300 (prefijos `CapMgr`/`TRK`).
- 0/0 en A7S y A6300 para token `[CAMERA_DEVICE][DET_DIR]`.
- Scripts: `analysis/s617_camera_device/` (pendiente) · Tests: `tests/test_s617_camera_device.py`.
