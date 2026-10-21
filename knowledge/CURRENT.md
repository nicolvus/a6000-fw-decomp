# Estado actual — léeme primero

Resumen operativo breve. Para el historial completo de decisiones, ver `knowledge/PROGRESS.md`.
Para restricciones del proyecto (sin firmware ejecutado, sin flasheo, sin `git push`), ver `docs/STATE.md`.

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
