# S93 — El bus de mensajes OSAL del userland: 16 grupos (GID) y 13 colas (LID)

**Alcance:** línea de ingeniería inversa **general** de la cámara: el **mapa de los servicios que
se comunican por OSAL** en el lado Linux (userland fw3.21), es decir, el "bus" interno de la cámara:
qué grupos de mensajes existen y qué biblioteca los usa. Conecta con S72 (wireless/DLNA), S87
(almacenamiento/MPR) y S71 (detección de caras). No es la línea SilentShutter, ni la montura (S66),
ni el AF, ni ADJ_CMD, ni ZPD, ni ZIT, ni ADF (ese es el lado del firmware de la cámara), ni el API
del SA, ni el visor del LCD/EVF, ni los modos de disparo, ni el IDT, ni AutoFraming.

**Estado:** VERIFICADO = contra bytes/símbolos. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s93_osal_bus.py`.

---

## 1. La convención (VERIFICADO)

El userland usa dos niveles de cola OSAL:

- **GID** (*Group ID*): el grupo de colas de un servicio. 16 nombres distintos.
- **LID** (*Local/Logical ID*): la cola concreta dentro del grupo. 13 nombres distintos.

Todos aparecen **como cadenas dentro de las bibliotecas** (las `.so` están *stripped* de la tabla de
símbolos, pero conservan los nombres de cola en `.rodata`).

## 2. Los 16 grupos (GID) y quién los usa (VERIFICADO)

| grupo | biblioteca(s) | lectura |
|---|---|---|
| `OSAL_MSGQ_GID_AIRPLANE_MODE_SCALAR_API` | `libInfraAirplaneMode.so` | API del modo avión hacia el escalar |
| `OSAL_MSGQ_GID_AIRPLANE_MODE_TEST` | `libInfraAirplaneMode.so` | prueba del modo avión |
| `OSAL_MSGQ_GID_APP_VIEW_SCALAR` | `libObj.so` | la app de vista hacia el escalar |
| `OSAL_MSGQ_GID_CAMERA_RAW_DEVELOP` | `libObj.so` | desarrollo RAW |
| `OSAL_MSGQ_GID_DETECT_FACE` | **`libBizFw.so`** | cola de **detección de caras** (enlace S71) |
| `OSAL_MSGQ_GID_DMM_CTRL` | `libBizFw.so`, `libInfraHdmi.so` | control del gestor de memoria (DMM) |
| `OSAL_MSGQ_GID_GPS_GET` | **`libmpr.so`** | petición de **GPS** (¡la A6000 lo incluye en el firmware!) |
| `OSAL_MSGQ_GID_INFRA_VDF` | `libObj.so` | infraestructura del display (enlace S86) |
| `OSAL_MSGQ_GID_NETSERVICE_SCALAR_API` | `libNetService.so` | API de red hacia el escalar |
| `OSAL_MSGQ_GID_NETSERVICE_SYNC_EMU` | `libNetService.so` | emulación síncrona del servicio de red |
| `OSAL_MSGQ_GID_NETSERVICE_TEST` | `libNetService.so` | pruebas del servicio de red |
| `OSAL_MSGQ_GID_NET_BACKUP_SERVER` | `libObj.so` | servidor de copia de seguridad por red |
| `OSAL_MSGQ_GID_SADRIVER` | `libBizFw.so` | driver del escalar |
| `OSAL_MSGQ_GID_TASK_ADC` | **`libRsrcHotshoe.so`** | tarea ADC del **hotshoe** (enlace S83/ACCY) |
| `OSAL_MSGQ_GID_WLAN_RSRC_DBG` | `libWlanResource.so` | depuración del recurso WLAN (S72) |
| `OSAL_MSGQ_GID_WLAN_RSRC_TEST` | `libWlanResource.so` | pruebas del recurso WLAN |

## 3. Las 13 colas (LID) (VERIFICADO)

| cola | biblioteca | lectura |
|---|---|---|
| `OSAL_MSGQ_LID_AIRPLANE_MODE_API` | `libInfraAirplaneMode.so` | API del modo avión |
| `OSAL_MSGQ_LID_DLNACONTROL_CP` | `libInfraDlnaControl.so` | **DLNA**: control point (S72) |
| `OSAL_MSGQ_LID_DLNACONTROL_MAIN` | `libInfraDlnaControl.so` | DLNA: hilo principal |
| `OSAL_MSGQ_LID_DLNACONTROL_MEDIASVR` | `libInfraDlnaControl.so` | DLNA: servidor multimedia |
| `OSAL_MSGQ_LID_GPS_GET` | `libmpr.so` | obtención de GPS |
| `OSAL_MSGQ_LID_MDNS_CONTROL_MAIN` | `libInfraMDnsControl.so` | **mDNS** (descubrimiento en la red) |
| `OSAL_MSGQ_LID_NETFUNCTIONMGR_MAIN` | `libInfraNetFunctionManager.so` | gestor de funciones de red |
| `OSAL_MSGQ_LID_NETSERVICE_ASYNC_REQ` | `libNetService.so` | petición asíncrona al servicio de red |
| `OSAL_MSGQ_LID_NETSERVICE_SYNC_REQ` | `libNetService.so` | petición síncrona |
| `OSAL_MSGQ_LID_NET_BACKUP_SERVER_INFRA_NET_SERVICE_CMP` | `libObj.so` | servidor de backup ↔ servicio de red |
| `OSAL_MSGQ_LID_R_HOTSHOE_API` | `libRsrcHotshoe.so` | API del recurso hotshoe |
| `OSAL_MSGQ_LID_WEBAPI_MAIN` | `libInfraWebApi.so` | **API web** de la cámara |
| `OSAL_MSGQ_LID_WLAN_RSRC_API` | `libWlanResource.so` | API del recurso WLAN |

## 4. Lo que revela el mapa (VERIFICADO + INFERENCIA)

- El lado Linux de la cámara está organizado en **microservicios** que se hablan por colas OSAL:
  red (`libNetService`), DLNA (`libInfraDlnaControl`), mDNS, hotshoe, modo avión, escalado
  (`libObj`), y el "firmware de negocio" `libBizFw.so`, que es el que **orquesta la detección de
  caras** (`OSAL_MSGQ_GID_DETECT_FACE`) y el driver del escalar (`OSAL_MSGQ_GID_SADRIVER`).
- **La A6000 incluye soporte de GPS en el firmware** (`libgps_rsrc.so` + `OSAL_MSGQ_GID_GPS_GET` en
  `libmpr.so`), aunque no tenga GPS de hardware → es código compartido con la A7S.
- **Existe una API web** (`libInfraWebApi.so`, `OSAL_MSGQ_LID_WEBAPI_MAIN`) y **mDNS**
  (`libInfraMDnsControl.so`): la cámara se anuncia y es controlable por red.
- `OSAL_MSGQ_GID_APP_VIEW_SCALAR` y `OSAL_MSGQ_GID_INFRA_VDF` conectan la app de vista con el
  escalar y con la infraestructura de display (VDF, S86) → el camino "app → escalar → VDF" del
  visor.

## 5. Abierto (NO_VERIFICADO)

- Los **mensajes** concretos que viajan por cada cola (categorías e IDs): no se ha desensamblado
  `libBizFw.so` ni `libNetService.so`.
- Qué servicios atienden `OSAL_MSGQ_GID_CAMERA_RAW_DEVELOP` y `OSAL_MSGQ_GID_NET_BACKUP_SERVER`.
- La relación entre el bus OSAL del userland y el framework ADF del firmware (`av-cam.bin`): ambos
  usan "OSAL" pero no hay evidencia de que compartan el mismo bus.
- El protocolo de la **API web** (`libInfraWebApi.so`).

## 6. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s93_osal_bus.py -q
```
