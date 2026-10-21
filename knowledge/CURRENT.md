# Estado actual — léeme primero

Resumen operativo breve. Para el historial completo de decisiones, ver `knowledge/PROGRESS.md`.
Para restricciones del proyecto (sin firmware ejecutado, sin flasheo, sin `git push`), ver `docs/STATE.md`.

[Plan de pruebas físicas pendientes](../docs/capture/physical-test-plan.md) (P1–P8, ninguna ejecutada; requieren tu autorización).

## S109 — el módulo `[CDIAG]` (270 trazas): el banco de diagnóstico del códec (21-10-2026, línea de RE general)

**VERIFICADO (22 tests, `tests/test_s109_cdiag.py`):** 270 tokens `[CDIAG]` (`0x43c3b0d4`–`0x43c3e86a`): 255 cadenas que empiezan por `[CDIAG]` y 15 `[ERR][CDIAG]`. Estructura: **7 escenarios** (HD REC/DEC, SD REC/DEC, JPEG ENC/DEC/ENCDEC) × **8 operaciones** (`DbgDiagAvc` `0x43c3b6df`, `CmpData` `0x43c3b72a`, `RunCodec` `0x43c3c123`, `RelMemArea` `0x43c3b768`, `SetMemArea` `0x43c3b7ec`, `SetData` `0x43c3c162`, `ConfirmDoneCodec`, `SetDiagMode` `0x43c3bf5c`), **27 firmas `CDIAGER …`**, **16 clases** (RTTI: `8CdCtrlIf` `0x43c3b67e` … `13CdUtilSysvMsg` `0x43c3e8ab`) y **2 ficheros** (`cdCtrlIf.cpp` `0x43c3b1a8`, `cdCtrlCore.cpp` `0x43c3b86c`). **Tabla de registro de clases** en `0x43fda6a0`: 16 pares `{vtable base común 0x43fd04f8, puntero al nombre RTTI}` (en la A7S, `0x43fdb6ec`) → es una tabla de **resolución clase→nombre**, no de vtables por clase. 118 funciones (`0x435a127a`–`0x435a50b6`), 295 sitios de referencia; **226/255** cadenas referenciadas y **29 muertas** (ni PIC ni puntero absoluto). Transporte por **OSAL**: `osal_rcv_msg` `0x43561260`, `osal_snd_msg` `0x4356120c`, `osal_free_msg` `0x435612ec`, `osal_try_valloc_msg` `0x435612d0`; el núcleo de la tarea (`0x435a1318`) llega a `osal_rcv_msg` vía `0x435a9f4c` (bl en `0x435a9f68`); escritor `0x435ab880` (310 llamadas), nivel `0xbe`, id `0xbad`.

**Diferencial A7S fw3.20**: 270 tokens, **270 cadenas comunes y 0 exclusivas** en ningún sentido, mismas 16 clases, 2 ficheros y 27 firmas → módulo **idéntico**. El A6300 fw2.01 tiene 310 tokens = 270 + **40 de 4K** (`[CTRL4KREC]`, `CdCtrl4KDec/Rec`, `CdExt*`, `CodecDiagLog`).

**Negativo verificado**: 0 menciones de `shutter`/`silent`/`imager`/`sensor`/`dmm` en las 270 trazas → sin efecto sobre S51.

[Informe](../analysis/s109_cdiag/cdiag.md) · [doc](../docs/capture/s109-cdiag.md). Siguiente: formato de `MSG_SENS_COMMAND`/`DIAGINFO`; codificación numérica de `cmd`/`mode`/`func`; emisor de los comandos `SENS_*`; fichero fuente de las clases de códec (no embebido).

## S116 — el módulo `[SFRS]` (117 trazas) de control por *pins* (21-10-2026, línea de RE general)

**VERIFICADO (23 tests, `tests/test_s116_sfrs.py`):** 117 cadenas `[SFRS]` en `0x43ce7661`–`0x43ceb8c4`; **131 puntos de emisión PIC** (`ldr rX,[pc,#imm]` + `add rX,pc`) y **52 funciones**, todas dentro de `0x439a0000`–`0x439c0000` (módulo compacto y localizado), **0** cadenas sin referencia. Sub-bloques: SUPERSTABLEMOVIE 37, MOTIONSHOTVIDEO 25, EFFECTMOVIEREC 23, PINSEND 12, SET_PATH_STATUS 9, SA 6, RC_AIC_TRIGGER 3, MULTIPLEXTRIGGER 2. Contenido: `SETPIN`/`GETPIN`/`PINSEND` con `file=%s line=%d`, `ReqYccAsap`, `YccOut`, `SendExecTrigger`, `CtSetAicParam`, `RC_CALLBACK`. Evidencia de código: `SETPIN` `cmp r1,#1` en `0x439aada4` (línea 58 en `0x439aadc0`), `GETPIN` `cmp` en `0x439aae3c` (línea 56: `movs r2,#0x38` en `0x439aae4c`), cola de `EXECUTE_PIN_SEND` en `0x439b1f4c`–`0x439b1f6c` (lee `[r4,#0x3f4..0x3ff]`, escribe `[r4,#0x410]=1` y `[r4,#0x40c]`, traza `0x43ceb80d`).

**Diferencial A7S fw3.20**: la A7S tiene **151** cadenas `[SFRS]`: **117 comunes, 0 exclusivas de la A6000 y 34 exclusivas de la A7S** → el módulo de la A6000 es un **subconjunto** del de la A7S.

**Observación**: 40 de las 52 funciones no imprimen `file=%s`, así que no se les puede asignar fichero fuente; de las 24 clases `.cpp` citadas solo 12 se localizan en el código.

[Informe](../analysis/s116_sfrs/sfrs.md) · [doc](../docs/capture/s116-sfrs.md). Siguiente: significado de SFRS, AIC, RC, VFX, IIB y PINSEND; si `line=%d` corresponde al `.cpp` de `file=%s` (falta la tabla de líneas); semántica de los tres modos de grabación.

## S117 — `[AUGI]`: la cabecera de 32 B del códec (21-10-2026, línea de RE general)

**VERIFICADO (27 tests, `tests/test_s117_augi.py`):** 75 apariciones de `[AUGI]` → **26 cadenas** con el prefijo `[AUGI]` y **49** con `[CodecIF][AUGI]…`; dos *clusters* de cadenas: los **impresores de estructura** (`0x43c6a909`–`0x43c6b517`, con los nombres de campo `length`, `num_AUs`, `PTS`, `DTS`, `nextHRDBuffer`, `nextPTS`, `size_SPS`, `size_PPS`, `PictureType`, `seq_parameter_set_id`) y el **volcado de depuración** `[AUGI] campo = %d` (`0x43cd993d`–`0x43cd9c8d`). **No es un subsistema de trazas**: es el nombre de una **cabecera de bloque de códec**, y las clases que la manipulan están nombradas en el binario: `DecExAugiConverter` `0x43c6a8db`, `DecInAudioAugiConverter` `0x43c6acc5`, `DecInVideoAugiConverter` `0x43c6b02e`, `EncExAugiConverter` `0x43c6b554`, más la entrada de API `StrmEngEncCIIf::CodecEventCreateVAUGI` `0x43c66fbf`. 86 puntos de emisión y **0** cadenas sin referencia; los impresores ocupan 4 funciones contiguas `0x436150ce`–`0x436163c0` y el dumper `0x4391ca90`. **La sigla no aparece expandida en ningún byte** (no se inventa su significado) y no se afirma qué cuenta `length`.

**Diferencial A7S fw3.20**: **idéntico** — mismas 75 apariciones y mismas 26 cadenas.

[Informe](../analysis/s117_augi/augi.md) · [doc](../docs/capture/s117-augi.md). Siguiente: qué cuenta exactamente `length`; el layout binario de la cabecera; el emisor de `CodecEventCreateVAUGI`.

## S118 — el módulo `[SFRA]` (100 trazas) de la infraestructura escalar (21-10-2026, línea de RE general)

**VERIFICADO (22 tests, `tests/test_s118_sfra.py`):** 100 trazas `[SFRA]` en `0x43ce5a16`–`0x43ce7723` (100 textos distintos), 11 sub-bloques (`[CMD]`, `[CMP]`, `[BUF]`, `[RATECONTROL]`, `[RC]`, `[NOTIFY]`, `[ERROR]`/`[ERR]`, `[WARNING]`, `[SFR_ERR_NOTREADY]`), 11 ficheros fuente (`ScalarInfraAsyncMain.cpp`, `SfrJpegBuffer.h`, 7× `ScalarInfraSequence*.cpp`, `SfrYc.cpp`, `DrvCallRc.cpp`) y 47 funciones. **`SFR` = `NS_SCALAR_INFRA` verificado por los nombres de clase C++** de la zona `[SFR]`, no por conjetura. **17 comandos** con los **ids decodificados de los bytes** en los predicados `0x43b63xxx` (tipo de mensaje en `+0x02`, sub-comando en `+0x0f`): `0x0100`/`0x10` GET_INFO, `/0x20` GET_JPEG, `/0x22` SET_JPEG_PARAM, `/0x30` GET_SA_RESULT, `/0x32` SET_SA_NOTIFY, `/0x42` LiveView SET_JPEG, `0x8110` SET_PATH(CLOSE), `0x8120` SET_PATH(OPEN), `0x9010` GET_INFO_CMP; despachador de finalizaciones `0x439a1640` con `TBB` de 5 bytes en `0x439a1654`; núcleo `ScalarInfraAsyncMain` `0x439a1864`.

**Diferencial A7S fw3.20**: **100/100 mensajes idénticos** y en el mismo orden (mismo conjunto, mismos sitios y funciones) → módulo **idéntico**, solo cambia su posición en el blob (`0x7a4a16` en la A6000 frente a `0x7998c4` en la A7S). El A6300 fw2.01 tiene **108** trazas: las 100 de la A6000 más 8 con nomenclatura antigua (`CMD_JPEG`, `CMD_LIVEVIEW`, `SET_PATH_CMP(JPEG CLOSE)`, `LiveViewStageIdle::exec openReq/closeReq`…).

[Informe](../analysis/s118_sfra/sfra.md) · [doc](../docs/capture/s118-sfra.md). Siguiente: la correspondencia de los 5 casos del `TBB` con los nombres `[CMP]`; 5 ids de sub-comando sin traza propia; el papel de `RC`/`VFX`/`IIB`.

## S121 — el módulo `[AIP]` (37 trazas): la interfaz de audio con el escalado (21-10-2026, línea de RE general)

**VERIFICADO (97 tests, `tests/test_s121_aip.py`):** 37 cadenas `[AIP]` en `0x43cdd844`–`0x43cdec50`; **16 funciones** y 6 sub-bloques RTTI: `SaWrapper` (8), `SaBackUpCtrl` (12), `SaDriverBase` (4), `LPS` (11), `SaDriverZoomNr` (1), `SetFader` (1). **Callbacks `Ack`/`Comp`/`Err` en tres capas**: SA (`0x43926d1c`/`0x43926de8`, con los predicados `[r1,#1]==0x14`/`0x13`), LPS (`0x4392b16c`/`0x4392b254`) y driver; los errores llevan `errCode`+`errState` (SA) o `ErrCode`+`ErrStatus` (LPS). **Tabla de backup**: **350 entradas de 12 B** en `0x43bd1964` con `{id = 0x10c0000 + n, offset, size}`; `WriteShadow2BakcupArea` vuelca `0x10c` B (`mov.w r0,#0x10c` en `0x4392ab78`) y `SetAudioNrType` publica el **bit 3** de `bkId = 0x10e0000`. Comandos hacia el escalar en `0x4392ac30` (`Cmd`/`Func` + `Zma`/`Ext`/`Mbx`) y `0x4392acb4` (`Cmd`/`Func`/`Unq`). Buffers LPS `0x82`/`0x83`/`0x85` con longitudes `0x2c`/`0x28`/`0x14`; `SetFader` (`0x4355ae98`) divide por 100/20/otro según `[r0,#0x78]`.

**Quién lo usa**: el **ADF** (S81): `[ADF][INIT]AUDIOIP INIT COMP` `0x43c26411`, tipos `AUDIO_IP_CONFIG_TYPE_*` `0x43c264fa`–`0x43c2659e` y comandos `SetAip0/1`, `GetSa0/1`, `SetSa`, `SetFader`, `SetZoomNr`. **No** es el «SA» de S108 (`Camera::SaFuncDrv`, `sa_func_*`): ninguna de las 37 trazas lo menciona.

**Diferencial**: A7S fw3.20 tiene **las mismas 37**; el A6300 fw2.01 tiene **63** = 37 + 26 (25 `[AIP][ZNR_EE]*` y `SetInstanceNumberExec Err %d`).

**Aporte metodológico (rectificó todo el repo)**: el subagente cuantificó los falsos positivos de cada regla de emparejamiento PIC (estricta 37/37 reales; kill analysis 60 pares = 37 verdaderos + **23 falsos**) y el caso concreto donde falla (`0x4355bcb2` resuelve a `0x43ceb58b`, no a `0x43cde863`, cuyo sitio real es `0x4392ab04`). Con la calibración de S118 (`[SFRA]`: 118 reales = 118 con la regla estricta, 166 con kill analysis, 186 con la ancha) se declaró **regla canónica estricta** y se rectificaron S106, S110, S113 y S115.

[Informe](../analysis/s121_aip/aip.md) · [doc](../docs/capture/s121-aip.md). Siguiente: significado de AIP/SA/LPS/ANR/ZNR/Zma/Ext/Mbx; formato de la cola `AudioIpCmdQueue`; contenido de las 350 entradas del backup.

## S119 — `[APL]`: la apertura/cierre de SA y HW, dentro de `[CAMERA_SA]` (21-10-2026, línea de RE general)

**VERIFICADO (47 tests, `tests/test_s119_apl.py`):** las **42 apariciones de `[APL]` no son un módulo propio**: las 42 están **dentro** de cadenas que empiezan por `"[CAMERA_SA]: "` (13 bytes), p. ej. `[CAMERA_SA]: [APL] HW Open Err %d` `0x43cebde1`, `[CAMERA_SA]: [APL] SA Open Err` `0x43cebe03`, `[CAMERA_SA]: [APL] Calloc InputPrm Err` `0x43cebe46` → **`[APL]` es una etiqueta de segundo nivel dentro de `[CAMERA_SA]`** y la entrada "APL 42" del mapa de módulos de S79 es una sub-etiqueta. 5 funciones emisoras (`0x439cea30` Open 7 trazas, `0x439cebe4` Close 9, `0x439cedd0` Free&Close 4, `0x439ceeb8` Open+ejecución 20, `0x439cf3b8` SA open/close 2) con **42/42 referencias PIC 1:1** bajo la regla estricta; las 5 equivalentes de la A7S en `0x439bcd80`, `0x439bcea0`, `0x439bcfc8`, `0x439bd05c`, `0x439bd3a4`. API: `ExecuteOpenMSG` `0x439d143c`, `ExecuteCloseMSG` `0x439d133c`, `ExecuteCalcStartMSG` `0x439d185c`, `CallocCamSaParam` `0x439d0f58` (la traza la llama *InputPrm*), `GetMemInfo` `0x439d1bd0`, `GetExecUnit` `0x439d168c` (la traza dice *GetZimaNo*); los `unit_hndl` son **handles del DMM** (S113: open `0x43903280`, close `0x43903414`, free `0x43902fbc`).

**Consumidor único**: `[CAMERA_MAIN_TC]` ("ApolloSA"), **un solo llamador** por función (`0x438765ca`, `0x43876650`, `0x438766da`, `0x43876714`, `0x43876a82`); ni `[IMAGING_CAP]` (S106) ni `CamCore` (S107) lo llaman.

**Diferencial A7S fw3.20**: los 42 textos coinciden uno a uno, pero allí **empiezan por `[APL]`** (`[APL] HW Open Err %d` `0x43ce1588`) → la fw3.21 de la A6000 **antepone la etiqueta de módulo** `[CAMERA_SA]: `. El A6300 fw2.01 tiene las mismas 42.

**Aporte metodológico (tercera calibración)**: la regla "ancha" da **67** pares para 42 cadenas reales → 25 falsos positivos comprobados desensamblando. Con S118 (`[SFRA]` 118) y S121 (`[AIP]` 37) son **tres** módulos donde la regla **estricta** coincide exactamente con la verificación a mano.

[Informe](../analysis/s119_apl/apl.md) · [doc](../docs/capture/s119-apl.md). Siguiente: el módulo `[CAMERA_MAIN_TC]` ("ApolloSA"), su consumidor, que sigue sin hito propio; layout de `InputPrm`; por qué la traza dice *GetZimaNo* si la función es `GetExecUnit`; los códigos de error (2, 6, 8, 0xff).

## S111 — el módulo `[TRK]` (215 cadenas) de tracking y detección (21-10-2026, línea de RE general)

**VERIFICADO (17 tests, `tests/test_s111_trk.py`):** 216 apariciones del literal `[TRK` → **215 cadenas** (214 que empiezan por `[TRK` + 1 anidada: `[TRK]: [TRK] cb_func == NULL`) → **207 textos distintos** (8 repetidos en dos direcciones cada uno) en `0x43cebceb`–`0x43cfe31c`, con **288 sitios de referencia** y **47 funciones** (283 strict + 5 relaxed). Sub-bloques: **STK** 76 trazas (saliency, touch, simulación de color y de toque), **BT** 44, **EDTSA** 19, **PMV** 16, **IRO2G** 13, **DETSA** 9, VAE/VAT/VOT 3 cada uno, más las familias STK_AUTO_SAL / STK_COLOR_SIM / STK_TOUCH_SIM. El código del módulo vive en `0x43a30000`–`0x43a39000` (284 sitios, 43 funciones) y los 4 restantes son *wrappers* de sesión en `0x439c0000`–`0x439d0000`; las zonas `sa_stubs` (ZIT), `fc` y `apl_osal` tienen 0 sitios. El firmware embebido incluye **99 ficheros `FC/*.cpp`** (`0x43cef12a`–`0x43cf707a`).

**Diferencial A7S fw3.20**: la A7S tiene **las mismas 215 cadenas y los mismos 207 textos** (listas `only_a6000`/`only_a7s` vacías) y los mismos recuentos (288 sitios, 47 funciones) → **módulo idéntico**, solo cambia su posición en el blob (`0x43ce1492`–`0x43cee615`).

