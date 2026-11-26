# Touch AF en orb-server (A6000 fw 3.21) — API remota de punto de enfoque por toque

Análisis **estático** (cero escrituras en cámara/firmware). Convención de cada afirmación:
**VERIFICADO** (código/bytes citados), **INFERENCIA** (deducción con evidencia parcial),
**NO_VERIFICADO** (no demostrado; se indica qué haría falta).

## 0. Objetos analizados

| Objeto | Ruta (recortada) | sha256 | Tamaño |
|---|---|---|---|
| orb-server A6000 fw3.21 | `firmware/extracted/fw321/.../nflasha15_unpacked_unpacked/bin/orb-server` | `2ef500ba5871b8017b94ef2af4788eb8c27e1614e6510db8f8b1839ab70ad4c6` | 3 680 104 B |
| orb-server A7S fw3.20 | `firmware/extracted/a7s-fw320/payload/.../bin/orb-server` | **idéntico** `2ef500ba…70ad4c6` | 3 680 104 B |
| orb-server A6300 fw2.01 | `firmware/extracted/a6300-fw201/payload/.../bin/orb-server` | `9c41b66e4f20b196280f3d79ea4ff386d66895c3592681f896986f21032be28a` | 5 494 000 B |
| libInfraWebApi.so A6000 (lado cámara) | `firmware/extracted/fw321/.../lib/libInfraWebApi.so` | — | 177 164 B |
| libInfraRemoteControlNet.so A6000 | `firmware/extracted/fw321/.../lib/libInfraRemoteControlNet.so` | — | 106 040 B |

ELF32 ARM EABI5, `EXEC`, “stripped” **pero con `.dynsym` completo** (nombres C++ visibles):
todo el análisis se apoya en símbolos + desensamblado Capstone (Thumb-2) y pseudocódigo REA/Ghidra.
Herramientas propias: `analysis/eyeaf/tools/{armdis,xrefs,xref_movt,vtable,sweep}.py`.

## 1. Respuesta corta

- **Firma**: `setTouchAFPosition` recibe **un array posicional de 2 doubles**: `params: [x, y]`.
  `parameterTypes()` construye `["double","double"]`; **no hay nombres de campo** en este build
  (no se acepta `{"x":…,"y":…}` en la capa libj: `call()` exige `JsArray` de longitud exactamente 2). **VERIFICADO**
- **Coordenadas**: dobles en **porcentaje del encuadre, `0.0 … 100.0`** (no 0..1, no −1..1, no píxeles).
  Fuera de rango ⇒ `parameter err` y no se envía nada. **VERIFICADO**
- **Tercer valor de la traza**: `val=%x` **no es parámetro del cliente**: es un empaquetado interno
  16:16 de las coordenadas ya escaladas, `val = (u16)(x*100) << 16 | (u16)(y*100)`. **VERIFICADO**
- **¿Dispara AF?** No en orb-server: orb solo reenvía la posición al proceso de cámara y devuelve
  `[int 0, {"AFResult":bool,"AFType":"Touch"}]`. El `AFResult` lo produce la cámara. **VERIFICADO (reenvío
  y estructura)**; si la cámara hace AF puntual, continuo o solo reposiciona el marco: **NO_VERIFICADO** (§4).
- **Disponibilidad**: orb-server **no filtra** por modo/objetivo/área; el único gate local es el rango 0..100.
  El método aparece en `getAvailableApiList` **si y solo si la cámara reporta el id `0x2d` (45)**, que orb
  traduce a nombre con una tabla estática. **VERIFICADO (mecanismo)**; condiciones de la cámara: **NO_VERIFICADO** (§5).

## 2. Tabla de funciones (A6000 fw3.21, direcciones de `.text`)

