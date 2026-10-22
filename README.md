# Sony A6000 Hardware & Firmware Reverse Engineering Project

Ingeniería inversa de hardware y firmware de la Sony A6000 (fw 3.21): arquitectura, arranque,
recuperación y pipeline de captura. El obturador electrónico es un
[subproyecto](projects/electronic-shutter/README.md). Sin firmware ejecutado, sin cámara, sin flasheo.

## Dónde mirar primero

- Estado operativo breve: [knowledge/CURRENT.md](knowledge/CURRENT.md) · restricciones: [docs/STATE.md](docs/STATE.md) · continuidad: [CONTEXT.md](CONTEXT.md).
- Historial completo de fases: [knowledge/PROGRESS.md](knowledge/PROGRESS.md).
- Catálogo de la línea de RE general (60 hitos): [docs/capture/linea-general-re.md](docs/capture/linea-general-re.md).
- Resultados y viabilidad: [docs/findings.md](docs/findings.md), [docs/feasibility-report.md](docs/feasibility-report.md).
- README histórico íntegro (S19–S100, antes de esta reorganización): [docs/history/README-historial-2026-10-21.md](docs/history/README-historial-2026-10-21.md).

## Fases recientes (más nuevas primero)
Cada enlace lleva a su informe; el resumen de hallazgos está en el [catálogo](docs/capture/linea-general-re.md) y en el [historial](docs/history/README-historial-2026-10-21.md).
- [S124: el bloque de parámetros de exposición/lectura por `drive_mode` del imager](analysis/s124_exposure_params/exposure_params.md): de dónde sale cada campo de la traza `SetExps` (`PrevDrv`/`NowDrv`/`NextDrv` = u16 en +4/+0/+6 del bloque de modo, **`shut` = byte +9**, `svd`/`shd`/`spl` = u32 del contexto en +0x178/+0x174/+0x170) y **diferencial A6000/A7S**: el conjunto de parámetros (`shut`, `svd`, `shd`, `spl`, `sint`, `gs`, `epdsel`) es **el mismo** en ambas cámaras (5 trazas de `[CAMERA_MAIN_SYNC]` idénticas texto a texto); la fw3.21 solo reescribe la instrumentación (`SetExps`/`SetRead`/`Execute` con el drive mode anterior) y el layout del contexto (`+0x13c` → `+0xfc`), y añade `[CAMERA_MAIN_LC]: zaf_now_shut_cycle=%d` `0x43ca7836`. **`shut` es el contador/índice de obturación, no un obturador electrónico** → sin efecto en S51. 7 tests.
- [S120: `[IDT_OPD]`, la segunda instancia del módulo IDT](analysis/s120_idt_opd/idt_opd.md): 274 apariciones (273 cadenas) con **274 gemelos `[IDT]` contiguos byte a byte** → el etiquetado es la única diferencia; `IDT_OPD` **no es una sigla inventada** sino un **recurso del `SyncResMgr`** (`RESOURCE_IDT_OPD` `0x43c9c461`) y unos comandos (`IDT_OPD_TOP_Sync_OPDAcquire` `0x43c9c2fc`) que ya existían en la A7S y el A6300, etiquetados allí como `[IDT]`. 165 funciones (`0x439dde84`–`0x439fcf9c`), bloques de mapa verificados (IE `0x439e80c8` con 19 campos, MAP `0x439ee7e8` con 18) y 18 punteros de volcado. **Además encontró un bug en la kill analysis del escáner compartido** (inactiva por `md.detail` apagado y mapeo de registros inválido) → ya corregido. 97 tests.
- [S126: `[CAMERA_MAIN]`, el módulo raíz de la cámara (135 trazas)](analysis/s126_camera_main/camera_main.md): el contenedor de la capa de coordinación (AF y calibración, seguimiento `waku`, keymap, carga de parámetros) que no pertenece a ningún submódulo: 48 funciones emisoras y **148 ficheros fuente** embebidos en la zona (`CamResource.cpp`, `CamSyncResource.cpp`, `SyncTask.cpp`, `ClockControl.cpp`, `init_cam_SetCamParam_main.cpp`, `ImagingMain.cpp`, `lc_AF_Scan.cpp`…); puente con el ZPD (S75) en `NOT_DETECT from ZPD MODULE … lc_HybridAF.cpp` `0x43c9d07e`. La etiqueta `[CAMERA_MAIN]:` es **nueva en la fw3.21** (A7S y A6300: 0 trazas; 92 y 121 mensajes idénticos **sin etiqueta**). 7 tests.
- [S122: el módulo `[CAMERA_MAIN_TC]` (127 trazas) de tiempo y giroscopio](analysis/s122_camera_main_tc/camera_main_tc.md): la capa de **TC** (timecode/gyro): 6 tramos de mensajes repartidos en GYRO/CALIB (32), DIST (13), APL/ApolloSA (47), SMART ZOOM (16) y DDT (18); 123 de 127 trazas vivas, 256 sitios PIC en 41 funciones y **17 publicadores** uniformes (cola OSAL, `osal_try_valloc_msg`), con el despachador **`ApolloSA_Main` `0x438730b0`** (`tbb` de 9 casos en `0x4387333e`) y **6 clientes de `[APL]`** (S119). La etiqueta es **nueva en fw3.21** (A7S/A6300: 0 trazas, 126/127 textos idénticos sin etiqueta). **No toca la línea del obturador** → S51 A/B/C = NO se mantiene. 40 tests.
- [S128: el mapa de etiquetado de la fw3.21: qué módulos son nuevos y cuáles se renombraron](analysis/s128_label_map/label_map.md): síntesis de 98 prefijos de módulo comparados texto a texto entre la A6000 fw3.21 y la A7S fw3.20: **58 son idénticos**, **18 "renombrados"** (la A7S tiene los mismos mensajes **sin etiqueta de módulo** y la fw3.21 los etiqueta: `[CAMERA_MAIN_YC]` 958/968, `[IMAGING_CAP]` 678/697, `[CAMERA_MAIN_SYNC]` 412/428, `[CAMERA_SA]` 228/231, `[CAMERA_MAIN_TC]` 122/125), 2 parciales y 20 propios → **la fw3.21 de la A6000 no reescribe el firmware: reescribe el logging**; el único cambio de contenido grande es `[CAM_IMAGER]` (179/371, S124). 6 tests.
- [S123: el módulo `[CAMERA_MAIN_CC]` (49 trazas) de control de captura](analysis/s123_camera_main_cc/camera_main_cc.md): la clase `CC` = el **control de captura**: 49 trazas en 6 tramos de `.rodata` (control 21, LUT 12, IE 8, miniRaw 2, MakerNote 2, CamCore-3DLUT 4), 47 referenciadas en 29 funciones y una **máquina de estados de 10 etapas** (`ExtractCaptureData`→`CaptureInit`→`SetReadImageParam`→`SetNRParam`→`SetOPDParam`→`AfterOPDAfterNR`→`SetDevelopParam`→`SetDualRecParam`→`SetDevDetectDevelopParam`→`WriteExifMakernote`); fija la **identidad de captura** (`CapMode`@`0x1c0`, `ExposureID`@`0x1b8`, `ContID`@`0x1bc`, `BDROSeq`@`0x6ec`, `FrameID`@`0x701`) y enlaza con `Stage_SACC.cpp`/`Stage_OPD.cpp` por una tabla de parámetros compartida. **La etiqueta `[CAMERA_MAIN_*]` no existe en la A7S ni en el A6300** (47/49 mensajes idénticos sin etiqueta). 32 tests.
- [S130: los 20 módulos "nuevos" del mapa de etiquetado: ¿contenido nuevo o solo otra etiqueta?](analysis/s130_new_modules/new_modules.md): al buscar el **núcleo** de cada mensaje en la A7S/A6300 solo **2 de los 20 son un cambio de etiqueta** (`[IDT_OPD]` 270/273 → `[IDT]`, `[DFE]` 11/11), 1 es parcial (`[JPEG]` 4/17) y **17 son contenido que no está en los otros dos firmwares** (`[ACCY]`, `[VPH_API]`, `[MOUNT_DEBUG]`, `[CAMERA_MAIN_LC]`, `[CLK_CTRL]`, `[DEPTH]`, `[PANDA]`…: sus tokens no aparecen ni una vez en la A7S ni en el A6300). Entre ellos, una **API de silenciador de obturador nueva** en la fw3.21 (`<shutter_mute_param>` `0x43ce3634`, `>shutter_mute_status<o/f:%d` `0x43ce3dfc`: 0 apariciones en A7S/A6300), aunque la traza del silenciador (`shutter mute on/off`, S118) sí está en las tres. 7 tests.
- [S127: el módulo `[CAMERA_MAIN_LC]` (72 trazas): AF, ZPD y DM AF](analysis/s127_camera_main_lc/camera_main_lc.md): el nombre engaña — **no calibra la lente**: es el módulo de **AF híbrido + ZPD + DM AF** (`Camera::LC` por RTTI, sigla **sin desarrollar**), con 78 sitios PIC en 37 funciones y 1 cadena muerta (`0x43c9c779`); el puente con el ZPD (S75) está en `LC_GetZpdResultInfo` `0x437c1e48` (cadena `0x43ca78c8`), cuyo gate es `ldrb.w [rX,#0xc0]` + `tst.w #2`. Material **propio de la A6000 fw3.21**: 0 prefijos y 0/72 mensajes coincidentes en A7S/A6300. **Sin efecto en S51**. 22 tests.
- [S121: el módulo `[AIP]` (37 trazas) de la interfaz de audio con el escalado](analysis/s121_aip/aip.md): la capa que gestiona el **audio** y su *fader* a través del acelerador: 6 sub-bloques RTTI (SaWrapper, SaBackUpCtrl, SaDriverBase, LPS, SaDriverZoomNr, SetFader) y **16 funciones**; callbacks `Ack`/`Comp`/`Err` en tres capas (SA `0x43926d1c`/`0x43926de8` con `[r1,#1]==0x14`/`0x13`, LPS `0x4392b16c`/`0x4392b254`); **tabla de backup de 350 entradas de 12 B** en `0x43bd1964` (`{id = 0x10c0000+n, offset, size}`) y `WriteShadow2BakcupArea` vuelca `0x10c` B. Su cliente es el **ADF** (S81: `[ADF][INIT]AUDIOIP INIT COMP` `0x43c26411`); no es el «SA» de S108 (`Camera::SaFuncDrv`). **A7S fw3.20: las mismas 37**; el A6300 añade 26 (`[AIP][ZNR_EE]*`). 97 tests.
- [S119: `[APL]`: la apertura/cierre de SA y HW dentro de `[CAMERA_SA]`](analysis/s119_apl/apl.md): las **42 apariciones de `[APL]` no son un módulo propio** — las 42 están **dentro** de mensajes que empiezan por `"[CAMERA_SA]: "` (`[CAMERA_SA]: [APL] HW Open Err %d` `0x43cebde1`…): es una **etiqueta de segundo nivel** dentro de `[CAMERA_SA]`; en la A7S fw3.20 esas mismas 42 cadenas **sí** empiezan por `[APL]`, así que la fw3.21 antepone la etiqueta de módulo. 5 funciones emisoras con 42/42 referencias 1:1, **un solo consumidor** (`[CAMERA_MAIN_TC]`, “ApolloSA”) y `unit_hndl` = handles del DMM (S113). 47 tests.
- [S118: el módulo `[SFRA]` (100 trazas) de la infraestructura escalar](analysis/s118_sfra/sfra.md): la fachada de cámara del framework `NS_SCALAR_INFRA` (verificado por los nombres de clase C++), con **17 comandos** cuyos ids se **decodifican de los bytes** en los predicados (`GET_INFO` `0x0100`/`0x10`, `GET_JPEG` `/0x20`, `SET_JPEG_PARAM` `/0x22`, `GET_SA_RESULT` `/0x30`, `SET_SA_NOTIFY` `/0x32`, `SET_PATH(OPEN)` `0x8120`…), despachador de finalizaciones con `TBB` de 5 bytes (`0x439a1654`) y núcleo `ScalarInfraAsyncMain` `0x439a1864`; 11 sub-bloques, 11 ficheros fuente. **A7S fw3.20: 100/100 mensajes idénticos** (y el A6300 añade 8 con nomenclatura antigua). 22 tests.
- [S117: `[AUGI]`, la cabecera de 32 B del códec](analysis/s117_augi/augi.md): 75 apariciones de `[AUGI]` → **26 cadenas** con ese prefijo y **49** con `[CodecIF][AUGI]…`; no es un subsistema de trazas sino el **nombre de una cabecera de bloque de códec**, con sus conversores nombrados en el binario (`DecExAugiConverter` `0x43c6a8db`, `DecInAudioAugiConverter` `0x43c6acc5`, `DecInVideoAugiConverter` `0x43c6b02e`, `EncExAugiConverter` `0x43c6b554`) y la entrada `StrmEngEncCIIf::CodecEventCreateVAUGI` `0x43c66fbf`; campos de la cabecera (`length`, `num_AUs`, `PTS`, `DTS`, `size_SPS/PPS`, `PictureType`…) y 86 puntos de emisión con 0 cadenas sin referencia. **A7S fw3.20: bloque idéntico** (mismas 75 apariciones y mismas 26 cadenas). 27 tests.
- [S116: el módulo `[SFRS]` (117 trazas) de control por *pins*](analysis/s116_sfrs/sfrs.md): el subsistema que gobierna los *pins* del sensor (`SETPIN`/`GETPIN`/`PINSEND`, `ReqYccAsap`, `YccOut`, `SendExecTrigger`, `CtSetAicParam`, `RC_CALLBACK`) con dos niveles de traza (`[DEBUG]`/`[ERR]`) y **131 puntos de emisión PIC en 52 funciones**compactas (`0x439a0000`–`0x439c0000`); sub-bloques: SUPERSTABLEMOVIE (37), MOTIONSHOTVIDEO (25), EFFECTMOVIEREC (23), PINSEND (12), SET_PATH_STATUS (9), SA (6), RC_AIC_TRIGGER (3), MULTIPLEXTRIGGER (2). En la A7S fw3.20 hay 151 cadenas: **117 comunes y 34 exclusivas de la A7S** → el módulo de la A6000 es un subconjunto. 23 tests.
- [S115: `[CAM_IMAGER]`, el driver del imager de la cámara](analysis/s115_cam_imager/imager_driver.md): 371 trazas (79 del ZIT ya de S80 → 292 del driver) en 94 funciones: el **transporte P2S** al sensor (canales **DFE0/DFE1**, datos **por páginas**, `P2SFormatter`, `CheckAddrOrder`), las interrupciones (`int_p2s_handler`, `int_timer_handler`), la **SIF** (sync code **en serie o en paralelo**), la API `ImagerCommon` de **un solo canal** hacia el **CISIF** y el serializador `SubLVDS`; sobre todo la **máquina de lectura/exposición por `drive_mode`**, con el campo **`shut`** en la traza de exposición (`0x43c93cc2`) y `SSBRK_ON`/`SIFSyncCode` al ejecutar → puntos de contacto directo con la línea del obturador (S56–S58). En la A7S fw3.20 el mismo driver está **sin etiqueta** y sin `SetExps`/`Execute0`. 9 tests.
- [S114: el motor de secciones de la captura, completo (17 ids ↔ 17 etapas)](analysis/s114_sections/section_engine.md): cierra la pregunta abierta de S106 — **15 de las 17 secciones** de la tabla `0x43ff8fb4` quedan nombradas: `0x01` = **Prelight** (nuevo: su manejador `0x437eb144` llama a `0x437eb07c`, que registra `CapturePrelight_Selector.cpp`) y las 14 restantes por su propio `*_Selector.cpp` (Exposure, Read, AfterRead, DevEntry, CorrectRaw, OpdBeforeNR, Develop, Marble, FeatureEffect, AfterEffect, Encode, AfterEnc, SortJpeg, DevExit); `0x00` y `0x06` **no tienen nombre** en el firmware (se describe su estructura) y 5 de los 16 selectores los registra código **fuera** de la tabla (`SequenceFilter` en 5 funciones) → hay selectores auxiliares. 9 tests.
- [S113: `[CAM_DMM]`, el gestor de memoria dinámico de la cámara](analysis/s113_cam_dmm/dmm_module.md): 54 trazas (todas de error) en `0x43cce6ae`–`0x43ccf1c3` y la implementación concentrada en **25 funciones contiguas** (`0x439011d8`–`0x43903d5c`); **11 operaciones** (`AllocNew`, `AllocNewRdv` = *rendezvous*, `AllocShare`, `Free`, `FreeRdv`, `Open`, `Close`, 4 `MemoryHandle::*` y las asíncronas `AsyncAllocNew`, `AsyncAllocRule`, `LoadExtraMap`) y **4 clases de error** (`ERR_DMM_RET_CODE`, `ERR_DMM_DIFFERENT_COMP` con `msg_id`/`my_id`, `ERR_DMM_HANDLE`, `ERR_DMM_OPEN`), más 4 de capa **OSAL** → la frontera DMM↔OSAL es real (S38); el userland `DmmAccess` de `libmprctrl.so` (S37) es **cliente** de este servidor, no una reimplementación. A7S fw3.20: 50/54 mensajes idénticos sin etiqueta. 11 tests.
- [S112: el módulo `[CAMERA_MAIN_SYNC]` (429 trazas) de sincronización de recursos](analysis/s112_camera_main_sync/camera_main_sync.md): el subsistema que coordina los recursos compartidos durante la captura — `SyncResMgr` (55 trazas: `Lock`/`Unlock`/`Free`/`Get` sobre `CAMDEV(0|1)`, RC y APL), volcado de registros `[CAM0]/[DDT]/[APL0]`, `DFS`/`DVS`, `Sync_Kick_IDT/RCH/RCV`, `HS_Sequence` y `int_HS timing`; **mapa función→traza completo** (430 funciones, 1 407 pares) y diferencial verificado: **418/429** mensajes existen también en la A7S fw3.20 sin la etiqueta (11 exclusivos: `Sync_Kick_*` con overflow, `SuperSlowMotion[Buffering]`, `EC::CapISO`…). 12 tests.
- [S111: el módulo `[TRK]` (215 cadenas) de tracking y detección](analysis/s111_trk/trk.md): el subsistema de **tracking** de la cámara, con 215 cadenas (207 textos distintos, 8 duplicados) en `0x43cebceb`–`0x43cfe31c` y **47 funciones**; sus sub-bloques son **STK** (76 trazas: *saliency*, *touch*, simulación de color/toque), **BT** (44), **EDTSA** (19), **PMV** (16), **IRO2G** (13), **DETSA** (9) y VAE/VAT/VOT; el código vive en `0x43a30000`–`0x43a39000` y trae **99 ficheros `FC/*.cpp`** embebidos. Diferencial A7S fw3.20: **las mismas 215 cadenas y 207 textos** (mismo número de sitios y funciones) → módulo idéntico, solo cambia su posición en el blob. 17 tests.
- [S110: `Camera::YC`, el motor de imagen de la A6000](analysis/s110_camera_main_yc/yc_engine.md): las **970 trazas** `[CAMERA_MAIN_YC]` (`0x43ca88f6`–`0x43ccd469`) describen el motor que calcula los parámetros del disparo: **API de 8 funciones** (`api_YC_InitCap` `0x437cf5f0`, `api_YC_SetCapBoks` `0x437d8c88`, `api_YC_SetSaCamDsp`…, `api_YC_DEV_SetCoodinate` `0x437d9d1c`) y **12 jobs** (`job_YC_SetParam`, `job_YC_CalcParam`, `job_YC_ModeManager` `0x4389f29e`, `job_YC_Initialize` `0x438aa574`…), con **141 sub-módulos etiquetados** (`SHD` 219, `ITP` 90, `YAP` 79, `DCV` 42, `OLC` 37, `NR` 36, `CLP` 29, `MARBLE` 24, `KKNR` 22, `PFR` 19); mapa **función→traza** de las 970 cadenas en **332 funciones** (960 referenciadas, 10 cadenas muertas) y **119 ficheros fuente** embebidos (`Sequence_*.cpp`, `yc_clp_common.cpp`, `init_cam_SetCamParam.cpp`…). **Diferencial A7S fw3.20**: los mismos mensajes existen sin la etiqueta → **969 de las 970** cadenas son comunes; la única nueva de la fw3.21 es `HD_SWEEP_HOLD =%x` (`0x43cbc27c`). 15 tests.
- [S109: el módulo `[CDIAG]` (270 trazas): el banco de diagnóstico del códec](analysis/s109_cdiag/cdiag.md): **7 escenarios** (HD REC/DEC, SD REC/DEC, JPEG ENC/DEC/ENCDEC) × **8 operaciones** (`DbgDiagAvc` `0x43c3b6df`, `CmpData` `0x43c3b72a`, `RunCodec` `0x43c3c123`, `SetMemArea`/`RelMemArea`, `SetData`, `ConfirmDoneCodec`, `SetDiagMode`) con **27 firmas `CDIAGER …`**, **16 clases** (RTTI) y su **tabla de registro** en `0x43fda6a0` (16 pares `{vtable base común, nombre}`); 118 funciones y 295 sitios de referencia, 226/255 cadenas referenciadas; habla con el núcleo por OSAL (`osal_rcv_msg`/`osal_snd_msg`). **A7S fw3.20: 270 cadenas idénticas, 0 exclusivas**; el A6300 añade 40 de 4K. 22 tests.
- [S108: el módulo `[CAMERA_SA]` (231 trazas) del acelerador escalar](analysis/s108_camera_sa/camera_sa.md): la capa de cámara que reporta los errores y el estado del SA (`Camera::SaFuncDrv`, S84) en 13 sub-bloques —APL (27), gestión de memoria (20), `GetAddr` (35), alineación de parámetros (29), paso de mensajes (18), parámetros DUALREC (14), cierre de handles (20), referencias `sa_func_*` (8) y códigos `SA_FUNCDRV_E_*` (3)—; la A7S fw3.20 y el A6300 fw2.01 tienen los **231/231 mensajes idénticos sin la etiqueta**: la fw3.21 solo añade el prefijo de módulo. 4 tests.
- [S107: `Camera::CamCore` y la pila de recursos `ResourceStack`](analysis/s107_camcore/camcore_resources.md): las 37 trazas `[CAMCORE]` de la fw3.21 de la A6000 (0 en la A7S fw3.20) describen la librería núcleo del controlador de cámara — SGC (`SgcTable`), RDC/PFR, AIF, `MemoryPool`/`ResourceBase`, `ExlHelper`, el *setter* de DMA, powersave y corrección de defectos (RTTI `N6Camera7CamCore8RdcImageE` `0x43c906b6`, `N6Camera7CamCore13SplitRdcImageE` `0x43cb0b94`); la pila `ResourceStack` (adquisición/liberación de recursos de CamCore, RC y DFE) se consume desde el gestor de captura (`[IMAGING_CAP]` `0x43ca10d1`–`0x43ca120f`). La fw3.21 **añade la etiqueta** `[CAMCORE]:`: los mismos mensajes (`ExlHelper`, `MonPowersave`, `ResourceStack)`) ya existían en la A7S sin etiqueta. 9 tests.
- [S106: `IMAGING_CAP`, el gestor de captura still de la A6000](analysis/s106_imaging_cap/imaging_cap_architecture.md): 697 trazas (`0x43c9b335`–`0x43ccab72`) y **83 nombres de fichero fuente embebidos** (`0x43ca8e14`–`0x43cb0cbe`) que reconstruyen el subsistema; **motor de secciones con 17 entradas** (`{id, manejador}` en `0x43ff8fb4`, 14 de ellas con su `Capture<Etapa>_Selector.cpp`), CapMgr con tabla de salto de 16 entradas, canal CAIF (`CAP_REQ`/`CAP_DATA`/`CAP_V_COM`), 8 modos `MODE_CAP*` del CamCore y la capa `ImageParam_Capture`/`RawMemManager`/DMM; esquema **PIC** de referencias a cadenas verificado (`694/697` referenciadas, 3 muertas); en la A7S fw3.20 el mismo subsistema **no lleva la etiqueta** `[IMAGING_CAP]`. 0 menciones del obturador → S51 sin efecto.
- [S105: panorámica/barrido (sweep), bracketing e intervalo](analysis/s105_panorama/panorama_bracket_interval.md): `CaptureManager::CaptureStart` (`0x437df646`) discrimina el modo con un campo de 2 bits del contexto `0x43e9b548` y, en el valor 2, pide la petición `0x301f` (`"!!! Can't send Panorama cmd"`); cadena `Stage_InitializeSweepAndSpoolBranch` → `PanoramaSweepStart` (`0x437e6b3c`) → `UpdateSweepCanvas` → `PanoramaSweepEnd` → `seq_panoramaClippingDecode` → `PanoramaStitch` (`0x438bcef8`); bracketing solo en el firmware como `lc_BracketAF.cpp` (`0x43ca79ba`); intervalo con `GetCaptureIntervalResource` (`0x437df338`), semáforo OSAL `CAPTURE_INTERVAL` y control por PTM (`[SDF] interval(PTM)` `0x43c7a1a5`, límite 900000 → `interval_ptm over 10[sec]`). 305 tests.
- [S104: prefijos de traza exclusivos de la A6000 sin decodificar](analysis/s104_prefixes/a6000_prefixes.md): seis prefijos que la A7S fw3.20 no tiene — `ADC_DEBUG` (ADC de 12 canales del LIRO), `AVR` y `AVOUT` (accesorios de `ACCY`), `ADR` (campo de dirección, no un módulo), `BKID` (*backup ID*) y `CAMCORE` (la librería `Camera::CamCore`); corrige S73 (cinco cadenas `ADJ ADC`, no cuatro).
- [S103: el subsistema SDF — la capa de *dataflow* de imagen still](analysis/s103_sdf/sdf_module.md): `[SDF]` (477 trazas) es el **ejecutor de trabajos de imagen still** al que el gestor de captura (`IMAGING_CAP`) envía **33 `MSG_ID_SDF_*`** (resize/rotate, encode/decode JPEG, CCNR, panorámica, THM, develop resize, face resize…); los 15 `[SDF_ERR]` son casi todos comprobaciones de **PTM** (el temporizador de imagen); en el userland, `OBJAVBBCBASECLASS::SdfCh`.
- [S102: menú principal (botón MENU), cadena de carga y apertura](docs/capture/s102-menu-principal.md): `libObj.so` → `viewUnified2.so` (registro de ~150 vistas, índices = `Vn` del log real) → `viewUnified3..8`; vistas BASE_MENU/GLOBAL_MENU/SETTINGMENUX/FNMENU; `DefRootView::ActionOpen*` es el árbitro de arranque, no la tecla MENU; evento de MENU sin demostrar. Anexos: [APK por función](analysis/apk-por-funcion/README.md), [decompilación de apps](analysis/decomp-apk/README.md).
- [S101: selector del tipo de mecanismo y consumidores de los campos de ajuste (A6000 vs A7S)](docs/capture/s101-conclusions.md): `+0x238`/`+0x280` solo se escriben; Darwin nunca fija el tipo (3 lectores, 0 escritores en A6000/A7S/A6300); selector A6000 `0x4379316a` sobre `[G+0x808]&7` (por defecto tipo 0) frente al de A7S por el byte `+0x7a`; plan de pruebas físicas pendientes. S51 se mantiene.
- [S100: el contrato de comandos del ADF (firmware) ↔ `AdfCh` (userland)](analysis/s100_adf_contract/adf_command_contract.md)
- [S99: la arquitectura del userland — las capas de `libObj.so`](analysis/s99_userland/userland_architecture.md)
- [S98: `libBizFw.so` — el orquestador userland y el puente con el ADF](analysis/s98_bizfw/bizfw_bridge.md)
- [S97: sincronización audio/vídeo del codificador](analysis/s97_encsync/encoder_sync.md)
- [S96: modos de captura — `drive_mode`, `CapMode` y la tabla 69 → 14 ShdMode](analysis/s96_modes/capture_modes.md)
- [S95: los ficheros que la cámara lee y escribe](analysis/s95_files/file_inventory.md)
- [S94: la API HAPI de la app remota](analysis/s94_hapi/hapi_api.md)
- [S93: el bus de mensajes OSAL del userland](analysis/s93_osal_bus/osal_message_bus.md)
- [S92: la base de datos de medios — SceneInfo, MovieFile e índice](analysis/s92_mediadb/media_database.md)
- [S91: submódulos del framework ADF (ADJ, SYSND, GS, FACE, AFNR, CH_SRC)](analysis/s91_adf/adf_submodules.md)
- [S90: reproducción de vídeo — PlayArranger, VFC y VDISP](analysis/s90_playback/playback.md)
- [S89: el módulo `IDT`/`IDT_OPD` — mapas del imager, FOPD e IDTSA](analysis/s89_idt/idt_opd_maps.md)
- [S88: GOLFSHOT (disparo de golf por sonido) y MOTIONSHOT](analysis/s88_shotmodes/golfshot_motionshot.md)
- [S87: almacenamiento, sistema de archivos y tarjeta](analysis/s87_storage/storage_filesystem.md)
- [S86: el subsistema del visor — `VDF` (marco de display) y `VEF` (visor electrónico)](analysis/s86_vdf_vef/vdf_vef_viewfinder.md)
- [S85: `CLK_CTRL` (control de reloj) y `VPH_API` (API del vídeo del visor)](analysis/s85_clk_vph/clk_ctrl_vph_api.md)
- [S84: el API del motor de imagen (SA) — catálogo de `sa_func_*`](analysis/s84_sa_api/sa_api_catalogue.md)
- [S83: los módulos "menores" del firmware, decodificados](analysis/s83_modules/minor_modules.md)
- [S82: AutoFraming y las etapas de control del pipeline](analysis/s82_autoframing/autoframing_stages.md)
- [S81: ADF — framework de arranque, MSGQ, MMGR y comandos DBGCMD](analysis/s81_adf/adf_framework.md)
- [S80: ZIT — corrección de defectos del sensor (DDC) en el imager](analysis/s80_zit/zit_defect_correction.md)
- [S79: mapa de módulos del firmware por prefijos de log](analysis/s79_modules/module_map.md)
- [S78: parámetros `apc_*` del motor de imagen YC](analysis/s78_apc/yc_apc_params.md)
- [S77: Creative Style y balance de blancos](analysis/s77_pp/picture_profile_creative_style.md)
- [S76: pipeline de captura (etapas `Stage_*`) y motor de imagen](analysis/s76_stages/stage_pipeline.md)
- [S75: ZPD (zone plate detection) — calibración del sensor con datos de la lente](analysis/s75_zpd/zpd_subsystem.md)
- [S73/S74: protocolo de ajuste de fábrica `ADJ_CMD` (panel/EVF/OLED) y `ContrastPlus`](analysis/s73_adj/adjust_cmd_recon.md)
- [S72: wireless y transferencia remota (WLAN / PlayMem / "Camera on Demand")](analysis/s72_wlan/wlan_playmem.md)
- [S71: subsistema de detección de caras y objetos (FC/FRC)](analysis/s71_frc/frc_subsystem.md)
- [S70: reconocimiento del subsistema EIS/gyro](analysis/s70_is/is_gyro_recon.md)
- [S69: subsistema de audio de la A6000 (línea general)](docs/capture/s69-audio-subsystem.md)
- [S68: gestión de batería, energía y carga (NP-FW50)](docs/capture/s68-battery-power.md)
- [S66: montura de lente E-mount (línea general, sin relación con SilentShutter)](docs/capture/s66-lens-mount.md)
- [S64: prueba en cámara de SilentShutter](docs/capture/s64-silent-ram-nvram-test.md)
- [S62: PMCA — inyección de código, service shell y la propiedad `modelName`](docs/capture/s62-pmca-injection.md)
- [S61: origen de los parámetros IMX210 y flujo de mensajes](docs/capture/s61-conclusions.md)
- [S60: emisor de mensajes IMX210 y receptores A7S](docs/capture/s60-conclusions.md)
- [S59: validación cruzada Claude + GPT-6.1 Sol](docs/capture/s59-conclusions.md)
- [S58: productores AE y configuración efectiva A7S Silent](docs/capture/s58-conclusions.md)
- [S57: semántica de ID1/SSB/svd-shd-spl, Silent IMX235, XPI y sincronía P2S](docs/capture/s57-conclusions.md)
- [S56: transporte de registros del IMX210 (IDs = direcciones 16 bit, P2S/DFE0), CISIF = receptor](docs/capture/s56-conclusions.md)
- [S55: origen de los pares GPIO (base de backup BK4), A7S vs A6000](docs/capture/s55-conclusions.md)
- [S54: P4C, tipo de mecanismo 0 y sincronización BIONZ](docs/capture/s54-conclusions.md)
- [S53: parser CAIF de Darwin, A7S vs A6000](docs/capture/s53-conclusions.md)
- [S52: mecanismo Silent Shooting A7S y viabilidad en A6000](docs/capture/s52-parallel-conclusions.md)
- [S51: decisión SÍ/NO sobre exposición totalmente electrónica](docs/capture/s51-decision.md)
- [S50: conclusiones conjuntas Claude + Codex](docs/capture/s50-parallel-conclusions.md)
- [S49: productor de configuración de captura](docs/capture/s49-capture-config-producer.md)
- [S48: proveedor del servicio de registro `+0x1ec`](docs/capture/s48-service-table-provider.md)
- [S47: entrada del payload y orden de C](docs/capture/s47-payload-producer-and-order.md)
- [S46: base VD y escritor del contexto](docs/capture/s46-vd-base-and-context-identity.md)
- [S45: contexto y consumidor real del timing IMX210](docs/capture/s45-context-identity-and-physical-closure.md)
- [S44: consumidor de registros y tabla de modos](docs/capture/s44-register-consumer-mode-table.md)
- [S43: tabla PIC y códigos de modo IMX210](docs/capture/s43-exposure-mmio-and-lock-codes.md)
- [S42: identidad de la llamada de exposición](docs/capture/s42-exposure-call-identity.md)
- [S41: productores de mensajes y snapshots](docs/capture/s41-message-origin-imx210.md)
- [S40: origen del contexto de modo](docs/capture/s40-context-origin-imx210.md)
- [S39: enum de imagen y discriminador APL](docs/capture/s39-image-format-apl.md)
- [S38: frontera DMM/OSAL en av-cam](docs/capture/s38-dmm-osal-static-frontier.md)
- [S37: definidor DMM en libmprctrl](docs/capture/s37-libmprctrl-dmm-extents.md)
- [S36: memoria de libInfraScalarMpr](docs/capture/s36-libinfra-scalar-mpr-memory.md)
- [S35: objetos DFE y frontera estática APL/IRQ](docs/capture/s35-dfe-objects-static-frontier.md)
- [S34: APL/DMA frente a VD e interrupciones](docs/capture/s34-apl-dma-vd-interrupts.md)
- [S33: origen de los handles YC](docs/capture/s33-yc-rendezvous-producer.md)
- [S32: callbacks VD y SyncYCout](docs/capture/s32-vd-callbacks-sync-ycout.md)
- [S31: subsistema CAMERA_MAIN_SYNC/DFECore](docs/capture/s31-camera-main-sync-strings.md)
- [S30: receptor y retorno de EncodeStill](docs/capture/s30-pipelines-capture-encode.md)
## Fases recientes (más nuevas primero)
Cada enlace lleva a su informe; el resumen de hallazgos está en el [catálogo](docs/capture/linea-general-re.md) y en el [historial](docs/history/README-historial-2026-10-21.md).

