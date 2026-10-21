# S81 — ADF: el framework de arranque, colas de mensajes y gestor de memoria del firmware

**Alcance:** línea de ingeniería inversa **general** de la cámara: el **framework base** del
`av-cam.bin` (A6000 fw3.21) que se ve en el prefijo de traza `[ADF]`: arranque, reenvío de
mensajes, colas de mensajes (MSGQ), gestor de memoria (MMGR) y la interfaz de **comandos de
depuración** (`[ADF][DBGCMD]`). No es la línea SilentShutter, ni la montura (S66), ni el AF, ni
ADJ_CMD, ni ZPD (S75), ni ZIT (S80), ni el pipeline (S76).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s81_adf.py`.

---

## 1. Qué es ADF (VERIFICADO)

`ADF` es el **módulo más grande del firmware por número de trazas**: **1220** cadenas empiezan por
`[ADF]` en la A6000 (1269 en la A7S fw3.20), con 1231 apariciones del prefijo en total. Reparto por
sub-niveles (A6000): raíz `[ADF]` 934, `[ADF][DBGCMD]` 102, `[ADF][ERR]` 70, `[ADF][SYSND]` 27,
`[ADF][ADJ]` 24, `[ADF][SAN]` 23, `[ADF][OUT]` 15, `[ADF][ADF]` 11, `[ADF][SYS]` 3, `[ADF][INIT]` 2,
`[ADF][DEBUG]` 2, `[ADF][GS]` 2, `[ADF][AFNR]` 2, `[ADF][FACE]` 2, `[ADF][CH_SRC]` 1.

## 2. El arranque (VERIFICADO)

| traza | dirección | qué dice |
|---|---|---|
| `[ADF]BootInit` | `0x43c26366` | inicio del arranque |
| `[ADF]InitWaitVsync SelectCompo msgId %x` | `0x43c26375` | **espera de vsync** y selección de *componentes* (`SelectCompo`) |
| `[ADF]InitWaitVsync SelectCompo NoMSGQ  %x` | `0x43c2639e` | no hay cola de mensajes para ese componente |
| `[ADF][INIT]AVIO INIT COMP` | `0x43c263f6` | fin de init del **AVIO** |
| `[ADF][INIT]AUDIOIP INIT COMP` | `0x43c26411` | fin de init del **AUDIO IP** (→ S69) |
| `[ADF]BootExit` | `0x43c263c9` | fin del arranque |

**Reenvío de mensajes** (pérdida de mensajes durante el arranque): `[ADF]INIT Resend MsgqNum 0x%x`
(`0x43c263d8`), `Resend header cateId %x msgId %x msgLength %x version %x` (`0x43c2642f`), `Resend
param %x` (`0x43c26474`), `Resend to Adf src %x reply %x msgId %x` (`0x43c2648f`), `Resend No Fifo
Data` (`0x43c264c1`), `Resend Err %x` (`0x43c264e1`).

**Configuración del IP de audio** (VERIFICADO, enlaza con S69):
`[ADF]AUDIO_IP_CONFIG_TYPE_VGS` (`0x43c264fa`), `_PR` (`0x43c26518`), `_MF` (`0x43c26535`),
`_BANDI_BASEDON_CONS` (`0x43c26552`), `_CONS` (`0x43c2657f`), `_BANDI` (`0x43c2659e`).

## 3. El gestor de memoria (MMGR) (VERIFICADO)

`[ADF]MMGR COMM INFO` (`0x43c265ce`) con la estructura
`indexNo, unitType, handle, allocNum, openNum` (`0x43c265e3`) y sus valores
(`0x43c26618`), `Total Info Num %x` (`0x43c26638`),
`AdfMemMgrCtrl::SetMemMgrCommResult err2 %x %x %x %x` (`0x43c26652`),
`[ADF]FreeUnit Handle=0` (`0x43c266bd`) y `[ADF]ExecDummySubsystem mId uT op uH %x %x %x %x`
(`0x43c2668c`).

## 4. Las colas de mensajes (MSGQ) (VERIFICADO)

Modelo: cada mensaje lleva **identificador de origen** (`srcId`), **id de mensaje** (`msgId`) y
**id de respuesta** (`replyId`):

- `[ADF]MSGQ Set:srcId %08X ,msgId %08X` (`0x43c26788`) — inserción.
- `[ADF]MSGQ Get:msgId %08X` (`0x43c267d5`) — extracción.
- `[ADF]MSGQ SendImmediateComp msgId:%x replyId:%x` (`0x43c268a8`) — envío inmediato con respuesta;
  `NoComp msgId:%x` (`0x43c2687c`) y `MsgId No Hit, msgId:%X, replyId:%X` (`0x43c268d8`).
- `[ADF]MSGQ ClearAllComp MsgNum = 0x%X` (`0x43c2691c`).
- Errores: `[ADF][ERR]MSGQ::Set err %x` (`0x43c2676d`), `MSGQ::Get m_msgqCount minus!`
  (`0x43c267ae`), `MSGQ::Get GetMsg Err %x` (`0x43c267ef`), `MSGQ::Get ReceiveASync Err %x`
  (`0x43c26811`).
- **Colas de grupo**: `[ADF]MSGQ_GID_HOTSHOE_INFRA1<-SetInput` (`0x43c266e6`),
  `<-SetOutput` (`0x43c2670d`), `<-ILLEGAL(CateId=%x,MsgId=%…)` (`0x43c26735`) → existe al menos un
  **grupo de colas del flash hotshoe** (`HOTSHOE_INFRA1`).

## 5. La interfaz de comandos de depuración (DBGCMD) — 102 comandos (VERIFICADO)

Todos empiezan por `[ADF][DBGCMD]` en `0x43c2a443`–`0x43c2b315`. Agrupados por dominio:

| dominio | comandos (muestra) |
|---|---|
| **System** | `ClearExecTime`, `ClearCompMSGQ`, `ClearMSGQ`, `CountMSGQ MsgqNum = %d`, `SetMSG`, `GetMSGQ`, `GetMSGQ V`, `GetMSGQ Scenario Done`, `SetMSG V`, `BootExit`, `AdfBootExit`, `AudioIpBootExit`, `GetMemMgrComm` |
| **Medida de tiempo de CPU** | `CPU2 ExecTime 60Hz max m/s 0x%x 0x%x` (`0x43c2a465`), `CPU2 ExecTime 60Hz over m/s` (`0x43c2a497`), y los de 48 Hz (`0x43c2a4ca`, `0x43c2a4fc`) → **el framework mide el tiempo de ejecución del ciclo de 60 Hz y de 48 Hz en la CPU2** |
| **Input** | `SetInput`, `SetInputContinue2/3/4`, `SetExtType`, `SetRefLevel`, `SetZoomLink`, `SetLowCut`, `SetUnderWater`, `SetRecLevel`, `SetReverseLR`, `SetAdjThrough` |
| **InputPro** | `SetIntMicSens`, `SetInputType`, `SetInputTrim`, `SetChSource`, `SetRecLevelMode`, `SetAgcLink`, `SetManualGainLink`, `SetRecLevelLimitter` |
| **Output** | `SetOutput`, `SetOutputContinue2/3/4`, `SetOutputContInternal`, `DetectJack`, `SetHdmiFormat`, `SetAntiClipping`, `SetSpSwap` |
| **OutputPro** | `SetHpMonitor`, `SetHpOut`, `SetAdjI2sMute` |
| **Proc (fases lineales del arranque)** | `SetLinearPhase`, `LinearPhaseMemPrint`, `LinearPhaseSetDec0/Dec1Print`, `LinearPhaseSetAip0/Aip1Print`, `LinearPhaseGetSa0/Sa1Print`, `LinearPhaseGetPin0/Pin1Print`, `LinearPhaseSetMbPrint`, `LinearPhaseSetSaPrint`, `LinearPhaseNomatch0/1Print` |
| **Proc (ruta de audio y zoom)** | `SetPath`, `SetMixRatio`, `GetMixRatio`, `SetFader`, `SetZoomNr`, `ProcGetZoomInfo`, `ZOOM[0]/[1]/[2] (v,p,s,f)` |
| **SystemSound** | `SetTable`, `SetPath`, `Request`, `SetVol`, `SetNotify`, `RequestPin`, `RequestPinConnetct/DisConnetct` |
| **SoundAnalyzer** | `StartGolfShot` (`0x43c2b143`), `StopGolfShot` (`0x43c2b16c`), `AnalyzeGolfShot` (`0x43c2b194`), `SetSoundAnalyze` (`0x43c2b1bf`) → **análisis de sonido para el disparo de golf** (→ módulo `GOLFSHOT`, 65 trazas) |
| errores | `arg err` (`0x43c2a61e`), `illegal argument number` (`0x43c2aae4`), `BAR ARG!!` (`0x43c2af69`), `ILEGAL PARAM` (`0x43c2afc5`) |

**Fases lineales (INFERENCIA):** el arranque es una secuencia de fases (`SetDec*` → `SetAip*` →
`GetSa*` → `GetPin*` → `SetMb` → `SetSa`), es decir, una **máquina de estados lineal** de
inicialización.

## 6. Diferencial A7S fw3.20 (VERIFICADO)

La A7S tiene **1269** trazas `[ADF]` (frente a 1220) y **110** comandos DBGCMD (frente a 102): la
fw3.20 tiene *más* superficie de depuración, coherente con que la fw3.21 de A6000 reorganizó la
traction de `CAMERA_MAIN_*` (S79).

## 7. Abierto (NO_VERIFICADO)

- Qué significan exactamente `ADF`, `MMGR`, `Compo`, `AIP`, `MB`, `SA` en este contexto (salvo
  `AIP` = Audio IP por `AUDIOIP INIT COMP`).
- El **formato del mensaje** (cabecera `cateId/msgId/msgLength/version`, `srcId`, `replyId`) y la
  tabla de destinos.
- La lista completa de grupos `MSGQ_GID_*` (solo se ha visto `HOTSHOE_INFRA1` en las trazas).
- Qué hace exactamente `ADF][ADJ]`, `ADF][SAN]`, `ADF][SYSND]`, `ADF][GS]`, `ADF][AFNR]`,
  `ADF][FACE]`, `ADF][CH_SRC]`.
- Cómo se invocan los comandos DBGCMD (¿mismo `DBGCMD` de `scripts/`? ¿telenet?).

## 8. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s81_adf.py -q
```
