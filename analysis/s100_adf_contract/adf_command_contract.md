# S100 — El contrato de comandos del ADF: 90 comandos de depuración y el canal `AdfCh` del userland

**Alcance:** línea de ingeniería inversa **general** de la cámara: la **interfaz de control** entre el
userland (Linux) y el framework **ADF** del firmware (`av-cam.bin`). Es la culminación de S81 (los
comandos DBGCMD), S91 (los submódulos ADF) y S98 (el puente `libBizFw.so`). No es la línea
SilentShutter, ni la montura (S66), ni el AF, ni ADJ_CMD, ni ZPD, ni ZIT, ni el API del SA, ni el
visor, ni las caras, ni el wireless, ni los modos de disparo, ni el IDT, ni AutoFraming.

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. no atribuido = pendiente.

Artefactos: `tests/test_s100_adf_contract.py`.

---

## 1. El lado firmware: 90 comandos `[ADF][DBGCMD]` (VERIFICADO)

El firmware expone su control interno como **comandos de depuración** con prefijo de familia. De
las 102 apariciones de `[ADF][DBGCMD]`, **90 son comandos** (las restantes son errores y duplicados):

| familia | nº | comandos |
|---|---|---|
| `Input` | 16 | `SetInput`, `SetInputContinue2/3/4`, `SetInputContInternal`, `SetExtType`, `SetRefLevel`, `SetZoomLink`, `SetLowCut`, `SetUnderWater`, `SetRecLevel`, `SetReverseLR`, `SetAdjThrough`, `GetShoeWaitMsComp`, `GetShoeIdComp`, `SetShoeOnComp` |
| `InputPro` | 8 | `SetIntMicSens`, `SetInputType`, `SetInputTrim`, `SetChSource`, `SetRecLevelMode`, `SetAgcLink`, `SetManualGainLink`, `SetRecLevelLimitter` |
| `Output` | 9 | `SetOutput`, `SetOutputContinue2/3/4`, `SetOutputContInternal`, `DetectJack`, `SetHdmiFormat`, `SetAntiClipping`, `SetSpSwap` |
| `OutputPro` | 3 | `SetHpMonitor`, `SetHpOut`, `SetAdjI2sMute` |
| `System` | 12 | `SetMSG`, `SetMSG V`, `GetMSGQ`, `GetMSGQ V`, `GetMSGQ Scenario Done`, `ClearMSGQ`, `ClearCompMSGQ`, `CountMSGQ`, `ClearExecTime`, `GetMemMgrComm`, `BootExit` |
| `SystemSound` | 7 | `SetTable`, `SetPath`, `Request`, `RequestPin`, `SetVol`, `SetNotify` |
| `Proc` | 19 | `SetPath`, `SetMixRatio`, `GetMixRatio`, `SetFader`, `SetZoomNr`, `SetLinearPhase`, `LinearPhase{MemPrint,SetDec0/1,SetAip0/1,GetSa0/1,GetPin0/1,Nomatch0/1,SetMb,SetSa}Print` |
| `SoundAnalyzer` | 4 | `StartGolfShot`, `StopGolfShot`, `AnalyzeGolfShot`, `SetSoundAnalyze` (S88) |
| `CPU2` | 4 | `ExecTime 60Hz/48Hz max|over m/s` (la **medida del tiempo de ejecución** del ciclo, S81) |

Las **fases lineales** (`LinearPhase*`) son la máquina de estados del arranque (S81): `SetDec0/1`
(decodificación), `SetAip0/1` (audio IP), `GetSa0/1` (SA), `GetPin0/1` (pin), `SetMb`/`SetSa` (memoria
base / escalar) y `Nomatch0/1` (sin coincidencia).

## 2. El lado userland: el canal `AdfCh` (VERIFICADO)

`libBizFw.so` (S98) implementa la clase **`OBJAVBBCBASECLASS::AdfCh`** con **35 métodos**:

| prefijo | métodos | equivalencia con el firmware |
|---|---|---|
| `Prc` (8) | `PrcSet`, `PrcSetPath`, `PrcSetMixRatio`, `PrcSetFader`, `PrcSetZoomNr`, `PrcSetLinearPhase`, `PrcSetPeakDetect`, `PrcSetAudioOutpinMute` | `Prc SetPath` / `Prc SetFader` / `Prc SetMixRatio` / `Prc SetZoomNr` (S81) |
| `Sys` (4) | `SysRequest`, `SysSetPath`, `SysSetTable`, `SysSetVolume` | `Sys …` |
| `In` (8) | `InSetInput`, `InSetIVoice`, `InSetLowCut`, `InSetRecLevel`, `InSetRefLevel`, `InSetUnderWater`, `InSetWindNr`, `InSetZoomLink` | `In SetInput` / `In SetIVoice` / `In SetLowCut` … |
| `InPro` (7) | `InProSetIntMicSens`, `InProSetInputType`, `InProSetInputTrim`, `InProSetChSource`, `InProSetRecLevelMode`, `InProSetAgcLink`, `InProSetRecLevelLimitter` | `InPro Set*` |
| `Out` (8) | `OutSetOutput`, `OutSetHdmiFormat`, `OutSetAntiClipping`, `OutSetSpSwap`, `OutSetVolume`, `OutDetectJack`, `OutProSetHpMonitor`, `OutProSetHpOut` | `Out SetOutput` / `Out SetHdmiFormat` / `Out DetectJack` … |

