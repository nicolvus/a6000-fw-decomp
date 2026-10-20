# Sesión 17, Claude A (hilo principal, sin subagentes) — Arbitraje ConnectPin/StsViewer

Alcance: análisis estático exclusivo de `libObj.so` y `libMWF.so` fw 3.21 (Sony A6000), ambos del mismo
árbol `firmware/extracted/fw321/.../lib/`. **No se afirma que SilentShutter funcione.** No hay cámara
conectada, no se flashea nada. Direcciones **ELF** salvo que se indique "Ghidra VA" (= ELF + 0x10000).

**Confirmo que no delegué ningún trabajo a otro agente ni subagente en esta sesión** (restricción
explícita del encargo). Todo el desensamblado (`llvm-objdump -d --triple=thumbv7-linux-gnueabi`),
las decompilaciones (`scripts/libobj_dec.sh`, Ghidra headless, proyecto `analysis/ghidra/a6000-libs`)
y la lectura de tablas de símbolos dinámicos se ejecutaron directamente desde este hilo con mis propias
herramientas (Bash/Read/Write), sin invocar la herramienta Agent en ningún momento.

Modelo/esfuerzo real usado: Claude Sonnet 5, el definido por la configuración de esta sesión en segundo
plano (no lo subí ni lo bajé yo).

---

## Corrección de direcciones respecto al encargo (hallazgo metodológico previo)

El encargo cita `GetStsViewer` en ELF `0x4294CC`. Al decompilar con Ghidra VA = ELF+0x10000 = `0x4394cc`
obtuve una función trivial sin sentido (dos saltos, sin indexado de tabla) — señal de desalineación. Verifiqué
con `llvm-objdump` crudo que el byte en ELF `0x4294cc` cae **a mitad de una instrucción Thumb de 4 bytes**
(`blx _Znwj@plt` en `0x4294ca-0x4294ce`), es decir, `0x4294cc` NO es una dirección de entrada válida en
espacio ELF. Comparando con el cuerpo decompilado de `TM::createLifeCycles` (que sí decompiló correctamente
en ELF `0x4195c0`, confirmando que ahí el offset +0x10000 es correcto), el propio pseudocódigo de Ghidra
cita la llamada a GetStsViewer como `func_0x004294cc` — pero esa cifra ya está en el espacio de direcciones
interno de Ghidra (ELF+0x10000), no en ELF crudo. Por tanto la dirección ELF real de `GetStsViewer` es
`0x4294cc − 0x10000 = 0x4184cc`, y hay que pedir la decompilación con Ghidra VA `0x4294cc` directamente
(sin sumar otra vez 0x10000). Hecho así, la decompilación es coherente y completa (ver abajo). Dejo esto
documentado explícitamente porque puede repetirse en sesiones futuras que reusen la cifra del encargo.

`ObjIf::ConnectPin` (ELF `0x41c25e`), en cambio, **sí** es una dirección ELF literal válida: apunta a un
sitio de llamada real `blx 0xdc8e8 <_ZN3MWF5ObjIf10ConnectPinEPvPNS_6ObjMsgES1_PNS_15ObjStatusViewerE@plt>`
dentro de una función anónima (stripped) cercana al símbolo exportado `ObjHandover_Create` — confirmado por
`llvm-objdump -d` directo sin offset. Esto reveló un hecho más importante que el propio sitio de llamada:
**`ConnectPin` no está definida en `libObj.so`**, es un símbolo importado (`@plt`) resuelto en `libMWF.so`.

---

## Hallazgo nuevo central: `ConnectPin`/`ObjPin::Connect`/`ObjStatusViewer` están en `libMWF.so`, no en `libObj.so`

Localicé en la tabla dinámica de `libMWF.so` (`llvm-objdump -T`) los símbolos reales, **definidos** (no
`UND`) en esa librería:

