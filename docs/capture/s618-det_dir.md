# S618 — `[DET_DIR]`: submódulo de directorio de detección (idéntico a CAMERA_DEVICE)

**3 trazas · 3 sitios (regla PIC estricta) · 0 muertas.** Detalle + datos: `analysis/s618_det_dir/` (pendiente) / `.json` (pendiente).

## Qué es

`[DET_DIR]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a mensajes del **directorio de detección (DETection DIRectory)**. Sin embargo, **no existen trazas independientes con prefijo `[DET_DIR]: `** — las 3 trazas listadas en el censo son **idénticas** a las de `[CAMERA_DEVICE][DET_DIR]` (S617), ya que DET_DIR es un sub-módulo de CAMERA_DEVICE.

## Las 3 trazas (idénticas a S617)

```
0x43cf72a6 [CAMERA_DEVICE][DET_DIR][osal_alloc_timer] %x
0x43cf72d4 [CAMERA_DEVICE][DET_DIR][osal_set_timer] %x
0x43cf7300 [CAMERA_DEVICE][DET_DIR][osal_free_timer] %x
```

## Hallazgos con dirección

- **Sin trazas independientes**: no existen cadenas con prefijo `[DET_DIR]: ` standalone — todas las trazas de detección están bajo el prefijo compuesto `[CAMERA_DEVICE][DET_DIR]`.
- **Sub-módulo de CAMERA_DEVICE**: DET_DIR es un sub-módulo de CAMERA_DEVICE (S617), no un módulo independiente.
- **Mismas 3 trazas**: `osal_alloc_timer`, `osal_set_timer`, `osal_free_timer` con prefijo `[CAMERA_DEVICE][DET_DIR]` (24 B).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[DET_DIR]` standalone | **0** | **0** | **0** |
| token `[CAMERA_DEVICE][DET_DIR]` | **3** | **0** | **0** |
| núcleos `osal_*_timer` | 3 con prefijo compuesto | 3 (prefijos `Spinal`/`CapMgr`/`TRK`) | 3 (prefijos `CapMgr`/`TRK`) |

→ **Sin trazas independientes**. El módulo DET_DIR **no tiene trazas propias** — todas sus trazas están bajo el prefijo compuesto `[CAMERA_DEVICE][DET_DIR]` (S617). El censo de 3 trazas para DET_DIR es **idéntico** al de CAMERA_DEVICE/DET_DIR (S617).

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 0/0 trazas `[DET_DIR]: ` standalone en A6000/A7S/A6300.
- 3/3 trazas `[CAMERA_DEVICE][DET_DIR]` confirmadas en A6000 (idénticas a S617).
- Scripts: `analysis/s618_det_dir/` (pendiente) · Tests: `tests/test_s618_det_dir.py` (pendiente).