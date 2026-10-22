# S177 — el módulo `[CAM_FUNC_MGR]` (43 trazas): el **gestor de funciones de cámara** (`Camera::Function`)

> Hito de **ingeniería inversa de firmware** (línea general; sin relación directa con la
> línea del obturador S101/S102). Sólo análisis de bytes: `analysis/rea-independent/input/av-cam.bin`
> (A6000 fw3.21, 11 427 236 B, sha256 `b60c845ccb90c0ff…`), comparado con la
> **A7S fw3.20** y el **A6300 fw2.01**.
> Convención: **vaddr = 0x43541000 + file_offset**.
> Referencias a cadenas: **regla PIC estricta** (canónica del repo,
> `analysis/s106_imaging_cap/pic_xref_methodology.md`).
> Restricciones del proyecto: **sin firmware ejecutado, sin cámara, sin flasheo, sin REA/Ghidra**.
>
> VERIFICADO = contra bytes. INFERENCIA = lectura razonada. **NO VERIFICADO** = pendiente.

---

## 1. Resumen / veredicto

**`[CAM_FUNC_MGR]` es la etiqueta de traza del subsistema `Camera::Function` de la A6000
fw3.21: un *gestor/despachador de funciones de cámara* que implementa el ciclo de vida de
las peticiones y respuestas de la cámara (`Capcon` = *capture controller*), las enruta entre
los cuatro clientes (usuario, proceso de fondo, *release* y núcleo), y las traduce al bus
inter-LSI mediante un *puente* (`LRBridge`).**

Lo esencial del hito (todas las cifras verificadas contra bytes, §7):

| magnitud | valor |
|---|---|
| cadenas con el token `[CAM_FUNC_MGR]` | **43** (43 apariciones = 43 textos distintos) |
| rango de las cadenas | `0x43ca12af` – `0x43cb02f1` |
| sitios de emisión (pares PIC, regla estricta) | **57** |
| funciones emisoras | **25** |
| cadenas muertas (sin referencia) | **1** (`0x43cb02f1`, `Pseudo AF Stop %d`) |
| pares PIC verificados a mano | **57 / 57** (sin reuso de registro) |
| cadenas con **gemelo exacto en `+16`** (el texto sin el prefijo) | **43 / 43** |
| clases RTTI `Camera::Function::*` | **18** (las mismas 18 en las tres fw) |
| entradas de la tabla de funciones | **65** (`{origin, name, id}` en `0x43ff17b8`) |
| `type_id` del puente LRB decodificados | **12** (0..11) |
| diferencial del token `[CAM_FUNC_MGR]` | A6000 fw3.21 **43** / A7S fw3.20 **0** / A6300 fw2.01 **0** |
| textos interiores (sin prefijo) presentes en | A7S **43/43**, A6300 **42/43** |

**Conclusión principal (confirma S130/S128 y corrige la lectura de S83):** el *subsistema*
`Camera::Function` **existe en las tres fw** (mismas 18 clases RTTI, mismo código, mismos
`type_id` del LRB). Lo **propio de la fw3.21 de la A6000 es la instrumentación**: la fw3.21
**duplica** cada traza con una variante **etiquetada** (`[CAM_FUNC_MGR]: …`) que además lleva
**id de módulo (3), nivel (13), fichero y línea**, y **conserva intacta la traza antigua**
(que ahora apunta 16 bytes más allá, al interior del mismo literal). Es el patrón «se
reescribe el logging», medido aquí byte a byte. §6.
Única salvedad: la **tabla de nombres `REQ_*`/`REPLY_*` con su campo `origin`** (65
entradas, §5) **existe en la A6000 fw3.21 y en la A7S fw3.20, pero no en el A6300 fw2.01**
(0 `REPLY_`, 0 `MSG_NONE`, 0 `FUNC <= ` en todo el binario).

---

## 2. Qué es exactamente `[CAM_FUNC_MGR]`

### 2.1 Base textual (sin inventar siglas)

**La sigla no se desarrolla en ninguna cadena**: ni `CAM_FUNC_MGR` ni `MGR` aparecen
expandidos. La identidad del módulo se establece por **RTTI y ficheros fuente**, no por
conjetura:

* **Namespace C++ `Camera::Function`** — 18 clases RTTI (mangled Itanium, formato
  `longitud` + nombre) **en las tres fw**:

  | clase RTTI | vaddr A6000 | vaddr A7S | vaddr A6300 |
  |---|---|---|---|
  | `N6Camera8Function18ExecStateTransBaseE` | `0x43cafc36` | `0x43ca65d9` | `0x43daadb4` |
  | `N6Camera8Function16CapconEventQueueE` | `0x43cafc5d` | `0x43cb1fc2` | `0x43dc4f89` |
  | `N6Camera8Function15EventDispatcherE` | `0x43cafc82` | `0x43ca6600` | `0x43daaddb` |
  | `N6Camera8Function12EventHandlerE` | `0x43cafccd` | `0x43ca664b` | `0x43daae26` |
  | `N6Camera8Function11ExecHandlerE` | `0x43cafcee` | `0x43ca666c` | `0x43daae47` |
  | `N6Camera8Function15ExecModeHandlerE` | `0x43cafd0e` | `0x43ca668c` | `0x43daae67` |
  | `N6Camera8Function18ExecReleaseHandlerE` | `0x43cafdd8` | `0x43ca6747` | `0x43daaf22` |
  | `N6Camera8Function10HandleInfoE` | `0x43cafdff` | `0x43ca676e` | `0x43daaf49` |
  | `N6Camera8Function12ReplyHandlerE` | `0x43cb001c` | `0x43ca6b7b` | `0x43daaf81` |
  | `N6Camera8Function11SendChannelE` | `0x43cb003d` | `0x43ca6b9c` | `0x43daafa2` |
  | `N6Camera8Function17ExecExpFocusTransE` | `0x43cb00e4` | `0x43ca6c0a` | `0x43dab010` |
  | `N6Camera8Function14ExecSleepTransE` | `0x43cb018c` | `0x43ca6c92` | `0x43dab098` |
  | `N6Camera8Function7CamMainE` | `0x43cb021d` | `0x43ca6d22` | `0x43dab128` |
  | `N6Camera8Function7CamUserE` | `0x43cb0313` | `0x43ca6dd8` | `0x43dab1ce` |
  | `N6Camera8Function16CameraBackGroundE` | `0x43cb03a6` | `0x43ca6cef` | `0x43dab0f5` |
  | `N6Camera8Function4FaceE` | `0x43cb03cb` | `0x43ca6e1c` | `0x43dab212` |
  | `N6Camera8Function7ReleaseE` | `0x43cb03f4` | `0x43ca6e45` | `0x43dab23b` |
  | `N6Camera8Function15ExecHandlerBaseE` | `0x43ccabb4` | `0x43cb1fe7` | `0x43dc4fae` |

* **Ficheros fuente** (§4): `Function/FunctionMessage.cpp`, `Function/FunctionNotify.cpp`,
  `Function/FunctionSetParam.cpp`, `Function/LRBridge.cpp`, `EventDispatcher.cpp`,
  `ExecModeHandler.cpp`, `ExecReleaseHandler.cpp`, `RawDevHandler.cpp`,
  `ReplyHandler.cpp`, `SendChannel.cpp`, `api/capcon_api_cam.cpp`,
  `api/capcon_api_businessif.cpp`, `tsk/tsk_capcon_sequence.cpp`,
  `tsk/tsk_rawdev_sequence.cpp`, `wrapper/CamMain.cpp`, `wrapper/CamUser.cpp`,
  `wrapper/CameraBackGround.cpp`, `wrapper/Face.cpp`.

