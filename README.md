# Sony A6000 Hardware & Firmware Reverse Engineering Project

Investigación de hardware, firmware, arquitectura, arranque, recuperación y
pipeline de captura. Se conservan los resultados anteriores. El obturador
electrónico pasa a ser un [subproyecto](projects/electronic-shutter/README.md).

## Agentes (Claude Code, Codex/ChatGPT, DeepSeek Harness)

Reglas en `AGENTS.md` y `CLAUDE.md`; skills en `.claude/skills/` y `.agents/skills/`
(copias idénticas, verificadas por `tests/test_agent_skills_sync.py`). Instalación de
REA/Ghidra, MCP y arranque de sesión: [docs/agent/README.md](docs/agent/README.md).
Para ChatGPT web, pegar [docs/agent/chatgpt-pack.md](docs/agent/chatgpt-pack.md).
Comprobación de entorno: `python scripts/agent/check_env.py`.

## Organización y resultados actuales

- [S77: Creative Style y balance de blancos](analysis/s77_pp/picture_profile_creative_style.md): dos tablas de estilos en `av-cam.bin` (13 entradas en `0x43ca6702`–`0x43ca676d` con `Real`, 12 en `0x43ca678b`–`0x43ca67f0` sin él), **idénticas en la A7S fw3.20**; el bloque `wb_*` (`0x43c76c26`–`0x43c76e2b`) es la **calibración de WB del display** (dentro de `ADJ_CMD`, S73), no el WB fotográfico; **negativo verificado**: 0 apariciones de `CreativeStyle`/`PictureProfile`/`Highlight`/`Saturation`/`Sharpness`/`wb_shift` en el firmware → el control vive en el userland: `wrapperCreativeStyle.so` (8 420 B: `getCreativeStyle`/`setCreativeStyle`/`convertProcessValueIdToValue`/`convertValueToProcessValueId`, `stella::8BitArray`, ruta de build `141H…Guiengine_131H`) y `wrapperWhiteBalance.so` (15 556 B: `setWhiteBalance(…,int,int,int)`, `resetAdjustmentValue`, backup vía `Bkup_Read_Setting_Attr`, aplicación vía `ViewBase::requestModelExecute`). 10 tests (`tests/test_s77_pp.py`).
- [S86: el subsistema del visor — `VDF` (marco de display) y `VEF` (visor electrónico)](analysis/s86_vdf_vef/vdf_vef_viewfinder.md): `VDF` (243 trazas) es un framework C++ completo del display (~200 clases RTTI `N3VDF*`): núcleo (`SubsystemMain::Main()` `0x43c8221b`), framework de mensajes (`MsgAccessor`/`MsgIterator`/`WaitQueue`), cmds de sistema (Pin*/Trigger/Receive/Sysv/CipaModeOut), de display (`SetPanelOut` `0x43c8714a`, `SetPanelBrightness` `0x43c86eea`, `SetPanelColorTemperature` `0x43c86886`, `SetParallax`, `SetOsdAlpha`), de entrada (`UpdateYuv` `0x43c888ef`, `SetYuvLayout`, `SetYuvMute`, `SetShutterMute`, `UpdateFaceFramePin` `0x43c887e9`), de servicio (`SetZebra`, `SetPeaking`, `SetHistogram`, `SetFaceFrame`, `SetEvfParallax`, `SetLiveDemo`), rutas de imagen (`SetPath` `0x43c89fca`, `4K…`) y dispositivos (`EoLineDevice`/`EoPanelDevice`/`MirrorSubsystemSynchronizer`); **puente con VPH** (S85: `VphSetZebraCall` `0x43c87294`, `VphUpdateYuvFunction` `0x43c85017`), **con ADF** (S81: `VdfToAdfYcDataSender` `0x43c86165` + bus **SSBI** del display), **con CLK_CTRL** (S85: `CheckUpdateYuvTiming` `0x43c847d1`) y **con las caras** (S71: marco de cara). `VEF` (149) = visor electrónico: espejo con el panel, modos 3D/2D, multicast de pausa, down-conversion **PAL/NTSC** y cancelación de efectos sincronizada con el VFC. 14 tests (`tests/test_s86_vdf_vef.py`).
- [S85: `CLK_CTRL` (control de reloj) y `VPH_API` (API del vídeo del visor)](analysis/s85_clk_vph/clk_ctrl_vph_api.md): dos módulos **nuevos en la fw3.21** (0 trazas en la A7S fw3.20). `[CLK_CTRL]` (66): 12 llamadas `ddl_clkctrl_*`, estados `STATE_INIT1(InitDelay)`→`STATE_NORMAL(InitSignal)`→`STATE_LOCK` (+ `STATE_CHANGE_CLK`), gestión **por subsistema** (`open/close subsytem = 0x%04x`, `Busy!! already opened`), cambios de reloj/retardo con **dos VFC** (`m_vfc.main/sub` `0x43c3ac2f`) y arquitectura **maestro/esclavo** (`Receive Message from Master` `0x43c3abd0`, `Send Message to Slave` `0x43c3ac86`) que se coordina con VPH (`vph stat:%d,mode:%d` `0x43c3aa69`). `[VPH_API]` (106): vocabulario de comandos del procesado de vídeo del visor — ruta, OSD, **marco de cara** (`<faceframe_on>`/`<update_faceframe>`/`<faceframe_color>`, puente con S71), timecode, mute, línea (closedcaption/macrovision/vbidwss), panel (brightness/cabc/depth/reverse/ysetup), ayudas (zebra/peaking/gridline/histogram/testpattern) y corrección (parallax/extblackframe/color_temperature), **cada uno con su gemelo `_sub`** (los dos canales) más 11 salidas de estado. 11 tests (`tests/test_s85_clk_vph.py`).
- [S72: wireless y transferencia remota (WLAN / PlayMem / "Camera on Demand")](analysis/s72_wlan/wlan_playmem.md): pila wireless del userland fw3.21 — `libWlanAdjust.so` (60 492 B: `wlanSetSsid/TxCh/TxMode/TxRate/TxPower`, 11 `wpa_ctrl_*`, `SetMacAddress`), `libWlanControlCommon.so` (23 840 B: `initializePort`, `installWlanDrivers`, 25 × "BMI"), `libWlanResource.so` (63 656 B: `GetMacAddress(WlanResource::ST_MSG_SYNC_REQ*)`, `OSAL_MSGQ_GID_WLAN_RSRC_DBG/_TEST`), **`libGOConnectionManager.so`** (106 016 B: P2P con rol **Group Owner**, estados Idle→Init→Auth→Wait→ChgKey→AuthConn→Finalizing→Stop, comandos WPS `StartWpsCmd`/`InputPin`/`AuthPush`/`ChangeKey`), `libInfraDlnaControl.so` (525 892 B: **DLNA/UPnP**, `dc_statetbl`, 9 `m_lid_*`), **`CameraOnDemandSaver.so`** (20 084 B: escribe en `/mnt/dcim/100msdcf` y **`/setting/psd.bin`**, el mismo fichero ZPD de S75) y `libHapiLib.so`; **`netconf/`** con 4 configuraciones (`bss.conf`/`p2p.conf` WPS `SonyImagingDevice` + `uuid=12345678-9abc-def0-1234-56789abcdef0`, `p2p_go_intent=10`, `p2p_ssid_postfix=-WCM`, `dhcpd.conf` subred 10.0.0.0/16). 16 tests (`tests/test_s72_wlan.py`).
- [S84: el API del motor de imagen (SA) — catálogo de `sa_func_*`](analysis/s84_sa_api/sa_api_catalogue.md): la superficie del driver `Camera::SaFuncDrv` tiene forma uniforme (`SA_FUNCDRV_ERR sa_func_<X>_<op>(__uint8_t unidad, __uint16_t func_code, <X>_START_PARAM*)`) y **19 familias**: `BFNR`, `BOKS`, `CONTP`, `DECOMP`, `DUALREC_BAYER`/`CLEARVID`, `GOLFSHOT` (dos sobrecargas de `start`: SSP y BGEST), `KKNR`, `LFNR`, `NFLASH` (flash), `PreDCV`, `SFTFCS`, `SPICA` (fases **PRE/MAPPING/POST**), `STAR`, `TBOX`, `YKNR`, `BDEX` (+ `MOTIONSHOT` y `NLAP` solo en A7S); 92 cadenas con `sa_func_` en A6000 (109 en A7S); errores `SA_FUNCDRV_E_OSAL/RLTCODE/ERRCODE`. **Diferencial**: la fw3.21 de A6000 **elimina** `NLAP` (0 ocurrencias) y `sa_func_MOTIONSHOT_*`; lo que queda es `MOTIONSHOTVIDEO` del módulo SFRS. 11 tests (`tests/test_s84_sa_api.py`).
- [S83: los módulos "menores" del firmware, decodificados](analysis/s83_modules/minor_modules.md): `[ACCY]` (106) = **accesorios por UART** (`NotifyAttachedUart` `0x43c24cca`, `[HW]:AD=%d, ID=%d` `0x43c24cac`); `[CAM_FUNC_MGR]` (43) = **gestor de funciones de captura** (`SyncProcMargin[usec] HS0..HS3@CPU2/CPU0(IDT)/CPU3(RCH)` `0x43ca12f6`, `SetCapMode:Invalid CapMode` `0x43caf036`); `[ENCOUCSTAT]` (49) = **errores del codificador AVC** (`AVC_ENC_VIDEO_ERR_STATE/MEMORY/PARAM/INDEX`); `[VIDENCSTAT]` (70) = **estado del encoder de vídeo** (`Pts`/`EndFlug` `0x43cd680b`); `[ENCSEQCTRL]` (46) = **secuenciador de encoding** (`[O/U Crank] Table[%d] fR sR` `0x43c4bd2b`); `[SAD]` (45) = **programas del motor de imagen** con cabecera (`CdcSaPrg/NmlSaPrg/RsdSaPrg Hdr Err`); `[PNL]` (41) = **panel/display** con callbacks y backup (`cmd_set_conf_cb_NULL` `0x43c761bd`); `[AUGI]` = **formato de bloque con cabecera** (`end_flag`/`PS_flag`/`EP_flag`); `[WSX]` (59) = **búsqueda en fichero "BSFS"** (`BSFS SEARCH LOOP ERROR` `0x43ce41fe`). 10 tests (`tests/test_s83_modules.py`).
- [S81: ADF — framework de arranque, MSGQ, MMGR y comandos DBGCMD](analysis/s81_adf/adf_framework.md): el **módulo más grande del firmware por trazas** (1220 cadenas `[ADF]` en A6000, 1269 en A7S) en `0x43c26366`–`0x43c37a62`; **arranque** `BootInit` `0x43c26366` → `InitWaitVsync SelectCompo` `0x43c26375` → `AVIO/AUDIOIP INIT COMP` `0x43c263f6`/`0x43c26411` → `BootExit` `0x43c263c9`, con **reenvío de mensajes** (`INIT Resend …` `0x43c263d8`–`0x43c264e1`); **IP de audio** (`AUDIO_IP_CONFIG_TYPE_VGS/PR/MF/CONS/BANDI` `0x43c264fa`–`0x43c2659e`, enlace con S69); **MMGR** (`MMGR COMM INFO` `0x43c265ce`); **MSGQ** (`MSGQ Set:srcId/msgId` `0x43c26788`, `SendImmediateComp` `0x43c268a8`, grupo `MSGQ_GID_HOTSHOE_INFRA1` `0x43c266e6`); y **102 comandos DBGCMD** (`0x43c2a443`–`0x43c2b315`): `System`, **medida del tiempo de CPU2 a 60/48 Hz** (`CPU2 ExecTime 60Hz max m/s` `0x43c2a465`), `Input`/`InputPro`, `Output`/`OutputPro`, `Proc` (**fases lineales del arranque**: `SetLinearPhase`, `SetDec0/1`, `SetAip0/1`, `GetSa0/1`, `GetPin0/1`), `SystemSound` y `SoundAnalyzer` con el **disparo de golf** (`StartGolfShot` `0x43c2b143`). 9 tests (`tests/test_s81_adf.py`).
- [S71: subsistema de detección de caras y objetos (FC/FRC)](analysis/s71_frc/frc_subsystem.md): **99 ficheros `FC/…`** en el `av-cam.bin`, **idénticos en A6000 fw3.21 y A7S fw3.20**; puente con el **acelerador Scalar (SA)**: recursos en Core2/Core3 (`AcquireRes … Core2 user[0]` `0x43cf094a`, `RES_SA_FOR_FRC2` `0x43cf09b8`), búferes `s_sa_temp_icon_mem`/`s_sa_param_mem` (`0x43cf0bd8`), MMU (`MakeMmu` `0x43cf0c11`), ciclo de cálculo (`ddl_saCalcCancel` `0x43cf0afb`, `alloc size:%d, expected:%d` `0x43cf0b39`) e iconos (`FRC: Init FaceIcon` `0x43cf0d6c`, `FaceIconInfo::Alloc()` `0x43cf0db8`); módulo `[FACE]` (70 trazas) y módulo `[TRK]` (216) con **seis detectores** — DETSA (Core2), EDTSA (Core3: cara/ángulo/nodo/rangos HSV), IRO2G, PMV (vectores de movimiento), STK (saliencia y similitud toque/color) y BT (fg/bg + mapas bayesianos); el algoritmo FRC reordena IDs por `record_rank` y prioriza la creación de iconos; además parpadeo, Pre-FDT, alternancia cara↔objeto, panorámica/retoque y MakerNote de caras. 20 tests (`tests/test_s71_frc.py`).
- [S80: ZIT — corrección de defectos del sensor (DDC) en el imager](analysis/s80_zit/zit_defect_correction.md): motor de corrección de defectos con 118 trazas `ZIT` (75 en A7S fw3.20) y clases `ZitMemBuffer` `0x43cf768e`, `ZitZphDefectBuffer` `0x43cf81a1`, `ZitZphLineTableBuffer` `0x43cf96ef`; trabaja sobre **cuatro áreas** (`adj`/`usr`/`slow`/`mend`, `0x43cf7706`) y en **bancos por read mode** (`0x43cf7771`); puente al motor de imagen con `ZitSaFunctionDriver` (`ZIT_SaOpen`/`ZIT_SaStart`/`ZIT_SaClose` `0x43cfa2a7`–`0x43cfa2ee`) y MMU propio; **siete operaciones en el SA** — `Merge`, `ConvThin`, `ConvUnity`, `ConvZ1C`, `Det` (`DetectInfo [ch1..ch4]`, `RAWInfo [AVE/MIN/MAX]`), `Hist` y `ZphSA` — más `ZitSA_ConvDdc`; registro de nivel y posiciones de defecto (`SetZitLog_*` `0x43cf7e5f`–`0x43cf7f2e`) y búferes `Zph*`; variantes de **long exposure** (`buildLongExpCapData_DDC`) y **vídeo** (`MovieAdj_SpreadDefectsOverSharedPixels`); drivers `ZitDdcDriver` (`0x4386bbee`) y `ZitZ1cDriver` (`0x437b93c0`) en `CAMERA_MAIN_IM`. 9 tests (`tests/test_s80_zit.py`).
- [S79: mapa de módulos del firmware por prefijos de log](analysis/s79_modules/module_map.md): extraídos todos los prefijos `[MÓDULO]` de las cadenas del blob: **348 módulos** en A6000 fw3.21 y **277** en A7S fw3.20; `CAMERA_MAIN` se descompone en **8 submódulos** — `CAMERA_MAIN_YC` (970, motor de imagen), `CAMERA_MAIN_SYNC` (429, `SyncResMgr`/`CAMDEV(0|1)`), `CAMERA_MAIN` (135), `CAMERA_MAIN_TC` (127, **giro**: `GyroStitScl`/`LmtGyroVect`, enlaza con S70), `CAMERA_MAIN_LC` (72, **calibración de lente**: `lc_Movie_DM_AF_Util_*`, enlaza con S75/ZPD), `CAMERA_MAIN_CC` (49, **control de captura**: `ExtractCaptureData`/`CaptureInit`/`SetNRParam` con `CapMode/ExposureID/ContID/BDROSeq`), `CAMERA_MAIN_IM` (42, **térmico**) y `CAMERA_MAIN_FC` (9, **datos de ojo**); y las familias mayores: `ADF` (1231), `IMAGING_CAP` (697), `SDF` (477), `CAM_IMAGER` (371), `IDT` (298), `IDT_OPD` (274), `VDF` (243), `CAMERA_SA` (231), `TRK` (216), `MOUNT_DEBUG/ERROR` (132/80), `SFRS/SFRA`, `VPH_API`, `ACCY`, `DBGCMD`, `STK`, `FACE`, `VIDENCSTAT`, `CLK_CTRL`, `GOLFSHOT`, `WSX`, `CTRLCORE`, `CAM_DMM`, `SAD`, `CAM_FUNC_MGR`, `APL`, `PNL`. 5 tests (`tests/test_s79_modules.py`).
- [S78: parámetros `apc_*` del motor de imagen YC](analysis/s78_apc/yc_apc_params.md): el motor `Camera::YC` calcula sus parámetros de imagen con un espacio de nombres jerárquico `apc_<módulo>.<parámetro>`: **50 parámetros** en **7 módulos** (`apc_lpf` 2, `apc_mask` 6, `apc_yld` 9, `apc_acm` 4, `apc_zoukou` 18, `apc_coring` 8, `apc_gain` 3) entre `0x43cc44cb` y `0x43cc4fe4`; el nombre va **embebido en la cadena de formato** del log (`'[CAMERA_MAIN_YC]: YAP:\tapc_lpf.vaplpf\t=%x'` `0x43cc44b4`); cada módulo lo calcula un job distinto (`apc_lpf`→`0x438b0f80`, `apc_mask`→`0x438b1058`, `apc_yld`→`0x438b11f0`, `apc_acm`→`0x438b177c`, `apc_zoukou`→`0x438b2070`, `apc_coring`→`0x438b2ac4` con firma `job_apc_coring_stl` `0x43cc513d`, `apc_gain`→`0x438b3570` con firma `job_apc_gain_stl` `0x43cc40df`); el cálculo depende de la secuencia BDRO, del ISO y del efecto de imagen. 6 tests (`tests/test_s78_apc.py`).
- [S76: pipeline de captura (etapas `Stage_*`) y motor de imagen](analysis/s76_stages/stage_pipeline.md): **73** etapas del procesado embebidas en el `av-cam.bin` con su fichero fuente (`Stage_Apollo.cpp` `0x43cc6e0f`, `Stage_BDRO.cpp` `0x43cc71fa`, `Stage_BOKS.cpp` `0x43cc7569`, `Stage_Decomp.cpp` `0x43cc7df8`, `Stage_Develop.cpp` `0x43cc82be`, `Stage_FaceDetect.cpp` `0x43cc8d9d`, `Stage_KKNR.cpp` `0x43cc9329`, `Stage_MARBLE.cpp` `0x43cc956d`, `Stage_OPD.cpp` `0x43cc9785`, `Stage_Orientation.cpp` `0x43cc97b4`, `Stage_SPICA` `0x43cc990c`, `Stage_STAR` `0x43cc9dd6`, `Stage_SoftFocus.cpp` `0x43cc9f22`, `Stage_StillDate.cpp` `0x43cca086`, `Stage_TBOX.cpp` `0x43cca36a`, `Stage_YKNR` `0x43cca4d9`, + Panorama/Raw/Resize/CaComm/CameraHAPI/AutoFraming/Adjust/Notify) y **26** funciones `sa_func_*` con correspondencia nominal etapa↔SA (BOKS, DECOMP, SPICA, STAR, YKNR, LFNR, DUALREC_BAYER/CLEARVID, BDEX); `Stage_SPICA` carga sus parámetros de `/usr/sabin/spica_*_tap_step*.bin` y `Stage_Adjust` contiene `ContrastPlus_Base` (`0x43cc7bc2`). 5 tests (`tests/test_s76_stages.py`).
- [S75: ZPD (zone plate detection) — calibración del sensor con datos de la lente](analysis/s75_zpd/zpd_subsystem.md): namespace `Camera::ZPD` con **14** clases (`MemObj`, `MemUnit`, `MemUnitBackup`, `MemFileLoadObj`, `Control::Detect`, `Control::WorkerBase`, `Control::SequencerBase`→`Sync`/`Async`/`Sequencer`, `ITrace` y **`ZPD::Lens::LensInterpretChunk`/`…ChunkEd`**, `0x43ccf318`–`0x43cd1c3b`); **tres orígenes de datos**: de la lente (`[ZPD]: load lens data from lens.` `0x43ccf2c7`), del cuerpo (**`/setting/psd.bin`**) y `dra data` (`0x43ccf2a0`); consumo en el DFE: factores de interrupción `ZPD0`/`ZPD1` (`0x43c91781`–`0x43c91925`), carga de posiciones de defecto en la **SRAM del sensor** (`ImgDdcSetter::loadDefectPos ZPD_SRAM shortage` `0x43cf75ee`) y trazas APB/AIF (`ZPD_APB0/1`, `ZPD W-ch0/R-ch1`); coordinación con el bus de la lente (`[BL]ZPD change EclipseDataComState from STANDBY to START` `0x43c976b5`; el protocolo MOUNT incluye el campo **`LC T.O. Cnt`** `0x43c96c1e`) y con el AF híbrido (`zpd_mario_afa.cpp`, `LC_GetZpdResultInfo`); **diferencial A7S fw3.20**: sin namespace de aplicación pero con los factores ZPD del DFE. 9 tests (`tests/test_s75_zpd.py`).
- [S73/S74: protocolo de ajuste de fábrica `ADJ_CMD` (panel/EVF/OLED) y `ContrastPlus`](analysis/s73_adj/adjust_cmd_recon.md): **38** comandos `ADJ_CMD_AVBB_PANELEVF_*` (`0x43c76c93`–`0x43c774b2`) para el display (VCOM, WB por sub-bloques R/G/B con `WB_SubB_{R,G,B}_Adrs=%02X`, CALDAC, **termistores** OLED/EVF, test de fábrica, detección de panel y de tipo de EVF) y 4 `ADJ_CMD_LIRO_DRIVERS_ADC_*` (`0x4398e578`); estructura del manejador `0x4363524c`: **un solo ID** (u16 `0x302` en `[r6+0x18]`) y **8 sub-comandos** (u8 en `[r6+0x1a]`, 1..8) que son **máscaras acumulativas** `0x01,0x03,0x07,0x0F,0x1F,0x3F,0x7F,0xFF` (`tbb` en `0x436354fc`, tabla de 8 bytes en `0x43635500`); `ContrastPlus_Base` (`0x43cc7bc2`) es procesado de imagen en el camino de captura. 10 tests (`tests/test_s73_adj.py`).
- [S70: reconocimiento del subsistema EIS/gyro](analysis/s70_is/is_gyro_recon.md): tres capas de trazas (`[CAMERA_IS][AS]`, `[EIS]`, `[DIST]`), termistores de display y **fichero de calibración por lente** `/mnt/FILE_IS_%04x.dat` (contador u16 + `snprintf`); la capa `IS` es el motor de estabilización por desplazamiento del sensor y **no** tiene relación con el obturador electrónico. 4 tests (`tests/test_s70_is.py`).
- [S68: gestión de batería, energía y carga (NP-FW50)](docs/capture/s68-battery-power.md): **resultado negativo verificado**: el `av-cam.bin` de A6000 **no tiene modelo del pack NP-FW50** (0 hits de `NP-FW`/`NPFW`/`FW50`); lo que hay es nivel de batería vía UPM (`Set UPM Battery Level` `0x43ca2dfd`), códigos de estado hacia un MCU (`ACV_BATT_Snd` `0x43c8f95e`, `BATT_AUTH_Snd` `0x43c8f96b`, `BATT_STATE1..3_Snd`, `BATT_TYPE1/2_Snd`, `Box_Temperature_Snd` `0x43c8f9fc`, `ACV Error Voltage` `0x43c8f83b`), **carga del flash** y no de la batería (`SB_CHARGE` `0x43cb4c23`, `uc_Charge*` `0x43ccd8c2`–`0x43ccd96c`), power save del imager y coordinación lente↔voltaje (`Wait E-MountLens ReduceVoltage` `0x43cc7aa4`, `CaptureCancel_PowerOffDetect` `0x43ca9d85`); la A7S conserva el bloque de estado pero no `BatteryInfo` ni los `Battery Info` de las luces. 19 tests (`tests/test_s68_power.py`). Sin efecto en S51 (fin electrónico NO VERIFICADO; A/B/C = NO).
- [S69: subsistema de audio de la A6000 (línea general)](docs/capture/s69-audio-subsystem.md): el audio es un *IP* más del driver de sensor (`AUDIOIP INIT COMP` `0x43c26411`, configs VGS/PR/MF/CONS/BANDI); micrófono (`SetParamSetMicMode` `0x43c26dc1`, `Abb::SetMicConfig` `0x43cddad4`); niveles (`SetParamSetRecLevel` `0x43c26df4`, `15AbbRecLevelCtrl` `0x43cdddf3`, `RecLevel SetRecLevel` `0x43929fa4`); WNR/voz (`WindStage:%d, MagDataRsv:%d` `0x43cddea7`, `MAGIC SetNwnr`, `PremiumCloserVoice`, `MyvoiceCanceling`); códecs `XAVCS_LPCM`/`MP4_LPCM`/`AAC` (`0x43c6909d`/`0x43c690c8`/`0x43c690f1`); enlace con vídeo (`ProcBuffMgrWrAudioPin` `0x43c28d29`, `AVBB_SCN_START/STOP_AUDIO`); la **A7S tiene códec externo** (`15AbbExtCodecCtrl` `0x43cd582e`) que la A6000 no. 9 tests (`tests/test_s69_audio.py`). Sin efecto en S51 (fin electrónico NO VERIFICADO; A/B/C = NO).
- [S66: montura de lente E-mount (línea general, sin relación con SilentShutter)](docs/capture/s66-lens-mount.md): subsistema `MOUNT`/"BL" del `av-cam.bin` A6000 (código `0x436dfe6c`–`0x436e9ea4`, 646 logs en `0x43c95659`–`0x43c9a900`, ficheros internos `Mount_Controller.cpp`/`Mount_DividedInfo.cpp`); bus cuerpo↔lente **UART** con handshake **CS/DATA** por GPIO (`gpio_get` `0x43b5e2bc`); **trama** `0xF0` | longitud `size+8` LE | commtype(`&7`) | **ID de comando** (`0x07` ATTACH_INFO1, `0x0A` CS_CREDIT, `0x15` UPDATE_DATA, `0x16` LENS_SLEEP, `0x2B` ALPHA_LENS_INFO) | datos | **checksum u16 LE** | footer `0x55`, con validación `HEADER/FOOTER/CHECKSUM/DATASIZE/COMMTYPE`; tipo de lente por 2 bits (`& 3`): 1 = **4.8 V** (4096 mV), 2 = no registrada, resto = desconocido (error `0xFF`, válido `0x0A`); ciclo de vida completo en los 63 logs de `0x436e5e3c` (LENS_WEAR → UART_HZ → ATTACH_INFO1..4 → STARTUP_INFO → CS_CREDIT → WAKE_UP → POWEROFF → DETACH_1/2/COMP → LOGIC_ON/OFF → STANDBY); **FW de la lente** por el mismo bus con CAIF/C3P (`0x436fe070`: LUPDT_INFO/LUPDT_DATA) y **segundo bus al DSP** `[LENS_PDR]`/BonoboDSP (`0x437089d4`, `0x43708a88`, `0x43708cc4`, MMIO `0xf292d000`); 18 ficheros `/lens/VX91xx_lensfile.bin` (cabecera `LF` de 16 B con `lens_id` en `+0x0c`, secciones `ED`/`CS`/`LC`, parser `0x43907c7c`), idénticos byte a byte a los de A6300 y **ausentes en A7S 3.20**; sombreado por lente (11 `ss_LensMountShdValue[]` + 32 `us_LensMountShdGain[]`) con tabla `tbb` de 69 modos de captura → 14 ShdMode (`0x438ef418`), bloque SHD **idéntico** A6000/A7S (217 logs cada uno); fw3.21 añade 4.8 V, LENS_WEAR, DETACH/attach, ALPHA_LENS_INFO, CS_CREDIT, CHG FREQ y handshake `[HS]` frente a la fw3.20. 31 tests (`tests/test_s66_lens_mount.py`). Sin efecto en S51 (fin electrónico NO VERIFICADO; A/B/C = NO).
- [S64: prueba en cámara de SilentShutter](docs/capture/s64-silent-ram-nvram-test.md): campo `0x83edf8bc` escrito/restaurado por service mode; backups NVRAM y 4 MB de RAM en ciclos off/on con control: sin cambios atribuibles al modo; `0x43804610` reinicializa el bloque (`+0x238`=0) y no hay ruta de persistencia en backup; sin consumidor de captura. Fin electrónico NO VERIFICADO; S51 A/B/C = NO. Prueba en modo normal por telnet/adb (OpenMemories Tweak): mismo bloque, `+0x238` forzado a 1 con 3 disparos ⇒ obturador sigue mecánico y la copia de trabajo no cambia; `scripts/camera_telnet.py`. Búsqueda estática del lector: copia de trabajo sin lector de Silent; instantánea `0x43e9b548`, campos vecinos, override de drive_mode y condiciones EFCS probados en cámara: sin cambio de obturador; solo el espejo `+0x210`=1 dio un sonido de disparo múltiple (4/4, un JPEG por petición; significado NO VERIFICADO). Pruebas en cámara detenidas por el usuario. Inventario de captura silenciosa vía `CameraSequence` (preview frames): [liveview-silent-capture-via-cameraex.md](docs/capture/liveview-silent-capture-via-cameraex.md). Volcados de cámara versionados en `analysis/camera-dumps/` (cada uno con `README.md`; referencia NVRAM buena: `nvram-referencia-20261020-214913`), ver [s65-nvram-incident-diff.md](docs/capture/s65-nvram-incident-diff.md). Reinicios de la cámara (logs en RAM, WDT/oops): [camera-reset-logs.md](docs/capture/camera-reset-logs.md). Firmware propio (vuelta atrás e instalación): [custom-fw-recovery-and-install.md](docs/capture/custom-fw-recovery-and-install.md); sondeo de guard `scripts/fdat_guard_probe.py` pendiente de ejecutar.

