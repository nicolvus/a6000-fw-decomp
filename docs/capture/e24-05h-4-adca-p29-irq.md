# E24-05h-4 — Auditoría final de ADC-A, grupo activo de P29 y entrega del evento de ADC-B (27-10-2026)

Sesión 100 % estática: sin cámara, sin USB, sin escrituras de RAM/NAND/NVRAM, sin FDAT ni flasheo, sin tocar el watchdog ni protecciones, sin parche. Base `aa570baf`. Cierra los residuos de [E24-05h-3](e24-05h-3-adcb-p29.md) (ADC-A, grupo de P29, IRQ del canal 0). No abre E24-05h-5 ni E24-06.

Reproducible: `python scripts/e24_05h4/adca_p29_irq.py` → `analysis/e24-05h-4/adca_p29_irq.json`; `pytest tests/test_e24_05h4_adca_p29_irq.py` (15 pruebas sobre bytes reales). `scripts/e24_05h4/flow.py` añade un recorrido de flujo con poda por tipo de bobina (`bl 0x20c74` + `cbz/cmp r0` fija r0) y ciclos por componentes fuertemente conexas, sobre el barrido de E24-05h-3.

## Veredictos A–G

| | Pregunta | Resp. | Naturaleza |
|---|---|---|---|
| **A** | ¿ADC-A retorna sin bloquear ADC-B con tipo 0? | **SÍ** | Estado 4 de ADC-B ejecuta ADC-A de forma síncrona solo hasta su primer estado (`0x20734`: arma temporizador, no «hecho») y retorna. Cierres de los estados 2/4/6/16 con tipo 0: 6/4/3/5 funciones, sin ciclos, sin indirectos, sin lecturas de pin (§1). El contexto del motor es de pila (`sub sp,#0x14`), no se comparte con ADC-B |
| **B** | ¿ADC-A introduce dependencia **mecánica** obligatoria? | **NO** | *Respuesta negativa demostrada* (no es evidencia insuficiente ni contradicción): el cierre completo con tipo 0 no contiene `0x51c6` ni lecturas de periférico de entrada. Solo escribe pines (estado 16 → `0xd18e(0x400000)` → `0x51c0`, igual que el estado 6 de ADC-B con `0x800000`). **Sí** introduce una dependencia **temporal** obligatoria, no mecánica (§2) |
| **C** | ¿Identificado el grupo de P29 durante la captura? | **SÍ** | Grupo **3**: P29 = **INT05 (modo 5), sin pull**, aplicado por «On init» `0x75f0` (`movs r0,#3` en `0x7616`, `bl 0x5792` en `0x7618`). Ninguno de los 156 manejadores de los FSM de captura alcanza un cambiador de grupo (§3). Condición: el sistema está en `On` (estado 2), único estado con grupo 3 |
| **D** | ¿Cadena software de entrega del evento de ADC-B reconstruida? | **SÍ** | Armado `0x1e1d2` → `0x94f6` → `0xf99a` (NVIC IRQ 32) → `0xfa18`; ISR `0xf8d3` → `0xf88e` → `[0x296d4]` = `0x1d04d` → motor. Todos los enlaces por bytes (§4). El enlace **vector↔NVIC** depende de un VTOR que no está en la imagen: la tabla coherente es la de base `0x42fc` (IRQ 32/33 = `0xf8d3`/`0xfa95`) |
| **E** | ¿Bloqueo estático **demostrado** que impida completar la captura sin rearme? | **NO** | Ninguna ruta de software bloquea por sí sola. Los puntos de espera no acotados existen pero dependen de eventos de hardware (canal 0 de `0x40023000`; temporizador base canal 11), son idénticos a los de la captura convencional, y no se demuestran fallando. No es contradicción |
| **F** | ¿Se puede demostrar ausencia de bloqueos en la ruta completa sin medir hardware? | **NO** | *Evidencia insuficiente* (no contradicción): VTOR/arranque, prioridad NVIC, semántica de bits de `ctrl` y reloj del contador, ISR/habilitación del temporizador base canal 11 y equivalencia temporal con T022 no están en `darwin_core.bin` |
| **G** | Valores mínimos a observar | — | Tabla en §6 |

