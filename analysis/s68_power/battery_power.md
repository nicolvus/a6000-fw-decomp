# S68 — Gestión de batería, alimentación y carga (NP-FW50) en la A6000

**Hito:** subsistema de batería/energía/carga de la cámara Sony A6000 (fw3.21), línea de ingeniería inversa **general** (no SilentShutter; S66 cerrado en `docs/capture/s66-lens-mount.md`).

**Método:** análisis estático de bytes de `av-cam.bin` (A6000 fw3.21, SHA-256 `b60c845c…`) y comparación con A7S (fw3.20, SHA-256 `b857d338…`). Capstone sobre bytes + literales PIC. Ningún firmware ejecutado, ninguna cámara tocada, binarios originales intactos.

**Notación:** VERIFICADO = comprobado contra bytes/instrucciones del blob; INFERENCIA = deducción lógica sin prueba directa de bytes; NO_VERIFICADO = no encontrado o sin evidencia de bytes.

---

## 1. Resumen ejecutivo

El firmware `av-cam.bin` de la A6000 fw3.21 **no contiene un modelo detallado de la batería NP-FW50** (no hay cadenas `NP-FW`, `NPFW`, `FW50`, tensión/corriente/ciclos/capacidad/SOC del pack, ni tablas de descodificación de pack). Lo que sí existe es:

- Un **acceso de bajo nivel al nivel de batería** vía "UPM" (`Set UPM Battery Level`, `0x4378f364`) que lee 8 bytes de un dispositivo y reporta estado/error.
- Códigos de protocolo de envío de estado de batería hacia un microcontrolador externo (`ACV_BATT_Snd`, `BATT_AUTH_Snd`, `BATT_STATE1..3_Snd`, `BATT_TYPE1/2_Snd`, `Box_Temperature_Snd`, `ACV Error Voltage`).
- Un **subsistema de carga de flash/strobe (SB)**, NO de batería principal: `SB_CHARGE`, `CamStrbChargeOn/Off`, `uc_ChargeCommand`, `uc_ChargeStatus`, `uc_ChargeEnable`, `uc_ChargeForceOff`, `b_SBChargeReq`, `b_GpflLogicPowerOn` (bloque de nombres en `0x43ccd8aa`–`0x43ccdc92`).
- **Power management del sensor/imager:** `MacroPowerSaveOnRequest/OffRequest`, `SubLVDS PowerSaveOn/Off`, timers `PowerOff` del imager, `MonPowersave`.
- Coordinación lente ↔ voltaje: `Wait E-MountLens ReduceVoltage Wait(%d ms)` (`0x43cc7aa4`) y `CaptureCancel_PowerOffDetect()` (`0x43ca9d85`).

**Comparativa A7S fw3.20:** la A7S conserva `Set UPM Battery Level`, `BATT_*_Snd`, `Box_Temperature_Snd`, las mismas variables de carga de flash y `SB_CHARGE`/`CamStrbChargeOn/Off`, pero **carece** de `BatteryInfo`, `IRLight/VideoLight Battery Info` y del bloque `[CAMERA_MAIN_FC]: OSAL_ERROR: BatteryInfo`.
**Corrección de la revisión (21-10-2026):** la A7S **sí** tiene `ACV Error Voltage` (`0x43c982d3`) y `ACV_BATT_Snd` (`0x43c983f6`); la afirmación inicial de que faltaban era incorrecta.

Todo lo relativo a "gestión de batería NP-FW50 real" (lectura del pack, umbrales, carga por USB/base, perfiles de consumo, apagado automático por batería) es **NO_VERIFICADO** en `av-cam.bin`.

---

## 2. Inventario de cadenas y logs (VERIFICADO contra bytes)

### 2.1 Batería principal / nivel (A6000 fw3.21)