- [S62: PMCA — inyección de código, service shell y la propiedad `modelName`](docs/capture/s62-pmca-injection.md): `updatershell` inyecta un fdat propio (cramfs con `libupdaterbody`, header 0x30 B por modelo, guard CRC + modelo/región/versión sin firma; CXD90014) que el updater ejecuta y expone shell USB `0x23`; `serviceshell` (senser, HASP) da terminal y backup `0x603`. `bk w 0x003e0005` no es una dirección sino la propiedad BK4 `modelName` (subsistema `0x3e`/índice 5, 16 B, solo lectura) del almacén `/setting` (`nflasha2`), verificada en el preset de fábrica como `ILCE-6000` (test 5/5). El procedimiento `ILCE-6001` es coherente con la selección de fdat por nombre reportado, pero el efecto «shell mode» queda **NO VERIFICADO** (la cadena no existe en el firmware). S51 se mantiene.
- [S61: origen de los parámetros IMX210 y flujo de mensajes](docs/capture/s61-conclusions.md): corrección TBH de S60-Sol (base `0x43806a08`); selección A/B del bloque `obj+0xe20` (A: bit6 de `G[0xD]`, G=`0x43e964a4`; B: `[[p]+0x3a]==1`), cadena de B recuperada hasta `obj+0x2be..` vía `0x43861ed0` y 6.º par desde BK4 `0x300AB` (`(0x2EA0,0x6028)`); los pares parecen ventanas lo/hi ±0x400, no tiempos; petición 9 emitida desde `HS_Main` y publicación en `VD_Pre`; petición 3 sin emisor; sin estados alcanzables. Fin electrónico NO VERIFICADO; S51 A/B/C = NO.
- [S60: emisor de mensajes IMX210 y receptores A7S](docs/capture/s60-conclusions.md): A6000: `0x438069f0` es una tarea de mensajes (casos 4/10 = respuestas a 3/9) y los 24 B `+0xdd0` son 6 pares u16 con dos productores (`0x437ab510`, `0x43aecbfa`); A7S: `0x1000/0x1001` = trazas (eco de SetExposure/SetRead), sin efecto de control. Auditoría GPT no obtenida (límite de uso). Fin electrónico NO VERIFICADO; S51 se mantiene.
- [S59: validación cruzada Claude + GPT-6.1 Sol](docs/capture/s59-conclusions.md): escritor del bloque IMX210 `+0xDD0` recuperado (`0x43b00da0`, valores M de payload externo, sin M/Tv/clk alcanzables); constructor real C_Imager A7S `0x436f3fc0` emulado, corrige tramas/base P2S de S58 y aclara mensajes `0x1000/0x1001` (lista blanca de modos). Fin eléctrico IMX210 NO VERIFICADO; S51 se mantiene.
- [S58: productores AE y configuración efectiva A7S Silent](docs/capture/s58-conclusions.md): cálculo numérico de svd/shd/spl recuperado; cadena SetMode→SetExposure→SetRead→Execute emulada con stubs; matriz IMX235 corregida (69 filas), 100 escrituras en dos dispositivos. SetRead/ganancia se distingue de SetExposure. Fin eléctrico IMX210 NO VERIFICADO; S51 se mantiene.
- [S57: semántica de ID1/SSB/svd-shd-spl, Silent IMX235, XPI y sincronía P2S](docs/capture/s57-conclusions.md): ID1 = registro combinado (modo de lectura + ShutMode + strobe); SSB acompaña a toda actualización de exposición y no al fin; svd/shd/spl mapeados exactamente y svd atado a un contador de VD; Silent A7S = modos de lectura 0x4e/0x4f (variantes de 0x4c/0x4d); fin electrónico NO VERIFICADO, S51 se mantiene.
- [S56: transporte de registros del IMX210 (IDs = direcciones 16 bit, P2S/DFE0), CISIF = receptor](docs/capture/s56-conclusions.md): trama `81|len|81|AH AL|datos`, ShutMode→ID1, pulso SSB; fin electrónico NO VERIFICADO, S51 se mantiene.
- [S55: origen de los pares GPIO (base de backup BK4), A7S vs A6000](docs/capture/s55-conclusions.md): escritor `0x436bcef4`, infraestructura de pines idéntica en A7S, sin consumidor GPIO de P4C, S51 se mantiene.
- [S54: P4C, tipo de mecanismo 0 y sincronización BIONZ](docs/capture/s54-conclusions.md):
  P4C (`CA_1ST_CURTAIN_START`) llega a BIONZ por `SENS_B` y `GPIO_9`; Darwin solo la escribe a 0, también sin mecanismo.
  El tipo 0 de A6000 equivale a Silent de A7S en exposición/ADC, no en reposición. Consumidor en BIONZ no localizado; S51 se mantiene.
  Ver también [P4C](docs/capture/s54-p4c-signal-trace.md), [BIONZ](docs/capture/s54-bionz-darwin-sync.md),
  [tipo 0](docs/capture/s54-mechanism-type-zero.md), [IMX210](docs/capture/s54-imx210-electronic-exposure.md) y
  [cronología](docs/capture/s54-capture-timeline.md).