## Agentes (Claude Code, Codex/ChatGPT, DeepSeek Harness)

Reglas en `AGENTS.md` y `CLAUDE.md`; skills en `.claude/skills/` y `.agents/skills/`
(copias idénticas, verificadas por `tests/test_agent_skills_sync.py`). Instalación de
REA/Ghidra, MCP y arranque de sesión: [docs/agent/README.md](docs/agent/README.md).
Para ChatGPT web: [docs/agent/chatgpt-pack.md](docs/agent/chatgpt-pack.md).
Entorno: `python scripts/agent/check_env.py`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `docs/` | Documentación: arquitectura, captura (`docs/capture/`), historial, referencias |
| `analysis/` | Un directorio por hito (`sNN_*`), con informe y datos |
| `tests/` | Un test por hito + utilidades |
| `scripts/` | Herramientas, conocimiento (`scripts/knowledge/`), agente |
| `knowledge/` | Estado (`CURRENT.md`), progreso e índices derivados |
| `src/` | Inventario, atlas, LIRO |
| `tools/`, `reports/`, `references/`, `research/`, `work/` | REA/Ghidra, informes, fuentes públicas, notas |
| `firmware/` | Firmware Sony original/extraído (en `.gitignore`, no se publica) |

## Subproyecto: obturador electrónico