**Nota metodológica**: el subagente usó la regla estricta (*nearest-ldr*, `MAX_GAP=0x40`); con la regla canónica del repo (todos los `ldr` del registro en 4 KB, aceptando solo destinos en el inicio de una cadena) las 215 cadenas dan **214 referenciadas y 657 sitios**. Además se **`ancho el rango de cadenas válidas** de `scan_pic_refs.py` (estaba fijo a `0x43c90000`–`0x43cd0000` y excluía la zona de `[TRK]`, lo que daba 0 referencias)**: ahora acepta `LO HI RUTA_SALIDA` y cubre toda la imagen.

[Informe](../analysis/s111_trk/trk.md) · [doc](../docs/capture/s111-trk.md). Siguiente: límites de las funciones `0x43a376d8`/`0x437a37734`; semántica de los 2 sitios *relaxed*; correspondencia 1:1 de los 99 ficheros `FC/*.cpp` con funciones.

## S115 — `[CAM_IMAGER]`: el driver del imager de la cámara (21-10-2026, línea de RE general)

**VERIFICADO (9 tests, `tests/test_s115_cam_imager.py`):** 371 trazas `[CAM_IMAGER]` (79 del módulo ZIT, ya de S80 → **292 del driver**) en **94 funciones** (`0x43543568`–`0x436dbd66`). **P2S**: dos canales (**DFE0**, **DFE1**), datos **por páginas** (`P2SData[Page:%01x]` `0x43c931d6`), `P2STransferSize` `0x43c931b2`, `P2SFormatter` `0x43c932ac`, `P2S CheckAddrOrder: ORDER ERROR !` `0x43c9327c`, `P2SWaitTransComp` `0x43c93180`, `P2S : Unsupported SyncMode.` `0x43c93156` → es el camino que S56 ("transporte de registros del IMX210, P2S/DFE0") siguió en la línea del obturador. **Interrupciones**: `int_p2s_handler` (+`_dfe0`/`_dfe1`), `int_timer_handler` y el temporizador por canal (`Imager TimerSetFunc/TimerStart Error!! [CH:%02x, err:%02x]`). **SIF** (11 trazas): `SetSyncCode` distingue **sync code en serie** (`0x43c94e55`) o **en paralelo** (`0x43c94e92`), más `SetSIFMode`, `SetSIFSigsel`, `SetDitherSet`, `SetDataEnableParam`, `ReadSIFScodeCnt`, `SyncCodeDetNum`, `SIF AD_MODE`. **`ImagerCommon`** (16): API "macro" hacia el **CISIF** (`Update_IIFINSEL`, `SetCISIFRequest`, `GetCISIFSyncCodeRequest`, `MacroPowerOn/SaveOn/OffRequest`, `Update_CISIFConnectParam`, `Update_MacroRxEnable`), 8 de ellas con `do not use CH_1` → **un solo canal**. **`SubLVDS`** (9): PowerOn/PowerSave/ChangeParam/GetReceiverEnable por bloque, con `SUBLCNTL_DFE1 does not exist on Regulus`.

**Punto de contacto con la línea del obturador**: la exposición y la lectura se programan **por `drive_mode`**: `SetExps : [PrevDrv][NowDrv][NextDrv][svd][shd][spl][shut]` `0x43c93cc2` (**campo `shut`**), `SetExpsZ` `0x43c939b5` (`svrz`, `shrz`, `splz`, `epd`, `epdsel`), `SetRead` `0x43c93fcb` (`AGainCont_EC`, `AGainCont`, `AGainDrv`), `SetReadZ` `0x43c93d67`, `Execute : […][SSBRK_ON][SLEEP_ON]` `0x43c94076`, `Execute. […][SSBRK_ON][SIFSyncCode]` `0x43c940d7`, `Execute0/1` `0x43c93ae2`/`0x43c9413a` (`ssb`, `read`, `svr`), `SetMode […][ntpal]` `0x43c93b2f`. El campo **`shut`** y el **SSB** son los puntos que conectan con S56–S58 (ID1/SSB).

**Diferencial A7S fw3.20**: 0 trazas con el prefijo, pero el mismo driver (P2S, SubLVDS, ImagerCommon, SIF, NTPAL, SSBRK) existe **sin etiqueta** y con menos instrumentación: `SetExps`, `Execute0` y `AGainCont` tienen **0** apariciones en la A7S.

**NO VERIFICADO**: el significado de `svd`, `shd`, `spl`, **`shut`**, `epd`, `epdsel`, `ssb`, `read`, `svr`, `ntpal` (el firmware no expande las siglas) y si `shut` difiere entre A6000 y A7S. Nada de esto **modifica** S51 (A/B/C = NO): no hay ningún mensaje de obturador electrónico.

[Informe](../analysis/s115_cam_imager/imager_driver.md) · [doc](../docs/capture/s115-cam-imager.md). Siguiente: decodificar la tabla de parámetros por `drive_mode` (69 modos, S96) y el significado de `shut`.

## S112 — el módulo `[CAMERA_MAIN_SYNC]` (429 trazas) de sincronización de recursos (21-10-2026, línea de RE general)

**VERIFICADO (12 tests, `tests/test_s112_camera_main_sync.py`):** 429 cadenas `[CAMERA_MAIN_SYNC]` en `0x43c9b409`–`0x43cb5616` (tras reextraerlas: el borrador del subagente apuntaba **un byte después** del inicio real y no cortaba el texto en el NUL). Contenido: **`SyncResMgr`** (55 trazas: `Lock`/`Unlock`/`Free`/`Get` sobre `CAMDEV(0|1)`, RC y APL), volcado de registros `[CAM0]`/`[DDT]`/`[APL0]`, `DFS`/`DVS` (11+5), `Sync_Kick_IDT`/`RCH`/`RCV`, `HS_Sequence` (5) e `int_HS timing`; 101 sub-bloques distintos (160 sin etiqueta, `SyncResMgr` 55, `APL_ERR` 17, `jpeg` 13, `DFS` 11, `Sequence_Movie` 9). **Mapa función→traza completo** (regla estricta): 425 cadenas referenciadas, 489 sitios (las que más emiten: `0x4354d740` 57, `0x43728dec` 44, `0x43812848` 40, `0x43812f34` 35, `0x437298e8` 32, `0x4379bb90` 29).

**Diferencial A7S fw3.20** (verificado byte a byte, ignorando especificadores de formato): 0 trazas con el prefijo y **418/429** mensajes comunes; los **11** exclusivos de la A6000 son `CamOutV` `0x43ca2de1`, `CamV` `0x43ca35b6`, `CONNETCT_COMP err` `0x43ca3fe7`, `DISCONNETCT err` `0x43ca4045`, `SuperSlowMotion[Buffering] error` `0x43cb0ded`, `Sync_Kick_IDT: overflow` (2), `Sync_Cam_Setting: DIST_RSLT_NG …` `0x43cb10f7`, `Sync_Kick_RCH: overflow` (2) y `EC::CapISO Error` `0x43cb55dd`.

[Informe](../analysis/s112_camera_main_sync/camera_main_sync.md) · [doc](../docs/capture/s112-camera-main-sync.md). Siguiente: significado de `Sync_Kick_IDT/RCH/RCV` y del contador `%d/8V`.

## S114 — el motor de secciones de la captura: 17 ids ↔ 17 etapas (21-10-2026, línea de RE general)

**VERIFICADO (9 tests, `tests/test_s114_sections.py`):** cierra la pregunta abierta de S106. **15 de las 17 secciones** de la tabla `{id u32, manejador u32}` de `0x43ff8fb4` quedan **nombradas**: `0x01` = **Prelight** (nuevo: el manejador `0x437eb144` llama a `0x437eb07c`, que registra `CapturePrelight_Selector.cpp`) y las 14 restantes por su propio `*_Selector.cpp` (`0x02` Exposure, `0x03` Read, `0x04` AfterRead, `0x05` DevEntry, `0x07` CorrectRaw, `0x08` OpdBeforeNR, `0x09` Develop, `0x0a` Marble, `0x0b` FeatureEffect, `0x0c` AfterEffect, `0x0d` Encode, `0x0e` AfterEnc, `0x0f` SortJpeg, `0x10` DevExit). **`0x00` (`0x437eabfc`) y `0x06` (`0x437eaa5c`) no tienen nombre** en el firmware: `0x00` es un selector puro de perfil (2 llamadas: `0x43ae75dc` obtener contexto, `0x43ae76ca` fijar modo) que elige un registro de 20 B según el modo; `0x06` tiene la misma forma que `0x01` pero sin llamar al selector de Prelight. Además **5 de los 16 nombres los registra código fuera de la tabla** (`SequenceFilter` en 5 funciones con 14 registros; `CapturePrelight` en 2; `CaptureDevelop`+`CaptureMarble` en una compartida) → existen **selectores auxiliares** que no son secciones.

**Método**: referencia PIC de la cadena → prólogo Thumb → si el sitio cae dentro del manejador, ese es el selector; si no, sus llamadas `bl` (capstone) → `0x01` llama al selector de Prelight.

[Informe](../analysis/s114_sections/section_engine.md) · [doc](../docs/capture/s114-section-engine.md). Siguiente: significado de `0x00` y `0x06`; la tabla de 20 B por sección; la relación entre secciones (`SectionQueueManager.cpp` `0x43caaf62`, `SectionEndFunc.cpp` `0x43caea54`).

## S113 — `[CAM_DMM]`: el gestor de memoria dinámico de la cámara (21-10-2026, línea de RE general)

**VERIFICADO (11 tests, `tests/test_s113_cam_dmm.py`):** 54 trazas `[CAM_DMM]` (todas de error) `0x43cce6ae`–`0x43ccf1c3`, con la implementación en **25 funciones contiguas** `0x439011d8`–`0x43903d5c`. **11 operaciones**: `AllocNew` (4), `AllocNewRdv` (4, *rendezvous*, confirmado por `MemoryHandle::AllocRendezvous` `0x43cceb4c`), `AllocShare` (4), `Free` (2), `FreeRdv` (2), `Open` (3), `Close` (2), 4 `MemoryHandle::*` (5) y las asíncronas `AsyncAllocNew` (9, función `0x439037c0`), `AsyncAllocRule` (7, `0x43903b80`), `LoadExtraMap` (7, `0x43903d5c`). **4 clases de error** del DMM: `ERR_DMM_RET_CODE` (10), `ERR_DMM_DIFFERENT_COMP` (10, con `msg_id`/`my_id` → la unidad pertenece a otro componente), `ERR_DMM_HANDLE` (4), `ERR_DMM_OPEN` (5); y **4 de capa OSAL** en las asíncronas (`ERR_OSAL_MSGQ`, `ERR_OSAL_HANDLE`, `ERR_OSAL_UIPC`, `rcv Invalid Src!`) → la frontera **DMM↔OSAL** del firmware es real (S38). El userland `DmmAccess` de `libmprctrl.so` (S37: `DmmAllocateNEWAndOpen_body`, `DmmShare`, `DmmCloseORFree_body`, `GetUnitHandleFromDmmAlloc`, `GetDMMRetMsg`) es **cliente** de este servidor, no una reimplementación.

**Diferencial A7S fw3.20**: 0 trazas con el prefijo; **50 de las 54** tienen mensaje equivalente sin etiqueta; las 4 restantes son `AllocNew`, que en la A7S se registraba como `AllocNew(DMM_OPTION_NOUNIT_WARN): ERR_DMM_RET_CODE!: %x` (`0x43cb4f99`) y que la fw3.21 sustituyó por cuatro mensajes detallados.

[Informe](../analysis/s113_cam_dmm/dmm_module.md) · [doc](../docs/capture/s113-cam-dmm.md). Siguiente: valores numéricos de `ERR_DMM_*`/`ERR_OSAL_*`; formato del mensaje OSAL asíncrono; tabla de reglas de `AsyncAllocRule`.

## S108 — el módulo `[CAMERA_SA]` (231 trazas) del acelerador escalar (21-10-2026, línea de RE general)

**VERIFICADO (4 tests, `tests/test_s108_camera_sa.py`):** 231 trazas `[CAMERA_SA]` en `0x43cc5286`–`0x43cef0d8`: la capa de cámara que reporta errores y estado del acelerador escalar (`Camera::SaFuncDrv`, S84), en 13 sub-bloques —APL (27), gestión de memoria (20), errores `GetAddr` (35), alineación de parámetros (29), paso de mensajes/mailbox (18), parámetros DUALREC (14), cierre de handles (20), referencias `sa_func_*` (8), errores especiales (4) y códigos `SA_FUNCDRV_E_OSAL/RSLTCODE/ERRCODE` (3)— más 51 de contenido mixto. **8 de las 19 familias `sa_func_*`** de S84 tienen traza directa aquí (`BDEX_exit`, `BFNR_release`, `BOKS`, `LFNR`, `KKNR`, `NFLASH`, `YKNR`, `DUALREC_BAYER`).

**Diferencial**: la A7S fw3.20 y el A6300 fw2.01 tienen **0** trazas con la etiqueta y los **231/231** mensajes **idénticos sin ella** → la fw3.21 solo añade el prefijo de módulo.

**Correcciones de la revisión** (agente principal): el borrador ponía "Parámetros Inválidos: 17" y omitía la categoría "Otros" (las 13 filas sumaban 195, no 231); daba `ExlHelper`/`MonPowersave` por presentes en `[CAMERA_SA]` (no lo están: son de `[CAMCORE]`, S107); y afirmaba que el A6300 tenía más trazas (tiene las mismas 231, sin etiqueta).

[Informe](../analysis/s108_camera_sa/camera_sa.md) · [doc](../docs/capture/s108-camera-sa.md). Siguiente: atribución función→traza (el esquema PIC de S110 permite hacerla) y el formato binario del mailbox del SA.

## S110 — `Camera::YC`: el motor de imagen de la A6000 (21-10-2026, línea de RE general)

**VERIFICADO (15 tests, `tests/test_s110_camera_main_yc.py`):** `[CAMERA_MAIN_YC]` = **970 trazas** `0x43ca88f6`–`0x43ccd469` en 4 bloques. **API de 8 funciones**: `api_YC_InitCap` `0x437cf5f0`, `api_YC_SetCapBoks` `0x437d8c88`, `api_YC_SetCapStar` `0x437cfe94`, `api_YC_SetCapTbox` `0x437d88e4`, `api_YC_SetSaCamDsp` `0x437ce0cc`/`0x437d77a8`/`0x437d8940`, `api_YC_SetVdPreParam` `0x437d0768`/`0x437d5608`/`0x437d9a04`, `api_YC_LfnrSetParam` `0x437d8bd4`, `api_YC_DEV_SetCoodinate` `0x437d9d1c`. **12 jobs**: `job_YC_Initialize` `0x438aa574`, `job_YC_ModeManager` `0x4389f29e`, `job_YC_SetParam` (15 sitios), `job_YC_SetParamOn` `0x438b7c48`, `job_YC_SetParamOff` `0x438b7ba4`, `job_YC_SetParamPrelight` `0x4389b80c`, `job_YC_SetPreParam` `0x4388bb54`, `job_YC_SetSaCamDspParam` `0x4388b2c4`, `job_YC_CalcParam` (14 sitios), `job_YC_SetCapBoks` `0x4387f4b0`, `job_YC_SetCapStar` `0x438aec84`, `job_YC_GetTagPointer` (19 sitios). **141 sub-módulos etiquetados**: `SHD` 219, `ITP` 90, `YAP` 79, `DCV` 42, `OLC` 37, `NR` 36, `CLP` 29, `MARBLE` 24, `KKNR` 22, `PFR` 19 (las siglas **no están expandidas** en el firmware). **Mapa función→traza**: 968 cadenas en **304 funciones** (1 756 pares), **958** referenciadas (kill analysis) y **2 cadenas muertas** confirmadas (ni PIC ni puntero absoluto). **119 ficheros fuente** embebidos en la zona: `Sequence_Common.cpp` `0x43cb14a1`, `Sequence_Movie.cpp` `0x43cb31f1`, `yc_clp_common.cpp` `0x43cb81ac`, `init_cam_SetCamParam.cpp` `0x43cb40b8`, `SyncLoader.cpp` `0x43cb397a`, `CS_ExifMakerNote.cpp` `0x43cc56dc`, `ddl_stitch.cpp` `0x43cc6964`… **Comprobación cruzada con S78** (Ghidra): la atribución PIC da `job_apc_main_stl` → `0x438b3ea8` y `job_apc_main_mov` → `0x438b5810`, las mismas direcciones de S78.

**Diferencial A7S fw3.20**: 0 cadenas con el prefijo (los mismos mensajes existen sin etiqueta) y, comparando el texto sin prefijo, **969 de las 970** cadenas de la A6000 existen también en la A7S; la única traza nueva de la fw3.21 es `HD_SWEEP_HOLD  =%x` (`0x43cbc27c`).

**Corrección de método (arrastrada a S106):** el escáner PIC emparejaba cada `add rX,pc` con el `ldr` más cercano del registro y se detenía en el primer destino válido; como el registro se reutiliza, atribtaba mal algunas referencias. Corregido (se prueban todos los `ldr` del registro en 4 KB y solo se aceptan destinos que caen en el inicio de una cadena): S106 pasa de 694/697 a **696/697** (de 3 cadenas muertas a **1**, `0x43ca9b12`).

[Informe](../analysis/s110_camera_main_yc/yc_engine.md) · [doc](../docs/capture/s110-camera-main-yc.md). Siguiente: significado de las siglas (SHD, ITP, DCV, OLC, CLP, PFR…); tabla de despacho de jobs (no localizada); enlace por código entre `api_YC_SetCapBoks/Star/Tbox` y las etapas `Stage_BOKS/STAR/TBOX`; sentido de `HD_SWEEP_HOLD`.

## S107 — `Camera::CamCore` y la pila de recursos `ResourceStack` (21-10-2026, línea de RE general)

**VERIFICADO (9 tests, `tests/test_s107_camcore.py`):** 37 trazas `[CAMCORE]` en la fw3.21 de la A6000 (`0x43c905ca`→`0x43cebcb2`) y **0** en la A7S fw3.20. RTTI: `N6Camera7CamCore8RdcImageE` `0x43c906b6` y `N6Camera7CamCore13SplitRdcImageE` `0x43cb0b94`. Contenido: SGC (`GetFlowType: No SgcTable` `0x43c905ca`), RDC/PFR (memoria PFR `0x43c90846`/`0x43c9088e`, `PFR in width[%d] > 596` `0x43c90ca3`), AIF (`AIF%d out[%d] > memsize[%d]` `0x43c90a96`, `pbl_aif_set_func` `0x43c90abd`, extents 1 o 2), `MemoryPool has no space.` `0x43c908e7`, `ResourceBase::Release was called without acquire` `0x43c90ec5`, `ExlHelper` (5 cadenas `0x43c90f98`–`0x43c91074`), *setter* de DMA (6 cadenas `0x43c910a4`–`0x43c91160`), `MonPowersave` `0x43c90f07` y corrección de defectos (`Acl::CAMHEAD_Z1C::setDefectPt` `0x43cebcb2`). **Las siglas (SGC, RDC, PFR, AIF, Exl) NO están expandidas en el firmware**: cualquier desarrollo es hipótesis.

**Pila `ResourceStack`**: 4 mensajes dentro del bloque `[IMAGING_CAP]` (`0x43ca10d1` `ResourceStack)CamCore Release Error!`, `0x43ca110d` `rcct_Release err RC`, `0x43ca11c2` `Dfe Release Error!`, `0x43ca120f` `ResStack) GetMemIndex Err handle`) → la pila de recursos de CamCore la consume el gestor de captura still (S106).

**Corrección de la revisión** (agente principal): el borrador daba por no verificada la presencia de `ExlHelper` (5) y `MonPowersave` (1) en la A7S — **existen** en ambos blobs, sin etiqueta; la fw3.21 solo **añade la etiqueta** `[CAMCORE]:`/`[IMAGING_CAP]:`. También se corrigieron los sitios de referencia de las trazas `sa_func_DUALREC_*` (los reales: `0x437ed95e`, `0x437ee4ae`, `0x437ee716`, `0x437eeb34`, `0x437ee84e`).

[Informe](../analysis/s107_camcore/camcore_resources.md) · [doc](../docs/capture/s107-camcore-resources.md). Siguiente: significado de SGC/RDC/PFR/AIF/Exl; formato interno de la ResourceStack; por qué 2 de las 5 cadenas `ExlHelper` no tienen referencia PIC.

## S106 — `IMAGING_CAP`: el gestor de captura still de la A6000 (21-10-2026, línea de RE general)

**VERIFICADO (18 tests, `tests/test_s106_imaging_cap.py`):** `[IMAGING_CAP]` = **697 trazas** `0x43c9b335`–`0x43ccab72` en 11 bloques; es el **gestor de captura still** (no el pipeline de vídeo, no el obturador). En el mismo bloque de cadenas el firmware lleva **83 nombres de fichero fuente** (`0x43ca8e14`–`0x43cb0cbe`): 16 `*_Selector.cpp`, 10 `CaptureUtility*.cpp`, 9 manejadores, 6 `RawMemManager*.cpp`, 8 `Stage_*.cpp`, `CaptureManager*.cpp`, `SectionController.cpp`, `CaifCom_Control.cpp`, `NotifyController.cpp`, `ImageParamCapture*.cpp`… → así se reconstruye la arquitectura real. **Motor de secciones**: tabla de **17 entradas** `{id u32, manejador u32}` en `0x43ff8fb4`; el despachador `FUN_437e534c` copia `0x88` B y busca el id entre 17; cada manejador devuelve un bloque de **20 B (5 u32)** con los parámetros de la sección, elegido según el modo de captura; 14 de los 17 referencian su `Capture<Etapa>_Selector.cpp` (`Exposure`, `Read`, `AfterRead`, `DevEntry`, `CorrectRaw`, `OpdBeforeNR`, `Develop`, `Marble`, `FeatureEffect`, `AfterEffect`, `Encode`, `AfterEnc`, `SortJpeg`, `DevExit`); los ids `0x00`, `0x01`, `0x06` no lo hacen y `CapturePrelight`/`SequenceFilter` se referencian fuera de la tabla → asignación id↔etapa completa NO VERIFICADA. **CapMgr**: eventos `LastDetectionEnd` `0x43ca9caa`, `NotifySyncStart` `0x43ca9cf2`, `StartRawSequence` `0x43ca9dc7`, `EndRawSequence` `0x43ca9e81`, `CaptureEnd` `0x43ca9d55`, `CheckLastDet` `0x43ca9dfd`, `CaptureCancel_PowerOffDetect` `0x43ca9d85`; el despachador `FUN_437ddf4c` salta con una tabla de 16 entradas en `0x43bc4e08`. **CAIF**: `CAP_REQ`/`CAP_REQ_CLR`/`CAP_SETTING`/`CAP_START`/`CAP_DATA`/`CAP_V_COM` con dirección `[EN->CA]`/`[CA->EN]`/`[CA->AVIP]` (`0x43cca4fb`–`0x43cca8c3`); `CAP_*` son nombres de mensaje del protocolo, no estados internos. **CamCore**: 8 modos de adquisición (`MODE_CAP`, `MODE_CAP_DRP`, `MODE_CAP_PREREVIEW`, `MODE_CAP_SNR`, `MODE_CAP_SNR_PREREVIEW`, `MODE_SNR_BUS_THROUGH`, `MODE_SNR_BUS_THROUGH_PREREVIEW`, `MODE_CDET`). **Memoria**: `ImageParam_Capture_Base` AddRef/Release/ALL Released (`0x43ca9842`–`0x43ca99d0`), `RawMemManager` (MemPool/MemBuffer/MemRuleLib/UnitTypeLib), `GetMem_*`/`ShareMem_StlRaw8`/`UseRaw_DualRec`/`FreeRaw_DualRec`, DMM (`SetDmmInfo) FATAL! overwrite` `0x43ca9bd1`. **Método**: las cadenas no se apuntan con punteros absolutos, sino con el esquema PIC `destino = literal_del_pool + (add rX,pc + 4)` (verificado con `0x437284da`→`0x43c9b335` y `0x437f5b4a`→`0x43cad93c`): **690 de las 697** cadenas referenciadas (regla canónica *estricta*); las **7** restantes (los cuatro `DistV_RC`/`DistH_RC`, `0x43ca9b12` `ShareMem_StlRaw8 Err…`, `0x43cc7d5c` `%s: ContrastPlus error` y `0x43cc839c` `Rch_Rcv_Zima_Base Err…`) no tienen referencia alguna (ni PIC ni puntero absoluto) → cadenas muertas. *(La «corrección» de S110, 694→696, se apoyaba en una regla que inventa referencias; la kill analysis tampoco es exacta. La regla canónica es la estricta, validada a mano en `[SFRA]` y `[AIP]`. Metodología: `analysis/s106_imaging_cap/pic_xref_methodology.md`.)* **Diferencial A7S fw3.20**: 0 cadenas con el prefijo `[IMAGING_CAP]`; los mismos mensajes existen **sin etiqueta** (`CapMgr) LastDetectionEnd…` `0x43cae3b3`, `SectionCtrl) Fatal!…` `0x43caefd1`) → la fw3.21 **añade la etiqueta**; los 16 `*_Selector.cpp` están en A6000, A7S y A6300.

**Negativo verificado:** 0 apariciones de `shutter`/`silent`/`EFCS`/`curtain`/`mechan` en las 697 trazas → el gestor de captura no registra nada del obturador. **Sin efecto en S51 (A/B/C = NO).**

[Informe](../analysis/s106_imaging_cap/imaging_cap_architecture.md) · [doc](../docs/capture/s106-imaging-cap.md). Siguiente: ids de sección sin nombre (`0x00`, `0x01`, `0x06`); significado de los 20 B por sección; formatos binarios de CAIF y `MSG_ID_SDF_*`.

## S105 — panorámica/barrido, bracketing e intervalo (21-10-2026, línea de RE general)

**VERIFICADO (305 tests, `tests/test_s105_panorama.py`):** `CaptureManager::CaptureStart` (`0x437df646`) discrimina el modo con un **campo de 2 bits** del contexto de captura `0x43e9b548`; en el valor 2 pide la petición **`0x301f`** (`movw r0,#0x301f` en `0x437df7a2`; error `[IMAGING_CAP]: !!! Can't send Panorama cmd` `0x43caa019`). Cadena: `Stage_InitializeSweepAndSpoolBranch` (`0x437f0838`) → `Stage_Panorama::PanoramaSweepStart` (`0x43549020`) → `PanoramaSweepStart` (`0x437e6b3c`, abre/cierra el encoder JPEG por trama) → `UpdateSweepCanvas` (`0x437e751c`, `seq_brcEncode()`) → `PanoramaSweepEnd` (`0x437e6e78`, `cmp_execStitchPreProcess()` + `cmp_checkFillResidual()`) → `seq_panoramaClippingDecode` (`0x43780eb4`) → `PanoramaStitch` (`0x438bcef8`: `seq_initStitch`/`seq_panoramaParallelStitch`/`seq_endStitch`) → `PanoramaResize`/`PanoramaResizeEncode`. El stitch es **por tiras** (`PanoramaStripSequence::StripInfo` `0x438f4bcc` consume `PreProcessResult::Strip[]` `0x43ccd5fa`); el **número de capturas no está en el firmware** (lo decide el userland). **Bracketing**: en el firmware solo `lc_BracketAF.cpp` (`0x43ca79ba`) → 2 métodos de `Camera::LC` (`0x437c74b6`, `0x437c7554`); el bracketing de EV/WB lo orquesta `libObj.so`. **Intervalo**: `GetCaptureIntervalResource` (`0x437df338`), semáforo OSAL `CAPTURE_INTERVAL` (`0x43caa2b1`–`0x43caa3f8`) y control por PTM (`[SDF] interval(PTM) %ld` `0x43c7a1a5`, límite 900000 → `[SDF_ERR] interval_ptm over 10[sec]` `0x43c7a1be`).

**NO VERIFICADO:** N de capturas, acrónimo CCNR, unidad del timer OSAL y del PTM, valor concreto del campo de 2 bits, clase LC del bracketing, ids `0x3005`/`0x301f`, algoritmo de `exec_tanzaku`.

[Informe](../analysis/s105_panorama/panorama_bracket_interval.md) · [doc](../docs/capture/s105-panorama-bracket-interval.md). Siguiente: el número de capturas (userland) y el significado del campo de 2 bits del contexto.

## S102 — menú principal (botón MENU): carga y apertura (21-10-2026, línea de RE general)

[S102](../docs/capture/s102-menu-principal.md): `libObj.so` → `viewUnified2.so` (registro de ~150 vistas; índices = `Vn` del log real) → `viewUnified3..8`; vistas BASE_MENU/GLOBAL_MENU/SETTINGMENUX/FNMENU; `DefRootView::ActionOpen*` es el árbitro de arranque, no la tecla MENU. Abierto: evento base de MENU y la vista de disparo que abre BASE_MENU (requiere log de RAM tras pulsar MENU). Anexos: APK por función y decompilación de apps (solo local).

## S101 — selector del tipo de mecanismo y consumidores de campos de ajuste (21-10-2026; etiquetado S70/S71/S72 en commits)

[Conclusiones S101](../docs/capture/s101-conclusions.md) — resumen consolidado; los apartados siguientes son el detalle.

### Recorrido de los 12 puntos abiertos

**VERIFICADO (3 tests, `tests/test_s101_pending.py`):** el bloque de 12 u16 `+0xdd0` lo escribe `0x437b1048` (bytes de estado de captura); la copia en bloque `0x438acc24`/`0x4389efc2` es de un bloque de parámetros con **mapa idéntico en A6000 y A7S** (no la estructura de captura desplazada): **S52 sigue vigente** (rectificado, había una afirmación errónea en la primera versión de S71); `0x437881a8` es el `bl` de init de arranque y `0x43802614` el comando `0x402e`; `Backup 0x3e0005` solo lo leen 2 sitios (cadena de 0x18 B). Los 12 puntos están cerrados (2, 8, 9, 11 como bloqueados/no resolubles; 10 con el grafo de menciones `analysis/s101_shutter_type/graph/module_graph.md`; 12 cubierto por S98/S100). **S51 se mantiene.**
[Informe](../analysis/s101_shutter_type/pending/report.md). **Selector de tipo:** A7S `cap+0x78c = 0x4379ec04(...)` y tipo 2 ⟸ byte `[X+0x7a]≠0` (opción Silent, inferencia) ⇒ `cap+0x748=1`; **A6000 sí tiene selector** (`0x4379316a`, `tbb` sobre `[G+0x808]&7`: 1→tipo 2, 2..6→tipo 1, resto 0 en `cap+0x784`) pero **no** el camino por el byte `+0x7a` ni escribe la bandera. `G=0x43e9b548` (instantánea de S64), campo `0x43e9bd50` (RAM `0x83e9bd50`) vale 0 en la imagen ⇒ tipo 0 por defecto; sin escritor PIC. **Experimento pendiente (requiere tu autorización y backup de NVRAM):** escribir 1 en `0x83e9bd50` y comprobar tipo (`0x83e9bccc`→2) y obturador. Barrido PIC completo: **ningún escritor directo de `G+0x805..0x80e`** (solo lectores `0x43790ac6/654/ee6`, `0x437904a8`, `0x43793106/60`); lo rellena una ruta por puntero (candidato: constructor de petición `0x43868a30`). Ver P1 de [docs/capture/physical-test-plan.md](../docs/capture/physical-test-plan.md). Detalle en `analysis/s101_shutter_type/pending/report.md`.

### Consumidores de `+0x238`/`+0x280` y byte de tipo de Darwin (detalle)

**VERIFICADO (3 tests, `tests/test_s101_block238.py`):** comando `0x40e3` (`0x43fffc60`) → handler `0x438032d5` → `+0x238`; `+0x280` por `0x43802614`. Las 62 referencias PC-relativas al bloque están todas en `0x43802000–0x43805000`; los accesores `0x43804de8` (40 llamadores) y `0x43804c38` (6) no van seguidos de ningún acceso a `0x234/0x238/0x23c/0x280`. **INFERENCIA fuerte:** ambos campos son solo escritura en `av-cam.bin` (explica S64). El parser CAIF de Darwin A6000 ya está resuelto en S53 (descarta el bit `0x20`). **NO VERIFICADO:** lectura vía puntero guardado en global o desde otro binario. S51 se mantiene.
[Informe](../analysis/s101_shutter_type/block238/block238_consumers.md). **Ampliación:** el puntero de los accesores tampoco llega a esos campos (19 destinos revisados). Darwin: `[0x20000050+ch]` solo tiene lectores (`0x1b080/0x1b096/0x1b0b2`), ningún escritor por código ni literal en el pool, y el arranque no hace carga de datos → INFERENCIA: lo rellena el host BIONZ por mensaje (NO VERIFICADO cuál). **Cierre S70:** A6000, A7S y A6300 tienen la misma estructura (3 lectores, 0 escritores del tipo) y el `__scatterload` de Darwin solo inicializa `0x20002a00+`: el bloque de tipos viene del cargador `0x0–0x41ff` (fuera de la actualización) o del host. La diferencia A6000/A7S está en el valor suministrado o en el bit `0x20` (S53). Vía host→Darwin revisada (tabla de 13 mensajes `0x27c68`; ninguna copia llega a `0x20000050–67`, ni con literales sesgados). Siguiente: traza pasiva autorizada de la RAM de Darwin o volcado del cargador; no hay más vía estática.

## S64 — prueba en cámara de SilentShutter (20-10-2026)

- Modo normal por telnet/adb (Tweak, 192.168.1.29): mismo bloque de ajustes; `+0x238`=1 forzado con 3 disparos ⇒ obturador sigue mecánico y la copia `0x83ed4ff0` no cambia; el espejo vuelve a 0 tras un disparo si no se fuerza. Disparo remoto requiere app propia con `CameraEx` (pendiente). Detalle en `docs/capture/s64-silent-ram-nvram-test.md`.
- Cierre de pruebas en cámara (20-10-2026): ningún campo probado (Silent `+0x238`, copia, instantánea `0x43e9b548`, vecinos, override drive_mode, `D+0x78`/`+0x34`) cambió el obturador; solo espejo `+0x210`=1 dio sonido de «disparo múltiple» (4/4, un JPEG por petición; significado NO VERIFICADO). Electrónico total: NO demostrado.
- Disparo remoto (`tools/remote-shutter/`, `CameraEx` sin preview, HTTP :8080) y matriz de 6 disparos con `+0x238`=1/2 y copia de trabajo: **todos sonaron igual** (oído del usuario); bloque alternativo no activo (`ctx+0x57c`=0). Sin obturador electrónico en modo de aplicaciones. Ver `docs/capture/s64-silent-ram-nvram-test.md`.
**VERIFICADO:** escribir `1` en `0x83edf8bc` (service mode, `dd`/dev/mem) y restaurar; NVRAM `flash` sin cambios y RAM 4 MB sin cambios atribuibles al modo (control en otra dirección da los mismos artefactos). Estático: `0x43804610` reinicializa el bloque (`+0x238`/`+0x280`=0) leyendo un byte de backup; ningún lector/escritor de backup ligado a `+0x238`. Sin consumidor de captura. S51 se mantiene.

[Detalle](../docs/capture/s64-silent-ram-nvram-test.md). Siguiente: llamadora `0x437881a8` (¿cuándo se inicializa?), handler hermano `0x43802614`, trazar `+0x280` en el objeto de trabajo.

## S62 — PMCA: inyección de código, service shell y `modelName` (20-10-2026)

**VERIFICADO (fuente + firmware):** `updatershell` inyecta un fdat propio (cramfs con `/bodylib/libupdaterbody.so`, header de 0x30 B por modelo, cifrado de plataforma, guard CRC + modelo/región/versión **sin firma**; familia CXD90014) que el updater ejecuta y que expone un shell USB `0x23` (`SHEL`/`PULL`/`PUSH`/`RMEM`/`BK*`). `serviceshell` (senser, HASP) da terminal + backup `0x603` + ficheros/memoria. `bk w 0x003e0005` no es una dirección ni un offset: es el id BK4 `subsistema 0x3e | índice 5` = `modelName` (16 B, attr `0x01`), escrito en el almacén `/setting` (`nflasha2`) vía `BKWR` o `0x603/2`; el preset de fábrica `CX77500_ALLLANG.bin` la trae como `ILCE-6000` + 7 NUL (`tests/test_s62_backup_modelname.py` 5/5). **NO VERIFICADO:** el efecto «shell mode» al escribir `ILCE-6001`; esa cadena no existe en el firmware 3.21 (solo `ILCE-6000` en presets), así que no es un match literal de tabla. S51 A=NO/B=NO/C=NO.

[Documento](../docs/capture/s62-pmca-injection.md) · [matriz](../analysis/s62-evidence-matrix.json). Siguiente: lectores de `Backup_read` para `0x3e0005` (REA) o traza pasiva autorizada.

## S68 — gestión de batería, energía y carga (NP-FW50) (21-10-2026)

**VERIFICADO (7 tests, `tests/test_s68_battery.py`):** resultado **negativo**: el `av-cam.bin` de A6000 **no contiene modelo del pack NP-FW50** (0 hits de `NP-FW`/`NPFW`/`FW50`, sin tensión/corriente/ciclos/SOC). Sí hay: nivel de batería vía UPM (`Set UPM Battery Level` `0x43ca2dfd`, función `0x4378f364`, lee 8 B de un dispositivo), códigos de estado hacia un MCU (`ACV_BATT_Snd` `0x43c8f95e`, `BATT_AUTH_Snd` `0x43c8f96b`, `BATT_STATE1..3_Snd`, `BATT_TYPE1/2_Snd`, `Box_Temperature_Snd` `0x43c8f9fc`, `ACV Error Voltage` `0x43c8f83b`), **carga del flash** y no de la batería (`SB_CHARGE` `0x43cb4c23`, `CamStrbChargeOn/Off`, `uc_ChargeCommand` `0x43ccd8c2`, `uc_ChargeStatus` `0x43ccd8ef`, `uc_ChargeEnable` `0x43ccd939`, `uc_ChargeForceOff` `0x43ccd96c`, `b_SBChargeReq` `0x43ccdc76`), power save del imager (`MacroPowerSaveOn/OffRequest`, `SubLVDS PowerSaveOn/Off`, `MonPowersave`) y coordinación lente↔voltaje (`Wait E-MountLens ReduceVoltage Wait(%d ms` `0x43cc7aa4`, `CaptureCancel_PowerOffDetect()` `0x43ca9d85`). La A7S (fw3.20) conserva el bloque de estado (`ACV_BATT_Snd` `0x43c983f6`, `ACV Error Voltage` `0x43c982d3`) pero **no** tiene `BatteryInfo` ni los `[IRLight]/[VideoLight] Battery Info`.

**Corrección de la revisión (21-10-2026):** el informe inicial del subagente afirmaba que la A7S carecía de `ACV Error Voltage` y `ACV_BATT_Snd`; es falso y está corregido en `analysis/s68_power/battery_power.md` y fijado por test.

**NO VERIFICADO:** modelo del pack (está en otro binario); destino de los códigos `BATT_*_Snd`; carga por USB/MTP/PD y por base (no hay modelo en el firmware); perfiles de consumo y apagado automático por batería.

**Sin efecto en la línea SilentShutter:** fin electrónico NO VERIFICADO; **S51 A=NO/B=NO/C=NO** se mantiene.

[Conclusiones](../docs/capture/s68-battery-power.md) · [informe](../analysis/s68_power/battery_power.md). Siguiente: el modelo del pack está fuera de `av-cam.bin` (userland o MCU); el bloque de "carga" es del flash; el destino de `ACV_BATT_Snd`.

## S78 — parámetros `apc_*` del motor de imagen YC (21-10-2026)

**VERIFICADO (6 tests, `tests/test_s78_apc.py`):** el motor de imagen `Camera::YC` (logs `[CAMERA_MAIN_YC]: YAP:`) calcula sus parámetros con un espacio de nombres jerárquico `apc_<módulo>.<parámetro>`: **50 parámetros** en **7 módulos**, entre `0x43cc44cb` y `0x43cc4fe4` — `apc_lpf` (2), `apc_mask` (6), `apc_yld` (9), `apc_acm` (4), `apc_zoukou` (18), `apc_coring` (8), `apc_gain` (3). El nombre va **embebido en la cadena de formato** del log (p. ej. `'[CAMERA_MAIN_YC]: YAP:\tapc_lpf.vaplpf\t=%x'` `0x43cc44b4`): no hay tabla de nombres aparte. Cada módulo lo calcula un job distinto (por el prefijo de log referenciado): `apc_lpf`→`0x438b0f80`, `apc_mask`→`0x438b1058`, `apc_yld`→`0x438b11f0`, `apc_acm`→`0x438b177c`, `apc_zoukou`→`0x438b2070`, `apc_coring`→`0x438b2ac4` (`void Camera::YC::job_apc_coring_stl(...)` `0x43cc513d`), `apc_gain`→`0x438b3570` (`void Camera::YC::job_apc_gain_stl(...)` `0x43cc40df`); más los jobs globales `job_apc_main_stl` (`0x438b3ea8`) y `job_apc_main_mov` (`0x438b5810`). El cálculo depende de la **secuencia BDRO** (`bdro_sequence error` `0x43cc4d37`), del **ISO** (`aus_X_ISO` `0x43cc4d68`) y del **efecto de imagen** (`picture_effect` `0x43cc4d8c`); la ganancia se sincroniza entre captura y preview (`AgcContStdBase`/`AgcContBlend` `0x43cc4428`/`0x43cc446e`).

**NO VERIFICADO:** significado exacto de `acmpm`/`acmpp`; dónde se materializan los 50 parámetros (probablemente `Camera::YC::T_AdjRam`, vista en `sjob_GetDetectArea` `0x438ea230`); tabla de valores por modo de captura; comparación con A7S.

[Conclusiones](../analysis/s78_apc/yc_apc_params.md). Siguiente: emparejar cada parámetro con el bloque de RAM donde se almacena y con la función SA que lo consume.

## S79 — mapa de módulos del firmware por prefijos de log (21-10-2026)

**VERIFICADO (5 tests, `tests/test_s79_modules.py`):** el firmware numera sus trazas con un prefijo `[MÓDULO]`; extrayendo todos los prefijos de las cadenas del blob se obtiene la tabla de módulos: **348 prefijos distintos en A6000 (fw3.21)** y **277 en A7S (fw3.20)**. `CAMERA_MAIN` se descompone en **8 submódulos** (VERIFICADO por nº de trazas y rango): `CAMERA_MAIN_YC` (970, motor de imagen: `api_YC_*`/`job_YC_*`), `CAMERA_MAIN_SYNC` (429, `SyncResMgr::Lock/Unlock/Free`, `CAMDEV(0|1)`), `CAMERA_MAIN` (135), `CAMERA_MAIN_TC` (127, **giro**: `GyroStitScl`, `LmtGyroVect`, `calib_r_ave` → enlaza con S70/EIS), `CAMERA_MAIN_LC` (72, **calibración de lente**: `lc_Movie_DM_AF_Util_getMiniRawAddr`… → enlaza con S75/ZPD), `CAMERA_MAIN_CC` (49, **control de captura**: `ExtractCaptureData/CaptureInit/SetReadImageParam/SetNRParam` con `CapMode/ExposureID/ContID/BDROSeq` → enlaza con S78), `CAMERA_MAIN_IM` (42, **térmico/ambiente**: `movie thermal diffTemp`, `environmentalTemp`) y `CAMERA_MAIN_FC` (9, **datos de ojo**: `Eye data is invalid, but lc flag is true`). Familias mayores: `ADF` (1231), `IMAGING_CAP` (697), `SDF` (477), `CAM_IMAGER` (371), `IDT` (298), `IDT_OPD` (274), `CDIAG` (270), `VDF` (243), `CAMERA_SA` (231), `TRK` (216), `VEF` (149), `MOUNT_DEBUG/ERROR` (132/80), `SFRS/SFRA` (117/100), `VPH_API` (106), `ACCY` (106), `DBGCMD` (102), `STK` (76), `FACE` (70), `VIDENCSTAT` (70), `CLK_CTRL` (66), `GOLFSHOT` (65), `WSX` (59), `CTRLCORE` (55), `CAM_DMM` (54), `SAD` (45), `CAM_FUNC_MGR` (43), `APL` (42), `PNL` (41). **Diferencial**: 83 prefijos exclusivos de A6000 (los `CAMERA_MAIN_*`, `CAMERA_IS`, `CAMERA_ADJ`, `CAMERA_DETECT_FC`, `CAMERA_DEVICE`, `ACCY`, `ADC_DEBUG`, `AVOUT`, `ADR`, `AVR`, `BKID`, `CAMCORE`…) y 12 exclusivos de A7S (`APL_PARM`, `APL_ESR`, `APL_ADDR`, `APL_REF`, `APL_SIZE`, `APL_TAR`, `APL_UPDT`, `NLAP`, `PIN`, `PINCOUNT`, `TCUB`, `CDCTCUBENCTABLE`).

**NO VERIFICADO:** qué significan las siglas `ADF`, `IDT`, `VDF`, `VEF`, `SFRS`/`SFRA`, `WSX`, `GOLFSHOT`, `ACCY`, `AUGI`, `SAD`, `APL`; correspondencia prefijo↔tarea real del OSAL; renombrados posibles entre fw3.20 y fw3.21.

[Conclusiones](../analysis/s79_modules/module_map.md) · [tabla JSON](../analysis/s79_modules/module_map.json).

## S80 — ZIT: corrección de defectos del sensor (DDC) (21-10-2026)

**VERIFICADO (9 tests, `tests/test_s80_zit.py`):** el imager (`Camera::Imager`) lleva un motor de **corrección de defectos** con 118 trazas `ZIT`/`Zit` (75 en la A7S fw3.20). Clases RTTI: `N6Camera6Imager12ZitMemBufferE` (`0x43cf768e`), `N6Camera6Imager18ZitZphDefectBufferE` (`0x43cf81a1`), `N6Camera6Imager21ZitZphLineTableBufferE` (`0x43cf96ef`). Trabaja sobre **cuatro áreas de memoria** (`ZIT:: shadowAddr adj:%x usr:%x slow:%x mend:%x` `0x43cf7706`): **adj** (ajuste de fábrica), **usr** (usuario), **slow** (long exposure) y **mend** (parche), con los defectos organizados en **bancos por "read mode"** (`<read:%d bank:%d>` `0x43cf7771`). **Puente con el motor de imagen**: `Camera::Imager::ZitSaFunctionDriver` con `ZIT_SaOpen`/`ZIT_SaStart`/`ZIT_SaClose` (`0x43cfa2a7`–`0x43cfa2ee`; firma `ZIT_SaClose()` `0x43cfa312`), handles DMM limitados (`dmmHandleList is Full` `0x43cf9cd3`) y **MMU propio** (`CloseFreeZitMMUParam` `0x43cfa210`). **Siete operaciones se ejecutan en el SA**: `Merge` (`0x43a13be8`), `ConvThin` (`0x43a194c4`), `ConvUnity` (`0x43a19908`), `ConvZ1C` (`0x43a19c58`), `Det` (`0x43a1a364`, con `DetectInfo [ch1..ch4]` y `RAWInfo [AVE/MIN/MAX]`), `Hist` (`0x43a1a834`) y `ZphSA` (`0x43a1aafc`), más `ZitSA_ConvDdc` (`0x43a139c8`). Registro de defectos: `SetZitLog_DetectSequencePre/MassiveDefectDetectNum/DefectLvAndPos/DefectPosNum` (`0x43cf7e5f`–`0x43cf7f2e`). Búferes "Zph": `ZitZphDefectBuffer::reCalcOffset/copyBuff/convertBackupSaveformat`, `ZphAdj_Merge_Req`, `ZphAdj_Det_Req`, `ZphDetSA`. Variantes: **long exposure** (`buildLongExpCapData_DDC`, merge `adj`+`usr`, `convDdcByCpu`) y **vídeo** (`MovieAdj_SpreadDefectsOverSharedPixels`). Drivers de nivel superior: `ZitDdcDriver` (`0x4386bbee`) y `ZitZ1cDriver` (`0x437b93c0`), ambos en `CAMERA_MAIN_IM`.

**NO VERIFICADO:** qué significan las siglas ZIT y Zph; qué es un "read mode"/banco y cuántos hay; formato binario y origen de fábrica de los datos de defecto; enlace exacto con ZPD (S75); algoritmos del SA que ejecutan las conversiones.

[Conclusiones](../analysis/s80_zit/zit_defect_correction.md).

## S71 — subsistema de detección de caras y objetos (FC/FRC) (21-10-2026)

**VERIFICADO (20 tests, `tests/test_s71_frc.py`):** el subsistema `Camera::FC` del `av-cam.bin` tiene **99 ficheros `FC/…`** embebidos, **idénticos en A6000 fw3.21 y A7S fw3.20** (0 diferencias), repartidos en `Alg` (`fc_alg_frc`, `smoothing`, `remove_overlap`, `target_selecting`, `tracking`, `tracking_obj(_color)`, `tracking_face_object`, `pre_fdt`, `attribute`, `extract_color`, `blink`, `exif_face_data`, `exif_makernote`, `normalize`, `object`, `pmv`, `select_key`, `track_init`, `touch`), `Seq` (`mon_face`, `mon_object`, `mon_frame`, `attribute`, `oneshot`, `pmv`, `re_init`, `touch`, `track_init`, `prc`, `rec_face`, `vae` + `fc_data_*`), `Drv` (`frc`, `bt`, `edt`, `fat`, `fdt`, `vat`, `detsa`, `iro`, `iro2g`, `pmv`, `stk`, `prc`, `vae`), `SaFuncDrv` (`fc_sa_frc2_drv`, `fc_sa_frc2_mmu`, `recog_sa_drv`), `Feature` (17), `Api` (9), `Lib` (7) y `Misc` (3). **Puente con el acelerador Scalar (SA)**: recursos en Core2/Core3 (`AcquireRes … Core2 user[0]` `0x43cf094a`, `Core3 user[1]` `0x43cf0981`, `RES_SA_FOR_FRC2` `0x43cf09b8`), búferes propios `s_sa_temp_icon_mem`/`s_sa_param_mem` (`0x43cf0bd8`/`0x43cf0bc3`), MMU (`MakeMmu …` `0x43cf0c11`), ciclo de cálculo (`ddl_saCalcCancel` `0x43cf0afb`, `int_fact=NOT_FINISH` `0x43cf0ad4`, `alloc size:%d, expected:%d` `0x43cf0b39`) e iconos de cara (`FRC: Init FaceIcon` `0x43cf0d6c`, `FaceIconInfo::Alloc() handle:%d` `0x43cf0db8`). Módulo `[FACE]` (70 trazas) con estados INIT/BASE/MON/IMME/ATTR/STOP. Módulo `[TRK]` (216 trazas) con **seis detectores**: DETSA (Core2), EDTSA (Core3, entrega cara/ángulo/nodo/rangos HSV), IRO2G (Core2), PMV (Core3, vectores de movimiento), STK (Core2, saliencia y similitud toque/color) y BT (fg/bg areas + mapas bayesianos). Algoritmo FRC: reordena IDs por `record_rank` y gobierna la creación de iconos por prioridad; además **parpadeo** (`fc_alg_blink.cpp`), Pre-FDT (African/Scene/Bunri/Hist/contraluz), alternancia cara↔objeto en el tracking, panorámica/retoque y **MakerNote de caras**.

**Corrección de la revisión (21-10-2026):** el borrador del subagente tenía direcciones en espacio de ficheros (`0x8060839`), nombres de búfer inexistentes (`s_temp_icon_mem`/`s_param_mem`), "SA (Secure Area)" (es el **acelerador Scalar**: SFRA = *ScalarA-ScalarInfra*, `sa_dfdet.bin` = detección de caras en el Scalar), semántica inventada para BT/FAT/IRO/PMV/STK y un **diferencial A7S falso** (los ficheros `FC/` son los mismos 99 en ambas cámaras).

**NO VERIFICADO:** siglas FDT/VAT/PRC/VAE/VOT; formato binario de los mensajes al Scalar; reparto Core2/Core3; algoritmos del SA para FRC; relación con `analysis/s63_af/` (otro agente) más allá de `fc_feature_touch_for_scanaf.cpp` y `fc_alg_pre_fdt.cpp`.

[Conclusiones](../analysis/s71_frc/frc_subsystem.md) · [tabla JSON](../analysis/s71_frc/frc_subsystem.json).

## S81 — ADF: el framework de arranque, MSGQ, MMGR y comandos DBGCMD (21-10-2026)

**VERIFICADO (9 tests, `tests/test_s81_adf.py`):** `ADF` es el **módulo más grande del firmware por número de trazas**: **1220** cadenas `[ADF]` en A6000 fw3.21 (1269 en A7S fw3.20) en `0x43c26366`–`0x43c37a62`, con sub-niveles raíz 934, `[DBGCMD]` 102, `[ERR]` 70, `[SYSND]` 27, `[ADJ]` 24, `[SAN]` 23, `[OUT]` 15, `[ADF]` 11, `[SYS]` 3, `[INIT]` 2, `[DEBUG]` 2, `[GS]` 2, `[AFNR]` 2, `[FACE]` 2, `[CH_SRC]` 1. **Arranque**: `[ADF]BootInit` `0x43c26366` → `InitWaitVsync SelectCompo` `0x43c26375` (espera de vsync y selección de componentes) → `[ADF][INIT]AVIO INIT COMP` `0x43c263f6` y `[ADF][INIT]AUDIOIP INIT COMP` `0x43c26411` → `[ADF]BootExit` `0x43c263c9`, con **reenvío de mensajes** (`INIT Resend MsgqNum` `0x43c263d8`, `Resend header cateId/msgId/msgLength/version` `0x43c2642f`, `Resend to Adf src/reply` `0x43c2648f`). **Configuración del IP de audio** (enlace con S69): `AUDIO_IP_CONFIG_TYPE_VGS` `0x43c264fa`, `_PR` `0x43c26518`, `_MF` `0x43c26535`, `_BANDI_BASEDON_CONS` `0x43c26552`, `_CONS` `0x43c2657f`, `_BANDI` `0x43c2659e`. **Gestor de memoria (MMGR)**: `MMGR COMM INFO` `0x43c265ce` con `indexNo, unitType, handle, allocNum, openNum` `0x43c265e3` y `AdfMemMgrCtrl::SetMemMgrCommResult` `0x43c26652`. **Colas de mensajes (MSGQ)**: `MSGQ Set:srcId %08X ,msgId %08X` `0x43c26788`, `MSGQ Get:msgId %08X` `0x43c267d5`, `SendImmediateComp msgId/replyId` `0x43c268a8`, `ClearAllComp` `0x43c2691c`, y el grupo `MSGQ_GID_HOTSHOE_INFRA1` `0x43c266e6` (colas del flash hotshoe). **102 comandos de depuración** (`[ADF][DBGCMD]`, `0x43c2a443`–`0x43c2b315`): `System` (ClearExecTime/ClearMSGQ/CountMSGQ/SetMSG/GetMSGQ/BootExit/GetMemMgrComm), **medida del tiempo de ejecución de la CPU2 a 60 Hz y 48 Hz** (`CPU2 ExecTime 60Hz max m/s` `0x43c2a465`, `48Hz` `0x43c2a4ca`), `Input`/`InputPro` (SetInput, SetRecLevel, SetAgcLink, SetManualGainLink, SetChSource…), `Output`/`OutputPro` (SetOutput, DetectJack, SetHdmiFormat, SetAntiClipping, SetHpMonitor, SetHpOut, SetAdjI2sMute), `Proc` (**fases lineales del arranque**: SetLinearPhase, SetDec0/1, SetAip0/1, GetSa0/1, GetPin0/1, SetMb, SetSa; y ruta de audio/zoom: SetPath, SetMixRatio, SetFader, SetZoomNr, ZOOM[0..2]), `SystemSound` (SetTable/SetPath/Request/SetVol/SetNotify/RequestPin) y **`SoundAnalyzer` con el disparo de golf** (`StartGolfShot` `0x43c2b143`, `StopGolfShot`, `AnalyzeGolfShot`, `SetSoundAnalyze`).

**NO VERIFICADO:** significado de `ADF`/`MMGR`/`Compo`/`AIP`/`MB`/`SA` en este contexto (salvo `AIP` = Audio IP); formato del mensaje (cabecera `cateId/msgId/msgLength/version` + `srcId`/`replyId`) y tabla de destinos; lista completa de grupos `MSGQ_GID_*`; qué hacen `ADF][ADJ]`, `[SAN]`, `[SYSND]`, `[GS]`, `[AFNR]`, `[FACE]`, `[CH_SRC]`; cómo se invocan los comandos DBGCMD.

[Conclusiones](../analysis/s81_adf/adf_framework.md).

## S83 — los módulos "menores" del firmware, decodificados (21-10-2026)

**VERIFICADO (10 tests, `tests/test_s83_modules.py`):** decodificación por evidencia (nombres de función y campos de estado) de los módulos de tamaño medio que S79 dejó sin descripción: **`[ACCY]`** (106) = **accesorios por UART** (`NotifyAttachedUart` `0x43c24cca`, `NotifyDetached` `0x43c24d1e`, `NotifyUartCommand` `0x43c24d41`, `[HW]:AD=%d, ID=%d` `0x43c24cac`; mismo hardware que el grupo `MSGQ_GID_HOTSHOE_INFRA1` de ADF, S81); **`[CAM_FUNC_MGR]`** (43) = **gestor de funciones de captura** (`SyncProcMargin[usec] HS0..HS3@CPU2/CPU0(IDT)/CPU3(RCH)` `0x43ca12f6`, `SetCapMode:Invalid CapMode` `0x43caf036`, `receive[..] before comp[..] (QUEUEING)` `0x43caf077`); **`[ENCOUCSTAT]`** (49) = **errores del codificador AVC** (`AVC_ENC_VIDEO_ERR_STATE/MEMORY/PARAM/INDEX` `0x43c50693`–`0x43c50730`); **`[VIDENCSTAT]`** (70) = **estado del encoder de vídeo** (`Pts = 0x%08x EndFlug` `0x43cd680b`, `augi,paddingAreaLength` `0x43cd6861`, `Use 2nd Latest Index` `0x43cd68af`); **`[ENCSEQCTRL]`** (46) = **secuenciador de encoding** con tabla de frame rate/sampling rate (`[O/U Crank] Table[%d] fR sR` `0x43c4bd2b`) y máquina de estados (`[state]0x%x -> 0x%x` `0x43c4bda2`); **`[SAD]`** (45) = **programas del motor de imagen** con cabecera (`CdcSaPrg/NmlSaPrg/RsdSaPrg Hdr Err` `0x43ce55bc`–`0x43ce55fa`); **`[PNL]`** (41) = **panel/display** con configuración por callbacks y backup (`Backup_read() b_id` `0x43c76155`, `cmd_set_conf_cb_NULL` `0x43c761bd`; enlaza con `ADJ_CMD`, S73); **`[AUGI]`** (75 token / 26 cadenas con prefijo) = **formato de bloque con cabecera** (`length`, `Reserved2`, `end_flag`, `PS_flag`, `EP_flag` `0x43cd9968`–`0x43cd99f4`); **`[WSX]`** (59) = servicio de **búsqueda en fichero "BSFS"** (`BSFS INIT: TG: %x` `0x43ce41bd`, `BSFS SEARCH LOOP ERROR` `0x43ce41fe`).

**NO VERIFICADO:** siglas BSFS/AUGI/SAD/WSX/ENCOUCSTAT; qué son los programas `Cdc/Nml/Rsd` del SA; los 4 sub-valores de `CapMode`; la tabla "O/U Crank" completa; formato exacto de la cabecera AUGI; módulos aún sin decodificar (`IDT`, `VDF`, `VEF`, `CLK_CTRL`, `SFRS`/`SFRA`, `GOLFSHOT`, `SAN`, `GS`, `CH_SRC`, `AFNR`).

[Conclusiones](../analysis/s83_modules/minor_modules.md).

## S84 — el API del motor de imagen (SA): catálogo de `sa_func_*` (21-10-2026)

**VERIFICADO (11 tests, `tests/test_s84_sa_api.py`):** la superficie del driver `Camera::SaFuncDrv` tiene una forma uniforme — `Camera::SaFuncDrv::SA_FUNCDRV_ERR Camera::SaFuncDrv::sa_func_<X>_<op>(__uint8_t, __uint16_t, Camera::SaFuncDrv::<X>_START_PARAM*)` = (unidad, código de función, parámetros) —, con **19 familias**: `BFNR` (init con `SaFuncDrvCmn*` + `BFNR_PARAM*`, acquire/start/release), `BOKS` (init/init_CONTROL/GetAddr/start/release/exit), `CONTP`, `DECOMP`, `DUALREC_BAYER`/`DUALREC_CLEARVID`, `GOLFSHOT` (con **dos sobrecargas de `start`**: `SSP_START_PARAM*`+`SSP_START_MBX*` y `BGEST_START_PARAM*`+`SA_MBX_0123*`), `KKNR`, `LFNR`, `NFLASH` (flash: `flash_add`/`amb_add`/`int_add`/`rc_line_ofs`), `PreDCV`, `SFTFCS` (`preinit(__uint16_t)` + mailbox `cha_mbx0/1/2`), `SPICA` (con fases **PRE/MAPPING/POST**), `STAR`, `TBOX`, `YKNR`, `BDEX`, y en la A7S además `MOTIONSHOT` y `NLAP`. Códigos de error: `SA_FUNCDRV_E_OSAL`, `SA_FUNCDRV_E_RSLTCODE`, `SA_FUNCDRV_E_ERRCODE`. Quien las invoca en la captura es el módulo `IMAGING_CAP` (697 trazas) y el propio driver con prefijo `[CAMERA_SA]` (231 trazas). 92 cadenas contienen `sa_func_` en la A6000 (109 en la A7S).

**Diferencial (VERIFICADO):** la fw3.21 de A6000 **elimina por completo** `NLAP` (0 ocurrencias; la A7S tiene 13, con `[YC][NLAP]isNLAP:true, iso_cont=0x%04x` `0x43cbbf71`) y `sa_func_MOTIONSHOT_*` (0 ocurrencias; la A7S los llama desde `IMAGING_CAP` `0x43cc403e`/`0x43cc4063` y tiene la firma `0x43ce3448`). Lo que permanece en la A6000 es `MOTIONSHOTVIDEO`, del módulo **SFRS** (otra cosa: vídeo de movimiento).

**NO VERIFICADO:** significado de las siglas de cada familia; estructura de los `<X>_START_PARAM`; qué algoritmo del SA corresponde a cada familia; detalle de las fases PRE/MAPPING/POST de SPICA; por qué la A6000 conserva SFRS/MOTIONSHOTVIDEO.

[Conclusiones](../analysis/s84_sa_api/sa_api_catalogue.md).

## S72 — wireless y transferencia remota (WLAN / PlayMem / "Camera on Demand") (21-10-2026)

**VERIFICADO (16 tests, `tests/test_s72_wlan.py`):** pila wireless del userland fw3.21 (`firmware/extracted/fw321/.../nflasha15_unpacked_unpacked/lib`, 157 `.so`): **`libWlanAdjust.so`** (60 492 B) = ajuste del radio (`WlanAdjust_Init/Res/Sus`, 11 `wpa_ctrl_*`, `wlanLoadFirmware`, `wlanSetSsid/TxCh/TxMode/TxRate/TxPower` + `wlanGet*`, `wlanStartTx/StopTx`, `m_fixed_psk`, `SetMacAddress`); **`libWlanControlCommon.so`** (23 840 B) = control del puerto (`initializePort/finalizePort`, `setPortToStartWlan/StopWlan`, `installWlanDrivers`, 25 × "BMI" = bus del chip, GPIO de energía); **`libWlanResource.so`** (63 656 B) = recurso/hilo (`WlanResourceMainThread`, `GetMacAddress(WlanResource::ST_MSG_SYNC_REQ*)`, DFS, colas `OSAL_MSGQ_GID_WLAN_RSRC_DBG`/`_TEST`); **`libGOConnectionManager.so`** (106 016 B) = **P2P con rol Group Owner**: máquina de estados **Idle→Init→Auth→Wait→ChgKey→AuthConn→Finalizing→Stop** (`startGO/stopGO`, `authPush`, `changeKey`), `GOConnectionManagerCmdMgr` (`ProcIdleToAuthReq`, `ProcWaitAuthReqToChgKey`, `ProcIssueFatalError`…) y `NetServiceWrapper` con los comandos **WPS** (`StartWpsCmd`, `CancelWpsCmd`, `InputPin`, `AuthPush`, `ChangeKey`) y eventos (`SendReqWpsEvtPush/ShowPin/InputPin`, `SendWpsCompleteEvt`); **`libInfraDlnaControl.so`** (525 892 B) = **DLNA/UPnP** (`dc_statetbl`, `dc_evtTbl`, 9 *callers* `m_lid_*`, `sendMsgToControlpoint/MediaServer/ContentHandler`); **`CameraOnDemandSaver.so`** (20 084 B) = guardado "on demand" en `/dev/ms1`, **`/mnt/dcim/100msdcf`** y **`/setting/psd.bin`** (hilo `cam_ondemand_saver_thread`, auto-numeración `%04d_%02X`); **`libHapiLib.so`** (89 628 B) = API de la app. **`netconf/` es un directorio** con 4 configuraciones: `bss.conf` (`manufacturer=Sony Corporation`, `model_name=SonyImagingDevice`, `device_name=WCM-Sample-Device`, `device_type=1-0050F204-1`, `config_methods=physical_display virtual_push_button`, `uuid=12345678-9abc-def0-1234-56789abcdef0`, `ctrl_interface=/tmp_network/run/wpa_supplicant`), `p2p.conf` (`p2p_go_intent=10`, `max_num_sta=1`, `p2p_ssid_postfix=-WCM`, `device_type=4-0050F204-1`, `config_methods=virtual_push_button physical_display keypad`), `dhcpd.conf` (subred `10.0.0.0/16`, rango `10.0.1.1-254`) y `pump.conf` (cliente DHCP en `ath0`/`ath1`).

**Hallazgo nuevo (VERIFICADO):** el `psd.bin` que escribe `CameraOnDemandSaver.so` es **el mismo fichero** que S75 identificó como origen "from body" de los datos **ZPD** de calibración del sensor → el "Camera on Demand" escribe en el almacén de ajustes de la cámara.

**Correcciones de la revisión (21-10-2026):** (a) `getMacAddress` no existe → el símbolo real es `GetMacAddress(WlanResource::ST_MSG_SYNC_REQ*)`; (b) las colas son `OSAL_MSGQ_GID_WLAN_RSRC_DBG` y `…_TEST` (no `…_API`); (c) **`libgps_rsrc.so` SÍ está en el firmware de la A6000** (109 384 B), el borrador afirmaba lo contrario; (d) la cadena GO está **más desarrollada en la A6000** (106 016 B vs 64 580 B; mismo esquema de 348 símbolos, 0 diferencias), no en la A7S; (e) `netconf` no es idéntico: 3 de 4 ficheros coinciden por SHA-256 y solo difiere `dhcpd.conf`; (f) la biblioteca HAPI se llama `libHapiLib.so`, no `libInfraHapiLib.so`.

**NO VERIFICADO:** cómo se enlazan `libGOConnectionManager` y `CameraOnDemandSaver`; por qué la fw3.21 duplica el tamaño de las bibliotecas WLAN; contenido y destino del `psd.bin` escrito; los 10 símbolos de DLNA exclusivos de la A6000.

[Conclusiones](../analysis/s72_wlan/wlan_playmem.md) · [tabla JSON](../analysis/s72_wlan/wlan_playmem.json).

## S85 — `CLK_CTRL` (control de reloj) y `VPH_API` (API del vídeo del visor) (21-10-2026)

**VERIFICADO (11 tests, `tests/test_s85_clk_vph.py`):** dos módulos **nuevos en la fw3.21 de A6000** (0 trazas en la A7S fw3.20). **`[CLK_CTRL]`** (66 trazas, `0x43c3a1df`–`0x43c3b09c`): control de reloj y de la señal de sincronización del visor, con 12 llamadas `ddl_clkctrl_*` (`open/close_clk`, `open/close_dly`, `set_sync_signal`, `set_sync_initial_signal`, `lock/unlock_sync_signal`, `set_sysv_delay[_changing]`, `set_sysv_initial_delay`, `get_clk_chg_enable`), máquina de estados `STATE_INIT1(InitDelay)` → `STATE_NORMAL(InitSignal)` → `STATE_LOCK` (+ `STATE_CHANGE_CLK`, `STATE_CHANGE_CLK_LOCKING`), **gestión por subsistema** (`open/close subsytem = 0x%04x`, `Busy!! 0x%04x already opened`, `lock_sync_signal subsystem = %x`), cambios de reloj y retardo (`CHANGE_CLK dly … clk … change_vfc=0x%x`, `ClkChgExec`, `DelayChgExec`) con **dos VFC** (`m_vfc.main=0x%0x, m_vfc.sub=0x%0x` `0x43c3ac2f`), y arquitectura **maestro/esclavo** (`Receive Message from Master` `0x43c3abd0`, `Send Message to Slave` `0x43c3ac86`, `Send HTP at` `0x43c3aae7`) que además se coordina con VPH (`vph stat:%d,mode:%d` `0x43c3aa69`). **`[VPH_API]`** (106 trazas, `0x43ce32e7`–`0x43ce3dfc`): vocabulario de **comandos** del procesado de vídeo del visor — ruta (`<mode>`, `<line_out>`, `<panel_out>`, `<dualpanel_out>`, `<update_yuv>`, `<mix_mode>`, `<force_out>`), OSD (`<osd_on>`, `<osdarea_on>`, `<osdarea>`, `<update_osd>`), **marco de cara** (`<faceframe_on>`, `<update_faceframe>`, `<faceframe_color>`), timecode, mute (`<yuv_mute>`, `<yuv_mute_param>`, `<yuv_mute_immediately>`, `<chroma_mute>`, `<shutter_mute_param>`), línea (`<line_closedcaption>`, `<line_macrovision>`, `<line_vbidwss>`, `<line_sync_setup>`, `<line_fchr>`, `<line_hdmi_still_range>`), panel (`<panel_brightness>`, `<panel_cabc>`, `<panel_depth>`, `<panel_reverse>`, `<panel_ysetup>`, `<set_panel_osd_luminance>`), ayudas (`<pictureeffect>`, `<ylevel_caution>`, `<zebra>`, `<peaking>`, `<gridline>`, `<histogram>`, `<testpattern>`, `<diceic_arb>`) y corrección (`<parallax_adjust>`, `<set_extblackframe>`, `<set_color_temperature>`) — **cada uno con su gemelo `_sub`** (los dos canales) — más 11 salidas de estado (`>hw_status<`, `>mode_status<`, `>histogram_result<`, `>yuv_delay<`, `>osdmix_size_panel/line<`, `>black_frame<`, `>panel_brightness_status<`, `>shutter_mute<`).

**Enlace con S71 (VERIFICADO):** el visor dibuja el marco de la cara detectada (`<faceframe_on>`, `<update_faceframe>`, `<faceframe_color>`).

**NO VERIFICADO:** significado de `laxo`, `diceic_arb`, `ylevel_caution`, `vbidwss`, `fchr`, `extblackframe`, `eomainsub`, `htp`; correspondencia exacta de los canales línea/panel; quién es el "master"; si VPH_API es un contrato con hardware externo o con el módulo VDF (S79); por qué la fw3.21 introduce ambos módulos.

[Conclusiones](../analysis/s85_clk_vph/clk_ctrl_vph_api.md).

## S86 — el subsistema del visor: `VDF` y `VEF` (21-10-2026)

**VERIFICADO (14 tests, `tests/test_s86_vdf_vef.py`):** **`[VDF]`** (243 trazas, `0x43c813fc`+) es un framework C++ completo del display (~200 clases RTTI `N3VDF*`): núcleo (`VDF::SubsystemMain::Main()` `0x43c8221b`, `SubsystemFactory::ExecCmd` `0x43c83b7f`), framework de mensajes (`MsgAccessor`/`MsgIterator`/`WaitQueue`), **cmds del sistema** (`PinConnect`/`PinSend`/`PinGet`/`PinDisconnect`/`Trigger`/`Receive`/`Sysv`/`Debug`/`CipaModeOut`), **cmds de display** (`SetPanelOut` `0x43c8714a`, `SetPanelBrightness` `0x43c86eea`, `SetPanelColorTemperature` `0x43c86886`, `SetParallax` `0x43c86e1c`, `SetDetectExtEvf` `0x43c862b9`, `SetOsdAlpha` `0x43c866ef`, `GetPanelBrightness` `0x43c86209`), **cmds de entrada** (`UpdateYuv` `0x43c888ef`, `SetOsdArea`, `SetYuvLayout`, `SetYuvMute`, `SetShutterMute`, `SetHdTrimming`, `UpdateFaceFramePin` `0x43c887e9`), **cmds de servicio** (`SetZebra` `0x43c8ad68`, `SetPeaking`, `SetHistogram`, `SetFaceFrame`, `SetEvfParallax`, `SetLiveDemo`, `SetPanelZoom`, `SetTimeCode`), **rutas de imagen** (`SetPath` `0x43c89fca`, `ThroughTransfer`, `ResizeTransfer`, `4K…`), memoria (`YuvIndexDoubleBuffer`, `YuvIndexQfhdMemoryManager`, `VfxRgba8888ToYuv422`) y dispositivos (`EoLineDevice`/`EoPanelDevice`/`LRMixDevice`, `MirrorSubsystemSynchronizer` `0x43c84c0c`). **Puente con VPH** (S85): `VphSetZebraCall` `0x43c87294`, `VphSetPeakingCall` `0x43c872f9`, `VphSetPanelDepthCall` `0x43c870e0`, `VphUpdateYuvFunction` `0x43c85017`, `DrvCallVphLatestCmdHolder` `0x43c8305e`; trazas `[VDF] CallVphUpdateYuv size_x/size_y` `0x43c82fd7` y `vph_set_yuv_mute_immediately ON/OFF sel=%d` `0x43c83004`. **Enlace con ADF** (S81): `VDF::VdfToAdfYcDataSender` `0x43c86165` (envía los datos YC al ADF) y persistencia en el **bus SSBI** del display (`ssbi_read/write` `0x43c814f0`/`0x43c81547`, `Backup_read(BKID_UPM_BOOT_CIPA_FLAG)` `0x43c82329`). **Enlace con CLK_CTRL** (S85): `CheckUpdateYuvTiming(VDF_PRM_SUBSYSTEM_CLKCTRL_INFO)` `0x43c847d1`, `HtpVfcMainPerformanceCounter` `0x43c855f1`. **Enlace con las caras** (S71): `VdfInputCmdUpdateFaceFramePin` `0x43c887e9`, `VdfFaceFrameUtility::UpdateFaceFrameNormal` `0x43c8c014`, `VdfSrvcCmdSetFaceFrameCommonDesign` `0x43c8a998`. **`[VEF]`** (149 trazas) = el visor electrónico: **espejo** con el panel (`reply_osal_id/mirror_osal_id` `0x43c8c36e`), modos **3D/2D/INIT** (`0x43c8d5cf`–`0x43c8d62f`), **multicast** de infraestructura para pausarlo (`Receive InfraMulticast PauseNotify` `0x43c8d10d`), **down-conversion** de la señal a **PAL/NTSC** (`DOWNCON: PAL 50i50p` `0x43c8d394`, `NTSC 30p24p` `0x43c8d403`), cancelación de efectos **sincronizada con el VFC** (`VFC Sync!!!` `0x43c8dc56`) y toma del bloque de trabajo YC del datarec (`free DMM_UNITTYPE_DATEREC_WORK_YC` `0x43c8da6b`).

**NO VERIFICADO:** qué es el modo "3D" del visor; formato de los mensajes VDF (`VDF_MSG_INFO`, `CATE_ID`, `MSG_ID`, `TRIGGER_TYPE`); implementación del espejo EVF↔panel; efectos de vídeo más allá de la cancelación; si este VDF es el mismo que el citado en S16–S18.

[Conclusiones](../analysis/s86_vdf_vef/vdf_vef_viewfinder.md).

## S77 — Creative Style y balance de blancos (21-10-2026)

**VERIFICADO (10 tests, `tests/test_s77_pp.py`):** en el `av-cam.bin` hay **dos tablas de nombres de estilo creativo**: `0x43ca6702`–`0x43ca676d` (**13** entradas: Vivid, Neutral, Portrait, Landscape, Clear, Deep, Light, Sunset, Nightview, Autumnleaves, **Real**, Sepia, Standard) y `0x43ca678b`–`0x43ca67f0` (**12**, las mismas sin `Real`); la **A7S fw3.20 tiene las mismas dos tablas** (`0x43cb540e`…, `0x43cc5ab8`…) → el juego de estilos no cambia entre fw3.20 y fw3.21. **El bloque `wb_*`** (`wb_b_data=%02X` `0x43c76c26`, `wb_data_tmp=%02X` `0x43c76c36`, `wb_r_data=%02X` `0x43c76c48`, `wb_g_data=%02X` `0x43c76c6b`, `wb_w_data=%02X` `0x43c76dca`/`0x43c76e21`, `wb_mask=%02X` `0x43c76dbb`/`0x43c76e13`) está **dentro del bloque de ajuste de panel `ADJ_CMD`** (S73) → es la **calibración de WB del display**, no el WB fotográfico. **Resultado negativo verificado:** en `av-cam.bin` hay **0 apariciones** de `CreativeStyle`, `PictureProfile`, `Highlight`, `Saturation`, `Sharpness`, `ColorTone` y `wb_shift` → el control del estilo/WB fotográfico vive solo en el userland. **`wrapperCreativeStyle.so`** (8 420 B): `WrapperCreativeStyle::getCreativeStyle/setCreativeStyle/convertProcessValueIdToValue/convertValueToProcessValueId/isInhOn`, `CmnViewProcessDataMgr::getInstance`, `stella::8BitArray<unsigned int>`; ruta de compilación embebida `…/build/141H/141H.DSLR.DM_UUD3.reco.LATEST.diadem.set/Guiengine_131H/` (modelo interno **141H** = ILCE-6000, motor GUI **Diadem**). **`wrapperWhiteBalance.so`** (15 556 B): `WrapperWhiteBalance::getWhiteBalance`, `setWhiteBalance(…, int, int, int)` (tres enteros: WB + compensación), `resetAdjustmentValue`, `isInhOn`, persistencia vía `WrapperSettingUtil::readBackup/writeBackup` → `BackupManager::Bkup_Read_Setting_Attr`, y aplicación vía `ViewBase::requestModelExecute`/`getModelInfo` con `ParamBase`/`PrmNumber`/`ParamList`.

**Correcciones de la revisión (21-10-2026):** la "tabla de Picture Profile" del borrador (offset `0xaa8d50`) es **código Thumb**, no datos; los nombres de parámetro `Highlight`/`Saturation`/`Sharpness` y `CreativeStyle`/`PictureProfile` **no existen** en el firmware; y los presets de WB (`Auto`, `Daylight`…) **no aparecen** en ninguna cadena del binario (el test lo fija como negativo).

**NO VERIFICADO:** qué tabla de estilos usa el código y qué significa la entrada `Real`; los valores por estilo (no están en el firmware ni en estas .so); los enumerados `WRAPPER_CREATIVE_STYLE`/`WRAPPER_WHITE_BALANCE`; el mapeo PP1..PP6/Off; los presets fotográficos de WB; los rangos de la compensación.

[Conclusiones](../analysis/s77_pp/picture_profile_creative_style.md) · [tabla JSON](../analysis/s77_pp/picture_profile_creative_style.json).

## S88 — GOLFSHOT (disparo de golf por sonido) y MOTIONSHOT (21-10-2026)

**VERIFICADO (9 tests, `tests/test_s88_shotmodes.py`):** el modo de golf shot dispara sincronizado con el **sonido del golpe**: 72 cadenas contienen `GOLFSHOT` en la A6000 (también 72 en la A7S), pero en la **A6000 la etiqueta va anidada** dentro de `[IMAGING_RSRC]:`, `[IMAGING_CAP]:` y `[CAMERA_MAIN_SYNC]:` (`[IMAGING_RSRC]: [GOLFSHOT]SA_LPF Exec[%02d]…` `0x43ca492f`), mientras que en la **A7S es prefijo principal** (65 cadenas que empiezan por `[GOLFSHOT]`, 0 en A6000) → la fw3.21 **reorganizó la traza**, no la función. El **módulo `[SAN]`** (5 cadenas) da los comandos: `[SAN]StartGolfShot` `0x43c2c72e`, `[SAN]StopGolfShot` `0x43c2c77a`, `[SAN]AnalyzeGolfShot` `0x43c2c792`, `[SAN]SetSoundAnalyze` `0x43c2c7dd` y `[SAN] CLAP DETECT SCORE = %d (%d[deg]) DIFF = %d` `0x43ce2f27` → **detecta el golpe por el sonido, con puntuación, ángulo (grados) y diferencia**; los mismos están como comandos de depuración del ADF (S81: `SoundAnalyzer StartGolfShot` `0x43c2b143`…). El motor de imagen ejecuta **tres fases SA**: `SA_LPF` `0x43ca492f`, `SA_BGEST` `0x43ca4984` (la estimación de fondo **decodifica un JPEG**: `Seq._BgestPre: JPEG_DEC OPEN OFF` `0x43cb1ba1`) y `SA_SSP` `0x43ca49d5`; el **"ALOCK"** enumera sus búferes (`BG_INPUT_IMAGE` `0x43cb1915`, `BG_IMAGE` `0x43cb1952`, `BG_MASK_IMAGE` `0x43cb1988`, `INPUT_IMAGE` `0x43cb19c3`, `INPUT_LPF_IMAGE` `0x43cb1a00`, `ALPHA_IMAGE` `0x43cb1a3d`, `KEY_ALPHA_LPF_IMAGE` `0x43cb1a76`, `SSP_IMAGE` `0x43cb1abb`, `PRE_KEY_SSP_IMAGE` `0x43cb1af6`); y el instante del disparo se calcula en **unidades de VFC** (`vfc2indx: Shot Timing Transform Error` `0x43ca4a8a`, `shot_time_vfc error!` `0x43cb18a9`, `vfc %x vfcSub %x` `0x43c36d0a` → conecta con los dos VFC de `CLK_CTRL`, S85). API del SA: `sa_func_GOLFSHOT_start` con dos sobrecargas (`SSP_START_PARAM*`+`SSP_START_MBX*` `0x43cedc91`; `BGEST_START_PARAM*`+`SA_MBX_0123*` `0x43cedff6`) y `sa_func_GOLFSHOT_release` `0x43cedf67`. **MOTIONSHOT: eliminado por completo en la A6000 fw3.21** (0 apariciones de `sa_func_MOTIONSHOT`; la A7S tiene 5) — lo que queda es `MOTIONSHOTVIDEO` (24 cadenas), del módulo **SFRS** (vídeo en movimiento), que no es lo mismo.

**Corrección de la revisión:** el borrador citaba **etiquetas de Ghidra** (`s__GOLFSHOT__…`) en vez de las cadenas reales, yreatribuía el prefijo de módulo.

**NO VERIFICADO:** qué es exactamente "ALOCK" y cómo se combinan los búferes; la unidad de `vfc2indx`; el significado de `deg`; si el `JPEG_DEC` de BGEST es el decodificador del proyecto; por qué la fw3.21 elimina MOTIONSHOT.

[Conclusiones](../analysis/s88_shotmodes/golfshot_motionshot.md) · [JSON](../analysis/s88_shotmodes/golfshot_motionshot.json).

## S89 — el módulo `IDT`/`IDT_OPD`: mapas del imager, FOPD e IDTSA (21-10-2026)

**VERIFICADO (11 tests, `tests/test_s89_idt.py`):** el módulo `IDT` (297 cadenas que empiezan por `[IDT]`) y `IDT_OPD` (273) es **el mismo código con dos prefijos**: cada mensaje aparece dos veces, contiguas (`4cmap.adrs Err:%X` en `0x43cf2c2e` y `0x43cf2c4b`; igual para `histmap` `0x43cf2c64`/`0x43cf2c83`, `summap` `0x43cf2c9e`/`0x43cf2cbc`, `shade_map` `0x43cf2bf0`/`0x43cf2c11`, `imgmap` `0x43cf1e45`/`0x43cf1e63`, `refmap` `0x43cf1eb5`/`0x43cf1ed3`, `backImgData` `0x43cf1e03`/`0x43cf1e26`, `miniRAW` `0x43cf40e0`/`0x43cf4100`, `msain0/1` `0x43cf463d`/`0x43cf4663`, `msaout` `0x43cf4689`/`0x43cf469e`, `p_backImgData` `0x43cf46ff`/`0x43cf471b`). **Los mapas que entrega al imager**: `backImgData`, `imgmap`, `refmap`, `shade_map`, `4cmap`, `histmap`, `summap`, `miniRAW`, `msain0/1`, `msaout`, más `ie_in/ie_out`, `lc_in/lc_out`, `mapRC_in`, `p_img_map` y `out_opd_cc/out_opd_ec`. El **miniRAW** lo consume directamente el AF híbrido: `[CAMERA_MAIN_LC]: [LC] Movie DM AF cannot get miniRAW Stored memhandle` `0x43c9c8ba` (→ S75/S71). **FOPD** (42 trazas): cuatro canales (`FOPD_AIF_R0/W0/W1/W2_ERROR` `0x43c91547`–`0x43c915a7`), lanzado desde la captura (`KickFOPD error` `0x43cadd2d`/`0x43cadd60`) y repartido por el `SyncResMgr` (`[IDT]r0:… [FOPD]r0:… [PRC]r0…` `0x43ca2939`). **Split/IDTSA** (52 trazas con "Split"): `GetIDTSA Unknown aspect` `0x43cf3306`/`0x43cf332c`, `calc SplitIDTSA error` `0x43cf34d4`/`0x43cf3508`, `IDTSA Invalid Ch select` `0x43cf3538`/`0x43cf3562`, `Illegal FRM mode for IDTSA` `0x43cf5147`, más `Split Movie Cannot use AIF/Insel`, `Fatal Not Copiled for Split Cap` → **captura partida** (2 frames) del AF por desplazamiento. **Regiones de detección** que el IDT calcula para el subsistema de caras: `kido_th[%d].up/dn` `0x43cf2962`/`0x43cf2983`, `ratio_wak[%d].up/dn/rgt/lft` `0x43cf29de`–`0x43cf2aa6`, `sel_hist`/`sel_sum`/`sel_wak`/`sel_waku`, `idealWidth/idealHeight` (mismo tipo de estructura que `box af_island_*` del módulo `[STK]`, S71). Además `VATR` (36 trazas, resultados `det`/`gle`, `0x43cf3ec8`) y `NSX_OPD` (`FRM set SGC unknown` `0x43c915c7`, `FRM start unknown` `0x43c915e9`, `IDT AIF illegal address`).

**NO VERIFICADO:** qué distingue las variantes `[IDT]` y `[IDT_OPD]`; el significado de `kido_th`, `ratio_wak`, `waku`, `gle`; formato y tamaño de cada mapa; qué es FOPD exactamente; cómo se calculan las coordenadas del modo Split; qué es `NSX`/`SGC`.

[Conclusiones](../analysis/s89_idt/idt_opd_maps.md).

## S82 — AutoFraming y las etapas de control del pipeline (21-10-2026)

**VERIFICADO (8 tests, `tests/test_s82_autoframing.py`):** el **encuadre automático** son **tres etapas** del pipeline: `Stage_AutoFraming.cpp` `0x43cc71a3`, `Stage_AutoFraming_ResizeRotate` `0x43cc71b9` y `Stage_AutoFraming_Branch` `0x43cc71d8` — **las mismas tres existen en la A7S fw3.20** (`0x43cc26ac`/`0x43cc26c2`/`0x43cc26e1`). El log clave es `[IMAGING_CAP]: Debug) ResizeRotate Framing size force set: offset[%d,%d] size[%d,%d] rotate[%d]` (`0x43cc7143`; A7S `0x43cc265b`): el encuadre se **impone** con offset, tamaño y **ángulo de rotación**, y antes se **valida** (`ImageAreaResize.us_Size_X/Y` `0x43cc6e5f`/`0x43cc6eaa`; el lienzo debe contener el área `canvas_size.ul_SizeX(%d) < ImageAreaResize.us_Frame_X(%d)` `0x43cc6ef5`/`0x43cc6f79`; y alineación `Align Error … us_Frame_X/us_Frame_Y/us_Size_X/us_Size_Y` `0x43cc6ffd`–`0x43cc70f2`). Las **ocho etapas de control/comunicación** (iguales en A7S): `Stage_CaComm.cpp` `0x43cc7b9c`, `Stage_CameraHAPI.cpp` `0x43cc7bad`, `Stage_Notify.cpp` `0x43caccd6`, `Stage_WaitControl.cpp` `0x43cad784`, `Stage_SACC`/`Stage_SACC.cpp` `0x43c9ee6c`/`0x43c9f18a`, `Stage_Common.cpp` `0x43cac363`, `Stage_DevLater.cpp` `0x43cac51b`, `Stage_DualRec.cpp` `0x43cac9f8`. Relación con el motor de imagen (INFERENCIA por proximidad en rodata): `CaComm`→`CONTP` (`sa_func_CONTP_acquire error` `0x43cc7bfa`), `DualRec`→`DUALREC_BAYER`/`DUALREC_CLEARVID` (`0x43cac9c1`/`0x43cac867`), `SACC`→`NFLASH` (flash) (`sa_func_NFLASH_start error` `0x43c9ef73`); **en AutoFraming no hay ninguna llamada `sa_func_*`**: el encuadre se aplica con parámetros de imagen propios.

**Corrección de la revisión (21-10-2026):** `Stage_WaitControl.cpp` está en `0x43cad784` (en `0x43cad6fd` está `Stage_RchRcv_ResizeTrim`); el error estaba también en el informe de S76 y **se ha corregido allí** (con test). Y es **falso** que en la A7S el AutoFraming esté "disperso o ausente": tiene las mismas tres etapas y el mismo log.

**NO VERIFICADO:** cómo se calcula el encuadre (qué dato lo origina) y qué es la "rotación" que se impone; su relación con los `apc_*` (S78); qué intercambian `CaComm` y `CameraHAPI` con la app; qué es exactamente "SACC".

[Conclusiones](../analysis/s82_autoframing/autoframing_stages.md) · [JSON](../analysis/s82_autoframing/autoframing_stages.json).

## S91 — submódulos del framework ADF: ADJ, SYSND, GS, FACE, AFNR, CH_SRC (21-10-2026)

**VERIFICADO (8 tests, `tests/test_s91_adf_submods.py`):** se cierran los submódulos que S81 dejó abiertos. **`[ADF][ADJ]`** (24 trazas) = el ajuste del **sensor de audio** (`AdfSenserCtrl::SetParamSet{MicMode 0x43c26dc1, RecLevel 0x43c26df4, ChSource 0x43c26e28, InputType 0x43c26e5c, RecLevelMode 0x43c26e91, HpMonitor 0x43c26ec9, InputTrim 0x43c26efe, LowCut 0x43c26f33}`) → es la **implementación** de los comandos de depuración `[ADF][DBGCMD] InputPro Set*` de S81 (enlace con S69). **`[ADF][SYSND]`** (27) = el **sonido del sistema** (pitido) con compensación de retardo por **60/50 Hz** (`m_StartTransDelay60` `0x43c279a4`, `m_StartTransDelay50` `0x43c279f9`, `m_dummySetOutputSysndDelay` `0x43c27941`, `PS ON` `0x43c278f0`) → el retardo se ajusta al estándar de TV de la región (mismo eje que el `DOWNCON` PAL/NTSC del visor, S86). **`[ADF][GS]`** (2) = arranque de un "path" de proceso (`START PROC PATH ERR` `0x43c327d3`, `START STATE ERR state : %x` `0x43c327f2`). **`[ADF][FACE]`** (2) = el ADF **arranca y detiene la detección de caras** (`StartExecFace` `0x43c32a3b`, `StopExecFace` `0x43c32a54`) → puente explícito ADF↔S71. **`[ADF][AFNR]`** (2) = proceso de **reducción de ruido del AF** (`StartExecAfnr:%x` `0x43c32990`, `StopExecAfnr` `0x43c329ac`). **`[ADF][CH_SRC]`** (1) = arranque del **micrófono AVIO** con FIFO (`AvioMicStateStart fifoErr %x` `0x43c2e99a`).

**NO VERIFICADO:** qué es "GS"; el parámetro de modo de AFNR; los 24 mensajes completos de ADJ; la relación exacta de los retardos 60/50 Hz con el estándar de TV.

[Conclusiones](../analysis/s91_adf/adf_submodules.md).

## S87 — almacenamiento, sistema de archivos y tarjeta (21-10-2026)

**VERIFICADO (9 tests, `tests/test_s87_storage.py`):** en `av-cam.bin` el **medio externo** es un recurso sincronizado de `CAMERA_MAIN_SYNC` (`ExternalStorageStart/Acquire/Release() Error` `0x43cb3148`/`0x43cb317f`/`0x43cb31b8`; A7S `0x43cb4372`), la ruta de la foto RAW es **`DCIM/100MSDCF/DSC%05d.ARW`** (`0x43cac566`; A7S `0x43cb022b`, más el ejemplo literal `DCIM/100MSDCF/DSC00001.ARW` `0x4401ea7f`) y **`/setting/psd.bin`** (`0x43ccf2b6`) es **novedad fw3.21** (0 apariciones en la A7S → coherente con S75 y S72). **Negativo verificado**: en `av-cam.bin` hay **0 apariciones** de `exFAT`/`EXFAT`/`FAT32`/`CLIP_` → el sistema de archivos está **en el userland**: **`libInfraFsys.so`** (375 524 B; **51 × "EXFAT"**, 8 × "FAT32"; estructuras **BPB** `BPB_Media`, `BPB_TotSec16/32`, `block size/start (org|adj)` y atributos `FSYS_ATTRIB_{ALL,ARCHIVE,DIRECTORY,HIDDEN,NONE,READONLY,SYSTEM,VOLUME}`; fechas con **desplazamiento UTC** y precisión de 10 ms), **`libObj.so`** (17.4 MB; **13 × "CLIP_"**; el modelo de contenido con `contentType`, `entryCondition`, `p_entryIdList`, `mainJpg`, `thumJpg`, `screenNail`, `exifSrcArea`, `lensModel`, `publicMakerNote`/`secretMakerNote` y, para el espacio, **`forcastUseSizeOnDstDisc`** (previsión del tamaño de la próxima captura), `remainSizeOnDstDisc`, `isExistUnsupportedContent`, `dubbingProhibitionFactor`) y **`libmpr.so`** (10.3 MB; el **índice**: `category folder`, `date num`, `entry num`, `last date folder`, `playlist num/folder/category folder`, `total mark num`, `creationTime`, `thumbPictFileModTime`, `aviFileModTime` y `seekPoint … packLength` → el índice apunta a posiciones dentro de los packs).

**Correcciones de la revisión:** las direcciones del borrador eran **offsets de fichero** (`0x772148`…) y no direcciones del binario; `CLIP_` **no está** en `av-cam.bin` sino en `libObj.so`/`libmpr.so`; y la implementación exFAT/FAT32 **sí** existe, en `libInfraFsys.so` (con BPB y atributos FSYS).

**NO VERIFICADO:** MBR/particiones y formateo; el máximo de imágenes por carpeta y la regla "reducir/divide"; la codificación de prefijos más allá de `DSC%05d.ARW`; el formato binario de `Index/`/`SceneInfo`/`DCF`; los contenedores de vídeo en tarjeta.

[Conclusiones](../analysis/s87_storage/storage_filesystem.md) · [JSON](../analysis/s87_storage/storage_filesystem.json).

## S93 — el bus de mensajes OSAL del userland (21-10-2026)

**VERIFICADO (6 tests, `tests/test_s93_osal_bus.py`):** el lado Linux de la cámara se organiza en **microservicios** que se hablan por colas OSAL, con dos niveles: **GID** (grupo, 16 nombres) y **LID** (cola, 13 nombres). Grupos: `AIRPLANE_MODE_SCALAR_API`/`_TEST` (libInfraAirplaneMode), `APP_VIEW_SCALAR`/`INFRA_VDF`/`CAMERA_RAW_DEVELOP`/`NET_BACKUP_SERVER` (libObj), **`DETECT_FACE`**/`DMM_CTRL`/`SADRIVER` (libBizFw), **`GPS_GET`** (libmpr), `NETSERVICE_SCALAR_API`/`SYNC_EMU`/`TEST` (libNetService), **`TASK_ADC`** (libRsrcHotshoe), `WLAN_RSRC_DBG`/`_TEST` (libWlanResource). Colas: `AIRPLANE_MODE_API`, `DLNACONTROL_CP`/`_MAIN`/`_MEDIASVR` (libInfraDlnaControl), `GPS_GET` (libmpr), **`MDNS_CONTROL_MAIN`** (libInfraMDnsControl), `NETFUNCTIONMGR_MAIN` (libInfraNetFunctionManager), `NETSERVICE_ASYNC_REQ`/`SYNC_REQ` (libNetService), `NET_BACKUP_SERVER_INFRA_NET_SERVICE_CMP` (libObj), `R_HOTSHOE_API` (libRsrcHotshoe), **`WEBAPI_MAIN`** (libInfraWebApi), `WLAN_RSRC_API` (libWlanResource).

