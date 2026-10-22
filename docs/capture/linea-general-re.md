# Línea de ingeniería inversa **general** de la cámara (catálogo de hitos)

> Esta línea es **independiente** de la del obturador electrónico (la "Línea B" del
> [README de capture](README.md)). Aquí se cataloga la RE general del firmware y del userland de la
> Sony A6000 (fw3.21), con comparación contra la A7S (fw3.20) cuando procede.
> Todo lo que sigue está **verificado contra bytes**; cada hito tiene su informe en `analysis/` y su
> test en `tests/`.

## 1. Índice de hitos

| hito | tema | hallazgo central | informe | test |
|---|---|---|---|---|
| S66 | montura de lente E-mount | trama del bus UART (`0xF0`/len/ID/checksum/`0x55`), 18 ficheros `/lens/VX91xx_lensfile.bin`, 69 modos → 14 ShdMode | [`analysis/s66/`](../analysis/s66/) · [doc](s66-lens-mount.md) | `tests/test_s66_lens_mount.py` |
| S67 | AF | **cancelado** (el tema lo cubre otro agente, `analysis/s63_af/`) | — | — |
| S68 | batería, energía y carga | **negativo**: no hay modelo NP-FW50 en `av-cam.bin`; sí nivel vía UPM, códigos a MCU y **carga de flash con control PWM** | [`analysis/s68_power/`](../analysis/s68_power/) · [doc](s68-battery-power.md) | `tests/test_s68_power.py` |
| S69 | audio | IP de audio del driver de sensor, micrófono, niveles, WNR; la A7S tiene **códec externo** y la A6000 no | [`analysis/s69_audio/`](../analysis/s69_audio/) · [doc](s69-audio-subsystem.md) | `tests/test_s69_audio.py` |
| S70 | EIS/gyro | tres capas `[CAMERA_IS][AS]`/`[EIS]`/`[DIST]` y traza por lente `/mnt/FILE_IS_%04x.dat` | [`analysis/s70_is/`](../analysis/s70_is/) | `tests/test_s70_is.py` |
| S71 | caras / FC-FRC | **99 ficheros `FC/` idénticos** en A6000 y A7S; puente con el **acelerador Scalar**; 6 detectores en `[TRK]` | [`analysis/s71_frc/`](../analysis/s71_frc/) | `tests/test_s71_frc.py` |
| S72 | wireless / PlayMem / OnDemand | P2P **Group Owner** (WPS, PIN), DLNA, `CameraOnDemandSaver` escribe **`/setting/psd.bin`** (el ZPD de S75) | [`analysis/s72_wlan/`](../analysis/s72_wlan/) | `tests/test_s72_wlan.py` |
| S73/S74 | protocolo `ADJ_CMD` | 38 comandos de ajuste de panel/EVF; **un ID y 8 sub-comandos = máscaras acumulativas** `0x01…0xFF` | [`analysis/s73_adj/`](../analysis/s73_adj/) | `tests/test_s73_adj.py` |
| S75 | ZPD (zone plate detection) | calibración del sensor **con datos de la lente**; 2 canales de interrupción DFE; escritura en la SRAM del sensor | [`analysis/s75_zpd/`](../analysis/s75_zpd/) | `tests/test_s75_zpd.py` |
| S76 | etapas del pipeline | **73 etapas `Stage_*`** con su fichero fuente y las **26 funciones `sa_func_*`** | [`analysis/s76_stages/`](../analysis/s76_stages/) | `tests/test_s76_stages.py` |
| S77 | Creative Style / WB | dos tablas de estilos (13 + 12); el bloque `wb_*` es del **display**; en el firmware no hay Picture Profile | [`analysis/s77_pp/`](../analysis/s77_pp/) | `tests/test_s77_pp.py` |
| S78 | parámetros `apc_*` | **50 parámetros** en 7 módulos del motor YC (`lpf`, `mask`, `yld`, `acm`, `zoukou`, `coring`, `gain`) | [`analysis/s78_apc/`](../analysis/s78_apc/) | `tests/test_s78_apc.py` |
| S79 | mapa de módulos | **348 prefijos de módulo** del firmware con su rango de direcciones | [`analysis/s79_modules/`](../analysis/s79_modules/) | `tests/test_s79_modules.py` |
| S80 | ZIT (defectos) | motor de **corrección de defectos (DDC)**: 4 áreas de memoria, 7 operaciones en el SA, 2 canales de interrupción | [`analysis/s80_zit/`](../analysis/s80_zit/) | `tests/test_s80_zit.py` |
| S81 | framework ADF | arranque, **MSGQ**, MMGR y **102 comandos de depuración** (`DBGCMD`) | [`analysis/s81_adf/`](../analysis/s81_adf/) | `tests/test_s81_adf.py` |
| S82 | AutoFraming | encuadre forzado con rotación tras validar canvas/alineación; 8 etapas de control | [`analysis/s82_autoframing/`](../analysis/s82_autoframing/) | `tests/test_s82_autoframing.py` |
| S83 | módulos menores | ACCY (accesorios UART), CAM_FUNC_MGR, VIDENCSTAT, ENCOUCSTAT, ENCSEQCTRL, SAD, PNL, AUGI, WSX | [`analysis/s83_modules/`](../analysis/s83_modules/) | `tests/test_s83_modules.py` |
| S84 | API del motor de imagen | **19 familias `sa_func_*`** con sus firmas C++; `NLAP` y `MOTIONSHOT` **eliminados** en fw3.21 | [`analysis/s84_sa_api/`](../analysis/s84_sa_api/) | `tests/test_s84_sa_api.py` |
| S85 | `CLK_CTRL` + `VPH_API` | control de reloj y vocabulario del vídeo del visor, **nuevos en fw3.21** | [`analysis/s85_clk_vph/`](../analysis/s85_clk_vph/) | `tests/test_s85_clk_vph.py` |
| S86 | `VDF` + `VEF` | el **visor**: ~200 clases, espejo EVF↔panel, down-conversion PAL/NTSC, marco de cara | [`analysis/s86_vdf_vef/`](../analysis/s86_vdf_vef/) | `tests/test_s86_vdf_vef.py` |
| S87 | almacenamiento | medio externo como recurso sincronizado; el FS está en el userland (`libInfraFsys.so` = exFAT/FAT32) | [`analysis/s87_storage/`](../analysis/s87_storage/) | `tests/test_s87_storage.py` |
| S88 | GOLFSHOT / MOTIONSHOT | disparo de golf por **análisis de sonido** (3 fases SA, ALOCK, temporización por VFC) | [`analysis/s88_shotmodes/`](../analysis/s88_shotmodes/) | `tests/test_s88_shotmodes.py` |
| S89 | `IDT`/`IDT_OPD` | mapas que el imager recibe; FOPD de 4 canales; captura **partida** (IDTSA) | [`analysis/s89_idt/`](../analysis/s89_idt/) | `tests/test_s89_idt.py` |
| S90 | reproducción | PlayArranger, programador de **VFC**, cuatro modos de salida VDISP | [`analysis/s90_playback/`](../analysis/s90_playback/) | `tests/test_s90_playback.py` |
| S91 | submódulos ADF | ADJ (sensor de audio), SYSND (sonido del sistema 60/50 Hz), FACE, AFNR, CH_SRC, GS | [`analysis/s91_adf/`](../analysis/s91_adf/) | `tests/test_s91_adf_submods.py` |
| S92 | medios | secuenciador LIRO, `Scene%02d.txt`, interfaz `MprIf` de `libmpr.so` | [`analysis/s92_mediadb/`](../analysis/s92_mediadb/) | `tests/test_s92_mediadb.py` |
| S93 | bus OSAL (userland) | **16 grupos (GID) y 13 colas (LID)**; `libBizFw.so` orquesta caras y escalar; mDNS y API web | [`analysis/s93_osal_bus/`](../analysis/s93_osal_bus/) | `tests/test_s93_osal_bus.py` |
| S94 | API HAPI | la API de la app remota: `REQ_MSGE`/`EVT_MSGE`/`COMP_MSGE` y 139 símbolos `CamApi*` | [`analysis/s94_hapi/`](../analysis/s94_hapi/) | `tests/test_s94_hapi.py` |
| S95 | ficheros de la cámara | **43 rutas**: parámetros SPICA/PSF en `/usr/sabin/` y **trazas que la cámara escribe en `/mnt/`** | [`analysis/s95_files/`](../analysis/s95_files/) | `tests/test_s95_files.py` |
| S96 | modos de captura | `drive_mode` (69) del imager y `CapMode`/`ExposureID`/`ContID`/`BDROSeq` de la captura | [`analysis/s96_modes/`](../analysis/s96_modes/) | `tests/test_s96_modes.py` |
| S98 | orquestador userland | `libBizFw.so` une userland y firmware: la clase `AdfCh` repite el vocabulario `Prc`/`Sys`/`In`/`Out` del ADF | [`analysis/s98_bizfw/`](../analysis/s98_bizfw/) | `tests/test_s98_bizfw.py` |
| S99 | arquitectura del userland | las capas de `libObj.so`: `MWF` (mensajes), `UFW` (recursos), `MprIf` (medios), `ux`+`GEN_*` (GUI), `AVBIZ` (apps) | [`analysis/s99_userland/`](../analysis/s99_userland/) | `tests/test_s99_userland.py` |
| S97 | sincronización del codificador | `McAvcEncModeMgr` con 14 `CMD_ID_*`, escritura del bloque AUGI con el audio | [`analysis/s97_encsync/`](../analysis/s97_encsync/) | `tests/test_s97_encsync.py` |
| S100 | contrato ADF ↔ `AdfCh` | 90 comandos `[ADF][DBGCMD]` y 35 métodos userland emparejados uno a uno | [`analysis/s100_adf_contract/`](../analysis/s100_adf_contract/) | `tests/test_s100_adf_contract.py` |
| S103 | subsistema SDF | la capa de *dataflow* still: 33 `MSG_ID_SDF_*`, 477 trazas, errores de PTM | [`analysis/s103_sdf/`](../analysis/s103_sdf/) · [doc](s103-sdf.md) | `tests/test_s103_sdf.py` |
| S104 | prefijos exclusivos A6000 | `ADC_DEBUG`, `AVR`, `ADR`, `BKID`, `AVOUT`, `CAMCORE`: ausentes en A7S | [`analysis/s104_prefixes/`](../analysis/s104_prefixes/) · [doc](s104-prefixes-a6000.md) | `tests/test_s104_prefixes.py` |
| S105 | panorámica / barrido / bracketing / intervalo | el modo se decide con 2 bits del contexto `0x43e9b548` y pide la petición `0x301f`; cadena `PanoramaSweepStart` → `PanoramaStitch`; bracketing solo como `lc_BracketAF.cpp`; intervalo con semáforo `CAPTURE_INTERVAL` y PTM | [`analysis/s105_panorama/`](../analysis/s105_panorama/) · [doc](s105-panorama-bracket-interval.md) | `tests/test_s105_panorama.py` |
| S109 | módulo `[CDIAG]` (diagnóstico del códec) | 270 trazas: 7 escenarios × 8 operaciones, 27 firmas `CDIAGER`, 16 clases con tabla de registro en `0x43fda6a0`; **idéntico en la A7S** (270/270) | [`analysis/s109_cdiag/`](../analysis/s109_cdiag/) · [doc](s109-cdiag.md) | `tests/test_s109_cdiag.py` |
| S116 | módulo `[SFRS]` (control por *pins*) | 117 trazas: `SETPIN`/`GETPIN`/`PINSEND`, `ReqYccAsap`, `SendExecTrigger`; 131 puntos PIC en 52 funciones compactas; sub-bloques SUPERSTABLEMOVIE 37, MOTIONSHOTVIDEO 25, EFFECTMOVIEREC 23; en la A7S hay 34 trazas más | [`analysis/s116_sfrs/`](../analysis/s116_sfrs/) · [doc](s116-sfrs.md) | `tests/test_s116_sfrs.py` |
| S117 | cabecera de códec `[AUGI]` | 75 apariciones → 26 cadenas `[AUGI]` + 49 `[CodecIF][AUGI]…`; conversores `DecEx/DecInAudio/DecInVideo/EncExAugiConverter` y `CodecEventCreateVAUGI`; 86 puntos de emisión, 0 sin referencia; **idéntico en la A7S** | [`analysis/s117_augi/`](../analysis/s117_augi/) · [doc](s117-augi.md) | `tests/test_s117_augi.py` |
| S118 | módulo `[SFRA]` (infraestructura escalar) | 100 trazas, 11 sub-bloques, 11 ficheros fuente; **17 comandos con ids decodificados de los bytes**; `TBB` de finalizaciones `0x439a1654`; núcleo `ScalarInfraAsyncMain` `0x439a1864`; **100/100 idéntico en la A7S** | [`analysis/s118_sfra/`](../analysis/s118_sfra/) · [doc](s118-sfra.md) | `tests/test_s118_sfra.py` |
| S124 | bloque de parámetros del imager por `drive_mode` | `shut` = byte +9 del bloque de modo; `svd`/`shd`/`spl` = u32 del contexto (+0x178/+0x174/+0x170); **mismo conjunto de parámetros en A6000 y A7S**; la fw3.21 solo cambia la instrumentación y añade `zaf_now_shut_cycle` | [`analysis/s124_exposure_params/`](../analysis/s124_exposure_params/) · [doc](s124-exposure-params.md) | `tests/test_s124_exposure_params.py` |
| S120 | módulo `[IDT_OPD]` (mapas del imager) | 274 apariciones con **274 gemelos `[IDT]`** contiguos; `IDT_OPD` = recurso del `SyncResMgr` (`RESOURCE_IDT_OPD` `0x43c9c461`) y comandos ya presentes en A7S/A6300; 165 funciones, bloques IE/MAP verificados | [`analysis/s120_idt_opd/`](../analysis/s120_idt_opd/) · [doc](s120-idt-opd.md) | `tests/test_s120_idt_opd.py` |
| S121 | módulo `[AIP]` (audio/fader vía el escalar) | 37 trazas, 16 funciones, 6 sub-bloques RTTI; callbacks `Ack`/`Comp`/`Err` en SA y LPS; **tabla de backup de 350 entradas** en `0x43bd1964`; cliente = ADF (S81); **idéntico en la A7S** | [`analysis/s121_aip/`](../analysis/s121_aip/) · [doc](s121-aip.md) | `tests/test_s121_aip.py` |
| S119 | etiqueta `[APL]` (sub-módulo de `[CAMERA_SA]`) | 42 apariciones **dentro** de mensajes `[CAMERA_SA]: [APL] …` (etiqueta de segundo nivel, no módulo); en la A7S las 42 empiezan por `[APL]`; 5 funciones emisoras, 1 solo consumidor (`[CAMERA_MAIN_TC]`) | [`analysis/s119_apl/`](../analysis/s119_apl/) · [doc](s119-apl.md) | `tests/test_s119_apl.py` |
| S111 | módulo `[TRK]` (tracking) | 215 cadenas (207 textos) en 47 funciones: STK (76), BT (44), EDTSA (19), PMV (16), IRO2G (13), DETSA (9); código en `0x43a30000`–`0x43a39000`; 99 ficheros `FC/*.cpp`; **idéntico en la A7S** (mismos textos y recuentos) | [`analysis/s111_trk/`](../analysis/s111_trk/) · [doc](s111-trk.md) | `tests/test_s111_trk.py` |
| S115 | driver del imager `[CAM_IMAGER]` | 371 trazas (292 del driver): P2S por páginas con DFE0/DFE1, `int_p2s_handler`/`int_timer_handler`, SIF (sync code serie/paralelo), `ImagerCommon`→CISIF (1 canal), `SubLVDS`; máquina de lectura/exposición por `drive_mode` con campo **`shut`** y `SSBRK_ON` | [`analysis/s115_cam_imager/`](../analysis/s115_cam_imager/) · [doc](s115-cam-imager.md) | `tests/test_s115_cam_imager.py` |
| S112 | módulo `[CAMERA_MAIN_SYNC]` | 429 trazas: `SyncResMgr` (55) sobre `CAMDEV(0\|1)`/RC/APL, volcado de registros, `DFS`/`DVS`, `Sync_Kick_*`, `HS_Sequence`; mapa función→traza (430 funciones); 418/429 comunes con la A7S | [`analysis/s112_camera_main_sync/`](../analysis/s112_camera_main_sync/) · [doc](s112-camera-main-sync.md) | `tests/test_s112_camera_main_sync.py` |
| S114 | motor de secciones de la captura | **15/17 secciones nombradas** (id↔etapa): `0x01`=Prelight por llamada directa al selector; `0x00`/`0x06` sin nombre en el firmware; 5 selectores auxiliares fuera de la tabla | [`analysis/s114_sections/`](../analysis/s114_sections/) · [doc](s114-section-engine.md) | `tests/test_s114_sections.py` |
| S113 | gestor de memoria dinámico `[CAM_DMM]` | 54 trazas, 25 funciones contiguas (`0x439011d8`–`0x43903d5c`); 11 operaciones (incl. *rendezvous* y asíncronas OSAL), 4 clases `ERR_DMM_*`; el userland `DmmAccess` (S37) es cliente de este servidor | [`analysis/s113_cam_dmm/`](../analysis/s113_cam_dmm/) · [doc](s113-cam-dmm.md) | `tests/test_s113_cam_dmm.py` |
| S108 | módulo `[CAMERA_SA]` | 231 trazas del acelerador escalar en 13 sub-bloques (APL, memoria, `GetAddr`, alineación, mailbox, DUALREC, handles, `SA_FUNCDRV_E_*`); 231/231 mensajes idénticos en A7S y A6300 **sin etiqueta** | [`analysis/s108_camera_sa/`](../analysis/s108_camera_sa/) · [doc](s108-camera-sa.md) | `tests/test_s108_camera_sa.py` |
| S110 | motor de imagen `Camera::YC` | 970 trazas `[CAMERA_MAIN_YC]`: API de 8 `api_YC_*`, 12 `job_YC_*`, 141 sub-módulos (SHD/ITP/YAP/DCV/OLC/NR/CLP/MARBLE/KKNR/PFR); 332 funciones; 969/970 comunes con la A7S | [`analysis/s110_camera_main_yc/`](../analysis/s110_camera_main_yc/) · [doc](s110-camera-main-yc.md) | `tests/test_s110_camera_main_yc.py` |
| S107 | `Camera::CamCore` + `ResourceStack` | 37 trazas `[CAMCORE]` (0 en A7S): SGC, RDC/PFR, AIF, `MemoryPool`, `ExlHelper`, DMA setter, powersave, defectos; RTTI `CamCore8RdcImageE`/`13SplitRdcImageE`; `ResourceStack` acquisition/liberation desde `[IMAGING_CAP]` | [`analysis/s107_camcore/`](../analysis/s107_camcore/) · [doc](s107-camcore-resources.md) | `tests/test_s107_camcore.py` |
| S106 | `IMAGING_CAP` (gestor de captura still) | 697 trazas + 83 ficheros fuente embebidos; motor de **17 secciones** (`0x43ff8fb4`), CapMgr, CAIF, 8 modos `MODE_CAP*`; esquema PIC de referencias a cadenas | [`analysis/s106_imaging_cap/`](../analysis/s106_imaging_cap/) · [doc](s106-imaging-cap.md) | `tests/test_s106_imaging_cap.py` |

## 2. Cómo se sostiene el rigor

- Cada informe separa **VERIFICADO** (dirección exacta en el blob, verificada leyendo los bytes) /
  **INFERENCIA** (lectura razonada) / **NO_VERIFICADO** (pendiente).
- Cada hito tiene un **test de bytes** en `tests/` que falla si una dirección o una cadena cambia.
- Cuando un subagente entrega un hito, el agente principal lo **re-verifica** y corrige lo que no
  encaja (así se corrigieron, entre otros, las direcciones en espacio de fichero, un diferencial
  A7S falso, una "tabla" que era código, y una afirmación de exclusividad de la fw3.21).
- El estado consolidado vive en [`knowledge/CURRENT.md`](../../knowledge/CURRENT.md) y el historial
  en [`knowledge/PROGRESS.md`](../../knowledge/PROGRESS.md).