- Pruebas físicas pendientes (no ejecutadas): [docs/capture/physical-test-plan.md](docs/capture/physical-test-plan.md).
- Decisión vigente: **no parchear** (S51, [decisión SÍ/NO](docs/capture/s51-decision.md)); categoría E, evidencia insuficiente; ni viabilidad ni imposibilidad demostradas.
- Conclusiones: [S50](docs/capture/s50-parallel-conclusions.md) · [S52 viabilidad A6000](docs/capture/s52-a7s-a6000-feasibility.md) · [EFCS](docs/capture/efcs-capture-selector.md) · [estado Silent](docs/capture/silent-shutter-status.md) · [traza](docs/silent-shutter-trace.md).
- Referencia comparativa: A7S 3.20 ([A6300 vs A6000](docs/capture/a6300-silent-comparison.md)).

## Documentos generales

[Alcance](docs/project-scope.md) · [Arquitectura](docs/architecture/README.md) · [Captura](docs/capture/README.md) · [Inventario físico](docs/hardware-inventory.md) · [Atlas ELF](docs/elf-classification.md) · [Dependencias](docs/subsystem-dependencies.md) · [Arranque y recuperación](docs/boot-and-recovery.md).

## Reproducción local sin instalar paquetes

Desde este directorio:

```sh
python3 -m src.inventory firmware/extracted/fw321 reports/inventory.json
python3 -m src.inventory firmware reports/firmware-inventory.json
python3 -m src.atlas
python3 -m src.liro firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin reports/silent-liro-dispatch.json --base 0x43541000 --table 0xabe30c --count 220
python3 -m unittest discover -s tests -v
/home/nicolas/Documents/GPREMIUM/ingreso-agentes/.venv/bin/ruff check src tests
/home/nicolas/Documents/GPREMIUM/ingreso-agentes/.venv/bin/mypy --ignore-missing-imports src
```

