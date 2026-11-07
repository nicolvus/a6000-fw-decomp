# E26-R75 — Verificación independiente de R74 y de la secuencia A/B de Darwin (07-11-2026, estático)

Revisa [R74](e26-r74-conclusion-final-efcs-negro.md) con Capstone sobre `av-cam.bin` (base `0x43541000`) y `darwin_core.bin` (base `0x4200`) 3.21, y con los 27 `backup_flash.bin` legibles de `analysis/camera-dumps/` (`pmca.backup.BackupFile`). Sin REA/Ghidra, sin cámara.
Prueba: `tests/test_e26_r75_verificacion_r74_darwin.py`. Contexto: [R66](e26-r66-bloques-darwin-en-nvram-1850000.md), [R67](e26-r67-eventos-a-b-p4c-p4e.md), [R68](e26-r68-auditoria-r65-r67.md), [R70](e26-r70-cierre-pendientes-r65-r69.md).

Etiquetas: **VERIFICADO** · **CORREGIDO** · **INFERENCIA** · **SOLO MIDIENDO**.

## 1. Afirmaciones de código de R74 §2

| Afirmación de R74 | Estado | Evidencia |
|---|---|---|
| Compuerta `[obj+0x15]` en `0x438417b6` (`ldrb r2,[r0,#0x15]; cmp r2,#1; bne 0x438417c6`) y, si ≠ 1, `record+0x64 = record+0x1c` con `+0x68 = +0x6a = 0` | **VERIFICADO** | `0x438417b4 ldr r0,[sp,#0x48]`; `0x438417b6/b8/ba`; `0x438417c6 ldrh r2,[r5,#0x1c]`, `strh.w r3,[r5,#0x68]`, `strh.w r3,[r5,#0x6a]`, `str r2,[r5,#0x64]` (r3 = 0). Con `=1` va a `bl 0x4383fa40` |
| El objeto es la propiedad `0x30097` | **VERIFICADO** | `0x4384109a ldr.w r2,[r8,r3]` con `r3 = 0x16b8`, `r8 = 0x43841088 + 0x7dde5c = 0x4401eee4`; `[0x4402059c] = 0x43f72b62`; `str r2,[sp,#0x48]` en `0x438410a0`. `0x43ff329c` y `0x4402059c` son los dos únicos punteros a `0x43f72b62`; solo hay un hueco GOT (`+0x16b8`) |
| `+0x15 = 0` (y `+0 = 1`) en todos los volcados | **VERIFICADO** | `getProperty(0x30097)` = 32 B idénticos en los 27 volcados: `0101001000490000 0001010100000000 0000001700000000 0000001500000015`; `[0] = 1`, `[0x15] = 0` |
| «13 referencias a `0x30097+0x15`, todas lecturas» | **CORREGIDO (número); VERIFICADO (todas lecturas)** | Son **14** lecturas `ldrb [obj,#0x15]` en 8 funciones: `0x4383fd86`, `0x4383fdd2` (`0x4383fd6c`); `0x4383fe30`, `0x4383ff5e` (`0x4383fe10`); `0x43840168`, `0x43840196`, `0x438402c0` (`0x43840150`); `0x43840332`; `0x438403fa`; `0x438407b6`; `0x43840fd8`; `0x438410a4`, `0x438412be`, `0x438417b6` (`0x43841070`). R74 no contó una, probablemente la del prólogo `0x438410a4`. Ningún `strb` tiene como base el objeto: los 15 `strb …,#0x15` de las funciones que cargan el hueco escriben otras estructuras (paquete de salida `r4 = [sp+0xc8]` en `0x438414fa`/`0x43841574`; `0x43845a76` sobre un puntero devuelto por `0x43859ac4` = constante `0x743b8c`; etc.) |
| Umbral `u16[0x3012b] = 0x1760` en `0x43842158` | **VERIFICADO** | Tabla BK4: índice 43 ↔ id `0x3012b` ↔ `0x43f73042`; GOT `0x43842350` apunta ahí; `getProperty(0x3012b)[:2] = 60 17` = `0x1760` en los 27 volcados. Se usa en `0x438421ac–0x438421b4` (`Tv > u16` → `bls`) |
| «Por qué no actúa con EFCS» (clase 3 a cualquier T) | **VERIFICADO el código; precisado el motivo** | Ver abajo |

**Por qué no actúa el umbral (precisión).** `0x43842158` solo se llama desde `0x438412d0` y solo si `[obj+0x15] = 0` (`0x438412be ldrb r5,[r3,#0x15]; cbnz r5,0x438412e8`), o sea en el firmware oficial. Dentro:

* Rama mecánica (`[cap+0x4bc] & 0xe0 ≠ 0`): clase 1 o 5, nunca depende de `0x3012b`.
* Rama electrónica: **el umbral solo se consulta si `[cap+0x41c] == 1` y `r3[+2] == 0`** (`0x4384219e–0x438421b6`; `r3` es el 4.º argumento, de otra función). Entonces clase 3 si `Tv ≤ 0x1760`, y clase 1 si es más rápido (la clase se guarda en `0x43eefb7c`).
* Si `[cap+0x41c] ≠ 1` → clase 3 (`0x438421e2`); si `r3[+2] == 1` depende de `[cap+0x38c]` (1 o 3); si `≥ 2` → clase 3.
* **CORRECCIÓN menor a R74 §2:** R74 atribuye la clase 3 fija a `cap+0x41c ≠ 1`. Es una de **tres** vías posibles (`cap+0x41c ≠ 1`, `r3[+2] ≥ 2`, o `r3[+2] = 1`); ninguna depende de T. Lo que descarta la rama del umbral es el dato medido: `pkt[1] = 0x02` a **1/500** (más rápido que 6 ms: con la rama del umbral saldría clase 1) y a 1/125. `pkt[1]` sale de `0x43841366`: clase 3 → `0x02` (o `0x42` si `[0x75a17b+…] == 1`), clase 1 → `0x00`/`0x40`. La conclusión no cambia.
* **Límite:** con un único disparo más rápido que 6 ms no se prueba que la clase sea constante en todo T, solo que en esa captura no pasó por la rama del umbral. El código de las tres vías alternativas es independiente de T, así que basta.

**Límite de «todas lecturas».** El rastreo es lineal sobre las 76 funciones que cargan el hueco `0x16b8` (el único camino a `0x43f72b62`). No cubre escrituras genéricas del sistema de backup por la tabla `0x43ff329c`, que es justamente quien rellena la imagen desde la NVRAM (por eso el valor es el de los volcados).

## 2. Darwin: ¿puede el firmware producir una pérdida que dependa de `B − A`?

### 2.1 Cómo se ejecutan A y B (VERIFICADO)

`0x18d6e` arma A y B con las interrupciones cortadas (`cpsid i … cpsie i`, `0x18e7e–0x18e88`, `0x18ec6–0x18ed0`) y luego espera con `0x203ae`.

| Rama | Llamadas |
|---|---|
| corta (`S+0x48 < −150`) | `0x198ee(retardo)` → `0x202f2(retardo≠0)` (A retardado) y `0x19932` → `0x2041e(0)` (B inmediato) |
| larga (`> 50`) | `0x198bc` → `0x202f2(0)` (A inmediato) y `0x19948(retardo)` → `0x2041e(retardo≠0)` (B retardado) |

El «retardo» solo cambia **cuándo** corre el cuerpo; los cuerpos son idénticos en todas las ramas:

* Retardado: `0x202f2`/`0x2041e` con argumento ≠ 0 arrancan en la máquina 2 (descriptor `0x29dc8`, temporizador id `0xc`) la secuencia `01 03 06 02 07` (A: espera `[S+0x14c]` µs, `0x20a8a` = `0x20cb2`+`0x16e68`+`0x202c2`) o `01 04 06 07` (B: espera, `0x20aa4` = cuerpo de B y `1e150` de la secuencia de la máquina 0 + `0x20c06(0)`).
* A: `0x202c2` (lista de la máquina 3, descriptor `0x29de4`, temporizador `0xd`) **solo si `[0x20003cd8+0x20]` ∈ {2,3,4}**: `t=2` → secuencia `00`; `t=3,4` → `01 02 03 04 05`; otro `t` (el valor esperado, 0): no hace nada. Luego `0x20cb2` (P4D ← 0 si tipo ∈ {1,2}), `0x16e68` (P4C ← 0; `S+0x10 = 0x93e6()`).
* B: `0xd116(1<<22)`, `0x201b0(0)` (solo anota `S+0x150`), `0x16fe2` (**función vacía**: `0x1ed20` es `bx lr`; igual `0x16ff4`), `0x20408` (puerto `0x30`, solo si `t ∈ 1..4`), **`0x20d00` (P4E ← 1 dentro de `cpsid`/`cpsie` vía `0x5c9e/0x5c88`; `0x210c0`: `S+0x180 = 0x93e6()`)**, `0x20c4a` (contador en `0x20000620`), secuencia `02 04 06 10 11` de la máquina 0 (descriptor `0x29d90`, temporizador `0xb`, `0x29d90−0x12 = 0x29d7e`) y `0x20c06(0)`.
* `0x20c74()` = `([0x200002c0] ≠ 0 ? [0x20000050] : 0) & 7` ∈ {0,1,2,3}, confirmado en `0x1b080/0x1b0e0`.