**Correspondencia explícita (VERIFICADO):** cada método de `AdfCh` tiene su comando gemelo en el
firmware, con el **nombre de familia traducido**:

| userland (`AdfCh`) | firmware (`[ADF][DBGCMD]`) |
|---|---|
| `PrcSetPath`, `PrcSetMixRatio`, `PrcSetFader`, `PrcSetZoomNr`, `PrcSetLinearPhase` | `Proc SetPath`, `Proc SetMixRatio`, `Proc SetFader`, `Proc SetZoomNr`, `Proc SetLinearPhase` |
| `SysSetTable`, `SysRequest`, `SysSetPath` | `SystemSound SetTable`, `SystemSound Request`, `SystemSound SetPath` |
| `InSetInput`, `InSetIVoice`, `InSetLowCut`, `InSetRecLevel`, `InSetRefLevel`, `InSetUnderWater`, `InSetWindNr`, `InSetZoomLink` | `Input SetInput`, `Input SetIVoice`… (`Input Set*`) |
| `InProSetIntMicSens`, `InProSetInputType`, `InProSetInputTrim`, `InProSetChSource`, `InProSetRecLevelMode`, `InProSetAgcLink`, `InProSetRecLevelLimitter` | `InputPro Set*` |
| `OutSetOutput`, `OutSetHdmiFormat`, `OutSetAntiClipping`, `OutSetSpSwap`, `OutDetectJack` | `Output Set*`, `Output DetectJack` |
| `OutProSetHpMonitor`, `OutProSetHpOut` | `OutputPro SetHpMonitor`, `OutputPro SetHpOut` |

**Conclusión (VERIFICADO):** el **contrato** userland↔firmware es una familia de prefijos
(`Prc`/`Proc` = proceso, `Sys` = sistema, `In`/`InPro` = entrada de audio, `Out`/`OutPro` = salida) y
un conjunto de verbos (`Set…`, `Get…`, `Clear…`, `Request`, `Count…`) **idénticos en ambos lados**,
con la **excepción** de cuatro métodos que solo existen en el userland: `PrcSetPeakDetect`,
`PrcSetAudioOutpinMute`, `OutSetVolume` y `SysSetVolume` (y del comando de firmware
`InputPro SetManualGainLink`, que el userland no expone). El userland **no puede** invocar los
comandos de solo-firmware (`LinearPhase*`, `CPU2 ExecTime`, `SoundAnalyzer*`, `ClearMSGQ`,
`CountMSGQ`, `GetMSGQ`): son puntos de inspección, no una API.

## Cierre CAM-01 (03-11-2026, medido en bytes)

- `[ADF]`: 1220 cadenas con el token (1186 con sitio de carga, 1336 sitios) en 877 funciones contenedoras; llamadores directos `bl` 1354, punteros literal/PC-relativos/`movw`+`movt` 356/2/0; ficheros fuente citados por esas funciones: ninguno; token en A6000/A7S/A6300: 1231/1280/1356; alcance `bl` ≤ 3 al obturador: ninguna de las 7 funciones de obturador conocidas.
- `[DBGCMD]`: 102 cadenas con el token (102 con sitio de carga, 113 sitios) en 88 funciones contenedoras; llamadores directos `bl` 25, punteros literal/PC-relativos/`movw`+`movt` 76/2/0; ficheros fuente citados por esas funciones: ninguno; token en A6000/A7S/A6300: 102/110/110; alcance `bl` ≤ 3 al obturador: ninguna de las 7 funciones de obturador conocidas.

Medido con `analysis/camera_closure/labels.py` (`labels.json`; regla PIC estricta, barrido `bl` por patrón de halfwords, función = primer `push {…lr}` hacia atrás). Las llamadas indirectas no se siguen.

No atribuido (lista original anterior a la medición; las funciones contenedoras y los sitios ya están medidos arriba, y nada de esto se afirma):

- El formato binario de cada comando (cabecera, `cateId`, `msgId`, `replyId`) y la tabla de
  equivalencia con las 11 peticiones `REQ_*` (S98).
- Qué hace exactamente el submódulo `Prc` ("proceso") y su relación con `Stage_*` (S76/S82).
- Por qué el firmware expone `InputPro SetManualGainLink` y el userland no.
- La semántica de `PrcSetPeakDetect` (¿detección de picos de audio?).

## 4. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s100_adf_contract.py -q
```
