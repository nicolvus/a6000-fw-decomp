# Topología `0x2a` del pin YC del grabador — sesión 14

Alcance: análisis estático de `libObj.so` / `libSysDef.so` fw 3.21. Direcciones ELF (Ghidra = ELF + 0x10000; en el texto del decompilado `func_0x…` son VA Ghidra). Evidencia reproducible: `scripts/dump_topology_table.py` → `analysis/topology-table-libobj.json`.

## 0. Corrección de la premisa

**DESCARTADO: «ObjHandover 0x2a».** `ObjHandover` es la categoría `CATEID_HANDOVER = 0x3a4c` (objeto de traspaso NFC/Wi-Fi: `MSGID_REQ_START_COMMUNICATION_EVT`, `GET_BOOT_CONNECT_STATE`). El «0x2a» es el **identificador de topología** (fila 0x2a de la tabla del `TopologyManager`) y la etiqueta `ObjHandover_Create+0x…` de los desensamblados es solo el símbolo exportado más cercano (artefacto de `llvm-objdump`).

## 1. Qué es una «topología» (VERIFICADO)

`libObj.so` contiene un `TopologyManager` (TM) con `TopologyLifeCycle` (LT) y `ObjectLifeCycle` (cadenas `[WRPPR_TOPOLOGY] TM::…/LT::…`, ELF `0xcc32c8…0xcc6666`; código ELF `0x4173a0–0x41c3ac`). Una topología = **un enlace de pines** entre dos objetos MWF. Las crea un *modelo* (UI/estado) llamando a `TM::createTopology` con una lista de ids.

- Tabla: `.rodata` ELF `0xcc4210`, **211 filas × 0x20 B** (`TM::createLifeCycles`, ELF `0x4195c0`, indexa `id*0x20`: `+4` StsId, `+8` objeto origen, `+0x14` objeto destino — VERIFICADO en el decompilado `analysis/ghidra/libobj-tm-4295c0.json`).
- Columnas (8×u32): `pin_type, sts_id, src_obj, src_dir, src_no, dst_obj, dst_dir, dst_no`. `pin_type` ∈ índices de `MwfTbl::m_pinTbl` (libSysDef `0x1b948`): 0 PIN_YC (msg `0x2001`), 2 PANEL, 3 LINE, 4 SOUND, 6 REC_CNT_INFO, 7 PB_CNT_INFO, 8 MEDIA_STATUS, 9 STILL_DATA (`0x2008`), 0xa EDIT_INFO, 0xb CAMERA_STATUS, 0xc IMPORT_CNT, 0xd EXPORT (`0x200c`). Dir: 1 = salida, 0 = entrada, 2 = bidireccional (INFERENCIA por estadística de la tabla; confirmada para el recorder, §3).
- `ObjId` de la tabla **no** es el índice de `m_objTbl` de libSysDef (allí StillRecorder es el 9).

## 2. Identidad de los objetos (por firma de pines)

| ObjId | Objeto | Evidencia | Estado |
|---|---|---|---|
| 11 | ObjStillRecorder | constructor `0x9178f0` crea `ObjPin(0,0,0)` (YC in), `ObjPin(9,0,0)` (STILL_DATA in), `ObjPin(0xd,0,1)` (EXPORT out) = exactamente las firmas de la tabla (`libobj-recorder-ctor-9278f0.json`) | VERIFICADO |
| 8 | ObjCamera | única fuente de STILL_DATA y CAMERA_STATUS; 6 salidas YC | INFERENCIA fuerte |
| 5 | ObjRenderer | 2 YC in, 1 YC out, 2 PANEL out, 2 LINE out = `m_pPinYcIn/YcIn1/YcOut0/PanelOut/PanelOut1/LineOut/LineOut1` del código de ObjRenderer | INFERENCIA fuerte |
| 9 | **ObjEffect** | 6 YC in / 5 YC out; recibe de Camera y Player, entrega a Renderer, MovieRecorder, StillRecorder y Scalar; cadenas `[ObjEffect]… PIN_YC, No:1, PIN_OUT` | INFERENCIA fuerte |
| 12 | ObjPlayer | 2 YC out, PB_CNT in; cadenas `[ObjPlayer] Get PIN(YC)` | INFERENCIA fuerte |
| 10 | ObjMovieRecorder | 2 YC in, 2 SOUND in, REC_CNT out | INFERENCIA |
| 30 | ObjScalar | YC in/out + SOUND + REC_CNT + PB_CNT | INFERENCIA |
| 3 | ObjDisplay | destino de PANEL/LINE de 5 | INFERENCIA |

## 3. La topología `0x2a` (VERIFICADO la fila; INFERENCIA la identidad de los objetos)

Fila ELF `0xcc4750` = `{pin_type 0 (YC), sts_id 6, src 9 (Effect) out#1, dst 11 (StillRecorder) in#0}`.

