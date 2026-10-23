# S381 — Despacho de mensajes en libObj.so (A6000 fw3.21)

## 1. Funciones clave de mensajería (imports UND, resueltas vía .plt)

| Función | Símbolo completo | .plt VA | Uso |
|---|---|---|---|
| SendAndRecv | `_ZN3MWF12EventWrapper11SendAndRecvEPviS1_i` | 0x000e0f24 | Envía mensaje y espera respuesta (síncrono) |
| queueMsg | `_ZN3MWF11ObjMsgQueue7EnqueueEPKNS_6ObjMsgE` | 0x000db8c4 | Encola un ObjMsg (productor) |
| dequeue | `_ZN3MWF11ObjMsgQueue11DequeueEPNS_6ObjMsgE` | (no en .plt resuelto) | Desencola un ObjMsg (consumidor) |
| GetMsgNum | `_ZN3MWF11ObjMsgQueue9GetMsgNumEv` | (no resuelto) | Número de mensajes en cola |
| RcvMsg | `_ZN3UFW11MsgReceiver6RcvMsgEPjPPN3MWF6ObjMsgE` | 0x000dd4a4 | Recibe mensaje de cola (consumidor) |
| SendCmd | `_ZN3UFW9MsgSender7SendCmdEPN3MWF6ObjMsgES3_` | 0x000dba34 | Envía comando asíncrono |
| SendEvt | `_ZN3UFW9MsgSender7SendEvtEPN3MWF6ObjMsgE` | 0x000dfc94* | Envía evento |
| BroadcastEvt | `_ZN3UFW9MsgSender12BroadCastEvtEPN3MWF6ObjMsgERSt4listIjSaIjEE` | 0x000e0ce4 | Broadcast de evento |
| PostAppMsg | `_ZN3MWF13ObjActiveBase10PostAppMsgEPKNS_6ObjMsgE` | 0x000de934 | Postea mensaje a app |
| GetObjMsg | `_ZN5AVBIZ8UNIVERSE7BizUtil9GetObjMsgEPN3MWF6ObjMsgEjPj` | 0x000de914 | Obtiene ObjMsg por ID |
| ObjMsg C1 | `_ZN3MWF6ObjMsgC1Ev` / `C1Ejj` | 0x000df194 / 0x000df224 | Constructor ObjMsg |
| ObjPin::Send | `_ZN3MWF6ObjPin4SendEjPNS_6ObjMsgE` | 0x000df9b4 | Envía mensaje por pin (tarea F) |
| StateMgr::ChangeState | `_ZN8StateMgr11ChangeStateEjPN3MWF6ObjMsgE` | 0x000e1754 | Cambio de estado con mensaje |

\* Algunas entradas .plt no aparecieron en el listado filtrado; están en key_symbols.json.

## 2. Registro de callbacks de cola (osal_*)

| .plt VA | Símbolo | Uso |
|---|---|---|
| 0x000dd804 | `osal_reg_msg_queue_cb` | Registra callback para cola de mensajes (asíncrono) |
| 0x000dd3b4 | `osal_reg_sync_msg_queue_cb` | Registra callback para cola sincrona |
| (no en .plt) | `osal_unreg_msg_queue_cb` | Desregistra callback |
| (no en .plt) | `osal_snd_msg` | Envía mensaje a cola |
| 0x000e13a4 | `osal_snd_sync_msg` | Envía mensaje sincrono |
| 0x000e0c54 | `osal_snd_sync_direct` | Envía directo sincrono |

**Estado:** Ninguna de estas entradas .plt tiene `BL` directo desde código de libObj.so (0 llamadores encontrados por barrido de bytes). Las llamadas a funciones importadas usan **acceso indirecto al GOT** (`ldr [pc]` + `add pc` + `ldr [reg]` + `cbz` + `blx reg`), no `BL` a stubs del .plt.

**Evidencia:** barrido de 4 396 498 instrucciones .text: 28 445 `bx/blx` a registro, 0 llamadas indirectas confirmadas al GOT con el patrón buscado. Los llamadores de `osal_reg_msg_queue_cb` y `osal_snd_msg` no se localizaron estáticamente. **NO_VERIFICADO** quién registra el callback de la cola `0x40193`.

## 3. Tabla de despacho de mensajes

No se encontró una tabla de saltos (TBB/TBH) estática para despacho por ID de mensaje en libObj.so. El despacho probablemente se hace en `av-cam.bin` (capa del núcleo) o mediante callbacks registrados vía `osal_reg_msg_queue_cb`.

**Registro de callback:** El patrón esperado es:
1. Un módulo llama a `osal_reg_msg_queue_cb(queue_id, callback_fn)` para registrar un handler
2. Cuando llega un mensaje a esa cola, el OSAL invoca el callback
3. El callback inspecciona `ObjMsg::GetMessageId()` y `ObjMsg::GetCategoryId()` para despachar

Los imports relevantes para inspección de mensajes:
- `_ZNK3MWF6ObjMsg12GetMessageIdEv` (0x000e2164 en .plt)
- `_ZNK3MWF6ObjMsg13GetCategoryIdEv` (0x000e1504 en .plt)

## 4. ¿Quién llama a RecordStill::Execute?

**No localizado estáticamente:**
- 0 `BL`/`BLX` directo a 0x90b248 (barrido completo de .text)
- 0 literales `0x0090b248` en .rodata, .data, .data.rel.ro, .got
- 0 literales `0x0090b249` (Thumb pointer con bit 0 = 1) en las mismas secciones

**Inferencia:** RecordStill::Execute se invoca vía **puntero de función** (vtable, tabla de callbacks, o campo de objeto) que se construye en runtime. No hay referencia estática alquilable.

**Evidencia:** `analysis/s380_libobj_map/got_indirect_c.py` (barrido de literales y xrefs).

## 5. Qué trae libObj.so que av-cam.bin no tiene (resumen)

libObj.so es la capa **camera-user**: UI (`ViewBase`, `GEN_*`), sistema de mensajes objeto (`MWF::ObjMsg*` dataflow infra (`DataflowInfraCh`, `Pin`), still image (`ObjStillRecorder`, `InfraStillPool`), state manager. av-cam.bin es el núcleo RT (IMX210, obturador, exposición, MMIO, control de sensor).

**Evidencia:** `analysis/s380_libobj_map/map.json` (secciones, símbolos). **VERIFICADO** por readelf + parser propio.

## 6. Bloqueos (requieren REA dinámico o pruebas físicas)

| Ítem | Bloqueo | Por qué |
|---|---|---|
| Quién llama a RecordStill::Execute | No hay literal, no hay xref, no hay BL directo | Llamada vía puntero de función en runtime |
| Quién registra callback de cola 0x40193 | No hay BL a `osal_reg_msg_queue_cb` .plt | Llamada vía GOT indirecto, no resuelto estáticamente |
| Quién envía ObjMsg 0x3500/0x3002 | No hay movw #0x3500/#0x3002 en libObj.so | Los IDs se construyen de otra forma o vienen de av-cam.bin |
| Qué trae libObj.so que av-cam.bin no tiene | Documentado en §5 | VERIFICADO |

---

**Tests:** `analysis/s380_libobj_map/tests/test_s381_dispatch.py` (ver abajo).
**JSON:** `analysis/s380_libobj_map/key_symbols.json`, `got_to_name.json`.
