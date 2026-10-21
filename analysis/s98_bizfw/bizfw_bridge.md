# S98 — `libBizFw.so`: el orquestador userland y el puente con el framework ADF

**Alcance:** línea de ingeniería inversa **general** de la cámara: la biblioteca que **une el userland
(Linux) con el firmware de la cámara** (`av-cam.bin`), es decir, el canal por el que la GUI, el
audio, la imagen y la red hablan con el framework **ADF** (S81) y con los subsistemas de detectar,
memoria, HDMI, escalar, SDF, SDI, VDF y VEF. Conecta con S93 (colas OSAL), S86 (visor), S71 (caras),
S81/S91 (ADF) y S99 (capas del userland).

**Estado:** VERIFICADO = contra bytes/símbolos. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

> **Nota de revisión (21-10-2026).** Informe del subagente verificado por muestreo; **una corrección
> importante**: las trazas `PrcSetPath to ADF` y `Snd Msg to ADF` **no están en `av-cam.bin`**
> (0 hits) sino **en `libBizFw.so`** (el userland es quien *envía* al ADF). Se añade además el
> hallazgo de la clase `OBJAVBBCBASECLASS::AdfCh` y la lista completa de destinos.

Artefactos: `analysis/s98_bizfw/bizfw_bridge.json`, `tests/test_s98_bizfw.py`.

---

## 1. La biblioteca (VERIFICADO)

`libBizFw.so` — **332 600 B** (fw3.21, *stripped*: los nombres de símbolo sobreviven como cadenas).

Usa **tres grupos de colas OSAL** (los mismos de S93):
`OSAL_MSGQ_GID_DETECT_FACE`, `OSAL_MSGQ_GID_DMM_CTRL`, `OSAL_MSGQ_GID_SADRIVER`.

## 2. El vocabulario de mensajes (VERIFICADO)

**9 categorías** (`CATEID_*`): `PIN`, `RENDERER`, `DISPLAY`, `SYSTEMSOUND`, `AUDIOPROCESSOR`, `MIC`,
`MIXER`, `SPEAKER`, `EFFECT`.

**1 identificador de mensaje** (`MSG_ID_*`): `MSG_ID_VDF_SRVC_SET_YC_REC_CONTROL` → el control de
grabación YC que se envía al **servicio del visor** (VDF, S86).

**11 peticiones** (`REQ_*`), con el patrón "verbo + E" de respuesta:
`REQ_DEPOSITE`, `REQ_DEPOSIT_MULTIE`, `REQ_DESTRUCTE`, `REQ_INQUIREE`, `REQ_OVERWRITEE`, `REQ_PARSEE`,
`REQ_PEEKE`, `REQ_POKEE`, `REQ_RAW_PARSEE`, `REQ_SHAREE`, `REQ_WITHDRAWE` → el **ciclo de vida de un
objeto** (depositar, consultar, compartir, releer, destruir).

Clase de estado: `StmCh` (12 símbolos: `StmCh4/5/7/8/9/13`, `StmChC1E/C2E`, `StmChD0E/D1E/D2E`).

## 3. El puente con el firmware: la clase `AdfCh` (VERIFICADO)

La clave del puente es la clase **`OBJAVBBCBASECLASS::AdfCh`** (canal ADF), cuyos métodos **repiten
exactamente el vocabulario de los comandos de depuración del ADF del firmware** (S81):

| método de `AdfCh` (userland) | comando equivalente del ADF (firmware) |
|---|---|
| `PrcSetPath(unsigned char)` | `Prc SetPath` |
| `SysSetTable(...)`, `SysRequest(...)`, `SysSetPath(...)` | `Sys SetTable` / `Sys Request` / `Sys SetPath` |
| `InSetInput`, `InSetIVoice`, `InSetLowCut`, `InSetWindNr` | `In SetInput` / `In SetIVoice` / `In SetLowCut` / `In SetWindNr` |
| `PrcSetFader(...)` | `Prc SetFader` |
| `OutSetOutput`, `OutSetSpSwap`, `OutSetVolume` | `Out SetOutput` / `Out SetSpSwap` / `Out SetVolume` |

→ **la numeración de prefijos (`Prc`/`Sys`/`In`/`InPro`/`Out`) es la misma en ambos lados**: es el
**contrato** entre el userland y el framework ADF.

## 4. A quién habla el userland (VERIFICADO)

Las trazas `Failed to Snd Msg to X` delatan los **diez destinos** del userland:

`ADF`, `DETECT`, `DMM`, `HAPI`, `HDMI`, `SA`, `SDF`, `SDI`, `VDF`, `VEF`.

| destino | qué es del lado firmware |
|---|---|
| `ADF` | el framework de arranque/mensajería (S81) |
| `DETECT` | la detección de caras (S71), que además tiene su propia cola `OSAL_MSGQ_GID_DETECT_FACE` |
| `DMM` | el gestor de memoria (`OSAL_MSGQ_GID_DMM_CTRL`, S99 `MWF`/`UFW`) |
| `HAPI` | la API de la app remota (S94) |
| `HDMI` | la salida HDMI |
| `SA` | el **escalador** (`OSAL_MSGQ_GID_SADRIVER`) |
| `SDF` / `SDI` | el dataflow de imagen (S99 `C_DataflowInfra_*`, S16–S30) |
| `VDF` / `VEF` | el visor y el visor electrónico (S86) |

En el lado firmware, el escalar aparece con **125 nombres de clase RTTI distintos `NS_SCALAR_INFRA*`** (167 apariciones del token)
(`N15NS_SCALAR_INFRA21ScalarInfraSequenceIfE` `0x43ce59d2`,
`N15NS_SCALAR_INFRA23ScalarInfraSequenceIdleE` `0x43ce5c4d`,
`N15NS_SCALAR_INFRA26ScalarInfraSequenceStageIfE` `0x43ce5c7a`).

## 5. Comparación A6000 fw3.21 vs A7S fw3.20 (VERIFICADO)

Las constantes de categorías e IDs de mensaje de `libBizFw.so` son **idénticas** en la A7S → código
compartido entre plataformas.

## 6. Abierto (NO_VERIFICADO)

- El formato binario de los mensajes ADF (cabecera, `cateId`, `msgId`, `replyId`) y la tabla de
  equivalencia con las 11 peticiones.
- Qué hace exactamente el canal `SA` frente a `SADRIVER`.
- Cómo se mapea `MSG_ID_VDF_SRVC_SET_YC_REC_CONTROL` al servicio del visor.

## 7. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s98_bizfw.py -q
```
