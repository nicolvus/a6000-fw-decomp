# S106 — `IMAGING_CAP`: el gestor de captura still de la A6000

**Hito de la línea de ingeniería inversa general** (no afecta a la decisión del obturador
electrónico: S51 sigue con A/B/C = NO).

Informe completo: [analysis/s106_imaging_cap/imaging_cap_architecture.md](../../analysis/s106_imaging_cap/imaging_cap_architecture.md) ·
Datos: `imaging_cap_architecture.json` · Test: `tests/test_s106_imaging_cap.py` (18 tests).

## Hallazgo central

`[IMAGING_CAP]` es el **módulo de trazas del gestor de captura *still*** de la cámara: 697
cadenas en `0x43c9b335`–`0x43ccab72`, en 11 bloques. No es el pipeline de vídeo ni el
obturador: **0 apariciones** de `shutter`/`silent`/`EFCS`/`curtain`/`mechan` en sus 697
cadenas.

## Qué se ha reconstruido (verificado contra bytes)

1. **83 nombres de fichero fuente embebidos** (`0x43ca8e14`–`0x43cb0cbe`) → la arquitectura
   real del subsistema en 14 familias: 16 `*_Selector.cpp`, 10 `CaptureUtility*.cpp`,
   9 manejadores (`EventDispatcher`, `ExecModeHandler`, `RawDevHandler`…), 6
   `RawMemManager*.cpp`, 8 `Stage_*.cpp`, `CaptureManager*.cpp`, `SectionController.cpp`,
   `CaifCom_Control.cpp`, `NotifyController.cpp`, `ImageParamCapture*.cpp`…
2. **Motor de secciones**: tabla de **17 entradas** `{id u32, manejador u32}` en
   `0x43ff8fb4`; el despachador `FUN_437e534c` copia `0x88` B y busca el id entre 17
   entradas; cada manejador devuelve un bloque de **20 B (5 u32)** con los parámetros de la
   sección, elegido según el modo de captura.
3. **Ids ↔ etapas**: 14 de los 17 manejadores referencian el nombre de su
   `Capture<Etapa>_Selector.cpp` (`CaptureExposure`, `CaptureRead`, `CaptureAfterRead`,
   `CaptureDevEntry`, `CaptureCorrectRaw`, `CaptureOpdBeforeNR`, `CaptureDevelop`,
   `CaptureMarble`, `CaptureFeatureEffect`, `CaptureAfterEffect`, `CaptureEncode`,
   `CaptureAfterEnc`, `CaptureSortJpeg`, `CaptureDevExit`).
4. **CapMgr**: máquina de eventos (`LastDetectionEnd`, `NotifySyncStart`, `StartRawSequence`,
   `EndRawSequence`, `CaptureEnd`, `CheckLastDet`, `CaptureCancel_PowerOffDetect`) con tabla
   de salto de 16 entradas en `0x43bc4e08`.
5. **Canal CAIF** con el codificador: `CAP_REQ`, `CAP_REQ_CLR`, `CAP_SETTING`, `CAP_START`,
   `CAP_DATA`, `CAP_V_COM`, con dirección explícita `[EN->CA]` / `[CA->EN]` / `[CA->AVIP]`.
6. **8 modos de adquisición del CamCore**: `MODE_CAP`, `MODE_CAP_DRP`, `MODE_CAP_PREREVIEW`,
   `MODE_CAP_SNR`, `MODE_CAP_SNR_PREREVIEW`, `MODE_SNR_BUS_THROUGH`,
   `MODE_SNR_BUS_THROUGH_PREREVIEW`, `MODE_CDET(for PreReview)`.
7. **Capa de memoria**: `ImageParam_Capture_Base` (AddRef/Release/ALL Released),
   `RawMemManager` (MemPool/MemBuffer/MemRuleLib/UnitTypeLib), `GetMem_*`/`ShareMem_*`/
   `UseRaw_DualRec`/`FreeRaw_DualRec`, DMM (`SetDmmInfo) FATAL! overwrite`).
8. **Cómo se referencian las cadenas**: esquema **PIC** (el pool guarda un desplazamiento:
   `destino = literal + (add + 4)`). Con la **regla canónica estricta** (el `ldr` más cercano
   del registro, la única que coincide con los dos módulos verificados a mano): **690 de las
   697** cadenas referenciadas; las **7** restantes (los cuatro mensajes `DistV_RC`/`DistH_RC`,
   `ShareMem_StlRaw8 Err…` `0x43ca9b12`, `%s: ContrastPlus error` `0x43cc7d5c` y
   `Rch_Rcv_Zima_Base Err…` `0x43cc839c`) no tienen referencia alguna (ni PIC ni puntero
   absoluto) → cadenas muertas. La metodología completa (y por qué el número depende de la
   regla) está en
   [`analysis/s106_imaging_cap/pic_xref_methodology.md`](../../analysis/s106_imaging_cap/pic_xref_methodology.md).
9. **Diferencial A7S fw3.20**: 0 cadenas con el prefijo `[IMAGING_CAP]`; los mismos mensajes
   existen **sin etiqueta de módulo** (`CapMgr) LastDetectionEnd…` `0x43cae3b3`,
   `SectionCtrl) Fatal!…` `0x43caefd1`). La fw3.21 de la A6000 **añade la etiqueta**; los 16
   `*_Selector.cpp` están en A6000, A7S y A6300 → estructura común a la familia.

## Abierto / NO VERIFICADO

- Los ids de sección `0x00`, `0x01` y `0x06` no referencian el nombre de su selector, y
  `CapturePrelight`/`SequenceFilter` se referencian fuera de la tabla: la asignación
  id↔etapa completa queda pendiente.
- El significado de los 20 B por sección y de los campos del contexto que los eligen.
- Los formatos binarios de los mensajes CAIF y `MSG_ID_SDF_*`.
- Nada de esto cambia S51: el gestor de captura no registra nada del obturador.

## Scripts

`analysis/s106_imaging_cap/scan_pic_refs.py` (referencias PIC de toda la imagen),
`scan_section_handlers.py` (tabla de 17 secciones y sus cadenas),
`scan_source_files.py` (inventario de ficheros), `scan_a7s_diff.py` (diferencial
A6000/A7S/A6300), `build_summary.py` (JSON resumen).
