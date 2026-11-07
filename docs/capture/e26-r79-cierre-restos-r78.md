# E26-R79 — Cierre de los restos de R78: handlers de tabla `0x295c4`/`0x25b70`, acciones 04–06/`0x2f` de S y reejecución de S (07-11-2026, estático)

Cierra lo que [R78](e26-r78-cierre-limites-r77.md) dejó sin verificar (§2 «04–06 y `0x2f` … no se desglosaron», «quién reejecuta S», §3 «límite abierto» de los handlers 3 y 4). Capstone y Unicorn sobre `darwin_core.bin` 3.21 (base `0x4200`). Cierres de llamadas con el mismo `_closure` de R78 (cuerpo hasta el retorno, sin seguir punteros). Prueba: `tests/test_e26_r79_restos_r78.py`. Sin REA ni cámara.
Etiquetas: **VERIFICADO** (bytes/emulación) · **CORREGIDO** · **INFERENCIA** · **SOLO MEDIBLE**.

## 1. Cuándo se invocan los handlers 3 (`0x295c4`) y 4 (`0x25b70`)

### 1.1 `0x295c4` = evento `0x16` de la tarea principal — VERIFICADO, CORREGIDO

**CORREGIDO respecto a R78 §3** («cae en la tabla `0x294f8` del descriptor `0x1a050` con campo `0x36b`»): `0x294f8` es la máquina de modos (n=`0x17`) y no contiene `0x295c4`. La tabla de `0x295c4` es **`0x29514`**: pares `(función, máscara)` de 8 bytes, base cargada en `0x1ba22` (literal `0x1bb0c`), que indexa el despachador **`0x1ba00(id)`** con `id < 0x2c`. `0x295c4 = 0x29514 + 8·0x16`: **entrada 0x16, función `0x1b137`, máscara `0x18a`**; el `0x36b` que vio R78 era la máscara de la entrada 0x15 (`0x295c0`).

* `0x1ba00` solo se llama desde `0x7e38` y `0x7f84`, dentro de la **tarea `0x7de2`**, que espera mensajes en la **cola 2** (`0x7df8: movs r0,#2; bl 0x4530`, `svc 0x21`). Mensaje = `(tipo, id)` en dos medias palabras; tipo 1 → `0x1ba00(id)` (`0x7e36–0x7e38`).
* La publica `0x1b97c(id)` (`0x1b994–0x1b9a6`: `(1, id)` a la cola 2). Su único sitio con `id = 0x16` es **`0x1bcbe`**, dentro de **`0x1bc12`**, y solo si `0x1b104() == 1`: bandera `[0x20002e74+8] == 1` y bit 2 de `[bloque 0xa + 5]` a 0 (`0x1b10a`, `0x1b118`), y pestillo 5 (`0x1bb82(5)`) libre. La bandera la pone a 1 el handler del evento `0x15` (`0x1b123`) y a 0 el del `0x16` (`0x1b13c–0x1b140`): son un **par petición/ack con el bloque de configuración `0xa`**, y `0x1b22c` refleja la bandera en el bloque 3.
* `0x1bc12` no tiene llamadores ni punteros directos: solo ocupa `0x2831c` de la lista de ganchos `0x282fc…` que ejecuta `0x127b8` (`0x127be–0x127c6`: `ldr r0,[r5,r4,lsl 2]; blx r0` hasta 0) desde **`0x12502` dentro de `0x124a6`**. `0x124a6` es el «aplicar paquete recibido»: lo alcanza `0x12334` (`0x12330`), llamada por `0x11f4a` (paquete con cabecera **`0x31`**, `0x11f42`, tras comprobar la suma `[+0x7e]`) y `0x120a8`; esas dos las llaman `0x1269c/0x12712/0x1272a` (`0x125f6`, desde `0x7c68`) y `0x7bba` (`0x11f58`, función de la tarea `0x7b24`).
* **Conclusión: el evento `0x16` nace de la recepción de un paquete `0x31` del otro procesador (canal de comunicación), no de la secuencia de captura.** Tras él corre `0x1984e(1)`: `0x1981e`, `0x19836`, **`0x1fee2`** (rearma la máquina de control S_a) y `0x1ff2a`.
* **¿Puede ocurrir entre la preparación y B?** El cierre estricto desde todas las acciones de `0x28fdc` y S (`0x28dd4`) más `0x1961c`, `0x190fc`, `0x1811a` **no contiene** `0x124a6`, `0x127b8`, `0x12330`, `0x11f22`, `0x1bc12`, `0x1ba00`, `0x1984e`, `0x1fee2`, `0x1b260` ni `0xcee6` (prueba). La captura no puede provocarlo; solo un paquete del host con el bloque `0xa` en ese estado, que es asíncrono a ella. **SOLO MEDIBLE** (cámara): si llega un `0x31` con ese cambio durante un disparo; estáticamente la habilitación es posible (tarea de comunicación y tarea principal son independientes de la de captura), la frecuencia no. Si ocurriera sería un reinicio de la máquina de control gobernado por el host, no una función de `B − A`.