* **Nombres de método** (cadenas `__PRETTY_FUNCTION__` de la zona): `perform`
  (`0x43cafcba`), `addHandler` (`0x43cafcc2`), `executeEvent` (`0x43cafd32`,
  `0x43cafdcb`), `destroyEvent` (`0x43cafd7d`, `0x43cafdcb`), `setReplyOsalId`
  (`0x43cafd8a`), `updateS1State` (`0x43cafd99`), `send` (`0x43cb006d`),
  `CapconExec` (`0x43cb0090`), `CheckTransfer` (`0x43cb020f`),
  `sendMessageToCamUser` (`0x43cb0342`), `CamBackGroundSendMsg` (`0x43cb0357`),
  `CamBackGroundResponseWrapper` (`0x43cb036c`), `tsk_capcon_sequence` (`0x43cb01af`),
  `tsk_rawdev_sequence` (`0x43cb01df`), `CapconReply` (`0x43ca1242`).

* **`Capcon` / `CAPCON`**: 11 apariciones en la A6000 fw3.21, 11 en la A7S fw3.20 y 13 en
  el A6300 fw2.01 → el subsistema de captura se llama `Capcon` en los tres firmwares.

### 2.2 Arquitectura reconstruida (por los bytes)

```
  REQ_*  (usuario / fondo / release)        REPLY_*  (núcleo CAM)
  ┌───────────────────────────┐              ┌───────────────────────────┐
  │ CamUser / CameraBackGround│              │  CamMain  (wrapper/)      │
  │        (wrapper/)         │              │  ReplyHandler, SendChannel│
  └───────────┬───────────────┘              └───────────┬───────────────┘
              │  REQ_*/REPLY_*  (tabla de 65 entradas, §5)
              ▼                                           ▲
      ┌───────────────────────────────────────────────────┴──────────┐
      │  Camera::Function::EventDispatcher / EventHandler /            │
      │  CapconEventQueue / ExecHandler / ExecModeHandler /           │
      │  ExecReleaseHandler / ExecStateTransBase /                     │
      │  ExecExpFocusTrans / ExecSleepTrans / HandleInfo               │
      │  (Function/*.cpp, tsk/tsk_capcon_sequence.cpp)                │
      └───────────────────────────┬───────────────────────────────────┘
                                  │  Translate "APP" messages
                                  ▼
              ┌──────────────────────────────────────────┐
              │  Camera::Function::LRBridge (Function/   │  12 type_id:
              │  LRBridge.cpp) — puente entre LSIs      │  0 REQ_APP_SND
              │  Snd / Rsv  ×  APP / V2ND / FSPSUM /    │  1 APP … 11 FSPSUM_CMP
              │  VSYNC_CUST                              │
              └──────────────────────────────────────────┘
```

### 2.3 El puente `LRBridge` y sus 12 `type_id` (VERIFICADO)

La función **`0x43805ea8`** (Lado *Snd* = envío) y **`0x438066d4`** (lado *Rsv* = recepción)
implementan el puente. Cada rama compara el `type_id` (byte en `[msg+0]`) con un valor
constante; los 12 valores quedan fijados así:

| `type_id` | nombre del mensaje | cmp (sitio exacto) | `Snd` | `Rsv` |
|---|---|---|---|---|
| 0 | `REQ_APP_SND` | `cbz` en `0x43805ec0` | `0x43caf219` | `0x43caf6bb` |
| 1 | `APP` | `cmp r2,#1` en `0x43805ef6` | `0x43caf26f` | `0x43caf711` |
| 2 | `APP_CMP` | `cmp r3,#2` en `0x43805f2a` | `0x43caf2bd` | `0x43caf75f` |
| 3 | `REQ_V2ND_SND` | `cmp r0,#3` en `0x4380601a` | `0x43caf450` | `0x43caf8f2` |
| 4 | `V2ND` | `cmp r3,#4` en `0x4380604e` | `0x43caf4a7` | `0x43caf949` |
| 5 | `V2ND_CMP` | `cmp r3,#5` en `0x43806084` | `0x43caf4f6` | `0x43caf998` |
| 6 | `REQ_VSYNC_CUST_SND` | `cmp r3,#6` en `0x43805f60` | `0x43caf30f` | `0x43caf7b1` |
| 7 | `VSYNC_CUST` | `cmp r3,#7` en `0x43805f9e` | `0x43caf37e` | `0x43caf820` |
| 8 | `VSYNC_CUST_CMP` | `cmp r3,#8` en `0x43805fdc` | `0x43caf3e5` | `0x43caf887` |
| 9 | `REQ_FSPSUM_SND` | `cmp r3,#9` en `0x438060ba` | `0x43caf549` | `0x43caf9eb` |
| 10 (`0xa`) | `FSPSUM` | `cmp r3,#0xa` en `0x438060f0` | `0x43caf5a2` | `0x43cafa44` |
| 11 (`0xb`) | `FSPSUM_CMP` | `cmp r3,#0xb` en `0x43806126` | `0x43caf5f3` | `0x43cafa95` |

Cada rama está habilitada por un bit de máscara en `[obj+0x41]` (`ldrb.w r3,[r5,#0x41]` +
`tst.w r3,#1/#2/#4`, p. ej. `0x43805eb6`). Los campos del mensaje que se imprimen son
`type_id`, `from_lsi` (byte en `[msg+1]`) y `req_seq_id` (u16 en `[msg+2]`); las trazas
`VSYNC_CUST*` añaden `vsync_type` (byte en `[msg+3]`).

Marcadores de temporización del mismo bloque: `LR REQAPP Start/End` (`0x43cafaea`,
`0x43cafafa`), `LR APP Start/End`, `LR APPCMP …`, `LR REQVSC …`, `LR VSC …`, `LR VSCCMP …`,
`LR REQV2 …`, `LR V2 …`, `LR V2 CMP …`, `LR REQFSP …`, `LR FSP …`, `LR FSPCMP …`
(`0x43cafaea`–`0x43cafc28`), referenciados por PIC en `0x43806a30`, `0x43806a66`,
`0x43806d16`, … → son *marcas de entrada/salida* de cada fase del puente.

### 2.4 El despachador de mensajes (VERIFICADO)

`0x43805930` (fichero `Function/LRBridge.cpp`) es el despachador: lee el **tipo de mensaje
u16** en `[msg+2]` (`ldrb r2,[r4,#3]` + `ldrb r3,[r4,#2]` + `orr`, `0x43805992`-`0x43805996`),
le resta `0x3000` (`sub.w r2,r3,#0x3000`, `0x4380599a`), comprueba `cmp r2,#0x30`
(`0x4380599e`) y salta con un **`tbb` de 49 entradas** (`0x438059a2`, tabla en `0x438059a4`)
→ **tipos de bus `0x3000`–`0x3030`**. Casos concretos: `0x302f` → `0x43805fb0` (rama
`VSYNC_CUST` *Snd* del LRB), `0x3019` → `0x43805a36` (rama *Rsv* del LRB); y los ids
`0x3006` y `0x301b` se comparan explícitamente (`0x43805a00`, `0x43805988`).

### 2.5 `SetCapMode` y `CapMode` (VERIFICADO)

`0x43803e2c` (`Function/FunctionSetParam.cpp`) valida el **modo de captura**: lee un byte
`CapMode` de `[obj+8]`, lo contrasta con una máscara de bits (`1 << CapMode` contra una
constante de 32 bits, `0x43803ea2`-`0x43803ea6`), y admite un máximo de `0x1d` (29)
(`cmp r1,#0x1d`, `0x43803e98`). Los valores `3`, `0x17` (23) y `0x1c` (28) tienen
tratamiento especial (`0x43803e6a`-`0x43803e92`). Si la máscara no encaja, se emite
`'[CAM_FUNC_MGR]: SetCapMode:Invalid CapMode[0x%x: %d: %d: %d: %d]'` (`0x43caf036`) con los
cinco valores: `CapMode` (`[obj+8]`), `[obj+9]`, `[obj+0xa]`, `[obj+0xb]` y un u32 empaquetado
con `[obj+0xc..0xf]` (`0x43803eae`-`0x43803ed6`).

