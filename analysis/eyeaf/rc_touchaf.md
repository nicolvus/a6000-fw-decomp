# Touch AF en el lado cámara: `libInfraRemoteControlNet.so` (A6000 fw 3.21)

Análisis **estático** (cero escrituras en cámara, firmware o RAM; solo lectura de ficheros y REA/Ghidra headless).
Convención: **VERIFICADO** (bytes o pseudocódigo citados, dirección exacta), **INFERENCIA** (deducción con
evidencia parcial), **NO_VERIFICADO** (no demostrado estáticamente; se indica qué faltaría).

## 0. Objeto y convención de direcciones

| Dato | Valor |
|---|---|
| Fichero | `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libInfraRemoteControlNet.so` |
| sha256 | `4b906c34ccc42679bc5063057a296457db1db8eea3f4ad4bf9e42c379f363ab2` |
| Tamaño / formato | 106 040 B, ELF32 ARM EABI5, `EXEC`, stripped **con `.dynsym` completo** (137 `FUNC`, nombres C++ y locales de módulo visibles) |
| Secciones | `.text` `0x3568–0x10f74`, `.rodata` `0x10f7c–0x16bbe`, `.data` `0x1f6e4–0x2190c`, `.bss` desde `0x2190c` |
| Herramientas | REA/Ghidra headless (`open_binary` una sola vez) + desensamblado Capstone local (Thumb-2) + volcados de tablas de `.data` |

> **Convención de direcciones.** Todas las direcciones de este informe son **vaddr del ELF** (que en este
> binario coincide con el *file offset* en las secciones PROGBITS). REA/Ghidra **suma `0x10000`**
> (p. ej. `RcWebAPIFunc` = ELF `0xfc2c` = REA `0x1fc2c`; `DAT_00036813` de REA = ELF `0x26813`).
> Los símbolos de `.dynsym` llevan el bit Thumb (`st_value` impar); la dirección real es `st_value & ~1`.

## 1. Respuesta corta

- **IDs del mensaje** (espacio `DefInfraRemoteControlNet`/`DefWebApi::WebApiMid`, campo `+0x00` del `WebApiMsg`):
  `MID_REQ_SET_TOUCH_AF_POSITION_EVT = 0x8f` (143), `MID_REQ_CANCEL_TOUCH_AF_POSITION_EVT = 0x92` (146),
  y **get = `0x95`** (149) — este último **sin** cadena `MSGID_REQ_GET_TOUCH_AF_*`; se identifica por el
  `case 0x95` de `PsmRcWebAPIGetEvt` que llama a la traza `PsmRcWebAPIGetTouchAFPosition` (str `0x15339`).
  Respuestas: `0x90`, `0x93`, `0x96`. **VERIFICADO**
- **Payload**: un único `u32` en `msg+0x0c`, empaquetado 16:16
  `val = (u16)(x*100) << 16 | (u16)(y*100)`; **x en `[31:16]`, y en `[15:0]`, escala 0…10000 = %·100**.
  La cámara **no** lo descompone: lo reenvía íntegro como valor de una propiedad de dispositivo. **VERIFICADO**
- **Disponibilidad de `setTouchAFPosition` (id 45 = `0x2d`)**: aparece en `getAvailableApiList` **si y solo si**
  `s_MethodValsTable[22].b1 (AvailableValid) ≠ 0` **y** `s_MethodValsTable[22].b3 (enaDisp) == 0`, con
  `b0 (SupportValid) = 1` fijo en el inicializador. `b1/b3` solo los escribe
  `RcWebAPIEditMethodValsTable(true, enaDisp, 0x2d)`, invocado desde `PsmRcCameraStateSetSupport(0x55000000, enaDisp)`,
  es decir **desde el estado que reporta la cámara** (`SUPPORT TOUCH_AF` con valor 1 → publica 45,46,47;
  valor 4 → publica solo 46; valor 2 → no publica nada). **VERIFICADO (mecanismo)**;
  qué valor manda la cámara en cada modo: **NO_VERIFICADO**.
- **Traza `SUPPORT TOUCH_AF : %x.%x`** (str `0x140be`): imprime **`id` de la propiedad de estado y su `valor`**
  — `(0x55000000, 1|2|4)` —, **no** un “flag de soporte + modo de área”. **VERIFICADO**