Las tres máquinas que usan A y B tienen **temporizadores distintos** (`0xb`, `0xc`, `0xd`, byte `+0x1b` del descriptor; las máquinas 0 y 1 comparten estado y temporizador, pero la 1 no se arranca aquí), y las dos cabezas (`0x202f2`, `0x2041e`) escriben el mismo `S+0x14c` con el mismo valor. No hay variable ni recurso que A y B se pisen.

### 2.2 Duración del pulso P4E y valores (VERIFICADO + MEDIDO)

Secuencia de B: id 2 (`0x20734`) → id 4 (`0x207e8`) → id 6 (`0x2083c`) → id `0x10` (`0x20a4c`).

* `0x20734` termina con `1e3d2(…, r2 = r8)` y `r8 = [B+0x32]·100`: espera `B+0x32·100 µs`.
* `0x207e8`: **P4E ← 0** (`0x20cd4`) y espera `([B+0x31] − [B+0x32])·100 µs` (`0x207fc–0x2080a`). `0x207be` (id 3) es el mismo cuerpo, usado por otras secuencias (`01 03 05 10 11`).
* `B+0x30/0x31/0x32` = `0x50/0x64/0x32` en **los 27 volcados** (bloque NVRAM `0x1850001`, offsets `0x30..0x32`): bytes `0x28..0x3b` = `0000000000000000 50 64 32 00 dc01 fd01 00000000`.
* Resultado: **P4E dura `0x32·100 = 5,0 ms`** y la secuencia completa `0x64·100 = 10 ms`. `B+0x30·100 = 8 ms` es la espera tras P4D ← 0 (`0x209d0/0x209f2`). `B+0x34/0x36` = `0x01dc/0x01fd` (476/509) son los umbrales de la FSM ADC (`0x2089c`).
* Consecuencia para `B − A`: en la rama corta, A cae siempre dentro del pulso de P4E (A llega entre 0 y 3,15 ms después de B, el pulso dura 5 ms); en la larga, P4E sube tras A. A cae siempre **antes** de la bajada de P4E (`B + 5 ms`) en ambas ramas. Es una **propiedad de la programación**, no una interacción: P4E ← 0 no la pisa nada.

### 2.3 Rearme `0x28dc5` y FSM ADC (VERIFICADO el código; las esperas son de hardware)

* Secuencia `30 0f 10 2f 14 15 …` en la máquina `S` (descriptor `0x28dd4`): `0x178ae` (id 0x30) mira `[S+8]`; `0x173d2` (id 0x0f) compara `0x93e6() − [S+0x10]` con `0x3a98` (15 ms) y emite el evento de error 3 si lo supera; `0x17418` (id 0x10) y `0x17880` (id 0x2f) esperan condiciones de pines (`0x1eff6` → `0x12260/0x122b0`, `0x1f01a` → `0x12240`) en pasos de 200 µs; id 0x14 (`0x175ea`) → `0x16e7a`: P4C ← 1 y `S+0x10` = ahora.
* El plazo de 15 ms cuenta desde **el último cambio de P4C** (preparación `0x16e7a` o A `0x16e68`), no desde B. P4C ← 1 ya está a 1 desde la preparación (R70 §2), así que si el rearme llega antes de un A retrasado, A baja igualmente (R70); si llega después, P4C hace un pulso 1→0→1. **Cuándo llega el rearme depende de pines (hardware)**: estáticamente no se puede ordenar frente a A.
* FSM ADC (`0x2089c`, máquina 1): mide `([S+0x180] − ahora)/5` (tiempo desde B, `S+0x180` lo sella `0x210c0` en B) y marca bits en `S+0x154` (`0x206be/0x20692`, `0x208fc/0x2093e/0x2098a`) y tiempos en `S+0x156/0x158/0x15a`. `S+0x154/0x156` solo se copian al paquete de estado que se envía al BIONZ (`0x1c398/0x1c39e`); no puerta ni retardo de A o B. No hay lector que mueva P4C/P4D/P4E según ellos.
* Rutas que bajan P4E antes de tiempo: `0x206ec` (P4D, P4E y P4C ← 0, parada de las tres máquinas) solo por `0x19b8e` (comando de parada, no por A/B); `0x1f68a` (acción de otra máquina, `0x298bc`): P4D ← 1 y P4E ← 0, no está en las secuencias de captura ni de B.
* P4D soltado tras B: ocurre en la rama corta (A retardado sigue a B) sin ninguna cancelación: P4D ← 0 y P4E ← 1 son escrituras independientes de puertos distintos (`0x51c0`, alias bit-band).

### 2.4 Conclusión sobre el firmware (VERIFICADO)