| Símbolo real (demangled) | ELF en `libMWF.so` | Tamaño |
|---|---|---|
| `MWF::ObjIf::ConnectPin(void*, ObjMsg*, ObjMsg*, ObjStatusViewer*)` | `0x2450c` | 0xc8 |
| `MWF::ObjPin::Connect(ObjPin*, ObjStatusViewer*)` | `0x29588` | 0x150 |
| `MWF::ObjPin::Disconnect()` | `0x29492` | 0xf6 |
| `MWF::ObjStatusViewer::GetStatus()` | `0x2c798` | 0xe |
| `MWF::ObjStatusViewer::GetStatusStore()` | `0x2c7c2` | 0x8 |
| `MWF::ObjStatusViewer::GetTargetStatus()` | `0x2c7a6` | 0xe |
| `MWF::ObjStatusViewer::SetCallBackFunc(void(*)(int,void*), void*)` | `0x2c7b4` | 0xe |
| `MWF::ObjStatusViewer(DefObjStatus::Status)` (ctor) | `0x2c758` | 0x40 |
| `MWF::ObjStatusConfig::Register(ObjStatusViewer*)` | `0x2c264` | 0x3c |
| `MWF::ObjIf::DisconnectPin(void*, ObjMsg*)` | `0x245d4` | 0xa4 |
| `AVBIZ::UNIVERSE::UObjPin::Connect(ObjPin*, ObjStatusViewer*, bool)` | *(UND en libMWF, no resuelta aquí)* | — |

Decompilé con Ghidra (Ghidra VA = ELF+0x10000, igual convención que `libObj.so`) `ConnectPin` (`0x3450c`),
`ObjPin::Connect` (`0x39588`) y `ObjStatusViewer::GetStatus` (`0x3c798`). Evidencia cruda completa en
`analysis/session17/claude-a/mwf_decomp.json` (y `getstsviewer_decomp.json`, `control_decomp.json` para
`GetStsViewer`/`TM::createLifeCycles`/el sitio de llamada de `ConnectPin`).

### `MWF::ObjIf::ConnectPin` (ELF libMWF `0x2450c`) — VERIFICADO

```
undefined4 ObjIf::ConnectPin(int *param_1, msg2, msg3, statusViewer)
{
  if (<flag de tracing activo>) { ...registra param_1, msg3, statusViewer en un buffer de traza... }
  uVar2 = (**(code **)(*param_1 + 0xc))(param_1, msg2, msg3, statusViewer);   // vtbl slot 3, llamada VIRTUAL
  if (<flag de tracing activo>) { ...registra uVar2 (resultado)... }
  return uVar2;
}
```

Es un **wrapper de trazabilidad genérico**: no contiene ninguna lógica de pines, tipos o exclusión. Se
limita a (opcionalmente) registrar los cuatro parámetros en un buffer de traza de depuración y a reenviar
la llamada al **método virtual** del objeto `param_1` (slot `+0xc` de su vtabla). Esto significa que el
comportamiento real de "ConnectPin" depende de qué clase concreta implementa ese slot de vtabla para el
objeto que se está conectando — para un pin estándar `MWF::ObjPin`, ese slot resuelve a `ObjPin::Connect`
(ver abajo); otras subclases (p. ej. `AVBIZ::UNIVERSE::UObjPin`, vista en el dynsym con firma
`Connect(ObjPin*, ObjStatusViewer*, bool)`, no resuelta/decompilada aquí) podrían tener lógica distinta —
**no descartado, no verificado para esas subclases**.

### `MWF::ObjPin::Connect` (ELF libMWF `0x29588`) — VERIFICADO (lógica completa leída)