| Dirección | Tamaño | Símbolo | Qué hace / evidencia |
|---|---|---|---|
| `0x21574c` | 524 | `Remote::v1_0::SetTouchAFPosition::call(shared_ptr<JsArray>)` | Exige `args->length()==2` (`[vtable+0x44]`), `args->get(0)`→`valueToDouble`→**x**, `args->get(1)`→**y**, llama `invoke(x,y)` (`[vtable+0x68]`). Si no: `sendStatus(client,3,"illegal argument")` (str `0x2ea140`). **VERIFICADO** |
| `0x214ec8` | 1724 | `SetTouchAFPosition::invoke(double,double)` | Valida `0 ≤ x ≤ 100` y `0 ≤ y ≤ 100` (constante `100.0` en `0x215308`), empaqueta `val`, `setEvtParamId(msg,0x192,0x8d)`, `AddToPool`, `sendMsgToServer`. **VERIFICADO** |
| `0x215958` | 416 | `SetTouchAFPosition::parameterTypes()` | `TypedJsArray<String>` con 2 entradas `"double"` (str `0x2e63e8`). **VERIFICADO** |
| `0x215af8` | 416 | `SetTouchAFPosition::resultTypes()` | 2 entradas: `"int"` (str `0x2e5c30`) y `"{\"AFResult\":\"bool\", \"AFType\":\"string\"}"` (str `0x327d9c`, ref. `0x215c1c`). **VERIFICADO** |
| `0x2156b0` | 32 | `SetTouchAFPosition::name()` | devuelve `"setTouchAFPosition"` (str `0x2e62b8`). **VERIFICADO** |
| `0x1a7820` | 2008 | `Remote::v1_0::SetTouchAFPosition_invoke_cmd(shared_ptr<Client>,WebApiIntMsg*)` | Maneja la respuesta de Infra: `msg+0x10`=response, `msg+0x0c`=relay, `msg+0x14`=**AFResult**; `setBoolean(…,"AFResult")`, `setString(…,"AFType","Touch")` (constante, str `0x2fb4a4`); responde `[0, {AFResult,AFType}]`; ACK `sendMsgToServerCmp(msg,0x194,0x8f,relay)`. **VERIFICADO** |
| `0x2175f4` | 292 | `GetTouchAFPosition::call(shared_ptr<JsArray>)` | Exige `args->length()==0` (compara con 0) y llama `invoke()`. **VERIFICADO** |
| `0x216ddc` | 1528 | `GetTouchAFPosition::invoke()` | `setEvtParamId(msg,0x198,0x93)` + `sendMsgToServer`. **VERIFICADO** |
| `0x1b756c` | 1960 | `GetTouchAFPosition_invoke_cmd` | `msg+0x14`→`"set"`; `setDoubleArray("touchCoordinates", arr)` con **array creado vacío** (`TypedJsArray<double>::create` en `0x1b776e`, sin ningún `push`). ACK `0x19a,0x95`. **VERIFICADO** |
| `0x217798` | 300 | `GetTouchAFPosition::resultTypes()` | 1 entrada: `"{\"set\":\"bool\", \"touchCoordinates\":\"double*\"}"` (str `0x329b28`, ref. `0x217842`). **VERIFICADO** |
| `0x217718` | 128 | `GetTouchAFPosition::parameterTypes()` | lista vacía (sin `String::create`). **VERIFICADO** |
| `0x216864` | 292 | `CancelTouchAFPosition::call()` | igual patrón, `length()==0`. **VERIFICADO** |
| `0x215fec` | 1528 | `CancelTouchAFPosition::invoke()` | `setEvtParamId(msg,0x195,0x90)` + `sendMsgToServer`. **VERIFICADO** |
| `0x1a75dc` | 580 | `CancelTouchAFPosition_invoke_cmd` | solo estado; ACK `0x197,0x92`; sin objeto JSON. **VERIFICADO** |
| `0x216a08`/`0x216989` | 128 | `CancelTouchAFPosition::{result,parameter}Types()` | listas vacías. **VERIFICADO** |
| `0x18773c` | 94 | `WebApiAddonUipc::setEvtParamId(msg,msgid,paramid)` | `memset(msg,0,0x620)`, `msg+0x00=msgid`, `msg+0x08=paramid`; traza `…msgid=0x%x, paramid=0x%x, relay=0x%x` (str `0x2e40d0`). **VERIFICADO** |
| `0x18767c` | 188 | `WebApiAddonUipc::sendMsgToServer(msg,&ret)` | `OrbSocket::SocketClient::Write(msg,0x620)`; error `size mismatch!! ret<=%d, sizeof(WebApiIntMsg)<=%d` (str `0x2e4070`). **VERIFICADO** |
| `0x1879dc` | — | `WebApiAddonUtils::convStringToId(paramName,std::string,int*)` | búsqueda lineal en tablas `{u32 id; const char* name}`. **VERIFICADO** |
| `0x187a54` | — | `WebApiAddonUtils::convIdToString(paramName,id,buf)` | inversa; usada para traducir ids de `getAvailableApiList` (paramName `0`). **VERIFICADO** |
| `0x1b52b0` | 2100 | `GetAvailableApiList_invoke_cmd` | recorre los ids devueltos por la cámara, `convIdToString(0,id,…)`, descarta los no mapeados (traza `[getAvailableApiList cmd] methodName_wk`); ACK `0x114,0x11`. **VERIFICADO** |