## 1. ADC-A desde el estado 4 de ADC-B

* Descriptor `0x29d90`, tabla `0x29e00`, terminal 17, temporizador 0 = id 5, estado RAM `0x2000381c/d`, celda `0x20003818`.
* Estado 4 de ADC-B (`0x20aa4`, ya analizado): P4B, `0x201b0(0)`, `0x20408`, cancela su propio temporizador (`0x1e476`, `0x20ad6`), instala `0x29d7e` (`0x20ae0`), **ejecuta `0x20c06(0)`** (`0x20ae6`) y termina con «hecho» (`0x20af0 b.w 0x1e4aa`).
* Lista que se ejecuta desde ADC-B: **`[2,4,6,16,17]`** (mismas instalaciones en `0x2045c` y `0x205d0`; otras listas de ADC-A —`[9,10,16,17]`, `[14,15,16,17]`, `[7,15,17]`, `[1,3,5,16,17]`— las instalan otros arrancadores y no pasan por ADC-B).

| Estado | Manejador | Efecto con tipo 0 | Añade con tipo ≠ 0 | Hecho / temporizador |
|---|---|---|---|---|
| 2 | `0x20734` | `0x5c9e/0x5c88` (sección crítica), `0x183d6`, `0x20c74`; arma temporizador `100·[0x20000300+0x32]` | `0x210a2`, `0x21014` (45 funciones, ciclos en `0x5cd4` y `0x5d00`) | **no hecho**, arma (`b.w 0x1e3d2` en `0x207ba`) |
| 4 | `0x207e8` | `0x20cd4` (sin `0x51c0`), arma `100·([+0x31]−[+0x32])` si positivo, si no 0 | `0x16ff4`, `0x20cd4` escribe pin `0x238` | no hecho, arma (`0x20818`) |
| 6 | `0x2083c` | `0x20c74=0` → salta a «hecho» | `0x1b17c`, `0x1f3d4`, `0x201b0(2/0)`, `0x16558` | hecho |
| 16 | `0x20a4c` | `0xd18e(0x400000)` (libera máscara local de P4B, escribe `0x51c0`) | igual | hecho |

* Simulación del motor (semántica de E24-05h-3 §2): invocación 0 (síncrona, desde ADC-B): estado 2 arma y avanza a 4; invocación 1 (evento): estado 4 arma y avanza a 6; invocación 2 (evento): 6 → 16 → 17. **ADC-A necesita dos eventos de su temporizador para llegar a terminal.**
* Verificado en bytes: el contexto que reciben los manejadores es un buffer de pila de `0x14` B creado en `0x1e33e` (`sub sp,#0x14`, `mov r0,sp` antes de `blx r1`); la llamada anidada de ADC-A no comparte banderas con la de ADC-B. `0x20c06` indexa el descriptor con `7·idx·4` desde `0x29d90`.
* **Ningún ciclo ni espera externa** en los cierres podados de ADC-A (tipo 0) ni de ADC-B 0–6 (tipo 0 y ≠ 0). El único `blx` residual es la lectura de contador `0x94e8` (indirecto a `[0x2792c+0x18]`, hoja). Un falso positivo del recorrido (`0x20fd6 = 0x1b30a(0x2c,0x31)`) se resuelve por réplica de `0x1b30a`: con esos argumentos solo escribe ISER del IRQ `0x2c` (`0x1b56e`), no llega a los sondeos de `0x5d00`.
* **Posición física del obturador:** no se lee en ningún manejador de ADC-A con tipo 0 (sin `0x51c6`, sin periférico de entrada). Con tipo ≠ 0, `0x210a2/0x1f3d4` quedan accesibles (no analizados a fondo: fuera del alcance de «tipo 0»).
* Temporizador de ADC-A: id 5 → bloque A (`0x2a69c`) → **canal HW 11 de los temporizadores base** (no es `0x40023000`); cuentas `⌊5·ticks/8⌋` acotadas a `[1, 0xffff]` (`0x24bee`); callback `0x2969c[11] = 0x1d041` → `b.w 0x197b0` → `0x199f2` → `b.w 0x20248` → `0x20220(0)` → `0x20c06(0)` (ADC-A). Despachador genérico: vectores `0xf305/0xf317/0xf329/0xf2d9` (`0x43ac–0x43b8`) → `0xf370(canal)` → `0xef28/0xf698` → `blx [0x2969c+4·canal]`. **No se enumeró** la ISR/habilitación específica del canal 11 (límite).