| Dirección | Cadena | Rol |
|---|---|---|
| `0x43ca2dfd` | `[CAMERA_MAIN_SYNC]: Set UPM Battery Level [state] %d [Error] %d` | Log de lectura de nivel de batería vía UPM |
| `0x43ca6a3c` | `[CAMERA_MAIN_FC]: OSAL_ERROR: BatteryInfo` | Error de BatteryInfo en cámara principal (FC) |
| `0x43ca6a5a` | `BatteryInfo` | Nombre de propiedad/info de batería |
| `0x43ca7e2e` | `[IRLight] Battery Info : %d` | Info de batería del iluminador IR |
| `0x43ca7f1d` | `[VideoLight] Battery Info : %d` | Info de batería de la luz de vídeo |
| `0x43c8f83b` | `ACV Error Voltage` | Error de tensión (ACV = ?) |
| `0x43c8f95e` | `ACV_BATT_Snd` | Envío de estado de batería ACV |
| `0x43c8f96b` | `BATT_AUTH_Snd` | Envío autenticación de batería |
| `0x43c8f979` | `BATT_STATE1_Snd` | Envío estado de batería 1 |
| `0x43c8f989` | `BATT_STATE2_Snd` | Envío estado de batería 2 |
| `0x43c8f999` | `BATT_STATE3_Snd` | Envío estado de batería 3 |
| `0x43c8f9a9` | `BATT_TYPE1_Snd` | Envío tipo de batería 1 |
| `0x43c8f9b8` | `BATT_TYPE2_Snd` | Envío tipo de batería 2 |
| `0x43c8f9fc` | `Box_Temperature_Snd` | Envío de temperatura (caja/batería) |

### 2.2 Carga de flash/strobe (SB) — NO carga de batería principal

| Dirección | Cadena | Rol |
|---|---|---|
| `0x43cb4c23` | `SB_CHARGE` | Nombre de estado/evento de carga de flash |
| `0x43cb4cac` | `WAIT_MEM_CHG` | Espera de memoria/carga |
| `0x43cb58b3` | `EV CamStrbChargeOn` | Evento: carga de flash ON |
| `0x43cb58c6` | `EV CamStrbChargeOff` | Evento: carga de flash OFF |

### 2.3 Power management del imager / sensor

| Dirección | Cadena | Rol |
|---|---|---|
| `0x43c90f07` | `[CAMCORE]: MonPowersave[%d] is already Enabled !` | Power save del imager |
| `0x43c9469c` | `[CAM_IMAGER]: ImagerCommon::MacroPowerSaveOnRequest Unknown index number` | Power save on request |
| `0x43c94729` | `[CAM_IMAGER]: ImagerCommon::MacroPowerOffRequest Unknown index number` | Power off request |
| `0x43c95466` | `SubLVDS PowerSaveOn: SUBLCNTL_DFE1 does not exist on Regulus.` | SubLVDS power save (Regulus = ISP) |
| `0x43c954ed` | `SubLVDS PowerSaveOff: SUBLCNTL_DFE1 does not exist on Regulus.` | SubLVDS power save off |

### 2.4 Coordinación lente ↔ voltaje / apagado por captura

| Dirección | Cadena | Rol |
|---|---|---|
| `0x43cc7aa4` | `[IMAGING_CAP]: Warning! Wait E-MountLens ReduceVoltage Wait(%d ms)` | Espera a reducción de voltaje de la lente E-mount |
| `0x43ca9d85` | `[IMAGING_CAP]: CapMgr)CaptureCancel_PowerOffDetect() offFactor=%d` | Cancelación de captura por detección de apagado |

### 2.5 Bloque de nombres de variables (carga/flash/poder)

Direcciones `0x43ccd8aa`–`0x43ccdc92` (tabla de nombres de variables globales, no código):

| Dirección | Nombre | Interpretación |
|---|---|---|
| `0x43ccd8aa` | `us_RechargeIntervalCnt` | Contador de intervalo de recarga |
| `0x43ccd8c2` | `uc_ChargeCommand` | Comando de carga |
| `0x43ccd8d3` | `us_ChargeCnt` | Contador de carga |
| `0x43ccd8e0` | `uc_ChargeOnCnt` | Contador de carga encendida |
| `0x43ccd8ef` | `uc_ChargeStatus` | Estado de carga |
| `0x43ccd8ff` | `uc_AcvOn` | ACV encendido (¿adaptador AC?) |
| `0x43ccd908` | `uc_UnregVolltage` | Voltaje no regulado (sic) |
| `0x43ccd919` | `uc_CapacitorStatus` | Estado de condensador (flash) |
| `0x43ccd92c` | `uc_PwmStatus` | Estado PWM |
| `0x43ccd939` | `uc_ChargeEnable` | Habilitar carga |
| `0x43ccd949` | `us_ActivePwmDutySlope` | Pendiente de duty cycle PWM activo |
| `0x43ccd95f` | `uc_GetInfoOK` | Obtener info OK |
| `0x43ccd96c` | `uc_ChargeForceOff` | Forzar apagado de carga |
| `0x43ccda49` | `uc_ChargeRequest` | Solicitud de carga |
| `0x43ccda5a` | `uc_ChargeStopRequest` | Solicitud de parada de carga |
| `0x43ccdc63` | `b_GpflLogicPowerOn` | Power on lógico GPFL |
| `0x43ccdc76` | `b_SBChargeReq` | Petición de carga de flash (SB) |