## 3. Q1 — Firma exacta y espacio de coordenadas

**VERIFICADO** — `SetTouchAFPosition::call` (pseudocódigo REA, `0x21574c`):

```c
iVar3 = (**(code **)(*(int *)*param_2 + 0x44))();      // args->length()
if (iVar3 == 2) {
    (**(code **)(*piVar5 + 0x4c))(local_1c, piVar5, 0);        // args->get(0)
    ok1 = MethodBase::valueToDouble(this, local_1c, &x);       // 0x24bba8
    if (ok1) { (…)(&local_20, param_2, 1);                     // args->get(1)
               ok2 = !MethodBase::valueToDouble(this, &local_20, &y); }
    if (!ok2) (**(code **)(*(int *)this + 0x68))(this, …, x, y);   // invoke(x,y)
} else sendStatus(client, 3, "illegal argument");           // 0x2ea140
```

- Tipos: `parameterTypes() = ["double","double"]`; `resultTypes() = ["int", '{"AFResult":"bool","AFType":"string"}']`.
- Nombres de campo: **no existen**; el método es posicional (`JsArray` de 2). Quien llame por HTTP/JSON-RPC
  debe enviar `"params": [x, y]`.
- Rango: **VERIFICADO** en `invoke` (`0x214ec8`), pseudocódigo:
  `if (x < 0.0 || 100.0 < x || y < 0.0 || 100.0 < y) → "parameter err"`. Constante `100.0` = literal
  `0x215308` (`00 00 00 00 00 00 59 40`).
- Unidades: **porcentaje del encuadre** (0 = borde izquierdo/superior, 100 = borde derecho/inferior).
  Es la única escala compatible con el escalado `*100` y el empaquetado de 16 bits (`0..10000`). **INFERENCIA fuerte**
  (el binario no documenta la semántica; no hay ninguna otra constante de escala en la función).

**Tercer valor `val=%x`** — **VERIFICADO**, pseudocódigo de `invoke` y asm `0x2150dc..0x215124`:

```c
local_6c0 = (uint)(long long)(y * 100.0) | ((int)(long long)(x * 100.0) << 0x10);  // 16:16
fprintf(stderr, "(%04d)[INF:setTouchAFPosition: %04d]touch AF position x=%f y=%f val=%x\n", …);
```

- **No es parámetro del cliente**: se calcula aquí, después de validar. `%x` = `val` en hexadecimal.
- Bits: **`[31:16]` = `x*100`** (0..10000), **`[15:0]` = `y*100`** (0..10000). Truncamiento hacia cero.
- Ejemplo: `x=50, y=50` ⇒ `val=0x13881388`; `x=100, y=0` ⇒ `0x27100000`.
- La traza sólo se emite con `WebApiAddonDbgMon::debug_level > 1`; el mensaje `parameter err`
  se emite con `debug_level >= 0`.

Cadenas exactas:
- `0x327c70` `(%04d)[PRN:setTouchAFPosition: %04d]---> IN  %s\n`
- `0x327ca4` `(%04d)[\x1b[41mERR\x1b[49m:setTouchAFPosition: %04d][setTouchAFPosition] parameter err \n`
- `0x327cf8` `(%04d)[INF:setTouchAFPosition: %04d]touch AF position x=%f y=%f val=%x\n`
- `0x327d40` `(%04d)[\x1b[41mERR\x1b[49m:setTouchAFPosition: %04d][setTouchAFPosition] sendMsgToServer err \n`

