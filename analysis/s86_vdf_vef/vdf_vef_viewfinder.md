# S86 — El subsistema del visor: `VDF` (marco de display) y `VEF` (visor electrónico)

**Alcance:** línea de ingeniería inversa **general** de la cámara: los dos módulos que gobiernan el
visor de la A6000 (fw3.21): **`VDF`** (Video Display Framework, 243 trazas, ~200 clases RTTI) y
**`VEF`** (visor electrónico, 149 trazas). No es la línea SilentShutter, ni la montura (S66), ni el
AF, ni ADJ_CMD (S73), ni ZPD (S75), ni ZIT (S80), ni ADF (S81), ni el API del SA (S84), ni
VPH/CLK_CTRL (S85), ni las caras (S71).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s86_vdf_vef.py`.

---

## 1. `VDF` — el marco de trabajo del display (VERIFICADO)

### 1.1 La arquitectura (clases RTTI, direcciones de sus nombres)

- **Núcleo**: `VDF::SubsystemMain::Main()` (`0x43c8221b`),
  `VDF::SubsystemMain::SendCommandOsal(OSAL_ID, void*, __uint32_t)` (`0x43c8224a`),
  `VDF::SubsystemMain::SendResponseOsal_stock(...)` (`0x43c8229e`),
  `VDF::SubsystemFactory::ExecCmd(const VDF::VDF_MSG_INFO*, OSAL_ID, OSAL_ID, __uint8_t)`
  (`0x43c83b7f`), `VDF::ComponentFactoryBase` / `ComponentFactoryIf` / `SystemFactory`
  (`0x43c83bea`–`0x43c83c38`).
- **Framework de mensajes**: `VDF::MsgAccessor` (`GetReceiveCateId`, `GetReceiveVersion`,
  `GetReceiveSrcId`, `GetReceivePayload`, `GetReceivePayloadSize`, `GetReceiveMsgId`,
  `GetReceiveMsgLength`, `ExecTrigger`, `SetContinue`, `SetContinueReceive`, `SetTriggerType`),
  `VDF::MsgIterator` (`SendCommandOsal`, `SendResponseOsal`, `SendPinOsal`, `SetStatus`,
  `SetCounter`, `ForceClearTriggerType`), `VDF::MsgQueueIf`, `VDF::WaitQueue` (`Enqueue`/`Dequeue`/
  `ExecTrigger`/`ExecReceive`), `VDF::Trigger`, `VDF::CmdBase`, `VDF::CmdIf`.
- **Cmds del sistema** (`VDF::SystemCmd*`): `PinConnect` (`0x43c83fd5`), `PinRequestConnect`
  (`0x43c8405b`), `PinSend` (`0x43c84318`), `PinGet` (`0x43c85f18`), `PinDisconnect` (`0x43c85e40`),
  `PinRequestDisconnect`, `PinSendComp`, `PinGetComp`, `PinConnectComp`, `PinDisconnectComp`,
  `Trigger`, `Receive`, `Sysv`, `Debug`, `CipaModeOut`, `NotifyDisplayInfoReady`, `Init`.
- **Cmds de display** (`VDF::VdfDisplayCmd*`): `SetPanelOut` (`0x43c8714a`), `SetLineOut`,
  `SetPanelBrightness` (`0x43c86eea`), `SetPanelBrightnessSlope` (`0x43c86836`), `SetPanelColor`
  (`0x43c86863`), `SetPanelColorTemperature` (`0x43c86886`), `SetPanelLRMix` (`0x43c868b4`),
  `SetPanelReverse` (`0x43c86dd3`), `SetPanelResolution` (`0x43c86cbb`), `SetPanelSaving`
  (`0x43c86df8`), `SetPanelOsdLuminance` (`0x43c86a56`), `SetOsdAlpha` (`0x43c866ef`),
  `SetParallax` (`0x43c86e1c`), `SetDetectExtEvf` (`0x43c862b9`), `SetDetectExtPanel`
  (`0x43c86365`), `SetDisplayQuality` (`0x43c86417`), `SetHdmiInput`, `SetOutputColorimetryPolicy`
  (`0x43c86806`), `GetPanelOut`, `GetPanelBrightness` (`0x43c86209`), `GetPanelColor`,
  `GetPanelAspect`, `GetPanelLRMix`, `GetLineOut`, `GetLineLRMix`, `GetExtEvf`, `GetProjector`.
- **Cmds de entrada** (`VDF::VdfInputCmd*`): `UpdateYuv` (`0x43c888ef`), `UpdateYuvPin`
  (`0x43c89169`), `UpdateOsd`, `UpdateOsdYuvIndex`, `UpdateFaceFramePin` (`0x43c887e9`),
  `UpdateTimeCodePin`, `UpdateTimeCodeOnOffPin`, `UpdateAirTouchFramePin` (`0x43c8861c`),
  `SetOsdArea` (`0x43c88066`), `SetOsdAreaOnOff`, `SetOsdOnOff`, `SetYuvLayout`,
  `SetYuvLayoutOption`, `SetYuvMute`, `SetYuv2DTo3DMute`, `SetShutterMute`, `SetDeepMute`,
  `SetHdTrimming` (`0x43c87eec`), `SetBlackFrameNotify`, `SetImageDimensionInfo`, `GetBlackFrame`,
  `GetOsdLayout`, `GetYuvLayout`, `GetYuvReadStart`, `EscapeDispMem`, `ReleasePinAndMem`,
  `FocusInfoPin`, `OsdCommandBreak`, `OsdCommandExec`, `OsdMute`.
- **Cmds de servicio** (`VDF::VdfSrvcCmd*`): `SetGridLine`, `SetZebra` (`0x43c8ad68`),
  `SetPeaking` (`0x43c8acb7`), `SetHistogram` (`0x43c8aaad`), `SetFaceFrame` (`0x43c8a979`),
  `SetFaceFrameCommonDesign`, `SetFaceFrameOptionDesign`, `SetFocusLockFrameInfo`,
  `SetEvfParallax`, `SetEvfTempInfoEvent`, `SetKeyStoneAdjust`, `SetLiveDemo`, `SetLiveDemoPin`,
  `SetLiveDemoSwapTrigger`, `SetPanelZoom`, `SetTimeCode`, `SetYcRecControl`, `SetYuvCaution`,
  `SetColorEffect`, `SetEmergencyEvent`, `DrawOsdForceStopper`.
- **Rutas de imagen** (`VDF::VdfPath*`): `SetPath` (`0x43c89fca`), `ThroughTransfer`,
  `ResizeTransfer`, `LimitCopyTransfer`, `4KResizeTransfer`, `4KThroughResizeTransfer`,
  `QfhdThroughTransfer`, `IdleTransfer`, `IdleFreeTransfer`, `GetOsdMix`, `SetOsdMix`.
- **Memoria e imagen**: `YuvIndexDoubleBuffer` (`0x43c817b5`), `YuvIndexQfhdMemoryManager`
  (`0x43c878b5`), `YuvWorkMemCloseFreeProcessor`, `VfxRgba8888ToYuv422Processor` (`0x43c8bf52`),
  `RcForEoFramePackingProcessor`, `RcResizeForQfhdProcessor`, `OsdImageSequence`.
- **Dispositivos**: `VDF::EoLineDevice` / `EoPanelDevice` / `LRMixDevice` (y sus implementaciones
  nulas `VdfNullEoLineDevice`, `VdfNullEoPanelDevice`, `VdfNullLRMixDevice`),
  `VDF::MirrorSubsystemSynchronizer` (`0x43c84c0c`), `VDF::VdfNullSynchronizer`,
  `VDF::LineStatusSolver` / `LineStatusSingleSolver`, `VDF::EoLineParallaxRepeater`.
- **Utilidades**: `VDF::VdfDefineConverter::ConvVfxUcTag2ManageInfoNo` (`0x43c83ed8`),
  `VDF::PerformanceCountAccumulator`, `VDF::DebugExecCountMonitor`, `VDF::UTimerPerformanceCounter`,
  `VDF::ThreadMonitorFootprint`, `VDF::VdfSafeMemoryReleaser`, `VDF::VdfDataStructureSnapshot`,
  `VDF::OsalMsgDumpStream`, `VDF::LogOutputStream`, `VDF::CLogFactory`.

### 1.2 El puente con el hardware de vídeo (VPH) — VERIFICADO

VDF **traduce** sus comandos al vocabulario de `VPH_API` (S85):
`VDF::VdfDisplayCmdSetPanelOut::VphSetZebraCall` (`0x43c87294`),
`::VphSetPeakingCall` (`0x43c872f9`), `::VphSetTimeCodeCall` (`0x43c87360`),
`::VphSetPanelDepthCall` (`0x43c870e0`), `::VphSetPanelOsdLuminanceCall` (`0x43c8706f`),
`VDF::VphUpdateYuvFunction` (`0x43c85017`, RTTI `N3VDF20VphUpdateYuvFunctionE`), `VDF::VphBlackFrameFunction` (`0x43c84ff9`),
`VDF::YuvIndexVphYuvMuteFunction` (`0x43c850b8`), `VDF::DrvCallVphLatestCmdHolder`
(`0x43c8305e`, RTTI `N3VDF29DrvCallVphLatestCmdHolderImplE`).
Trazas: `[VDF] CallVphUpdateYuv size_x(%d) size_y(%d)` (`0x43c82fd7`),
`[VDF]vph_set_yuv_mute_immediately ON/OFF sel=%d` (`0x43c83004`/`0x43c83031`),
`[VDF] adjust BigImage Line Layout %d %d !!!!` (`0x43c82f27`) y su gemelo **Panel** (`0x43c82f53`).

### 1.3 El enlace con ADF, con el bus SSBI y con CLK_CTRL — VERIFICADO

- `VDF::VdfToAdfYcDataSender` (`0x43c86165`, RTTI `N3VDF20VdfToAdfYcDataSenderE`) → VDF **envía los datos YC al framework ADF** (S81).
- `VDF::SusRes` (suspend/resume) usa el **bus SSBI** del display: `ssbi_read(%x)` (`0x43c814f0`),
  `ssbi_write(%x)` (`0x43c81547`), `Backup_write_vsize(%x)` (`0x43c813fc`),
  `Backup_read(%x)` (`0x43c81429`), `Backup_read(BKID_UPM_BOOT_CIPA_FLAG)` (`0x43c82329`) →
  el estado del display se guarda en el almacén BK4 con la marca **CIPA**.
- `VDF::CheckUpdateYuvTiming(VDF::VDF_PRM_SUBSYSTEM_CLKCTRL_INFO)` (`0x43c847d1`),
  `VDF::IsCallVphMode(VDF::VDF_PRM_SUBSYSTEM_CLKCTRL_INFO, VPH_ENUM_MODEID, ...)` (`0x43c8482c`),
  `VDF::HtpVfcMainPerformanceCounter` (`0x43c855f1`, RTTI `N3VDF28HtpVfcMainPerformanceCounterE`), `VDF::HtpVfcSubCheckPoint` (`0x43c85616`) →
  VDF **depende del control de reloj** (S85) para saber cuándo refrescar.

### 1.4 El enlace con la detección de caras (S71) — VERIFICADO

`VDF::VdfInputCmdUpdateFaceFramePin` (`0x43c887e9`), `VDF::UpdateFaceFrameNormal` (`0x43c8880f`),
`VDF::VdfFaceFrameUtility::UpdateFaceFrameNormal` (`0x43c8c014`),
`VDF::VdfSrvcCmdSetFaceFrame` (`0x43c8a979`), `::SetFaceFrameCommonDesign` (`0x43c8a998`),
`::SetFaceFrameOptionDesign` (`0x43c8a9c3`) → el **marco de cara** que se dibuja en el visor lo genera
el subsistema FC (S71) y lo entrega a VDF, que a su vez lo pasa a VPH (`<faceframe_on>`,
`<update_faceframe>`, `<faceframe_color>` de S85).

## 2. `VEF` — el visor electrónico (VERIFICADO)

- **Espejo**: `[VEF] reply_osal_id=%#x, mirror_osal_id=%#x` (`0x43c8c36e`),
  `[VEF] my_osal_id=%#x, mirror_osal_id=%#x` (`0x43c8c39a`) → el EVF y el panel son **espejos**
  (subsistema "mirror": `VDF::MirrorSubsystemSynchronizer`).
