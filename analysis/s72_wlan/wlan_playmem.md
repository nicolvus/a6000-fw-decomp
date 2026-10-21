# S72 — Wireless y transferencia remota (WLAN / PlayMem / "Camera on Demand") en la A6000 fw3.21

**Alcance:** línea de ingeniería inversa **general** de la cámara: la pila **wireless** del userland
(fw3.21) — WLAN (control, ajuste y recurso), **P2P/Wi-Fi Direct con rol "Group Owner"**, **DLNA**,
el **"Camera on Demand"** (guardado de capturas en el almacenamiento) y la configuración de
`wpa_supplicant`/DHCP. No es la línea SilentShutter, ni la montura (S66), ni el AF, ni el pipeline
(S76), ni el API del motor de imagen (S84).

**Estado:** VERIFICADO = contra bytes/símbolos. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

> **Nota de revisión (21-10-2026).** Documento revisado contra los binarios: el borrador del subagente
> tenía cuatro errores — (a) `getMacAddress` no existe: el símbolo real es
> `GetMacAddress(WlanResource::ST_MSG_SYNC_REQ*)`; (b) las colas son
> `OSAL_MSGQ_GID_WLAN_RSRC_DBG` y `OSAL_MSGQ_GID_WLAN_RSRC_TEST` (no `…_API`); (c) **`libgps_rsrc.so`
> SÍ está en el firmware de la A6000** (109 384 B), no ausente; (d) la cadena GO está **más
> desarrollada en la A6000** (106 016 B frente a 64 580 B de la A7S), no al revés.

Artefactos: `analysis/s72_wlan/wlan_playmem.json`, `tests/test_s72_wlan.py`.

---

## 1. Las seis bibliotecas (VERIFICADO)