- **Por dentro** no hay “mover el marco” ni “disparar AF” separados: hay **una escritura de propiedad**
  `MWF::ObjMsg(MID 0x3a4a)` con `PARAM 0x1003 = 0x55000001` (set) / `0x55000002` (cancel) y
  `PARAM 0x1005 = val`, enviada **síncrona** como evento `0x169`. La ejecución del AF ocurre en el consumidor
  de `MID 0x3a4a` (fuera de este binario). **VERIFICADO (emisión) / NO_VERIFICADO (consumidor)**
- **`getTouchAFPosition`** devuelve **solo un bool `set`** (= `estado == 8`), calculado con el último estado
  `0x55000007/0x55000008` recibido. **Nunca devuelve coordenadas** → `touchCoordinates` vacío en orb-server.
  **VERIFICADO**
- **Canal**: este librería consume **mensajes osal/MWF** (`osal_reg_msg_queue_cb`, `osal_snd_msg`,
  `osal_snd_sync_msg`; colas `0x17684a6`, `0x31920`, `0x31928`). El punto de entrada externo es
  `libInfraWebApi.so` (`WebApiUser::WebApi3::wa_job_setTouchAFPosition_*`, `OrbSocket::SocketServer/Client`)
  sobre socket Unix. **No hay ruta binder**; desde una app Android *de la cámara* la vía real es el
  JSON-RPC de Smart Remote Control (`setTouchAFPosition`), igual que desde el PC.

## 2. Tabla de funciones (direcciones ELF de `.text`)

| Dirección | Tamaño | Símbolo (dynsym o REA) | Qué hace / evidencia |
|---|---|---|---|
| `0x5641` | 416 | `InfraRemoteControlNetMainThread` | Bucle principal: `osal_rcv_msg_tmo(DAT_000319d0)` → `PsmRcMainThreadProcMsg` (0x1000/0x1002/0x5000/0x6000) |
| `0x4bb4` | 180 | `RcApiRecvWebApiCmpToApi` | `osal_rcv_msg_tmo(DAT_00031920, …, 3000)`; copia `0x610` B (respuesta WebApi) |
| `0x4b10` | 164 | `RcApiSendWebApiCmpToMain` | `osal_valloc_msg_wait(DAT_00031920)`, `memcpy 0x610`, `osal_snd_msg` → **respuesta al peer WebApi** |
| `0x4d99` | 252 | `RcApiSendMsgWebAPI` | `osal_snd_sync_msg(0x17684a6, …)` con `mid 0x17684a5`, msg de `0x610` B |
| `0x4c69` | 304 | `RcApiSendEventObj` | `osal_snd_sync_msg` a la cola de eventos (`DAT_00031918` para `0x169`) |
| `0xfc2c` | 4008 | `RcWebAPIFunc` | **Dispatcher de peticiones**. `case 0x8f` → str `0x166ff` `MSGID_REQ_SET_TOUCH_AF_POSITION_EVT`; `case 0x92` → str `0x16769`; `case 0x98` = SET_CAMERA_FUNCTION, etc. |
| `0xd050` | 7814 (3 rangos) | `PsmRcWebAPIGetEvt` | **Dispatcher de lecturas**. `case 0x95` → `PsmRcWebAPIGetTouchAFPosition` (str `0x15339`) |
| `0x87b4` | 580 | `RcCameraStateSetParameterFromWebApi` | Traduce `webApiMid`→ escritura de propiedad; set: traza `0x13848`, valor `msg+0xc` (`ldr r4,[r6,#0xc]` @`0x890a`) |
| `0x6c28` | 246 | `PsmRcCameraStateSendDeviceProperty` (REA `FUN_00016c28`) | `ObjMsg(0x3a4a, 0x1001000)` + `AddParam(0x1001/0x1005/0x1003)` + `RcApiSendEventObj(0x169)` |
| `0x8ed9` | 9688 (8 rangos) | `RcCameraStateSetParameter`; contiene `PsmRcCameraStateSetCameraStatus` | Decodifica el *feed* de estado: tipo `1`=SUPPORT, `2`=NOT_SUPPORT, `4`=ENABLE_DISPLAY_ONLY; grupo `0x55000000` → traza `SUPPORT TOUCH_AF` (str `0x140be`) |
| `0x65b0` | 737 | `PsmRcCameraStateSetSupport` (REA `FUN_000165b0`) | Marca soporte + `RcWebAPIEditMethodValsTable(true, enaDisp, s_ValsTable[+0xc])` |
| `0x6900` | 709 | `PsmRcCameraStateSetNotSupport` (REA `FUN_00016900`) | Igual con `false`; retira del `s_MethodValsTable` |
| `0xfb1d` | 272 | `PsmRcWebAPIEditAvailableApiList` | Construye la lista publicada: recorre `s_MethodValsTable` (28 entradas de 20 B) y escribe ids en `DAT_0003698c`, contador en `DAT_00036988` |
| `0x10d6d` | 148 | `RcWebAPIEditMethodValsTable(bool,bool,int)` | Busca entrada por `+4 == id`; escribe `+1=bEnable`, `+2=1`, `+3=bEnaDisp` |
| `0xc448` | 1052 | `PsmRcWebAPIIsAcceptableMethod` (REA `FUN_0001c448`) | `msgid→tabla`: `0x8f → 0x2d`; exige `b0` y `b1`; si no, ret `-5`/`-7` |
| `0xbf68` | 160 | `PsmRcWebAPISearchMethodFromMethodValsTable` | Búsqueda lineal por id en `s_MethodValsTable` |
| `0xcc50` | 892 | `PsmRcWebApiEvtManage_add` (REA `FUN_0001cc50`) | Validación + alta de evento pendiente + timer `30 000 000` µs |
| `0xfae5` | 56 | `RcWebApiEvtManage_del` | `→ FUN_0001f148`; cierra el evento pendiente y responde |
| `0x10d49` | 36 | `PsmRcWebAPICopyAvailableApiList` | `memcpy(…, 0x100)` de la lista |