- [S53: parser CAIF de Darwin, A7S vs A6000](docs/capture/s53-conclusions.md):
  el paquete ev1 llega por MFS5 (ID `0x0c`, 22 B); el parser A7S consume el bit Silent `0x20` y deja de
  accionar las bobinas de cortina; el de A6000 lo descarta. Falta lógica en el firmware Darwin A6000; S51 se mantiene.
  Ver también [reconstrucción](docs/capture/s53-darwin-caif-reconstruction.md),
  [comparación](docs/capture/s53-darwin-a7s-a6000-comparison.md),
  [cortinas](docs/capture/s53-curtain-actuator-control.md) y
  [viabilidad](docs/capture/s53-a6000-silent-feasibility.md).
- [S52: mecanismo Silent Shooting A7S y viabilidad en A6000](docs/capture/s52-parallel-conclusions.md):
  la A7S no suprime el control de cortinas, lo marca como Silent (bit `0x20` en CAIF)
  y deja de esperar respuesta del MCU de obturador; cadena clase→ShutMode verificada
  por instrucciones. Decisión física en el MCU Darwin y semántica eléctrica del IMX210
  sin verificar; viabilidad en A6000 **NO VERIFICADA**, se mantiene S51 (no parchear).
  Ver también [cortinas](docs/capture/s52-a7s-curtain-trace.md),
  [propagación de clase](docs/capture/s52-shutmode-propagation.md),
  [IMX210/exposición](docs/capture/s52-imx210-electronic-exposure.md) y
  [viabilidad A6000](docs/capture/s52-a7s-a6000-feasibility.md).