```
int ObjPin::Connect(ObjPin *this, ObjPin *other, ObjStatusViewer *viewer)
{
  if (other == 0 || other == this)            return 3;        // pin inválido
  if (*(other+4) != *(this+4))                 return 0x7000;   // "kind"/pin_type no coincide
  dir = *(other+0xc);
  if      (dir == 1) { if (*(this+0xc) == 0)            goto err_0x7003; }
  else if (dir == 2) { if (*(this+0xc) != 2)             goto err_0x7003; }
  else if (dir == 0) { if (*(this+0xc) != 1)             goto err_0x7003; }
  else                                                    goto err_0x7003;  // dirección desconocida

  // --- a partir de aquí, SIN más comprobaciones de estado previo ---
  func_0x0002c3f4(this+0x1c);  func_0x0002c3f4(other+0x1c);     // lock/sección crítica (par, no exclusión lógica)
  *(this+0x10)  = other;                      // SOBREESCRIBE el puntero de "pin conectado" de this
  *(this+0x38)  = 1;                          // flag "conectado"
  if (viewer != 0) {                          // registra un objeto de estado nuevo (0x2c B) en el viewer
    alloc = new(0x2c); ObjStatusConfig::Register(alloc, viewer);
    *(this+0x18) = alloc;
  }
  *(other+0x10) = this;                       // SOBREESCRIBE el puntero de "pin conectado" de other
  if (viewer != 0) { ...mismo registro para 'other'... }
  ...notificación/evento de traza (id 0x82, valores this/other, resultado)...
  return iVar2;  // código de resultado de la notificación de traza, no de la conexión misma
}
```

**Hallazgos clave (VERIFICADO por lectura directa del decompilado, no inferencia):**

1. **No hay comprobación de "¿ya está conectado a otro pin?"** antes de escribir `*(this+0x10)=other` ni
   `*(other+0x10)=this`. Las tres únicas condiciones de rechazo son: pin nulo/igual a sí mismo, `kind`
   (`+4`) distinto entre ambos pines, y dirección (`+0xc`) incompatible (0=entrada/1=salida/2=ambas, según
   el patrón de comparación cruzada). **No existe ningún guard de exclusividad de slot ni de "pin de
   destino ya ocupado"** en esta función.
2. El campo `this+0x10` ("pin conectado actual") es **un único puntero, no una lista**. Esto implica que,
   a nivel de estructura de datos de `ObjPin`, un pin de destino solo puede recordar **un** origen conectado
   a la vez: una segunda llamada a `Connect()` sobre el mismo pin de destino con un origen distinto
   **sobrescribiría** el puntero anterior sin desconectar explícitamente al primero (no hay `Disconnect()`
   automático visible en este camino).
3. El parámetro `ObjStatusViewer*` (el "StsViewer" del encargo) **no participa en ninguna decisión de
   aceptar o rechazar la conexión**. Su único uso es: si no es nulo, se asigna un nuevo objeto de estado
   de 0x2c bytes por cada pin conectado y se registra ante el viewer vía
   `MWF::ObjStatusConfig::Register(ObjStatusViewer*)`. Es decir, el viewer es un **registro/agregador de
   notificación de estado de varias conexiones**, no un cerrojo de aceptación.

### `MWF::ObjStatusViewer::GetStatus` (ELF libMWF `0x2c798`) — VERIFICADO (trivial)

```
void ObjStatusViewer::GetStatus(this) { <llamada indirecta a 0xffbb432c(*(this+4)); 0xff834854(); } 
```
Cuerpo de 14 bytes: delega a dos punteros de función cuyo destino no pude resolver en esta sesión (las
direcciones `0xffbb432c`/`0xff834854` no corresponden a ningún símbolo ni PLT de `libMWF.so` que haya
localizado; posible reubicación/relleno de Ghidra sin resolver, o llamada a una tabla de función miembro
indirecta de otra clase). **NO VERIFICADO** el contenido exacto; lo que sí es VERIFICADO es que `GetStatus`
es trivial (una delegación de 14 bytes), consistente con ser un simple getter de estado, no un método con
lógica de arbitraje.

---

## `GetStsViewer` (ELF libObj.so `0x4184cc`, Ghidra VA `0x4294cc`) — VERIFICADO: caché singleton por `sts_id`