### 2.6 Cola de eventos: `receive` antes de `comp` (VERIFICADO)

`0x43803fb8` implementa la **ordenación recepción→completado**: guarda la petición
recibida (`strh r0,[r4,#2]`, `str r1,[r4,#4]`, `strb r7,[r4]`, `0x43803fcc`-`0x43803fd0`) y,
si ya hay una en curso, emite `'… receive[%d,%d] before comp[%d,%d] (QUEUEING)'`
(`0x43caf077`) o `(FAILED)` (`0x43caf0b4`).

### 2.7 Transiciones y cliente `CamMain` (VERIFICADO)

* `0x4380952a` — `Unexpected ExpFocusTransition : message [%x] timing [%d]` (`0x43cb009b`);
* `0x438096ae` — `Unexpected SleepTransition : message [%x] timing [%d]` (`0x43cb010a`);
* `0x43809714` — `unknown message in Imager Sleep Process: %x` (`0x43cb0150`): la función
  ordena el tipo de mensaje con una cadena de comparaciones (`cmp r3,#0x203`,
  `cmp r3,#0x101`, `cmp r3,#0x13`, `cmp r3,#0`, `cmp r3,#0x1c`, `cmp.w r3,#0x100` —
  `0x43809716`-`0x4380973c`): es la **máquina de proceso de sleep del imager**.
* `0x43809c24` (`wrapper/CamMain.cpp`) — `#### Execute unretract command!!` (`0x43cb027c`).
* `0x43809ce8` (`wrapper/CamMain.cpp`) — `IsNeedScanAf (%d)` (`0x43cb02ad`) e
  `IsNeedAe     (%d)` (`0x43cb02cf`): la función traduce un byte de estado a un id de
  mensaje (`movw r1,#0x301d` para `0xa`, `movw r1,#0x3034` para `0x15`,
  `0x43809cf8`/`0x43809d02`) y consulta una bandera `[obj+0xa7] & 0x20`
  (`0x43809d0c`-`0x43809d14`).

---

## 3. Las 43 trazas (dirección exacta + sitio de referencia)

`addr` = dirección de la cadena; `sitio` = dirección del `add rX,pc` (regla PIC estricta,
verificada a mano en §7).

| # | addr | texto | sitio(s) |
|---|---|---|---|
| 1 | `0x43ca12af` | `[CAM_FUNC_MGR]: CAPCON WARNING! FILE:%s LINE=%d func:%s param=%x %x %x` | `0x43787bc4` |
| 2 | `0x43ca12f6` | `[CAM_FUNC_MGR]: SyncProcMargin[usec] HS0:%u HS1:%u HS2:%u HS3@CPU2:%u HS3@CPU0(IDT):%u HS3@CPU3(RCH):%u VDDrive:%u VDPost:%u` | `0x43787c48` |
| 3 | `0x43caefe8` | `[CAM_FUNC_MGR]: ERROR !!! osal_err:0x%04x %s : %d` | `0x43801ac6`, `0x43801b1e`, `0x43801d02`, `0x43801d58`, `0x43805890`, `0x438058e8`, `0x438061e6`, `0x4380623e`, `0x43806422`, `0x4380647a`, `0x438064ea`, `0x43806542` |
| 4 | `0x43caf036` | `[CAM_FUNC_MGR]: SetCapMode:Invalid CapMode[0x%x: %d: %d: %d: %d]` | `0x43803edc` |
| 5 | `0x43caf077` | `[CAM_FUNC_MGR]: receive[%d,%d] before comp[%d,%d] (QUEUEING)` | `0x43803ff0` |
| 6 | `0x43caf0b4` | `[CAM_FUNC_MGR]: receive[%d,%d] before comp[%d,%d] (FAILED)` | `0x4380401e` |
| 7 | `0x43caf136` | `[CAM_FUNC_MGR]: ERROR !!! osalErr:0x%04x %s : %d` | `0x438056d2`, `0x4380579c`, `0x438057c8`, `0x43805820` |
| 8 | `0x43caf17d` | `[CAM_FUNC_MGR]: ERROR !!! LSI_NUM_TYPE:0x%04x %s : %d` | `0x43805736` |
| 9 | `0x43caf1b3` | `[CAM_FUNC_MGR]: UNKNOWN EID !!! type:[0x%02x] %s : %d` | `0x43805a6c` |
| 10 | `0x43caf1e9` | `[CAM_FUNC_MGR]: ERROR !!! type:[0x%02x] %s : %d` | `0x43805ab2` |
| 11 | `0x43caf219` | `[CAM_FUNC_MGR]: [LRB]REQ_APP_SND Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x43805ed6` |
| 12 | `0x43caf26f` | `[CAM_FUNC_MGR]: [LRB]APP Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x43805f0a` |
| 13 | `0x43caf2bd` | `[CAM_FUNC_MGR]: [LRB]APP_CMP Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x43805f40` |
| 14 | `0x43caf30f` | `[CAM_FUNC_MGR]: [LRB]REQ_VSYNC_CUST_SND Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x vsync_type:0x%02x` | `0x43805f7a` |
| 15 | `0x43caf37e` | `[CAM_FUNC_MGR]: [LRB]VSYNC_CUST Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x vsync_type:0x%02x` | `0x43805fb8` |
| 16 | `0x43caf3e5` | `[CAM_FUNC_MGR]: [LRB]VSYNC_CUST_CMP Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x vsync_type:0x%02x` | `0x43805ff6` |
| 17 | `0x43caf450` | `[CAM_FUNC_MGR]: [LRB]REQ_V2ND_SND Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x4380602e` |
| 18 | `0x43caf4a7` | `[CAM_FUNC_MGR]: [LRB]V2ND Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x43806064` |
| 19 | `0x43caf4f6` | `[CAM_FUNC_MGR]: [LRB]V2ND_CMP Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x4380609a` |
| 20 | `0x43caf549` | `[CAM_FUNC_MGR]: [LRB]REQ_FSPSUM_SND Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x438060d0` |
| 21 | `0x43caf5a2` | `[CAM_FUNC_MGR]: [LRB]FSPSUM Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x43806106` |
| 22 | `0x43caf5f3` | `[CAM_FUNC_MGR]: [LRB]FSPSUM_CMP Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x4380613c` |
| 23 | `0x43caf648` | `[CAM_FUNC_MGR]: ERROR !!! LRBridge SndV2ndLatchCmp. %s : %d` | `0x438065ce`, `0x4380663a` |
| 24 | `0x43caf684` | `[CAM_FUNC_MGR]: ERROR !!! LRBridge SndApp2Cmp. %s : %d` | `0x438066a6` |
| 25 | `0x43caf6bb` | `[CAM_FUNC_MGR]: [LRB]REQ_APP_SND Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x43806702` |
| 26 | `0x43caf711` | `[CAM_FUNC_MGR]: [LRB]APP Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x43806736` |
| 27 | `0x43caf75f` | `[CAM_FUNC_MGR]: [LRB]APP_CMP Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x4380676c` |
| 28 | `0x43caf7b1` | `[CAM_FUNC_MGR]: [LRB]REQ_VSYNC_CUST_SND Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x vsync_type:0x%02x` | `0x438067a6` |
| 29 | `0x43caf820` | `[CAM_FUNC_MGR]: [LRB]VSYNC_CUST Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x vsync_type:0x%02x` | `0x438067e4` |
| 30 | `0x43caf887` | `[CAM_FUNC_MGR]: [LRB]VSYNC_CUST_CMP Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x vsync_type:0x%02x` | `0x43806822` |
| 31 | `0x43caf8f2` | `[CAM_FUNC_MGR]: [LRB]REQ_V2ND_SND Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x4380685a` |
| 32 | `0x43caf949` | `[CAM_FUNC_MGR]: [LRB]V2ND Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x43806890` |
| 33 | `0x43caf998` | `[CAM_FUNC_MGR]: [LRB]V2ND_CMP Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x438068c6` |
| 34 | `0x43caf9eb` | `[CAM_FUNC_MGR]: [LRB]REQ_FSPSUM_SND Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x438068fc` |
| 35 | `0x43cafa44` | `[CAM_FUNC_MGR]: [LRB]FSPSUM Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x43806932` |
| 36 | `0x43cafa95` | `[CAM_FUNC_MGR]: [LRB]FSPSUM_CMP Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x` | `0x43806968` |
| 37 | `0x43cb009b` | `[CAM_FUNC_MGR]: Unexpected ExpFocusTransition : message [%x] timing [%d]` | `0x4380953c` |
| 38 | `0x43cb010a` | `[CAM_FUNC_MGR]: Unexpected SleepTransition : message [%x] timing [%d]` | `0x438096c0` |
| 39 | `0x43cb0150` | `[CAM_FUNC_MGR]: unknown message in Imager Sleep Process: %x` | `0x438097c6` |
| 40 | `0x43cb027c` | `[CAM_FUNC_MGR]: #### Execute unretract command!!` | `0x43809c86` |
| 41 | `0x43cb02ad` | `[CAM_FUNC_MGR]: IsNeedScanAf (%d)` | `0x43809d20` |
| 42 | `0x43cb02cf` | `[CAM_FUNC_MGR]: IsNeedAe     (%d)` | `0x43809d42` |
| 43 | `0x43cb02f1` | `[CAM_FUNC_MGR]: Pseudo AF Stop %d` | **— (muerta)** |