- [S51: decisión SÍ/NO sobre exposición totalmente electrónica](docs/capture/s51-decision.md):
  A (¿ruta demostrada?) NO, B (¿evidencia para parchear?) NO, C (¿imposibilidad probada?) NO
  — falta de demostración, no prueba de imposibilidad. Decisión vigente: no parchear.
  Ver también [informe Codex T2/T3](docs/capture/s51-codex-t2-t3.md).

- [S50: conclusiones conjuntas Claude + Codex](docs/capture/s50-parallel-conclusions.md):
  **NO_VERIFICADO** una foto de resolución completa con exposición electrónica sin
  cierre de cortina mecánica; tampoco demostrada su imposibilidad. Nombres
  `CURTAINMODE`/`*_ELEC_SHUT` no prueban efecto eléctrico (ambos investigadores lo
  rechazan). Informes: [Claude](docs/capture/s50-claude-electronic-config.md) ·
  [Codex](docs/capture/s50-codex-exposure-curtains.md).

- [S49: productor de configuración de captura](docs/capture/s49-capture-config-producer.md):
  clave `0xce` = comando `S_IMAGER_CURTAINMODE`; tabla de servicios de `av-cam.bin`
  inicializada por `liro.ko`. Productores reales: puente USB/«Senser» de `libsencore.so`
  y cuatro funciones de `libObj.so`.