## 3. Q1 — IDs numéricos y layout del payload

### 3.1 IDs (VERIFICADO)

Los tres métodos están en **`s_TimerValsTable`** (`0x20e00`, 81 entradas × 28 B, `.data`):

| Fila | Dirección | `{+0 req, +4 resObj, +8 res, +0xc PRM, +0x10 cat, +0x14 ResObjCmd, +0x18 ResAppId}` |
|---|---|---|
| 61 | `0x214ac` | `{0x8f, 1, 0x90, 0x8e, 0x54, 0x2005, 0x55000003}` |
| 62 | `0x214c8` | `{0x92, 1, 0x93, 0x91, 0x54, 0x2005, 0x55000005}` |
| 63 | `0x214e4` | `{0x95, 0, 0x96, 0x94, 0x54, 0, 0}` |

| Método (JSON) | REQ | RES | PRM | API id publicado | ResObjCmd | ResAppId |
|---|---|---|---|---|---|---|
| `setTouchAFPosition` | `0x8f` | `0x90` | `0x8e` | `0x2d` (45) | `0x2005` | `0x55000003` |
| `cancelTouchAFPosition` | `0x92` | `0x93` | `0x91` | `0x2e` (46) | `0x2005` | `0x55000005` |
| `getTouchAFPosition` | `0x95` | `0x96` | `0x94` | `0x2f` (47) | — | — |

Cadenas exactas (ELF):
- `0x166ff` `[RC_D]: MSGID_REQ_SET_TOUCH_AF_POSITION_EVT` (xref en `0x10538`, `case 0x8f` de `RcWebAPIFunc`)
- `0x1672b` `[RC_W]: MSGID_REQ_SET_TOUCH_AF_POSITION_EVT - Parameter ERROR`
- `0x16769` `[RC_D]: MSGID_REQ_CANCEL_TOUCH_AF_POSITION_EVT` (xref en `0x10576`, `case 0x92`)
- `0x16798` `[RC_W]: MSGID_REQ_CANCEL_TOUCH_AF_POSITION_EVT - Parameter ERROR`
- `0x15339` `PsmRcWebAPIGetTouchAFPosition` (xref en `0xee3e`, `case 0x95`)