## 4. Q2 — Qué hace al aplicarse y qué mensaje viaja a la cámara

**Cadena verificada**:

1. `invoke(x,y)` valida rango, calcula `val`, `WebApiAddonUipc::setEvtParamId(msg, 0x192, 0x8d)`
   (`0x214fxx`, call site en `0x2150d8`). **VERIFICADO**
2. Escribe el payload en `msg+0x10` (`str r2,[sp,#0x28]` con `msg` en `sp+0x18`, `0x2150fc`). **VERIFICADO**
3. `relay = LibOrbRelayPool::AddToPool(client)` (`0x1859bc`); `sendMsgToServer(msg,&ret)` escribe
   **1568 B (`0x620`)** por `OrbSocket::SocketClient` (socket Unix al proceso de cámara). **VERIFICADO**
4. La cámara responde y orb ejecuta `SetTouchAFPosition_invoke_cmd` (`0x1a7820`), que lee
   `msg+0x10` (código de respuesta) y `msg+0x14` (bool **AFResult**), responde al cliente y cierra con
   `sendMsgToServerCmp(msg, 0x194, 0x8f, relay)`. **VERIFICADO**
5. Lado cámara: `libInfraWebApi.so` registra `WebApiUser::WebApi2::wa_job_setTouchAFPosition_cmd`
   (`0x11e50`) + `_evt`/`_cmp`; la lógica de estado está en `libInfraRemoteControlNet.so`
   (`PsmRcWebAPIGetTouchAFPosition`). **VERIFICADO (existencia de símbolos)**

**Layout de `WebApiIntMsg`** (deducido de `setEvtParamId` y de los lectores; **VERIFICADO** para los
offsets usados, tamaño `0x620`):

| Offset | Campo | Evidencia |
|---|---|---|
| `+0x00` | `msgid` | `setEvtParamId` (`str r6,[r4]` con `r6=0x192`) |
| `+0x08` | `paramid` | `str r5,[r4,#8]` con `r5=0x8d` |
| `+0x0c` | `relay` | traza `relay=0x%x`; `ldr …[param_2,#0xc]` |
| `+0x10` | payload/`response` | escritura de `val`; lectura como código de respuesta |
| `+0x14` | `bool` (AFResult / currentSet) | `ldrb r2,[r6,#0x14]` |

**Identificadores numéricos del protocolo interno** (uipc orb↔cámara) — **VERIFICADO** por los
`setEvtParamId`/`sendMsgToServerCmp` de cada método y por la tabla `liborbEvtCmdTbl`
(`libInfraWebApi.so` @ `0x2d5d4`, cuádruplas `{cmd, evt, cmp, param}`):

| Método JSON | petición (msgid/paramid) | evento | ACK (`sendMsgToServerCmp`) |
|---|---|---|---|
| `setTouchAFPosition` | `0x192 / 0x8d` | `0x193 / 0x8e` | `0x194 / 0x8f` |
| `cancelTouchAFPosition` | `0x195 / 0x90` | `0x196 / 0x91` | `0x197 / 0x92` |
| `getTouchAFPosition` | `0x198 / 0x93` | `0x199 / 0x94` | `0x19a / 0x95` |
| `setFocusMode` | `0x186 / 0x81` | — | `0x188 / 0x83` |

Fila `0x192` en `liborbEvtCmdTbl`: `0x2d8a4` = `{0x192,0x193,0x194,0x8e}`. **VERIFICADO**

**Resultado devuelto al cliente** (`SetTouchAFPosition_invoke_cmd`, `0x1a7820`):

```c
if (response == 0) {
    AFResult = *(bool*)(msg + 0x14);
    StructureBase::setBoolean(obj, "AFResult", AFResult);
    StructureBase::setString (obj, "AFType", "Touch");      // constante 0x2fb4a4
    results = JsArray[ 0 /*int*/, obj ];                    // [0, {AFResult,AFType}]
} else MethodBase::sendStatus(client, response, "");
```

**¿Mueve el marco, dispara AF, o ambas?**
- `setTouchAFPosition` **no** contiene ningún indicador de “disparar AF”: no envía `actHalfPressShutter`
  (ese método no existe en este binario, §8) ni pone bits de AF en el mensaje; sólo viaja la posición. **VERIFICADO**