- [S48: proveedor del servicio de registro `+0x1ec`](docs/capture/s48-service-table-provider.md):
  wrappers `0x43561298/0x4356…b4/…324` resueltos; slots `+0x1e8/+0x1ec/+0x200` sin
  escritor en el blob — son importaciones que rellena el cargador/host, no `av-cam.bin`.

- [S47: entrada del payload y orden de C](docs/capture/s47-payload-producer-and-order.md):
  solicitud recibida en `0x43e95420` → payload `0x43ed4620`;
  callback antes de copia C, con `+94/+95` dentro del rango `0x1a4`.
  S48: productor anterior a `0x43789cc0`, registro `0x301d7`; hito abierto.

- [S46: base VD y escritor del contexto](docs/capture/s46-vd-base-and-context-identity.md):
  inicialización `0x43e16d2c=0xf3120000`, destino `0xf3120220`;
  callback `0x437dad78`, clave `0xce`, produce C+94/+95 desde dos u16.
  Antecedente; S47 resuelve entrada y orden. Productor original y efecto físico pendientes.

- [S45: contexto y consumidor real del timing IMX210](docs/capture/s45-context-identity-and-physical-closure.md):
  antecedente: contexto C localizado; virtual+74 consume IMX210+3a0 hasta
  escritura del controlador base+220. La base se resuelve en S46; alias P/C pendiente.