Total: **57 sitios** en **25 funciones**. **Una única cadena muerta**: `0x43cb02f1`
(`Pseudo AF Stop %d`) — **0** referencias PIC y **0** punteros absolutos de 4 B en los
11,4 MB; en la A7S está muerta igual (`0x43ca6dc6`, sin referencias).

---

## 4. Mapa función → traza → fichero fuente (25 funciones)

El fichero fuente se atribuye por el **wrapper de traza propio de cada fichero** (cada
`Function/*.cpp` tiene su pequeño helper de log: `bl 0x43805604` en `LRBridge.cpp`,
`bl 0x43803d80` en `FunctionSetParam.cpp`, …) y por la referencia PIC más próxima al
nombre de fichero (`find_pic_targets.py`).

| inicio | nº | fichero fuente | wrapper | cadenas |
|---|---|---|---|---|
| `0x43787b70` | 1 | `api/capcon_api_cam.cpp` | `0x43787ac4` | `0x43ca12af` |
| `0x43787c0e` | 1 | `api/capcon_api_cam.cpp` | `0x43787ac4` | `0x43ca12f6` |
| `0x43801a1c` | 2 | `Function/FunctionNotify.cpp` | `0x4380196c` | `0x43caefe8` |
| `0x43801c48` | 2 | `Function/FunctionNotify.cpp` | `0x4380196c` | `0x43caefe8` |
| `0x43803e2c` | 1 | `Function/FunctionSetParam.cpp` | `0x43803d80` | `0x43caf036` |
| `0x43803fb8` | 2 | `Function/FunctionSetParam.cpp` | `0x43803d80` | `0x43caf077`, `0x43caf0b4` |
| `0x438056b4` | 1 | `Function/LRBridge.cpp` | `0x43805604` | `0x43caf136` |
| `0x43805708` | 1 | `Function/LRBridge.cpp` | `0x43805604` | `0x43caf17d` |
| `0x4380577c` | 2 | `Function/LRBridge.cpp` | `0x43805604` | `0x43caf136` |
| `0x43805808` | 1 | `Function/LRBridge.cpp` | `0x43805604` | `0x43caf136` |
| `0x43805870` | 2 | `Function/LRBridge.cpp` | `0x43805604` | `0x43caefe8` |
| `0x43805930` | 2 | `Function/LRBridge.cpp` | `0x43805604` | `0x43caf1b3`, `0x43caf1e9` |
| `0x43805ea8` | **12** | `Function/LRBridge.cpp` | `0x43805604` | 11–22 |
| `0x438061c4` | 2 | `Function/LRBridge.cpp` | `0x43805604` | `0x43caefe8` |
| `0x43806400` | 2 | `Function/LRBridge.cpp` | `0x43805604` | `0x43caefe8` |
| `0x438064c8` | 2 | `Function/LRBridge.cpp` | `0x43805604` | `0x43caefe8` |
| `0x43806590` | 1 | `Function/LRBridge.cpp` | `0x43805604` | `0x43caf648` |
| `0x438065fc` | 1 | `Function/LRBridge.cpp` | `0x43805604` | `0x43caf648` |
| `0x43806668` | 1 | `Function/LRBridge.cpp` | `0x43805604` | `0x43caf684` |
| `0x438066d4` | **12** | `Function/LRBridge.cpp` | `0x43805604` | 25–36 |
| `0x4380952a` | 1 | `api/capcon_api_businessif.cpp` | `0x4380947c` | `0x43cb009b` |
| `0x438096ae` | 1 | `api/capcon_api_businessif.cpp` | `0x43809600` | `0x43cb010a` |
| `0x43809714` | 1 | `api/capcon_api_businessif.cpp` | `0x43809600` | `0x43cb0150` |
| `0x43809c24` | 1 | `wrapper/CamMain.cpp` | `0x43809a64` | `0x43cb027c` |
| `0x43809ce8` | 2 | `wrapper/CamMain.cpp` | `0x43809a64` | `0x43cb02ad`, `0x43cb02cf` |

Las dos funciones de `api/capcon_api_cam.cpp` son: `0x43787b70` (helper
`CapconWarning(file, line, func, p1, p2, p3)`: construye el texto
`CAPCON WARNING! FILE:%s LINE=%d func:%s` + `   param1=%x, param2=%x param3=%x` y además la
traza etiquetada) y `0x43787c0e` (`SyncProcMargin`: vuelca 8 márgenes de sincronización
—HS0, HS1, HS2, HS3@CPU2, HS3@CPU0(IDT), HS3@CPU3(RCH), VDDrive, VDPost— leídos de una
tabla en `[r3,r2]` con campos u32 en `+0, +4, +8, +0xc, +0x10, +0x14, +0x24, +0x28`).

**Ficheros fuente del subsistema** (18 referencias PIC, todas verificadas; en la A6000
fw3.21 **4 de ellos llevan el directorio `Function/`**):
`api/capcon_api_cam.cpp` `0x43ca124e` · `Function/FunctionMessage.cpp` `0x43caeef6` ·
`Function/FunctionNotify.cpp` `0x43caf01a` · `Function/FunctionSetParam.cpp` `0x43caf0ef` ·
`Function/LRBridge.cpp` `0x43caf167` · `EventDispatcher.cpp` `0x43cafca6` ·
`ExecModeHandler.cpp` `0x43cafd3f` · `ExecReleaseHandler.cpp` `0x43cafda7` ·
`RawDevHandler.cpp` `0x43cafed5` · `ReplyHandler.cpp` `0x43cb000b` ·
`SendChannel.cpp` `0x43cb005d` · `api/capcon_api_businessif.cpp` `0x43cb0072` ·
`tsk/tsk_capcon_sequence.cpp` `0x43cb01c3` · `tsk/tsk_rawdev_sequence.cpp` `0x43cb01f3` ·
`wrapper/CamMain.cpp` `0x43cb0268` · `wrapper/CamUser.cpp` `0x43cb032e` ·
`wrapper/CameraBackGround.cpp` `0x43cb0389` · `wrapper/Face.cpp` `0x43cb03e3`.

