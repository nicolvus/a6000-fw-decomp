# G22-DISPATCH — de la tecla a la acción: quién convierte el evento, quién lo consume y por qué la acción 4 no se ejecuta

**Estado (27-11-2026, sesión G22-ESTATICO + G22-TECLA): CAUSA ESTÁTICA IDENTIFICADA Y MEDIDA; el destino ya sale `c`
y lo que falta es el eslabón de la vista.** La sesión **G22-TECLA** (§7.3) cerró la hipótesis del §7: el destino de los
tres eventos no lo fija `libObj+0x111972` (ese código **no se ejecuta**: 0 ramas y 0 punteros en el fichero) sino
`libObj+0x113076`, y el llamante real de `InputService::createEvent` se ve en `TRACE 1106b8 … lr=libObj+0x113080`.
Con el interruptor `DESTKEYV=1` (3 sitios, `04 22` → `0c 22`) los tres eventos salen `dest=12` y **se despachan**
(`TRACE 7eed0c`), pero el bit 8 de `AppSystem::dispatch` no llega a `libObj+0xf59f0` (ese thunk solo se ve llamarse
desde `viewUnified2+0x198450` con ids numéricos) y `execAction` (`libObj+0x11817e`) sigue a 0 disparos. La tecla
Reproducción sí llega a la cola
del framework (medido en [G22-COLA](g22-cola-eventos.md): `code=150100f2 dest=4 clase=1`), pero **el `destino` del
evento es el byte `4` de `Event[+8]`, y la vista de disparo solo recibe eventos por el bit `8` de ese byte**
(`AppSystem::dispatch`, `libObj+0x7eed0c`). Con `dest & 8 == 0` el evento se entrega al gestor de datos
(`libObj+0x7f4528`), cuyo conmutador por identificador no conoce `0x1501xxxx` ni `0x1507xxxx`, y
`ActionEventMapBase::DispatchEvent` (`libObj+0xf59f0`) **nunca se ejecuta con un evento de entrada**. La «lista del
filtro de la vista» no es de la vista: es la `std::list` de trabajo de `InputService` (`InputService+0xc`), la vacía
el propio `pushFilterEvent` y su contenido va a `EventManager::push`. Ni la máscara `0x7ffffffe` ni la clase `1`
son la puerta: la máscara es un dato que `InfraInput::GetEventStatus` **devuelve** y la clase solo elige cola.

§1–§6 y §9 son de la sesión **sin cámara y sin QEMU** (todo leído con `readelf`/`capstone` sobre los ELF 3.21 de
`analysis/gui/g22/harness/stage/cam/usr/lib`); §7.1/§7.2 y §7.3 son **medidos en el invitado** con `qemu-system-arm` y
el arnés (`scripts/gui/harness/live.py`), sin cámara. Direcciones = VA del ELF (el primer `PT_LOAD` tiene vaddr 0; el
segundo lleva +0x8000, de ahí `v2o`). Los cuatro usuarios de `dest` se citan con sus bytes.

---

## 1. Respuesta 1 — quién consume la «lista del filtro» y por qué no ejecuta