- [S44: consumidor de registros y tabla de modos](docs/capture/s44-register-consumer-mode-table.md):
  119 pares ID/valor llegan al backend de comandos y a MMIO; virtual+a8
  compara clases de modo. Productor local de byte+95=2 recuperado;
  alias con C y cierre físico pendientes.

- [S43: tabla PIC y códigos de modo IMX210](docs/capture/s43-exposure-mmio-and-lock-codes.md):
  registros preparados en memoria software, sin MMIO directo; las llamadas
  posteriores guardan estado. Cadenas refutan códigos de bloqueo AF y confirman
  selección de modos. Transporte físico y origen de clase2 siguen pendientes.

- [S42: identidad de la llamada de exposición](docs/capture/s42-exposure-call-identity.md):
  wrapper `436d6320` → slot virtual +28 → backend `436d6f6c`;
  productor de controles por copia y usos byte de clase2 contrastados.
  Origen del valor2, parser3023 y dependencia R+5cc todavía pendientes.

- [S41: productores de mensajes y snapshots](docs/capture/s41-message-origin-imx210.md):
  productores internos de `4000/4036`, tablas de valores y constructores de
  snapshots recuperados; frontera OSAL activa Línea C: selector EFCS y
  clase2 contrastados, sin fin electrónico demostrado. Origen `3023` PARCIAL.

- [S40: origen del contexto de modo](docs/capture/s40-context-origin-imx210.md):
  comandos API `4000/4036/3023` alimentan `+24/+48/+458`; copias de `0x560`
  bytes y tabla de despacho recuperadas. Semántica IMX210 y alias PARCIAL.

- [S39: enum de imagen y discriminador APL](docs/capture/s39-image-format-apl.md):
  tres consumidores convergen en detección de cambio y reinicialización;
  origen del enum con cuatro escrituras condicionales en VD_Pre.
  Formato de píxel/pitch y vínculo con opción de usuario/FPS sin cerrar.