**Lo que revela (VERIFICADO):** el "firmware de negocio" `libBizFw.so` es quien **orquesta la detección de caras** (`OSAL_MSGQ_GID_DETECT_FACE`) y el driver del escalar; la **A6000 incluye soporte de GPS en el firmware** (`libgps_rsrc.so` + `OSAL_MSGQ_GID_GPS_GET` en libmpr) aunque no tenga GPS de hardware (código heredado de la A7S); y la cámara **se anuncia por mDNS y expone una API web** (`libInfraMDnsControl.so`, `libInfraWebApi.so`).

**NO VERIFICADO:** los mensajes concretos de cada cola; qué sirven `CAMERA_RAW_DEVELOP` y `NET_BACKUP_SERVER`; si el bus OSAL del userland es el mismo que el ADF del firmware; el protocolo de la API web.

[Conclusiones](../analysis/s93_osal_bus/osal_message_bus.md).

## S90 — reproducción de vídeo: PlayArranger, VFC y VDISP (21-10-2026)

**VERIFICADO (23 tests, `tests/test_s90_playback.py`):** el subsistema de reproducción de vídeo del `av-cam.bin` se articula en **tres ejes**: (1) los **organizadores de reproducción** (`20AbstractPlayArranger` `0x43c43c7c`, `12PlayArranger` `0x43c43c93`, `19PlayArrangerAdapter` `0x43c43cd2`, `16NullPlayArranger` `0x43c43d00`, `20VideoArrangerAdapter` `0x43c43cbb`, `22VideoReserveCmdCreator` `0x43c43ca2`); (2) el **programador de VFC** (contador de campos de vídeo: `20AbstractVFCCmdIssuer` `0x43c43dea`, `12VFCCmdIssuer` `0x43c43e01`, `12VFCScheduler` `0x43c43e95`, `12VFCSchedulerCore` `0x43c43ea4`, `14VFCScheCmdList` `0x43c43e3a`, `16VFCReScheCmdList` `0x43c43e4b`, `24VideoFieldCounterFactory` `0x43c43e1f`) que **programa los comandos al reloj de vídeo** (mismo reloj que `CLK_CTRL`, S85); y (3) el **estado de reproducción** (`10MPlayState` `0x43c43ecf`, `MPlay` `0x43c66542`) con la traza ` bid=MPLAY cid=%#hx flg=%d dvfc=%#x ivfc=%#x edge=%#hx` (`0x43c660e0`) y `Issue VFCCmd to MPLAY.` (`0x43c7291e`). El **visor de vídeo** (VDISP) tiene **cuatro modos de salida**: `VDISP24p` (`0x43c4811f`), `VDISP30p25p` (`0x43c481c2`, `SeqCtrl,PcpSet`), `VDISP60i50i` (`0x43c48341`) y `VDISP60p50p` (`0x43c4856a`), cada uno con su lógica de descarte de cubos TCUB (`[DiscardTcub] [cnt:t/b/p][%d] tc[%d][0x%02x%02x…]`) y su `GetPlayState(): DISP_PLAY_UNKOWN is NOERR` → el **mismo eje de down-conversion PAL/NTSC** que S86. Además, la reproducción consume el bloque `AUGI` (`16DecAugiConverter` `0x43c43d2a`, `20NullDecAugiConverter` `0x43c43d13`, `21DecTcubEventRequester` `0x43c43ce8`) y la tabla de secuencia VP (`24AbstractVpTableSequencer` `0x43c43d3d`, `16VpTableSequencer` `0x43c43d58`, `6VPInfo` `0x43c43d6b`, `10VPInfoCore` `0x43c43d73`, `21AbstractTblMsgHandler` `0x43c43d94`, `13TblMsgHandler` `0x43c43dac`).