`InputService::pushFilterEvent` (`libObj+0x1117f4`) ya está descrito en [G22-COLA §2](g22-cola-eventos.md#2-la-cadena-de-la-tecla-hasta-la-cola-verificado-en-el-invitado);
lo que faltaba era **de quién es la lista**:

```asm
1117f4  push {r4,r5,r6,r7,lr} · sub sp,#0xc
1117fa  mov  r6, r0            ; r6 = this (InputService)
111800  add.w r4, r6, #0xc      ; r4 = &this-><lista>   <-- la lista es del SERVICIO, no de la vista
111810  bl   0x1114b0          ; clear()
111814  ldr  r3,[pc,#0x54]     ; [0x11186c] = 0x423c   (desplazamiento dentro del .got)
111816  add  r5, pc            ; r5 = 0xf1b3b6 + 0x11181a = 0x102cbd0 = .got  (ver nota)
111818  ldr  r3,[r5,r3]        ; GOT[0x423c] -> &variable .bss en 0x10a8c50
11181a  ldr  r3,[r3]           ; el filtro registrado (en el invitado: viewUnified2+0x181fb9)
11181c  cbz  r3, 0x111826
11181e  mov  r0, r4  ·  ldr r1,[r7,#4]
111822  blx  r3                ; filtro(&lista, evento)      <-- el filtro ESCRIBE en la lista del servicio
...
111830  bl   0x11127e          ; front()
11183a  ldr  r1,[r3]  ·  11183c bl 0x127bb6   ; AbstractUtilityManager::pushEvent(elemento)
111842  bl   0x1114de          ; pop_front()
111848  bl   0x11113e          ; empty()   (1 = vacía)
11184e  beq  0x111830          ; while (!empty())
111852  bl   0x127bc4          ; notify()
```

Nota de la aritmética PIC: el inmediato del `add r5, pc` de 16 bits es `pc+4` con el bit 0 limpio, y el `.got` de
`libObj` empieza exactamente en **`0x102cbd0`** (sección `.got`, verificado con `readelf -S`), así que
`0x102cbd0 + 0x423c = 0x102d0e0c` es el *slot* que apunta a la variable `.bss` **`0x10a8c50`** (la que el shim lee
con `P 10a8c50`).

Consecuencias, en estático:

- **Quien consume la lista es `pushFilterEvent`**, no la vista. Las dos únicas funciones que leen `InputService+0xc`
  con este molde son `pushFilterEvent` y su gemela `0x1116f8`; `viewUnified2.so` no tiene ninguna referencia a esa
  lista (solo recibe su puntero como primer argumento del filtro).
- Cada elemento se entrega a `0x127bb6`, que es un *forwarder* de dos instrucciones:
  `ldr r0,[r0,#4]` + `b.w 0x7f0adc` = `EventManager::push(evento, notify = 0)` (`0x7f0ade`: `movs r2,#0`).
- Por tanto **de esa lista no puede salir una acción**: lo único que sale es el evento (o sus copias) hacia la cola
  del framework. La «lista de la vista» que suponía [g22-cola-eventos §7](g22-cola-eventos.md#7-qué-sigue-roto-no-lo-arregla-esta-sesión)
  no existe: es una lista de paso del servicio, y se vacía en la misma llamada.

## 2. Respuesta 2 — qué entra en la lista, con qué máscara, y la tabla `{evento, acción}`

### 2.1 El filtro de la vista: reescribe, no filtra (VERIFICADO leyendo instrucciones)

`viewUnified2+0x181fb8` (`(lista, evento)`), con el código del evento en `r5` (`Event::getId`, PLT `0xe6298`):

```asm
181fbe  mov  r6, r0                 ; r6 = &lista de InputService
181fc0  mov  r0, r1  ·  181fc4 blx 0xe6298   ; r5 = Event::getId(evento)
181fc8  ldr  r3,[pc,#0xac]          ; [0x182078] = 0x15050012
...
181fe8  ldr  r3,[pc,#0x94]          ; [0x182080] = 0x150100f2   <-- el código de la tecla (pulsación)
181fea  cmp  r0, r3
181fec  beq  0x182014               ; <-- la tecla TOMA esta rama
181fee  adds r3, #0x20              ; 0x15010112
181ff2  beq  0x182014
...
182014  movs r0, #0x10  ·  182016 blx 0xe6fbc  ; operator new(16) = un Event nuevo
18201a  ldr  r1,[pc,#0x74]          ; [0x182090] = 0x15070010   <-- código del evento SINTETIZADO
18201c  movs r2, #4                 ; destino  = 4
18201e  movs r3, #1                 ; clase    = 1
182022  blx  0xe5c84                ; Event::Event(0x15070010, 4, 1)
182030  bl   0x181f9e               ; push_back(&lista, nodo)
182034  ldr  r3,[pc,#0x5c]          ; [0x182094] = 0x150700c0
182036  cmp  r5, r3
182038  beq  0x18205a               ; si el evento era 0x150700c0: no sintetiza nada más
18203a  ...                         ; si no: Event(0x150701a0, 4, 1)   ([0x182098] = 0x150701a0)
18205a  bl   0x181f9e               ; push_back(&lista, nodo del evento ORIGINAL, sin condición
```

Y `0x181f9e` es `push_back` de una `std::list<Event*>`: `bl 0x181f64` (nodo nuevo) y
`b.w 0xea938` = `std::_List_node_base::_M_hook` (símbolo importado).

Resultado concreto para una pulsación de Reproducción (`0x150100f2`), **tres eventos** en la misma lista y por
tanto en la cola del framework, los tres `dest=4`, `clase=1`:

| evento encolado | de dónde sale |
|---|---|
| `0x15070010` | rama `0x182014` (0x150100f2 está en su conjunto) |
| `0x150701a0` | rama `0x18203a` (todo evento distinto de `0x150700c0`) |
| `0x150100f2` | `0x18205a`, el original, **siempre** |

Conjunto que dispara la rama `0x182014` (literales `0x182078`…`0x18208c` + los `add`/`sub` del árbol):
`0x15010011`, `0x15010012`, `0x15010032`, **`0x150100f2`**, `0x15010112`, `0x15070050`, `0x15060020`/`0x150800c2`,
`0x15060030`/`0x150800d2` y `0x15060010`/`0x150800b2`.

### 2.2 La máscara `0x7ffffffe` NO se aplica en este camino

La máscara vive en las listas `_InfraInputKeyList` (12 B por entrada, `{clave, evento, máscara}`). Para la
Reproducción, grupo `0xf`, lista `.data` **`0x4aa848`**:

```
4aa848: f7 01 00 00 | f0 00 01 15 | fe ff ff 7f     {0x1f7, 0x150100f0, 0x7ffffffe}
4aa854: 95 70 00 00 | 20 01 01 15 | fe ff ff 7f     {0x7095, 0x15010120, 0x7ffffffe}
4aa860: 22 00 00 0a | f0 00 01 15 | fe ff ff 7f     {0xa000022, 0x150100f0, 0x7ffffffe}
4aa86c: 1c 00 00 0a | 20 01 01 15 | fe ff ff 7f     {0xa00001c, 0x15010120, 0x7ffffffe}
```

Su descriptor está en `.data` **`0x4aa6c8`** = `{0x4aa848, 0x181a3d, 4, 0, 0}` (lista, callback, nº de entradas).
Los descriptores verificados son `0x4aa628` (grupo 7, `{0x4aa914, 0x1816d5, 202}`), `0x4aa63c` (grupo 8,
`{0x4aa87c, 0x1816b5, 8}`), `0x4aa650` (grupo 9, `{0x4ab37c, 0x181b39, 5}`) y `0x4aa6c8` (grupo 0xf), todos con paso
`0x14` y fila `= grupo − 7`. **Corrección menor a [g22-reproduccion-sd §8.1a](g22-reproduccion-sd.md#81-estático-nuevo-va-del-elf-leído-de-los-binarios)**:
la base `0x4aa59c` que da ese informe coincide numéricamente con `0x4aa628 − 7·0x14`, pero los bytes de
`0x4aa59c…0x4aa627` son identificadores de evento (`0x15010212`, `0x15010211`, …), no punteros de descriptor.

Quién usa la máscara: `InfraInput::GetEventStatus(int grupo, int clave, _InfraInputEvent*)`
(`libObj+0x805804`) recorre las entradas (`paso 0x44`, `[entrada+4] == clave`), copia 0x18 B a la salida y deja la
máscara en **`_InfraInputEvent+8`** (`0x8058ca: str r5,[r4,#8]`); por defecto `0x7ffffffe` (`0x80588a`). Es una API
de **consulta** (`pull`): la máscara se devuelve, no se compara contra el evento. En esta versión **nadie llama a
`GetEventStatus` desde el camino de la tecla**; sus dos únicos llamantes son `libObj+0x807df0` (dentro de
`SetEventKeyList`) y `libObj+0xaf590c` (un `getMask(this)` = `GetEventStatus(this+4, this+8, 1, &tmp) → tmp[+8]`).

### 2.3 La tabla `{evento, acción}` de `.rodata` y su único lector

`.rodata` VA **`0x3a03d4`**, 19 entradas de 8 B `{evento, acción}` (bytes de la primera:
`f0 00 01 15 | 04 00 00 00`):

| # | evento | acción | # | evento | acción |
|---|---|---|---|---|---|
| 0 | **0x150100f0** | **4** | 10 | 0x15020080 | 155 |
| 1 | 0x15040010 | 8 | 11 | 0x150200c0 | 156 |
| 2 | 0x15010020 | 1 | 12 | 0x15020030 | 157 |
| 3 | 0x150102b0 | 2 | 13 | 0x15020090 | 158 |
| 4 | 0x15010030 | 3 | 14 | 0x15030100 | 11 |
| 5 | 0x15010110 | 7 | 15 | 0x150300e0 | 9 |
| 6 | 0x15010050 | 6 | 16 | 0x150300f0 | 10 |
| 7 | 0x15090010 | 152 | 17 | 0x15050040 | 12 |
| 8 | 0x15050010 | 153 | 18 | 0x15050050 | 12 |
| 9 | 0x15070050 | 5 | | | |

**El único código de toda la biblioteca que lee esa tabla es `viewUnified2+0x1906a8`**
(`19` = `cmp r3,#0x13`; la tabla se arma con `ldr r2,[pc,#0x20]` = `0x0020fd1e` en `0x1906d0` y `add r2, pc` en
`0x1906b2`: `0x20fd1e + 0x1906b6 = 0x3a03d4`). Esa función devuelve 1 y escribe la acción en `*r1`, o 0 si no hay
entrada. **No tiene ni un `bl`/`b.w` que la llame y no hay ningún puntero a ella en el fichero**; el filtro de
§2.1 tampoco la usa. Con los vtables construidos en tiempo de ejecución (ningún vtable del fichero contiene
`0xf59f1`, que sí se ejecuta) no se puede demostrar ausencia de llamada indirecta: queda **NO VERIFICADO** si la
tabla se consulta, pero sí está verificado que **no la consulta nada del camino de la tecla**.

## 3. Respuesta 3 — la puerta es `Event[+8]` (destino), y la clase solo elige cola

### 3.1 `Event`: el destino es un byte y la clase otro byte

`Event::Event(unsigned long, unsigned char, unsigned char)` = `libObj+0x7f17f8`:

```asm
7f17f8  push {r4,r5,r7,lr}
7f17fc  strb r2,[r0,#8]     ; +8 = byte «destino»   (bytes 02 72)
7f1800  strb r3,[r0,#9]     ; +9 = byte «clase»     (bytes 43 72)
7f1802  str  r1,[r0,#4]     ; +4 = código de 32 bits (bytes 41 60)
7f1804  movs r0,#8  ·  blx operator new  ·  ParamList::ParamList   ; +0xc = ParamList*
7f1812  movs r0,#4  ·  blx operator new  ·  [x]=1 · [r4]=x         ; +0 = int* con 1
```

y `Event::getDest()` = `libObj+0x7eebf8`: `80 b5 00 af | 00 7a | 80 bd` = `ldrb r0,[r0,#8]` (un **byte**, no una
palabra). `InputService::createEvent` (`libObj+0x1106b8`) fija el destino con su propio 2.º argumento y la clase a
**1** siempre (`0x1106ca: 01 23` antes de `blx Event::Event`).

### 3.2 `AppSystem::dispatch` reparte por bits del destino

`libObj+0x7eed0c` (llamado desde el bucle `AppSystem::Main`, `0x7eefe2` y `0x7ef0ce`). Tras ajustar `[this+0x24]`
con el evento `0x11001002` y `[this+0x28]` con `0x11001004`, hace `r6 = Event::getDest()` (`0x7eed78`) y:

| prueba | bytes | consumidor | qué es |
|---|---|---|---|
| `dest & 1` | `7eee20: 16 f0 01 0f` | `0x7f4c30([this+8], e)` | notificador de ganchos |
| `dest & 2` | `7eedda: 06 f0 02 03` | `0x7ed49c([this+4], e)` | gestor de sucesos de sistema |
| `dest & 4` | `7eed94: 06 f0 04 03` | `0x7f4528(*[this], e)` | gestor de datos/parámetros |
| `dest & 8` | `7eee5a: 06 f0 08 06` | `[this+0x1c]` → **vtable[+8]** | **la vista** (`ActionEventMap`) |

```asm
7eee62  ldr  r0,[r4,#0x1c]   ; e0 69   <- el objeto que puso el constructor de AppSystem
7eee64  mov  r1, r5          ; 29 46   <- el Event*
7eee66  ldr  r3,[r0]  ·  ldr r3,[r3,#8]  ·  blx r3   ; 03 68 9b 68 98 47
```

`[AppSystem+0x1c]` se rellena en el constructor del sistema con
`[r4+0x14]->vtable[0x3c]()` (`0x7ef326 blx`) y `0x7ef332: e0 61` = `str r0,[r4,#0x1c]`: es el **objeto raíz de la
vista** (el `DefRootView`) del que cuelgan los `ActionEventMap`. El evento se libera al final
(`Event::~Event` + `operator delete`, `0x7eee84`/`0x7eee8c`).

### 3.3 Ningún producto de entrada lleva el bit 8 (VERIFICADO enumerando llamantes)

Sitios de `InputService::createEvent` en `libObj` y destino que pasan (instrucción `movs r2,#imm` inmediatamente
anterior al `blx` del PLT `0xdf280`):

| destino | nº | sitios (VA) |
|---|---|---|
| `0` | 3 | `0x110804`, `0x11085c`, `0x1108c8` |
| `1` | 1 | `0x110b68` (`callback_tp`) |
| `4` | 14 | `0x111788`, `0x1118a0`, **`0x11197c`**, `0x111cc8`, `0x111f40`, `0x11209c`, `0x112244`, `0x112468`, `0x1128ec`, `0x1129ac`, `0x112a7c`, `0x112b40`, `0x112c10`, `0x11307c` |
| sin `movs` en la ventana | 3 | `0x112e00`, `0x113178`, `0x1132d8` (el destino les llega de otro registro) |

**Ninguno pasa 8.** Los tres únicos `Event::Event(..., dest=8, ...)` de `libObj` construyen ids que no son de
entrada (`0x17000002` en `0x1028c0`, `0x16060011` en `0x415b20`, `0x1606000d/0x1606000e` en `0x445ff4`), y el
«difusor» `0xf` (`0xff354`, `0x100034`, `0x100410`) es para eventos `0x1101xxxx`/de consola. En
`viewUnified2.so` solo hay dos constructores de eventos y ambos son `dest=4` (`0x182048`, `0x19947c`).

Y la publicación de la tecla, en la función que la construye (`libObj+0x1118xx`):

```asm
111970  ldr  r3,[pc,#0x114]   ; [0x111a88] = 0x3178 (desplazamiento del singleton en el .got)
111972  movs r2, #4           ; bytes 04 22   <-- DESTINO 4 de todos los eventos de tecla
111974  ldr.w sl,[r4,r3]  ·  ldr r0,[sl]
11197c  blx  0xdf280          ; InputService::createEvent(código, 4)
111986..1119da                ; addParameter(0x1b), (0x1c), (0x20)
1119ea  b.w  0xdce8c          ; InputService::pushFilterEvent(evento)   (bytes cb f7 4f ba)
```

Es decir: **la tecla se publica con `dest = 4` y así se queda**; el filtro de la vista (§2.1) fabrica sus dos copias
también con `dest = 4` (`0x18201c: 04 22`, `0x182042: 04 22`). Por eso la medición ve `dest=4` en `EQTRACE` y por eso
`DispatchEvent` no recibe ni un `0x1501xxxx`.

### 3.4 La clase (`Event[+9]`) no es «la clase de evento de la vista»: es el selector de cola

`EventManager::push(Event*, bool)` = `libObj+0x7ef960`:

```asm
7ef960  push…  ·  r4=this · r5=evento · r6=notify
7ef970  bl   0x7ef88c        ; clase = ldrb [evento+9]    (0x7ef890: 40 7a)
7ef974  cmp  r0, #1          ; bytes 01 28
7ef978  bne  0x7ef9d2        ; clase != 1 -> ver más abajo
        ; ---- clase 1 -> cola 1 ----
7ef97c  bl   0x7ef8f4        ; lock
7ef980  ldr  r2,[r4]  ·  ldr r3,[r4,#8]  ·  ldr r0,[r2,#4]  ·  blx r3   ; gancho([this+8])(cola1, e)
7ef98e  ldr  r0,[r3,#4]  ·  7ef990 bl 0x7f0aac                      ; cola1.push(e)
7ef994  ldr  r0,[r3,#4]  ·  7ef998 bl 0x7f0aa0                      ; cola1.size()
7ef99c  movs r1,#0x64  ·  7ef9a2 bl __aeabi_uidivmod                ; size % 100
7ef9a8  cbnz r1, 0x7ef9c4                                            ; resto != 0 -> sin aviso
7ef9b8  testmode_debugPrint("[FMWK] EventQueue pile. count: %d")     ; cadena 0xd88103
7ef9c4  bl   0x7ef902        ; unlock
7ef9ca  cbz  r6, 0x7ef9ea    ; si notify: [this+4]()  (0x7ef9cc-0x7ef9ce)
        ; ---- clase 0 -> cola 0 ----
7ef9d2  cbnz r0, 0x7ef9ea    ; cualquier otra clase: NO se encola
7ef9d6  bl   0x7ef8f4        ; lock
7ef9da  ldr  r3,[r4]  ·  7ef9de ldr r0,[r3]  ·  7ef9e0 bl 0x7f0aac    ; cola0.push(e)
7ef9e6  bl   0x7ef902        ; unlock
```

Las dos colas son `new char[8]` en el constructor (`0x7ef894`): `[this][0]` = cola 0, `[this][4]` = cola 1 (cada una
un `new(8)` en `0x7ef8b6`/`0x7ef8ce`), `count(i)` = `ldr.w r0,[r3, r5, lsl #2]` (`0x7efa0a`), el trasvase
`0x7ef910` mueve **un** elemento y `AppSystem::Main` (hilo `Appframework`) solo extrae de la **cola 0**
(`0x7eefda pop`, `0x7eefe2 dispatch`, y el trasvase en `0x7ef03a` tras `cbz r5` en `0x7ef036`).

**Respuesta**: no hay ninguna «clase de evento» que la vista tenga que registrar. La clase es 0 o 1 y sólo decide
*cuándo* se despacha (0 = cola inmediata, 1 = cola diferida, otra = descartado). El reparto a la vista es el
`destino` (§3.2). Lo que sí tiene la vista es una **tabla de disparo** por vista
(`View::getTriggerTable` = `[View+0x20]`, `libObj+0x7f1a98`) y un traductor de ids de evento:
`ViewBase::transformByTriggerTableForFuncEvent` (`libObj+0x120934`) devuelve **5** si la tabla es nula, y
`ViewBase::GetEventId` (`libObj+0x121d58`) pasa el id por un mapa (`libObj+0xf2fe0`, `this+0x28` → `+0x1c`).
Determinar si la vista de disparo tiene entrada para `0x150100f2` en ese mapa es el paso 2 de §7 (§8.3: NO VERIFICADO).

## 4. Respuesta 3b — la vista sí acepta ids `0x1501xxxx` cuando le llegan

`viewUnified2+0x17df8c` (método sin exportar; lo llaman los tres despachadores `0x17df8c`/`0x17e048`/`0x17e080`):

```asm
17df8c  mov r5,r0  ·  17df92 blx 0xe74a8   ; r4 = ViewBase::GetEventId()  (id del evento en curso)
17dfb0  lsrs r3,r4,#0x14  ·  lsls r3,r3,#0x14   ; r3 = id & 0xFFFFF000   (bytes 23 0d 1b 05)
17dfb4  cmp.w r3, #0x15000000                   ; b3 f1 a8 5f
17dfb8  bne 0x17dfd4                            ; no es 0x15xxxxx -> despacha tal cual
17dfba  0x150700c0  ·  17dfc0 0x15010011  ·  17dfc6 0x15090002   ; excepciones: se despachan tal cual
17dfcc  cmp r4,#0x41  ·  ite eq  ·  moveq r4,#0x41  ·  movne r4,#2   ; el resto de 0x15xxxxx -> id = 2
17dfd4  ldr.w r0,[r5,#0x124]   ; r0 = el ActionEventMap de esta vista
17dfde  b.w   0xe9890          ; ActionEventMapBase::DispatchEvent(r0, id)  (libObj+0xf59f0, bytes 6b f7 57 bc)
```

Dos consecuencias:

1. **el lado de la vista está preparado**: un `0x1501xxxx` (salvo tres excepciones) se convierte en el id **2** y se
   entrega al mapa de acciones de `[View+0x124]`. Los ids pequeños que la medición ve en `DispatchEvent`
   (`2, 8, 0x23, 0x2a, 0x42…0x54`) son exactamente eso: ids **traducidos** (`2` = «evento 0x15xxxxx genérico»;
   `8`, `0x23`… vienen de la tabla de disparo o del mapa de `GetEventId`), no eventos del framework;
2. con `dest=4` el evento **nunca llega a este código**, así que da igual qué haría después: el corte está antes.

## 5. Respuesta 4 — no hay «modo VIEW» de `InputService` en el camino de la tecla

- `InputService::getInputEventStatus(ParamList*, ParamList const*)` = `libObj+0x114104` es un **mandato de consola**
  basado en `ParamList`: lee `0x17005003`/`0x17005008`, construye `ParamList`/`ParamInt` (`0xf0fb0`), compara el
  estado con 0…6 y añade el resultado a la salida (`0x1700500c`). **No tiene ni un llamante** en todo `libObj`
  (ni por PLT ni por `bl`), y no lo usa el camino de la tecla.
- El camino de la tecla no consulta ningún modo: la función de `libObj+0x1118xx` crea el evento
  (`createEvent(código, 4)`), le añade tres parámetros y llama a `pushFilterEvent` **sin ninguna condición previa**
  sobre el estado del servicio (las únicas ramas son `cbz` de reservas de memoria).
- Lo que sí es un dato «de modo» es el par (destino, máscara) que llega desde arriba: `dest=4` y
  `máscara=0x7ffffffe` («sin condición»). Activarlo al modo VIEW significaría **cambiar el destino a `4|8`**, no
  conmutar un modo del servicio.

## 6. Grafo estático (quién llama a quién)

```
driver IR ─► InfraInput ─► snd_InfraInputEvent_to_InputServant (0x110138)
                                   │ hilo del servicio
                                   ▼
              libObj+0x1118xx: createEvent(id, 4)  ──►  Event{id, dest=4, class=1}
                                   │                      ▲ Event::Event 0x7f17f8
                                   │ addParameter 0x1b/0x1c/0x20
                                   ▼
              InputService::pushFilterEvent (0x1117f4)
                    │ lista = &this+0xc                        (0x111800)
                    │ filtro = *[GOT→0x10a8c50]                (0x111814-0x111822)
                    ▼
              viewUnified2+0x181fb8 (filtro)  ── push_back ──► lista del servicio
                    │  sintetiza 0x15070010 (0x182014) y 0x150701a0 (0x18203a), ambos dest=4 class=1
                    │  y reengancha el original (0x18205a)
                    ▼ (vuelve a pushFilterEvent)
              vaciado: front/pop (0x11127e/0x1114de) ─► 0x127bb6 = AbstractUtilityManager::pushEvent
                                                          │ ldr r0,[r0,#4]
                                                          ▼
                                            0x7f0adc ─► EventManager::push(e, notify=0)
                                                          │ (PLT 0xdf270; clase 1 → cola 1)
                                                          ▼
              EventManager (singleton)   cola0 = [em][0]   cola1 = [em][4]
                    ▲ trasvase 1→0 (0x7ef910, un evento)
                    │
              AppSystem::Main (0x7eeee8, hilo «Appframework»)
                    │ pop cola0 (0x7ef940) ─► AppSystem::dispatch (0x7eed0c)
                    ▼
              reparto por Event[+8] (getDest 0x7eebf8)
                 ├ 1 → 0x7f4c30     ├ 2 → 0x7ed49c
                 ├ 4 → 0x7f4528  ◄── AQUÍ ENTRA LA TECLA (no conoce 0x1501xxxx/0x1507xxxx)
                 └ 8 → (*[AppSystem+0x1c])->vtable[+8]  ──►  ActionEventMapBase::DispatchEvent (0xf59f0)
                                                                │ thunk virtual (vtable[+8] del objeto)
                                                                ▼
                                    viewUnified2+0x17df8c: id = ViewBase::GetEventId()
                                         (0x15xxxxx salvo 3 excepciones → id = 2)
                                                                │
                                                                ▼
                                    [View+0x124]->DispatchEvent(id) → acción → execAction
                                                                │
                                    tabla .rodata 0x3a03d4 {0x150100f0, 4} — único lector 0x1906a8
                                                                  (sin llamantes estáticos: NO VERIFICADO)
```

## 7. Veredicto

**La acción 4 no llega porque el evento de la tecla se publica con `Event[+8] = 4` (destino «datos/parámetros») y la
vista de disparo solo se alcanza con `dest & 8`.** No es la cola (G22-COLA la dejó a tiempo), no es la clase
(`1` sólo significa «cola diferida»), no es la máscara (`0x7ffffffe` = sin condición, y además no se compara), y no
es la lista del filtro (esa lista es del servicio y la vacía él mismo en la misma llamada). El eslabón que falta es
**el reparto por destino dentro de `AppSystem::dispatch`**: `0x7eed94` manda la tecla a `0x7f4528` y `0x7eee5a` —la
puerta de la vista— no se ejecuta nunca para un `0x1501xxxx`.

Que el `4` sea el valor «correcto de fábrica» o un valor que en la cámara real acaba en `4|8` es la pregunta que
abre el paso siguiente; estáticamente **ningún producto de entrada del firmware construye jamás un evento con el bit
8**, así que, si la cámara enciende la vista con una tecla, o cambia el destino después de `createEvent`, o la
vista no se entera por esta vía.


### 7.1 Medido con `DESTKEY=1` (26-11-2026): el destino `4|8` no basta

Se implementó el parche en el shim (`DESTKEY=1`, `libObj+0x111972` `04 22` → `0c 22`, comprobando los bytes antes de
escribir; registro `DESTKEY: libObj+0x111972 movs r2,#4 -> #0xc`). Arranque en frío con `DESTKEY=1` (perfil `dest1`,
puerto 8665, 284 s hasta la primera pantalla, 79 fotogramas, OSD pintada) y **una pulsación de Reproducción no cambia la
pantalla**: píxeles opacos 0,10 antes y 0,10 después, y el fotograma sigue siendo la OSD de disparo (misma imagen). Es
decir: sumar el bit 8 al destino **no abre la vista de reproducción**.

Consecuencia: o el evento sigue sin llegar a `DispatchEvent`, o llega y la vista lo descarta en el mapa `[View+0x28]+0x1c`
o en la tabla `{evento, acción}` (`viewUnified2+0x1906a8`, sin llamantes estáticos). La medida que lo separa es la del §7
(`TRACEFN=f59f0,11817e` + una pulsación); el intento de hacerla con `DESTKEY=1 TRACEFN=…` se quedó en el cuelgue de
arranque de G22-CUELGUE («2 listas», 478 s, 2 fotogramas), así que **queda pendiente**.

### 7.2 Medido con `EQTRACE` (26-11-2026): el destino sale `4`, no `0xc`

Con el estado guardado de `dest1` (que ya arrancó con `DESTKEY=1`, registro `DESTKEY: libObj+0x111972 movs r2,#4 -> #0xc`),
`E EQTRACE=1` y una pulsación de Reproducción:

```
EQTRACE 1 code=15070010 dest=4 clase=1 notify=0 lr=libObj.so+0x111841
EQTRACE 2 code=150701a0 dest=4 clase=1 notify=0 lr=libObj.so+0x111841
EQTRACE 3 code=150100f2 dest=4 clase=1 notify=0 lr=libObj.so+0x111841   <- la tecla
EQTRACE 5 code=150100f1 dest=4 clase=1 notify=0 lr=libObj.so+0x111841   <- la suelta
```

Los tres eventos del camino salen con **destino 4** aunque el parche de `0x111972` está aplicado: **ese `movs` no es el que fija
el destino de esta ruta** (el `push` llega desde `libObj+0x111841`, no desde `0x11197c`), así que la hipótesis del §7 hay que
moverla: el destino de la tecla lo pone el llamante de `InputService::createEvent` que termina en ese `push`, y los dos eventos
sintéticos los fija el filtro de la vista (`viewUnified2+0x18201c`/`+0x182042`, los dos `dest=4` del listado). Siguiente medida
concreta: parchear esos dos literales a `0x0c` y repetir `EQTRACE` (debe salir `dest=c`) **y** `TRACEFN=f59f0,11817e` con la
pulsación en la misma pasada; sin `dest=c` en `EQTRACE`, no tiene sentido mirar la vista.

### 7.3 Medido con `DESTKEYV` (27-11-2026, sesión G22-TECLA): el destino sale `c` y lo fija `libObj+0x113076`

Se añadió al shim un interruptor **`DESTKEYV=1`** (apagado por omisión) que cambia **tres** `movs r2,#4` de 2 bytes
(`04 22` → `0c 22`, comprobando los bytes antes de escribir, idempotente y llamado en los dos ganchos `dlopen` porque
`viewUnified2.so` entra **después** de `libObj.so`):

| sitio | bytes | qué fija |
|---|---|---|
| `libObj+0x113076` | `04 22` | el destino de la **pulsación/suelta de la tecla** (`createEvent` en `0x11307c`) |
| `viewUnified2+0x18201c` | `04 22` | `Event(0x15070010,4,1)` del filtro de la vista |
| `viewUnified2+0x182042` | `04 22` | `Event(0x150701a0,4,1)` del filtro de la vista |

**Cómo se localizó el sitio de la tecla (esto es lo que corrige la hipótesis del §7).** Con `TRACEFN=1106b8`
(`InputService::createEvent`) armado **en caliente** (`E TRACEFN=…`, exige `TRACEFN=0` en el arranque para que el shim
fije la base de `libObj`) y una pulsación de Reproducción, el llamante sale en la propia traza:

```
WAITLOG 318.14 tecla 0x1f7
TRACE 1106b8 n=1 r0=80f54118 r1=150100f2 r2=c r3=3178 lr=ae0a2081 (libObj.so+0x113080)   <- el `blx` de 0x11307c
EQTRACE 1 code=15070010 dest=12 clase=1 notify=0 lr=libObj.so+0x111841
EQTRACE 2 code=150701a0 dest=12 clase=1 notify=0 lr=libObj.so+0x111841
EQTRACE 3 code=150100f2 dest=12 clase=1 notify=0 lr=libObj.so+0x111841
```

- `r2=c` en `createEvent` **y** `dest=12` en los tres `EQTRACE`: el interruptor hace lo que dice. El antes está en §7.2
  (`dest=4` en los tres, con `DESTKEY=1` aplicado).
- `lr=libObj+0x113080` = retorno del `blx` de **`0x11307c`**, así que el `movs r2,#4` que hay que tocar es el de
  **`0x113076`** (`04 22`), no el de `0x111972` (DESTKEY): la función de `0x11191c` que contiene ese último **no tiene ni
  una referencia en el fichero** (0 ramas a `0x11191c` y 0 palabras `0x11191c`/`0x11191d` en `.text`, `.rodata`,
  `.data`, `.data.rel.ro` ni `.got`; test `test_la_gemela_111972_no_tiene_ni_una_referencia`), o sea que `DESTKEY`
  parcheaba código muerto. La función **viva** (`0x1130xx`) es su gemela: calcula el código desde la base
  (`0x150100f0`) con `+2` (pulsación → `0x150100f2`, `0x11304c`), `+1` (suelta → `0x150100f1`, `0x113054`) o `+4`
  (`0x113050`), llama a `createEvent` y luego a `pushFilterEvent`.
- Los dos eventos sintéticos ya salían del filtro con `dest=12`, lo que confirma el §2.1 (el filtro **no** reescribe el
  destino del original: no hay ningún `strb rX,[rY,#8]` entre `0x181fb8` y `0x182068`;
  test `test_el_filtro_fija_el_destino_de_sus_dos_copias_y_no_toca_el_original`).

**Qué pasa después (medido en el invitado, `TRACEFN=7eed0c,7ef910,7f4528,7eee68,f59f0,11817e`).** Los tres eventos se
despachan; el consumidor del bit 4 los recibe y el reparto por destino **sí llega a la rama del bit 8**:

```
TRACE 7ef910 n=1 r0=518f20 r1=0 r2=518f2c r3=0 lr=ae77e03f (libObj.so+0x7ef03e)     <- trasvase cola 1 -> cola 0
TRACE 7eed0c n=1 r0=aacfed10 r1=54c408 r2=518f2c r3=1 lr=ae77dfe7 (libObj.so+0x7eefe6)  <- AppSystem::dispatch
TRACE 7f4528 n=1 r0=525658 r1=54c408 r2=518f2c r3=0 lr=ae77ddaf (libObj.so+0x7eedae)    <- consumidor del bit 4
TRACE 7eee68 n=8 r0=807abce8 r1=1249870 r2=10 r3=aef46630 lr=ae75088b (libObj.so+0x7f488a)   <- rama dest&8
  DEREF 0xaef46630+0: ae06ab49 ae06ab75 ae06a8ed 00000000 b6e08e50 aeb2814a aef45af8 b6e08e50 aeb2815b
  DEREF 0x121ac08+0: 0121ac50 15070010 0000010c 0121ac20 …   <- Event: +0 int*, +4 CÓDIGO, +8 dest|clase
  DEREF 0x1249870+0: 012498b8 150701a0 0000010c 01249888 …
  DEREF 0x11cbd10+0: 011cca48 150100f2 0000010c 0119cf08 …
```

Es decir: **la vista sí recibe el evento** — la palabra `+8` de los tres es `0x0000010c` (`dest=0x0c`, `clase=0x01`) y la
rama `dest & 8` de `AppSystem::dispatch` se ejecuta con el `Event*` en `r1`. `TRACE 11817e`
(`ActionCheckerListBase::execAction`) sigue a **0 disparos** en las tres pasadas.

**Corrección al §3.2 (bytes, verificados otra vez).** El reparto de `0x7eed0c` no es una cadena 1/2/4/8: los cuatro
tests del **destino** están intercalados con impresiones de depuración que dependen de **otro** byte,
`[AppSystem+0x24]` (bits 8/0x10/0x20/0x40 → `0x7eeb74`), y van en este orden: `and r3,r6,#4` (`0x7eed94` →
`0x7f4528`), `and r3,r6,#2` (`0x7eedda` → `0x7ed49c`), `tst r6,#1` (`0x7eee20` → `0x7f4c30`) y `and r6,r6,#8`
(`0x7eee5a` → `(*[AppSystem+0x1c])->vtable[+8]`), con `r6 = Event::getDest()` (`0x7eed78`).

**La ranura `vtable[+8]` NO es `libObj+0xf59f0`.** Con `libObj` en `0xadf5c000` (lo dice la propia traza:
`ae75088a & ~1 - 0x7f488a`), la tabla del objeto `[AppSystem+0x1c]` es `0xaef46630` y su **palabra de byte +8** (la
tercera, `ldr r3,[r0]` + `ldr r3,[r3,#8]` en `0x7eee66`) es **`0xae06a8ed` = `libObj+0x10e8ed`**, no
`libObj+0xf59f0`. `0xf59f0` es un *thunk* de 12 B (`ldr r3,[r0]` · `ldr r3,[r3,#8]` · `blx r3`, bytes en `0xf59f0`), y
en el invitado **solo** se le ve llamar desde `viewUnified2+0x198450` con ids **numéricos**
(`r1=2`, `r1=8`, `r1=0x2a`), nunca desde `AppSystem::dispatch` ni con un `Event*`.

### 7.4 El eslabón que falta: el reparto multicast `libObj+0x10e8ec` y el mapa `{evento → acción}` de la vista

`libObj+0x10e8ec` (destino real de la ranura) es un **reparto a todos los oyentes**: recorre una `std::list` en
`this+0x14` y para cada elemento hace `(*oyente)->vtable[8](oyente, evento)`:

```asm
10e8ec  push {r4,r5,r7,lr} · r5 = r0 + 0x14 · r4 = r1          ; r4 = el Event*
10e8fa  bl 0x10e8e2 · str r0,[r7,#4] · bl 0x10e8be · str r0,[r7]   ; begin()/end() de la lista
10e90a  adds r0,r7,#4 · bl 0x10e844                            ; iterador -> valor
10e910  mov r1,r4 · ldr r0,[r0,#4]                             ; r0 = el oyente, r1 = el Event*
10e914  ldr r3,[r0] · ldr r3,[r3,#8] · blx r3                  ; (*oyente)->vtable[8](oyente, evento)
```

Con esto el mapa del evento queda así de medido: tecla → `createEvent(dest=0xc)` → cola 1 → cola 0 →
`AppSystem::dispatch` (bit 4 al gestor de datos **y** bit 8 a la vista) → `libObj+0x10e8ec` → **cada oyente** decide →
`execAction` **nunca** se llama. El eslabón que falta está, por tanto, dentro de los oyentes: el `ActionEventMap` de la
vista no traduce `0x150100f0`/`0x150100f2` a la acción `4` (o la acción no está en su lista de *checkers*).

Lo que se sabe de ese tramo, con su etiqueta:

- **VERIFICADO (bytes)**: el traductor de ids de la vista es `ViewBase::GetEventId` (`libObj+0x121d58`):
  `r0 = [this+0x14]` → `Event::getId()` (`0xdbafc`), y ese id se busca en el **mapa de `this+0x28`** con
  `libObj+0xf2fe0` (`find(this+0x1c, clave)` → `[entrada+4]`); luego compara la clase con
  `(View::getView()<<12)+0x13000000` y, si coincide, devuelve la **diferencia** (`0x121d76`: `bic r3,r5,#0xfe0` ·
  `0x121d7a`: `bic r3,r3,#0x1f` · `0x121d84`: `cmp r3,r0` · `0x121d88`: `rsbeq r5,r3,r5`). Es el único lector de ese
  mapa (los dos sitios que llaman a `0xf2fe0` son `0x121d6a`, dentro de esta función, y `0x131fe4`).
- **VERIFICADO (bytes)**: la tabla `{evento, acción}` (`.rodata 0x3a03d4`, 19 entradas, `{0x150100f0,4}`) tiene un solo
  lector, `viewUnified2+0x1906a8`, y ese lector **no es alcanzable**: 0 ramas a `0x1906a8` y 0 palabras `0x1906a9` en
  `viewUnified2.so` ni en `libObj.so`. No es de ahí de donde sale la acción 4 de este binario.
- **NO_VERIFICADO**: quién es el oyente que debería traducir, y con qué tabla. Candidatos a medir: (a) la lista de
  `[AppSystem+0x1c]+0x14` (cuántos oyentes tiene y qué vtable tiene cada uno: `P`/`DEREF` sobre esa lista, o una
  trampa en `0x10e914`); (b) si el mapa de `View+0x28` tiene entrada para `0x150100f0`/`0x150100f2` (leerlo con
  `TRACEDEREF` en la entrada de `0x121d58`, donde `r0` es la vista); (c) la tabla de disparo `[View+0x20]`
  (`View::getTriggerTable`, `libObj+0x7f1a98`).
- **NO_VERIFICADO (de dónde salen los dos objetos)**: `AppSystem+0x1c` lo pone `[this+0x14]->vtable[0x3c]()`
  (`0x7ef326`/`0x7ef332`); la tabla medida del objeto (`0xaef46630`) cae en `.data.rel.ro` de una biblioteca de la
  familia `viewUnified*` (**INFERENCIA**: coincide con `viewUnified2.so+0x446630`, dentro de
  `.data.rel.ro 0x4448d8…0x49b124`), lo que explicaría que la raíz de la vista viva fuera de `libObj`; falta medirlo.

> **Corregido en §8 (G22-OYENTE, 26-11-2026):** el objeto `[AppSystem+0x1c]` **no** es un `ActionEventMapBase` de la
> vista sino un `UtilityManager`, y sus 8 oyentes medidos no incluyen ninguna vista. Lo que falla no es el reparto del
> destino sino la traducción del id en `ViewBase::GetEventId` (devuelve `0x150100f2` sin traducir).

**Nota de método (para no repetir el fallo).** `TRACEDEREF=d<reg>:<off>:<n>` desreferencia **siempre**, así que solo vale
en trampas cuyo registro sea un puntero: puesta en la trampa de `1106b8` (donde `r1` es el *código* del evento) o en la
de `f59f0` (donde `r1` es un id pequeño) mata al hilo con SIGSEGV y deja el invitado sin ese hilo (pasó dos veces en esta
sesión: `pila (sig 11 tid … I-InputEvent)` y `pila (sig 11 tid … Appframework)`, con `addr=150100f2` y `addr=2`). Los
datos de esta sección son de las pasadas limpias; el `p1`/`p2` de los `EQTRACE` empieza en 1 en cada arranque.

**Arranques.** Dos arranques en frío con `SHIMEXTRA='DESTKEYV=1 TRACEFN=0 WAITLOG=3000'` (`/home/nicolas/hv/harness`,
perfiles `tecla2` y `tecla3`, puertos 8692/8693) se quedaron en el cuelgue conocido (G22-CUELGUE: 2 fotogramas, 2 listas,
0,0046 de píxeles opacos) y **aun así sirven para medir el camino de la tecla** (§7.3), porque el bucle `AppSystem::Main`
sigue vaciando la cola; para ver la pantalla hay que repetir el arranque. `destkeyv()` deja
`DESTKEYV: libObj+0x113076 04 22 -> 0c 22` en el registro (necesita `WLALL=1` para llegar a `shim.log`).

## 8. Medido en G22-OYENTE (26-11-2026): quién recibe el bit 8 y por qué la acción 4 no se ejecuta

Interruptor nuevo del shim **`OYD=1`** (apagado por omisión): pone un `UDF` en `libObj+0x10e914` (`68 03` = `ldr r3,[r0]`,
la primera de las tres instrucciones de la llamada virtual del reparto) y la **emula** en el manejador
(`c->arm_r3 = vt; c->arm_pc = pc + 2`), de modo que la trampa es repetible sin parchear la instrucción siguiente (lo que
sí hace `TRACEREP`). Por cada vuelta imprime clave del mapa, oyente, su vtable, la ranura `+8` y el **nombre RTTI**, cada
dirección como «biblioteca+desplazamiento» (`dladdr`), más el tamaño del mapa (`this+0x28`) y el `Event` que llega
(`+4` código, `+8` destino, `+9` clase). Evidencia: `reports/evidence/g22-oyente-20261126/`.

### 8.1 `[AppSystem+0x1c]` es un `UtilityManager`, **no** el `ActionEventMap` de la vista

La vtable que el invitado midió en `libObj+0xfea630` (§7.3) tiene `offset-to-top` 0 y su palabra `-4` apunta a un
`typeinfo` cuyo nombre es **`14UtilityManager`**; sus tres únicas ranuras son `0x10eb49`, `0x10eb75` y `0x10e8ed` (el
reparto). `0x10e8ed` aparece **una sola vez** en todo el fichero, así que la identificación no es ambigua.
`UtilityManager::regist(int, UtilityBase*)` (`libObj+0x10ee08`) es el alta de oyentes y el constructor (`+0x10eb48`) deja
el contenedor en `this+0x14`.

Corrige el §7.4: la ranura del bit 8 **no** es el `DispatchEvent` de la vista (`0xf59f0` es el thunk
`this->[this]->vtable[8]` de `DefRootView::ActionEventMapBase`, otra clase). El reparto del destino 8 es el **registro de
utilidades del framework** (`LookManager`, `SvcCaution`, `InputService`, `Database::HndlMgr`…), no la vista de disparo.

### 8.2 Los ocho oyentes, medidos

`oyentes=8` en todas las pasadas (la cuenta sale del propio mapa, `this+0x28`), y el orden es el del `std::map<int,
UtilityBase*>` (in-orden por clave):

| # | clave | RTTI del oyente | vtable | ranura `+8` (lo que ejecuta) |
|---|---|---|---|---|
| 1 | `0x1d` | `LookManager` | `libObj+0xfed4e8` | `libObj+0x137684` |
| 2 | (puntero) | `SvcCaution` | `libObj+0xfebcd8` | `libObj+0x123954` |
| 3 | `0x1d` | `TestcmdManager` | `libObj+0xfe9600` | `libObj+0xfebd8` |
| 4 | `0x35` | `HighlightManagerCustom` | **`viewUnified2+0x452870`** | `libObj+0x104650` |
| 5 | `0x25` | `InputService` | `libObj+0xfea788` | `libObj+0x1106e0` |
| 6 | `0x25` | `CameraProfileService` | `libObj+0xfea7b0` | `libObj+0x1142ea` |
| 7 | `0xbd` | `TopologyManager` | `libObj+0xcc32b8` | `libObj+0x41a934` |
| 8 | (puntero) | `Database::HndlMgr` | `libObj+0xccb9ac` | `libObj+0x439520` |

**Ninguno es una vista.** El único cuya vtable vive en `viewUnified2.so` es `HighlightManagerCustom`, que es el gestor
del resalte de foco, no la vista. `ScalarView::EventHandler` (`libObj+0x116bd0`) y
`ActionCheckerListBase::execAction` (`libObj+0x11817e`) siguen a **0 disparos** con las trampas armadas durante >380 s
(`oyente6`): la vista no entra por aquí.

### 8.3 La tecla **sí** llega al reparto, y los ocho la reciben y la ignoran

Tres medidas encadenadas en el mismo invitado (`oyente8`, `DESTKEYV=1 OYD=1`):

1. **Se publica con el bit 8**: `EQTRACE 2 code=15070010 dest=12 clase=1 notify=0 lr=libObj.so+0x111841`,
   `EQTRACE 4 code=150100f2 dest=12 …`, `EQTRACE 6 code=150100f1 dest=12 …` (`oyente6`).
2. **Entra en la rama `dest & 8`**: con `TRACEFN=7eee68` + `TRACEDEREF=d1:4:3` (aquí `r1` **sí** es el `Event*`), cada
   despacho imprime el evento: `15070010 ffff010c …`, `150701a0 0000010c …`, `150100f1 020a010c …` (palabra `+8` =
   `0x010c`: destino `0x0c`, clase `1`).
3. **Llega a los oyentes**: `OYENTE n=256 … rtti=N8Database7HndlMgrE evento=0x20d17f8 codigo=0x15070010 dest=0xc clase=0x1
   oyentes=8` — la cuenta de llamadas al reparto pasó de 128 a 256 justo con el evento sintético de la tecla, o sea que
   los ocho oyentes recibieron la pulsación.

Ninguno de los ocho hace nada con ella: `execAction` sigue a 0 y la pantalla no cambia.

### 8.4 El eslabón que falta está en la **traducción del id**, no en el destino

`ViewBase::GetEventId` (`libObj+0x121d58`) sí recibe la tecla — 141 llamadas medidas con `TRACEFN=121d58` y
`TRACEDEREF=0:14:1` (dos niveles: `r0` = vista, `[vista+0x14]` = `Event*`), con `codigo=150100f2 dest|clase=0000010c`
entre ellas. Y lo que devuelve se ve en su llamante (`viewUnified2+0x1994e8`, tras el `blx` a la ranura virtual; trampa
con `TRACELIB=viewUnified2.so` + `TRACEFN2=1994e8`, caliente):

```
TRACE 1994e8 n=3 r0=2a         r3=1306c000      <- evento 0x1306c02a: TRAducido (id 0x2a)
TRACE 1994e8 n=4 r0=150100f2   r3=15010000      <- la tecla: SIN traducir (devuelve el código tal cual)
TRACE 1994e8 n=5 r0=8          r3=1306c000      <- otro evento de la vista: id 8
TRACE 1994e8 n=6 r0=150701a0   r3=15070000      <- el sintético del filtro: SIN traducir
```

La regla del código (`0x121d76`-`0x121d8c`) es: `v = mapa[View+0x28][id]`; si `v & ~0xfff == (View::getView()<<12) +
0x13000000` devuelve `v - esa base`. Para la vista de disparo esa base es **`0x1306c000`** (vista `0x6c`), así que el
espacio de eventos **que la vista sabe accionar es `0x1306cNNN`**; los códigos de entrada `0x1501xxxx`/`0x1507xxxx` no
pertenecen a él y se devuelven **sin traducir** (`0x150100f2`), con lo que el conmutador del consumidor
(`viewUnified2+0x1994e8`: casos `0xf07`, `0xf03`, `2`, `8`, `0x2a`…) no encuentra caso y no ejecuta nada.

Conclusión causal completa: tecla `0x1f7` → `0x150100f2` (dest `0x0c`) → cola 1 → cola 0 → `AppSystem::dispatch`
(bits 4 y 8) → `UtilityManager` (8 oyentes, ninguno vista) **y** la vista (vía `viewUnified2`, que llama a
`GetEventId`) → `GetEventId` **no traduce** `0x1501xxxx` → no hay acción → `execAction` 0.

### 8.5 ¿Se puede cerrar en el arnés con un interruptor del tipo `DESTKEYV`? **No**

El interruptor que había (`DESTKEYV`) actuaba sobre el **destino**, y el destino ya no es el problema: la tecla llega a
todo lo que depende de él. Lo que falta es una entrada `{0x1501xxxx → 0x1306c004}` en el mapa de la vista o el productor
que convierta el código de entrada en un evento `0x1306cNNN` (candidatos ya localizados, sin medir: el conmutador
`getFilterEventFunc`/`getFuncEvent`/`inverseTransformFuncEvent` de `viewUnified2` en `0x1820cc`/`0x182400`/`0x182a84`, y
la tabla de disparo `[View+0x20]`, `View::getTriggerTable` = `libObj+0x7f1a98`). Cerrarlo pediría o bien una cueva de
código que llame al `insert` del mapa con la clave y el valor calculados con `View::getView()`, o bien el productor real,
que hoy no está identificado; ninguna de las dos es un parche de 2 bytes como `DESTKEYV`.

**Medida de pantalla (lo que sí se puede afirmar):** con el estado del arnés en este entorno, pulsar Reproducción **no
cambia la pantalla**: `antes.png` y `despues.png` de `reports/evidence/g22-oyente-20261126/` son byte a byte iguales
(12 861 B, 0 píxeles distintos) y `/estado` sigue en `2 fotogramas · 2 listas · opacos 0,0046`. Los cinco arranques en
frío de la sesión (`oyente1`…`oyente8`) acabaron en el cuelgue conocido **G22-CUELGUE** (mismo fotograma), así que la
comparación de pantalla se hizo sobre la OSD a medio componer: es evidencia del síntoma, no de la reproducción.

### 8.6 Cómo se instrumentó (y qué no se pudo medir)

- `OYD=1`: trampa repetible en `0x10e914` con emulación de la instrucción; imprime por oyente clave, puntero, vtable,
  ranura `+8`, RTTI y cuenta del mapa. Se arma en el gancho `dlopen` de `libObj` y también en caliente (`E OYD=1`).
- `E TRACEFN=…` en caliente **sin** `TRACEFN` en el arranque: ahora el shim busca la base de `libObj` con
  `libbase_de()` (antes exigía `TRACEFN=0` en el arranque para dejar fijada `trc_base`).
- Lo que **no** se pudo medir: el contenido del mapa `View+0x28` (habría que interpretar el `std::map` del invitado y el
  `find` es `0xf2fe0`, ajeno a la firma de `regist`); y la pantalla de disparo completa, por G22-CUELGUE.

## 9. VERIFICADO / INFERENCIA / NO VERIFICADO

| # | Afirmación | Etiqueta | Evidencia |
|---|---|---|---|
| 1 | `Event` guarda código (palabra) en `+4`, **destino (byte)** en `+8` y clase (byte) en `+9`; `getDest` es `ldrb r0,[r0,#8]` | **VERIFICADO** | `libObj+0x7f17fc` (`02 72`), `+0x7f1800` (`43 72`), `+0x7f1802` (`41 60`), `+0x7eebf8` |
| 2 | La lista que recibe el filtro es `InputService+0xc` y la vacía `pushFilterEvent`; cada elemento va a `0x127bb6` → `EventManager::push(notify=0)` | **VERIFICADO** | `0x111800`, `0x111822`, `0x111830`-`0x111852`, `0x127bb6`, `0x7f0adc`/`0x7f0ade` |
| 3 | Para `0x150100f2` el filtro sintetiza `Event(0x15070010, 4, 1)` y, como el id no es `0x150700c0`, también `Event(0x150701a0, 4, 1)`, y reengancha el original | **VERIFICADO** | `viewUnified2+0x181fe8`-`0x18205a`; literales `0x182090`/`0x182094`/`0x182098`; `_M_hook` en `0xea938` |
| 4 | La máscara `0x7ffffffe` de la entrada `{0x1f7, 0x150100f0}` no se compara en el camino: `InfraInput::GetEventStatus` la **devuelve** en `_InfraInputEvent+8` | **VERIFICADO** | lista `0x4aa848`, `libObj+0x8058ca`, `0x80588a` |
| 5 | `AppSystem::dispatch` reparte por bits del destino: 1/2/4/8; el 8 es `(*[AppSystem+0x1c])->vtable[+8]` | **VERIFICADO** | `0x7eee20`, `0x7eedda`, `0x7eed94`, `0x7eee5a`, `0x7eee62`-`0x7eee6a` |
| 6 | `[AppSystem+0x1c]` = `[this+0x14]->vtable[0x3c]()` (objeto raíz de la vista) | **VERIFICADO** | `0x7ef326` (`blx`), `0x7ef332` (`e0 61`) |
| 7 | Ningún `createEvent` de `libObj` usa destino con el bit 8 (0, 1 y 4) y la tecla se publica con `movs r2,#4` en `0x111972` | **VERIFICADO** | tabla de §3.3; bytes `04 22` en `0x111972` |
| 8 | La clase sólo elige cola (1 → cola 1 con aviso cada 100; 0 → cola 0; otra → descartado); solo la cola 0 la vacía `AppSystem::Main` | **VERIFICADO** | `0x7ef974`, `0x7ef98e`, `0x7ef9d2`, `0x7ef9de`, `0x7eefda`, `0x7ef036` |
| 9 | La vista sí admite `0x15xxxxx`: `(id & 0xFFFFF000)==0x15000000`, tres excepciones, y el resto se despacha como id `2` | **VERIFICADO** | `viewUnified2+0x17dfb0`-`0x17dfde` |
| 10 | La tabla `{evento, acción}` (`.rodata 0x3a03d4`, 19 entradas, `{0x150100f0, 4}`) tiene un único lector, `viewUnified2+0x1906a8`, sin llamantes ni punteros en el fichero | **VERIFICADO** (bytes) / **NO VERIFICADO** (que no se llame por vtable construido en ejecución) | `0x3a03d4`, `0x1906a8`, literal `0x20fd1e` en `0x1906d0` |
| 11 | `getInputEventStatus` (`0x114104`) es un mandato `ParamList` y no participa en el camino de la tecla (0 llamantes) | **VERIFICADO** | `0x114104`-`0x1141e8`, PLT de `ParamList::add` |
| 12 | El destino `4` es el valor de fábrica «correcto» y en la cámara la vista se alcanza por otra vía | **NO VERIFICADO** | — (paso 1 de §8) |
| 13 | Qué contiene el mapa `[ViewBase+0x28]+0x1c` (`0xf2fe0`) para `0x150100f0`/`0x150100f2` | **NO VERIFICADO** | — (paso 2 de §8) |
| 14 | La tabla de disparo (`View::getTriggerTable` = `[View+0x20]`) de la vista de disparo no es nula | **NO VERIFICADO** | `libObj+0x7f1a98`, `0x120934` (devuelve 5 si es nula) |
| 15 | El destino de los tres eventos de una pulsación de Reproducción lo fijan `libObj+0x113076` y los dos literales del filtro; con `DESTKEYV=1` salen `dest=12` (`0x0c`) | **VERIFICADO (medido)** | `TRACE 1106b8 n=1 … r1=150100f2 r2=c lr=libObj.so+0x113080`; `EQTRACE 1..3 … dest=12` |
| 16 | `libObj+0x111972` (DESTKEY) pertenece a código sin referencias: 0 ramas a `0x11191c` y 0 palabras `0x11191c`/`0x11191d` en todo el fichero | **VERIFICADO (bytes)** | test `test_la_gemela_111972_no_tiene_ni_una_referencia` |
| 17 | La rama `dest & 8` de `AppSystem::dispatch` **sí** se ejecuta con los tres eventos (`Event[+8]=0x0c`) | **VERIFICADO (medido)** | `TRACE 7eee68` + `DEREF 0x11cbd10: … 150100f2 0000010c` |
| 18 | La ranura `(*[AppSystem+0x1c])->vtable[byte+8]` **no** es `libObj+0xf59f0`: con `libObj` en `0xadf5c000`, la tabla `0xaef46630` tiene `0xae06a8ed` = `libObj+0x10e8ed` | **VERIFICADO (medido + aritmética)** | `DEREF 0xaef46630+0: ae06ab49 ae06ab75 ae06a8ed …`; corrige el §3.2/§7 |
| 19 | `libObj+0x10e8ec` es un reparto multicast: recorre la lista de `this+0x14` y hace `(*oyente)->vtable[8](oyente, Event*)` | **VERIFICADO (bytes)** | `0x10e8ec`-`0x10e934` (`0x10e914`: `ldr r3,[r3,#8]` · `0x10e918`: `blx r3`) |
| 20 | `execAction` (`libObj+0x11817e`) sigue sin ejecutarse con la tecla, aun con `dest=0xc` | **VERIFICADO (medido)** | 0 líneas `TRACE 11817e` en tres pasadas |
| 21 | El oyente del bit 8 era una incógnita | **CERRADO** | lo sustituyen las filas 22-29 |
| 22 | `[AppSystem+0x1c]` es un **`UtilityManager`** (vtable `libObj+0xfea630`, `offset-to-top` 0, RTTI `14UtilityManager`, ranuras `0x10eb49`/`0x10eb75`/`0x10e8ed`) | **VERIFICADO (estático + medido)** | vtable y RTTI leídos del ELF y del invitado; `0x10e8ed` aparece una sola vez en el fichero |
| 23 | El reparto recorre el `std::map<int, UtilityBase*>` de `this+0x14` (header en `+0x18`: left `+0x20`, cuenta `+0x28`; nodo `{+0x10 clave, +0x14 puntero}`; incremento importado por el veneer `0xe0b00`) | **VERIFICADO (bytes)** | `0x10e8c8`, `0x10e8a6`, `0x10e844`, `0x10e834`-`0x10e83a`, `UtilityManager::regist` `0x10ee08` |
| 24 | El registro tiene **8 oyentes** y ninguno es una vista: `LookManager`, `SvcCaution`, `TestcmdManager`, `HighlightManagerCustom`, `InputService`, `CameraProfileService`, `TopologyManager`, `Database::HndlMgr` | **VERIFICADO (medido)** | `OYENTE n=1..8 oyentes=8` con RTTI; `reports/evidence/g22-oyente-20261126/oyentes-oyente1.txt` |
| 25 | Con `DESTKEYV=1` la tecla se publica con `dest=12` (`0x0c`), clase 1 y `notify=0` | **VERIFICADO (medido)** | `EQTRACE … code=150100f2 dest=12`; `eqtrace-dest12-oyente6.txt` |
| 26 | La tecla **entra** en la rama `dest & 8` de `AppSystem::dispatch` y **llega a los 8 oyentes** (`codigo=0x15070010 dest=0xc clase=0x1`) | **VERIFICADO (medido)** | `TRACE 7eee68` + `DEREF d1:4:3`; `OYENTE n=256 … codigo=0x15070010`|
| 27 | `ViewBase::GetEventId` recibe la tecla (141 llamadas, `codigo=150100f2 dest|clase=0000010c`) y **la devuelve sin traducir** (`0x150100f2`), mientras los eventos de la vista (`0x1306cNNN`) devuelven ids pequeños (`0x2a`, `8`, `2`) con base `0x1306c000` | **VERIFICADO (medido)** | `TRACE 1994e8 r0=… r3=…`; `geteventid-devuelve-oyente8.txt` |
| 28 | La vista solo sabe accionar eventos `0x1306cNNN` (`(View::getView()<<12)+0x13000000`, vista `0x6c`); los códigos de entrada `0x1501xxxx`/`0x1507xxxx` no se traducen y el conmutador del consumidor (`viewUnified2+0x1994e8`: `0xf07`, `0xf03`, `2`, `8`, `0x2a`) no tiene caso | **VERIFICADO (medido + bytes)** | fila 27 y `viewUnified2+0x1994d8`-`0x1994fe` |
| 29 | `ScalarView::EventHandler` (`0x116bd0`) y `execAction` (`0x11817e`) siguen a **0 disparos** con la tecla llegando al reparto | **VERIFICADO (medido)** | trampas armadas >380 s en `oyente6`, 0 líneas `TRACE 116bd0`/`TRACE 11817e` |
| 30 | Cerrar el tramo con un interruptor de destino («estilo `DESTKEYV`») es imposible: el destino ya no corta nada y lo que falta es la traducción del id (entrada del mapa `View+0x28` o productor de eventos `0x1306cNNN`) | **VERIFICADO (medido)** | §8.5 |

## 10. Tests sin QEMU

`tests/test_g22_dispatch.py` (**21 casos**, 5 de ellos nuevos de G22-OYENTE) fija, contra los ELF 3.21 de
`analysis/gui/g22/harness/stage/cam/usr/lib` (no versionados: si faltan, el módulo se salta):

1. `Event` +4/+8/+9 y `getDest`;
2. `createEvent` con clase 1 fija;
3. los 21 llamantes de `createEvent` y su destino: **ninguno con el bit 8**;
4. la publicación de la tecla (`movs r2,#4` en `0x111972` + `b.w pushFilterEvent` en `0x1119ea`);
5. el filtro: entrada, literales de códigos y `_M_hook`;
6. las dos copias sintéticas (`0x15070010`, `0x150701a0`) con `dest=4, clase=1`;
7. el vaciado de la lista y `0x127bb6` → `0x7f0adc` (`notify=0`);
8. el reparto por destino en `AppSystem::dispatch` (máscaras 1/2/4/8 y el `blx` a `vtable[+8]`);
9. `[AppSystem+0x1c]` desde `vtable[0x3c]`;
10. `EventManager::push`: `cmp r0,#1`, las dos colas y el aviso cada 100;
11. la tabla `{evento, acción}` y su único lector (19 entradas, `0x13`, literal `0x20fd1e`);
12. la lista de teclas del grupo `0xf` (`0x4aa6c8` → `0x4aa848`) y la máscara `0x7ffffffe`;
13. la vista acepta `0x15xxxxx` (`0x17dfb0`) y `getInputEventStatus` no tiene llamantes.

Los cinco casos de G22-OYENTE fijan la identidad del `UtilityManager` (vtable `0xfea630`, RTTI, ranura `+8`, unicidad
de `0x10e8ed` en el fichero), los bytes del reparto (`0x10e8ec`-`0x10e91a`, con la trampa en `0x10e914`), la forma del
mapa (begin/end/valor/constructor) y la evidencia del invitado: **8 oyentes, ninguno con `View`/`ActionEventMap`/
`DefRootView` en su RTTI**. En `tests/test_gui_harness.py` se añade
`test_oyd_pone_un_udf_repetible_en_10e914_y_emula_la_carga`.

Medido en 7 s (`pytest tests/test_g22_dispatch.py -q`): 21 casos, sin QEMU. Los tres ficheros de la serie
(`test_g22_cola.py`, `test_g22_repro.py`, `test_g22_dispatch.py`) suman 35 casos en verde. Los tres casos nuevos de
G22-TECLA fijan los bytes que se parchean: los de `libObj+0x113076` (con el `blx` de `0x11307c` a `createEvent` y los
`adds r1,r6,#2/#1/#4` del código), la ausencia de referencias a `libObj+0x11191c`, y los dos literales del filtro junto
con la ausencia de `strb rX,[rY,#8]` en el filtro. En `tests/test_gui_harness.py` hay además un caso
(`test_destkeyv_parchea_los_tres_sitios_medidos_y_comprueba_los_bytes`) que comprueba que el shim escribe sólo esos tres
sitios, que compara los bytes antes (`*p != 0x2204`) y que se llama en los dos ganchos `dlopen`.

## PARA PENDIENTES.md

| ID | Estado | Resumen | Criterio de cierre |
|---|---|---|---|
| G22-OYENTE | CERRADO (26-11-2026) | **El reparto del bit 8 es un `UtilityManager` con 8 oyentes y ninguno es una vista.** VERIFICADO en bytes y medido: la vtable que el invitado midió en `libObj+0xfea630` es de `UtilityManager` (RTTI `14UtilityManager`, `offset-to-top` 0, ranuras `0x10eb49`/`0x10eb75`/`0x10e8ed`; `0x10e8ed` aparece **una sola vez** en el fichero). Su ranura `+8` recorre el `std::map<int, UtilityBase*>` de `this+0x14` (header `+0x18`, left `+0x20`, cuenta `+0x28`, nodo `{+0x10 clave, +0x14 puntero}`, incremento importado por el veneer `0xe0b00`) y llama a `(*oyente)->vtable[8](oyente, Event*)` en `0x10e914`. Interruptor nuevo `OYD=1` del shim (trampa repetible con **emulación** de `ldr r3,[r0]`, sin parchear la instrucción siguiente; imprime clave, oyente, vtable, ranura `+8`, RTTI y cuenta del mapa como «biblioteca+desplazamiento»). MEDIDO: `oyentes=8` y los ocho son `LookManager` (`+0x137684`), `SvcCaution` (`+0x123954`), `TestcmdManager` (`+0xfebd8`), `HighlightManagerCustom` (vtable `viewUnified2+0x452870`, `+0x104650`), `InputService` (`+0x1106e0`), `CameraProfileService` (`+0x1142ea`), `TopologyManager` (`+0x41a934`) y `Database::HndlMgr` (`+0x439520`). Con `DESTKEYV=1` la tecla **sí** llega: `EQTRACE code=150100f2 dest=12 clase=1`, `TRACE 7eee68` + `DEREF d1:4:3` da `15070010/150701a0/150100f1` con palabra `+8 = 0x010c`, y `OYENTE n=256 … codigo=0x15070010 dest=0xc clase=0x1 oyentes=8`. `ScalarView::EventHandler` (`0x116bd0`) y `ActionCheckerListBase::execAction` (`0x11817e`) siguen a **0 disparos** con las trampas armadas >380 s. Evidencia en `reports/evidence/g22-oyente-20261126/`. Tests: `tests/test_g22_dispatch.py` (5 casos nuevos) y `tests/test_gui_harness.py` (1). | Cumplido: los 8 oyentes identificados con RTTI y la tecla medida dentro del reparto. |
| G22-ACCION4 | ABIERTO (26-11-2026) | **El eslabón que falta es la traducción del id, no el destino del evento.** MEDIDO: `ViewBase::GetEventId` (`libObj+0x121d58`) recibe la tecla (141 llamadas, `codigo=150100f2 dest|clase=0000010c`) y **la devuelve sin traducir** (`0x150100f2`): su regla es «si `mapa[View+0x28][id]` tiene la forma `(View::getView()<<12)+0x13000000` devuelve la diferencia», y para la vista de disparo esa base es `0x1306c000` (vista `0x6c`), así que los eventos de la vista (`0x1306cNNN`) sí se traducen (`r0=0x2a`, `0x8`, `0x2`) y los de entrada (`0x1501xxxx`/`0x1507xxxx`) no. El conmutador del consumidor (`viewUnified2+0x1994e8`, casos `0xf07`/`0xf03`/`2`/`8`/`0x2a`) no tiene caso para ellos. Corrige la hipótesis del destino (`DESTKEYV` no cierra nada, §8.5). MEDIDO además: pulsar Reproducción **no cambia la pantalla** (`antes.png`/`despues.png` idénticos, 12 861 B, 0 píxeles distintos; `/estado` en `2 fotogramas · 2 listas · opacos 0,0046`); los cinco arranques en frío de la sesión acabaron en **G22-CUELGUE**, así que la captura es de la OSD a medio componer. | Identificar el productor que convierte un código de entrada `0x1501xxxx` en un evento de vista `0x1306cNNN` (candidatos: `viewUnified2+0x1820cc` `getFilterEventFunc`, `+0x182400` `getFuncEvent`, `+0x182a84` `inverseTransformFuncEvent`, y la tabla de disparo `[View+0x20]` = `View::getTriggerTable` `libObj+0x7f1a98`), o demostrar que la cámara lo hace por otra vía; cierre en el arnés: `TRACE 11817e` > 0 con `r1=4` tras una pulsación y cambio de pantalla con diff de PNG sobre una OSD completa (requiere antes cerrar G22-CUELGUE en frío) |