- [S38: frontera DMM/OSAL en av-cam](docs/capture/s38-dmm-osal-static-frontier.md):
  blob LIRO sin resolución ELF; slot importado +0x2e4 cero en archivo.
  Pool 0x61003c compartido, servidor/escritor de extents sin recuperar.
  Próximo: enum de formato S33 hasta campos APL, stride y tamaño.

- [S37: definidor DMM en libmprctrl](docs/capture/s37-libmprctrl-dmm-extents.md):
  getters de extents DmmAccessPLA y paquete AllocDmmMemory resueltos;
  cliente OSAL 0x61003c y enlace exacto al PLT S30. Dominio físico/lógico,
  identidad del slot av-cam y productor físico YC todavía sin demostrar.

- [S36: memoria de libInfraScalarMpr](docs/capture/s36-libinfra-scalar-mpr-memory.md):
  `void**` devuelve un mapeo SysV usado para copiar datos still. Las dos APIs
  DMM son importaciones UND; backend av-cam y productor físico YC siguen abiertos.

- [S35: objetos DFE y frontera estática APL/IRQ](docs/capture/s35-dfe-objects-static-frontier.md):
  Ofmt/Ifmt y métodos virtuales resueltos; leen/activan SGC `0xfc0a…`, sin
  vínculo APL→IRQ→EC/LM demostrado. Frontera de esta vía agotada; siguiente:
  proveedor DMM importado `0x43561524` y consumidor real del handle YC.

- [S34: APL/DMA frente a VD e interrupciones](docs/capture/s34-apl-dma-vd-interrupts.md):
  programación y kick síncronos; evento Drive no acredita fin DMA. Registrador
  DFE y causas software resueltos; vínculo banco APL→IRQ→EC/LM y cuadro físico
  propio/siguiente aún sin demostrar.

- [S33: origen de los handles YC](docs/capture/s33-yc-rendezvous-producer.md):
  26 llamadas y 13 parámetros locales rastreados hasta handles Rendezvous;
  escritor secundario `0x43814ea0→input+0xd4=P+0xbc` identificado.
  Rama APL seguida hasta configuración MMIO; backend DMM, layout/pitch/formato
  y fin DMA físico pendientes.

- [S32: callbacks VD y SyncYCout](docs/capture/s32-vd-callbacks-sync-ycout.md):
  destinos de las listas Drive/Post resueltos; productor YC con handle DMM
  compartido. Dirección de píxeles, pitch/formato y fin DMA siguen sin cerrar.

- [S31: subsistema CAMERA_MAIN_SYNC/DFECore](docs/capture/s31-camera-main-sync-strings.md):
  hallazgo por cadenas (`strings`) de un motor de temporización VD del sensor
  no explorado en S16–S30 (centradas en libObj.so/libBizFw.so). Decompiladas 8
  funciones clave (`VD_Pre`→`VD_Sequence`→`VD_Post`→`VD_Drive`); acceso MMIO real
  verificado a `0xf3c30110–0xf3c3015c`. Candidato más cercano al productor YC
  sin dirección de píxeles/plano/pitch/fin DMA. Superado por S32.

- [S30: receptor y retorno de EncodeStill](docs/capture/s30-pipelines-capture-encode.md):
  InfraAvbbc→InfraStillEncoder→SDF, espera hasta completion y continuación a Pool.
  CaptureId no es un descriptor YC; captura nueva sin cortinas y contrato DMA/caché
  del YC siguen abiertos. Auditoría estática: 12 comprobaciones.

- [Avance Darwin y control del obturador](docs/capture/darwin-state-machine.md):
  tablas de fases reconstruidas, notificación y escrituras comparadas;
  viabilidad de obturación totalmente electrónica A6000 aún sin demostrar.

- [Alcance general y dos líneas de trabajo](docs/project-scope.md).
- [Línea A: arquitectura general](docs/architecture/README.md).
- [Línea B: pipeline de captura](docs/capture/README.md).
- [Inventario físico documental](docs/hardware-inventory.md): 16 bloques y preguntas,
  con identificación de chips pendiente.
- [Atlas ELF](docs/elf-classification.md): 679 rutas ARM, 641 contenidos únicos;
  147 ejecutables, 469 bibliotecas candidatas y 63 módulos. 391 asociaciones
  funcionales todavía desconocidas.
- [Mapa de dependencias](docs/subsystem-dependencies.md): 3890 DT_NEEDED,
  incluidas 8 resoluciones ambiguas. Datos completos: reports/elf-atlas.json.
- [Arranque y recuperación](docs/boot-and-recovery.md): evidencia inicial y
  preguntas; recuperación de hardware no demostrada.

La carpeta conserva el nombre histórico para mantener válidas las rutas de
REA y las evidencias. No se movió ni eliminó firmware o investigación anterior.

## Estado del subproyecto de obturador

Comparación activa: [A6300 2.01 frente a A6000 3.21](docs/capture/a6300-silent-comparison.md).
Referencia comparativa vigente desde 19-10-2026: **A7S 3.20** (instrucción del usuario; sustituye a A6300 2.01, que queda como histórico). Ver [manuales de servicio](docs/references/a7s-vs-a6000-service-manuals.md).
Se identificaron modos y callbacks específicos de Silent en A6300; el modo
`0x4e` de IMX284 es rechazado por el controlador IMX210 de A6000.
Los selectores se comprobaron con 14 casos de emulación de instrucciones.
El [ajuste y sus respuestas de software](docs/capture/a6300-silent-software.md)
se han seguido separadamente de la captura física.
Se reconstruyó además la [selección Silent del paquete CAIF](docs/capture/silent-caif-transport.md)
hasta el transporte de sus 31 bytes; falta identificar su interpretación física.
Una ruta omitida por Silent quedó identificada como
[contabilidad de eventos KikiLog](docs/capture/silent-kikilog.md), con
receptor comprobado por REA; se descarta como prueba de control de cortinas.
Esto impide trasladar directamente esa opción y no demuestra una limitación
del silicio. La investigación continúa; no hay parche funcional validado.

**EFCS reconstruido: [selector de captura e IMX210](docs/capture/efcs-capture-selector.md).**
Se identificó la copia entre bancos que transporta EFCS, su selección de clase
y la copia al byte +9 recibido por SetExposure, con sus condiciones de backend.
La clase 2 sigue sin interpretación física suficiente para activar SilentShutter.
Base anterior: [exposición IMX210 y transferencia P2S](docs/capture/imager-exposure-p2s.md).
Se siguieron el coordinador de exposición, la selección por bancos, los métodos
SetExposure/SetRead y las escrituras del transporte P2S. Se corrigieron entradas
de función y se descartó un falso lector de Silent por identidad de estructura.
[Consumidores y correcciones E018](docs/capture/silent-imager-consumers.md).
El proyecto Ghidra conserva más de 37000 funciones registradas; el análisis amplio
terminó por tiempo, por lo que ese número no acredita cobertura completa.
Las exportaciones de funciones conservan el hash del firmware original.