- Devuelve `AFResult` ⇒ la cámara **sí evalúa un AF** y reporta éxito/fracaso para el punto. **INFERENCIA**
  (el bool se lee tal cual del mensaje de la cámara; su semántica exacta no está en orb-server).
- AF puntual vs continuo: **NO_VERIFICADO**. Requiere (a) desensamblar
  `libInfraRemoteControlNet.so` (`PsmRcWebAPIGetTouchAFPosition` y la máquina `RcCameraStateSetParameter`
  @`0x8ed9`, 9688 B) o (b) prueba en cámara observando si el punto queda fijado, si reenfoca al mover el
  encuadre y si `AFResult` cambia.
- Efecto lateral útil (**INFERENCIA**): al ser un simple reenvío de coordenadas, llamadas repetidas a
  ~10 Hz deberían bastar para “arrastrar” el punto desde un PC; el coste es un round-trip uipc por llamada.

## 5. Q3 — Disponibilidad

**Capa orb (VERIFICADO)**:
- No hay ninguna comprobación de modo de disparo, área de AF, objetivo montado ni modo de película antes de
  `sendMsgToServer`. Lo único que puede impedir el envío es el rango de coordenadas (`parameter err`) o el
  fallo de escritura en el socket (`sendMsgToServer err`).
- `getAvailableApiList` **no se construye en orb**: orb recibe de la cámara una lista de **ids numéricos** y
  traduce cada uno con `WebApiAddonUtils::convIdToString(0, id, buf)`; los ids sin entrada se descartan
  (traza `[getAvailableApiList cmd] methodName_wk`). Además, `response!=0` ⇒
  `response form Infra is not success`.
- Tabla ids↔nombres en orb-server, `.rodata` @ **`0x2e4514`**, formato `{u32 id; const char* name}`,
  84 entradas + terminador `-1` (dump completo en `analysis/eyeaf/data/api_id_table_a6000.json`):

| id | nombre |
|---|---|
| `0x29` (41) | `setFocusMode` |
| `0x2a` (42) | `getFocusMode` |
| `0x2b` (43) | `getSupportedFocusMode` |
| `0x2c` (44) | `getAvailableFocusMode` |
| **`0x2d` (45)** | **`setTouchAFPosition`** (entrada `0x2e479c`, nombre en `0x2e47a0`, cadena `0x2e62b8`) |
| **`0x2e` (46)** | **`cancelTouchAFPosition`** (entrada `0x2e47a4`) |
| **`0x2f` (47)** | **`getTouchAFPosition`** (entrada `0x2e47ac`) |
| `0x53` (83) / `0x52` (82) | `getEvent` / `receiveEvent` |

⇒ **`setTouchAFPosition` figura en `getAvailableApiList` si y sólo si la cámara incluye el id 45.** Es una
condición de la cámara, no de orb.

**Capa cámara (parcial)**:
- **VERIFICADO** que la lista se genera ahí: `libInfraWebApi.so` `wa_job_getAvailableApiList_cmd`
  (`0xf55c`, trunca a `0x40` entradas y añade las de `wa_getAvailableApiListAddTbl` = `{0,1,0x53}` en
  `0x2df64`), y `libInfraRemoteControlNet.so` contiene
  `PsmRcCameraStateChangeAvailableApiList`, `PsmRcWebAPIEditAvailableApiList`,
  `PsmRcWebAPICopyAvailableApiList`, `RcCameraState_update_AvailableApiList_nr`.
- **NO_VERIFICADO**: qué estados concretos habilitan el id 45 (modo disparo, `AF area`, objetivo, ajuste
  "Touch AF" del menú). Ruta para cerrarlo: desensamblar `PsmRcWebAPIEditAvailableApiList` /
  `RcCameraStateSetParameter` en `libInfraRemoteControlNet.so` y localizar la condición que escribe el
  id `0x2d`; o probar en cámara con/sin objetivo y con/sin "Touch AF" activado.
