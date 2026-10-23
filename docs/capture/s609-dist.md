# S609 — `[CAMERA_IS][DIST]`: submódulo de corrección de distorsión exclusivo de la A6000 fw3.21

**5 trazas · 5 sitios (regla PIC estricta) · ~2 funciones emisoras · 0 muertas.** Detalle + datos: `analysis/s609_dist/` (pendiente) / `.json` (pendiente).

## Qué es

`[CAMERA_IS][DIST]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 5 mensajes del **submódulo de corrección de distorsión (DIST = Distortion Correction)** dentro del módulo **CAMERA_IS** (Image Stabilization / Estabilización de Imagen). La sigla **SÍ tiene base textual**: `CAMERA_IS` → **C**a**M**era **I**mage **S**tabilization; `DIST` → **D**istortion correction; `IS` → **I**mage **S**tabilization / **I**nternal **S**tabilizer.

## Las 5 trazas (vaddr → texto corto)

```
0x43c98e75 [CAMERA_IS][DIST]: ERR:MakeDistCorPrm prm=null
0x43c98ea5 [CAMERA_IS][DIST]: ERR:CnvPosInvDistCorr prm=null
0x43c98ed8 [CAMERA_IS][DIST]: ERR:CnvPosInvDistCorr prm=inv1 (%d, %d)
0x43c98f14 [CAMERA_IS][DIST]: WRN:CnvPosInvDistCorr prm=inv2 (%d, %d)
0x43c98f51 [CAMERA_IS][DIST]: ERR:MakeDistRawAppliTag prm=null
```

## Hallazgos con dirección

- **Doble prefijo jerárquico**: `[CAMERA_IS][DIST]: ` — prefijo padre `[CAMERA_IS]: ` (módulo IS) + sub-prefijo `[DIST]: ` (submódulo distorsión). Longitud total: 18 B (`[CAMERA_IS][DIST]: `).
- **Funciones de parámetros de distorsión**: `MakeDistCorPrm` (crear parámetros de corrección), `CnvPosInvDistCorr` (convertir posición con corrección inversa de distorsión), `MakeDistRawAppliTag` (crear tag de aplicación RAW de distorsión).
- **Validación de punteros nulos**: 4/5 trazas validan `prm=null` (parámetro nulo) — patrón defensivo.
- **Niveles de severidad**: 4 `ERR` + 1 `WRN` (warning para `prm=inv2`).
- **Parámetros de inversión**: `inv1` e `inv2` — dos matrices/parámetros de corrección inversa de distorsión.
- **Logger dual (patrón S177/S179/S603–S608)**: la fw3.21 **duplica** la traza: nueva con prefijo `[CAMERA_IS][DIST]: ` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Estructura CAMERA_IS**: el módulo `[CAMERA_IS]` en fw3.21 tiene 4 sub-módulos visibles: `[MOUNT]` (2 trazas), `[DIST]` (5 trazas), `[AS]` (3 trazas), `[EIS]` (4 trazas) — total ~14 trazas bajo CAMERA_IS.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAMERA_IS][DIST]` | **5** | **0** | **0** |
| token `[CAMERA_IS]` (padre) | **~14** | **0** | **0** |
| núcleo sin prefijo (`MakeDistCorPrm`, `CnvPosInvDistCorr`, `MakeDistRawAppliTag`) | 0/5 como literal autónomo | **0** | **0** |
| estabilizador/gyro relacionado | `IS_LensMount*`, `GyroAD`, `rcct_SetStblz*` | **strings sueltas** | **strings sueltas** |
| código equivalente (IS/DIST) | `0x43c98xxx`… | **parcial** | **parcial** |

→ **Submódulo *nuevo* en traza y código.** El subsistema de corrección de distorsión DIST **no existe en A7S/A6300** (ni en traza ni con esas funciones `MakeDistCorPrm`, `CnvPosInvDistCorr`, `MakeDistRawAppliTag`). A7S/A6300 tienen strings sueltas de estabilizador/gyro (`imageStabilizer`, `GyroStitScl`, `LmtGyroVect`) pero **sin módulo CAMERA_IS estructurado ni submódulo DIST**. La fw3.21 de la A6000 **introduce** el módulo CAMERA_IS completo con sus 4 sub-módulos (MOUNT, DIST, AS, EIS).

**Longitud del prefijo jerárquico fija:** 18 B (`[CAMERA_IS][DIST]: `) → no variable.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **corrección de distorsión óptica (lente)**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 5/5 cadenas `[CAMERA_IS][DIST]: ` confirmadas en `0x43c98e75`–`0x43c98f51`.
- 0/0 en A7S y A6300 para token `[CAMERA_IS][DIST]` y `[CAMERA_IS]`.
- Scripts: `analysis/s609_dist/` (pendiente) · Tests: `tests/test_s609_dist.py` (pendiente).