---

## 5. La estructura de datos que gestiona: la tabla de 65 funciones

**Tabla en `.data`, base `0x43ff17b8`, paso 12 B, 65 entradas** con la forma

```c
struct FuncEntry { const char *origin; const char *name; u32 id; };
```

* `name` e `id` están **inicializados en el fichero**;
* `origin` se escribe **en runtime** por la función de inicialización `0x43787d88`
  (`add r3,pc` → `0x43ff17c0` en `0x43787d8c`), que llena los 65 campos `origin` con
  `'FUNC <= USER'`, `'FUNC <= BG  '`, `'FUNC <= REL '`, `'FUNC <= CAM '` o `'???         '`.

`origin` = **quién puede emitir esa función** (cliente), `name` = el nombre del mensaje,
`id` = su identificador.

| k | slot | id | origin | name |
|---|---|---|---|---|
| 0 | `0x43ff17b8` | `0x0` | `???         ` | `UNKNOWN` |
| 1 | `0x43ff17c4` | `0x1` | `FUNC <= USER` | `REQ_MOVIE` |
| 2 | `0x43ff17d0` | `0x2` | `FUNC <= USER` | `REQ_MOVIE_REC` |
| 3 | `0x43ff17dc` | `0x3` | `FUNC <= USER` | `REQ_STILL_EE` |
| 4 | `0x43ff17e8` | `0x4` | `FUNC <= BG  ` | `REQ_PB` |
| 5 | `0x43ff17f4` | `0x5` | `FUNC <= BG  ` | `REQ_HOLD` |
| 6 | `0x43ff1800` | `0x6` | `FUNC <= USER` | `REQ_HS_EE` |
| 7 | `0x43ff180c` | `0x7` | `FUNC <= USER` | `REQ_HS_PLAY` |
| 8 | `0x43ff1818` | `0x8` | `FUNC <= USER` | `REQ_PANORAMA_EE` |
| 9 | `0x43ff1824` | `0x9` | `FUNC <= BG  ` | `REQ_POWER_OFF` |
| 10 | `0x43ff1830` | `0xa` | `FUNC <= USER` | `REQ_CUSTOM_WB` |
| 11 | `0x43ff183c` | `0xb` | `FUNC <= USER` | `REQ_GOLF_EE` |
| 12 | `0x43ff1848` | `0xc` | `FUNC <= USER` | `REQ_GOLF_SOUND_DET_END` |
| 13 | `0x43ff1854` | `0xd` | `FUNC <= USER` | `REQ_GOLF_PLAY` |
| 14 | `0x43ff1860` | `0x8101` | `FUNC <= USER` | `REQ_TOUCH_SCAN` |
| 15 | `0x43ff186c` | `0x11` | `FUNC <= USER` | `REQ_TOUCH_NOSCAN` |
| 16 | `0x43ff1878` | `0xe` | `FUNC <= USER` | `REQ_DUALREC_DEV` |
| 17 | `0x43ff1884` | `0x8100` | `FUNC <= USER` | `REQ_MOVIE_EO` |
| 18 | `0x43ff1890` | `0xf` | `FUNC <= USER` | `REQ_BB_OUT` |
| 19 | `0x43ff189c` | `0x8000` | `FUNC <= USER` | `REQ_CLEANING` |
| 20 | `0x43ff18a8` | `0x10` | `FUNC <= USER` | `RAW_CONT_CAP_CANCEL` |
| 21 | `0x43ff18b4` | `0x16` | `FUNC <= USER` | `REQ_AUTO_BB` |
| 22 | `0x43ff18c0` | `0x17` | `FUNC <= USER` | `REQ_SHS_EE` |
| 23 | `0x43ff18cc` | `0x18` | `FUNC <= USER` | `REQ_SHS_REC` |
| 24 | `0x43ff18d8` | `0x19` | `FUNC <= USER` | `REQ_FELOCK_ON` |
| 25 | `0x43ff18e4` | `0x8102` | `FUNC <= USER` | `REQ_FELOCK_OFF` |
| 26 | `0x43ff18f0` | `0x12` | `FUNC <= USER` | `REQ_PREVIEW_MODE` |
| 27 | `0x43ff18fc` | `0x13` | `FUNC <= USER` | `REQ_EXP_FOCUSED_ON` |
| 28 | `0x43ff1908` | `0x15` | `FUNC <= USER` | `REQ_EXP_FOCUSED_OFF` |
| 29 | `0x43ff1914` | `0x100` | `FUNC <= USER` | `REQ_BKF_AF` |
| 30 | `0x43ff1920` | `0x101` | `FUNC <= REL ` | `REQ_CAPTURE_START` |
| 31 | `0x43ff192c` | `0x102` | `FUNC <= REL ` | `REQ_CAPTURE_END` |
| 32 | `0x43ff1938` | `0x103` | `FUNC <= REL ` | `REQ_AF_START` |
| 33 | `0x43ff1944` | `0x8301` | `FUNC <= REL ` | `REQ_AF_STOP` |
| 34 | `0x43ff1950` | `0x8302` | `FUNC <= REL ` | `REQ_AE_START` |
| 35 | `0x43ff195c` | `0x104` | `FUNC <= REL ` | `REQ_AE_STOP` |
| 36 | `0x43ff1968` | `0x300` | `FUNC <= REL ` | `REQ_AF_CHANGE` |
| 37 | `0x43ff1974` | `0x301` | `FUNC <= CAM ` | `REPLY_MOVIE` |
| 38 | `0x43ff1980` | `0x302` | `FUNC <= CAM ` | `REPLY_MOVIE_REC` |
| 39 | `0x43ff198c` | `0x303` | `FUNC <= CAM ` | `REPLY_STILL_EE` |
| 40 | `0x43ff1998` | `0x304` | `FUNC <= CAM ` | `REPLY_PB` |
| 41 | `0x43ff19a4` | `0x305` | `FUNC <= CAM ` | `REPLY_HOLD` |
| 42 | `0x43ff19b0` | `0x306` | `FUNC <= CAM ` | `REPLY_HS_EE` |
| 43 | `0x43ff19bc` | `0x307` | `FUNC <= CAM ` | `REPLY_HS_PLAY` |
| 44 | `0x43ff19c8` | `0x308` | `FUNC <= CAM ` | `REPLY_PANORAMA_EE` |
| 45 | `0x43ff19d4` | `0x309` | `FUNC <= CAM ` | `REPLY_POWER_OFF` |
| 46 | `0x43ff19e0` | `0x30a` | `FUNC <= CAM ` | `REPLY_CUSTOM_WB` |
| 47 | `0x43ff19ec` | `0x30b` | `FUNC <= CAM ` | `REPLY_GOLF_EE` |
| 48 | `0x43ff19f8` | `0x30c` | `FUNC <= CAM ` | `REPLY_GOLF_SOUND_DET_END` |
| 49 | `0x43ff1a04` | `0x30e` | `FUNC <= CAM ` | `REPLY_GOLF_PLAY` |
| 50 | `0x43ff1a10` | `0x310` | `FUNC <= CAM ` | `REPLY_PRELIGHT` |
| 51 | `0x43ff1a1c` | `0x311` | `FUNC <= CAM ` | `REPLY_SCANAF` |
| 52 | `0x43ff1a28` | `0x312` | `FUNC <= CAM ` | `REPLY_S1` |
| 53 | `0x43ff1a34` | `0x313` | `FUNC <= CAM ` | `REPLY_TOUCH_SCAN_1` |
| 54 | `0x43ff1a40` | `0x314` | `FUNC <= CAM ` | `REPLY_TOUCH_SCAN_2` |
| 55 | `0x43ff1a4c` | `0x316` | `FUNC <= CAM ` | `REPLY_TOUCH_SCAN_3` |
| 56 | `0x43ff1a58` | `0x319` | `FUNC <= CAM ` | `REPLY_DUALREC_DEV` |
| 57 | `0x43ff1a64` | `0x31e` | `FUNC <= CAM ` | `REPLY_MOVIE_EO` |
| 58 | `0x43ff1a70` | `0x326` | `FUNC <= CAM ` | `REPLY_AUTO_BB` |
| 59 | `0x43ff1a7c` | `0x327` | `FUNC <= CAM ` | `REPLY_SHS_EE` |
| 60 | `0x43ff1a88` | `0x328` | `FUNC <= CAM ` | `REPLY_SHS_REC` |
| 61 | `0x43ff1a94` | `0xfff` | `FUNC <= CAM ` | `REPLY_FE_LOCK` |
| 62 | `0x43ff1aa0` | `0x329` | `FUNC <= CAM ` | `REPLY_ERR` |
| 63 | `0x43ff1aac` | `0xf00` | `FUNC <= CAM ` | `REPLY_FACE_DET_OFF` |
| 64 | `0x43ff1ab8` | `0x10` | `???         ` | `MSG_NONE` |