Confirmación cruzada del emparejamiento con la numeración de orb (**VERIFICADO**):
`libInfraWebApi.so` (lado cámara, cara a orb) contiene `liborbEvtCmdTbl` en **`0x2d5d4`**, cuádruplas
`{cmd, evt, cmp, param}`; filas 45–47 (fichero `0x258a4`, `0x258b4`, `0x258c4`):
`{0x192,0x193,0x194,0x8e}`, `{0x195,0x196,0x197,0x91}`, `{0x198,0x199,0x19a,0x94}`.
La columna **`param` (0x8e/0x91/0x94) es exactamente el `PRM` de esta librería**, y
`msgid_cámara = PRM + 1` en las tres filas (relación que también se cumple en filas vecinas, p. ej.
`{0x186,…,0x82}` → `0x83` `MSGID_REQ_SET_FOCUS_MODE_EVT`). **Corrige** el `0x8d/0x90/0x93` de
`analysis/eyeaf/orb_touchaf.md` (error de una unidad).

### 3.2 Layout del payload (VERIFICADO)

`WebApiMsg`/`WebApiIntMsg` de `0x620` B; offsets usados por este binario:

| Offset | Campo | Evidencia |
|---|---|---|
| `+0x00` | `msgid` (webApiMid) | `switch(*(int*)param_1)` en `RcWebAPIFunc` `0xfc2c` |
| `+0x08` | `paramid`/PRM (id de evento de la orden) | `osal`/`RcWebAPI…`; `s_TimerValsTable+0xc` |
| `+0x0c` | **payload u32** (`val`) para set/cancel | `ldr r4,[r6,#0xc]` (`0x890a`), `ldr r5,[r6,#0xc]` (`0x8900`) |
| `+0x10` | respuesta (payload de `RES`) | `*(int*)(param_2+0x10)` en `case 0x95`; `local_664/660` en `RcWebAPIFunc` |
| `+0x14` | bool de respuesta (lo que orb lee como `AFResult`) | lectura en orb `0x1a7820`; aquí `local_58..` |

Traza → campo concreto, `RcCameraStateSetParameterFromWebApi` (`0x87b4`):

```c
/* case 0x8f (ELF 0x8904-0x8934) */
uVar6 = *(uint *)(param_1 + 0xc);                      /* val, ldr r4,[r6,#0xc] @0x890a */
FUN_000160b4(..., "[RC_D]: Called %s, SET_TOUCH_AF_POSITION value %x\n",   /* str 0x13848 */
             "RcCameraStateSetParameterFromWebApi", uVar6);
iVar2 = 0;                                             /* sub-id 0 → fila s_ValsTable @0x1fe28 */
...
/* fin del recorrido de s_ValsTable (ELF 0x89a0) */
else if (r3 == 0x8f && r5 == 0)  FUN_00016c28(0x55000001, r4);   /* ldr r0,[literal @0x89f8] = 0x55000001 */
else if (r3 == 0x92 && r5 == 1)  FUN_00016c28(0x55000002, r4);   /* literal @0x89fc = 0x55000002 */
else                             FUN_00016c28(s_ValsTable[idx].viewID, r4);
```

- **x** y **y** viajan ya empaquetados; el lado cámara **no** aplica ninguna escala ni recorte:
  el `u32` de `+0x0c` es literalmente el `0x1005` de la propiedad. **VERIFICADO**
- Origen del empaquetado (lado orb, ya documentado): `val = (u16)(x*100) << 16 | (u16)(y*100)`
  sobre `double` en porcentaje 0…100 (`orb_touchaf.md` §3). **VERIFICADO (orb)**
- `cancelTouchAFPosition` envía `val` = lo que traiga `msg+0xc`; orb manda `0` (no hay coordenadas). **INFERENCIA fuerte**

## 4. Q2 — Condición exacta de `setTouchAFPosition` (id 45) en `getAvailableApiList`

### 4.1 Tabla que decide (`s_MethodValsTable`, ELF `0x216dc`, `.data`, 28 × 20 B) — VERIFICADO

Entrada **22**: bytes `01 00 01 00 | 2d 00 00 00 | 2e 00 00 00 | 2f 00 00 00 | ff ff ff ff`
(fichero `0x196dc + 22·20 = 0x19894`), es decir:

| `+0` b0 `SupportValid` | `+1` b1 `AvailableValid` | `+2` b2 (valid/ViewResponse) | `+3` b3 `enaDisp` | ids publicables |
|---|---|---|---|---|
| **1** (constante de inicialización) | **0** (⇒ id 45 oculto al arrancar) | 1 | 0 | `0x2d`, `0x2e`, `0x2f`, `—` |