### 2.6 Cadenas NO presentes en la A6000 fw3.21 (0 hits)

`NP-FW`, `NPFW`, `FW50`, `USB power`, `PowerProfile`, `AutoPowerOff`, `N.Stickby`, `DV.power`, `PowerMgr`, `Energy`, `Drain`, `libbackup` (solo `AdfBackUpCtrl` = backup de suspensión, subsistema ADF, no batería), cargador por USB/base, umbrales de batería, ciclos, capacidad, SOC.

---

## 3. Código y funciones (VERIFICADO contra instrucciones)

| Dirección | Función / rol | Evidencia |
|---|---|---|
| `0x4378f364` | `Set UPM Battery Level`: lee 8 bytes de dispositivo en `obj+5` (`ldm.w r5,{r0,r1}`), reporta `[state] [Error]`; error → `movs r0,#4` + log; success → `bl 0x43901a8c` | Desensamblado directo; string xref `0x43ca2dfd` en `0x4378f3ca` |
| `0x437b7d6c` | `BatteryInfo` OSAL_ERROR handler: compara resultado de `bl 0x439fd740` con 2, lee `obj[0x49c]`, loguea `OSAL_ERROR: BatteryInfo` | Desensamblado directo; string xref `0x43ca6a3c` en `0x437b7dee` |
| `0x437cf1f0` | `IRLight Battery Info`: lee flags de `r1` (offsets 0x1a, 0x22, 0x7, 0xf), escribe bytes de estado de batería en globals, loguea `[IRLight] Battery Info : %d` | Desensamblado directo; string xref `0x43ca7e2e` en `0x437cf2fe` |
| `0x437d0768` | `VideoLight Battery Info`: lee `r1` offsets 0x1d, 0x11, 0x9, 0xa, 0xb, 0x1e; lógica de umbral (0x302=770), contadores de recarga, loguea `[VideoLight] Battery Info : %d` | Desensamblado directo; string xref `0x43ca7f1d` en `0x437d0946` |
| `0x4385fff0` | `CamStrbChargeOn/Off`: emite eventos `EV CamStrbChargeOn/Off` (`0x43cb58b3`/`0x43cb58c6`) | Xrefs `0x43860124`/`0x4386051a` → `0x43cb58b3`/`0x43cb58c6` |

**Llamadores directos (VERIFICADO):**
- `0x437b7ee6` (dentro de `0x437b7ea2`) → `0x437b7d6c` (BatteryInfo error)
- `0x437cf996`, `0x437cf972` (dentro de `0x437cf928`) → `0x437cf1f0` (IRLight)
- `0x437d0946` (dentro de `0x437d0768`) → `0x437d0768` (VideoLight) — recursivo/auto-referencia por literal
- `0x43860124`, `0x4386051a` (dentro de `0x4385fff0`) → strings de `CamStrbChargeOn/Off`
- `0x437b5e18` (dentro de `0x437b5d30`) → `0x4385fff0` (CamStrbCharge)

---

## 4. Modelo de datos de la batería (estado)

### 4.1 Qué se lee del pack (NP-FW50)

**NO_VERIFICADO:** no existe en `av-cam.bin` ninguna cadena `NP-FW`/`FW50` ni rutina de lectura de tensión/corriente/temperatura/ciclos/capacidad/SOC del pack de batería. No se ha localizado una tabla de descodificación de pack ni una máscara de campos de batería.