**Reparto por origen**: `USER` 26 entradas (peticiones del usuario), `BG` 3 (`REQ_PB`,
`REQ_HOLD`, `REQ_POWER_OFF`), `REL` 7 (`REQ_CAPTURE_START/END`, `REQ_AF_START/STOP`,
`REQ_AE_START/STOP`, `REQ_AF_CHANGE`), `CAM` 27 (todas las `REPLY_*`), `???` 2
(`UNKNOWN`, `MSG_NONE`).

**La misma tabla, byte a byte, existe en la A7S fw3.20**: base `0x43ff65d4`, 65 entradas
con los **mismos nombres y los mismos ids en el mismo orden**, y la **misma función de
inicialización** (`0x437a43c4`, `add r3,pc` → `0x43ff65dc` en `0x437a43c8`, con **los
mismos desplazamientos** `+4, +0x10, +0x1c, +0x40, …, +0x2f8` que en la A6000). La única
diferencia observada es el valor del campo `id` de la **última** entrada (`MSG_NONE`):
`0x10` en la A6000 frente a `0x43fd2020` en la A7S (allí ese palabra queda solapado con el
bloque de nombres RTTI que empieza en `0x43ff68e0` → probablemente un artefacto de
disposición del compilador, no un cambio funcional).

**En el A6300 fw2.01 esta tabla NO existe**: **0** apariciones de `REPLY_`, **0** de
`MSG_NONE`, **0** de `RAW_CONT_CAP_CANCEL` y **0** de `FUNC <= ` en todo el binario (sí
tiene los nombres de tipo del LRB: `REQ_APP_SND`, `REQ_FSPSUM_SND`, `REQ_V2ND_SND`,
`REQ_VSYNC_CUST_SND`). → El *naming* `REQ_*`/`REPLY_*` con origen es propio de la fw3.21 de
la A6000 y de la fw3.20 de la A7S, **no** del A6300 fw2.01.

---

## 6. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAM_FUNC_MGR]` (ocurrencias) | **43** | **0** | **0** |
| cadenas distintas con el token | 43 | 0 | 0 |
| textos interiores (sin prefijo) presentes | — | **43 / 43** | **42 / 43** |
| texto interior ausente | — | — | `Pseudo AF Stop %d` (la cadena muerta) |
| clases RTTI `Camera::Function::*` | 18 | **18** | **18** |
| ficheros `Function/*.cpp` | 4, **con** directorio (`FunctionMessage`, `FunctionNotify`, `FunctionSetParam`, `LRBridge`) | 3, **sin** directorio (`FunctionMessage.cpp` `0x43ca6e60`, `FunctionNotify.cpp` `0x43ca6f4e`, `LRBridge.cpp` `0x43ca708f`) | 2, sin directorio (`FunctionNotify.cpp` `0x43dab34d`, `LRBridge.cpp` `0x43daced6`) |
| ficheros `wrapper/*`, `tsk/*`, `api/*` | 9 | 9 (iguales) | 9 (iguales) |
| entradas de la tabla de funciones | 65 | 65 (idéntica) | **no existe** (0 `REPLY_`, 0 `FUNC <= `) |
| función de init de la tabla | `0x43787d88` | `0x437a43c4` (idéntica) | — |
| `type_id` del LRB | 0..11 | 0..11 (idénticos) | 0..11 (idénticos) |
| traza nueva (wrapper con id de módulo) | 7 wrappers por fichero | — | — |

### 6.1 La prueba de que es un cambio de *logging*, no de código

**(a) El texto es el mismo, sólo cambia el prefijo.** Para **43 de 43** cadenas, los bytes
en `vaddr+16` son **exactamente** el texto sin el prefijo `"[CAM_FUNC_MGR]: "` (16 B), y ese
texto **existe en la A7S** (43/43) y en el A6300 (42/43). Ejemplo:
`0x43caf219` = `"[CAM_FUNC_MGR]: [LRB]REQ_APP_SND Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x"`;
en `0x43caf229` (cadena + 16) empieza `"[LRB]REQ_APP_SND Snd type_id:…"` — el literal
original, en la **misma dirección de la A7S**: `0x43ca7108`.

**(b) El código de llamada es idéntico salvo por una llamada añadida.** En la A6000
(`0x43805ed6`):

```
0x43805ed4  ldr      r3, [pc, #0x28c]
0x43805ed6  add      r3, pc        ; -> 0x43caf219  '[CAM_FUNC_MGR]: [LRB]REQ_APP_SND Snd …'
0x43805ed8  bl       #0x43805604   ; traza NUEVA (modulo=3, nivel=0xd, fichero, linea)
0x43805edc  ldr      r0, [pc, #0x288]
0x43805ee0  add      r0, pc        ; -> 0x43caf229  '[LRB]REQ_APP_SND Snd …'  (= +16)
0x43805ee6  bl       #0x43902718   ; traza VIEJA, intacta
```

En la **A7S** (`0x437ac63e`, el mismo código) sólo existe la traza vieja:

```
0x437ac63a  ldr      r0, [pc, #0x15c]
0x437ac63e  add      r0, pc        ; -> 0x43ca7108  '[LRB]REQ_APP_SND Snd …'
0x437ac642  bl       #0x438f7114   ; traza (única)
```

y en el **A6300** (`0x437f621e`) igual, con `bl #0x43986518`.

**(c) El contenido de la traza nueva es el mismo + 3 cosas nuevas**: *id de módulo*
(`3`), *nivel* (`0xd`), *fichero* y *línea*. Ejemplo (error OSAL, `0x438061c4`):

```
0x438061de  movs     r1, #0xd            ; nivel
0x438061e2  movs     r2, #1             ; flag
0x438061e6  add      r3, pc   -> 0x43caefe8 '[CAM_FUNC_MGR]: ERROR !!! osal_err:0x%04x %s : %d'
0x438061e8  movs     r0, #3             ; ID DE MÓDULO = 3
0x438061ea  add      r5, pc   -> 0x43caf167 'Function/LRBridge.cpp'
0x438061ec  movw     r6, #0x7de         ; línea 2014
0x438061f4  bl       #0x43805604        ; traza nueva
0x438061f8  ldr      r0, [pc, #0x7c]
0x43806200  add      r0, pc   -> 0x43ca3c34 'ERROR !!! osal_err:0x%04x %s : %d'  (genérica, compartida)
0x43806202  bl       #0x43902718        ; traza vieja
```

