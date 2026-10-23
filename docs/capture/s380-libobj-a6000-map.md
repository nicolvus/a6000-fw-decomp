# S380 — Mapa de libObj.so (A6000 fw3.21)

**Auditoría 23-10-2026:** el conteo 1914 y los mapas por stride fijo eran incorrectos. Prevalece el método PLT → GOT corregido de §4; el JSON regenerado separa ambas direcciones. Las métricas de símbolos y secciones se conservan.

**Archivo:** `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so`
**Idéntico a:** `analysis/camera-extract/usr/lib/libObj.so` (17 436 172 B)
**Formato:** ELF32 ARM, DYN (PIE), stripped, base 0x0
**SHA-256:** no calculado en esta sesión (ver S385)

## 1. Mapa de secciones

| Sección | VA | Offset | Size | Flags |
|---|---|---|---|---|
| .gnu.hash | 0x000000d4 | 0x000d4 | 0x3484 | A |
| .dynsym | 0x00003558 | 0x03558 | 0x0e210 | A |
| .dynstr | 0x00011768 | 0x011768 | 0x0231e5 | A |
| .gnu.version | 0x0003494e | 0x03494e | 0x001c42 | A |
| .gnu.version_r | 0x00036590 | 0x036590 | 0x000040 | A |
| .rel.dyn | 0x000365d0 | 0x0365d0 | 0x0a0248 | A |
| .rel.plt | 0x000d6818 | 0x0d6818 | 0x004ba0 | A |
| .init | 0x000db3b8 | 0x0db3b8 | 0x00000a | AX |
| .plt | 0x000db3c4 | 0x0db3c4 | 0x0077a0 | AX |
| .text | 0x000e2b70 | 0x0e2b70 | 0xae6a1c | AX |
| .fini | 0x00bc958c | 0xbc958c | 0x000006 | AX |
| .rodata | 0x00bc9598 | 0xbc9598 | 0x2c8a1a | A |
| .ARM.extab | 0x00e91fb4 | 0xe91fb4 | 0x0cde80 | A |
| .ARM.exidx | 0x00f5fe34 | 0xf5fe34 | 0x06a770 | AL |
| .init_array | 0x00fd25a4 | 0xfca5a4 | 0x00041c | WA |
| .fini_array | 0x00fd29c0 | 0xfca9c0 | 0x000008 | WA |
| .jcr | 0x00fd29c8 | 0xfca9c8 | 0x000004 | WA |
| .data.rel.ro | 0x00fd29d0 | 0xfca9d0 | 0x05a090 | WA |
| .dynamic | 0x0102ca60 | 0x1024a60 | 0x000170 | WA |
| .got | 0x0102cbd0 | 0x1024bd0 | 0x008750 | WA |
| .data | 0x01035320 | 0x102d320 | 0x073588 | WA |
| .bss | 0x010a88a8 | NOBITS | 0x03a328 | WA |

**Segmentos LOAD:**
- LOAD 1: offset 0x0, VA 0x0, size 0xfca5a4 (código + .rodata, R E)
- LOAD 2: offset 0xfca5a4, VA 0xfd25a4, size 0xd6304 (datos + .got + .data + .bss, RW)

**Nota:** Para VA < 0xfca5a4, offset de archivo == VA (primer segmento LOAD, PIE base 0x0).

## 2. Tabla de símbolos dinámicos (.dynsym)

- Total símbolos: 3617
- UND (importados): 1801 (func=1387, obj=35)
- Definidos (exportados): 1816 (func=1771)

**Imports func (UND, STT_FUNC) — 1387 total.** Muestra de relevantes para mensajería/dataflow:

| Símbolo | Notas |
|---|---|
| `_ZN5MprIf11EncodeStillEPNS_16EncodeStillParamE` | MprIf encode still |
| `_ZN5MprIf19MakeWriteStillImageEPNS_20WriteStillImageParamEPN3MPR9StillInfoE` | MprIf write still image |
| `_ZN5MprIf15ReadStillSingleEN3MPR7EntryIdEmPNS_13ReadStillCtrlEPNS0_10BufferAreaE` | MprIf read still |
| `_ZN5MprIf10WriteStillEPNS_15WriteStillParamEPN3MPR9StillInfoEm` | MprIf write still |
| `_ZN3MWF11ObjMsgQueue7EnqueueEPKNS_6ObjMsgE` | queueMsg (enviar mensaje) |
| `_ZN3MWF11ObjMsgQueue11DequeueEPNS_6ObjMsgE` | dequeue |
| `_ZN3MWF11ObjMsgQueue9GetMsgNumEv` | get msg count |
| `_ZN3UFW11MsgSender7SendCmdEPN3MWF6ObjMsgES3_` | enviar comando |
| `_ZN3UFW11MsgSender7SendEvtEPN3MWF6ObjMsgE` | enviar evento |
| `_ZN3UFW11MsgSender12BroadCastEvtEPN3MWF6ObjMsgERSt4listIjSaIjEE` | broadcast evento |
| `_ZN3UFW11MsgReceiver6RcvMsgEPjPPN3MWF6ObjMsgE` | RcvMsg (recibir mensaje) |
| `_ZN3UFW12EventWrapper11SendAndRecvEPviS1_i` | SendAndRecv |
| `osal_reg_msg_queue_cb` | registrar callback de cola |
| `osal_reg_sync_msg_queue_cb` | registrar callback sincrono de cola |
| `osal_unreg_msg_queue_cb` | desregistrar callback |
| `osal_snd_msg` | enviar mensaje (cola) |
| `osal_snd_sync_msg` | enviar mensaje sincrono |
| `osal_snd_sync_direct` | enviar directo sincrono |
| `osal_rcv_msg_tmo` | recibir mensaje con timeout |

**Imports objetos (UND, STT_OBJECT):** 35 (no listados exhaustivamente).

## 3. Exports definidos (STT_FUNC) — 1771 total

Muestra de relevantes para obturador / still / imagen:

| VA | Size | Símbolo |
|---|---|---|
| 0x00913901 | 16 | `ObjStillRecorder_Init` |
| 0x00913911 | 12 | `ObjStillRecorder_Exit` |
| 0x0091391d | 38 | `ObjStillRecorder_Create` |
| 0x00913943 | 14 | `ObjStillRecorder_Destroy` |
| 0x00913951 | 12 | `ObjStillRecorder_RegisterCommand` |
| 0x0091395d | 12 | `ObjStillRecorder_UnregisterCommand` |
| 0x0012c755 | 40 | `_ZN9PrmObjMsgC1EPN3MWF6ObjMsgE` |
| 0x0012c77d | 8 | `_ZNK9PrmObjMsg18getParamTypeObjMsgEv` |
| 0x0012c7d9 | 14 | `_ZN9PrmObjMsg3GETEPK9ParamListm` |
| 0x00815845 | 228 | `_ZN8StateMgr11ChangeStateEjPN3MWF6ObjMsgE` |
| 0x0080592d | 304 | `_ZN10InfraInput17SendEventInitDataEi` |
| 0x0093956d | 8 | `InfraStillPool_RegisterCommand` |
| 0x00939575 | 8 | `InfraStillPool_UnregisterCommand` |
| 0x00939691 | 68 | `InfraStillPool_Init` |
| 0x00939745 | 52 | `InfraStillPool_Exit` |
| 0x00541795 | 34 | `TsDynamicArray_init` |
| 0x00574065 | 54 | `FS_init` |
| 0x00565191 | 144 | `FSS_init` |

**Corrección 23-10-2026:** `0x0090b248` no es export y sus diagnósticos dicen **RecordImage**. La etiqueta histórica `RecordStill::Execute` no está demostrada. RecordStill A6000 está en `0x908afc`; ver [auditoría de contrato](recordstill-contract-audit-2026-10-23.md) y [S382](s382-recordstill-callers.md).

## 4. .plt → nombre (primeras entradas resueltas via .rel.plt)

.rel.plt tiene 2420 relocaciones R_ARM_JUMP_SLOT hacia GOT. Auditoría 23-10-2026: se retira la división por 16 y el mapeo por orden. El PLT contiene **2420 cuerpos ARM de 12 B** y **391 veneers Thumb de 4 B**, además del encabezado de 20 B: `2420*12 + 391*4 + 20 = 30624`. El resolutor sigue las instrucciones hasta el slot GOT; `map.json` separa `got_map` de `plt_map` (2811 direcciones de entrada ARM/Thumb).

Entradas .plt relevantes para mensajería:

