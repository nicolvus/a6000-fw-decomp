# S126 — `[CAMERA_MAIN]`: el módulo raíz de la cámara (135 trazas)

> Hito de la **línea de ingeniería inversa general**. Verificación contra los bytes del
> `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21); convención **vaddr =
> 0x43541000 + file_offset**. Regla de referencias: la **estricta** (canónica, ver
> [`pic_xref_methodology.md`](../s106_imaging_cap/pic_xref_methodology.md)). Sin efecto en S51.

## 1. Qué es

`[CAMERA_MAIN]` es el **módulo raíz** de la cámara: el que agrupa lo que no pertenece a
ninguno de los submódulos especializados (`[CAMERA_MAIN_CC]`, `_IM`, `_LC`, `_TC`, `_SYNC`, `_YC`).
No es un subsistema con una función propia, sino el **contenedor de trazas de la capa de
coordinación** (AF, calibración, recursos, keymap, carga de parámetros).

- **135 trazas** con el prefijo `[CAMERA_MAIN]:`, de `0x43c9c57b` a `0x43ccae46`.
- **48 funciones** las emiten (regla estricta) y hay **148 ficheros fuente** embebidos en la
  zona de cadenas.

## 2. Contenido por bloques (lo que se puede leer en las trazas)

| bloque | n | qué es | ejemplos |
|---|---|---|---|
| **AF y calibración** | ~40 | calibración de la posición de enfoque, `fc_depth`, `AF-A`, `Scanless` (AF sinobyector) | `calibration_fc_pos:%d getFcPos(suc_ref_index_target):%d` `0x43c9c57b`, `Calibration start` `0x43c9c6d5`, `FOCUS MODE is not AF-A` `0x43c9cd19`, `Scanless NG because of Face AF` `0x43c9cd3f`, `Select AF Area is out of SCANLESS-RANGE x %d y %d` `0x43c9cda2`, `this lens is not permitted` `0x43c9ce07`, `SCANLESS OK! %d ympc %d csum %d cpeak %d defocus %d` `0x43c9ce8f` |
| **seguimiento / waku** | ~10 | el área de seguimiento (`waku`) y sudebug | `waku area is %d` `0x43c9d53f`, `waku : [%d %d] [%d %d] tracking : [%d %d] [%d %d]` `0x43c9d55e` |
| **keymap y carga de parámetros** | ~15 | tabla de teclas y carga de `LoadNum`/`Ch` | `keymap size is under 0 [%d]` `0x438d16b0`, `>>### LoadNum %x, Ch %x` `0x4378a68c` (51 trazas: es la función que más de este módulo emite) |
| **ZPD / hybrid AF** | ~5 | el ZPD (S75) avisa al AF híbrido | `NOT_DETECT from ZPD MODULE in spite of ZpdPreEnable. lc_HybridAF.cpp %d` `0x43c9d07e` |
| **varios sin etiqueta** | 82 | mensajes sueltos del nivel raíz | — |

## 3. Ficheros fuente de la zona (148)

Los nombres embebidos en `0x43c9c57b`–`0x43ccae46` y sus alrededores describen la capa de
coordinación: `CamSyncResource.cpp`, `CamResource.cpp`, `SyncTask.cpp`, `ClockControl.cpp`,
`SystemDelay.cpp`, `init_cam_SetCamParam_main.cpp`, `ImagingMain.cpp`, `InfraImaging.cpp`,
`CS_imaging.cpp`, `CS_ExportAPI.cpp`, `StaticSetInfo.cpp`, `capcon_api_cam.cpp`,
`lc_AF_Scan.cpp`, `lc_wrap_upm.cpp`, `lc_HybridAF.cpp`, `RCWrapper.cpp`,
`DualRecResManager.cpp`, `StageResourceStack.cpp`, `CaptureUtilityCommon.cpp`,
`CaptureUtilityRC.cpp`, `CaptureUtilityDebug.cpp`, `CaptureUtilityExifMkNote.cpp`,
`Stage_SACC.cpp`, `still_seq_panoramaStitch.cpp`, `Spinal.cpp`… → el "núcleo" de la cámara es
un **gestor de recursos** (`CamResource`/`CamSyncResource`/`StageResourceStack`) con tareas de
sincronización (`SyncTask`), control de reloj (`ClockControl`) y un planificador de secuencias
(`Spinal`).

## 4. Diferencial A6000 fw3.21 vs A7S fw3.20 / A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| trazas `[CAMERA_MAIN]` | 135 | **0** | **0** |
| mensajes idénticos texto a texto | — | 92 | 121 |
| mensajes sólo de la A6000 | — | 43 | 14 |

→ La etiqueta `[CAMERA_MAIN]:` es **nueva en la fw3.21 de la A6000**: en la A7S y el A6300 los
mismos mensajes existen **sin etiqueta** (92 de 135 coinciden texto a texto; los 43 restantes
son reformulaciones o mensajes nuevos de la fw3.21). La fw3.21 de la A6000 es la que **etiqueta
por submodule** de forma sistemática (`[CAMERA_MAIN]`, `[CAMERA_MAIN_CC]`, `_IM`, `_LC`, `_TC`,
`_SYNC`, `_YC`, `[IMAGING_CAP]`…).

## 5. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| 135 trazas `0x43c9c57b`–`0x43ccae46` | `extract_camera_main.py` (prefijo + corte en NUL) |
| 48 funciones emisoras | mapa PIC con la regla estricta + prólogos Thumb |
| 148 ficheros fuente en la zona | búsqueda de `*.cpp`/`*.h` en ±16 KB del rango de cadenas |
| 92/121 mensajes comunes con A7S/A6300 | comparación texto a texto sobre los blobs |
| 0 trazas `[CAMERA_MAIN]` en A7S/A6300 | búsqueda del prefijo en los tres blobs |

## 6. NO VERIFICADO / abierto

- La **división** de los 82 mensajes "sin etiqueta" en sub-bloques temáticos (la etiqueta del
  módulo no lleva segundo nivel).
- Qué ficheros fuente corresponden a cada una de las 48 funciones (el mapa es por función, no
  por fichero).
- El significado de `waku`, `ympc`, `csum`, `cpeak`, `LoadNum`/`Ch` y `suc_ref_index_target`.
- Nada de esto **afecta a S51** (A/B/C = NO).

## 7. Ficheros de este hito

| fichero | contenido |
|---|---|
| `strings_raw.json` | las 135 cadenas con vaddr/offset/texto |
| `func_map.json` | mapa función → traza (48 funciones) |
| `summary.json` | sub-bloques, ficheros fuente y diferencial |
| `extract_camera_main.py` | script de extracción (reproducible) |