### 4.2 Código de la lista (`PsmRcWebAPIEditAvailableApiList`, `0xfb1d`) — VERIFICADO

```c
if (b1 == 0 || b0 == 0) {                       /* (int)piVar2 + -0xf == entry+1 ; piVar2[-4] = entry+0 */
    if (b2 != 0 && entry[4] != -1 && b3 == 0)   /* (*piVar2 != -1 && entry+3 == 0) */
        emit(entry[4]);                          /* aquí entry[4] == -1 → nada */
} else {                                         /* b0 != 0 && b1 != 0 */
    if (b3 == 0) emit(entry[1]);                /* 0x2d */
    if (entry[2] != -1) emit(entry[2]);          /* 0x2e */
    if (entry[3] != -1 && b3 == 0) emit(entry[3]); /* 0x2f */
    if (entry[4] != -1) emit(entry[4]);
}
```
Emitir = `(&DAT_0003698c)[DAT_00036988++] = id` (64 slots; traza `CNT:%d(MAX:34)`, str `0x14d71`).

**Condición exacta de id 45: `b1 ≠ 0 ∧ b3 == 0`** (con `b0 = 1` siempre).
Consecuencias verificadas:
- `b3 == 0` → publica **45, 46, 47**;
- `b3 == 1` → publica **solo 46**;
- `b1 == 0` → **no publica ninguno** de los tres.

### 4.3 Quién mueve `b1`/`b3` — VERIFICADO

```c
/* RcWebAPIEditMethodValsTable(bool ena, bool enaDisp, int id)  0x10d6d */
entry = find(s_MethodValsTable, id);        /* coincide con entry+4 */
entry[1] = ena;   entry[2] = 1;   entry[3] = enaDisp;
```
Único invocador relevante (`RcWebAPIEditMethodValsTable` sólo se llama desde 12 sitios; los de este grupo
pasan `s_ValsTable[idx]+0xc`):

```c
/* PsmRcCameraStateSetSupport(id, enaDisp)  — 0x65b0, llamada desde 0x8ed9 @ ELF 0xa0f4 */
idx = find(s_ValsTable, id);                        /* id == +0x04 */
s_ValsTable[idx].supported = 1;  s_ValsTable[idx].enaDisp = 1;
...
RcWebAPIEditMethodValsTable(true, enaDisp, s_ValsTable[idx].id_api);   /* 0x2d si id == 0x55000000 */
```
y el llamador (dentro de `PsmRcCameraStateSetCameraStatus`, en `RcCameraStateSetParameter` `0x8ed9`):

```c
if (valor == 1) { /* DEF_..._SUPPORT */                 FUN_000165b0(id, 0); }   /* ELF 0xa0c6 */
else if (valor == 2) { /* NOT_SUPPORT */                FUN_00016900(id, (id & 0xff000000) == 0x0d000000); }
else if (valor == 4) { /* ENABLE_DISPLAY_ONLY */        FUN_000165b0(id, 1); }   /* ELF 0xa0f4 */
else  traza "[RC_E]: DEF_REMOTE_APP_PARAM_TYPE_SUPPORT:%x"
```
Ramas exactas del grupo en el `switch` de estado (`0x8ed9`, ELF `0x9fda-0xa02c`) — **VERIFICADO**:

```c
else if ((id & 0xff000000) == 0x55000000) {   /* cmp r2,#0x55000000 @0x9fda */
    trace("[RC_D]: Called %s SUPPORT TOUCH_AF : %x.%x", "PsmRcCameraStateSetCameraStatus", id, valor);
    if (id == 0x55000000)
        St_SupportedAPI_set_BITs(&DAT_00031b1c, 0x1000, valor);   /* 1/4 ponen bit, 2 lo quitan */
    DAT_00031b14 |= 0x1000;                                      /* cambio pendiente */
}
...
if ((flags_id != DAT_00031b10) || (flags_chg != DAT_00031b14)) {
    trace("[RC_D]: Called %s SUPPORT:GE_CHANGE1_AVAILABLEAPILIST", ...);
    DAT_00031b10 |= 2;                    /* avisa al cliente: recalcula availableApiList */
}
```
`St_SupportedAPI_set_BITs(p,bit,valor)` (`0x7971`): `valor==1 || valor==4 → *p |= bit`; `valor==2 → *p &= ~bit`.
Retransmitido por `PsmRcCameraStateChangeAvailableApiList` (`0xb4b1`) → `RcWebAPISendChangeParametersCmd`.