## 2. Dependencia temporal de ADC-A: estados 3 y 32 de la captura

Hallazgo nuevo (no estaba en E24-05h): dos manejadores de la máquina de captura (49 estados, descriptor `0x28fdc`, posición/id `0x200036fc/d`) **fallan si ADC-A y ADC-B no están ambos en terminal**:

| Estado | Manejador | Condición | Resultado |
|---|---|---|---|
| 3 | `0x1860c` | `0x196a2≠0` ∧ `[0x20000300+0xcd]` bit 2 = 0 ∧ `0x19974()=0` | FAIL (`b.w 0x1e4c2`, `0x18630`) |
| 32 | `0x192a0` | `0x19974()=0`; con ambas en terminal además `0x1e782/0x1e710/0x1e70c` | FAIL (`0x192c4`); si todo OK → `b.w 0x1b178` |

`0x19974 → 0x204b2 → 0x20c34`: devuelve 1 solo si ADC-B es terminal (`0x20c2c`) **y** ADC-A es terminal (`ldr =0x29d90; b.w 0x1e16e`). Orden de la lista de captura: `…,28,31,32,48,49`; **el estado 32 sigue inmediatamente al 31**. Según E24-05h §5 FAIL no avanza y se reintenta en la siguiente invocación del motor: el estado 32 **espera** (por reintento, sin plazo) a que ADC-A llegue a 17. Otras esperas activas por ambas FSM (`0x20384`, `0x204b6`, llamadas desde `0x1981e/0x19836`) no están en el estado 31 (`en_estado_31_0x18d6e = []`) y usan listas distintas (`[9,10,16,17]`, `[1,3,5,16,17]`).

Consecuencia: el requisito es idéntico con tipo 0 y con tipo ≠ 0 (las cuentas de ADC-A salen de `[0x20000300+0x31/0x32]` antes de cualquier bifurcación por tipo). Es un riesgo temporal que comparte la captura convencional, no una dependencia mecánica.

## 3. Grupo activo de P29 (B)

Los diez sitios de `0x5792` aplican un grupo constante (`movs r0,#k` inmediatamente antes):

| Estado (`0x25b50`, filas de 16 B) | Callbacks | Grupo | P29 |
|---|---|---|---|
| (arranque) `0x46b2` | `0x478a` | 0 ó 1 (según `[obj+6]\|[obj+7]<<8 ∈ {5,2}`) | salida GPIO |
| 0 Init | `0x7150` | **5** (`0x71c4`: 6, retardo, 5) | salida GPIO |
| 1 Seton | `0x73cc` | **2** | entrada GPIO |
| **2 On** | **`0x75f0`** | **3** | **INT05 (modo 5)**, sin pull |
| 3 | `0x8044` | **4** (condicional a `[r4+0x14]=0`) | entrada GPIO |
| 4 Off | `0x8234` | **5** (`0x8538`: 6, luego 5) | salida GPIO |
| 5 Upd | `0x8da4/0x8da8` | — | — |