Lo que SÍ se lee (VERIFICADO):
- `0x4378f364` lee 8 bytes de un dispositivo apuntado por `obj+5` y expone `state` + `error` (log `Set UPM Battery Level [state] %d [Error] %d`). Semántica de los 8 bytes: **INFERENCIA** (nivel de batería, no verificada contra bytes).
- `BATT_AUTH_Snd` / `BATT_STATE1..3_Snd` / `BATT_TYPE1/2_Snd` / `ACV_BATT_Snd` (0x43c8f95e–0x43c8f9b8): envío de estado/tipo/autenticación de batería hacia un microcontrolador externo (probablemente el MCU de la batería o el sistema de gestión de poder). Sin xrefs directos (acceso por offset desde tabla), destino **NO_VERIFICADO**.
- `Box_Temperature_Snd` (0x43c8f9fc): envío de temperatura. **INFERENCIA** si es de batería o de la cámara.

### 4.2 Qué se escribe de vuelta

**NO_VERIFICADO:** no se ha localizado escritura de vuelta al pack de batería (carga, calibración, reset de ciclos). Las variables `uc_ChargeCommand`, `uc_ChargeEnable`, `uc_ChargeForceOff`, `uc_ChargeRequest`, `uc_ChargeStopRequest` pertenecen al subsistema de **flash/strobe (SB)**, no a la batería principal (evidencia: `SB_CHARGE`, `b_SBChargeReq`, `uc_CapacitorStatus`, `CamStrbChargeOn/Off`).

### 4.3 Tablas y máscaras

**NO_VERIFICADO:** no se han localizado tablas de descodificación de batería ni máscaras de campos de pack.

---

## 5. Carga: USB (MTP/PD) y base

**NO_VERIFICADO en `av-cam.bin`:**
- No existe `USB power`, cargador por USB, PD, base de carga.
- Las variables de "carga" localizadas (`uc_ChargeCommand`, `uc_ChargeStatus`, `uc_ChargeEnable`, `uc_ChargeForceOff`, `uc_ChargeRequest`, `uc_ChargeStopRequest`, `b_SBChargeReq`) están en el bloque junto a `SB_CHARGE`, `CamStrbChargeOn/Off`, `uc_CapacitorStatus` → son de **carga del condensador del flash**, no de la batería NP-FW50.
- No hay logs de "full", "abnormal", "charging", "charge complete" de batería.

Lo que sí existe (carga de flash, VERIFICADO): `SB_CHARGE` (`0x43cb4c23`), `WAIT_MEM_CHG` (`0x43cb4cac`), `EV CamStrbChargeOn` (`0x43cb58b3`), `EV CamStrbChargeOff` (`0x43cb58c6`), función `0x4385fff0`.

---

## 6. Perfiles de energía y apagado automático

### 6.1 Perfiles de consumo localizados (VERIFICADO)

- `MacroPowerSaveOnRequest` / `MacroPowerOffRequest` (`0x43c9469c`, `0x43c94729`): control de power save/off del imager por canal (rechaza `CH_1`).
- `SubLVDS PowerSaveOn/Off` (`0x43c95466`/`0x43c954ed`): bloques SubLVDS del ISP Regulus; `SUBLCNTL_DFE1` no existe en Regulus (rama de error).
- `MonPowersave` (`0x43c90f07`): monitor de power save del CAMCORE.

### 6.2 Apagado automático

**NO_VERIFICADO:** no existe `AutoPowerOff` (0 hits). No se ha localizado un temporizador de apagado automático por inactividad ni un gestor de perfiles de consumo (LCD, AF, Picture Effect).

### 6.3 Relación con montura (LOGIC_ON/LOGIC_OFF de S66) y lente

- `Wait E-MountLens ReduceVoltage Wait(%d ms)` (`0x43cc7aa4`): la captura espera a que la lente E-mount reduzca voltaje. Vínculo lente ↔ alimentación **VERIFICADO** (cadena + contexto `[IMAGING_CAP]`).
- `CaptureCancel_PowerOffDetect() offFactor=%d` (`0x43ca9d85`): cancelación de captura por detección de apagado. Vínculo captura ↔ power-off **VERIFICADO** (cadena).
- No se ha localizado `LOGIC_ON`/`LOGIC_OFF` en el subsistema de batería (esas cadenas son de la montura, S66). No hay evidencia de bytes de que el subsistema de batería controle el encendido/apagado lógico del cuerpo.