Ruta: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/`
(157 `.so` en la A6000; 160 en la A7S fw3.20).

### 1.1 `libWlanAdjust.so` (60 492 B) — ajuste del radio

Ciclo de vida `WlanAdjust_Init` / `WlanAdjust_Res` / `WlanAdjust_Sus`; control del
`wpa_supplicant` con 11 apariciones de `wpa_ctrl_*` (open/close/detach/get_fd/send/request/pending/recv);
`wlanLoadFirmware`; configuración `wlanSetSsid`, `wlanSetTxCh`, `wlanSetTxMode`, `wlanSetTxRate`,
`wlanSetTxPower` y sus `wlanGet*`; `wlanStartTx` / `wlanStopTx`; estado interno
`m_fixed_ssid`, `m_fixed_psk`, `m_interfaceName`, `m_senserHandle`, `m_txCh`, `m_txGi`, `m_txMode`,
`m_txRate`, `m_txPower`, `m_chRange`; `SetMacAddress` (con traza `[WLAN_ADJUST_E]: Error: SetMacAddress`).

### 1.2 `libWlanControlCommon.so` (23 840 B) — control del puerto

`initializePort` / `finalizePort`, `setPortToStartWlan` / `setPortToStopWlan`,
`installWlanDrivers` / `uninstallWlanDrivers`, `loadWlanFirmware`; **25 apariciones de "BMI"** (el
bus de mensajes del chip, `BMI_read_mem`/`BMI_write_mem`) y control **GPIO** para la energía del
radio.

### 1.3 `libWlanResource.so` (63 656 B) — recurso y hilo principal

`wlanResource_init/res/sus`, `WlanResourceMainThread` (hilo con colas OSAL), `startWlan` /
`stopWlan`, `GetMacAddress` (`_Z13GetMacAddressPN12WlanResource15ST_MSG_SYNC_REQE`, con traza
`[WR_E]: Error GetMacAddress: %s Line: %d`), soporte **DFS** (9 apariciones). Colas:
`OSAL_MSGQ_GID_WLAN_RSRC_DBG`, `OSAL_MSGQ_GID_WLAN_RSRC_TEST`.

### 1.4 `libGOConnectionManager.so` (106 016 B) — P2P con rol "Group Owner"

**348 símbolos mangled, exactamente los mismos que en la A7S fw3.20 (0 diferencias)**.

- `GOConnectionManager` (200 apariciones): máquina de estados
  **Idle → Init → Auth → Wait → ChgKey → AuthConn → Finalizing → Stop**, con `startGO` / `stopGO`,
  `disconnect` / `reconnect`, `authPush`, `changeKey`, `cancel`.
- `GOConnectionManagerCmdMgr`: `IsExecInitialize/StartGO/StopGO/Disconnect/Cancel/WpsPush/WpsInput/ChangeKey`,
  `ChangeState`, `ChkReturnCode`, `ChkFatalError`, y procesadores
  `ProcInitialize`, `ProcStartGO`, `ProcIdleToAuthReq`, `ProcWaitAuthReqToChgKey`, `ProcStopGO`,
  `ProcIssueCompErrSequence`, `ProcIssueFatalError`, `ProcIgnoreEvt`.
- `NetServiceWrapper` (83 apariciones): comandos **WPS** (`StartWpsCmd`, `CancelWpsCmd`, `InputPin`,
  `AuthPush`, `ChangeKey`); eventos (`SendStartEvt`, `SendLostEvt`, `SendStopCmp`,
  `SendFinalizeCmp`, `SendStartWpsCmp`, `SendReqWpsEvtPush`, `SendReqWpsEvtShowPin`,
  `SendReqWpsEvtInputPin`, `SendCoonectedEvt`, `SendRefuseWpsCmp`, `SendHwErrEvt`, `SendSwErrEvt`,
  `SendWpsCompleteEvt`); consultas (`GetSSIDEv`, `GetTargetDeviceName`, `GetOwnDeviceName`,
  `GetKeyInfo`, `IsStateInit/Idle/Connected/DoWps`, `IsBusy`, `IsReady`) y registro
  (`RegisterNotifyEvent`, `RegisterToNetConnectionManager`).

INFERENCIA: la cámara actúa de **Group Owner Wi-Fi Direct** y el móvil de cliente; es el corazón de
"Camera on Demand" cuando está activo.

### 1.5 `libInfraDlnaControl.so` (525 892 B) — DLNA/UPnP

Tabla de estados `dc_statetbl` y `dc_evtTbl` (+ `dc_evtTbl_before_mode`); 9 *callers* de Life
Finder: `m_lid_Initialize_caller`, `m_lid_Start_caller`, `m_lid_Stop_caller`, `m_lid_Search_caller`,
`m_lid_Connect_caller`, `m_lid_Disconnect_caller`, `m_lid_SetSlideShow_caller`,
`m_lid_SetContent_caller`, `m_lid_SendContent_caller`; y envío de mensajes a los tres actores
UPnP: `sendMsgToControlpoint`, `sendMsgToMediaServer`, `sendMsgToContentHandler`. 274 apariciones de
"DLNA" y 4 de "UPnP". 1971 símbolos mangled (A7S: 1981; 10 exclusivos de A6000 y 20 de A7S).

### 1.6 `CameraOnDemandSaver.so` (20 084 B) — "Camera on Demand"

Clase `CAM_ONDEMAND_SAVER` con `init` / `exit` / `snd_msg`; hilo
`cam_ondemand_saver_thread`; **sistemas de archivos** `/dev/ms1`, **`/mnt/dcim/100msdcf`** y
**`/setting/psd.bin`**; modos *FT mode* (Linux file system), *YC module mode* y *normal fsys write*;
auto-numeración `%04d_%02X`; montaje/desmontaje de medios `/dev/ms1` y `/mnt`.

**Dato nuevo (VERIFICADO):** `/setting/psd.bin` es el **mismo fichero** que S75 identificó como
origen "from body" de los datos **ZPD** de calibración del sensor → el "Camera on Demand" **escribe
en el almacén de ajustes de la cámara**, no solo en la tarjeta.

### 1.7 `libHapiLib.so` (89 628 B) — API de la app Sony

Presente en ambas cámaras (A7S: 77 380 B). **No existe `libInfraHapiLib.so`** (el nombre real es
`libHapiLib.so`).

## 2. La configuración del supplicant y del DHCP: `netconf/` (VERIFICADO)

`netconf` es un **directorio con cuatro ficheros de configuración** (no un binario):

| fichero | contenido clave |
|---|---|
| `bss.conf` | `ctrl_interface=/tmp_network/run/wpa_supplicant`, `ap_scan=0`, `disable_scan_offload=1`, `wps_cred_processing=1`; WPS: `manufacturer=Sony Corporation`, `model_name=SonyImagingDevice`, `model_number=0`, `device_name=WCM-Sample-Device`, `device_type=1-0050F204-1`, `serial_number=0`, `config_methods=physical_display virtual_push_button`, `os_version=80000000`, `uuid=12345678-9abc-def0-1234-56789abcdef0` |
| `p2p.conf` | `p2p_intra_bss=0`, `p2p_go_intent=10`, `p2p_oper_reg_class=81` (canal dinámico), `p2p_listen_reg_class=81`, `persistent_reconnect=0`, `max_num_sta=1`, `p2p_ssid_postfix=-WCM`; WPS: `device_type=4-0050F204-1`, `config_methods=virtual_push_button physical_display keypad`, mismo `uuid` |
| `dhcpd.conf` | `subnet 10.0.0.0 netmask 255.255.0.0`, `range 10.0.1.1 10.0.1.254`, `option routers 10.0.0.1`, `default-lease-time 600`, `max-lease-time 7200` |
| `pump.conf` | cliente DHCP: `retries 3`, `nogateway`, dispositivos `ath0`/`ath1` con `nodns` y `autoip` |

**Diferencial (VERIFICADO por SHA-256):** `bss.conf`, `p2p.conf` y `pump.conf` son **byte a byte
idénticos** entre A6000 fw3.21 y A7S fw3.20; solo **`dhcpd.conf` difiere**.

## 3. PlayMem / "Camera on Demand" (VERIFICADO + INFERENCIA)

- VERIFICADO: `CameraOnDemandSaver.so` **guarda archivos** en el almacenamiento (`/mnt/dcim/100msdcf`)
  y en `/setting/psd.bin`; no hay en esa biblioteca ninguna ruta de **transferencia** por radio.
- VERIFICADO: la transferencia/emparejamiento P2P lo aporta `libGOConnectionManager.so` (WPS + PIN +
  Group Owner) con `netconf/p2p.conf` como configuración del supplicant.
- INFERENCIA: "Camera on Demand" = la cámara actúa de **Group Owner** (`libGOConnectionManager`) para
  que el móvil entre, y el **guardado de la captura** lo hace `CameraOnDemandSaver` (incluido el
  `psd.bin` de calibración). El flujo exacto entre ambos componentes **no está demostrado** por los
  bytes: no hay mensaje compartido visible entre las dos bibliotecas.

## 4. Diferencial A6000 fw3.21 vs A7S fw3.20 (VERIFICADO)

| componente | A6000 fw3.21 | A7S fw3.20 | observación |
|---|---|---|---|
| `libGOConnectionManager.so` | 106 016 B, **348 símbolos** | 64 580 B, **348 símbolos** | **esquema idéntico** (0 diferencias); la A6000 tiene **más código** (no menos) |
| `libInfraDlnaControl.so` | 525 892 B, 1971 símbolos | 360 556 B, 1981 símbolos | 10 símbolos exclusivos de A6000, 20 de A7S |
| `CameraOnDemandSaver.so` | 20 084 B, 28 símbolos | 14 244 B, 28 símbolos | esquema idéntico, la A6000 es mayor |
| `libWlanResource.so` | 63 656 B | 33 004 B | la A6000 duplica el tamaño |
| `libWlanAdjust.so` | 60 492 B | 49 420 B | — |
| `libHapiLib.so` | 89 628 B | 77 380 B | presente en ambas |
| `libgps_rsrc.so` | **presente (109 384 B)** | presente (88 944 B) | **corrección**: la A6000 **sí** lo incluye en el firmware (aunque la A6000 no tenga GPS de hardware) |
| `netconf/` | 4 ficheros | 4 ficheros | 3 idénticos; `dhcpd.conf` distinto |
| `.so` en todo el firmware | 460 | 474 | — |

## 5. Abierto (NO_VERIFICADO)

- Cómo se enlazan `libGOConnectionManager` y `CameraOnDemandSaver` (mensaje, IPC o fichero).
- Por qué la fw3.21 de A6000 duplica el tamaño de las bibliotecas WLAN (funcionalidad nueva o
  compilación con más símbolos).
- Contenido y destino del `psd.bin` escrito por el saver (¿subconjunto del ZPD del cuerpo?).
- Lista completa de los 10 símbolos de DLNA exclusivos de la A6000.
- Enumeración real de dispositivos (no hay `libgps_rsrc` funcional en A6000 sin hardware).

## 6. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s72_wlan.py -q
```
