# S503 — módulo `[ZPD]` (zero point detection / AF, línea general)

## Alcance

Decodificación del módulo `[ZPD]` del `av-cam.bin` A6000 fw3.21, comparado con
A7S fw3.20 y A6300 fw2.01.

## VERIFICADO

- **Volumen de cadenas que contienen `ZPD`:** A6000 = 55, A7S = 10, A6300 = 48.
  Fuente: `strings | grep -c ZPD` sobre los tres `av-cam.bin`.
- **Inventario REA:** 53 cadenas (`analysis/s503_zpd/zpd_strings.json`), incluyendo:
  - Prefijo directo `[ZPD]:` (5): `lens attach sequence end.`, `load dra data.`,
    `load lens data from lens/body.`, `load:%s`.
  - RTTI `N6Camera3ZPD*`: `MemFileLoadObj`, `MemObj`, `MemUnit`, `MemUnitBackup`,
    `Lens::LensInterpretChunk`, `Control::{Detect,Sequencer,SequencerBase,SyncSequencer,
    AsyncSequencer,WorkerBase}`, `ITrace`.
  - `[DFECore]`: errores `SetZPD0/1IntFactor`, `ClearZPD0/1IntFactor`.
  - `[MOUNT_DEBUG]`: `[BL]ZPD change EclipseDataComState from STANDBY to START`.
  - `[CAMERA_MAIN]`: `NOT_DETECT from ZPD MODULE in spite of ZpdPreEnable`,
    `time is zero Main/LC/ZPD/zpd_mario_afa.cpp`.
  - IRQ/AIF/APB: `Detected IRQ : ZPD CH1`, `CPU IRQ : ZPD0/ZPD1`,
    `CPU APB : ZPD_APB0/1 ...`, `CPU AIF : ZPD W-ch0/R-ch1/... Start/Done`.
  - `ZPD_START:OFF/ON`, `ZPD_SCC`, `ZPD_CLT`, `ZPD_CLT : ON`.
  - `[DFECore]: ImgDdcSetter::loadDefectPos ZPD_SRAM shortage bank:%d addr:%x`.
- **Referencias de código:** 29 xrefs (`analysis/s503_zpd/zpd_xrefs.json`); 9 funciones
  contenedoras resueltas (`analysis/s503_zpd/zpd_functions.json`), 11 xrefs sin función.
- **Funciones resueltas:** `FUN_436e3f14`, `FUN_43754be0`, `FUN_43904ab4`,
  `FUN_43904be8`, `FUN_43904c90`, `FUN_43904cfc`, `FUN_43a0f5c4`, `FUN_43fa9994`,
  `FUN_43fa9b8c`.
- **Subsistemas inferidos (VERIFICADO por texto/RTTI):** módulo C++ `Camera::ZPD`
  con control de detección (`Detect`), secuenciadores síncrono/asíncrono, carga de
  memoria (`MemFileLoadObj`, `MemObj`, `MemUnit`, `MemUnitBackup`), interpretación
  de datos de lente (`Lens::LensInterpretChunk`), trazas (`ITrace`) y backup
  (`SusResInfo`). Integración con DFE (interrupciones ZPD0/1, APB/AIF), montura
  (EclipseDataComState) y CAMERA_MAIN (detección AF, timing).
- **Comparación:** A6000 tiene más cadenas ZPD que A7S (55 vs 10) y más que A6300
  (48); A7S es el que menos expone este módulo. Ver `analysis/s503_zpd/zpd_compare.json`.

## INFERENCIA

- ZPD = *Zero Point Detection* del AF (medición de punto cero del sistema de enfoque),
  con carga de datos de lente y detección; vive bajo `Camera::ZPD` y se integra con
  DFE/montura. El RTTI confirma una clase completa de control, no solo un log.
- La mayor exposición en A6000/A6300 frente a A7S sugiere diferencias de AF/lente,
  no relación con obturador electrónico.

## NO VERIFICADO

- Semántica de `ZPD_CLT`, `ZPD_SCC`, `ZPD_START`, parámetros de interrupción.
- Correspondencia con servicios de AF (`MSG_ID_*`) y con S52/S53.
- Si afecta a captura silenciosa: sin evidencia textual.

## Artefactos

- `analysis/s503_zpd/zpd_strings.json` (53 cadenas REA)
- `analysis/s503_zpd/zpd_xrefs.json` (29 xrefs)
- `analysis/s503_zpd/zpd_functions.json` (9 funciones)
- `analysis/s503_zpd/zpd_unresolved.json` (11 xrefs sin función)
- `analysis/s503_zpd/zpd_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución ni cámara.