Extracción: `7z x firmware/original/Update_ILCE6000V321.dmg -ofirmware/extracted/updater` y `/home/nicolas/.local/share/pmca-venv/bin/python references/fwtool/fwtool.py unpack -f firmware/extracted/updater/Update_ILCE6000V321/Resources/FirmwareUpdater.app/Contents/Resources/FirmwareData_ILCE6000V321.dat -o firmware/extracted/fw321`.

La CLI real necesita `-f` y `-o`: el ejemplo posicional del proyecto base no corresponde a esta versión.
La extracción WBI por CLI falla al intentar interpretar recursivamente una sección como ext2. La alternativa ejecutada fue iterar `fwtool.sony.wbi.readWbi`, guardar `chunk.contents.read()` y registrar `physicalAddr`, `virtualAddr`, tamaño y SHA-256 en `reports/wbi-sections.json`. Véase el procedimiento completo en `docs/firmware-analysis.md`.

679 ELF ARM confirmados por readelf; 45 archivos con coincidencias de palabras
clave en la búsqueda inicial. El inventario total incluye contenedores,
derivados y duplicados: sus tamaños no deben sumarse como memoria del dispositivo.
El atlas reutiliza metadatos por hash y productor; se comprobaron 679 aciertos
en la segunda pasada. Los snapshots REA conservan evidencia, pero no sustituyen
un proyecto persistente de Ghidra ni garantizan evitar una nueva importación.