```
int GetStsViewer(int sts_id)
{
  mgr = _DAT_00429700;                 // puntero singleton al TopologyManager (mismo objeto que usa createLifeCycles)
  result = 0;
  if (sts_id != 0) {
    // busca sts_id como clave en un mapa en *mgr+0x48
    found = map_find(*mgr+0x48, &sts_id);
    if (found) {
      result = *(found_entry + 4);     // devuelve el ObjStatusViewer* YA EXISTENTE para ese sts_id
    } else {
      viewer = alloc(8);
      ObjStatusViewer::ctor(viewer, DefObjStatus::Status(1));   // construye uno nuevo
      result = viewer;
      if (viewer) map_insert(*mgr+0x48, sts_id, viewer);        // lo cachea bajo la clave sts_id
    }
  }
  return result;   // 0 si sts_id==0 (filas sts_id=0 no tienen viewer)
}
```

**Esto confirma, con evidencia directa de código (no inferencia), el mecanismo que sesión 16 solo
planteaba como hipótesis**: `GetStsViewer` es un *get-or-create* sobre un mapa indexado por `sts_id`,
propiedad del mismo objeto `TopologyManager` singleton (`_DAT_00429700`) que contiene la tabla de 211 filas
en `+0x60` (ver `TM::createLifeCycles` abajo). Como las filas `0x2a` y `0xb4` comparten literalmente
`sts_id=6`, **las dos llamadas a `GetStsViewer(6)` devuelven el mismo puntero `ObjStatusViewer*`** (la
primera lo crea, la segunda recupera el mismo objeto del mapa). Las filas con `sts_id=0` (`0x0a`, `0x07`)
NO tienen viewer (la función devuelve 0 para `sts_id==0`): es decir, **`0x0a` y `0x07` nunca pasan por este
mecanismo de registro de estado compartido en absoluto**.

---

## `TM::createLifeCycles` (ELF `0x4195c0`) — confirma el rol del StsViewer en la construcción de topología

```
void TM::createLifeCycles(void *param_1)
{
  mgr = _DAT_00429700;
  n = rowCount(mgr+0x60);
  for (i = 0; i < n; i++) {
    row_id   = rowIndexTable[i];
    srcPin   = ResolvePin(table[row_id].src_obj_field, param_1);   // table+8  = src_obj
    dstPin   = ResolvePin(table[row_id].dst_obj_field, param_1);   // table+0x14 = dst_obj
    viewer   = GetStsViewer(table[row_id].sts_id_field);           // table+4  = sts_id  <-- AQUÍ
    if (<condición de pertenencia del modelo a esta lista de IDs>) {
      if (srcPin == 0 || dstPin == 0) { <error, log> }
      else {
        lc = alloc(0x14);                        // LifeCycle (0x14 B)
        LifeCycle::ctor(lc, row_id, srcPin, dstPin, viewer);   // guarda id, src, dst y EL VIEWER
        if (lc == 0) { <error, log> } else { <inserta lc en una lista del manager (+0x30)> }
      }
    }
  }
}
```

Esto confirma (VERIFICADO) que **cada fila de topología obtiene su propio objeto `LifeCycle` que almacena
el `ObjStatusViewer*` correspondiente a su `sts_id`**, calculado en el momento de construir la lista de
ciclos de vida (no en el momento de `Connect()` mismo). `LifeCycle::ctor` es `func_0x0042b6c0`; no decompilé
su cuerpo interno esta sesión (fuera del bloqueo de las 10 preguntas), pero el propio sitio de llamada ya
demuestra qué datos recibe.

---

## Respuestas a las 10 preguntas del encargo

### 1. ¿Qué representa realmente `StsId`?

**VERIFICADO**: `StsId` es la clave de un mapa (`GetStsViewer`, ELF `0x4184cc`) propiedad del
`TopologyManager`, que indexa objetos `MWF::ObjStatusViewer` cacheados. No es un identificador de permiso
ni de exclusión por sí mismo: es literalmente una clave de caché de objetos de estado/notificación
compartidos. `sts_id=0` es un valor especial que **nunca crea ni devuelve un viewer** (filas `0x0a`/`0x07`
no participan de este mecanismo). `sts_id=6` es compartido exactamente por las filas `0x2a` y `0xb4`
(únicas dos con ese valor en las 211 filas, re-confirmado en sesión 16 y de nuevo aquí).

### 2. ¿Qué mantiene el objeto `StsViewer` (`ObjStatusViewer`)?

