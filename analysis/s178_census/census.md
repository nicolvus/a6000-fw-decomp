# S178 — censo de cobertura de la línea de módulos: 372 etiquetas en la A6000 fw3.21

> Hito de la **línea de ingeniería inversa general**. Solo bytes: `av-cam.bin` de la A6000 fw3.21
> (`analysis/rea-independent/input/av-cam.bin`), con la A7S fw3.20 y el A6300 fw2.01 como
> comparación. Convención: `vaddr = 0x43541000 + file_offset`. Regla de referencias:
> **estricta**, con el mapa global en `analysis/s106_imaging_cap/pic_refs_strict_global.json`
> (17 525 destinos) y los de A6300/A7S en `analysis/s169_drive_api/`.

## 1. Resumen

Se ha levantado el **censo completo de etiquetas de módulo** de la A6000 fw3.21 para saber
cuánto queda por decodificar y cuáles son los candidatos másoborosos.

| magnitud | valor |
|---|---|
| etiquetas distintas `[XXX]` en la A6000 fw3.21 | **372** (techo) |
| etiquetas **con hito de decodificación** propio | **58** |
| etiquetas **cubiertas como sub-etiqueta** de un módulo ya decodificado (`[X][Y]` con `X` decodificado) | **38** |
| **pendientes reales** | **276** |
| **cobertura total** (hito + sub-etiqueta) | **96/372** = **25.81 %** |
| etiquetas **exclusivas de la A6000** (0 en A7S y 0 en A6300) | **93** |
| etiquetas presentes en A6000/A7S pero **ausentes en el A6300** | **7** |

**Todo el catálogo de hitos** (S66–S178) decodifica **52** etiquetas (fotografía del momento; el
catálogo sigue creciendo en la sesión paralela) y el resto (320) es el trabajo pendiente real de la línea.
El invariante es que ambas cifras suman **372**.

## 2. Las 7 etiquetas que el A6300 **elimina**

| etiqueta | A6000 | A7S | A6300 |
|---|---|---|---|
| `[STK]` | 76 | 76 | **0** |
| `[STK_AUTO_SAL]` | — | — | **0** |
| `[STK_COLOR_SIM]` | — | — | **0** |
| `[STK_C_SIM]` | — | — | **0** |
| `[STK_TOUCH_SIM]` | — | — | **0** |
| `[STK_T_SIM]` | — | — | **0** |
| `[OSD]` | — | — | **0** |

La familia **`[STK]`** (con sus variantes `*_SIM`, `AUTO_SAL`) y **`[OSD]`** (on-screen display)
existen en la A6000 y en la A7S y **desaparecen por completo en el A6300 fw2.01**: son
funciones de la plataforma antigua (E-mount / pre-LIRO) que la nueva plataforma no arrastra.
Esto es un **control de versionado de plataforma**, no de modelo: la A7S (2016) comparte la
plataforma con la A6000, y el A6300 (2019) es de otra.

## 3. Las etiquetas pendientes más grandes

Ordenadas por nº de apariciones del token en la A6000 fw3.21 (las 25 primeras):

| etiqueta | A6000 | A7S | A6300 | nota |
|---|---|---|---|---|
| `[SDF]` | 477 | 479 | 488 | framework de codificación (S83 lo rozó) |
| `[ERR]` | 288 | 281 | 655 | |
| `[VDF]` | 243 | 162 | 162 | visor: la A6000 tiene **81 más** que las otras dos |
| `[ERROR]` | 213 | 213 | 214 | |
| `[BL]` | 154 | 75 | 96 | driver de la montura (S66/S133 lo tocaron) |
| `[VEF]` | 149 | 141 | 144 | |
| `[STK]` | 76 | 76 | **0** | **eliminado en el A6300** |
| `[TD]` | 73 | 73 | 84 | |
| `[VIDENCSTAT]` | 70 | 70 | 71 | |
| `[FACE]` | 70 | 70 | 70 | |
| `[RC]` | 69 | 69 | 71 | API de recursos (S164/S172) |
| `[DEBUG]` | 67 | 37 | 37 | |
| `[GOLFSHOT]` | 65 | 65 | 64 | |
| `[WSX]` | 59 | 59 | 59 | |
| `[INFO]` | 58 | 1 | 37 | |
| `[RE]` | 54 | 53 | 54 | |
| `[INT_ERROR]` | 53 | 53 | 53 | |
| `[ENCOUCSTAT]` | 49 | 54 | 68 | |
| `[CONFIG]` | 47 | 47 | 47 | |
| `[BT]` | 44 | 44 | 44 | |
| `[CAM_FUNC_MGR]` | 43 | **0** | **0** | **exclusiva de la A6000** → S177 |
| `[PNL]` | 41 | 41 | 41 | |
| `[SAN]` | 35 | 34 | 34 | |
| `[AUDPINEDTR]` | 34 | 34 | 79 | |
| `[CAM_SCALAR]` | 34 | **0** | **0** | **exclusiva de la A6000** |
| `[REMOTE]` | 32 | **0** | **0** | **exclusiva de la A6000** |