[Ruta de configuración y receptor LIRO](docs/capture/silent-shutter-status.md):
Se verificaron factory, CamMgr, Off/On y cola 0x30001; av-cam.bin recibe tipo5,
despacha 0x40e3 y guarda el modo. Tabla de 220 comandos reproducible. El blob
contiene un controlador IMX210 candidato; funciones conservadas en un
proyecto Ghidra persistente. Todavía no hay vínculo probado entre ese estado
y el fin electrónico de exposición: no hay parche funcional ni viabilidad cerrada.

Prioridad actual del usuario: **EFCS y posible cortina trasera electrónica**.
Se localizaron acciones, secuencias, despacho a conversores y envío OSAL
separados para EFCS y SilentShutter. El éxito de envío no demuestra final de
exposición. [Informe principal y comparación de métodos](docs/capture/shutter-investigation.md).
También se verificó el caso 0x1008 del coordinador y se documentaron eventos
de captura/AutoReview en el [pipeline parcial](docs/capture-pipeline.md).
La lectura electrónica completa y el receptor físico permanecen abiertos.
El transporte se acotó hasta /dev/uipc y el encolado del núcleo; hay una cola
0x30001 cuya correspondencia estática con el receptor quedó resuelta en E016.

Al 15-10-2026: **categoría E, evidencia insuficiente**. Extracción oficial 3.21
e inventario realizados; no hay parche ni viabilidad demostrada. Esta categoría
solo corresponde al subproyecto, no limita la investigación general.

Avance con REA tras el reinicio: constructor y dos opciones On/Off de SilentShutter
identificados en CautionConfig.so; rama de conversión de mensajes localizada en
libObj.so. El diagnóstico NON SUPPORTED rechaza ciertos mensajes; no demuestra
imposibilidad por hardware. Tampoco se demuestra soporte funcional en A6000.
Evidencias y limitaciones: [traza SilentShutter](docs/silent-shutter-trace.md).

Último avance de captura: [S29, WriteStill de entrada a cierre](docs/capture/s29-writestill-end-to-end.md): orden `0x10000003`, escritura, retorno RecStill→FEA→Obj, cierre del Pool y respuesta `0x10000004`. SetImageWrited corresponde a `0x6108/0x1007`, no `0x1009`. El cierre de software no acredita durabilidad física ni SilentShutter.

[S28, contrato de pines YC](docs/capture/s28-osal-pin-contract-closure.md): InfraImaging sirve `0x50004`; VEF y ScalarInfra identificados. Las cuatro propiedades del pin no son una imagen para WriteStill.

Resultados: `docs/findings.md`, `docs/feasibility-report.md`; continuidad: `CONTEXT.md`.
Original Sony conservado en `firmware/original/`; fuentes públicas fijadas en `reports/source-revisions.json`. No publicar `firmware/` ni las copias locales de fuentes sin revisar sus licencias. No se accedió a una cámara.

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

## Sesión 19 — seguimiento de conectividad

S19-02 verificó el salto efectivo `UObjPin::Connect`/`ConnectPinWrapper` hacia
`MWF::ObjPin::Connect`, incluido el comportamiento de validación genérico. La
instancia LifeCycle creada por `TM::createLifeCycles` sigue sin una arista de
ejecución demostrada hasta ese salto; esto no acredita SilentShutter funcional.
Detalle reproducible: [S19-02 LifeCycle/Connect](docs/capture/s19-lifecycle-connect.md).

S19-03 corroboró que el extremo ObjId 53 de la topología `0xb4` corresponde a
la clase `ObjStillRecorder` por su constructor exportado y sus pines, pero no
recuperó su auto-registro dinámico. No hay evidencia de SilentShutter funcional.
Detalle: [S19-03 ObjId 53](docs/capture/s19-objid53-registration.md).

S19-04 verificó que `ObjCamera` construye nueve pines de salida y que la fila
`0x0a` enlaza Camera.out0 con Effect.in0, pero no encontró un descriptor DMM o
`AvbbcPhycMem` atribuible a ese YC. El par DMM conocido es de Effect/PbCap y la
SDS de `0x800` B no es raster. El contrato real de Live View continúa pendiente;
no hay evidencia de SilentShutter funcional. Detalle:
[S19-04 contrato YC](docs/capture/s19-camera-yc-real-contract.md).

S19-11 verificó que ObjEffect acepta los valores de modo efectivos 2–5, pero
sólo 3 intenta `0x3900/0x0002`; 2/4/5 retornan por error. No es la ruta PbCap
ni demuestra una condición de obturación electrónica. Detalle:
[S19-11 modos ObjEffect](docs/capture/s19-objeffect-modes-2-5.md).

S19-05 confirmó el ciclo interno PbCap de ObjEffect/SDF (precondiciones,
conexión de infraestructura, buffers de salida, entrega y cleanup), pero no
una ruta Camera→SDF ni compatibilidad del YC real de Camera. La SDS no es
raster y la ausencia de un único guard de tipo no prueba aceptación. No hay
evidencia de SilentShutter funcional. Detalle:
[S19-05 ObjEffect/SDF](docs/capture/s19-camera-effect-sdf.md).

La tabla LIRO de captura quedó inventariada hasta sus diez variantes no
seleccionables; son secuencias convencionales con estados/retry, sin prueba de
adquisición electrónica o Silent. Véase
[S19-07](docs/capture/s19-liro-remaining-sequences.md).

S19-09 reconstruyó la frontera `CameraSequence → SDCom → ScalarDaemon` y el
ciclo ticket/memoria compartida/`release` del cliente, sin demostrar JPEG,
640×480, YC, S2, MPR ni SilentShutter. Véase
[S19-09 CameraSequence/SDCom](docs/capture/s19-camerasequence-sdcom.md).

S19-13 separó la emisión RelMgr de `0x3015`, la limpieza local del dispatcher
y la limpieza LIRO de `ctx+0x754`; no vinculó esos hechos a idle, liberación
DMM, CAIF/Darwin ni una ventana segura antes de cortinas. Véase
[S19-13 cancelación posterior a S2](docs/capture/s19-post-s2-cancellation-states.md).

S20 — **VERIFICADO:** recuperados llamadores DCF, registro JPEG/contenido en
la variante AVI y callback `0x40000012`; **NO_VERIFICADO:** cadena completa de
una solicitud, rollback y persistencia SD/reproducción. Véase
[cadena MPR/DCF posterior a WriteStill](docs/capture/s20-codex-mpr-dcf-chain.md).
Se mantiene **A > E > P ≈ E2**; SilentShutter no se declara funcional.

S21 Codex — **VERIFICADO:** pre-registro condicional anterior a WriteStill,
unión Recorder/RecStill → StillWriterFilter y ramas JPEG/RAW. **NO_VERIFICADO:**
completion FEA completa, rollback DCF y primera visibilidad en reproducción.
Véase [exposición → biblioteca](docs/capture/s21-codex-exposure-to-library.md).

S22 separa la serialización LIRO del productor físico de un YC nuevo: el
primero está comprobado, el segundo no. Informe:
[sensor → YC para StillRecorder](docs/capture/s22-sensor-to-yc.md).
Auditor estático: 194 PASS; **A > E > P ≈ E2** sin cambios.
SilentShutter no se declara funcional.