**VERIFICADO (parcial)**: por `ObjPin::Connect`, el viewer recibe, por cada pin que se conecta pasándole
ese viewer, un objeto de estado nuevo de 0x2c bytes registrado vía `ObjStatusConfig::Register`. Por
`ObjStatusViewer::GetStatus`/`GetStatusStore`/`GetTargetStatus` (nombres reales del dynsym de libMWF), el
objeto expone una consulta de estado actual vs. estado objetivo — es decir, es un **agregador de estado de
una o varias conexiones de pin**, con capacidad de callback (`SetCallBackFunc`). No es, por su interfaz
(`GetStatus`/`GetTargetStatus`/callback), una primitiva de exclusión mutua (no hay `Lock`/`TryAcquire` en
los símbolos exportados de la clase). **NO VERIFICADO** el contenido exacto de `GetStatus` (delega a dos
punteros que no pude resolver).

### 3. ¿Existe arbitraje de conexión?

**NO_VERIFICADO → ahora con evidencia fuerte de que NO, al menos en `ObjPin::Connect`**: la función
completa decompilada solo rechaza por (a) pin nulo/igual, (b) `kind` incompatible, (c) dirección
incompatible. **No hay ninguna comprobación de "pin de destino ya conectado a otro origen"** antes de
sobrescribir el puntero de conexión. Clasificación: **VERIFICADO que `ObjPin::Connect` no arbitra por
ocupación de pin**; **NO_VERIFICADO/NO_DESCARTADO** que exista arbitraje en una capa superior (p. ej. en
quien decide invocar `createLifeCycles`/`Connect` para una fila u otra, o en la subclase `AVBIZ::UNIVERSE::
UObjPin::Connect`, no decompilada esta sesión) o en el `ObjStatusViewer::GetStatus` no resuelto.

### 4. ¿`0x2a` y `0xb4` son alternativas mutuamente excluyentes?

**INFERENCIA fuerte, a nivel de estructura de datos**: SÍ, en el sentido de que el campo `dst_pin+0x10`
("pin conectado actual") del pin de entrada único de `StillRecorder` **es un solo puntero, no una lista**.
Conectar `0x2a` (Effect→Recorder) escribe ese puntero con el pin de salida de Effect; conectar `0xb4`
(objeto 53→Recorder) lo sobrescribiría con el pin de salida del objeto 53. **No pueden ambas ser el "pin
conectado" simultáneamente del mismo destino a la vez**, porque no hay estructura de lista en `ObjPin`,
solo un puntero escalar. Esto es coherente con, y refuerza, que comparten el mismo `sts_id=6`/mismo
`ObjStatusViewer` — probablemente como forma de que la capa superior (TopologyManager/modelo) sepa que son
alternativas del mismo "grupo lógico" y deba desconectar una antes de conectar la otra, aunque **no
encontré el código que impone ese orden** (sería responsabilidad del llamador, no de `ObjPin::Connect`).
Clasificación: **INFERENCIA fuerte (estructura de datos), NO VERIFICADO (política explícita de exclusión
a nivel de llamador)**.

### 5. ¿Puede `0x2a` estar activa simultáneamente con `0x0a` y `0x07`?

**VERIFICADO que no hay ningún obstáculo estructural para ello**: `0x0a` (Camera.out0→Effect.in0) y `0x07`
(Effect.out0→Renderer.in0) tienen `sts_id=0` y por tanto **ni siquiera pasan por `GetStsViewer`** (no
comparten viewer con nada). Son pines *distintos* de `ObjEffect` (`in0` para `0x0a`, `out0` para `0x07`,
`out1` para `0x2a`) — cada pin tiene su propio campo `+0x10`, así que no hay colisión de puntero entre
ellos. La única pregunta real es si el **modo interno de Effect** (`EffectInternalMode`, ver sesión 16)
permite servir simultáneamente la salida `out0` (Renderer, modo normal de visor) y `out1` (Recorder, según
sesión 14/15/16 ligado a los modos `{1..5}`) — eso sigue **NO VERIFICADO** (bloqueo que esta sesión no
cierra: no se trazó el disparador real de los modos 2-5 ni se encontró guard de exclusión en el gestor de
pines de ObjEffect en sesión 16, confirmado otra vez aquí al no encontrar tal guard en `ObjPin::Connect`
tampoco). Es decir: **`0x0a`+`0x07` conviviendo con `0x2a` no está prohibido por `ConnectPin`/`ObjPin`**;
si está prohibido, sería por el modo interno de `ObjEffect`, cuestión que permanece abierta.