---

## 7. DC/DD (libbackup/backup) y "drain" de energía

- `AdfBackUpCtrl` / `AdfSusResCtrl` (`0x43c2a12f`–`0x43c2a3fd`, `0x43c27791`–`0x43c277ee`): backup de suspensión/restauración (SusRes) del subsistema ADF, no de batería. `ChangeBackUp`, `ReadBackUp`, `WriteBackUp`, `Init MemMgr`, `REG/UNREG CB`.
- `McBackupBlock`, `WrapBackupBase`, `ModuleGetBackupQTable` (`0x43c41454`, `0x43c68bd7`, `0x43c77d68`, `0x43c7ed7f`): subsistema de backup genérico (SDF/VDF/PNL).
- `DC` / `DD`: aparecen como fragmentos dentro de otras cadenas (ej. `DCh`, `M|DdY`) — **no hay evidencia de un subsistema "DC/DD" de gestión de batería**; son coincidencias de subcadena.
- `libbackup` / "drain" de energía: **0 hits** → NO_VERIFICADO. No hay evidencia de un módulo `libbackup` relacionado con batería ni de "drain" de energía.

---

## 8. Coordinación alimentación ↔ captura (orden de apagado)

- `CaptureCancel_PowerOffDetect() offFactor=%d` (`0x43ca9d85`): la captura se cancela ante detección de apagado. **VERIFICADO** (cadena en `[IMAGING_CAP]`).
- `Wait E-MountLens ReduceVoltage Wait(%d ms)` (`0x43cc7aa4`): la captura espera la reducción de voltaje de la lente. **VERIFICADO** (cadena).
- No se ha localizado un orden explícito de apagado "primero tarjeta, luego sensor" ni viceversa en el subsistema de batería. **NO_VERIFICADO**.

---

## 9. Comparativa A6000 (fw3.21) vs A7S (fw3.20)

| Elemento | A6000 fw3.21 | A7S fw3.20 | Diferencia |
|---|---|---|---|
| `Set UPM Battery Level` | `0x43ca2dfd` | `0x43ca8a94` | Ambas |
| `BatteryInfo` / `OSAL_ERROR: BatteryInfo` | `0x43ca6a5a` / `0x43ca6a3c` | Ausente | Solo A6000 |
| `[IRLight] Battery Info : %d` | `0x43ca7e2e` | Ausente | Solo A6000 |
| `[VideoLight] Battery Info : %d` | `0x43ca7f1d` | Ausente | Solo A6000 |
| `ACV Error Voltage` | `0x43c8f83b` | `0x43c982d3` | **En ambas** (revisión: la A7S sí lo tiene) |
| `ACV_BATT_Snd` | `0x43c8f95e` | `0x43c983f6` | **En ambas** (revisión) |
| `BATT_AUTH_Snd` / `BATT_STATE1..3_Snd` / `BATT_TYPE1/2_Snd` | `0x43c8f96b`–`0x43c8f9b8` | `0x43c983f6`–`0x43c98450` | Ambas, distinta dirección |
| `Box_Temperature_Snd` | `0x43c8f9fc` | `0x43c98494` | Ambas |
| `SB_CHARGE` / `WAIT_MEM_CHG` | `0x43cb4c23` / `0x43cb4cac` | `0x43caa7d4` / `0x43caa85d` | Ambas (flash) |
| `CamStrbChargeOn/Off` | `0x43cb58b3` / `0x43cb58c6` | `0x43cab730` / `0x43cab743` | Ambas (flash) |
| Variables de carga (`uc_ChargeCommand`…) | `0x43ccd8c2`… | `0x43cc7663`… | Ambas, distinta base |
| `PowerSave` (imager/SubLVDS) | `0x43c90f07`… | `0x43c99edf`… | Ambas |
| `PowerOff` timers (imager) | `0x43c93e49`… | `0x43c9c75d`… | Ambas |
| `NP-FW` / `FW50` / `USB power` / `AutoPowerOff` / `PowerMgr` / `Energy` | Ausentes | Ausentes | Ninguna tiene gestión detallada de batería NP-FW50 |
| `BatteryInfo` (propiedad) | Presente | Ausente | A6000 la añade |