El `id de módulo = 3` y el `nivel = 13` son las constantes de la traza nueva (fijadas con
`movs r0,#3` / `movs r1,#0xd` justo antes de cada llamada; verificado byte a byte en los
7 wrappers y en los sitios de ejemplo; en `SyncProcMargin` —función invocada por puntero,
sin `bl` directo— los fija el llamante). Los 7 wrappers de traza son **uno por fichero
fuente**: `0x43787ac4`, `0x4380196c`, `0x43803d80`, `0x43805604`, `0x4380947c`,
`0x43809600`, `0x43809a64` (con 2/4/3/42/1/2/3 sitios respectivamente).

**(d) Los `type_id` del LRB y el despachador son los mismos en las tres fw**: la función
`0x43805ea8` (A6000) tiene su equivalente en la **A7S** en `0x437ac620` (que llama a la
traza antigua `0x438f7114`) y en el **A6300** en `0x437f6200` (traza antigua `0x43986518`),
con las mismas comparaciones de `type_id`; y el bloque de inicialización de la tabla de
funciones es estructuralmente idéntico (`0x437a43c4` en la A7S).

**(e) Tabla de funciones**: idéntica en A6000 y A7S (65 entradas, mismos nombres y ids);
**inexistente** en el A6300 fw2.01.

**Lectura del diferencial**: lo propio de la fw3.21 de la A6000 es (i) el **prefijo
`[CAM_FUNC_MGR]: `**, (ii) la **traza duplicada con id de módulo/nivel/fichero/línea**, y
(iii) la **cualificación con directorio `Function/`** de cuatro ficheros (y la aparición de
`Function/FunctionSetParam.cpp`, que no existe en la A7S ni en el A6300). **El código del
subsistema `Camera::Function` no cambia.**

---

## 7. Verificación y método

* **Regla de referencias**: estricta (canónica del repo,
  `analysis/s106_imaging_cap/scan_pic_refs_strict.py`). El escaneo local del hito
  (`analysis/s177_cam_func_mgr/verify_pic.py`, misma regla) coincide **exactamente** con el
  mapa global `analysis/s106_imaging_cap/pic_refs_strict_global.json`: **57 = 57 sitios**.
  (No se re-barrió la imagen.)
* **Verificación a mano de los pares PIC**: se desensamblaron los **57** pares
  (`verify_pic.py`, Capstone en modo Thumb con `detail=True` para detectar escrituras al
  registro), comprobando en cada uno: (a) el `ldr rX,[pc,#imm]` más cercano del mismo
  registro, (b) el literal del pool, (c) `destino = literal + (add + 4)`, y (d) que el
  registro **no** se reescribe entre el `ldr` y el `add`.
  **57/57 correctos, 0 reutilizaciones de registro.** Ejemplo (sitio `0x43805ed6`):
  `ldr r3,[pc,#0x28c]` @`0x43805ed4` → pool `0x43806164` = `0x4a933f`;
  `add r3,pc` @`0x43805ed6` → `0x4a933f + 0x43805eda = 0x43caf219` =
  `'[CAM_FUNC_MGR]: [LRB]REQ_APP_SND Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x'` ✓.
* **Tabla de funciones**: leída byte a byte del fichero (65 × 12 B) y el campo `origin`
  reconstruido **simulando la función de init `0x43787d88`** (`scan_cfm_functable.py`).
* **Scripts del hito** (`analysis/s177_cam_func_mgr/`): `scan_cfm_strings.py`,
  `scan_cfm_pic.py`, `verify_pic.py`, `scan_cfm_funcmap.py`, `scan_cfm_funcfiles.py`,
  `scan_cfm_markers.py`, `scan_cfm_diff.py`, `scan_cfm_prefijo.py`,
  `scan_cfm_tables.py`, `scan_cfm_functable.py`, `scan_cfm_dual.py`,
  `scan_cfm_negativo.py`, `build_cam_func_mgr.py`, `dasm.py`, `dump_strings.py`,
  `dump_strings_fw.py`, `dump_ptrtable.py`, `dump_nametable.py`, `find_ptrs.py`,
  `find_ptr_range.py`, `find_pic_targets.py`, `find_calls.py`, `near_file.py`.
* **Tests**: `tests/test_s177_cam_func_mgr.py` (comprueban bytes reales: si cambia una
  dirección, el test falla).

---

## 8. Interés para la línea del obturador

**Negativo acotado: el módulo `[CAM_FUNC_MGR]` NO habla de obturación, de obturador
electrónico, de lectura del sensor de imagen ni de tiempos de exposición.**

Comprobación literal sobre las 43 trazas (`analysis/s177_cam_func_mgr/scan_cfm_negativo.py`):

| término | coincidencias en las 43 trazas | nota |
|---|---|---|
| `shutter` | **0** | |
| `silent` | **0** | |
| `curtain` | **0** | |
| `electro` | **0** | |
| `mech` | **0** | |
| `expos` | **0** | (las apariciones de `exp` son `ExpFocusTransition` / `SleepTransition`) |
| `iso` | **0** | |
| `apert` | **0** | |
| `sensor` | **0** | |
| `shut` / `svd` / `shd` / `spl` | **0** | (los parámetros del imager de S124/S134 **no** aparecen aquí) |
| `frame` | **0** | |
| `imager` | 1 | `unknown message in Imager Sleep Process: %x` (`0x43cb0150`) — **proceso de sleep del imager**, no lectura de sensor |
| `scan` | 1 | `IsNeedScanAf (%d)` (`0x43cb02ad`) — **AF de barrido**, no barrido de sensor |
| `af ` | 2 | `IsNeedScanAf`, `Pseudo AF Stop %d` |
| `ae ` | 1 | `IsNeedAe     (%d)` (`0x43cb02cf`) — **disparo de AE**, no obturación |

Matices que **sí** conviene registrar:

* La tabla de funciones (§5) **sí** gestiona peticiones de captura y de obturación
  lógica: `REQ_CAPTURE_START` (`0x101`), `REQ_CAPTURE_END` (`0x102`),
  `REQ_AF_START/STOP`, `REQ_AE_START/STOP`, `REQ_AF_CHANGE`, `REQ_EXP_FOCUSED_ON/OFF`,
  `REQ_PREVIEW_MODE`, `REQ_MOVIE`, `REQ_STILL_EE`, `REQ_TOUCH_SCAN`, `REQ_GOLF_EE`,
  `REQ_BB_OUT`, `RAW_CONT_CAP_CANCEL`, `REQ_FELOCK_ON/OFF`. Son **órdenes de alto nivel**
  (disparar una captura, arrancar/parar AF o AE), **no** parámetros del mecanismo de
  obturación.
* `REQ_CAPTURE_START`/`REQ_CAPTURE_END` son **instrucciones de "dispara el obturador"**
  en el sentido abstracto del gestor; **el módulo no baja al nivel del obturador**: no
  menciona `shutter`, `silent`, `curtain`, `shut/svd/shd/spl`, ni ningún registro de
  sensor. Es un **gestor de funciones**, no un controlador de mecanismo.
* El término `unretract` (`#### Execute unretract command!!`, `0x43cb027c`) es del
  **obturador mecánico** (retracción del espejo/obturador) según el contexto de `CamMain`;
  **no** implica obturador electrónico.

⇒ **Para la línea del obturador: S51 A=NO / B=NO / C=NO se mantiene**; este módulo no
aporta ninguna ruta electrónica al obturador. Es un gestor de *órdenes* de cámara de alto
nivel, y su valor para la línea está en que **centraliza** `REQ_CAPTURE_START/END`
(quien los emite es `Camera::Function::Release`, `FUNC <= REL`).

---

## 9. NO VERIFICADO / abierto