### 1.2 `0x25b70` = paso de arranque, una sola vez — VERIFICADO

`0x25b50…0x25ba4` es una **lista de 22 punteros a funciones de arranque** terminada en 0 (`0x7151, 0x72c3, … 0x75f1 (índice 8), 0x76cf (9) … 0x8da9`). Ningún literal del código apunta a `0x25a00–0x25bb0` y ningún llamador alcanza `0x75f0`: lo consume el cargador/SO, ausente de la imagen. `0x75f0` es una rutina que **vuelve** (`pop {…pc}` en `0x76cc`), no un bucle: inicializa y, en `0x7654–0x765e`, si `0xcf14(0) == 1` llama `0x1b260` (único llamador) → `0x1b274: bl 0xcee6` (único llamador) → `0x1984e(0)`. Es **inicialización del arranque**: no se ejecuta en un disparo. **INFERENCIA** (el consumidor no está en la imagen): que la lista se recorre solo al arrancar, por ser la forma de las listas de inicialización y por el retorno de `0x75f0`.

## 2. Acciones 04–06, `0x2f`/`0x30` de S y reejecución — VERIFICADO

Tabla `0x28df0`: 04 `0x171a7`, 05 `0x171eb`, 06 `0x1725d`, **`0x2f` `0x17881`**, **`0x30` `0x178af`**. **CORREGIDO** respecto a R78 §2, que juntó «`0x17880/0x178af`» bajo `0x2f`: son dos acciones distintas (las secuencias `0x28dc5…` usan `0x30`).

| Acción | Espera | Resultado (emulado con Unicorn sobre los bytes reales) |
|---|---|---|
| 04 `0x171a6` | `S+0x44` bit 4 = 0: arma vigilancia `0x17924(3, 0x186a0)` y consulta `0x16718`; `0x16718` devuelve `0x241ca()` = **1** (stub `movs r0,#1`) | **avanza y sigue** (`0x1e4aa`); no retiene |
| 05 `0x171ea` | igual con `0x241ce()` = 0, copia `S+0x3f/0x40/0x41` y `0x241e0()` = **1** | avanza y sigue |
| 06 `0x1725c` | `0x241ce()` = 0 | avanza y sigue |
| `0x2f` `0x17880` | `0x1f01a`: avanza si `0x12240() == 0` (byte `[0x20002e10]` y palabra `[0x20002e24]`, estado del módulo de comunicación/pines que escribe `0x122b0`); si no, `0x16dc0` (vigilancia `S+0x18/0x1c`) y, sin vencer, **retiene** y rearma el temporizador a 200 µs (`0x1e3d2(m,0,0xc8)`) | `fl=0` avanza; `fl≠0` retiene + 200 µs |
| `0x30` `0x178ae` | lee `[S+8]` (`S = 0x200036d8`): si = 0 avanza (`0x1e4aa`); si ≠ 0 llama `0x1e3d2(m, 0, [S+8])`: rearma el temporizador con ese plazo y **avanza y cede** (no retiene) | no lee `S+0x32/0x48`; **no se localizó ningún almacén a `S+8`** (seguimiento de registros sobre todas las funciones con literal de S, incluidos derivados), luego con la imagen sola el plazo es 0 (INFERENCIA; un `memset`/copia de estructura no se vería) |

Los ayudantes `0x241ba/c2/ca/ce/dc/e0` son **stubs de cuatro bytes** (`movs r0,#k; bx lr`; k = 0,0,1,0,1,1) en esta imagen, por eso 04–06 nunca retienen aquí; con `S+0x44` bit 4 = 1 también avanzan. La vigilancia de 04–06 (`0x17924`: `S+0x64/68/6c`, `0x186a0·0x1388` ticks ≈ 500 s si `0x93e6` cuenta µs, INFERENCIA de la unidad) nunca se evalúa porque no hay retención.