### 6. ¿Cómo se crea una topología con ID dinámico?

**VERIFICADO (mecanismo general, confirmado por lectura de `createLifeCycles`)**: no hay "creación de una
topología individual" como operación aislada — `TM::createLifeCycles` (ELF `0x4195c0`) recorre TODAS las
filas activas de la tabla de 211 para un "modelo" dado (`param_1`), resolviendo para cada una el pin origen,
el pin destino y el `ObjStatusViewer` (vía `sts_id`), y construye un objeto `LifeCycle` (0x14 bytes) que
retiene esos tres punteros. El ID dinámico de sesión 16 (76/93 sitios de `createTopology` sin literal
resuelto) corresponde a filas que entran en esta misma maquinaria pero cuyo índice de fila lo decide una
tabla externa o un campo de instancia en tiempo de ejecución, no un `movs r3,#ID` visible en el sitio de
llamada — mecanismo igual, origen del índice distinto. Esta sesión no decompiló más sitios dinámicos
concretos (fuera de alcance de las 10 preguntas), por lo que sigue **NO VERIFICADO** cuál o cuáles de esos
76+116 sitios dinámicos corresponden específicamente a las filas `0x2a`/`0xb4`/`0x0a`/`0x07`.

### 7. ¿Existe otro creador de `0x2a` además de `ModelPbCap`?

**Sin cambios respecto a sesión 16: NO_VERIFICADO (no descartado)**. No repetí el barrido de los 213
sitios esta sesión (no era el foco); la cobertura de sesión 16 (17/93 create resueltos a literal, único
`0x2a` = `ModelPbCap` ELF `0x613694`) sigue siendo la mejor evidencia disponible. Lo que esta sesión añade
es contexto: dado que `createLifeCycles` resuelve el viewer en el momento de construir la *lista completa*
de un modelo (no fila por fila bajo demanda), "crear la fila `0x2a`" en la tabla de 211 no implica por sí
solo que se llegue a invocar `ObjPin::Connect` para esa fila — haría falta que el modelo en cuestión
también incluya `0x2a` en su lista de filas activas pasada a `createLifeCycles`. No verifiqué qué modelos
(aparte de `ModelPbCap`) incluyen la fila `0x2a` en su lista.

### 8. ¿Qué es el "objeto 53" (origen de la fila `0xb4`)?

**NO_VERIFICADO (identidad)**, sin cambios respecto a sesiones previas. Evidencia circunstancial ya
documentada (no generada esta sesión, re-citada para contexto): el objeto 53 tiene salidas YC adicionales
hacia `ObjEffect` mismo (`claude-main-bridge-verification.md`: fila `0xaf` objeto53→Effect.in0 con
`sts_id=0`; fila `0xcc` objeto53.out3→Effect.in1 con `sts_id=2`) y, según `objhandover-2a-topology.md`,
tiene "3 entradas YC y 4 salidas YC" más E/S STILL — un perfil compatible con un objeto puente/escalador
(`ObjScalar` es la hipótesis más citada en sesiones previas, pero no until confirmada por constructor). No
dediqué tiempo esta sesión a localizar su constructor porque no era parte de las 10 preguntas asignadas
con evidencia nueva disponible en el tiempo dado; lo dejo explícitamente como NO_VERIFICADO, no como
"resuelto por descarte".

### 9. ¿Quién invoca mediante vtable a `ExecCmdAppFaderEfctEndEvt` y `SequencePinDeliverBase`?