| .plt VA | Símbolo |
|---|---|
| 0x000db7c8 | `_ZN3MWF11ObjMsgQueue7EnqueueEPKNS_6ObjMsgE` (queueMsg) |
| 0x000dbc8c | `_ZN3MWF10ObjMsgList6GetMsgEi` |
| 0x000dbe90 | `_ZN12SequenceBase15ReceiveResponseEPN3MWF6ObjMsgE` |
| 0x000dccfc / 0x000dcd00 | `osal_reg_sync_msg_queue_cb` |
| 0x000dcdbc | `_ZN3UFW11MsgReceiver6RcvMsgEPjPPN3MWF6ObjMsgE` (RcvMsg) |
| 0x000dd064 / 0x000dd068 | `osal_reg_msg_queue_cb` |
| 0x000dde10 | `_ZN3MWF13ObjActiveBase10PostAppMsgEPKNS_6ObjMsgE` |
| 0x000dddf8 | `_ZN5AVBIZ8UNIVERSE7BizUtil9GetObjMsgEPN3MWF6ObjMsgEjPj` |
| 0x000de4cc | `_ZN3MWF6ObjMsgC1Ev` |
| 0x000de540 | `_ZN3MWF6ObjMsgC1Ejj` |
| 0x000deb30 | `_ZN3MWF6ObjPin4SendEjPNS_6ObjMsgE` |
| 0x000dfc0c | `_ZN3MWF12EventWrapper11SendAndRecvEPviS1_i` (SendAndRecv) |
| 0x000dff8c / 0x000dff90 | `osal_snd_sync_msg` |
| 0x000e1210 | `_ZN12SequenceBase11SetRcvMsgIdEi` |

## 5. Qué trae libObj.so que av-cam.bin no tiene

libObj.so es la capa **camera-user** (usuario). Contiene que av-cam.bin (firmware del núcleo de cámara, base 0x43541000) no tiene:

1. **Clases de UI/view:** `ViewBase`, `GEN_*` (histogram, bar, icon, lines, calendar, index, button, editbox), `LkmIconguide`, `LkmLineout`, `Model*ToInstance` — todo el sistema de interfaz de usuario de la cámara.
2. **Sistema de mensajes objeto:** `MWF::ObjMsg`, `MWF::ObjMsgQueue`, `MWF::ObjMsgList`, `MWF::ObjActiveBase`, `MWF::ObjIf`, `MWF::ObjPin`, `MWF::EventSender`, `MWF::EventReceiver`, `MWF::EventWrapper` — infraestructura de paso de mensajes entre objetos.
3. **Dataflow infra:** `DataflowInfraCh`, `DataflowInfraSender`, `DataflowInfraReceiver`, `DataflowInfraMsg`, `INFRA_GET_PIN`, `INFRA_CONNECT_PIN`, `INFRA_DISCONNECT_PIN` — canales de datos entre módulos (incluyendo YC/pin para SFRA).
4. **Pin system:** `ObjPin::Send`, `ObjPin::Create`, `UPinCmdHandler` — envío de comandos por pin (relevante para tarea F: entrega de YC a SFRA).
5. **Still image objects:** `ObjStillRecorder`, `InfraStillPool`, `UtilStillSize` — grabación y gestión de imágenes fijas (RecordImage y su helper RecordStill).
6. **State manager:** `StateMgr::ChangeState` — máquina de estados.
7. **Gestión de archivos/archivo:** `FS_init`, `FSS_init`, `Backup_write`, `Backup_reg_cb` — sistema de archivos y backup.

av-cam.bin contiene el núcleo de cámara en tiempo real (IMX210, obturador, exposición, MMIO, control de sensor) — libObj.so no contiene eso.

**Evidencia:** `analysis/s380_libobj_map/map.json`, `key_symbols.json`. **VERIFICADO** por readelf + parser propio.

## 6. Estado del daemon REA para libObj.so

**Auditoría 23-10-2026:** REA abrió el ELF correctamente. La consulta de instrucción expiró tras 300 s y la sesión se cerró. No se demuestra imposibilidad de analizarlo ni se mantiene un bloqueo humano basado en dependencias faltantes.

**Alternativa usada:** bytes, readelf, Capstone y decodificación Thumb compartida. Las 2420 relocaciones GOT y las 2811 direcciones de entrada PLT ARM/Thumb están resueltas; se retira la supuesta ausencia de 506 entradas. Identidad funcional y flujo siguen requiriendo análisis.

---

**Tests:** `analysis/s380_libobj_map/tests/test_s380_map.py` (ver abajo).
**JSON:** `analysis/s380_libobj_map/map.json`, `key_symbols.json`, `got_to_name.json`.