- Dato de apoyo: el A6300 **sí** tiene cachés explícitas `setTouchAFSupportCache`,
  `setTouchAFStatusSettingCache`, `setTouchAFSettingAppID` (en su `libInfraRemoteControlNet.so`); el A6000
  **no** las tiene ⇒ **INFERENCIA**: en el A6000 el estado de touch AF se evalúa sin caché, por estado de cámara.

## 6. Q4 — `getTouchAFPosition`, `cancelTouchAFPosition` y eventos

| Método | params | resultado JSON | Evidencia |
|---|---|---|---|
| `getTouchAFPosition` | `[]` | `{"set": bool, "touchCoordinates": double[]}` | `resultTypes` `0x217798` (schema `0x329b28`), `TouchAFCurrentPositionParams::isValid` `0x1cbe1c` |
| `cancelTouchAFPosition` | `[]` | `[]` (sin resultado) | `resultTypes` `0x216a08` vacío, `_invoke_cmd` `0x1a75dc` sólo `sendStatus` |
| `setTouchAFPosition` | `[double,double]` | `[int, {"AFResult":bool,"AFType":string}]` | `0x215af8`, `0x1a7820` |

- **`touchCoordinates` sale siempre vacío en este firmware** (**VERIFICADO** en `GetTouchAFPosition_invoke_cmd`
  `0x1b756c`): se crea `TypedJsArray<double>` vacío en `0x1b776e` y se adjunta tal cual con
  `setDoubleArray("touchCoordinates", …)` en `0x1b78ee`; la función **no contiene ni una sola instrucción
  de coma flotante** (`vldr/vcvt/vmul/vdiv` ausentes en `0x1b756c..0x1b7d14`) ni llamadas de inserción.
  ⇒ no sirve para *leer* la posición actual del punto en fw3.21.
- `"set"` = `*(bool*)(msg+0x14)`: indica si el punto está fijado. **VERIFICADO (offset)**;
  semántica exacta del valor de la cámara: **INFERENCIA**.
- Evento `touchAFPosition` (**VERIFICADO**, `GetEvent_invoke_cmd` @ `0x1c49c0..0x1c4b0c`):
  ```c
  TypedJsArray<double>::create();
  StructureBase::setString (e, "type", "touchAFPosition");          // str 0x2fe634
  StructureBase::setBoolean(e, "currentSet", <bool>);
  StructureBase::setDoubleArray(e, "currentTouchCoordinates", arr);
  ```
  Esquema declarado: `0x33d86c` `{"type":"string", "currentSet":"bool", "currentTouchCoordinates":"double*"}`
  (usado por `GetEvent::resultTypes` @ `0x22a36c`).
- `TouchAFPositionParams` (`isValid` `0x1cbb2c`) usa `"AFResult"`/`"AFType"` — es la estructura del
  resultado de `setTouchAFPosition`, no del evento.
- **Cuándo/frecuencia**: el cliente descubre el evento llamando a `getEvent`; orb devuelve la lista de
  eventos que la cámara entrega en cada petición (no hay push al cliente; existe un método interno
  `receiveEvent`, id `0x52`). El evento se construye en la misma pasada de `GetEvent_invoke_cmd`, con una
  rama según un byte de estado (`ldrb …[fp,#0xb]`, `cmp #8` @ `0x1c4a90`) que puede omitir campos.
  **INFERENCIA** en cuanto a cadencia (depende del bucle `getEvent` del cliente); **NO_VERIFICADO** si el
  A6000 emite este evento en todos los modos.

## 7. Q5 — Comparación A6300 / A7S

- **A7S fw3.20**: el `orb-server` es **byte a byte idéntico** al de la A6000 (mismo `sha256`), por tanto la
  superficie JSON de touch AF es **idéntica** (mismos 3 métodos, misma firma, mismos ids). **VERIFICADO**
  Matiz: su `libInfraRemoteControlNet.so` (59 964 B) **no contiene ninguna cadena `touchaf`** y su
  `libInfraWebApi.so` sí tiene el job ⇒ **INFERENCIA**: la API existe en orb pero el soporte real en la
  cámara podría ser parcial; **NO_VERIFICADO** sin probar en un A7S.
