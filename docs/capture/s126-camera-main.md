# S126 — `[CAMERA_MAIN]`: el módulo raíz de la cámara (135 trazas)

**Hito de la línea de ingeniería inversa general** (sin efecto en S51).

Informe: [analysis/s126_camera_main/camera_main.md](../../analysis/s126_camera_main/camera_main.md) ·
Datos: `summary.json`, `func_map.json` · Test: `tests/test_s126_camera_main.py`.

## Hallazgo central

`[CAMERA_MAIN]` es el **módulo raíz** de la cámara: el contenedor de las trazas de la capa de
coordinación (AF y calibración, seguimiento, keymap, carga de parámetros) que no pertenecen a
ningún submódulo especializado. 135 trazas `0x43c9c57b`–`0x43ccae46`, **48 funciones**
emisoras y **148 ficheros fuente** embebidos en la zona (`CamResource.cpp`,
`CamSyncResource.cpp`, `SyncTask.cpp`, `ClockControl.cpp`, `init_cam_SetCamParam_main.cpp`,
`ImagingMain.cpp`, `lc_AF_Scan.cpp`, `StageResourceStack.cpp`…).

## Contenido destacado

- **AF y calibración**: `calibration_fc_pos:%d getFcPos(suc_ref_index_target):%d` `0x43c9c57b`,
  `Calibration start` `0x43c9c6d5`, `FOCUS MODE is not AF-A` `0x43c9cd19`,
  `Scanless NG because of Face AF` `0x43c9cd3f`, `this lens is not permitted` `0x43c9ce07`,
  `SCANLESS OK! %d ympc %d csum %d cpeak %d defocus %d` `0x43c9ce8f`.
- **Seguimiento**: `waku area is %d` `0x43c9d53f`, `waku : [%d %d] [%d %d] tracking : …` `0x43c9d55e`.
- **ZPD → AF híbrido**: `NOT_DETECT from ZPD MODULE in spite of ZpdPreEnable. lc_HybridAF.cpp %d`
  `0x43c9d07e` (cierra el puente con S75).
- **keymap / carga**: `keymap size is under 0 [%d]` `0x438d16b0` y
  `>>### LoadNum %x, Ch %x` `0x4378a68c` (la función que más trazas del módulo emite: 51).

## Diferencial

La etiqueta `[CAMERA_MAIN]:` es **nueva en la fw3.21 de la A6000**: la A7S fw3.20 y el A6300
fw2.01 tienen **0** trazas con ese prefijo, pero **92** (A7S) y **121** (A6300) de los mensajes
existen allí **sin etiqueta**. Es la misma política de etiquetado por submódulo que se vio en
S106 (`[IMAGING_CAP]`), S119 (`[APL]` dentro de `[CAMERA_SA]`) y S120 (`[IDT_OPD]`).

## Abierto / NO VERIFICADO

- La subdivisión de los 82 mensajes "sin etiqueta"; qué fichero fuente corresponde a cada una de
  las 48 funciones; el significado de `waku`, `ympc`, `csum`, `cpeak`, `LoadNum`/`Ch`.