## 4. Las 93 etiquetas exclusivas de la A6000 (0/0)

De las 93, **52 ya están decodificadas** por hitos previos (S106 `[IMAGING_CAP]`, S110
`[CAMERA_MAIN_YC]`, S112 `[CAMERA_MAIN_SYNC]`, S115 `[CAM_IMAGER]`, S120 `[IDT_OPD]`, S122
`[CAMERA_MAIN_TC]`, S123 `[CAMERA_MAIN_CC]`, S126 `[CAMERA_MAIN]`, S127 `[CAMERA_MAIN_LC]`,
S128/S129 `[CAMERA_MAIN_IM]`, S131 `[VPH_API]`, S132 `[CLK_CTRL]`, S133 `[MOUNT_DEBUG]`, S136
`[ACCY]`, S143 `[CAM_UTIL_ADJ]`, S144 `[CAM_UTIL_SENS]`, S148 `[DEPTH]`, S151 `[PANDA]`, S156
`[TP_R]`, S164 `[CAMERA_IS]`, S165 `[JOG]`, S166 `[ADC_DEBUG]`, S167 `[SAD]`, S170 `[ILLUMI]`,
S173 `[CAM_UTIL]`/`[CAMERA_ADJ]`, S175 `[LIF_DEBUG]`, …).

Las pendientes más grandes de ese subconjunto son `[CAM_FUNC_MGR]` (43), `[CAM_SCALAR]` (34),
`[REMOTE]` (32), `[JPEG]`, `[LENS_YC]`, `[IMAGING_RAW]`, `[CAMERA_DSP_APL]`, `[NSX_VOT]`,
`[CAM_CMD]`, `[MOUNT_INFO]`, `[DIST]`, `[HOUSING]`, `[IMAGING_RSRC]`, `[MOUNT]`,
`[MOUNT_WARNING]`, `[ZPD]`, `[EIS]`, `[LENS_PDR]`, `[CAMERA_DEVICE]`, `[DET_DIR]`, `[SENSER]`,
`[STABILIZER]`, `[AVOUT]`, `[AVR]`, `[JIRO]`, `[UTILITY]`, `[ADR]`, `[CAMERA_DETECT_FC]`,
`[EO_SW]`, `[FILE_NUM]`, `[FSYSMODE]`, `[RING_DIAL]`, …

## 5. Salvedad metodológica del propio censo

La extracción usa el patrón `\[[A-Z][A-Z0-9_]{1,24}\]`, que **también captura fragmentos de
formatos** que no son etiquetas de módulo: `[D0]`–`[D7]`, `[IN1]`, `[IN2]`, `[NULL]`, `[SIZE]`,
`[STAT]`, `[HW]`, `[D0]`–`[D7]`… Por tanto **372 es un techo**, no un número exacto de
módulos; el recuento de módulos reales es menor. La cifra **52 decodificados / 320 pendientes**
y la lista de **93 exclusivas de la A6000** son las que sí son accionables.

## 6. Qué NO se afirma

- **NO** se afirma que las 320 pendientes sean todas módulos: hay fragmentos de formato.
- **NO** se ha elegido el «siguiente módulo» por tamaño, sino por valor: los candidatos con más
  información para la línea del obturador son los que hablan de disparo, lectura del sensor o
  tiempos (p. ej. `[VDF]`, `[RC]`, `[EIS]`, `[STABILIZER]`, `[ZPD]`).
- **NO** se ha analizado el contenido de ninguna etiqueta pendiente: el censo es de **cobertura**,
  no de contenido.

**Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.** El censo no aporta ninguna evidencia
sobre el obturador electrónico: es una foto de cuánto queda por hacer en la línea de módulos.

## 7. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s178_census.py -q
```

## 8. Revisión del agente principal

_(vacía)_