## Validación

Veintiséis pruebas correctas; ruff y mypy sin avisos en `src tests`. TDD aplicado
a inventario, atlas, símbolos versionados, roles ELF y agregación de
dependencias, referencias Thumb y extracción LIRO. Registro actual:
reports/shutter-validation.md; registro previo: reports/atlas-validation.md. Dos archivos
auxiliares del DMG no legibles se registran como errores; el payload y el
firmware están inventariados y los 679 ELF se analizaron sin errores.

Repositorio Git inicializado y publicado en `github.com/nicolvus/a6000-fw-decomp` (rama `main`); desde S54 cada fase se commitea y se sube. `firmware/` está en `.gitignore`: los artefactos de firmware no se publican. Inicialmente no se instalaron paquetes. Después, el usuario autorizó hacer funcionar REA: se instaló REA localmente y se extrajeron Ghidra/JDK portables. No se ejecutaron programas del firmware.

## REA operativo

REA 6.5.0 instalado en `tools/rea` con versión y dependencias fijadas en package-lock.json. Ghidra 12.1.4 y Temurin JDK 21 portables, sin modificar paquetes del sistema. Descargas y hashes verificados: `reports/rea-provider-downloads.json`. Registro MCP aplicado a `/home/nicolas/.codex/config.toml`, con respaldo `.rea.backup`; reiniciar Codex para cargarlo.