**Respuesta a “¿qué son los dos valores de `SUPPORT TOUCH_AF : %x.%x`?”**: `(%x1, %x2) = (id de item de
estado, valor)`, con `id = 0x55000000` y `valor ∈ {1 (SUPPORT), 2 (NOT_SUPPORT), 4 (ENABLE_DISPLAY_ONLY)}`;
**no** es “flag de soporte + modo de área de AF”. El “modo/área” no aparece en este punto: los únicos
items del grupo con semántica propia son `0x55000001` (set), `0x55000002` (cancel), `0x55000003/0x55000004`
(resultado de set, valores 2/3), `0x55000005/0x55000006` (resultado de cancel, valores 4/5) y
`0x55000007/0x55000008` (estado del marco, bytes 7/8).

### 4.4 Gate de ejecución (independiente de la lista) — VERIFICADO

`PsmRcWebAPIIsAcceptableMethod` (`0xc448`) mapea `msgid → id de tabla` (`0x8f → 0x2d`, `0x92 → 0x01`? no:
`0x92` no está en el mapa → "Not Check" ⇒ pasa) y exige, vía `PsmRcWebAPISearchMethodFromMethodValsTable`:

```c
if (entry[0] == 0) { ret = -5;  trace "SupportValid FALSE"; }   /* b0 */
if (entry[1] == 0) { ret = -7 cuando entry[2] == 0; trace "AvailableValid FALSE"/"ViewResponse FALSE"; }
```
⇒ Aunque el método no esté en `availableApiList`, la llamada devuelve `-5` “Not Supported or Available method”
(`PsmRcWebAPIGetEvt`/`RcWebAPI…` traza en `0xcc50` → `uVar2=8`).

## 5. Q3 — Qué hace la orden por dentro (capa cámara)

Cadena completa, con instrucciones:

1. `RcWebAPIFunc` `case 0x8f` (ELF `0x1052e`): `FUN_0001cc50(msg)` (validación) y, si 0,
   `RcCameraStateSetParameterFromWebApi(msg)`. **VERIFICADO**
2. `RcCameraStateSetParameterFromWebApi` (`0x87b4`): `val = msg+0x0c` → `FUN_00016c28(0x55000001, val)`;
   para `0x92`: `FUN_00016c28(0x55000002, val)`. **VERIFICADO**
3. `PsmRcCameraStateSendDeviceProperty` (`0x6c28`, ELF `0x6c48-0x6ccc`):

```c
MWF::ObjMsg::ObjMsg(msg, /*mid*/ 0x3a4a, /*param*/ 0x01001000);   /* movw r1,#0x3a4a @0x6c48 */
ParamStd<uchar>::ParamStd(1);                AddParam(msg, 0x1001);   /* 1 byte = 1 */
uint v[1] = { valor };  ParamArray<uint> p1(v);  AddParam(msg, 0x1005);   /* valor (val) */
uint i[1] = { id   };   ParamArray<uint> p2(i);  AddParam(msg, 0x1003);   /* 0x55000001/2 */
RcApiSendEventObj(0x169, {0x3002, &msg});                     /* osal_snd_sync_msg */
```
| Parámetro MWF | Contenido |
|---|---|
| **MID** | `0x3a4a` |
| `PARAM 0x1001` | `uchar = 1` |
| `PARAM 0x1003` | `u32 id` = **`0x55000001`** (set) / **`0x55000002`** (cancel) |
| `PARAM 0x1005` | `u32 valor` = `val` empaquetado (x<<16 \| y) |

4. **`¿mover` vs `enfocar`?** En esta librería **no se distinguen**: no existe ningún MID de “AF start”
   asociado a touch AF; la única orden es la escritura de propiedad. `AF` real (medición, reencuadre) ocurre
   en el consumidor de `MID 0x3a4a`, **fuera de este binario** → **NO_VERIFICADO** aquí.