```
 Player(12) ──0xa1/0x4──┐
                         ▼
 Camera(8) ──0xa────►  ObjEffect(9) ──o0 (0x7)────► Renderer(5) ──PANEL/LINE (5,6)──► Display(3)
                         │  └─o1 ──0xe───► MovieRecorder(10) in0
                         │        ├─0x2a──► StillRecorder(11) in0  ◄── pin YC del recorder (this+0x60)
                         │        └─0x86──► Scalar(30) in0         (y Scalar o0 ─0x85─► Effect i0)
```

Todos los enlaces YC que llegan al recorder: `0x2a` (Effect o1, StsId 6) y `0xb4` (obj 53 o2, StsId 6). **No existe ninguna topología Camera→Recorder en YC**; la cámara solo alimenta al recorder por STILL_DATA (`0x8`: 8→11) o vía el objeto 53 (`0xb0`/`0xb1`).

## 4. Quién construye la topología y cuándo (VERIFICADO)

| Modelo | Lista | Dirección |
|---|---|---|
| **ModelPbCap** | `{topología CntMgr por medio, 0x2a, 0}`; código `0x6135dc` (almacena `0x2a` en `0x613680`, llama a `createTopology` wrapper `0x420630` con evento 6 en `0x613694`) | PbCap |
| ModelRedEye / ModelTrimming / ModelFocusRevision | lista estática `{0xa1, 0x7, 0x5, 0x6, 0x2a}` (`0x62495c`, `0x6ae8d4`, `0x55e0a0`) | edición |
| ModelBootEE (Live View) | lista estática `{0xa, 0x7}` en ELF `0xcdb108` | EE |
| Reproducción base (BigImagePb, Browser, ContShotsPb, PbZoom…) | `{0xa1, 0x7, 0x5, 0x6}` = Player→Effect→Renderer→Display | PB |

- La lista de PbCap se destruye con `0x613718` → wrapper `0x420656` (evento 7).
- `0x2a` **no** está en ninguna lista de modelos de disparo (BootEE, MovieRec, ScalarCameraPatch, StillIntervalRec…): la búsqueda de listas estáticas (34 decodificadas) y dinámicas con constante `0x2a` solo la encuentra en PbCap/RedEye/Trimming/FocusRevision. NO VERIFICADO para Paint/Art/Beauty (listas no localizadas).
- `0x420630` / `0x420656` / `0x420688` = `createTopology` / `destroyTopology` / consulta (`0x415e8c`; PbCap la usa con `{tipo 6 REC_CNT, obj 11, …}` para obtener la topología recorder→CntMgr del medio).

## 5. Ciclo de conexión

1. Un modelo llama `createTopology(evento, lista, 0)` (`0x420630` → `TM::createTopology` `0x41a26c`).
2. TM crea `ObjectLifeCycle` por objeto y `TopologyLifeCycle` por fila (`0x4195c0`: `LT(id, srcLife, dstLife, StsViewer)` ctor `0x42b6c0`).
3. Estados de TM (cadenas `m_state`): `TOP_INCOMPLETE → TOP_OBJ_CREATING → TOP_OBJ_CREATED → TOP_OBJ_STARTING → TOP_OBJ_STARTED → TOP_PIN_CONNECTING → TOP_COMPLETE`; inverso: `TOP_WAIT_INACTIVE → TOP_PIN_DISCONNECTING → TOP_OBJ_STOPPING → TOP_OBJ_DESTROYING`; también `SUSPENDING/RESUMING`.
4. `LT::connectPin` (ELF `0x41c0fc`; única llamada a `MWF::ObjIf::ConnectPin` en `0x41c25e`): construye `ObjMsg{0x1000 tipo, 0x1001 nº, 0x1002 dir}`, `ObjIf::GetPin` en origen y destino y luego `ObjIf::ConnectPin(…, ObjStatusViewer)`; errores `[WRPPR_TOPOLOGY] LT::connectPin() …`.
5. Desconexión: `LT::disconnectPin` → `ObjIf::DisconnectPin`.

## 6. Productor conectado al pin YC del recorder en PbCap

**ObjEffect, pin YC de salida nº 1 (StsId 6).** El recorder (`YcPinReqDeliver` `0x90a668`) envía `ObjMsg(0x2000,0x1011)` por ese pin; lo recibe el parser de comandos de pin YC de ObjEffect (ELF `0x1e9880`, cadena `YcPinCommand[%d]: MSGID_REQ_DELIVER`). Detalle en `analysis/yc-pin-delivery-flow.json`.

## 7. NO VERIFICADO

- Constructor de ObjEffect/ObjRenderer/ObjCamera (la identidad 5/8/9/12 es por firma de pines).
- Listas de topologías de Paint/Art/Beauty y de los modelos de disparo (StillRec, Camera, MovieRec): no se decodificaron las dinámicas.
- Qué sinks son los objetos 0, 46, 53, 59, 56 (53 tiene STILL in/out, 3 YC in y 4 YC out).
- Qué evento concreto de UI dispara `0x6135dc` (acción de estado de PbCap).