**Conclusión comparativa:** ninguna de las dos cámaras tiene en `av-cam.bin` un modelo detallado de batería NP-FW50 ni carga por USB/base. La A6000 añade `BatteryInfo` y `IRLight/VideoLight Battery Info` respecto de la A7S (revisión: `ACV_BATT_Snd` y `ACV Error Voltage` están en ambas). Ambas comparten el subsistema de carga de flash (SB) y el power save del imager.

---

## 10. Frontera: VERIFICADO vs NO_VERIFICADO

### VERIFICADO (contra bytes de av-cam.bin A6000 fw3.21)

1. Cadenas exactas de batería/nivel en las direcciones de §2.1 (§2.1).
2. Función `0x4378f364` lee 8 bytes de dispositivo (`obj+5`) y loguea `Set UPM Battery Level [state] [Error]`; error → código 4.
3. Función `0x437b7d6c` maneja `OSAL_ERROR: BatteryInfo` (lee `obj[0x49c]`, compara resultado con 2).
4. Funciones `0x437cf1f0` (IRLight) y `0x437d0768` (VideoLight) decodifican info de batería de un struct y loguean `Battery Info : %d`.
5. Cadenas `BATT_*_Snd` / `ACV_BATT_Snd` / `Box_Temperature_Snd` / `ACV Error Voltage` en `0x43c8f83b`–`0x43c8f9fc`.
6. Subsistema de carga de flash (SB): `SB_CHARGE`, `CamStrbChargeOn/Off`, `uc_ChargeCommand`… en `0x43cb4c23`–`0x43ccdc76`; función `0x4385fff0`.
7. Power save del imager: `MacroPowerSaveOn/OffRequest`, `SubLVDS PowerSaveOn/Off`, `MonPowersave`.
8. `Wait E-MountLens ReduceVoltage` (`0x43cc7aa4`) y `CaptureCancel_PowerOffDetect` (`0x43ca9d85`).
9. A7S comparativa: mismas variables de carga de flash y `BATT_*_Snd` (incluidos `ACV_BATT_Snd` y `ACV Error Voltage`), sin `BatteryInfo` ni `[IRLight]/[VideoLight] Battery Info`.

### INFERENCIA (sin prueba directa de bytes)

- Los 8 bytes leídos por `0x4378f364` = nivel/carga de batería NP-FW50 (semántica no verificada).
- `BATT_*_Snd` / `ACV_BATT_Snd` = envío de estado de batería a MCU externo (destino no verificado).
- `uc_AcvOn` = estado de adaptador AC (nombre sugiere AC, no verificado).
- Las variables `uc_Charge*` = control de carga (pero pertenecen al flash, no a la batería principal).

### NO_VERIFICADO (no encontrado en av-cam.bin)

1. Modelo de datos del pack NP-FW50: ID de modelo, tensión, corriente, temperatura, ciclos, capacidad, SOC del pack. (0 hits de `NP-FW`/`FW50`.)
2. Tablas de descodificación de pack ni máscaras de campos.
3. Escritura de vuelta al pack (calibración, reset de ciclos).
4. Carga por USB (MTP/PD) ni por base; logs "full"/"abnormal" de carga de batería.
5. Perfiles de consumo (LCD, AF, Picture Effect) ni gestor de perfiles de energía (`PowerProfile`, `PowerMgr`, `Energy` ausentes).
6. Apagado automático por inactividad/batería (`AutoPowerOff` ausente).
7. Control del circuito de carga de batería (encendido/apagado, límite de corriente).
8. Subsistema `DC/DD` / `libbackup` de batería ni "drain" de energía (0 hits relevantes).
9. Orden explícito de apagado captura ↔ tarjeta.
10. Vínculo directo subsistema de batería ↔ encendido/apagado lógico del cuerpo (`LOGIC_ON/LOGIC_OFF` son de la montura, S66).

---

## 11. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s68_power.py -q
```

El test verifica contra bytes: cadenas en direcciones exactas, funciones, constantes/tablas clave y la comparación A6000 vs A7S.
