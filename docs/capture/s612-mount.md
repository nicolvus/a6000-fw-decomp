# S612 — `[CAMERA_IS][MOUNT]`: submódulo de montura IS exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**5 trazas · 5 sitios (regla PIC estricta) · ~2 funciones emisoras · 0 muertas.** Detalle + datos: [JSON](../../analysis/s612_mount/mount.json).

## Qué es

`[CAMERA_IS][MOUNT]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 5 mensajes del **submódulo de montura para estabilización de imagen (IS = Image Stabilization)** dentro del módulo **CAMERA_IS**. La sigla **SÍ tiene base textual**: `CAMERA_IS` → **C**a**M**era **I**mage **S**tabilization; `MOUNT` → **montura** del objetivo (lens mount).

## Las 5 trazas (vaddr → texto corto)

```
0x43c98da6 [CAMERA_IS][MOUNT]: [Error] IS_LensMountExpStartCB (%x)
0x43c98dde [CAMERA_IS][MOUNT]: [Error] IS_LensMountExpStartCB - checkData
0x43c9a3a7 [CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyroCB (%x)
0x43c9a3e3 [CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyroCB - checkData
0x43c9a426 [CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyro (%x)
```

## Hallazgos con dirección

- **Doble prefijo jerárquico**: `[CAMERA_IS][MOUNT]: [Error]` — prefijo padre `[CAMERA_IS]: ` (módulo IS) + sub-prefijo `[MOUNT]: ` (submódulo montura) + nivel `[Error]`. Longitud total: 28 B (`[CAMERA_IS][MOUNT]: [Error] `).
- **Callbacks de montura IS**: 2 callbacks principales:
  - `IS_LensMountExpStartCB` — callback de inicio de exposición para montura IS (con validación `checkData`)
  - `IS_LensMountPanoramaGyroCB` / `IS_LensMountPanoramaGyro` — callback de giroscopio para panorama IS (con validación `checkData`)
- **Validación de datos**: `checkData` — verificación de integridad de datos del callback.
- **Nivel de severidad**: 5/5 `Error` — todas las trazas son de error.
- **Logger dual (patrón S177/S179/S603–S611)**: la fw3.21 **duplica** la traza: nueva con prefijo `[CAMERA_IS][MOUNT]: [Error] ` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Estructura CAMERA_IS**: el módulo `[CAMERA_IS]` en fw3.21 tiene 4 sub-módulos visibles: `[MOUNT]` (5 trazas), `[DIST]` (5 trazas), `[AS]` (3 trazas), `[EIS]` (4 trazas) — total ~17 trazas bajo CAMERA_IS.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAMERA_IS][MOUNT]` | **5** | **0** | **0** |
| token `[CAMERA_IS]` (padre) | **~17** | **0** | **0** |
| núcleo sin prefijo (`IS_LensMountExpStartCB`, `IS_LensMountPanoramaGyroCB`, `IS_LensMountPanoramaGyro`) | 0/5 como literal autónomo | **0** | **0** |
| strings relacionadas montura A7S | 0 | **70+** (`[BL]MOUNT_*`, `Mount: `, etc.) | **70+** |
| código equivalente (IS/MOUNT) | `0x43c98da6`… | **parcial (BL mount)** | **parcial (BL mount)** |

→ **Submódulo *nuevo* en traza y código.** El submódulo de montura para IS **no existe en A7S/A6300** (ni en traza ni con esas funciones `IS_LensMountExpStartCB`, `IS_LensMountPanoramaGyroCB`, `IS_LensMountPanoramaGyro`). A7S/A6300 tienen un subsistema de montura BL (`[BL]MOUNT_*`, `Mount: `) pero **sin integración en módulo IS estructurado**. La fw3.21 de la A6000 **introduce** el submódulo MOUNT dentro de CAMERA_IS.

**Longitud del prefijo jerárquico fija:** 28 B (`[CAMERA_IS][MOUNT]: [Error] `) → no variable.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **callbacks de montura para estabilización de imagen (IS)**, no el obturador per se. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 5/5 cadenas `[CAMERA_IS][MOUNT]: [Error]` confirmadas en `0x43c98da6`–`0x43c9a426`.
- 0/0 en A7S y A6300 para token `[CAMERA_IS][MOUNT]`.
- Scripts: `analysis/s612_mount/` (pendiente) · Tests: `tests/test_s612_mount.py`.