```sh
./scripts/rea doctor --client codex --provider ghidra --json
./scripts/rea analyze "$PWD/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha16_unpacked_unpacked/lib/libcamera.so" --provider ghidra --json
```

Comprobado: protocolo MCP initialize, 207 herramientas, binary_session, diagnóstico Ghidra/Codex y análisis ARM real. En este sandbox, la comprobación Java desde Node requiere ejecución autorizada fuera de la restricción EPERM; no confundir ese fallo con ausencia del JDK. Binwalk, Unblob y JADX siguen pendientes; no son necesarios para el ELF ya extraído.

## Empezar desde cero (clon nuevo + firmware 3.21 recién descargado)

**Para agentes de IA:** ejecutar `scripts/agent/bootstrap.sh` (idempotente, `--dry-run` disponible) y seguir el runbook [docs/agent/bootstrap-desde-cero.md](docs/agent/bootstrap-desde-cero.md) (verificación, orientación, REA, ciclo de fase y límites). Lo siguiente es el desglose manual de esos mismos pasos.

Los binarios (firmware, Ghidra, JDK, `node_modules`, `.venv`) no están en Git: se reconstruyen así.
Todo desde la raíz del repo; Linux x86_64.

```sh
# 1. Clonar y entrar
git clone https://github.com/nicolvus/a6000-fw-decomp.git sony-a6000-electronic-shutter && cd sony-a6000-electronic-shutter

# 2. Firmware oficial 3.21 (Mac updater) y verificación
mkdir -p firmware/original && cd firmware/original
curl -L -o Update_ILCE6000V321.dmg "https://support.d-imaging.sony.co.jp/download/NEX/AcicwqgUEQ/Update_ILCE6000V321.dmg?fm=am"
sha256sum Update_ILCE6000V321.dmg   # esperado: 844349ff7edddc294c0fddd90a454848eeda8987b6bf043c9757982b3a42ba3e
cd ../..

# 3. Entorno Python (herramientas, tests, grafo de conocimiento)
python3 -m venv .venv && . .venv/bin/activate && pip install pytest ruff mypy pyyaml capstone unicorn

# 4. Desempaquetar con fwtool (vendorizado en references/fwtool; necesita sus dependencias Python, ver su README)
7z x firmware/original/Update_ILCE6000V321.dmg -ofirmware/extracted/updater
python references/fwtool/fwtool.py unpack \
  -f firmware/extracted/updater/Update_ILCE6000V321/Resources/FirmwareUpdater.app/Contents/Resources/FirmwareData_ILCE6000V321.dat \
  -o firmware/extracted/fw321
# Si falla la extracción WBI anidada: procedimiento alterno en docs/firmware-analysis.md
# Comprobación: firmware/extracted/fw321/firmware.fdat debe tener SHA-256
#   603b42ec9d2dd66b91e38c15a6a23e860fb8af46a072050903506672036f0f90 (firmware/hashes/sha256.json)

# 5. Inventario y atlas ELF (679 ELF ARM esperados)
python3 -m src.inventory firmware/extracted/fw321 reports/inventory.json
python3 -m src.atlas

# 6. REA + Ghidra + JDK locales (versiones y hashes en reports/rea-provider-downloads.json)
(cd tools/rea && npm ci)                      # rea-agents 6.5.0 (Node 22/24)
mkdir -p tools/providers   # descomprimir aquí ghidra_12.1.4_PUBLIC y jdk-21.0.12.1+1 (URLs en el JSON)
./scripts/rea doctor --client codex --provider ghidra --json

# 7. Binario principal para REA: av-cam.bin (base 0x43541000, ARM)
mkdir -p analysis/rea-independent/input
cp firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin analysis/rea-independent/input/

# 8. Comprobar todo y arrancar el grafo de conocimiento
python scripts/agent/check_env.py --sha
python3 scripts/knowledge/index_docs.py && python3 scripts/knowledge/build_graph.py
python -m pytest tests -q
```

