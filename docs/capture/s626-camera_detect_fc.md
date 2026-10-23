# S626 — `[CAMERA_DETECT_FC]`: módulo de detección de cámara (Focus Camera) exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**1 traza · 1 sitio (regla PIC estricta) · ~1 función emisora · 0 muertas.** Detalle + datos: [JSON](../../analysis/s626_camera_detect_fc/camera_detect_fc.json).

## Qué es

`[CAMERA_DETECT_FC]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 1 mensaje del **módulo de detección de cámara (Focus Camera / FC)**. La sigla **SÍ tiene base textual**: `CAMERA_DETECT_FC` → **CAMERA** (cámara) **DETECT** (detección) **FC** (Focus Camera / Full Camera?).

## La traza (vaddr → texto corto)

```
0x43cf02c9 [CAMERA_DETECT_FC]: %s @%s L%d
```

## Hallazgos con dirección

- **Formato de logging estructurado**: `%s @%s L%d` — función/archivo (`%s`), línea (`@%s`), número de línea (`L%d`).
- **Logger dual (patrón S177/S179/S603–S625)**: la fw3.21 **duplica** la traza: nueva con prefijo `[CAMERA_DETECT_FC]: ` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Prefijo fijo**: 20 B (`[CAMERA_DETECT_FC]: `) → fijo.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAMERA_DETECT_FC]` | **1** | **0** | **0** |
| núcleo sin prefijo (`%s @%s L%d`) | 0/1 como literal autónomo | **0** | **0** |
| strings relacionadas detección cámara | 0 | **pocas** | **pocas** |
| código equivalente | `0x43cf02c9`… | **parcial** | **parcial** |

→ **Módulo *nuevo* en traza, código preexistente.** El mecanismo de detección de cámara **existe en A7S/A6300** (strings genéricas de detección) pero **sin el submódulo estructurado `CAMERA_DETECT_FC` con logging formateado**. La fw3.21 de la A6000 **introduce** el módulo con logging formateado y **duplica** la traza (nueva con logger de módulo + vieja con logger global `0x43902718`).

**Longitud del prefijo fija:** 20 B (`[CAMERA_DETECT_FC]: `) → fijo.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **detección de cámara (logging estructurado)**, no el obturador per se. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 1/1 cadena `[CAMERA_DETECT_FC]:` confirmada en `0x43cf02c9`.
- 0/0 en A7S y A6300 para token `[CAMERA_DETECT_FC]`.
- Scripts: `analysis/s626_camera_detect_fc/` (pendiente) · Tests: `tests/test_s626_camera_detect_fc.py`.