5. **Completado**: `RcWebApiEvtManage_add` (`0xcc50`) dejó el evento pendiente con `ResObjCmd = 0x2005` y
   `ResAppId = 0x55000003` (set) / `0x55000005` (cancel) y un timer de 30 s. Cuando el *feed* de estado trae
   `0x55000003..0x55000006`, `RcCameraStateSetParameter` los traduce y cierra el evento:

```c
case 0x55000003: appId = 0x55000003; valor = 2; break;   /* ELF 0xae?? — tabla de 4 casos */
case 0x55000004: appId = 0x55000003; valor = 3; break;
case 0x55000005: appId = 0x55000005; valor = 4; break;
case 0x55000006: appId = 0x55000005; valor = 5; break;
trace "[RC_D]: Called %s TOUCH_AF parm.appId: %x";
RcWebApiEvtManage_del({objCmd=0x2005, appId, valor, webApiId}, 0);   /* 0xfae5 → 0xf148 */
```
⇒ el “resultado” del touch AF se construye **a partir de un código de estado 2/3 (set) o 4/5 (cancel)**,
no de una medición devuelta por la orden. **VERIFICADO (flujo)**; semántica exacta de 2/3/4/5 y su conversión
al `AFResult` bool que orb lee en `+0x14`: **NO_VERIFICADO** (ocurre en `libInfraWebApi.so`).
6. En éxito, `RcWebAPIFunc` **no** emite su propio frame de respuesta (`local_66c` sigue 0 →
   `RcApiSendMsgWebAPI` no se llama); solo en error de validación emite `RES 0x90` con código negativo
   (ELF `0x10562`: `movs r3,#0x90`). **VERIFICADO**

## 6. Q4 — `PsmRcWebAPIGetTouchAFPosition` (`case 0x95` de `PsmRcWebAPIGetEvt`, ELF `0xee3e`)

```c
/* ELF 0xee46-0xee5c */
r3 = *(u8*)(r7 + 0x4d17);       /* = DAT_00031b08 + 0x4d0b  →  ELF 0x26813  (REA DAT_00036813) */
if (r3 == 8) *(u8*)(r4 + 0x10) = 1;    /* subs r3,#7 ; strb r3,[r4,#0x10] */
else         *(u8*)(r4 + 0x10) = 0;
```
- Devuelve **un solo byte** en `msg+0x10`: `set = (estado == 8)`. **No hay x, y ni array**.
  En orb, `touchCoordinates` se crea como `TypedJsArray<double>` **vacío** y se serializa vacío
  (`GetTouchAFPosition_invoke_cmd` `0x1b756c`): **ambos lados coinciden**. **VERIFICADO**
- El byte de estado se escribe solo desde el *feed* de estado, grupo `0x55000000` (ELF `0xacd0-0xacee`):

```c
if ((id - 0x55000007) <= 1) {           /* subs r2,#7 ; cmp r2,#1 ; bhi  → id ∈ {0x55000007, 0x55000008} */
    trace("[RC_D]: Called %s TOUCH_AF : %x\n", uVar9);        /* str 0x14717 */
    b = id & 0xff;                       /* and r0, r1, #0xff */
    if (DAT_00036813 != b) { DAT_00036813 = b; DAT_00031b14 |= 0x1000; }
}
```
⇒ `set == true` **si y solo si** el último estado de touch AF recibido fue `0x55000008` (OFF = `0x55000007`).
- **Por qué `touchCoordinates` sale vacío en orb-server**: la cámara **nunca almacena ni reenvía** la
  posición (el `val` de set no se guarda en ningún global: se usa y se descarta). **VERIFICADO** para este
  binario; que no exista otro productor fuera de él: **NO_VERIFICADO**.

## 7. Q5 — Canal alternativo desde una app Android de la cámara

- **Transporte real de esta librería**: mensajes **osal/MWF**, no binder:
  `osal_reg_msg_queue_cb` / `osal_snd_msg` / `osal_snd_sync_msg` / `osal_valloc_msg_wait`
  (importadas vía PLT; implementación Linux en `libosal_uipc.so`, socket Unix de dominio).
  Colas usadas: `0x17684a6` (peticiones WebApi, `mid 0x17684a5`), `DAT_00031920` (respuestas WebApi),
  `DAT_00031928` (uipc asíncrono, `0x410` B), `DAT_00031918`/`0x31914` (eventos `0x169`/`0x175`). **VERIFICADO**