Después de instalar:

1. Leer [knowledge/CURRENT.md](knowledge/CURRENT.md) y [docs/STATE.md](docs/STATE.md) (restricciones y política de RE).
2. Registrar los MCP `rea` y `sony-a6000-knowledge` ([docs/agent/README.md](docs/agent/README.md#mcp-claude-code-y-codex)); ajustar las rutas absolutas de `.mcp.json` a tu clon.
3. Abrir **una sola** sesión REA (`av-cam.bin` tarda ~8 min en frío): `python analysis/rea-independent/bin/session_daemon.py <sock> "$(cat analysis/rea-independent/exp2-open-args.json)"` (ajustar `path` al clon) y consultar por lotes con `bin/q.py <sock> guion.json`; cerrarla al acabar el hito.
4. Antes de reutilizar un hallazgo: skill `contradiction-audit`; antes de buscar a mano: `knowledge-navigation`; tras editar `.md`: `knowledge-maintenance`.
5. Reglas que no cambian: sin ejecutar firmware, sin flasheo, REA primero y verificar lo decisivo contra bytes. Foco actual: obturador electrónico (decisión vigente S51: no parchear).
6. Para saber qué falta, ver [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md) y los «Próximo» del final de [knowledge/PROGRESS.md](knowledge/PROGRESS.md).
