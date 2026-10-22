# S178 — censo de cobertura de la línea de módulos

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

Censo completo de las etiquetas `[XXX]` de la A6000 fw3.21, para saber cuánto queda:

| magnitud | valor |
|---|---|
| etiquetas distintas en la A6000 fw3.21 | **372** (techo) |
| con hito de decodificación en el catálogo | **52** |
| **pendientes** | **320** |
| **exclusivas de la A6000** (0 en A7S y 0 en A6300) | **93** |
| presentes en A6000/A7S pero **ausentes en el A6300** | **7** |

**La familia `[STK]`** (`[STK_AUTO_SAL]`, `[STK_COLOR_SIM]`, `[STK_C_SIM]`, `[STK_TOUCH_SIM]`,
`[STK_T_SIM]`) **y `[OSD]`** existen en la A6000 y en la A7S y **desaparecen por completo en el
A6300 fw2.01**: son funciones de la **plataforma antigua** (E-mount / pre-LIRO) que la nueva
plataforma no arrastra → control de **versionado de plataforma**, no de modelo (la A7S de 2016
comparte plataforma con la A6000; el A6300 de 2019 es de otra).

Otros datos del censo: `[VDF]` tiene **81 apariciones más** en la A6000 (243) que en la A7S y el
A6300 (162); las pendientes más grandes son `[SDF]` (477), `[ERR]` (288), `[VDF]` (243),
`[ERROR]` (213), `[BL]` (154), `[VEF]` (149), `[STK]` (76), `[TD]` (73), `[VIDENCSTAT]` (70),
`[FACE]` (70), `[RC]` (69), `[DEBUG]` (67), `[GOLFSHOT]` (65), `[WSX]` (59), `[INFO]` (58),
`[RE]` (54), `[INT_ERROR]` (53), `[ENCOUCSTAT]` (49), `[CONFIG]` (47), `[BT]` (44),
`[CAM_FUNC_MGR]` (43, exclusiva), `[PNL]` (41), `[SAN]` (35), `[AUDPINEDTR]` (34),
`[CAM_SCALAR]` (34, exclusiva), `[REMOTE]` (32, exclusiva).

**Salvedad**: el patrón de extracción también captura fragmentos de formato (`[D0]`–`[D7]`,
`[IN1]`, `[NULL]`, `[SIZE]`, `[STAT]`, `[HW]`), así que **372 es un techo**.

**Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.** El censo es de cobertura, no de
contenido.

Informe: [analysis/s178_census/census.md](../analysis/s178_census/census.md) ·
test: `tests/test_s178_census.py` (8 tests).