**Escrituras P4B–P4E:** cierres exactos (18, 18, 13, 62 y 5 funciones) **sin** `0x1ecec`, `0x20c90`, `0x20cb2`, `0x20cd4`, `0x20d00`, `0x20d26/0x20e0e/0x20e98`, `0xd18e`. 04, 05, 06 y `0x30` no contienen tampoco `0xd116`/`0x51c0`/`0x16558`. Solo `0x2f` alcanza P4B (`0x22c ← 1`, `0xd116 → 0x51c0`), **únicamente** por `0x16dea: bl 0x16558` (único llamador en su cierre) tras `[S+0x18] − t > [S+0x1c]`: la misma ruta de error de R78 (≈145 s), no un disparo normal.

**Retardo con T:** ninguna de las cinco lee `S+0x32` ni `S+0x48` (prueba por función con literal de S). Sus plazos son constantes (salvo `0x30`, con `[S+8]` sin escritor localizado) (200 µs de sondeo, vigilancia de ≈145–500 s) o dependen de la bandera externa de `0x2f`.

**Quién reejecuta S tras la primera pasada — no está en la imagen (SOLO MEDIBLE/NO VERIFICABLE estáticamente):**
* `0x178e6` (ejecutor: `0x1e5f2` + `0x1e33e(0x28dd4)`) y `0x17900` tienen 14 y varios llamadores, todos arrancadores `0x16c04–0x1708e`, sin punteros a `0x178e6/7` ni `0x17900/1`; el descriptor `0x28dd4` solo lo cargan esos arrancadores y el ejecutor. Ni el bucle de captura `0x1961c` ni la acción `0x0a` (`0x16d0c → 0x17900 → 0x1e16e`) vuelven a ejecutar S: solo comprueban si terminó.
* Los temporizadores de S son los bytes `07 0d 0d 06` del descriptor (`0x28dd4+0x18`): el 7 es temporizador de hardware (`0x1e192 → 0x24c24 → 0x9168`) y `0x1e3d2` lo programa a 200 µs; el `0xd` es no-op (`0x1e1ba–0x1e1d0`). La interrupción de ese temporizador se registra en la **tabla de vectores del cargador (`0x0000–0x41ff`, ausente)**; desde la imagen no se puede ver qué llama a S de nuevo. Medible en cámara (traza de la IRQ del temporizador 7 durante un disparo).

## 3. ¿Cambia la conclusión de R74/R75? — No

* El firmware **no** introduce ninguna pérdida ni retardo dependiente de la separación `B − A`: ninguna acción de la máquina S (04–06, `0x2f`, `0x30`, ni 09/0a/13/14 de R78) lee `T` (`S+0x32/S+0x48`), ni escribe P4C/P4D/P4E; P4B solo por la ruta de error de vigilancia de ≈145 s.
* Los dos handlers de tabla restantes (`0x295c4` evento `0x16`, `0x25b70` arranque) quedan identificados y fuera de la captura. Lo único que podría ejecutarse entre la preparación y B es el evento `0x16` si el host manda un paquete `0x31` con el bloque `0xa` en ese estado: es un reinicio del control que impone el host, sin dependencia de `B − A` conocida.
* **Pendiente solo de cámara** (sin ID nuevo; ya cubierto por la medición de E26-R75-T0): traza de si llega algún `0x31`/evento `0x16` durante un disparo y de la IRQ del temporizador 7 que reejecuta S; la imagen no contiene ni el vector ni el emisor de paquetes.

| Resto de R78 | Estado |
|---|---|
| Handler 3 (`0x295c4`) | **VERIFICADO/CORREGIDO**: evento `0x16` de la cola 2, publicado por `0x1bc12` tras un paquete `0x31`; fuera de la captura |
| Handler 4 (`0x25b70`) | **VERIFICADO**: paso de arranque (lista de 22); consumidor fuera de la imagen (**INFERENCIA** de «solo al arrancar») |
| Acciones 04–06, `0x2f` | **VERIFICADO**: 04–06 avanzan siempre (stubs); `0x2f` espera bandera externa; sin P4C–P4E ni T |
| Reejecución de S | **SOLO MEDIBLE**: IRQ del temporizador 7, vector en el cargador ausente |