1. **No existe en Darwin ningún mecanismo que haga depender la acción de A o de B (qué escribe, con qué anchura, en qué orden interno) de `B − A`.** Cuerpos idénticos en las dos ramas, máquinas y temporizadores separados, P4E de anchura fija (5,0 ms), sin lectores de los tiempos medidos que cierren un lazo, y manejadores de microsegundos (`cpsid` solo alrededor de la escritura de P4E).
2. Lo único que depende de la separación es **el instante físico** de cada flanco, ya programado por `0x18d6e`.
3. Dos puntos no decidibles en estático, ambos de hardware: el momento del rearme (P4C ← 1) respecto a A (esperas de pines), y el valor de `[0x20000050]` (R74 §3).

## 3. Corrección de la lectura de R74 §4: la pérdida no se ata a A, se ata al retardo de B

R74 §4 describe la dependencia como «la pérdida es constante mientras B ocurre antes de A y decrece con `B − A`» y la lee como transitorio **ligado al evento A**. Con los mismos datos, sustituyendo `B − A` por `B − t0` (`t0` = instante en que `0x18d6e` arma A y B: A en la rama larga, B en la corta; `B − t0 = máx(B − A, 0)`):

| T (ms) | `B − A` | `B − t0` | δ normalizada |
|---|---|---|---|
| 1,33 | −2,07 | 0 | 1,24 |
| 2,00 | −1,40 | 0 | 1,32 |
| 2,86 | −0,54 | 0 | 1,30 |
| 4,00 | +0,57 | 0,57 | 1,29 |
| 5,00 | +1,57 | 1,57 | 1,04 |
| 8,00 | +4,57 | 4,57 | 0,17 |

* En la rama corta A se mueve 2 ms respecto a B (de −2,07 a −0,54) y la pérdida no cambia: **la posición de A no influye**. En la larga A no se mueve (`t0`) y la pérdida cae al retrasar B.
* El modelo «función de `B − t0`» (constante 1,25–1,3 ms con B inmediato, nula pasados ≈ 4–5 ms) explica los tres puntos de la rama corta y los de la larga sin necesitar comportamiento especial para `B − A < 0`; el de `B − A` obliga a una meseta en el lado negativo.
* **CORREGIDO:** el transitorio no está ligado al flanco A (P4C ↓ / P4D ↓) sino al tiempo que B se separa del arranque de la secuencia (preparación y armado inmediatamente anteriores: P4D ← 1 de `0x20c90`, P4C ← 1 de `0x16e7a`, `0x1811a`). Es **INFERENCIA** sobre 6–7 puntos de R62; no distingue entre `t0` = armado y `t0` = preparación.
* Consecuencia práctica: los candidatos de R74 §4 («tensión entre imanes al soltar P4D en A», «P4C») pierden apoyo; gana la hipótesis de que la segunda cortina responde 1,25 ms antes de lo previsto si P4E sube pronto después del encendido de P4D/P4C de la preparación. La compensación de R74 §6.2 (adelantar A) sigue siendo válida como parche de exposición, pero actúa sobre A, que no es la variable física. Si se compensara, lo coherente sería **retrasar B** (`B+0x8a`, rama larga) o actuar sobre `G+0x42`; en la corta, retrasar B respecto a `t0` no es posible (B es inmediato), así que solo queda adelantar A.

## 4. Qué solo se decide midiendo, y por qué

| Pregunta | Por qué no es estática |
|---|---|
| Momento real del rearme (P4C ← 1) respecto a A y B | Espera `0x1eff6/0x1f01a`: lectura de pines del MCU |
| `[0x20000050]` (tipo de mecanismo) | Lo escribe el cargador `0x0000–0x41ff` (R72), no incluido en ningún volcado |
| Intervalo entre P4D ← 1 / P4C ← 1 de la preparación y `t0` (decide si la variable es `B − t0` o `B − prep`) | Depende de esperas hardware y de cuándo el BIONZ manda la orden; haría falta analizador lógico en P4C/P4D/P4E (o 2 puntos más de δ con `B − t0` mayor, sin cambiar la rama) |
| Pieza física concreta (cortina, imán, flex, alimentación) | No hay dato de firmware que distinga |

## 5. Estado

* R74 §2: **VERIFICADO**, con dos precisiones (14 lecturas; la clase 3 fija tiene tres vías posibles, no una).
* R74 §3 (Darwin sin dependencia de T): **VERIFICADO y ampliado** (§2).
* R74 §4 lectura «ligada al evento A»: **CORREGIDO** (§3). La causa sigue siendo física (R74 §1 vigente).
* Nuevo pendiente **E26-R75-T0**: medir con analizador lógico P4C/P4D/P4E (o 2 disparos más con B−t0 > 4,5 ms y > 2 ms) para fijar qué referencia usa la pérdida; sin cámara no se avanza.