- **Punto de entrada desde fuera del módulo**: `RcWebAPIFunc` es un símbolo **global exportado**
  (`.dynsym`) y se invoca vía PLT (`0x3500`); el llamador es el peer WebApi, es decir, **`libInfraWebApi.so`**,
  que sí habla con orb:
  `WebApiUser::WebApi3::wa_job_setTouchAFPosition_{cmd,evt,cmp}` (`0x11e51`, `0x11e0d`, `0x14eb5`),
  `liborbEvtCmdTbl` (`0x2d5d4`) y `OrbSocket::SocketServer/SocketClient` (+`sendMsgToOrb`,
  `getAndDelLiborbEvtRelay`). La unidad que viaja por el socket es `WebApiIntMsg` de **`0x620` B**. **VERIFICADO**
- **¿Binder?** No hay ninguna referencia a binder/libbinder en `libInfraRemoteControlNet.so` ni en
  `libInfraWebApi.so` (imports: `osal_*`, `fprintf/malloc/memcpy/…`, `MWF::ObjMsg`). **VERIFICADO (ausencia
  en imports)**; que un servicio Android lo exponga por otro camino: **NO_VERIFICADO**.
- **¿Desde la app Android de la cámara?** `SmartRemote.odex` **ya** implementa el método
  (`strings`: `---> setTouchAFPosition(x=`, `---> cancelTouchAFPosition()`, `Invoke and wait a TouchAF *CANCEL* call...`,
  `CameraOperationTouchAFPosition$CameraNotificationListener$AFType`), pero lo hace **sobre la API remota
  JSON-RPC** (misma que usa orb-server/el PC), no inyectando el MID interno. Emitir el MID `0x8f`
  “a mano” exigiría escribir un `WebApiMsg` de `0x610` B en la cola osal `0x17684a6`/`0x31920`
  (o el `WebApiIntMsg` de `0x620` B en el socket de `libInfraWebApi`), con los identificadores
  `{REQ 0x8f, PRM 0x8e, payload +0xc}`. **INFERENCIA** (los ids y el struct están verificados; el
  acceso a la cola/socket desde un proceso ajeno no se ha demostrado).
- **Recomendación práctica**: no hay atajo desde Android; el camino estático soportado es
  `setTouchAFPosition` (JSON-RPC) → `libInfraWebApi` → `MID 0x8f` → `MID 0x3a4a`.

## 8. Correcciones y cabos sueltos

| Afirmación previa | Estado tras este análisis |
|---|---|
| `orb_touchaf.md`: “`setEvtParamId(msg,0x192,0x8d)`”, “ACK `0x194/0x8f`” | **Corregido**: el `param` de la fila de `liborbEvtCmdTbl` es **`0x8e`** (fichero `0x258a4`), y el MID interno de esta librería es **`0x8f`** (no `0x8d`). `0x192` es el id de la capa JSON/orb, `0x8f` el de la capa RC. |
| “la lógica de estado está en `PsmRcWebAPIGetTouchAFPosition`” | Es solo el handler de lectura (`case 0x95`); el estado está en `RcCameraStateSetParameterFromWebApi` + `PsmRcCameraStateSetCameraStatus` + `PsmRcCameraStateSendDeviceProperty` |
| `touchCoordinates` vacío | **Explicado**: la cámara no devuelve coordenadas (solo `set: bool`), y orb crea el array vacío |

**NO_VERIFICADO (qué haría falta)**
1. Qué valores `0x55000000/1|2|4` manda realmente la A6000 (depende del objetivo/modo/área de AF): requiere
   traza en cámara (`[RC_D]: … SUPPORT TOUCH_AF`) o `getAvailableApiList` real.
2. Consumidor de `MID 0x3a4a` (¿`Camera::FC`/BIONZ?, ¿`av-cam.bin`?): no está en este ELF; buscar el handler de
   `ObjMsg(0x3a4a)` y el significado de `PARAM 0x1003 = 0x55000001|2` en los módulos de cámara.
3. Semántica de los códigos 2/3/4/5 y su conversión a `AFResult` (bool que lee orb) — está en `libInfraWebApi.so`.
4. Accesibilidad de las colas osal / socket uipc a un proceso Android arbitrario de la cámara.
