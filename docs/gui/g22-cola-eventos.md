# G22-COLA — la cola de eventos del framework: quién la llena, quién la vacía y por qué se atasca

**Estado (26-11-2026, sesión G22-COLA): CAUSA MEDIDA Y ARREGLADA con un parche de 2 bytes; el corte de la tecla
se mueve al eslabón siguiente.** La cola de eventos del framework (`EventManager`, `libObj`) **no estaba llena**:
se llena *despacio* porque `InputService` encola la tecla en la **cola 1** (clase 1) con `notify = 0`, es decir
**sin despertar al hilo que la vacía** (`Appframework`), y ese hilo solo trasvasa **un** evento de la cola 1 a la
cola 0 por vuelta. Con dos eventos por pulsación (bajada y suelta) el retardo crece sin tope y el invitado acaba
avisando `[FMWK] EventQueue pile. count: %d` cada 100 eventos acumulados —aviso que **no** significa «cola
llena», como se había inferido en [g22-reproduccion-sd §8.3](g22-reproduccion-sd.md#83-dónde-se-corta-ahora-verificado)—.
Arreglo (`EVQNOTIFY`, por omisión): `libObj+0x7f0ade` pasa de `movs r2,#0` a `movs r2,#1`, así la publicación de
entrada **avisa** al consumidor en vez de dejarlo dormido hasta su plazo. **Medido después** (39 eventos de
entrada, perfil `cola4`): los 39 llevan `notify=1`, los trasvases cola 1 → cola 0 se doblan en la misma ventana
(≥32 → ≥64) y **no aparece ni un aviso `[FMWK] EventQueue pile`** (la cola 1 no llega a 100). Lo que **sigue**
sin funcionar es lo de siempre: `DispatchEvent` no recibe `0x1501xxxx` y `execAction` no se ejecuta nunca
(medido otra vez antes y después, §5); el corte está ahora en el filtro de la vista, no en la cola.

Sesión: **26-11-2026** (reloj del anfitrión 05:20–06:10, −03), **sin cámara física** (todo `qemu-system-arm`,
perfiles `cola1`…`cola4`, puertos 8684–8687, un solo `qemu` propio a la vez). Espacio de direcciones: **VA del
ELF** de `libObj.so`/`viewUnified2.so` 3.21 (el primer `PT_LOAD` tiene vaddr 0; el segundo lleva +0x8000, por eso
se usa `v2o`); `TRACEFN` del shim usa el desplazamiento respecto a la base de la biblioteca.

---

## 1. La cola, en estático (VERIFICADO leyendo instrucciones)

`EventManager` es un objeto pequeño de `libObj` (singleton; en el invitado `r0 = 0x8084e480`):

| VA | Qué es |
|---|---|
| `+0x7ef894` | init: mutex en `+0xc`, **aviso** (fn) en `+4`, gancho en `+8`, `malloc(8)` = **dos colas** (`[this]` = `{cola0, cola1}`) |
| `+0x7ef960` | **`EventManager::push(Event*, bool notify)`** (`dynsym`) |
| `+0x7ef88c` | clase del evento = `Event[+9]` (`ldrb r0,[r0,#9]`) |
| `+0x7ef910` | **trasvase**: `cola1 → cola0` (saca de una con `poll` y mete en la otra) |
| `+0x7ef940` | **pop de la cola 0** (el que usa el consumidor) |
| `+0x7ef9fc` | `count(indice)` |
| `+0x7ef8f4` / `+0x7ef902` | lock / unlock (`pthread_mutex` en `+0xc`) |

`Event` (`Event::Event(código, destino, clase)` = `+0x7f17f8`) guarda **código en `+4`**, **destino en `+8`** y
**clase en `+9`**. `push` ramifica por la clase:

- **clase 1** → `cola[1]` y, si el 2.º argumento es 1, llama al aviso (`+0x7ef8ea` → `[this+4]()`);
- **clase 0** → `cola[0]`, **sin aviso**;
- cualquier otra → no encola.

Y tras encolar en la cola 1 calcula `count(cola1)` y, **si el resto de dividir por 100 es 0**, imprime
`[FMWK] EventQueue pile. count: %d` (cadena VA `0xd88103`, alcanzada con `ldr`+`add pc` desde `+0x7ef9aa`;
el `%100` es `__aeabi_uidivmod` en `+0xbc8574`). **Es un diagnóstico periódico de profundidad, no un aviso de
cola llena.**

**Quién la vacía** es `AppSystem::Main` (`libObj+0x7eeee8`), el hilo **`Appframework`**
([g22-arnes-ui-qemu §5.8](g22-arnes-ui-qemu.md) ya lo identificó; aquí se cierra el circuito de la cola):

```
r5 = min([AppSystem+0x28], EventManager::count(1))      ; 0x7eef4e ldr r5,[r4,#0x28]
...
while (count(0) != 0) { e = pop(cola0); AppSystem::dispatch(e); }     ; 0x7eefda / 0x7eefe2
if (r5 == 0) goto sin_trasvase;                          ; 0x7ef036 cbz r5  <-- puerta
EventManager::move(cola1 -> cola0);                      ; 0x7ef03a  (un evento)
r5 -= 1; repetir                                         ; 0x7ef042
```

Es decir: **la cola 1 solo llega al consumidor por el trasvase, un evento por vuelta, y `[AppSystem+0x28]`
solo lo escribe el evento `0x11001004` (parámetro `0xe`)**. Si vale 0, el trasvase no corre; si vale *n*, la
vuelta mueve hasta *n*.

## 2. La cadena de la tecla, hasta la cola (VERIFICADO en el invitado)

`InputService::pushFilterEvent` (`+0x1117f4`) tiene dos caminos y **en el arnés toma el primero**:

```
filtro = *(libObj+0x10a8c50)            ; slot del GOT -> variable .bss (una sola referencia en todo el ELF)
if (filtro) filtro(&lista, evento);      ; 0x111822 blx r3   <-- camino tomado
else        lista.push(evento);
while (!lista.empty()) { e = lista.pop(); AbstractUtilityManager::pushEvent(e); }   ; 0x11183c bl 0x127bb6
AbstractUtilityManager::notify();        ; 0x111852 bl 0x127bc4
```

- El filtro que hay en el invitado, leído con `P 10a8c50` = **`0x78ca8fb9`** = `viewUnified2.so+0x181fb9`
  (base `0x78b27000`, de las trazas). Esa función compara el código del evento con la tabla de `viewUnified2`
  (`.text` VA `0x182080` = `0x150100f2`, `0x182084` = `0x15070050`…) y reengancha los eventos en una lista
  (`std::_List_node_base::_M_hook`).
- La publicación final la hace **`libObj+0x7f0adc`**, que llama a `EventManager::push(evento, **notify = 0**)`
  (`movs r2,#0` en `+0x7f0ade`). El mismo fichero tiene la variante con aviso en `+0x7f0acc`
  (`AbstractUtilityManager::pushEvent`, `notify = 1`), que es la que usa `ModelManager`.

**Medido** (`EQTRACE`, herramienta nueva de esta sesión, §6) con cuatro pulsaciones en el perfil `cola2`:

```
254.27 [shim] EQTRACE 132 code=150100f2 dest=4 clase=1 notify=0 lr=libObj.so+0x111841   <- Reproducción, bajada
254.86 [shim] EQTRACE 134 code=150100f1 dest=4 clase=1 notify=0 lr=libObj.so+0x111841   <- suelta
256.88 [shim] EQTRACE 136 code=15010072 dest=4 clase=1 notify=0 lr=libObj.so+0x111841   <- arriba, bajada
257.35 [shim] EQTRACE 138 code=15010074 dest=4 clase=1 notify=0 lr=libObj.so+0x111841   <- menu
262.24 [shim] EQTRACE 172 code=150100f2 dest=4 clase=1 notify=0 lr=libObj.so+0x111841   <- Reproducción otra vez
```

Es decir: **la tecla sí entra en la cola del framework** (corrige la lectura de [g22-reproduccion-sd §8.3](g22-reproduccion-sd.md#83-dónde-se-corta-ahora-verificado)
«no hay quien lo despache»), pero lo hace **en la cola 1 y sin avisar**.

## 3. Por qué la cola se atasca (MEDIDO)

En el invitado la vuelta de `Appframework` no es frecuente. `cola1`, **290 s de invitado con 1 pulsación**:
`TRACEFN` con **≥128** publicaciones, **≥32** trasvases, **≥128** extracciones y **≥128** despachos (los
contadores de `TRACEFN` imprimen las 16 primeras y luego potencias de 2, así que son cotas inferiores).
Con 2 eventos de entrada por pulsación y **1 trasvase por vuelta**, cada pulsación deja al menos un evento
*pendiente*, y la espera del consumidor tiene un plazo de ~3 s (`Event::wait` = `poll`, `+0x7eec00`): el retardo
de una tecla crece con las pulsaciones acumuladas. Cuando la profundidad de la cola 1 pasa por un múltiplo de
100, el invitado lo escribe (`[FMWK] EventQueue pile. count: 100`, visto en
[g22-reproduccion-sd §8.2](g22-reproduccion-sd.md#82-medido-la-tecla-sí-sale-del-driver-y-llega-a-inputservice-verificado)).
En `cola1` (290 s) y en `cola2` (263 s) **no llegó a 100**: 0 líneas `[FMWK]`. Es decir: con pocas pulsaciones
la cola no se satura —el corte de la tecla **no** es la saturación—, pero el ritmo de vaciado (1 evento por
vuelta, sin aviso) no aguanta una sesión de navegación con decenas de pulsaciones, que es el escenario de
G22-CUELGUE. **La profundidad de la cola no se mide directamente** (no hay lectura de memoria del montón en el
shim); el aviso cada 100 es la única medida indirecta.

## 4. El arreglo (`EVQNOTIFY`, 2 bytes)

`sonyshim.c`, al cargar `libObj.so`, escribe `+0x7f0ade`: `movs r2,#0` → `movs r2,#1` (mismo molde que
`efcs_patch`/`NULLMWF`: `mprotect` + `clear_cache`). Con eso la publicación de entrada **avisa** al consumidor y
`Appframework` despierta en el acto en vez de esperar su plazo. Se apaga con `NOEVQNOTIFY=1`.

- No toca el trasvase, ni el pop, ni `AppSystem::dispatch`: el camino sigue siendo el del firmware.
- `INFERENCIA`: en la cámara ese punto avisa (si no, tendría el mismo retardo). No hay medida de la cámara
  física que lo confirme.

## 5. Antes / después (mismo perfil de medidas, mismos 4 pulsaciones)

Mismos binarios, mismo `SHIMEXTRA`, mismo arranque en frío, mismas pulsaciones (reproduccion · arriba · menu ·
reproduccion) y luego 15 pulsaciones más de Reproducción en `cola4`. Perfiles `cola2` (antes, puerto 8685) y
`cola4` (después, puerto 8687); extractos en `reports/evidence/g22-cola-20261126/`.

| Medida (invitado) | Antes (`cola2`) | Después (`cola4`) |
|---|---|---|
| eventos de entrada publicados en la cola (`EQTRACE` `0x1501xxxx`) | 8 | **39** |
| `notify` de esos eventos | **0** (los 8) | **1** (los 39) |
| trasvases cola 1 → cola 0 (`+0x7ef910`, cota inferior) | ≥32 | **≥64** |
| publicaciones / extracciones / despachos (`+0x7ef960` / `+0x7ef940` / `+0x7eed0c`, cotas) | ≥128 / ≥128 / ≥128 | **≥256 / ≥256 / ≥256** |
| avisos `[FMWK] EventQueue pile` (profundidad 100) | 0 | **0** |
| `DispatchEvent` (`+0xf59f0`) con `0x1501xxxx` | **0** | **0** (r1 = `2`, `8`, `0x23`, `0x2a`, `0x1101…`) |
| `ActionCheckerListBase::execAction` (`+0x11817e`) | **0** | **0** |
| SIGSEGV / abortos | 0 | 0 |
| `/estado` al final | 2 fotogramas, 2 listas, opacos 0,0046 | 5 fotogramas, **0 listas**, opacos 0,0 |

Lo que cambia con el parche es el **ritmo de entrega**: cada evento de entrada despierta al consumidor en vez de
esperar a su plazo. Lo que **no** cambia es que la tecla no llega a la acción (§7).

## 6. Herramienta nueva: `EQTRACE`

`EQTRACE=1` (con `EQMAX=n`, 200 por omisión) envuelve `EventManager::push` —el shim ya interponía el símbolo
para `SYNCTRACE`, aquí se añade el código de clase— y escribe una línea por publicación con **código del evento**
(`Event+4`), **destino** (`+8`), **clase** (`+9`), **notify** y **quién la publica** (`lr`):

```
[shim] EQTRACE 132 code=150100f2 dest=4 clase=1 notify=0 lr=libObj.so+0x111841
```

Responde de una vez «¿el evento llega a la cola del framework, y a cuál?», que es lo que faltaba para no
deducirlo del registro del invitado. Extractos versionados: `reports/evidence/g22-cola-20261126/`.

## 7. Qué sigue roto (no lo arregla esta sesión)

Después del parche, la tecla llega al despachador en milisegundos, pero:

- `DispatchEvent` (`libObj+0xf59f0`, thunk virtual de 12 B) se dispara con identificadores internos de la vista
  (`2`, `8`, `0x23`, `0x2a`) y **ninguno** `0x1501xxxx`;
- `ActionCheckerListBase::execAction` (`libObj+0x11817e`): **0 disparos**;
- el filtro de la vista (`viewUnified2+0x181fb8`) **sí** conoce el código de la tecla (compara con
  `0x150100f2` en `0x182080`) y reengancha eventos en una `std::list`, pero de ahí no sale ninguna acción.

O sea: el corte ya no está en la cola del framework (medido: estaba en el ritmo del trasvase y en la falta de
aviso) sino **dentro del filtro/la cadena de la vista de `viewUnified2`**, que es donde hay que seguir.

Y un dato nuevo para G22-CUELGUE, medido aquí por casualidad al pulsar 19 veces Reproducción con el parche
puesto: `/estado` pasa a **`5 fotogramas · 0 listas · opacos 0,0`** y **no se recupera** 8 s después de pulsar
MENU. Es decir, **el cuelgue de la navegación no es la cola del framework**: con el parche la cola 1 no llegó a
100 (0 avisos) y la pantalla se quedó igualmente en blanco. Coincide con lo que ya decía
[g22-cuelgue-navegacion §2](g22-cuelgue-navegacion.md): las teclas entran y el que deja de trabajar es el hilo
que despacha las vistas.

## 8. Cómo repetir la medida (~5 min, sin cámara)

```sh
cd /home/nicolas/h-cola
HOME=/tmp/hcola/home SD_ESTRUCTURA=1 \
SHIMEXTRA="WAITLOG=3000 EQTRACE=1 EQMAX=400 TRACEFN=7ef960,7ef910,7ef940,7eed0c,1106b8,1117f4,f59f0,11817e TRACEREP=1 TRACEMAX=16" \
  /home/nicolas/a6000-arnes/.venv/bin/python scripts/gui/harness/live.py /tmp/hcola/work --perfil-dir colaX --puerto 86XX
# a los ≈160 s, GET /estado; luego
curl -X POST -d '{"k":"reproduccion","v":1}' http://127.0.0.1:86XX/tecla; sleep 1
curl -X POST -d '{"k":"reproduccion","v":0}' http://127.0.0.1:86XX/tecla
# y se miran live/colaX/shim.log: EQTRACE (notify), TRACE f59f0 (r1) y TRACE 11817e
curl -X POST http://127.0.0.1:86XX/salir
```

Test sin QEMU: `tests/test_g22_cola.py` (6 casos: aviso «cada 100», `Event{+4,+8,+9}`, separación de colas,
trasvase/consumidor y sus puertas, `pushFilterEvent` sin aviso, y que el shim trae `EQTRACE` y `EVQNOTIFY`).

## 9. VERIFICADO / INFERENCIA / NO_VERIFICADO

| # | Afirmación | Etiqueta | Evidencia |
|---|---|---|---|
| 1 | `[FMWK] EventQueue pile. count: %d` se imprime cuando la profundidad de la cola 1 es múltiplo de 100, no cuando se llena | **VERIFICADO** | `libObj+0x7ef99c` `movs r1,#0x64` + `+0x7ef9a2` `__aeabi_uidivmod` + `+0x7ef9a8` `cbnz r1`; cadena en `0xd88103` |
| 2 | `Event` guarda código en `+4`, destino en `+8` y clase en `+9`; `push` manda clase 1 a la cola 1 (con aviso opcional) y clase 0 a la cola 0 (sin aviso) | **VERIFICADO** | `+0x7f17f8`, `+0x7ef88c`, `+0x7ef98e`/`+0x7ef9de` |
| 3 | El consumidor es `AppSystem::Main` (hilo `Appframework`): extrae de la cola 0 y despacha con `AppSystem::dispatch` | **VERIFICADO** | `+0x7eefda` (`pop`), `+0x7eefe2` (dispatch), `+0x7ef03a` (trasvase) |
| 4 | El trasvase cola 1 → cola 0 es el único camino y está detrás de `cbz r5` con `r5 = min([AppSystem+0x28], count(1))` | **VERIFICADO** | `+0x7eef4e`, `+0x7ef036`, `+0x7ef910` |
| 5 | La tecla **sí** entra en la cola del framework, como `0x150100f2`/`0x150100f1`, clase 1, `notify = 0`, desde `pushFilterEvent+0x4d` | **VERIFICADO** | `EQTRACE` en `cola2` (§2) |
| 6 | El filtro de la vista que registra el invitado es `viewUnified2.so+0x181fb9` y compara el evento con `0x150100f2` | **VERIFICADO** | `P 10a8c50` = `0x78ca8fb9`; tabla `.text` `0x182080` |
| 7 | En 290 s de invitado la cola 1 **no** llegó a 100 (0 avisos `[FMWK]`) y el corte de la tecla no es la saturación | **VERIFICADO** | `cola1`: 0 líneas `[FMWK]`; `cola2`: contadores `TRACEFN` |
| 8 | Con `EVQNOTIFY` el `notify` de los 39 eventos de entrada pasa a 1 y el número de trasvases se dobla en la misma ventana | **VERIFICADO** | `cola4` (§5) |
| 11 | Con el parche, `DispatchEvent` sigue sin recibir `0x1501xxxx` y `execAction` sigue a 0: el parche mueve el corte, no cierra el síntoma | **VERIFICADO** | `cola4`, §5 |
| 12 | La pantalla queda en «0 listas» tras 19 pulsaciones también con el parche: el cuelgue no es la cola | **VERIFICADO** (síntoma) / **INFERENCIA** (causa) | `/estado` de `cola4` (§7) |
| 13 | La profundidad real de la cola 1 en cada instante (no hay lectura del montón del invitado) | **NO VERIFICADO** | sólo el aviso cada 100 |
| 9 | En la cámara ese punto avisa (o el mismo esquema no tendría el retardo) | **INFERENCIA** | no hay medida física |
| 10 | Qué consume la `std::list` del filtro de `viewUnified2` y por qué no ejecuta la acción | **NO VERIFICADO** | §7 |

## PARA PENDIENTES.md

| ID | Estado | Resumen | Criterio de cierre |
|---|---|---|---|
| G22-COLA | MEDIDO Y PARCIALMENTE ARREGLADO (26-11-2026) | **La cola de eventos del framework (`EventManager`, `libObj`) no se llenaba: se vaciaba despacio.** Estático VERIFICADO: `push` (`+0x7ef960`) separa por clase (`Event[+9]`): clase 1 → cola 1 con aviso opcional, clase 0 → cola 0 sin aviso; el único camino cola 1 → cola 0 es el trasvase `+0x7ef910`, que el bucle `AppSystem::Main` (`+0x7eeee8`, hilo `Appframework`) ejecuta **una vez por vuelta y solo si `r5 = min([AppSystem+0x28], EventManager::count(1))` ≠ 0**; el consumidor extrae de la cola 0 (`+0x7ef940`) y despacha (`+0x7eed0c`). El aviso del invitado **`[FMWK] EventQueue pile. count: %d` se imprime cuando la profundidad de la cola 1 es múltiplo de 100** (`__aeabi_uidivmod` con 100 en `+0x7ef9a2`; cadena `0xd88103`), **no** cuando la cola se llena — corrige la inferencia de G22-REPRO §8.3. MEDIDO en el invitado (perfiles `cola1`/`cola2`, 26-11-2026): la tecla **sí entra** en la cola, como `code=150100f2`/`150100f1` `dest=4 clase=1 **notify=0**` desde `pushFilterEvent+0x4d` (herramienta nueva `EQTRACE=1 EQMAX=n`, que envuelve `EventManager::push` e imprime código/destino/clase/notify/llamante); en 290 s con 1 pulsación, ≥128 publicaciones, ≥32 trasvases, ≥128 extracciones, ≥128 despachos y **0** avisos `[FMWK]` (la cola no llegó a 100). **Causa**: `InputService` publica sin avisar y el trasvase mueve 1 por vuelta → el retardo de cada tecla crece con las pulsaciones acumuladas (plazo del consumidor `Event::wait` = `poll`, ~3 s). **Arreglo**: `EVQNOTIFY` (por omisión; `NOEVQNOTIFY=1` lo quita) escribe `movs r2,#1` en `libObj+0x7f0ade` (2 bytes, molde `efcs_patch`) → el `notify` de los eventos de entrada pasa a 1 y el despacho deja de esperar la vuelta. **Sigue abierto**: `DispatchEvent` (`+0xf59f0`) no recibe ningún `0x1501xxxx` y `execAction` (`+0x11817e`) no se ejecuta nunca (igual antes y después del parche); el filtro de la vista (`viewUnified2.so+0x181fb9`, registrado en `libObj+0x10a8c50`, medido con `P 10a8c50`) conoce el código y reengancha los eventos en una `std::list` (`_List_node_base::_M_hook`) pero no ejecuta la acción. **Para G22-CUELGUE**: con el parche puesto, 19 pulsaciones de Reproducción dejan `/estado` en `5 fotogramas · 0 listas · opacos 0,0` sin recuperarse tras MENU y **sin** aviso `[FMWK]` (la cola no era el cuelgue). La profundidad real de la cola no se mide (no hay lectura del montón del invitado). Test sin QEMU: `tests/test_g22_cola.py` (6 casos). | Que una pulsación de `0x1f7` produzca `TRACE f59f0 … r1=150100f0` y `TRACE 11817e` > 0 en la misma pasada, y que con `EQTRACE` la cola 1 no pase de ~10 tras 50 pulsaciones |
