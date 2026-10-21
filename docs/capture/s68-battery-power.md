# S68 — Gestión de batería, alimentación y carga (NP-FW50) en la A6000

**Hito:** línea de ingeniería inversa **general** de la cámara: subsistema de batería/energía del
`av-cam.bin` (nivel de batería, códigos de estado hacia un MCU, carga del flash, power save del
imager, coordinación lente↔voltaje). **Independiente** de la línea SilentShutter y de la montura
(S66). Sin cambios en S51 (fin electrónico NO VERIFICADO; A/B/C = NO).

**Método:** análisis estático de bytes del `av-cam.bin` de A6000 (fw3.21) y comparación con A7S
(fw3.20). Capstone sobre bytes; **ningún firmware ejecutado, ninguna cámara tocada**.

**Pruebas:** `tests/test_s68_battery.py` (7 tests) · Informe detallado: `analysis/s68_power/battery_power.md`
· Tabla: `analysis/s68_power/battery_power.json`.

---

## 1. Resultado principal (VERIFICADO, y es un resultado **negativo**)

**El `av-cam.bin` de la A6000 no contiene un modelo detallado de la batería NP-FW50.** No hay
cadenas `NP-FW`/`NPFW`/`FW50`, ni tensión/corriente/ciclos/capacidad/SOC del pack, ni tablas de
decodificación del pack (verificado con `bytes.find` sobre el blob completo). Lo que sí existe:

1. **Nivel de batería vía UPM** (acceso de bajo nivel a un dispositivo):
   `Set UPM Battery Level [state] %d [Error] %d` (`0x43ca2dfd`, función `0x4378f364`), que lee
   8 bytes de un dispositivo y reporta estado/error.
2. **Códigos de protocolo hacia un microcontrolador externo**: `ACV_BATT_Snd` (`0x43c8f95e`),
   `BATT_AUTH_Snd` (`0x43c8f96b`), `BATT_STATE1..3_Snd`, `BATT_TYPE1/2_Snd`,
   `Box_Temperature_Snd` (`0x43c8f9fc`) y `ACV Error Voltage` (`0x43c8f83b`).
3. **Carga del flash/strobe (SB)**, *no* de la batería principal: `SB_CHARGE` (`0x43cb4c23`),
   `CamStrbChargeOn/Off`, `uc_ChargeCommand` (`0x43ccd8c2`), `uc_ChargeStatus` (`0x43ccd8ef`),
   `uc_ChargeEnable` (`0x43ccd939`), `uc_ChargeForceOff` (`0x43ccd96c`),
   `b_GpflLogicPowerOn` (`0x43ccdc63`), `b_SBChargeReq` (`0x43ccdc76`).
4. **Power save del imager/sensor**: `MacroPowerSaveOnRequest/OffRequest`,
   `SubLVDS PowerSaveOn/Off`, temporizadores de `PowerOff` del imager, `MonPowersave`.
5. **Coordinación lente ↔ voltaje**: `Wait E-MountLens ReduceVoltage Wait(%d ms)`
   (`0x43cc7aa4`) — la captura espera a que la lente E-mount reduzca voltaje — y
   `CaptureCancel_PowerOffDetect()` (`0x43ca9d85`).
6. **Información de batería en las luces**: `[IRLight] Battery Info : %d` (`0x43ca7e2e`),
   `[VideoLight] Battery Info : %d` (`0x43ca7f1d`) y el error
   `[CAMERA_MAIN_FC]: OSAL_ERROR: BatteryInfo` (`0x43ca6a3c`).

## 2. Comparativa A6000 (fw3.21) vs A7S (fw3.20) (VERIFICADO)

| Rasgo | A6000 | A7S |
|---|---|---|
| `Set UPM Battery Level` | sí (`0x43ca2dfd`) | sí (`0x43ca8a94`) |
| `BATT_*_Snd`, `Box_Temperature_Snd` | sí | sí |
| `ACV_BATT_Snd` / `ACV Error Voltage` | sí | **sí** (`0x43c983f6` / `0x43c982d3`) |
| Carga de flash (`SB_CHARGE`, `CamStrbChargeOn/Off`, `uc_Charge*`) | sí | sí |
| `BatteryInfo` / `[IRLight]/[VideoLight] Battery Info` | sí | **no** |
| `[CAMERA_MAIN_FC]: OSAL_ERROR: BatteryInfo` | sí | no |

**Corrección aplicada en la revisión (21-10-2026):** el informe inicial afirmaba que la A7S carecía
de `ACV Error Voltage` y `ACV_BATT_Snd`; es **falso** (la A7S tiene ambas). El test fija ahora las
direcciones correctas de la A7S para que la afirmación no vuelva a colarse.

## 3. Frontera (NO_VERIFICADO)

- Modelo del pack (tensión, ciclos, capacidad, SOC) → **no está en `av-cam.bin`**: está en otro
  binario (userland o MCU).
- Destino de los códigos `BATT_*_Snd` / `ACV_BATT_Snd` (¿MCU de la batería? ¿gestor de energía?).
- Carga por USB/MTP/PD y por base: **no hay modelo en el firmware** (solo la carga del flash).
- Perfiles de consumo (Picture Effect, AF, LCD) y apagado automático por batería: no localizados
  como subsistema en `av-cam.bin`.
- Significado de `VGS/PR/MF/CONS/BANDI` (configuración del bloque de audio, S69).

## 4. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s68_battery.py -q
```

Referencias: `analysis/s68_power/battery_power.md` (informe), `.json` (tabla).