**Revisión:** verificado por muestreo (15/15 nombres de clase en sus direcciones + las cadenas `bid=MPLAY`, `Issue VFCCmd to MPLAY.` y los cuatro modos VDISP): el informe del subagente era correcto, sin correcciones.

**NO VERIFICADO:** la semántica exacta de `cid`/`flg`/`dvfc`/`ivfc`/`edge` en la cabecera MPLAY; qué son los "cubos TCUB" que se descartan; la relación entre `VPInfo` y el `AUGI` de S83; el punto de reanudación (`18ResumePointChanger` `0x43c43f04`) y la reserva (`18ReserveCmdRegister` `0x43c43f47`).

[Conclusiones](../analysis/s90_playback/playback.md) · [JSON](../analysis/s90_playback/playback.json).

## S95 — los ficheros que la cámara lee y escribe (21-10-2026)

**VERIFICADO (7 tests, `tests/test_s95_files.py`):** el firmware de la A6000 usa **43 rutas de fichero** en cuatro zonas: **`/usr/sabin/`** (27), **`/mnt/`** (11), **`/setting/`** (1) y **`/usr/dfe/`, `/etc/`, `/usr/share/`** (4). **Parámetros de procesado**: **22 ficheros SPICA** con la nomenclatura `spica_musashi_<modo>_<canal>_tap_step<N>.bin` (`<modo>` ∈ still, mov, mov_4k, mov_interlace, dualrec, dualrec_4k; `<canal>` ∈ **C**/**Y**; dos pasos) — confirma y precisa lo que S76 apuntaba: el procesado SPICA toma sus parámetros de ficheros externos, con variantes por modo de captura (incluida la grabación dual BAYER+CLEARVID de S82); además `star_kernel_param.bin` (`0x43cc3d1a`, el kernel STAR de S84) y las **tablas de PSF** de la deconvolución `dcv_psf_table_{still,movie,movie_4k,dualrec}.bin` (`0x43cb9a34`–`0x43cba9ea`, para `Stage_Decomp`/`Stage_LoadDeconvPsfTbl` de S76). **La cámara escribe sus propias trazas en el disco RAM**: `/mnt/FILE_IS_%04x.dat` (IS/EIS, S70), `/mnt/FILE_TC_COMMON_%04x.dat` (giro, S70), `/mnt/lc_mslog_%04x.dat` (calibración de lente/ZPD, S75), `/mnt/Mount_ms_log_%03d.dat` (montura, S66), `/mnt/cc_ms_log%04x.dat` (control de captura, S82), `/mnt/detect_ms_log%04x.dat` (detección, S71), `/mnt/YC_FILE%04x.dat`, `/mnt/log.bin` y `/mnt/%s.%4d%02d%02d_%02d%02d%02d.dat` (con **fecha y hora** en el nombre) → **estos ficheros deben estar en los volcados de RAM de la cámara** (`analysis/camera-dumps/`, S64/S65) y son una fuente primaria para contrastar los hitos sin más instrumentación. Otros: `/usr/dfe/dfe.bin` (`0x43cd1b94`, la imagen del DFE), `/setting/psd.bin` (`0x43ccf2b6`, 0 en A7S), `/etc/localtime`, `/usr/share/zoneinfo`, `/usr/share/locale`.

**NO VERIFICADO:** el formato binario de los `spica_musashi_*` y de las tablas PSF; qué es "musashi"; el formato de `/mnt/*.dat`; si esas trazas sobreviven en el volcado de RAM; por qué 4K y dualrec tienen parameter sets propios.

[Conclusiones](../analysis/s95_files/file_inventory.md) · [JSON](../analysis/s95_files/file_inventory.json).

## S92 — la base de datos de medios: SceneInfo, MovieFile e índice (21-10-2026)

**VERIFICADO (10 tests, `tests/test_s92_mediadb.py`):** el modelo de medios de la cámara tiene su parte de **userland** (`libmpr.so`, `libObj.so`, `libInfraFsys.so` — ver S87) y su parte de **firmware** en `av-cam.bin`: el **secuenciador LIRO** (`[CAMERA_MAIN]: LiroSequencerMovieFileFormat : %d` `0x43ca3b3a`, que además lee la **posición del dial de diafragma**: `LiroSequencer cannot read IRIS_DIAL_POS` `0x43ccadbf`) y la **nomenclatura de escena** `Scene%02d.txt` (`0x43ccb21b`). En el userland, la interfaz `MprIf` (1525 apariciones en `libmpr.so`) gestiona el contenido: `PreRegisterDcfContentSync` (8), `GetHighlightSceneInfo` (2), `SceneInfo` (10) y, en `libObj.so`, `SceneInfo`/`HighlightScene` (5). La ruta de la foto sigue siendo `DCIM/100MSDCF/DSC%05d.ARW` (`0x43cac566`).

**Revisión:** verificado por muestreo (todas las cadenas citadas en sus direcciones) — el informe del subagente era correcto, sin correcciones; se añade el dato de `IRIS_DIAL_POS`.

**NO VERIFICADO:** el contenido de los `Scene%02d.txt` y dónde se almacenan exactamente; la relación con la especificación **DCF** (`xDCF`/`D2FxDCF` en el blob); cómo se relacionan `MovieFileFormat` y la nomenclatura de clips de la tarjeta; el formato del índice en disco (`Index/`).

[Conclusiones](../analysis/s92_mediadb/media_database.md) · [JSON](../analysis/s92_mediadb/media_database.json).

## S94 — la API HAPI de la app remota (21-10-2026)

**VERIFICADO (6 tests, `tests/test_s94_hapi.py`):** `libHapiLib.so` (89 628 B en A6000; 77 380 B en A7S) es la biblioteca de la **API de la app remota** (HAPI). Estructura (símbolos mangled verificados): `HapiLibMain` (singleton, `getInstance`, `mainLoop`, `interrupt`, `getTargetQId`), `Cam::CamService` (`getInstance`, `run`, `interrupt`, `processReq(REQ_MSGE)`, `processComp(COMP_MSGE)`, `processCaptureEvent(EVT_MSGE)`) y `Sdf::SdfService` (`run`, `interrupt`). Tipos de mensaje: **`REQ_MSGE`** (29 apariciones), **`EVT_MSGE`** (3), **`COMP_MSGE`** (53), `SDF_MSG_SENDE` (6), `MAIN_MSG_RECVE` (4) y la categoría **`CATEID_HAPI`** (1) con `CATEID_SDF_ACK/COMP/NEXT`. La API de cámara propiamente dicha son **139 símbolos `Camera::CamApi*`** (`CamApiBase::apiFactory`, `stmDepositYc`, `stmDepositRaw`, `stmInquire`, `stmWithdraw`, `checkOneTicket`/`checkThreeRawTickets`, `convertErrorCode`, `freeImageInstance`/`freeExif`/`freeStdYc`, `setHapiCommon`) → la app puede **depositar YC o RAW, pedir/info/tirar de tickets y recibir eventos de captura**. Del lado de la cámara, la etapa `Stage_CameraHAPI.cpp` (`0x43cc7bad`) es el punto de entrada (S82).

**NO VERIFICADO:** los IDs numéricos de `msg_id` (qué acción corresponde a cada uno); el mapeo exacto cola OSAL ↔ `Stage_CameraHAPI`.

[Conclusiones](../analysis/s94_hapi/hapi_api.md) · [JSON](../analysis/s94_hapi/hapi_api.json).

## S96 — modos de captura: `drive_mode`, `CapMode` y la tabla 69 → 14 ShdMode (21-10-2026)

**VERIFICADO (7 tests, `tests/test_s96_modes.py`):** hay **dos niveles de "modo"**. El **`drive_mode`** es el modo del **imager** (0..0x44 = **69 valores**): lo usan `SetExposure`/`Execute`/`SetRead`/`GetModeParam` (`[CAM_IMAGER]: Invalid SetExposure Error!! [drive_mode:%2d]` `0x43c9397a`, `Invalid Execute` `0x43c93a6c`, `Invalid SetRead` `0x43c93d30`, `GetTransModeState DriveMode Error!! [src_drive_mode:%02x] [dest_drive_mode:%02x]` `0x43c94a9f`, `Invalid GetModeParam` `0x43c94aff`), sincroniza con el resto del sistema (`SIFSyncCode`, `GetPrelightImagerDriveMode` `0x43cae26b`) y **condiciona el tamaño de lectura** (`getDriveModeSizeRatio` `0x43cae2b7`); y el **patrón de ojos** depende de él (`[DFECore]: eyePtn:%d is unusable in driveMode:%d.` `0x43c92bde`). El **`CapMode`** (con `ExposureID`, `ContID`, `FrameID` y `BDROSeq`) es el modo de la **captura**, en `CAMERA_MAIN_CC`: `ExtractCaptureData()` `0x43ca54c8`, `CaptureInit()` `0x43ca552b`, `SetReadImageParam()` `0x43ca55a9`, `SetNRParam()` `0x43ca5627`, `SetOPDParam()` `0x43ca56a5`. El cruce modo→sombreado es la tabla `tbb` de **69 bytes** en `0x438ef418` que usa `SHD::GetShdMode` (`0x438ef40e`, `cmp r3,#0x44` + `tbb [pc,r3]`) y que reduce los 69 modos a **14 ShdMode** (S66). Modos nombrados en el firmware: foto (`SDF_RECMODE_STILL_REC` `0x43c7effb`), vídeo (`REQ_MOVIE_REC` `0x43ca13be`), ráfaga (`BURST_CNT` `0x43cb4bfe`), panorámica (`MSG_ID_SDF_PANORAMA_CCNR_ENCODE` `0x43c781e4`), barrido (`PanoramaSweepStart` `0x43cab054`), bracketing (`lc_BracketAF.cpp` `0x43ca79ba`), intervalo (`[SDF] interval(PTM) %ld` `0x43c7a1a5`) y golf (S88).

**NO VERIFICADO:** la tabla de 69 `drive_mode` con nombre (no está en el blob); el rango de `CapMode`/`ContID`; cómo se calcula `BDROSeq`; la equivalencia `drive_mode` ↔ `CapMode`.

[Conclusiones](../analysis/s96_modes/capture_modes.md).

## S97 — sincronización audio/vídeo del codificador (21-10-2026)

**VERIFICADO (12 tests, `tests/test_s97_encsync.py`):** los módulos que coordinan audio, vídeo y el codificador AVC en la A6000 fw3.21: **`[ENCMODEMGR]`** (21 trazas, `0x43c4ac73`) = `McAvcEncModeMgr` (`15McAvcEncModeMgr` `0x43c431fb`), que gestiona el modo de encoding y la **secuencia de comandos** (`RecordCodecIfCmd: CmdCode/CmdTime/ExecTime/CurrentRefTime`, `ComQue CANNOT Exec!`, y los `CMD_ID_*`: `ACT_ENC`, `GET_REF_TIMER`, `INIT_ES_API_PARAM`, `INACT_CHIP`, `ALLOC_USER_DATA_AREA`, `BEGIN_ENC`, `SET_SEQ_PARAM`, `TERM_ENC`, `STILL_ENC`, `APPLY_USER_DATA_GOP/PIC`, `MUTE_AUDIO_CAPTURE`, `INIT_RC_BUFFER`, `SET_RC_WTPT`, `SET_ENC_READ_POINTER`; métodos `ProcVsyncPre/Post`, `ProcMsg(MSG_MC_AVC_ENC*)`, `EnqueueCodecIfCmd`); **`[ENCAUDOUCR]`** (9, `0x43c4b444`) = escritura del bloque **AUGI** con el audio (`IsOuCrank/Sampling/FrameRate/ImagingRate`, `TermEnc(vfc24/vfc32/cnt): NormalTerm/OuCrankTerm/GopNum`, `Begin Enc: StartAdr/BuffAdr/BuffSize`, `AUGI(AVCODEC-AVSC) OverFlowFile:`, `WriteAugi : AUGI FLAG END`, `[AUDIO INFO] Pts = 0x%08x EndFlug = 0x%02x, Num Au = %x`); **`[ENCAUDSYNC]`** (17, `0x43c526d3`) = sincronización por **semáforos** (`McSyncEncStart::SetEncStartTimeForThumbnail`, `MC[%d] comes later/earlier`); **`[ENCOUCUDMG]`** (7, `0x43c522fb`) = desbordamiento/alineación de datos de usuario; **`[VIDENCCTRL]`** (13, `0x43cd6070`) = control del encoder con 22 apariciones de `MSGID_AVC_ENC_VIDEO_*`; más los ya decodificados `[VIDENCSTAT]` (70) y `[ENCOUCSTAT]` (49).

**Corrección de la revisión (21-10-2026):** (a) el borrador daba **offsets de fichero** (`0x70a444`…) → convertidos a direcciones del binario (`0x43c4b444`, `0x43c4ac73`, `0x43c631fb`, `0x43c522fb`); (b) es **falso** que estos módulos sean exclusivos de la A6000: la A7S fw3.20 tiene **el mismo conjunto y los mismos recuentos** (`ENCMODEMGR` 21, `ENCAUDSYNC` 17, `ENCAUDOUCR` 9, `ENCOUCUDMG` 7, `VIDENCCTRL` 13, `VIDENCSTAT` 70) y los mismos símbolos; la única diferencia es que la A7S tiene **5 trazas de error más** en `[ENCOUCSTAT]` (54 frente a 49).

**NO VERIFICADO:** el formato exacto de los mensajes `MSG_MC_AVC_ENC*`; el formato del bloque AUGI en la tarjeta; cómo se eligen los parámetros de sincronización.

[Conclusiones](../analysis/s97_encsync/encoder_sync.md) · [JSON](../analysis/s97_encsync/encoder_sync.json).

## S99 — la arquitectura del userland: las capas de `libObj.so` (21-10-2026)

**VERIFICADO (6 tests, `tests/test_s99_userland.py`):** `libObj.so`, la mayor biblioteca del userland (17 436 172 B en A6000; 16 184 848 B en A7S), contiene **2507 símbolos mangled en 167 namespaces** (la A7S: 2538 en 168) → el userland de la A6000 es **prácticamente el mismo** que el de la A7S. Reparto por capas: **`MprIf`** (318, medios: contenidos, carpetas por fecha, playlists — S87/S92), **`MWF`** (241, núcleo de mensajes: `MWF::ObjMsgList`/`ObjMsg`/`ObjMsgEntry`/`RsrcAcsr`), **`ux`** (227, gráficos: `ux::core::GraphicsImage`, `GraphicsSystem::setOSDGainParam`, `TextLayout::registerFontFaceFile`), **`AVBIZ`** (138, *universo de aplicaciones*: `AVBIZ::UNIVERSE::UActiveObject` con `onStarting`/`onStopping`/`SendMsgToApp`/`eventProcessing`, `UBbSuspend`/`UBbResume`, `SelectorProxy`, `ULog_u16x5`/`ULog_u8x10`), **`OBJAVBBCBASECLASS`** (128, el puente de imagen Obj→AVBBC, S16–S30), **`MprCtrl`** (58), **GUI** (`ViewBase` 53, `LayoutableWidgetBase` 45, `AppWidgetBase` 27, `DefRootView` 22, `CmnViewMenuData` 23) y el **toolkit `GEN_*`** (`GridList` 45, `Calendar` 34, `Button` 29, `Label` 24, `Balloon` 22, `EditBox` 20), **`C_DataflowInfra_*`** (44, pipeline de datos), **`InputService`** (36), **`UFW`** (34, recursos: `DfsWrapper`, `MsgReceiver::RcvMsg/PostMsg`, `RsrcWrapper::AcquireSingle/ReleaseAll`), **`NetCommonLibrary_*`** (25) y **`GCM_*`** (24), más `ScalarView` (17), `HighlightManager` (19) y `GlobalAccessor` (18).

**Lo que revela (VERIFICADO + INFERENCIA):** el userland es **capas** — `MWF` (mensajes) + `UFW` (recursos) como base, `MprIf`/`MprCtrl` para medios, `ux`+`GEN_*`+`ViewBase` para la **interfaz**, `AVBIZ::UNIVERSE` como **gestor de aplicaciones** con mensajería asíncrona, `OBJAVBBCBASECLASS`+`C_DataflowInfra_*` para la **imagen**, `NetCommonLibrary`+`GCM` para la **red**. `UFW::RsrcWrapper::AcquireSingle/ReleaseAll` es el **arbitraje de recursos** del lado Linux (coherente con el `SyncResMgr` del firmware, S81) y el "escalar" aparece en ambos lados (`ScalarView`, cola `SADRIVER`, S93). **La A6000 tiene 10 símbolos menos de red** (`NetCommonLibrary_`: 25 frente a 35), coherente con S72.

**NO VERIFICADO:** qué separa `MprIf` de `MprCtrl` y `MWF` de `UFW`; los 167 namespaces completos; cómo se registran las apps del `UNIVERSE`.

[Conclusiones](../analysis/s99_userland/userland_architecture.md).

## S98 — `libBizFw.so`: el orquestador userland y el puente con el ADF (21-10-2026)

**VERIFICADO (9 tests, `tests/test_s98_bizfw.py`):** `libBizFw.so` (**332 600 B**, *stripped*) es la biblioteca que **une el userland con el firmware**: usa tres colas OSAL (`OSAL_MSGQ_GID_DETECT_FACE`, `OSAL_MSGQ_GID_DMM_CTRL`, `OSAL_MSGQ_GID_SADRIVER`), define **9 categorías** de mensaje (`CATEID_PIN/RENDERER/DISPLAY/SYSTEMSOUND/AUDIOPROCESSOR/MIC/MIXER/SPEAKER/EFFECT`), **1 identificador** (`MSG_ID_VDF_SRVC_SET_YC_REC_CONTROL`, el control de grabación YC dirigido al servicio del visor) y **11 peticiones** con respuesta (`REQ_DEPOSITE`, `REQ_DEPOSIT_MULTIE`, `REQ_DESTRUCTE`, `REQ_INQUIREE`, `REQ_OVERWRITEE`, `REQ_PARSEE`, `REQ_PEEKE`, `REQ_POKEE`, `REQ_RAW_PARSEE`, `REQ_SHAREE`, `REQ_WITHDRAWE` → el ciclo de vida de un objeto: depositar, consultar, compartir, releer, destruir), más la clase de estado `StmCh`. **El puente es la clase `OBJAVBBCBASECLASS::AdfCh`**: sus métodos repiten **exactamente** el vocabulario de los comandos de depuración del ADF del firmware (S81) — `PrcSetPath` ↔ `Prc SetPath`, `SysSetTable`/`SysRequest`/`SysSetPath` ↔ `Sys …`, `InSetInput`/`InSetIVoice`/`InSetLowCut`/`InSetWindNr` ↔ `In …`, `PrcSetFader` ↔ `Prc SetFader`, `OutSetOutput`/`OutSetSpSwap`/`OutSetVolume` ↔ `Out …` → **la numeración de prefijos (`Prc`/`Sys`/`In`/`InPro`/`Out`) es el contrato entre userland y firmware**. El userland envía mensajes a **diez destinos**: `ADF`, `DETECT`, `DMM`, `HAPI`, `HDMI`, `SA`, `SDF`, `SDI`, `VDF`, `VEF`. En el firmware, el escalar tiene **125 nombres de clase RTTI `NS_SCALAR_INFRA*`** (p. ej. `N15NS_SCALAR_INFRA21ScalarInfraSequenceIfE` `0x43ce59d2`). El vocabulario es **idéntico en la A7S fw3.20** → código compartido.

**Corrección de la revisión (21-10-2026):** las trazas `PrcSetPath to ADF` y `Snd Msg to ADF` **no están en `av-cam.bin`** (0 hits) sino en `libBizFw.so`: es el **userland** quien envía al ADF (el subagente las atribuye al firmware). El test lo fija.

**NO VERIFICADO:** el formato binario de los mensajes ADF y la tabla de equivalencia con las 11 peticiones; qué distingue el canal `SA` de `SADRIVER`; el mapeo de `MSG_ID_VDF_SRVC_SET_YC_REC_CONTROL` al servicio del visor.

[Conclusiones](../analysis/s98_bizfw/bizfw_bridge.md) · [JSON](../analysis/s98_bizfw/bizfw_bridge.json).

## S100 — el contrato de comandos del ADF (firmware) ↔ `AdfCh` (userland) (21-10-2026)

**VERIFICADO (7 tests, `tests/test_s100_adf_contract.py`):** el firmware expone su control interno como **90 comandos `[ADF][DBGCMD]`** agrupados en familias: `Input` 16 (`SetInput`, `SetInputContinue2/3/4`, `SetExtType`, `SetRefLevel`, `SetZoomLink`, `SetLowCut`, `SetUnderWater`, `SetRecLevel`, `SetReverseLR`, `SetAdjThrough`, `GetShoe*`/`SetShoeOnComp`), `InputPro` 8 (`SetIntMicSens`, `SetInputType`, `SetInputTrim`, `SetChSource`, `SetRecLevelMode`, `SetAgcLink`, `SetManualGainLink`, `SetRecLevelLimitter`), `Output` 9 (`SetOutput`, `SetOutputContinue2/3/4`, `DetectJack`, `SetHdmiFormat`, `SetAntiClipping`, `SetSpSwap`), `OutputPro` 3, `System` 12, `SystemSound` 7, `Proc` 19 (las **fases lineales del arranque**: `SetLinearPhase`, `LinearPhase{SetDec0/1,SetAip0/1,GetSa0/1,GetPin0/1,Nomatch0/1,SetMb,SetSa,MemPrint}Print`, `SetPath`, `SetMixRatio`, `SetFader`, `SetZoomNr`), `SoundAnalyzer` 4 (golf, S88) y `CPU2` 4 (la **medida del tiempo de ejecución** a 60/48 Hz, S81). El userland (`libBizFw.so`) implementa la clase **`OBJAVBBCBASECLASS::AdfCh`** con **35 métodos** (`Prc` 8, `Sys` 4, `In` 8, `InPro` 7, `Out` 8) y **cada uno tiene su comando gemelo en el firmware con la familia traducida** (`PrcSetPath`↔`Proc SetPath`, `SysSetTable`↔`SystemSound SetTable`, `InSetInput`↔`Input SetInput`, `InProSetAgcLink`↔`InputPro SetAgcLink`, `OutSetOutput`↔`Output SetOutput`, `OutProSetHpMonitor`↔`OutputPro SetHpMonitor`) → **la numeración de prefijos y verbos ES el contrato userland↔firmware**. Excepciones: cuatro métodos solo en userland (`PrcSetPeakDetect`, `PrcSetAudioOutpinMute`, `OutSetVolume`, `SysSetVolume`) y un comando solo en firmware (`InputPro SetManualGainLink`); el userland no puede invocar los comandos de inspección (`LinearPhase*`, `CPU2 ExecTime`, `SoundAnalyzer*`, `ClearMSGQ`, `CountMSGQ`, `GetMSGQ`).

**NO VERIFICADO:** el formato binario de cada comando y su equivalencia con las 11 peticiones `REQ_*` (S98); qué hace el submódulo `Prc`; la semántica de `PrcSetPeakDetect`.

[Conclusiones](../analysis/s100_adf_contract/adf_command_contract.md).

## S104 — prefijos de traza exclusivos de la A6000 (21-10-2026)

**VERIFICADO (6 tests, `tests/test_s104_prefixes.py`):** seis prefijos de `analysis/s79_modules/module_map.json` que la A7S fw3.20 **no** tiene. `ADC_DEBUG` (14 cadenas, `0x43ce50dd`→`0x43ce5273`): ADC de **12 canales** del LIRO, tarea `TSK_ADC` y `boot_exit_adcliro`, mensaje OSAL de 0x20 B con cabecera `0xfff1` (`0x4398eb22`). `AVR` (2, `0x43c25502`→`0x43c25528`): **accesorio** LANC-AVR del módulo `ACCY` (`LANC-AVR Attached` `0x43c252b4`, handlers GPIO `0x43565680`/`0x435656d4`). `ADR` (1, `0x43cce3fa`): **campo** de dirección de una apertura IM dentro de un mensaje de `0x43901d50`, no un módulo. `BKID` (4, `0x43cce1ea`→`0x43cfb1a8`): *backup ID* (`BKID_SDF_QTBL_C` `0x43c77aeb`, `Backup_read(BKID_*)`). `AVOUT` (2, `0x43c2549e`→`0x43c254c6`): accesorio **AvOut** de `ACCY` (`AvOut Attached` `0x43c25260`). `CAMCORE` (37, `0x43c905ca`→`0x43cebcb2`): la librería **`Camera::CamCore`** (SGC, RDC/PFR, AIF/DMA, recursos, `ExlHelper`; RTTI `N6Camera7CamCore8RdcImageE` `0x43c906b6`).

**Corrección de S73:** hay **cinco** cadenas `ADJ ADC`, no cuatro; `GET_DATA` (`0x43ce4fc7`) no está referenciada.

## S103 — el subsistema SDF: la capa de dataflow de imagen still (21-10-2026)

**VERIFICADO (51 tests, `tests/test_s103_sdf.py`):** `[SDF]` = **477 trazas** (`0x43c7785b`→`0x43c806f9`) y **15 `[SDF_ERR]`** (`0x43c7a145`→`0x43c7eb78`). SDF es el **ejecutor de trabajos** de imagen still: el gestor de captura (`IMAGING_CAP`, S106) le envía **33 `MSG_ID_SDF_*`** distintos (`paint_image`, `copy_image`, `resize_rotate`, `resize_rotate_lowspeed`, `encode_jpeg`, `decode_jpeg`, `encode_jpeg_rec`, `decode_jpeg_rss`, `encode_jpeg_with_work`, `redeye`, `beauty_effect`, `image_effect`, `image_mix`, `split_encode`, `split_resize`, `develop_resize`, `develop_resize_apl`, `scn_encode`, `scn_encode_with_thm`, `ccnr_encode`, `ccnr_encode_with_mode`, `ccnr_resize`, `panorama_ccnr_encode`, `thm_copy`, `thm_encode`, `jpeg_sort`, `dist_encode`, `dist_resize`, `dist_resize_no_tanz`, `face_resize`, `set_date_image_param`, `set_date_image_param_dual`, `ptm_count`), todos en `0x43c78000`→`0x43c78350`. Los errores son casi todos de **PTM** (`bigger_value.ptm_32==PTM_SECOND_ZONE`, `smaller_value.ptm_32==PTM_FIRST_ZONE`, `interval PTM`, `check stop PTM`) → el temporizador de imagen (`PTM`, `MSG_ID_SDF_PTM_COUNT`). Funciones: `FUN_43638308` (init; pasa `0x43c77857` = la cadena `"sdf"`), `FUN_435ab6f0` (dispatcher), `FUN_4363c730` (factoría de trabajos JPEG), `FUN_4363ca28` (ejecutor), `FUN_43639c78` (manejador de mensajes). En userland, `OBJAVBBCBASECLASS::SdfCh::{resizeRotate,paintImage,copyImage}` (`libObj.so`). La A7S fw3.20 tiene el mismo módulo con **479** trazas (`0x43c7a1eb`→`0x43c83082`).

**NO VERIFICADO:** el significado del acrónimo (la hipótesis *Still DataFlow* encaja con `DataflowInfraErrorCode` en la primera traza, pero no hay evidencia textual); el formato de los mensajes `MSG_ID_SDF_*`; las dos trazas de diferencia con la A7S.

## S69 — subsistema de audio de la A6000 (línea general) (21-10-2026)

**VERIFICADO (9 tests, `tests/test_s69_audio.py`):** el audio del `av-cam.bin` A6000 es un *IP* más del driver de sensor: arranque `AUDIOIP INIT COMP` (`0x43c26411`) con configs VGS/PR/MF/CONS/BANDI; micrófono (`AdfSenserCtrl::SetParamSetMicMode` `0x43c26dc1`, `Abb::SetMicConfig` `0x43cddad4`, `AbbMicSensAdjustCtrl::SetStatus` `0x43cddd49`); niveles (`SetParamSetRecLevel` `0x43c26df4`, `SetParamSetRecMode` `0x43c26e91`, `15AbbRecLevelCtrl` `0x43cdddf3`, `RecLevel SetRecLevel` `0x43929fa4`); WNR y cancelación de voz (`WindStage:%d, MagDataRsv:%d` `0x43cddea7`, `MAGIC SetNwnr`, `New WNR ON/OFF`, `PremiumCloserVoice`, `MyvoiceCanceling`, `iVoice` `0x43cddeec`–`0x43cddf9a`); códecs `XAVCS_LPCM` `0x43c6909d`, `MP4_LPCM` `0x43c690c8`, `AAC` `0x43c690f1`; diagnóstico (`targetAudioFormat` `0x43c5c68e`, `audioChannelNum` `0x43c5c6b1`, `audioMuteRec` `0x43c5ca62`); enlace con vídeo (`ProcBuffMgrWrAudioPin` `0x43c28d29`, `AVBB_SCN_START/STOP_AUDIO`); backup de sonido (`9AudioIpIf` `0x43cdd82e`, `Sa SaChangeBackup` `0x43cddfbc`). **A7S (fw3.20) tiene códec externo** (`15AbbExtCodecCtrl` `0x43cd582e`, `ConvChSsau2AudioIpCh` `0x43c2f48a`) que la A6000 (fw3.21) **no tiene**; el resto del audio es prácticamente idéntico (235 vs 237 cadenas).

**NO VERIFICADO:** frecuencia de muestreo/bits/canales; "reduce voltage" del micrófono; muxer de audio en el contenedor; coeficientes del DSP de WNR; ganancia/calibración del micrófono; semántica de VGS/PR/MF/CONS/BANDI.

**Sin efecto en la línea SilentShutter:** fin electrónico NO VERIFICADO; **S51 A=NO/B=NO/C=NO** se mantiene.

[Conclusiones](../docs/capture/s69-audio-subsystem.md) · [informe](../analysis/s69_audio/audio_subsystem.md). Siguiente: muestreo/canales reales, muxer de audio en el contenedor de vídeo, semántica de las configs VGS/PR/MF/CONS/BANDI.

## S66 — montura de lente E-mount (línea general; sin relación con SilentShutter) (20-10-2026)

**VERIFICADO (31 tests, `tests/test_s66_lens_mount.py`):** el `av-cam.bin` de A6000 contiene un subsistema de montura de lente completo: código `0x436dfe6c`–`0x436e9ea4`, 646 logs en `0x43c95659`–`0x43c9a900`, ficheros internos `Mount_Controller.cpp`/`Mount_DividedInfo.cpp`. Bus cuerpo↔lente **UART** con handshake **CS/DATA** por GPIO (`gpio_get` `0x43b5e2bc`); **trama**: cabecera `0xF0`, longitud `size+8` LE, commtype `&7` en `+3`, **ID de comando en `+5`** (`0x07` ATTACH_INFO1, `0x0A` CS_CREDIT, `0x15` UPDATE_DATA, `0x16` LENS_SLEEP, `0x2B` ALPHA_LENS_INFO), checksum **u16 LE** (suma de `buf+1` durante `len-4`) y footer `0x55`; validación `HEADER_NG`→`FOOTER_NG`→`CHECKSUM_NG`→`DATASIZE_NG`→`COMMTYPE_NG`. Tipo de lente = 2 bits (`campo & 3`): 1 → **4.8 V** (4096 mV), 2 → no registrada, resto → desconocido (error `0xFF`; válido `0x0A`). Ciclo de vida completo en los 63 logs de la tarea `0x436e5e3c` (LENS_WEAR → UART_HZ → ATTACH_INFO1..4 → STARTUP_INFO → CS_CREDIT → WAKE_UP → POWEROFF → DETACH_1/2/COMP → LOGIC_ON/OFF → STANDBY). **FW de la lente** por el mismo bus con CAIF/C3P (emisor `0x436fe070`: `LUPDT_INFO`/`LUPDT_DATA`; capa CAIF `0x436ba2c8`) y **segundo bus al DSP de la lente** `[LENS_PDR]`/BonoboDSP (`0x437089d4`, `0x43708a88`, `0x43708cc4`, MMIO `0xf292d000`). 18 ficheros `/lens/VX91xx_lensfile.bin` (cabecera `LF` de 16 B: `u16@2=0x10`, `u32@4=filesize−0x10`, `u16@12=lens_id`; secciones `ED`/`CS`/`LC`; tabla de nombres en `0x43C22BF2`, 18 slots × `0x42`; parser en `0x43907c7c`) cargados por un servicio **dentro de `av-cam.bin`** (`0x43904fb0` → `0x43b2a7e2` → lookup `0x43907bc4` sobre la tabla `0x43C22BF2` → parser `0x43907c7c`), al que `Camera::Lens::ODL::Load` (`0x43721b9c`) los pide con `AsyncSend`/`AsyncRecieve` («lensfile» solo aparece en `av-cam.bin` en toda la partición `dev`); ficheros A6000 idénticos byte a byte a los de A6300; la A7S 3.20 no tiene este subsistema. Sombreado por lente: 11 `ss_LensMountShdValue[]` + 32 `us_LensMountShdGain[]`; perfil por tabla `tbb` de **69 modos de captura → 14 ShdMode** (`0x438ef418`); bloque SHD **idéntico** A6000/A7S (217 logs cada uno, solo cambia el prefijo `[CAMERA_MAIN_YC]:`). fw3.21 (A6000) **añade** 4.8 V, LENS_WEAR, DETACH/attach, ALPHA_LENS_INFO, CS_CREDIT, CHG FREQ y handshake `[HS]` frente a la fw3.20 (A7S), que conserva el núcleo y la ruta de FW-update.

**NO VERIFICADO:** pines físicos de CS/DATA y de la alimentación 4.8 V; unidades de `UART_HZ 750/1500`; nombre de cada ID de comando (la tabla de descriptores se registra en runtime); identidad del servicio que abre los ficheros de lente.

**Sin efecto en la línea SilentShutter:** fin electrónico NO VERIFICADO; **S51 A=NO/B=NO/C=NO** se mantiene.

[Conclusiones](../docs/capture/s66-lens-mount.md) · [montura](../analysis/s66/lens_power_attach.md) · [sombreado](../analysis/s66/lens_shading.md) · [clase/ODL](../analysis/s66/lens_class_and_jobs.md). Siguiente: pines GPIO del bus de lente (backup BK4 o esquema), framing/IDs de comando restantes, servicio que carga `/lens/VX91xx_lensfile.bin`.

## S61 — origen de parámetros IMX210 y flujo de mensajes (20-10-2026)

**A6000 (Claude, 22 tests):** TBH corregido (base `0x43806a08`; script/test de Sol actualizados). Bloque `obj+0xe20`: **A** (`0x437ab474`) escribe solo si `bit6(G[0xD])==0` con `G=0x43e964a4` (GOT+0x21a0; **no** el objeto de 0xF20 B: corrige S60) 6×`(G[0x168],G[0x16A])`; **B** (`0x43aecbec`) solo si `[[p]+0x3a]==1` (stage: 0 en `0x437a9d30`, `src+0xb4` en `0x437aa65c`, borrado si `G[0xD]` bit6). B ← `obj8=obj+0x2cc` ← P0 `0x43861ed0` (←`obj+0x2be..0x2d0`, origen NO localizado); 6.º par ← tabla BK4 `0x300AB` (idéntica en 5 `CX77500`: 18×`(0x2EA0,0x6028)`). Pares = ventanas lo/hi ±0x400 (H «tiempos» debilitada). Petición 9 ← `0x43b00ed8` ← **`HS_Main` `0x4378fef4`**; publicación ← **`VD_Pre` `0x43792a0c`**; petición 3 sin emisor; `0x8003030f`≈alias de `0x3030f`. Estados ALCANZABLES: 0 (un PERMITIDO). Fin electrónico **NO VERIFICADO**; **S51 A=NO/B=NO/C=NO.**

[Conclusiones](../docs/capture/s61-conclusions.md) · [parámetros](../docs/capture/s61-imx210-parameter-origin.md) · [mensajes](../docs/capture/s61-message-flow.md) · [matriz](../analysis/s61-evidence-matrix.json). Siguiente: escritores de `obj+0x2be..`/`G+0x168`/`G[0xD]`, leer `HS_Main` entero (¿fin de exposición?), sembrar Thumb en los 5 puntos.

## S60 — emisor de mensajes IMX210 y receptores A7S (20-10-2026)

**A6000 (Sol 6 tests + Claude):** `0x438069f0` = despachador de la tarea de mensajes `0x43806e38` (recv `0x3030f`); casos 4/10 son respuestas a 3/9 (`0x43b00fe6`/`0x43b00f62` → `0x43806400` → `0x8003030f`). Corrección: TBH base `0x43806a08` (casos → `0x43806c28`/`0x43806d06`). Los 24 B `+0xdd0` = `obj+0xe20..e37`: 6 pares u16 escritos por `0x437ab510` (A) y `0x43aecbfa` (B) vía accesor `0x43ae8504`; semántica de tiempo HIPÓTESIS. **A7S (Claude, 12 tests):** `0x1000/0x1001` = registros de traza (API `0x438f6864`, 381 llamadores) a la cola `0x8f013a`, no bloqueantes, eco de SetExposure/SetRead; Silent no los emite; consumidor no localizado. `0x439b3918`=memcpy ARM, `0x438f7114`=printf de trazas. **GPT:** auditoría NO obtenida (límite de uso hasta 17:56). Fin electrónico **NO VERIFICADO**; **S51 A=NO/B=NO/C=NO.**

[Conclusiones](../docs/capture/s60-conclusions.md) · [cruzada](../docs/capture/s60-cross-validation.md) · [matriz](../analysis/s60-evidence-matrix.json). Siguiente: auditoría GPT pendiente, productores de `obj+0x168/0x16a` y petición caso 3/9; traza pasiva autorizada para física.

## S59 — Claude + GPT-6.1 Sol: bloque IMX210 `+0xDD0` y constructor real A7S (20-10-2026)

**GPT (A6000, 11 tests):** escritor del bloque `0x437876dc()+0xdd0` = `0x43b00da0` (copia 80 B → `obj+0xdb4`; publicada por `0x43b00dd4` si `obj+0x57c≠0`; fuente `obj+0xd64` ← payload en `0x438069f0` casos 4/10). Constructor deja ceros: M no sale de constantes. `clk` NO es el objeto de histogramas (corrige S58-A §5). VdNum=`max(0,raw−0x3000)`. M/Tv/clk alcanzables 0x0B/0x2F: NO VERIFICADO. **Claude (A7S, 9 tests):** constructor real `C_Imager` = `0x436f3fc0`; con él las mismas 100 escrituras que S58, pero base P2S real `0xfc088300` y 3 tramas (127/94/26 B): S58-C (`0xf3c00300`, 5 tramas) era artefacto sintético. Mensajes `0x1000/0x1001` = lista blanca de modos `{0x0b,0x35,0x37,0x38}` (no estado sin inicializar; receptor sin localizar). Consumidor de ganancia `0x436f459c`: único llamador `0x436f5b40`. Revisión GPT corrigió C59-5/7/9/10. Fin electrónico IMX210 **NO VERIFICADO**; **S51 A=NO/B=NO/C=NO.**

[Conclusiones](../docs/capture/s59-conclusions.md) · [cruzada](../docs/capture/s59-cross-validation.md) · [matriz](../analysis/s59-evidence-matrix.json). Siguiente: emisor del payload de `0x438069f0` (origen real de M/Tv/clk) y receptores de `0x1000/0x1001` (Thumb sembrada); física: traza pasiva autorizada.

## S58 — productores AE y configuración A7S efectiva (Claude→Codex, 20-10-2026)

**Hito offline cerrado con cobertura delimitada:** productores `0x4383d4d0` y `0x4383c9dc` comprobados en Unicorn (600/600 y 300/300 en campañas); falta origen Tv/M/clk real. Productor/validador host NO son idénticos para todo VdNum/svr. **CORRECCIÓN de S57:** SetExposure A7S=`0x436f4168`, SetRead=`0x436f4a94`; matriz IMX235=69 filas de 0x14 B con selección indirecta de 15 columnas. Diferencias 0x4c→0x4e=14, 0x4d→0x4f=11. Cadena de cuatro métodos y P2S ejecutada para seis modos, objeto sintético y servicios stub; no es captura integral. Son 100 escrituras (99 DEV81 + 1 DEV83), no 99 totales. Umbral 0x1000 pertenece a ganancia; consumidor `0x436f459c` pone/borra bit4 de 0x81:0x5f, también en foto. **S51 A=NO/B=NO/C=NO.** No se demuestra fin electrónico del IMX210.

[Conclusiones y reproducción](../docs/capture/s58-conclusions.md) · [matriz](../analysis/s58-evidence-matrix.json). Siguiente: recuperar escritor del bloque `0x437876dc()+0xdd0` leído por `0x437aa65c`, con valores M/Tv/clk alcanzables; para semántica física, datasheet o traza pasiva autorizada. No repetir comparación de matriz S57 ni atribuir el umbral a exposición.

## S57 — antecedente; A7S corregida por S58 (Claude, 20-10-2026)

**VERIFICADO (`tests/test_s57_imx210_exposure.py` 34/34, Unicorn + Capstone + REA):** ID1 (dir 1) = **registro combinado**: SetMode carga bits 0/2 desde la matriz (A `0x4401ca2c`; B `0x4401c734` es copia de A en cada Execute), SetExposure fija bits 2,7,4,6 según ShutMode, `0x436d7c08` el bit 3 (SSB), `0x436d7cf0` borra 2,7,4 solo en la ruta de ajuste (`+0x279`, AdjustCmd 0x91). **SSB** se pide siempre tras SetExposure y antes de `Execute(1)` (5 productores; ausente en `Execute(0)` y en `ExposureTimerEnd!`); A7S lo genera dentro de SetExposure si `arg+2>0x1000`. **svd/shd/spl:** mapeo exacto (svd 12 b → ID3/ID4[3:0]; shd 14 b → ID5/ID6[5:0]; spl 12 b → ID7/ID8[3:0]; 400/400); `cap+0x650`=svd cuenta pasos del host (`cap+0x4b9c`) y `0x4381106c` valida `svd=n·svr_num−1`; productor AE (banco `0x43eb35d0`) NO localizado. ShutMode real en captura: solo 0 y 1. **IMX235 Silent** `0x4e/0x4f` = variantes mínimas de `0x4c/0x4d` (1–4 registros; dir `0x000C`) y 33–35/35 distintos de `0x0b`; sin comando de «terminar integración». **XPI** = CN0400 pin 6 → sensor F6 (también A7S), 0 cadenas `SHT_RST`. **P2S SyncMode** se escribe en `0xfc088800`; solo modo 2 usa banderas OSAL y disparo 1,0,1.
Fin electrónico de integración a resolución completa: **NO VERIFICADO** (ningún registro se reescribe al terminar). **S51 se mantiene.** Próximo: `trace_native_values` sobre el pipeline AE (`0x43844e80/0x4384b268/0x4385b234`) o traza pasiva CIS0+XPI+VD.
[Conclusiones](../docs/capture/s57-conclusions.md) · [Matriz](../analysis/s57-evidence-matrix.json). REA con `GHIDRA_MAXMEM=6G`, sesión cerrada.

## S56 — transporte de registros IMX210 (Claude, 20-10-2026)

**VERIFICADO (`tests/test_s56_imx210_transport.py` 26/26, emulación Unicorn del código real):** `SetExposure` solo escribe registros sombra; `Execute` (vtable+0x38) los envía por **P2S(DFE0)** (`0xfc088300`): los «IDs» (119 punteros `0x43fe995c`, mapa `0..0x155`, ID1 duplicado) son **direcciones de 16 bit**; trama `81|len|81|AH AL|datos`, 119 registros → 2 transmisiones, ida y vuelta exacta. `svd/shd/spl` = IDs 3–8 (+0x144–0x149); `ShutMode` 0–4 → ID1 = 40/C4/94/D4/C0 (solo el 2 carga 0x100/0x101). Pulso SSB = ID1 bit3 enviado 2 veces. CISIF = receptor (no bus de configuración). Cadena sin GPIO/P4C. A7S: mismo P2S, registros de 5 B con byte de dispositivo, sin ShutMode 2. SENS_B: sin consumidor (clústeres 0xf2a1/0xf2403 parecen reloj/ADC).
Fin electrónico de integración a resolución completa: **NO VERIFICADO**. **S51 se mantiene.** Próximo: traza pasiva CIS0+XPI+VD (decodificable) o rastrear origen de `0x43eb35d0`.
[Conclusiones](../docs/capture/s56-conclusions.md) · [Matriz](../analysis/s56-evidence-matrix.json). REA con `GHIDRA_MAXMEM=6G`, sesión cerrada.

## S55 — origen de los pares GPIO (base de backup BK4), A7S vs A6000 (Claude, 20-10-2026)

**VERIFICADO (`tests/test_s55_bionz_sync.py` 16/16):** los pares (canal, bit) de la tarea CA **no** vienen de código externo: slot de servicio `+0x2e0` = `Backup_read_4Byte` (liro.ko) y los valores están en
`0110_backup/*/CX77500_*.bin` (A6000; A7S `CX78500_*`), formato BK4 reconstruido de `backup.ko`. El escritor de `0x43e77298…0x43e772d4` es **`0x436bcef4`** (A7S `0x436dc054`; S54 no lo vio: store vía GOT).
Lectores = (3,17),(10,3),(0,12),(0,7),(5,14), salidas (7,15),(7,13): handshake SIO; banco 0 = `GPIO_S_n` (nfc.ko + esquema; (0,7)=CA_RELEASE_LOCK). Estructura **idéntica en A7S** (14 funciones 1:1, mismos IDs/valores;
único `set` extra de A7S = no-op). Ningún par con bit 9 fuera del banco 0 → `GPIO_9` sin lector GPIO (INFERENCIA); `SENS_B` sin rastro (NO VERIFICADO). `ExposureEndNotify`/`ExpStartComp` no leen GPIO.
IMX210 sin avance. H55-1 VERIFICADO, H55-2/4 descartadas en lo recuperado, H55-3/5/6/7 NO VERIFICADO. **S51 se mantiene.**
Próximo: traza pasiva P4C/VD/CIS0 autorizada; estático: bloque SENS_B (escritores `0xf2a1…`), IDs dinámicos de `0x43716dd0`.
[Conclusiones](../docs/capture/s55-conclusions.md) · [Matriz](../analysis/s55-evidence-matrix.json). REA: `analysis/rea-independent/bin/session_daemon.py` con `GHIDRA_MAXMEM=6G`, 1 sesión cerrada.

## S54 — P4C, tipo de mecanismo 0 y BIONZ (Claude, 20-10-2026)

**VERIFICADO (`tests/test_s54_p4c.py` 21/21):** `CA_1ST_CURTAIN_START` (P4C) llega a BIONZ por **`SENS_B` (AA13) y `GPIO_9` (AD21)**, igual en A7S (el esquema A7S sí está en
`docs/references/`: corrige «pines A7S inferidos» de S53). Darwin solo escribe **P4C←0** (9 sitios por ROM, nunca ←1; `0x51f2` conserva b12), también en la rama sin mecanismo;
en A7S Silent la escritura P4C se conserva. **Tipo 0 de A6000 ≡ rama Silent A7S** en exposición/diferidos/ADC (diff llamada a llamada), pero **no** en reposición (A7S Silent actúa
con `no_silent=1`; tipo 0 nunca) ni en lo previo a Darwin. Tipo = `[0x20000050+ch]` validado por `[0x200002c0+ch]` (manejador 33 de `0x2a1a0`); escritor NO localizado.
BIONZ: primitivas GPIO `0x43b5e2bc/22e/29a` (base `0xf2910000`); lectores de la tarea CA usan variables de pin sin inicializar en la imagen → **consumidor de P4C NO localizado**.
IMX210 sin avance. H54-1 INFERENCIA, H54-2 PARCIAL, H54-3/4/7 NO VERIFICADO, H54-5 PARCIAL reforzada, H54-8 INFERENCIA fuerte. **S51 se mantiene.**
Próximo: `av-cam` A7S (barrido `gpio_get`) + inicializador de pines; traza pasiva de P4C/`GPIO_9` autorizada.
[Conclusiones](../docs/capture/s54-conclusions.md) · [Matriz](../analysis/s54-evidence-matrix.json). SHA ROM A6000/A7S y `av-cam.bin` OK.

## S53 — parser CAIF de Darwin A7S vs A6000 (Claude, 19-10-2026)

**VERIFICADO (bytes, `tests/test_s53_darwin_caif.py` 10/10):** el paquete CAIF ev1 (22 B) llega a Darwin (FM3, base `0x4200`) por
MFS5 (P36–P38 = `MSS_*_DWN` ↔ IC6000 BIONZ X) como mensaje mss-async **ID `0x0c`** (código `03 01`, 22 B; identidad con op `0x10300`:
INFERENCIA fuerte). **Parser:** A7S `0x18396`, A6000 `0x17f8c`, idénticos salvo que A7S guarda `pkt[+0x12]&0x20` en `S+0xd0.b5`
(`0x18460`) → predicado `no_silent` `0x19a86`/`0x216c2` que **impide escribir P4D/P4E** (`1ST/2ND_CURTAIN_MG`; `0x2172c`, `0x21786`,
`0x217b2…`, diferidos `0x214dc/0x214fa`) y omite el seguimiento ADC. A6300 tiene la misma rama. **A6000 descarta el bit** y sus
escritores (`0x20cb2`, `0x20d00`, `0x20d26…`) no tienen argumento Silent. Modo 2 de `+0x0d`: sin consumidor (PARCIAL).
**Escenario B:** falta lógica de firmware en Darwin A6000 (además de LIRO e IMX210). **S51 se mantiene.** Pines A7S por inferencia.
[Conclusiones](../docs/capture/s53-conclusions.md) · [Matriz](../analysis/s53-evidence-matrix.json). SHA 3/3 ROM Darwin OK.

## S52 — clase 0, `+0x748` y cortinas (Claude+Codex, 19-10-2026)

**VERIFICADO:** la A7S **no suprime** el control de cortinas en LIRO. Envía igual el paquete CAIF ev1 al MCU de obturador, pero con
Silent **marcado** (`+0x12` bit `0x20`, `+0xd` modo 2; `0x4386329a/0x43863258`) y byte de clase = 3. Además deja de **esperar** las
respuestas del mecanismo: CAIF 3 y bandera `0x800000` (`0x438b1cba`, `0x438b726c`), según `captura+0x748`. Esa bandera es la misma que la
A6000 tiene en `+0x740`: tiene lectores pero ningún escritor (latente). La clase 0 llega a `param+9`: `0x43864c74→0x43f04c8c→R+0x69→cap+0x651→0x436f2938→vtable+0x28`.
Identidad de R resuelta por el coordinador (`analysis/s52_coordinator_check.py`). La clase sola no omite CAIF/MMIO (solo el mensaje `0x22`).
**INFERENCIA fuerte:** la decisión física la toma el MCU Darwin (parser CAIF no localizado). P5 NO VERIFICADO; **S51 se mantiene**.
Corrección: IMX235 `cfg2+4|=8` en todos los ShutMode (no solo 0). Próximo: parser CAIF en `darwin_core.bin` A7S vs A6000 (bit `0x20`).
[Conclusiones](../docs/capture/s52-parallel-conclusions.md) · [Matriz](../analysis/s52-evidence-matrix.json). SHA 8/8 + manifiestos OK.

## A7S Silent reconstruido (estático) — 19-10-2026

**VERIFICADO (bytes+LLVM+REA, test `work/claude/tests/test_a7s_silent_facts.py`):** en A7S 3.20, `0x40e3`→estado `+0x250`→conversor
`0x4379ec04` (tipo {0,2})→`captura+0x78c`→ (a) selector `0x43826d58`: tipo 2 ⇒ drive_mode `0x4e/0x4f` (IMX235, columnas propias,
45/69 campos distintos de `0x0b`); (b) política `0x438649bc`: tipo 2 ⇒ clase de obturación 0. A6000: receptor `+0x238` existe, pero su
selector `0x437f7f98` y su política `0x43842158` son el mismo código **sin** ramas Silent, y el IMX210 no tiene modos `0x4e/0x4f`.
H1 mayormente refutada; S51 (no parchear) se mantiene. Pendiente: clase 0 → cortinas. [Informe](../docs/capture/a7s-silent-reconstruction.md).

## Referencia comparativa — 19-10-2026

**Decisión del usuario:** A7S 3.20 sustituye a A6300 2.01 como referencia (A6300 queda histórica; supera la instrucción del 16-10).
Manuales Level 3: mismo CXD90027GF con 12 pares sub-LVDS; sensores IMX235 (A7S) / IMX210 (A6000). [Comparación](../docs/references/a7s-vs-a6000-service-manuals.md). Firmware A7S en `firmware/extracted/a7s-fw320`, sin analizar.

## Hito REA independiente (Línea B) — 19-10-2026

**VERIFICADO:** REA 6.5.0+Ghidra 12.1.4 abre `av-cam.bin` (raw ARM, base 0x43541000)
con `REA_GHIDRA_STARTUP_TIMEOUT_MS=900000`: análisis completo en ~459–486 s (por defecto
330 s no basta), 42006 procedimientos, pico RSS 2,3 GB. Frente a 464 entradas históricas:
363 exactas, 9 absorbidas, 92 ausentes (las Thumb sembradas a mano, p. ej. 0x43789cc0).
234/234 listados idénticos a Línea A; LLVM decodifica en las 38708 direcciones.
`libmprctrl.so`: 8 funciones coinciden en bytes, nº de instrucciones y offsets (análisis ~22 s).
**PARCIAL:** el decompilador B no pliega literales a `_DAT_f3c3xxxx` (Línea A sí, 19/234).
Setters 0x436c6288/6294 escriben `0xf3120000+0x48/+0x4c`; semántica NO_VERIFICADO.
**Sin evidencia nueva** de exposición electrónica independiente de cortinas.
Límite: la sesión REA no persiste (rea#1048 abierta); Línea A sigue siendo la referencia de verificación (Thumb sembradas); la exploración nueva va primero por REA: ver `docs/STATE.md` § Política de ingeniería inversa.
Línea A, `silent-liro.*`, firmware y S1–S48 intactos (SHA idénticos).
[Informe](../docs/capture/rea-independent-milestone.md). Próximo exacto S48 sin cambios.

## S51 — decisión vigente (19-10-2026)

**A=NO, B=NO, C=NO.** No hay una ruta electrónica demostrada ni un parche justificable, y tampoco una imposibilidad demostrada.
T1 (VERIFICADO): el modo `0..7` (getter `0x43842404`→`0x43eedecc`) solo llega al registro `0x4383fb6c` (+0x6d/+0x6e/+0x70,
serializado por `0x438e2b98`) y a eventos; `ModeRsvParam` = `0x43795a60(cap+0x4d0 drive_mode, +0x4d4, +0x4d5)`, con el drive_mode
fijado en `0x437f7ff4` sin depender del modo. C_Imager: `SetMode 0x436d62e4`, `SetExposure 0x436d6320`, `SetRead 0x436d6398`.
T3 (Codex): no hay guarda configurable sobre el cierre de la 2ª cortina. T2: ID1/100/101 sin dirección/semántica de sensor.
**Decisión: detener el parche.** Retomar solo con el datasheet del IMX210 o con una traza pasiva autorizada de la interfaz serie
del sensor. [Decisión](../docs/capture/s51-decision.md) · [Codex](../docs/capture/s51-codex-t2-t3.md). SHA 1490/1490 OK.

## S50 — estado anterior (19-10-2026)

**VERIFICADO (investigación paralela Claude+Codex):** `0xb6 A_LINEAR_ELEC_SHUT` sin fila de callback ni caso `C+0x60` → inerte. `0x4382dd78`
construye B desde C (`C+0x94/95→B+0x36/37`); `0x43842158` usa `C+0x94/95` como override del modo `0..7` (`0x43eefb1c+0x60`) que solo se exporta
a registros de estado. **CORRECCIÓN S49:** `1/2/3/6` = cantidad de callbacks, no clases. Bypass CA `+74f` no es foto silenciosa.
**Pregunta final: NO_VERIFICADO** (ni demostrada ni imposibilidad). Falta consumidor físico del modo y significado eléctrico ID1/100/101.
[Conjunto](../docs/capture/s50-parallel-conclusions.md) · [Claude](../docs/capture/s50-claude-electronic-config.md) · [Codex](../docs/capture/s50-codex-exposure-curtains.md). SHA 1490/1490 OK.

## S49 — estado anterior (19-10-2026)

**VERIFICADO:** `0x301d7` = id OSAL de la cola de comandos de ajuste/servicio; clave `0xce` = `S_IMAGER_CURTAINMODE`
(payload `(habilitar, valor)`). Tabla de servicios de `av-cam` copiada por `liro.ko` (`tsk_entry`, `memcpy(hdr[0x14]+0x24)`):
slots `0x4354129c/a0/b4` = `osal_unreg_msg_queue_cb/osal_reg_sync_msg_queue_cb/osal_dynamic_id`. Productor: puente USB
`libsencore` (`TransactionStart 0x25fc8`) y `adjstctl`/`libtestcmd`; `libObj` solo claves 0/1/0x67. **NO_VERIFICADO:** emisor
en uso normal y significado del valor. Informe: [S49](../docs/capture/s49-capture-config-producer.md). Próximo S50:
consumidores de `C+0x94/+0x95`, `C+0x60`, `0xb6`.

## S48 — estado anterior (19-10-2026)

**VERIFICADO:** servicios `+0x1e8/+0x1ec/+0x200` de la tabla `0x435410b4` están a 0 en el blob y solo se leen
(wrappers `0x43561298/0x435612b4/0x43561324`): el proveedor y el emisor del paquete `0x301d7` están **fuera de
`av-cam.bin`**. Función de alta `0x43789fdc` (crea manejador `0x301d7`). **NO_VERIFICADO:** emisor/productor de
`+0x1c/+0x1e`. Informe: [S48](../docs/capture/s48-service-table-provider.md). Próximo: buscar el emisor en
userland (`libObj.so` etc., hits `d7 01 03 00`) o cerrar la línea como frontera externa.

## S47 — estado anterior (19-10-2026)

**VERIFICADO:** entrada `0x43789cc0`, registrada con ID `0x301d7`;
fila clave `0xce` en `0x43ff29b8` → handler `0x43789708`.
Copia solicitud `0x140`B a `0x43e95420`; payload en `0x43e9543c`
→ argumento4 de `0x437da100` → `0x43ed4620` → callback `0x437dad78`.
`0x43ed44dc` es otra solicitud sintética, no el buffer recibido.
Callback ANTES de copia C: despacho `0x43792f9c` domina copia `0x43794096`;
`0x43ae90ce` copia `0x1a4` desde `0x43e9d3b4` a `0x43e9b380`,
incluyendo `+0x94/+0x95`. S46 no queda refutada por orden.
**PARCIAL:** productor original de los dos u16 anterior a `0x43789cc0`;
valor2 y propagación B/G. Servicio de registro `+0x1ec`, slot `0x435412a0=0`.
**Próximo exacto S48:** contrato/proveedor de ese registro y productor del
paquete ID `0x301d7`, clave `0xce`, stores `+0x1c/+0x1e`.
No repetir orden ni solicitud sintética como única fuente. Punto opcional VD
aplazado; clases1–3 físicas y VD/cortinas sin cierre. Hito S46–S52 abierto.
SHA/manifiestos intactos; sin git.
[Informe S47](../docs/capture/s47-payload-producer-and-order.md).

## S46 — antecedente (18-10-2026)

**VERIFICADO:** owner `0x43e15f18` → `0x436c6f3c` → `0x436c7950`
→ setter `0x43acee66` inicializa `0x43e16d2c=0xf3120000`;
destino de S45 base+220=`0xf3120220`, escritura condicional.
C fuente `0x43e9d3b4` construido con offsets partidos `1e40+2c`.
Callback `0x437dad78`, fila `0x43ff8adc`, clave `0xce`, escribe
C+94/+95 desde payload4B: primer u16!=0 → (1,low8(segundo u16));
primer u16=0 → (0,0). Scratch `0x43f7bbf4`, distinto de snapshot `0x43ef2474`.
**PARCIAL:** propagación condicional de (1,2) por copia a C/B/G;
productor del payload y orden completo pendientes. P=padre+1454 sin alias C.
Integración/cortinas y semántica eléctrica `0xf3120220` NO_VERIFICADO.
**Próximo exacto S47:** argumento4 de `0x437da100` hasta payload
`0x43ed4620`; productor de los dos u16 de clave `0xce` y orden frente
a `0x43792f9c/0x4379409e`; después semántica del controlador VD.
[Informe S46](../docs/capture/s46-vd-base-and-context-identity.md).

## S45 — antecedente (18-10-2026)

**VERIFICADO:** contexto437b5b14=43eaadd8, copia0xb0 desde43e993a4;
VD_Pre reconstruye este último desde raíz copiada43e99514.
C=contexto[14]=43e9b380, copia1a4 desde43e9d3b4. AliasP/C pendiente.
GetterIMX210+3a0=43ad9202, virtual+74;43ad90b6→438c828c usa el retorno,
calcula captura+570→43795dec→436c74c8→43ad2bd6 escribe base+220.
**PARCIAL:** controlador43e16d28, base=*(43e16d2c) sin escritor recuperado;
MMIO físico de esa escritura e integración/cortinas NO_VERIFICADO.
**Próximo exacto:** escritores43e9d3b4+94/+95/copiaP→C y escritor43e16d2c
desde owner43e15f18. No repetir getter+74 ni consumidor/virtual+a8.
Termina serie explícitaS40–S45; hito abiertoS46+, sin agotamiento/Línea E.
SHA/.gpr/.rep intactos; sin .git/commit.
[Informe S45](../docs/capture/s45-context-identity-and-physical-closure.md).

## S44 — antecedente (18-10-2026)

**VERIFICADO:** consumidor436d75f8 lee119 paresIDu16/byte+2 de43fe995c;
436d839c→436d79b0→75f8→backend+298→436d5ed0 carga MMIO,
436d5f60 pulsa B+8. Canales{1,2,0}; bancos43bc14e8.
Virtual+a8=436d65b8 compara nibble alto del registroID0 entre13 índices;
ignora flags y devuelve1 si cambia. No transporte dentro del comparador.
**PARCIAL:**4385cf2c produceP+95=2; P=raíz+2bc, alias con
C=*(contexto+50) no probado; snapshot43ef2474 candidato, no identidad.
**Próximo exacto:**origen del contexto de437b5b14 y campo+50 hastaP/C;
después lectoresIMX210+3a0 y semántica físicaID0/integración/VD/cortinas.
No repetir consumidor/virtual+a8; no agotamiento estático ni Línea E.
OSALbit31 y AF permanecen cerrados. SHA/.gpr/.rep intactos; sin .git/commit.
[Informe S44](../docs/capture/s44-register-consumer-mode-table.md).

## S43 — antecedente (18-10-2026)

**VERIFICADO:** PIC4401eee4; slots resueltos a estructuras4401c6xx–4401caxx,
ID u16 + dato byte+2, b3, sin MMIO directo/vtables.43ad9a40/43ad99d4
guardan estado en objeto+fc (la variable ya no representa base PIC).
**RECHAZO** códigos de bloqueo AF: cadenas SetSequenceMode img/fratechg/clamp,
ImgMode/IMAGE_FRAME_RATE/SYNC_RAW_OUTPUT_SIZE; virtual+94 consulta tabla de
modos del backend. **ACEPTO**4380e020/43902718 como log/trace.
**PARCIAL:** transporte de staging, lector IMX210+3a0 y escritor C+94/+95.
**Próximo exacto:** consumidores de registros por slots PIC y virtual+a8 desde
436d92e0; virtual+10 436d8ff4 es getter de0x70B, sin transporte. Después
C=*(contexto+50) en4382dd78→B43eae270→G43ea6ad4→43842158.
No cierre físico, agotamiento global, Línea E ni reapertura OSAL bit31.
SHA/proyecto intactos; sin .git, sin commit.
[Informe S43](../docs/capture/s43-exposure-mmio-and-lock-codes.md).

## S42 — antecedente (18-10-2026)

**VERIFICADO:** corrección de nomenclatura S41:436d6320 es wrapper,
436d634a llama virtual+28; vtable43fcc090+28=436d6f6d. Constructor436d72e8
y factoría436d6504 publican objeto43e7f4a8 en contenedor43e7f858.
Clase2: cargas BYTE en436d7136/7142 desde parámetro+08/+14,
buffers4401c6d2/4401c7ce, cálculo→objeto+3a0. Cortinas/VD NO_VERIFICADO.
**PARCIAL:**4382dd78 copia C=*(contexto+50), C+94/+95 a B43eae270+36/+37;
4384cb58→437b0480 copia c14B a G43ea6ad4;438412d0 pasa G al selector.
Escritor original de valor2 pendiente. No confundir stores43845b68/70:
son otro objeto. R43e9b548+5cc=43e9bb14=ImgState43e9baec+28;
lectores438553dc/4385558a pertenecen a43e18c60, no R.
Cadena de bloque0x44=68B hasta4378e334/43795a60 contrastada, pero sin
dependencia recuperada desde R+5cc. Descriptores3023: parser sin tipar.
**Próximo exacto:** escritores C+94/+95 hasta valor2; lectores IMX210+3a0
y buffers hasta transporte/cortinas; alias ImgState+28 hacia43eea2e4;
consumidor indirecto de getters3023. No reabrir OSAL bit31 sin evidencia nueva.
No agotamiento estático: Línea E no activada; A6300 existe, sin analizarlo.
SHA/proyecto intactos; sin .git, sin commit.
[Informe S42](../docs/capture/s42-exposure-call-identity.md), `analysis/ghidra/s42-findings.json`.

## S41 — antecedente (18-10-2026)

**PARCIAL:** cola principal30001 y snapshots3030f. Productores internos
4000/4036:43816448/43818c1c/43817e20→4381a138→435aa20c→4356120c.
Conversores:43bc59e0={1,0,5},43bc5a50={1,2,0,3}; nombres de opciones
NO_VERIFICADO. Case1:43b01026 envía objeto+4/564B; case10 largo:
43b00f62 envía objeto+6c0/5e0B, incluyendo copia previa en+6c4.
Destino8003030f frente a receptor3030f: bit31 sin resolver, no cerrar bucle.
R+458 o R+48→0,2,1,4 en VD_Pre; sin enlace demostrado a integración.
**Próximo:** productores de argumento1+36/+37 de43842158 (valor2),
argumentos+8/+14 de clase2 en436d6f6c y sincronía de cortinas;
metadatos3023 y lectores de R+5cc hasta argumentos tipados del sensor.
Slots OSAL en435410b4 cero: frontera de implementación; se activó Línea C
para contrastar selector EFCS separado: banco+41c, diagnóstico+7e y
anulación+36/+37. Clase2 alcanza rama distinta; cierre físico NO_VERIFICADO.
Sin agotamiento A/B universal.
SHA/proyecto intactos.
[Informe S41](../docs/capture/s41-message-origin-imx210.md), `analysis/ghidra/s41-findings.json`.

## S40 — antecedente (18-10-2026)

**PARCIAL:** `context[0]+24/+48/+458` provienen de staging43edf684,
escrito por comandos API4000/4036/3023 (bytes solicitud+0a/+09/+0e),
con ceros condicionales438040e8 y437935ae.43804cdc copia560B a raíz;
43804c82/43804d12→43b00d06 copian snapshot objeto+8. Tabla despacho
43fff30c:220×12B; tabla selección43ca3c21={1,1,0,1}.
API demostrada, menú/FPS/píxel y exposición/read-enable/generación física
NO_VERIFICADO. No agotamiento estático.43804cc8 toma staging;
43806a80/43806d50 toman mensaje+4/+8. **Próximo:** productores originales
de esos mensajes case1/10 de438069f0, después enlace
tipado a selectores IMX210. Proyecto readOnly/noanalysis y firmware intactos.
[Informe S40](../docs/capture/s40-context-origin-imx210.md), `analysis/ghidra/s40-findings.json`.

## Qué existe

- Grafo de conocimiento en `.knowledge-cache/knowledge.sqlite` (regenerable, gitignorado):
  **1189 entidades Function, 1764 relaciones CALLS deduplicadas (2604 fuentes de evidencia
  preservadas en `relation_sources`), 39 relaciones CORRECTS/SUPERSEDES.**
- Fuentes del grafo: dossiers JSON legacy, ~430 exports Ghidra (pseudocódigo decompilado),
  5 evidencias REA. Catalogadas por forma estructural en `knowledge/catalog/JSON-CATALOG.md`
  (2146 JSON, 108 familias; dos familias explícitamente excluidas por falta de identidad
  verificable — ver PROGRESS.md Fase 12.4.A).
- CLI unificada: `scripts/knowledge/search.py` (`exact`/`text`/`tree`/`section`/`graph`/
  `trace`/`claim`/`ask`/`freshness`). Servidor MCP: `scripts/knowledge/mcp_server.py`
  (11 tools, límite global 20000 chars).
- Benchmarks: línea base pre-rediseño en `knowledge/benchmarks/baseline-2026-10-18-pre-12.6.md`
  (NO editar). Benchmark rediseñado con verdad de referencia estructurada en
  `knowledge/benchmarks/report-v2.md` (generar con `scripts/knowledge/benchmark_v2.py`).

## Última fase completada

**S39 (18-10-2026):** av-cam SHA/memoria verificados; silent-liro solo
readOnly/noanalysis, sin mutaciones. Tres llamadores de 43814d24 convergen
en config+0c→43ef71a4→4387a6c4→caché 43e77ccc por unidad, valores
0/1/2/4; cambio invalida/reinicializa APL, sin campo hardware/pitch enlazado.
No confundir índices P con remapeo separado input+38. 43ae8d56 fija
context[2]=root+5a4; campo43e9bb14 tiene cuatro escrituras en VD_Pre,
copia/cero/remapeo según estado. Nombres de píxel y opción/FPS no demostrados.
**PARCIAL**, sin declarar agotamiento estático universal. Próximo: fuentes
context[0]+24/+48/+458 y copias masivas hasta solicitud/tabla tipada.
Incógnita física prioritaria: productor/handle/VD y cierre de integración.
[Informe S39](../docs/capture/s39-image-format-apl.md),
`analysis/ghidra/s39-findings.json`. Se conservan S31–S38 debajo como historial.

**S38 (18-10-2026):** SHA av-cam verificado, silent-liro readOnly/noanalysis;
.gpr/.rep intactos. 85 literales 61003c, 16 sin xrefs: pool compartido,
sin servidor/alta recuperados. Blob ORIL/LIRO, no ELF; readelf -d/-r y nm
fallan. Tabla 435410b4, slot +2e4=0 en archivo.
**FRONTERA ESTATICA AGOTADA** para resolución ELF/valor externo del slot
en este blob; no ausencia universal de receptor. Extents→P/APL y productor
físico YC NO_VERIFICADO. **Próximo paso exacto:** enum de formato S33,
input+38←P+1b4←context[2]+28, conversor 43814d24 y campos APL/stride/tamaño.
[Informe S38](../docs/capture/s38-dmm-osal-static-frontier.md),
`analysis/ghidra/s38-findings.json`. S31–S37 se conservan debajo como historial.

**S37 (18-10-2026):** `libmprctrl.so`, SHA
`514e14116caa1d15d75bd56641dabfe815f620b6208008929c44d8d70386011d`,
define AllocDmmMemory/FreeDmmMemory; proyecto nuevo `libmprctrl.gpr`, copia
0444 y export readOnly. Getters originales son **DmmAccessPLA**: leen
dirección/tamaño en respuesta+0x10/+0x14, sin demostrar dominio físico/lógico
ni valor concreto. AllocDmmMemory devuelve cabecera de paquetes, otro layout.
Cliente OSAL **0x61003c**, payload 0x18: compatible parcialmente con campos
S33, pero no idéntico a envoltura 0x55/0x70 ni prueba del slot av-cam.
PLT libObj 0xdc180 importa exactamente DmmCloseAndFree definido aquí,
con DT_NEEDED directo. **Productor físico YC NO_VERIFICADO.** Próximo:
receptor 0x61003c y proveedor tabla av-cam+0x2e4 hasta escritor de extents,
misma clave/ID Rendezvous y APL. [Informe S37](../docs/capture/s37-libmprctrl-dmm-extents.md),
`analysis/ghidra/s37-findings.json`. S31–S36 se conservan debajo.

**S36 (18-10-2026):** analizada únicamente `libInfraScalarMpr.so`, SHA
`b56b4c6172a60b879ebf405bc64e19e7456d230ff6125a21bbd4469e35c0d2c9`, en
proyecto Ghidra separado, export final readOnly. `AllocDmmMemory(int,ushort*)`
y `FreeDmmMemory(int)` son **UND**, no cuerpos locales. `AllocSharedMemory`
devuelve ID SysV y dirección virtual de `shmat`, usada en copia de datos still;
no demuestra origen YC/DMA ni relación con Rendezvous. Próximo: localizar
definidor de `_ZN9DmmAccess14AllocDmmMemoryEiPt` y
`_ZN9DmmAccess13FreeDmmMemoryEi`; resolver por separado slot av-cam.
[Informe S36](../docs/capture/s36-libinfra-scalar-mpr-memory.md),
`analysis/ghidra/s36-findings.json`. S31–S35 se conservan.

**S35 (18-10-2026), investigación de firmware:** los cuatro objetos DFE son
Ofmt/Ifmt; RTTI, vtables y métodos +8 de sus hijos resueltos. Leen y activan
bit 0 de SGC `0xfc0a1210/1310/1610/1710` (+0x1000 en unidad 1), sin lectura/ack
APL recuperado. Bit `0x00200000` sin causa física identificada; los usos en
enable del controlador son otro dominio. **FRONTERA ESTATICA AGOTADA para
esta vía**, no imposibilidad universal: falta routing/semántica hardware o traza
pasiva correlacionada APL/IRQ/VD/handle en cámara sin flashear. Ciclo físico
NO_VERIFICADO. Próximo: DMM importado `0x43561524`, `tabla+0x2e4`, productor
Rendezvous y lector YC real. [Informe S35](../docs/capture/s35-dfe-objects-static-frontier.md),
`analysis/ghidra/s35-findings.json`; S31–S34 se conservan debajo como historial.

**S34 (18-10-2026), investigación de firmware:** tres BL a `0x43814ea0`
contrastados con el blob; direcciones → MMIO → kick 0/1 síncronos en Image.
Ruta VD_Sequence demostrada; selector permite categoría HS para dos productores,
sin demostrar factibilidad conjunta de cada modo/rama. Sin llamada directa desde
Post/Drive. El evento Drive `0x80` puede preceder Sequence o venir de timer 4:
no demuestra fin DMA. Registrador DFE de cuatro callbacks y cuatro conversiones
de causa resueltos; falta mapear bancos APL a causa/estado/callback y handle/VD.
Kick en `…0500` es +0x100 respecto de bancos `…0400`. Cuadro propio/siguiente
y cierre inicio-exposición/DMA/fin-exposición **NO_VERIFICADO**.
[Informe S34](../docs/capture/s34-apl-dma-vd-interrupts.md),
`analysis/ghidra/s34-findings.json` / `s34-audit.json`; proyecto/binario intactos.

**S33 (18-10-2026), investigación de firmware:** AllocShare completo y sus
26 llamadas YC cerradas estáticamente (12 funciones, 13 parámetros locales
inicializados a cero). `input+0x10` referencia handles de trabajo, varias rutas
AllocRendezvous; helper `0x43814ea0` puede activar `+0xc8` y escribir
`input+0xd4=P+0xbc` en tres productores (también se propaga por copia).
Rama APL seguida hasta palabras de extents y registros MMIO en bancos
`0xf3850400/0xf3950400/0xf3a50400`; el flag secundario es estado de software.
La palabra `handle+4` es clave conservada de la solicitud, no dirección raster
demostrada. Despacho Image dentro de VD_Sequence y publicación alternativa
desde HS_Sequence (`0x43790b68`). Pendientes: proveedor importado DMM
(`tabla+0x2e4`), productor que satisface Rendezvous, pitch/formato y fin DMA físico.
[Informe S33](../docs/capture/s33-yc-rendezvous-producer.md),
`analysis/ghidra/s33-audit.json`. Proyecto y binario sin cambios; sin cámara.

**S32 (18-10-2026), investigación de firmware:** continuó S31 sin ampliar la
arquitectura de conocimiento. Resueltos `0x43ad6034` (despachador), su thunk
`0x43ad6052`, el adaptador `0x43b03a48`, registradores
`0x4379704c`/`0x43797090` y seis destinos de las listas VD. Nueva rama
`0x4379b44c→0x4390366c` prepara referencias DMM compartidas en el bloque YC;
no es únicamente temporización. CORRECCIÓN de S31: «YC out window overflow»
se imprime en `0x4379cb2e`, dentro de `0x4379bb90`; es comparación temporal,
no finalización DMA. Falta el handle fuente efectivo (`input+0x10/+0xd4`),
su mapeo a píxeles/pitch/formato y la tupla del consumidor remoto.
Evidencia estática, sin cámara: [informe S32](../docs/capture/s32-vd-callbacks-sync-ycout.md)
y `analysis/ghidra/s32-findings.json`. El pendiente S31 descrito abajo es histórico
y queda actualizado por S32; la captura física sigue NO_VERIFICADO.

**Fase 12.11** (2026-10-18): tras cerrar la arquitectura del sistema de conocimiento
(instrucción explícita del usuario de no ampliarla más), se retomó la investigación
principal del shutter completamente electrónico.

1. `SetRead` IMX210 (0x436d7e08) decompilada íntegra vía Codex: no lee
   Silent+0x238/+0x280 ni produce buffer YC/DMA (ver `docs/capture/silent-imager-consumers.md`).
2. Corregida línea obsoleta en `CONTEXT.md`: el alta/callback de `0x50004` ya estaba
   cerrado desde S28, no pendiente.
3. Descartado, por ausencia total de cadenas `IMX210`/`exposure`/`SilentShutter`/`EFCS`
   en los 90+ `.ko` del firmware A6000, que el control del sensor viva en un módulo de
   kernel separado — refuerza que todo vive en `av-cam.bin`/librerías de servicio.
4. **Hallazgo S31** (`docs/capture/s31-camera-main-sync-strings.md`): subsistema
   `CAMERA_MAIN_SYNC`/`DFECore` en `av-cam.bin` — motor de temporización VD del sensor
   que ninguna sesión S16–S30 había explorado (todas se centraron en la capa de
   servicio libObj.so/libBizFw.so). Decompiladas 8 funciones clave vía Codex:
   `VD_Pre` (0x43792a0c) →evento 0x40→ `VD_Sequence` (0x4379155c) →evento 0x100→
   `VD_Post` (0x4379210c) →cola→ `VD_Drive` (0x4378f410); variante `EC_VD_Post`
   (0x4378f848) guarda el número de VD procesado en 0x43e992dc, comprobado por
   `int_LM_Send1st_Handler` (0x43792750); `camIntHandler0/1` (0x436cf954/0x436cf780)
   despachan causas de interrupción reales. **VERIFICADO: acceso MMIO real** a
   registros físicos 0xf3c30110–0xf3c3015c vía 0x436ccd9c→0x43ad6006. **PARCIAL:**
   `VD_Sequence→0x43796954→0x4379bb90` (SyncYCout.cpp) es el candidato más cercano
   al productor YC, pero no entrega dirección de píxeles/plano/pitch/fin DMA.
   **Pendiente exacto:** resolver los destinos de las llamadas indirectas vía
   `0x43ad6034` desde las listas de trabajo de `VD_Drive`/`VD_Post`.

**Fase 12.6** (2026-10-18): validación del grafo ampliado + rediseño del benchmark.
Encontrado y corregido un bug real: 840 relaciones CALLS duplicadas (misma función
reanalizada en varias sesiones JSON generaba una relación por archivo en vez de una sola
con procedencia múltiple) — ver `relation_sources` y `_upsert_call_relation` en
`build_graph.py`. Añadida distinción llamada directa vs. vía thunk de Ghidra.

## Bloqueadores reales / pendiente

- **Prueba de integración E2E completada** (2026-10-18, Fase 12.10): relación CALLS real
  con evidencia exacta confirmada (`AsyncProcessor::execute()`→`captureStart()`, callsite
  `0x108144`) y una relación inexistente correctamente NO inventada. Checkpoint de prueba
  escrito por Claude Code recuperado por una sesión nueva de Codex (`get_current_state`,
  sin leer `CONTEXT.md`/`PROGRESS.md`), que además localizó la evidencia original y
  distinguió un hallazgo VERIFICADO de una pregunta NO_VERIFICADO real. Prueba inversa
  (checkpoint de Codex recuperado por Claude Code) también confirmada. Contexto medido:
  recuperación de Claude Code ≈4024 caracteres / ~1006 tokens estimados; sesiones Codex
  completas reportaron 29 247 y 16 805 tokens reales (cifra de sesión, no de una sola
  llamada — no comparable 1:1 con la estimación de Claude Code). Checkpoints de prueba
  eliminados tras verificar. Detalle completo en `PROGRESS.md` Fase 12.10.
- **Codex ya tiene registrado el servidor MCP** (resuelto 2026-10-18, con autorización
  explícita del usuario): `~/.codex/config.toml` ahora define
  `[mcp_servers.sony-a6000-knowledge]` (python3 del `.venv` del proyecto +
  `scripts/knowledge/mcp_server.py`). Respaldo previo en
  `~/.codex/config.toml.bak-20261018T114752`. Detalle completo en `PROGRESS.md` Fase 12.9.
- **El servidor MCP `sony-a6000-knowledge` para Claude Code aparece "Pending approval"**
  en `claude mcp list` dentro de esta sesión no interactiva: requiere que el usuario lo
  apruebe desde una sesión `claude` interactiva. Mientras tanto, la verificación anterior
  usó la función Python real del servidor (misma lógica, mismo archivo) como sustituto.
- **Validación desde sesión interactiva nueva** (no `exec`, ni en Codex ni en Claude Code):
  lo verificado arriba usa `codex exec` (no interactivo) y la función Python directa; el
  descubrimiento en el modo interactivo normal de cada cliente sigue sin confirmación
  externa del usuario.
- Mapeo de lenguaje natural a nodo de `trace` (p. ej. "¿qué llama a 0x50004?") sigue siendo
  manual: hay que ubicar el nodo primero con `search.py exact`.

**Siguiente objetivo (indicado por el usuario):** no ampliar más esta arquitectura salvo
defecto importante; volver a la investigación principal — captura completamente
electrónica en Sony A6000 — reutilizando las evidencias existentes.

## Siguiente acción sugerida

Ver "Próximo paso exacto" al final de `knowledge/PROGRESS.md`.
