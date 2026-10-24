# S615 — `[CAMERA_IS][EIS]`: submódulo de estabilización electrónica de imagen (EIS) exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**4 trazas · 4 sitios (regla PIC estricta) · ~2 funciones emisoras · 0 muertas.** Detalle + datos: [JSON](../../analysis/s615_eis/eis.json).

## Qué es

`[CAMERA_IS][EIS]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 4 mensajes del **submódulo de estabilización electrónica de imagen (EIS = Electronic Image Stabilization)** dentro del módulo **CAMERA_IS**. La sigla **SÍ tiene base textual**: `CAMERA_IS` → **C**a**M**era **I**mage **S**tabilization; `EIS` → **E**lectronic **I**mage **S**tabilization (estabilización electrónica de imagen).

## Las 4 trazas (vaddr → texto corto)

```
0x43c9a2b2 [CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzPower error!
0x43c9a2eb [CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzGridH error!
0x43c9a324 [CAMERA_IS][EIS]: GyroAD[p],GyroAD[y], %d, %d
0x43c9a352 [CAMERA_IS][EIS]: %x, %d, %d
```

## Hallazgos con dirección

- **Doble prefijo jerárquico**: `[CAMERA_IS][EIS]:` — prefijo padre `[CAMERA_IS]:` (módulo IS) + sub-prefijo `[EIS]:` (submódulo EIS). Longitud total: 17 B (`[CAMERA_IS][EIS]:`).
- **Control de potencia**: `rcct_SetStblzPower` — configuración de potencia de estabilización (error con código hex).
- **Configuración de grid**: `rcct_SetStblzGridH` — configuración de grid horizontal de estabilización (error con código hex).
- **Datos de giroscopio**: `GyroAD[p],GyroAD[y]` — lectura de giroscopio en ejes pitch (p) e yaw (y) con valores decimales.
- **Datos genéricos**: `%x, %d, %d` — traza genérica con hex + 2 decimales.
- **Logger dual (patrón S177/S179/S603–S614)**: la fw3.21 **afirma duplicar** la traza (NO_VERIFICADO - requiere xrefs/REA): nueva con prefijo `[CAMERA_IS][EIS]:` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Estructura CAMERA_IS**: el módulo `[CAMERA_IS]` en fw3.21 tiene 4 sub-módulos visibles: `[MOUNT]` (5 trazas), `[DIST]` (5 trazas), `[AS]` (3 trazas), `[EIS]` (4 trazas) — total ~17 trazas bajo CAMERA_IS.
- **Función `rcct_*`**: API de control de estabilización (rcct = Real-time Camera Control/Tracking?).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAMERA_IS][EIS]` | **4** | **0** | **0** |
| token `[CAMERA_IS]` (padre) | **~17** | **0** | **0** |
| núcleo sin prefijo (`rcct_SetStblzPower`, `rcct_SetStblzGridH`, `GyroAD`, `Shot Timing`) | 0/4 como literal autónomo | **4/4** (con prefijo `[GOLFSHOT]` o sin prefijo) | **2/4** (`rcct_SetStblzPower/GridH` sin prefijo) |
| strings EIS relacionadas A7S | 0 | **3** (`EIS_RC1V_SetPower`, `Sequence_Movie: SPC_ERR`) | **pocas** |

→ **Submódulo *nuevo* en traza, código preexistente.** Las funciones EIS (`rcct_SetStblzPower/GridH`, `GyroAD`) **existen en A7S/A6300** (mismas strings núcleo) pero **sin el prefijo `[CAMERA_IS][EIS]: `**. A7S usa prefijo `[GOLFSHOT]` o sin prefijo; A6300 solo strings sueltas. La fw3.21 de la A6000 **añade prefijo `[CAMERA_IS][EIS]: `** y **duplica** la traza (nueva con logger de módulo + vieja intacta con logger global `0x43902718`).

**Longitud del prefijo jerárquico fija:** 17 B (`[CAMERA_IS][EIS]:`) → no variable.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **estabilización electrónica de imagen (EIS) y datos de giroscopio**, no el obturador per se. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 4/4 cadenas `[CAMERA_IS][EIS]:` confirmadas en `0x43c9a2b2`–`0x43c9a352`.
- 0/0 en A7S y A6300 para token `[CAMERA_IS][EIS]`; 2-4 núcleos idénticos en A7S/A6300 sin prefijo.
- Scripts: `analysis/s615_eis/` (pendiente) · Tests: `tests/test_s615_eis.py`.