- **A6300 fw2.01** (`orb-server` 5 494 000 B, sin `.dynsym`, con tabla de rutas literal):
  - **Posee los 3 métodos de touch AF** con la **misma firma**, confirmada por su tabla `getMethodTypes`
    (cadena literal en el binario):
    `["setTouchAFPosition",["double","double"],["int","{\"AFResult\":\"bool\", \"AFType\":\"string\"}"],"1.0"]`,
    `["getTouchAFPosition",[],["{\"set\":\"bool\", \"touchCoordinates\":\"double*\"}"],"1.0"]`,
    `["cancelTouchAFPosition",[],[],"1.0"]`. **VERIFICADO**
  - **Añade** (no presente en A6000): `actTrackingFocus`, `cancelTrackingFocus`, `setTrackingFocus`,
    `getTrackingFocus`, `getSupportedTrackingFocus`, `getAvailableTrackingFocus`, `setHighlightSceneFaceSetting`
    (+ supported/available/get), `getTemporarilyUnavailableApiList`, `actHalfPressShutter`,
    `cancelHalfPressShutter`, `startContShooting`, `setContShooting*`, `actWhiteBalanceOnePushCustom`, etc.
    243 métodos únicos frente a 86 del A6000. **VERIFICADO** (tabla de rutas del A6300 vs inventario de
    `name()` del A6000, §8).
  - **No hay ningún método ni campo de ojos**: ni `EyeAF`, ni `pupil`, ni `eye`, ni `faceDetection`.
    Lo único con “face” es `*HighlightSceneFaceSetting*` (escena *Highlight*) y los flashes `*RedEye*`.
    **VERIFICADO** por barrido de cadenas de ambos binarios.
- **Conclusión para Eye AF**: la API remota no expone Eye AF en **ninguna** de las tres cámaras; el A6000
  **no puede heredar** un Eye AF nativo por esta vía desde el A6300, porque el A6300 no lo publica.
  Lo que sí podría heredarse conceptualmente es la familia *tracking focus* (seguimiento por objeto),
  ausente en el A6000 y traducida a mensajes uipc propios. **VERIFICADO (ausencia de API)** /
  **NO_VERIFICADO** que el hardware del A6000 pudiera ejecutarla aunque no la exponga.

## 8. Q6 — `getFocusMode` / `setFocusMode` (y ausencia de `ChangeAF`/`changeAFArea`)

**Inventario completo del API del A6000** (86 nombres, extraídos de las 87 funciones `name()` del
`Remote::v1_0`; lista en `analysis/eyeaf/data/remote_methods_a6000.json`). Los únicos métodos relacionados
con enfoque son:

`setFocusMode`, `getFocusMode`, `getSupportedFocusMode`, `getAvailableFocusMode`,
`setTouchAFPosition`, `getTouchAFPosition`, `cancelTouchAFPosition`.

⇒ **`ChangeAF`, `changeAFArea`, `setAFArea`, `actHalfPressShutter`, `actTrackingFocus` NO existen** en
este build. **VERIFICADO** (no hay símbolo, ni nombre en el inventario, ni cadena).

**`setFocusMode`** (`0x2112ec`, 2036 B) — **VERIFICADO**:
- Parámetro: **una cadena** con el *nombre* del modo. `call()` exige `length()==1` y `valueToString`.
- Conversión nombre→id: `WebApiAddonUtils::convStringToId(paramName=0x11, name, &id)` (call site `0x2115da`,
  implementación `0x1879dc`); traza `[INF:setFocusMode] focusModeId=%d` (str `0x323fb0`);
  si la conversión falla: `[setFocusMode] setFocusMode err` (str `0x323f74`).
- Envío: `setEvtParamId(msg,0x186,0x81)`; ACK `0x188/0x83`.
- Tabla nombre↔id del enfoque en `.rodata` @ **`0x2e5244`** (`{u32 id; const char* name}`):

| id | nombre | dirección cadena |
|---|---|---|
| 0 | `""` (vacío) | `0x2e37c8` |
| 1 | `MF` | `0x2e6cdc` |
| 2 | `AF-S` | `0x2e6ce0` |
| 3 | `A-Macro` | `0x2e6ce8` |
| 4 | `AF-C` | `0x2e6cf0` |
| 5 | `AF-A` | `0x2e6cf8` |
| 6 | `AF-D` | `0x2e6d00` |
| 7 | `DMF` | `0x2e6d08` |
| 8 | `MF-R` | `0x2e6d0c` |
| `-1` | terminador | — |