* Los grupos solo cambian en las inits de estado, en `0x71c4` (Init main) y `0x8538` (Off main). El cierre estático de los **156 manejadores** de todos los FSM de captura (FSM_A, C, D, E, exterior `0x29cf0`, interior de 49, ADC-A/B/C: 816 funciones) **no contiene ninguno** de `0x5792, 0x46b2, 0x7150, 0x71c4, 0x73cc, 0x75f0, 0x8044, 0x8234, 0x8538, 0x55d0, 0x5b60, 0x5512`.
* «On main» `0x76ce` bloquea en la cola 0 (`bl 0x4530`) y solo sale con mensaje tipo 1 ó 2 (`cmp #1/#2`); `On next` (`0x274b8`) = `[3,3]`: salir de `On` exige ese mensaje, no ocurre dentro del FSM de captura. Tablas `next`: Init `0x274a4[0]=1`; Seton `0x274a8=[2,3,5,3]` (evento 2 → 5 = Upd, solo desde Seton); On `0x274b8=[3,3]`.
* P29 se **lee** por sondeo en `0x1ec9c` y `0x7d12–0x7d16`; con modo 5 el nivel externo (red `MSS_S2_REQ_CA`) llega sin que BIONZ lo fuerce Darwin. El nivel inicial de PDOR2.9 y la habilitación de INT05 **dejan de ser relevantes** (entrada, lectura por sondeo). Límites: el cierre ignora llamadas indirectas; que el sistema esté en `On` durante la captura se apoya en que «On init» `0x75f0` arranca la carga de la máquina exterior (`0x1b260 → 0xcee6 → 0x1984e`, E24-05), no en una prueba nueva.

## 4. Cadena de entrega del evento 0 de ADC-B (C)

| Eslabón | Evidencia (bytes) | Condición que puede impedir la entrega |
|---|---|---|
| Init global del contador | `0x8fb4 → 0xf834` (estado `[0x20002d68]` 0→1, `0xfaba`: `ctrl(+8)`=0x50…, contador=0) → `0xf84e` (1→2, `bic 0x50`); cadena `0x46b2 → 0x47f4 → 0x5f04 → 0x8fb4` | Los tres callbacks previos de `0x8fb4` (`[0x2792c+4/+0xc/+0x24]`) deben devolver 0; `0xf834` devuelve −1 si ya estaba iniciado |
| Armado | estado 1 de ADC-B → `0x1e3d2` → tras el manejador `0x1e2b6 → 0x1e1d2(9, S+0x14c)` → `0x24d1a`, `0x24ca4` (parada), `0x24cfa`, `0x24c6e` (mín. 10 ticks) → `0x9388 → 0x94f6(canal 0, ticks)` | `ticks` se multiplica por 5 y se divide por 5; si no coincide (desborde de 32 bit) la cuenta pasa a `0xffffffff` |
| Contador y comparador | `0xf86e`: si `[0x20002d68]∈{1,2}` lee `[0x40023000+4]`; compare = ticks + contador → `[0x20002d70]` | Si el estado global no es 1/2, no se lee el contador (compare = ticks + 0) |
| Habilitación | `0xf99a`: si estado de canal `[0x20002d6c]==0` → `0xfaa2(0x20)` (ISER1 bit 0 = **IRQ 32**), estado←1, `0xf8ee` (config de `ctrl +0x1c` desde `[0x27970]=0x180` ⇒ `0x2094` calculado; compare → `+0x14`); `0xfa18` (1→2, `ctrl` \|= 0x81, &~0x40) | **Canal ocupado:** `0xf99a` devuelve −1 y `0x94f6` lo ignora; la parada previa (`0xfa54` 2→1, `0xf9ce` 1→0) evita esto |
| ISR | Vector IRQ 32 = `0xf8d3`: lee `[0x40031094]` bit 0 (monitor de IRQ 32: `0x14+4·IRQ`) → `0xf88e(0)`: exige `ctrl +0x1c` bit 6, lo limpia (escribe 0x80) y hace `blx [0x296d4+4·canal]` | `[0x40031094]` bit 0 = 0 o bit 6 sin activar ⇒ no hay despacho |
| Callback | `0x296d4[0]=0x1d04d` → `0x197d8 → 0x199b0 → 0x203ae`; si 0 → `0x197c6 → 0x199fe → 0x20274 → 0x20220(2) → 0x20c06(2)` | El callback corre **en contexto de ISR**; si el hilo que sondea (`0x18e8a…`) tuviera igual o mayor prioridad, no se ejecutaría |
| Parada (un disparo) | Estado 4 de ADC-B fija bit 3 con `0x1e476(ctx,0)`; tras el manejador `0x1e300 → 0x1e0e4 → 0x24ca4 → 0x93a0 → 0xfa54 + 0xf9ce` | Solo el estado 4 cancela el temporizador. En `[1,5,6,7]`/`[1,3,6,2,7]` el canal puede quedar en estado 2; no se analizó si re-dispara al dar la vuelta el contador (no afecta a `[1,4,6,7]`) |