**NO_VERIFICADO, sin avance esta sesión**. Mi foco (StsViewer/ConnectPin/createLifeCycles) no tocó estas
dos funciones; sigo sin localizar el `bl`/`blx` indirecto vía vtabla que las invoca. Dato colateral
relevante encontrado esta sesión: `ObjIf::ConnectPin` en `libMWF.so` también despacha por vtable
(`(**(code**)(*param_1+0xc))(...)`), es decir, **el patrón de "wrapper de trazabilidad + despacho virtual"
es el mismo mecanismo genérico del framework MWF** que probablemente usan también los manejadores de
mensaje de `ObjEffect` — refuerza (sin probar) que localizar esos dos invocadores pasa por encontrar qué
tabla de vtabla instala esos punteros para la instancia concreta de `ObjEffect` activa, no por un `bl`
directo.

### 10. ¿Existe algún camino de modelo fotográfico hacia los modos 2-5 de `EffectInternalMode`?

**NO_VERIFICADO, sin avance esta sesión** (fuera del alcance directo de StsViewer/ConnectPin que me
correspondía). Lo que esta sesión sí aporta indirectamente: confirmé que `0x0a` y `0x07` (`sts_id=0`, sin
viewer) son estructuralmente independientes de `0x2a` (`sts_id=6`, con viewer compartido con `0xb4`) a
nivel de pines — es decir, si existiera un modelo de disparo fotográfico que alcanzara los modos 2-5, no
habría colisión de pin con la ruta normal de visor (`0x0a`→`0x07`) a nivel de `ObjPin::Connect`; la
pregunta de si tal modelo existe permanece abierta y no se investigó aquí.

---

## Clasificación global de esta sesión

| # | Afirmación | Clasificación |
|---|---|---|
| `ConnectPin`/`ObjPin::Connect`/`ObjStatusViewer` están definidos en `libMWF.so`, no en `libObj.so` (son `@plt` en `libObj.so`) | VERIFICADO (dynsym + decompilado) |
| `GetStsViewer` es un *get-or-create* por `sts_id` sobre un mapa del `TopologyManager` singleton | VERIFICADO (decompilado completo) |
| `0x2a` y `0xb4` (únicas filas con `sts_id=6`) obtienen el MISMO puntero `ObjStatusViewer*` | VERIFICADO (consecuencia directa de 1+2) |
| `sts_id=0` (filas `0x0a`, `0x07`) nunca obtiene viewer | VERIFICADO (rama `if(sts_id!=0)` de `GetStsViewer`) |
| `ObjPin::Connect` no comprueba si el pin de destino ya está conectado a otro origen antes de sobrescribir | VERIFICADO (lectura completa del decompilado) |
| El campo "pin conectado" de `ObjPin` es un puntero escalar, no una lista | VERIFICADO |
| `0x2a` y `0xb4` no pueden ambas ser el pin conectado del mismo destino a la vez (estructuralmente) | INFERENCIA fuerte |
| El `ObjStatusViewer` participa en la decisión de aceptar/rechazar una conexión | DESCARTADO (no aparece en ninguna rama condicional de `ObjPin::Connect`) |
| `TM::createLifeCycles` resuelve pin origen, pin destino y viewer por fila, para TODAS las filas activas de un modelo, en una sola pasada | VERIFICADO |
| `0x0a`/`0x07` y `0x2a` pueden coexistir sin colisión de pin a nivel de `ObjPin` | VERIFICADO (pines distintos, sin dependencia de `sts_id`) |
| Coexistencia real de `0x0a`+`0x07`+`0x2a` a nivel de modo interno de `ObjEffect` | NO VERIFICADO (bloqueo persiste) |
| Otro creador de `0x2a` aparte de `ModelPbCap` | NO VERIFICADO (sin cambios de sesión 16) |
| Identidad del "objeto 53" | NO VERIFICADO (sin cambios) |
| Invocador vía vtabla de los dos escritores de modo 1 | NO VERIFICADO (sin cambios) |
| Camino fotográfico hacia modos 2-5 de Effect | NO VERIFICADO (sin cambios) |
| Arquitectura E (Live View → EncodeStill vía Effect) | **Sin cambio de veredicto**: ni viable ni descartada. Esta sesión cierra el bloqueo técnico "decompilar GetStsViewer/ConnectPin" con un resultado que **debilita** la hipótesis de que el StsViewer compartido sea un mecanismo de arbitraje activo (es un agregador de notificación, no un cerrojo), pero **refuerza** la hipótesis de exclusión estructural pasiva entre `0x2a` y `0xb4` por el puntero escalar de `ObjPin`. Ninguna pieza nueva conecta esto con un disparo fotográfico real. |