- Existe además una tabla reducida (3 entradas) @ `0x2e5b90`: `MF`→1, `AF-S`→2, `AF-C`→3; su parámetro
  asociado **NO_VERIFICADO** (parece un subconjunto para otro contexto/ajuste).
- Cuáles de esos nombres están realmente disponibles lo decide la cámara:
  `getSupportedFocusMode` (id `0x2b`) y `getAvailableFocusMode` (id `0x2c`) devuelven listas de nombres;
  el `invoke_cmd` de ambos traduce ids numéricos a nombre con trazas
  `getSupportedFocusMode %d -> %s` (`0x2fc498`) y `getAvailableFocusMode focusMode %d -> %s` (`0x2fc3ac`).

**`getFocusMode`**: esquema literal `0x33d658`
`{"type":"string", "currentFocusMode":"string", "focusModeCandidates":"string*"}` (usado por
`GetEvent::resultTypes`, campo `focusMode` de `getEvent`). **VERIFICADO** para el evento;
**INFERENCIA** (fuerte) que la respuesta de `getFocusMode` tenga la misma forma sin el campo `type`,
porque los `invoke_cmd` de la familia comparten constructor de estructura y traducen ids a nombres
(`getFocusMode %d -> %s`, str `0x2fb51c`).

## 9. Receta para mover el punto desde un PC

```http
POST /sony/camera   (JSON-RPC de orb)
{"method":"setTouchAFPosition","params":[50.0,30.0],"id":1,"version":"1.0"}
```
- `params[0]` = x % (0 = izquierda, 100 = derecha), `params[1]` = y % (0 = arriba, 100 = abajo).
- Respuesta correcta: `{"result":[0,{"AFResult":true,"AFType":"Touch"}]}`. **INFERENCIA** sobre el
  envoltorio JSON-RPC exacto (orb lo sirve por su capa libj; el nombre del endpoint no se ha fijado aquí),
  **VERIFICADO** sobre el contenido del array de resultados.
- Antes de usarlo: `getAvailableApiList` debe contener `"setTouchAFPosition"`; si no, la cámara no lo
  reporta como disponible en ese estado (ver §5).
- Para “arrastrar”: repetir la llamada con la nueva posición (una por frame de interés). No existe API de
  lectura de la posición actual (ver §6).

## 10. Límites de este informe

- No se ha ejecutado ni instrumentado nada; todo es estático (`readelf`, Capstone, REA/Ghidra sobre
  `orb-server`, lectura de tablas de `libInfraWebApi.so` y `libInfraRemoteControlNet.so`).
- **NO_VERIFICADO**: (a) si la cámara hace AF puntual, continuo o sólo reposiciona el marco al recibir
  `0x192/0x8d`; (b) condiciones de estado que publican el id 45; (c) semántica exacta de `AFResult` y de
  `"set"`; (d) comportamiento en A7S (API idéntica, soporte interno distinto).
- Siguiente paso propuesto para (a)/(b): abrir `libInfraRemoteControlNet.so` en REA y analizar
  `PsmRcWebAPIGetTouchAFPosition`, `RcCameraStateSetParameter` (`0x8ed9`) y
  `PsmRcWebAPIEditAvailableApiList`.

## 11. Reproducibilidad

```bash
O=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/bin/orb-server
python3 analysis/eyeaf/tools/armdis.py $O 0x214ec8 0x215590        # invoke(double,double)
python3 analysis/eyeaf/tools/xref_movt.py $O 0x214ec8             # refs
python3 analysis/eyeaf/tools/xrefs.py $O 0x327cf8                 # cadena de traza
# pseudocódigo: MCP rea (open_binary + batch_decompile de las direcciones de §2)
```

Datos crudos en `analysis/eyeaf/data/`: `dynsym.json`, `all_strings.json`,
`remote_methods_a6000.json` (86 métodos), `api_id_table_a6000.json` (ids↔nombres),
`a6300_routes.json` (243 rutas del A6300) y los desensamblados `*.dis.txt`.