**Tabla de vectores.** La imagen contiene dos: base `0x4200` (SP + excepciones; IRQ 0–46 todas `0x6809` por defecto) y otra con `Reset=0x45c9` en `0x4300`, es decir base `0x42fc` (palabra 0 = `0x6809`, no es SP). Solo esta última pone `0xf8d3`/`0xfa95` (`0x43bc/0x43c0`) en los índices **IRQ 32/33**, que son exactamente los que habilita `0xf99a` (`0x20/0x21`) y cuyos monitores lee la ISR (`0x94/0x98 = 0x14+4·IRQ`). Triple coherencia → es la tabla en uso (INFERENCIA; el VTOR lo fija el arranque, fuera de la imagen). Si se usara la de `0x4200`, la IRQ iría a `0x6809`.

Parámetros no demostrados por software: prioridad NVIC de IRQ 32 (no se halló escritura de IPR), reloj y preescalador del contador (`[0x2796c]=0x10400`), semántica de cada bit de `ctrl`, unidad de los ticks (µs inferida).

## 5. Dictamen integrado (D)

| Aspecto | 1 Convencional, temporizador funcional | 2 Tipo 0 sin rearme, temporizador funcional | 3 Tipo 0 con fallo |
|---|---|---|---|
| ADC-B | 1 → 4 → 6 → 7 (un evento de canal 0) | idéntico; sin P4D/P4E, `0x16fe2`, `0x20c4a` | **IRQ 32 ausente** (condición de hardware): ADC-B queda en 4; los bucles `0x18e8a/0x18f7e/0x18f88` esperan `0x203ae` sin plazo → espera indefinida, consecuencia determinista del software dada esa ausencia |
| ADC-A | 2 → 4 → 6 → 16 → 17, dos eventos del temporizador base canal 11 | mismas cuentas y eventos; manejadores más cortos, sin pines ni ciclos | **Evento canal 11 ausente**: ADC-B y estado 31 terminan; el estado 32 reintenta (FAIL) indefinidamente. **ADC-A "bloqueada" por software: no demostrado ni posible** (manejadores finitos) |
| Estado 3/32 | Requieren ADC-A y ADC-B en terminal | ídem | ídem |
| Grupo P29 | 3 (INT05) | 3 (INT05) | **Grupo incorrecto**: solo si el sistema no está en `On`; no hay camino estático dentro de la captura |
| Bloqueos de software demostrados | ninguno | ninguno | ninguno por sí mismo; las esperas dependen de IRQ |
| Riesgos de hardware | IRQ 32, IRQ canal 11, VTOR, prioridad | los mismos (no dependen del tipo de bobina) | los mismos |

El tipo 0 **no cambia** ninguna de las condiciones de entrega ni de espera; solo suprime escrituras de pines y rutas de posición.

## 6. Experimento mínimo de solo lectura (no ejecutado) — G

Con el método de lectura de T022 durante un disparo normal (sin escrituras). Orden de aparición de los valores en una captura que completa:

| # | Valor | Dirección | Esperado / qué decide |
|---|---|---|---|
| 1 | Tipo de bobina | resultado de la función `0x20c74` (`0x1b080(0)&7`); no es una celda RAM: se deduce de las escrituras P4D/P4E (E24-05h-2) | 0 en el escenario; define si aplica el análisis |
| 2 | Estado del sistema | `0x20002a04` | 2 (`On`) ⇒ grupo 3 |
| 3 | Posición/id de la captura | `0x200036fc/0x200036fd` | 31 → 32; si se queda en 32 repetidamente ⇒ espera de ADC-A/B (§2) |
| 4 | ADC-B posición/id/celda | `0x2000381e/0x2000381f/0x20003820` | 1 → 4 → 7; si se queda en 4 ⇒ no llegó el evento canal 0 |
| 5 | Ticks de ADC-B | `S+0x14c = 0x20003824` | duración armada (un valor, sin unidad conocida) |
| 6 | `S+0x32`, `S+0x444` bit 4, `S+0x170` bit 0 | `0x2000370a`, `0x20003b1c`, `0x20003848` | `0x1600`; 0; 0 (compuerta `0x19b9e`) |
| 7 | ADC-A posición/id/celda | `0x2000381c/0x2000381d/0x20003818` | llega a 17 antes del estado 32; si se detiene en 4 ó 6 ⇒ falta evento canal 11 |
| 8 | Duraciones de ADC-A | `0x20000331`, `0x20000332` | cuentas `100·[+0x32]` y `100·([+0x31]−[+0x32])` |
| 9 | Temporizador canal 0 | `0x20002d68` (global, esperado 2), `0x20002d6c/0x20002d6d` (estado/flag), `0x20002d70` (compare) | estado 2 mientras corre; 0 tras el evento |
| 10 | Temporizador base canal 11 | `0x20002d30+4·11 = 0x20002d5c` | palabra de control del canal |
| 11 | Registros del periférico (solo si el método alcanza periféricos) | `0x40023004` (contador), `0x40023014` (compare), `0x4002301c` (ctrl), `0x40031094` (monitor IRQ 32) | contador alcanza compare; ctrl bit 6; monitor bit 0 |
| 12 | Configuración de P29 (idem) | puerto 2 bit 9 (`0x5792`: PFR `0x40033008`, PCR `0x40033108`, DDR `0x40033208`, PDOR `0x40033408`) | PFR bit 9 = 1 (función INT), DDR bit 9 = 0 |

Solo con 3, 4, 7 y 9 (RAM) ya se distingue entre «no llegó el evento de ADC-B», «no llegó el de ADC-A» y «la captura avanzó».

## 7. Pruebas

`tests/test_e24_05h4_adca_p29_irq.py` (15): lista de ADC-A y estado 4 de ADC-B; contexto de pila; ADC-A tipo 0 sin ciclos/pines/indirectos; qué añade tipo ≠ 0; simulación; temporizador del canal 11 y callback; cierres de ADC-B sin ciclos; dependencia de estados 3 y 32; grupos por estado; P29 modo 5 en grupo 3; ausencia de cambiadores de grupo en el cierre de captura; salida de `On` solo por mensaje; cadena de armado/ISR/callback/parada; coherencia de vectores IRQ 32/33; configuración del canal 0. Pasan junto con las 16 de E24-05h-3.

## 8. Límites

Sin ejecución ni emulación. Recorrido estático por `bl/b.w` y saltos directos (más `tbb` acotados y réplica de `0x1b30a`); las llamadas indirectas (`blx reg`) no se siguen salvo la hoja `0x94e8`. No se analizó la ISR ni la habilitación del temporizador base canal 11, ni la prioridad/VTOR (arranque fuera de la imagen), ni los bits de `ctrl`. «Reintenta» del estado 32 viene de la semántica FAIL de E24-05h §5. La interpretación de los ticks como µs sigue siendo inferencia. El resto es observación física: **E24-05h-5** (diferida, requiere orden expresa) recibe la tabla del §6 como criterio.