## Siguiente bloqueo técnico

1. Decompilar `LifeCycle::ctor` (ELF libObj `0x42b6b0` aprox., Ghidra VA `0x42b6c0`) y la función que
   realmente invoca `ObjPin::Connect`/`ObjIf::ConnectPin` para un `LifeCycle` ya construido (probablemente
   un método `LifeCycle::Activate`/`Connect` separado de `createLifeCycles`), para saber en qué momento
   exacto del ciclo de vida de un modelo se produce la llamada a `Connect()` real (créación de lista ≠
   conexión activa, según el propio `createLifeCycles`: solo construye y encola el `LifeCycle`, no veo ahí
   la llamada a `Connect`).
2. Decompilar `AVBIZ::UNIVERSE::UObjPin::Connect(ObjPin*, ObjStatusViewer*, bool)` (símbolo UND en
   `libMWF.so`, probablemente en otra librería del framework AVBIZ) para descartar que los pines de
   `ObjEffect`/`StillRecorder` usen esta variante en vez de la `MWF::ObjPin::Connect` genérica analizada
   aquí — si la usan, esta sesión no cubre su lógica de arbitraje (si la tiene).
3. Resolver los dos punteros de función indirectos (`0xffbb432c`, `0xff834854`) dentro de
   `ObjStatusViewer::GetStatus` para confirmar al 100% que no hay lógica de exclusión oculta ahí.

## Dato intercambiable con Codex C (SDF/YC/Sequence `0x6013`)

**Hallazgo verificable concreto**: `ObjEffect` puede tener su **entrada `in0` (recibiendo YC de
`ObjCamera.out0`, fila `0x0a`, `sts_id=0`, ELF tabla `0xcc4210+0x0a*0x20`) y su salida `out1` (hacia
`ObjStillRecorder.in0`, fila `0x2a`, `sts_id=6`, ELF tabla `0xcc4210+0x2a*0x20`) conectadas simultáneamente
sin ninguna colisión estructural detectada en `MWF::ObjPin::Connect` (ELF `libMWF.so` `0x29588`) ni en
`GetStsViewer`/`TM::createLifeCycles`** (ELF `libObj.so` `0x4184cc`/`0x4195c0`): son pines distintos del
mismo objeto `ObjEffect` (cada uno con su propio campo escalar de "pin conectado" en offset `+0x10` de su
propia instancia `ObjPin`), y `in0` (`sts_id=0`) ni siquiera comparte `ObjStatusViewer` con `out1`
(`sts_id=6`). La única colisión estructural real encontrada es entre **`out1` de Effect (fila `0x2a`) y la
salida #2 del objeto 53 (fila `0xb4`)**, que comparten el mismo pin de destino único en `ObjStillRecorder`
y por tanto no pueden ambas ser simultáneamente "el pin conectado" de ese destino (el campo es un puntero
escalar, no una lista) — si Codex C está investigando si SDF/YC puede alimentar `StillRecorder` en paralelo
con `ObjEffect` por una ruta distinta a la `0xb4`, esta restricción escalar en `ObjPin` es la pieza concreta
a tener en cuenta: cualquier segunda fuente que *también* llame `Connect()` sobre el mismo pin de entrada de
`StillRecorder` sobrescribirá, no sumará, la conexión de Effect, salvo que pase por un pin de entrada
distinto (StillRecorder tiene más de un pin de entrada declarado en la tabla — no enumerados aquí; fuera de
mi alcance esta sesión).