- **Modos**: `[VEF][RE] SystemCmdNotifyMode::Execute 3D Mode` (`0x43c8d5cf`),
  `2D Mode` (`0x43c8d5ff`), `INIT Mode` (`0x43c8d62f`), `Invalid mode(Error)!!!` (`0x43c8d661`) →
  el visor trabaja en modo **3D / 2D / inicialización**.
- **Multicast de infraestructura** para pausar el visor: `Receive InfraMulticast PauseNotify`
  (`0x43c8d10d`), `PauseReleaseNotify` (`0x43c8d0dd`), `RegistComp`/`UnregistComp` y sus equivalentes
  de envío (`0x43c8d188`–`0x43c8d20f`).
- **Salida de vídeo**: `[VEF] DOWNCON: PAL 50i50p` (`0x43c8d394`), `PAL 25p` (`0x43c8d3ae`),
  `NTSC 60i60p` (`0x43c8d3e8`), `NTSC 30p24p` (`0x43c8d403`),
  `[VEF][ERROR] Invalid clk_rate (%d)` (`0x43c8d3c5`) → **down-conversion de la señal de vídeo** a
  formatos PAL/NTSC (salida por HDMI/composite).
- **Cancelación de efectos sincronizada con el VFC**:
  `VefEffectCmdEffectCancel::Activate - VFC Sync!!!` (`0x43c8dc56`),
  `Execute - currentVfc(%d) >= targetVfc(%d)` (`0x43c8dcfd`), `Execute COMP_WAIT`/`COMP_SEND`
  (`0x43c8dc91`/`0x43c8dcc7`).