1. **Significado de las siglas**: `CAM_FUNC_MGR` y `MGR` **no se expanden** en ninguna
   cadena; `LRB`/`LRBridge` tampoco (el nombre de la clase es `LRBridge` y el del fichero
   `LRBridge.cpp`, pero no hay cadena que lo desarrolle). NO VERIFICADO. La lectura
   «gestor de funciones de cámara / puente de peticiones entre LSIs» es **INFERENCIA**
   sostenida por el comportamiento medido (tabla de peticiones/respuestas, despacho por
   id, puente `Snd`/`Rsv` con `from_lsi`).
2. **Significado de `Capcon`**: `Capcon` aparece 11 veces en cada fw (ficheros
   `capcon_api_cam.cpp`, `capcon_api_businessif.cpp`, `tsk_capcon_sequence.cpp`, clase
   `CapconEventQueue`, método `CapconExec`), pero **no se expande** en ninguna cadena. NO
   VERIFICADO.
3. **Qué significa exactamente `LRB`, `APP`, `V2ND`, `FSPSUM`, `VSYNC_CUST`** y sus
   sufijos `_SND` / `_CMP` / `REQ_`: los **12 `type_id` están decodificados** (§2.3) pero
   la semántica de cada tipo (qué transporte, qué LSI, qué temporización) NO VERIFICADA.
   `from_lsi` es el byte del campo emisor, pero **no se ha identificado la lista de LSIs**
   ni sus ids.
4. **Relación entre el `id` de la tabla de funciones (§5) y los tipos de bus
   `0x3000`–`0x3030` del despachador (§2.4)**: son **dos espacios de ids distintos** y su
   correspondencia NO está establecida (p. ej. `REPLY_MOVIE` tiene id `0x301` en la tabla
   pero el bus maneja `0x3001`–`0x3030`).
5. **Atribución de fichero de dos funciones**: `0x43803e2c` y `0x43803fb8` se atribuyen a
   `Function/FunctionSetParam.cpp` por proximidad (wrapper `0x43803d80` + única referencia
   PIC a ese nombre en `0x4380462c`); no hay referencia directa dentro de sus propios
   cuerpos. NO VERIFICADO al 100 %.
6. **Significado de `CapMode`** (byte validado contra una máscara de 32 bits, valores
   `3`, `0x17`, `0x1c`, máximo `0x1d`): **NO VERIFICADO**; no se ha enlazado con los
   modos de captura de S66/S123.
7. **Identificador de cola OSAL propio del módulo**: no se ha localizado una cola
   exclusiva de `Camera::Function` (el subsistema usa `osal_try_valloc_msg` `0x435612d0`,
   `osal_snd_msg` `0x4356120c`/`0x43561228` y `osal_free_msg` `0x435612ec` sobre colas
   genéricas). NO VERIFICADO.
8. **Qué es `LSI_NUM_TYPE`** (error `0x43caf17d`) y `EID` (`UNKNOWN EID`, `0x43caf1b3`):
   siglas sin desarrollar. NO VERIFICADO.
9. **`CapMode`/`Receive`/`Comp`**: la semántica exacta de `comp` (completion) y de la
   cola donde se guarda la petición pendiente (`[r4+0..8]` de un global en `0x43edf674`)
   NO VERIFICADA en detalle.
10. **`Pseudo AF Stop %d`**: la cadena está **muerta** en la A6000 y en la A7S, y **no
    existe** en el A6300. No se ha determinado qué código la usaba en versiones
    anteriores (si alguna). NO VERIFICADO.

---

## 10. Revisión del agente principal

*(vacía — pendiente de revisión)*

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (31 tests / 1024 subtests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 43 cadenas `[CAM_FUNC_MGR]` en la A6000 fw3.21 entre `0x43ca12af` y
   `0x43cb02f1`; **0** en la A7S fw3.20 y el A6300 fw2.01 → comprobado con `bytes.count()`.
   **57 sitios** (regla estricta, que coincide 57=57 con el mapa global) en **25 funciones**, con
   los **57/57 pares PIC verificados a mano** (pool, `destino = literal + (add+4)`, sin reuso de
   registro). **1 cadena muerta**: `Pseudo AF Stop %d` `0x43cb02f1` (0 referencias PIC y 0
   punteros absolutos).
2. **Hallazgo estructural muy fuerte (verificado a mano)**: las **43/43** cadenas tienen **gemelo
   exacto en `vaddr+16`** — el prefijo `"[CAM_FUNC_MGR]: "` ocupa exactamente **16 B** y se
   inserta **delante** del literal original, que **sigue intacto**. Es la firma mecánica del
   rewrite de *logging* de la fw3.21: **no se reescribe la cadena, se antepone una copia**.
   Verificado con `bytes` en las 43.
3. **Base textual sin inventar**: `Camera::Function` (namespace C++ RTTI `N6Camera8Function…`),
   **18 clases idénticas en las tres fw**; el puente `LRBridge` (`Function/LRBridge.cpp`) y 18
   ficheros fuente (`Function/`, `wrapper/`, `tsk/`, `api/`).
4. **Tabla de 65 funciones** en `0x43ff17b8` (paso 12 B): `{const char *origin; const char *name; u32 id;}`.
   Comprobación directa: entradas `[0] name="UNKNOWN" id=0`, `[1] "REQ_MOVIE" id=1`, `[2]
   "REQ_MOVIE_REC" id=2`, `[3] "REQ_STILL_EE" id=3`, `[4] "REQ_PB" id=4`; el campo `origin` vale 0
   en el fichero (se inicializa en runtime, `0x43787d88`).
5. **Los 12 `type_id` del puente `LRBridge`**: `0x43805ea8` (Snd) y `0x438066d4` (Rsv), con las
   comparaciones en `0x43805ec0`…`0x43806126` → `REQ_APP_SND`, `APP`, `APP_CMP`,
   `REQ_V2ND_SND`, `V2ND`, `V2ND_CMP`, `REQ_VSYNC_CUST_SND`, `VSYNC_CUST`, `VSYNC_CUST_CMP`,
   `REQ_FSPSUM_SND`, `FSPSUM`, `FSPSUM_CMP`. Cada rama se habilita con un bit de máscara en
   `[obj+0x41]`; los campos impresos son `type_id` (`[msg+0]`), `from_lsi` (`[msg+1]`) y
   `req_seq_id` (u16 en `[msg+2]`).
6. **Despachador `0x43805930`**: tipo de mensaje u16 en `[msg+2]`, `sub.w r2,r3,#0x3000`
   (`0x4380599a`), `cmp r2,#0x30` (`0x4380599e`) y **`tbb` de 49 entradas** (`0x438059a2`) →
   **tipos de bus `0x3000`–`0x3030`**.
7. **Es cambio de *logging*, no de código (diferencial verificado)**: los **textos interiores**
   están presentes **43/43** en la A7S y **42/43** en el A6300 (la A7S solo tiene la traza
   *vieja* en `0x437ac63e` → `bl 0x438f7114`; el A6300 en `0x437f621e` → `bl 0x43986518`), y la
   **tabla de 65 funciones no existe en el A6300** (`REPLY_` **0**, `MSG_NONE` **0**, `FUNC <= ` **0**;
   en la A6000: 27 / 1 / 4).
8. **Negativo acotado**: 0 de `shutter`/`silent`/`curtain`/`electro`/`mech`/`expos`/`iso`/`apert`/
   `sensor`/`shut`/`svd`/`frame` en las 43 trazas. Gestiona órdenes de alto nivel
   (`REQ_CAPTURE_START/END`, `REQ_AF_START/STOP`, `REQ_AE_START/STOP`…) pero **no baja al nivel
   del obturador**; el `unretract` `0x43cb027c` es del obturador **mecánico** → **sin efecto en
   S51** (A/B/C = NO).