- **Memoria**: `[VEF]Map Area alloc %x err` (`0x43c8d310`),
  `[VEF] free DMM_UNITTYPE_DATEREC_WORK_YC` (`0x43c8da6b`) → el visor **toma prestado el bloque de
  trabajo YC del datarec**.
- **Rendimiento**: `[VEF] exec time max = %x, ave = %x` (`0x43c8d56b`).
- **Mensajes con identidad única**: `MsgInfoUniqueIdImplanter::Implant uniqueId = %d`
  (`0x43c8c6b7`), `SetSubComp` (`0x43c8c73c`).

## 3. Abierto (NO_VERIFICADO)

- Qué es exactamente el modo "3D" del visor (¿la pantalla del EVF en 3D?).
- El formato de los mensajes de VDF (`VDF_MSG_INFO`, `CATE_ID`, `MSG_ID`, `TRIGGER_TYPE`).
- Cómo se implementa el "espejo" entre EVF y panel (qué datos se duplican).
- Qué efectos de vídeo (`VefEffectCmd*`) existen aparte de la cancelación.
- Si `VDF` es el mismo framework que el `VDF` citado en S16-S18 (docs de YC/SDF) o una versión
  distinta.
- La implementación de `VphBlackFrameFunction` y `VfxRgba8888ToYuv422`.

## 4. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s86_vdf_vef.py -q
```
