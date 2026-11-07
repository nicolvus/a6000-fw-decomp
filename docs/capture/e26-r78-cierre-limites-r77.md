# E26-R78 — Cierre de los límites de R77: intérprete de secuencias, acciones 09/0a/13/14 y alcance de `0x1fee2` (07-11-2026, estático)

> **Nota R79 (07-11-2026):** los restos de §2 y §3 quedan cerrados en [R79](e26-r79-cierre-restos-r78.md). Cambios: (1) `0x295c4` no es de la tabla `0x294f8`: es la **entrada `0x16` de la tabla de eventos `0x29514`** (despachador `0x1ba00`, cola 2 de la tarea `0x7de2`), publicada por `0x1bc12` tras un paquete `0x31` del host; `0x25b70` es una **lista de 22 pasos de arranque**; ambos fuera de la captura; (2) la acción `0x2f` es `0x17881` y la `0x30` `0x178af` (no «`0x17880/0x178af`» juntas); 04–06 de S avanzan siempre (ayudantes stub), `0x2f` espera una bandera externa, ninguna lee T ni escribe P4C–P4E; (3) quién reejecuta S queda fuera de la imagen (IRQ del temporizador 7, vector en el cargador). La conclusión de R74/R75 no cambia.

Cierra los tres límites que dejó [R77](e26-r77-preparacion-p4d-orden-temporal.md) (§2 fila 7, §4 «Límites» y §1 «arranque de esos tres»). Capstone y Unicorn sobre `darwin_core.bin` 3.21 (base `0x4200`). Método de [R70](e26-r70-cierre-pendientes-r65-r69.md) §1. Prueba: `tests/test_e26_r78_limites_r77.py`. Sin REA ni cámara.
Etiquetas: **VERIFICADO** (bytes/instrucciones/emulación) · **CORREGIDO** · **INFERENCIA** · **SOLO MEDIBLE**.

## 1. Semántica de `0x1e4c2`, `0x1e4f6`, `0x1e4aa` — VERIFICADO

Las tres son funciones de 6 instrucciones que reciben `r0 = m`, el **registro de paso de 20 bytes** que `0x1e33e` pone a 0 en la pila antes de cada acción (`0x1e36e–0x1e37c`) y que pasa luego a `0x1e234(desc, m)` (`0x1e3c2–0x1e3c6`). Solo tocan la media palabra `m+0x10`:

| Función | Instrucción decisiva | Efecto sobre el paso |
|---|---|---|
| `0x1e4aa` | `orr r0, r0, #0x40` (`0x1e4b4`) | **avanzar el índice y encadenar**: la nueva acción corre en la misma pasada |
| `0x1e4c2` | `orr r0, r0, #0x80` (`0x1e4cc`) | **retener**: no avanza; la acción se repite en la pasada siguiente |
| `0x1e4f6` | `bic r0, r0, #0x40` (`0x1e500`) | como `m` llega a 0 es un no-op: **avanzar y ceder** (fin de pasada) |

Cómo lo lee `0x1e234` (VERIFICADO por bytes): sin puntero de secuencia o con `seq[idx] ≥ n` devuelve 0 y no avanza (**terminar**: la secuencia acaba al llegar a `id == n`; `0x1e33e` no llama a la entrada con `id == n`). Bit `0x80` (`0x1e25c: lsls #0x18; bmi 0x1e2b6`) salta el avance; bit `0x100` busca hacia delante la entrada con id `m[0xc]` (`0x1e4da`); sin bits, `idx++` y, si `seq[idx] > n`, registra error 3 (`0x1e32e`). Después, bits 0–2 arrancan y 3–5 paran temporizadores (`0x1e192/0x1e1d2/0x1e0e4`; `0x1e3d2/0x1e424` rellenan `m[0],m[4],m[8]` y esos bits), y el bit `0x40` (`0x1e322: lsls #0x19; bpl; mov.w r8,#1`) hace devolver 1, con lo que `bne 0x1e346` repite el bucle de `0x1e33e`.

**Emulación (Unicorn, intérprete real `0x1e33e`, tabla mínima en RAM con las tres funciones reales):** `[C,C,S,C,fin]` → pasada 1 ejecuta `C,C,S` y queda en índice 3; pasada 2 ejecuta `C` y llega a id terminal; pasada 3 no ejecuta nada. `[H,C,fin]` → `H` en las tres pasadas, índice 0 (no avanza). `[S,S,C,fin]` → una acción por pasada.

**Quién repite las pasadas:** la secuencia de captura corre en un bucle ocupado: `0x1961c` llama a `0x1e33e` (`0x19684`), informa (`0x1e5f2`) y repite mientras `0x1e16e(0x28fdc) == 0` (`0x19696–0x1969e`), es decir hasta que la acción actual sea el id terminal `0x31`. **Retener = ese bucle reitera la misma acción.**

**Esperar/reintentar con plazo (ejemplo real, acción `0x0f` de S, `0x173d2`, emulada):** con `t = 0x93e6()` (devuelve `~contador`, decrece) y `e = [S+0x10] − t` (µs desde que P4C subió), si `e < 15000` llama a `0x1e4c2` y `0x1e3d2(m, 0, 200)`: **retiene y rearma el temporizador del descriptor a 200 µs**; si `e ≥ 15000` registra error 3 (`0x1edd4`) y salta a `0x1e4aa` (avanza y sigue). Emulado: `e = 0, 5000, 14999` retiene (índice 0, temporizador 200); `e = 15000, 20000` avanza con error 3.

**Consecuencia sobre R77 §2 fila 6 (CORREGIDO, matiz):** con EFCS las acciones 02, 03, 04, 06 («inertes», `0x196a2 = 0`) **no retienen**: terminan en `0x1e4f6` (02 `0x18608`, 04 `0x18656`) o en `pop {r4, pc}` (03 `0x18634`, 06 `0x18676`), es decir avanzan y ceden. Retienen solo con `0x196a2 ≠ 0` (03 si `0x19974()==0`, 06 si `0x199b4()==0`: `b.w 0x1e4c2`).

## 2. Acciones 09, 0a, 13 y 14 de `0x28f88` (descriptor `0x28fdc`, tabla `0x28ff8`) — VERIFICADO

Las cuatro arrancan o esperan la **máquina S** (`0x28dd4`, estado `0x200036d8`, tabla `0x28df0`, n = `0x32`), no máquinas nuevas:

| Acción | Función | Qué hace | Fin de paso |
|---|---|---|---|
| 09 | `0x186f1` | `arg = S+0x42` bit 3; si `S+0x46` bit 0 → `0x16cd8` (secuencia `0x28dae`), si no `0x16ca4` (`0x28da1`): `S+0x14` bit 5 ← arg, `S+6 ← 2`, `0x1e150` y `0x178e6` (informa y ejecuta **una pasada** de S) | `0x1e4f6`: avanza y cede |
| 0a | `0x1871f` | `0x16d0c → 0x17900 → 0x1e16e(0x28dd4)`: ¿acción actual de S ≥ `0x32`? Sí → `bne 0x18676` (avanza y cede); no → `0x1e4c2` | **retiene hasta que S termina** |
| 13 | `0x1896b` | `S+0x46` bit 0 → `0x16da2` (secuencia `0x28d8b` = `0d`) si no `0x16d84` (`0x28d8f` = `0d 1d`); `S+6 ← 5/3`, `0x178e6` | `0x1e4f6` |
| 14 | `0x1898d` | `0x16d9e → 0x17900` (S terminada) | no → `0x1e4c2` (retiene); sí → `0x1e4aa` (avanza y sigue) |

Las secuencias `0x28da1` y `0x28dae` son idénticas en ids: `04 05 06 07 08 2f 09 0a 2f 0b 2f 0c` (funciones: `0x171a7 0x171eb 0x1725d 0x172a1 0x172b5 0x17880/0x178af 0x172e5 0x172f9 0x17329 0x1736b`). `0x178e6` es el único ejecutor de S (14 llamadores, todos de arranque, sin punteros).

**Escrituras en P4B–P4E.** Cierre estático (llamadas directas y secuencias arrancadas) desde las cuatro acciones y desde todas las acciones de S que arrancan (218 funciones desde 09, 125 desde 13; 0a y 14 no llaman a nada más que `0x17900`):

* Ninguna alcanza los escritores de **P4C** (`0x1ecec`), **P4D** (`0x20c90`, `0x20cb2`), **P4E** (`0x20cd4`, `0x20d00`) ni los de puertos por registro `0x20d26/0x20e0e/0x20e98` (prueba).
* **Único alcance: P4B (`0x22c ← 1`) por la ruta de error de vigilancia, a 6 niveles:** acción `0x0a` de S (`0x172f9`, 09) o `0x1d` (`0x175fd`, 13) → `0x16dc0` → `0x16558` → `0xd380` → `0xd116(0x40, 1)` (`0xd3aa–0xd3ac`) → `bl 0x51c0` con `r0 = 0x22c` (`0xd176–0xd17a`) si `r4 & [0x20002bd0+8] ≠ 0`. Las máscaras `0x5407f/0x5444f` (y `-1`) contienen `0x40`; solo queda condicionada la rama `0x1bdd0() ≠ 0` (máscara `0x800`). `0x16dc0` solo llama a `0x16558` si `[S+0x18] − t > [S+0x1c]`, con `[S+0x1c] = 0x7148·0x1388` (armado en `0x16df8`): ≈ 145 s si `0x93e6` cuenta µs (INFERENCIA de la unidad, convención de R70). **No ocurre en un disparo normal.** Corrige la cota de R77 («sin escrituras P4B–P4E a ≤ 4 niveles»): hay un camino a 6 niveles, solo de error.

**Retardo dependiente de T.** En ese cierre no hay ninguna lectura de `S+0x32`; `S+0x48` se lee una sola vez, en `0x18394` (volcado de estado a un paquete, `[r0+0x50]`, vía `0x1edd4 → 0x1ed72 → 0x1ed30 → 0x18366`, usado por las acciones de log 09/0f de S). `0x182d8` (lector de `G+0x42`) y `0x1961c` no están en el cierre. **Respuesta: ninguna de las cuatro introduce retardo dependiente de T antes de la acción `0x1f`.** Sí introducen una **espera**: 0a/14 retienen la lista de captura hasta que S llega a su terminal; la duración la fijan condiciones de hardware y temporizadores: acción 8 espera el pin `0x0d` (tabla `0x29784`, índice 1), `0x0a` el `0x15` (índice 2) y `0x0b` el `0x16` (índice 7, `0x122b0`), sondeados cada 200 µs (`0x1e3d2`) con vigilancia; 04–06 y `0x2f` usan otros ayudantes (`0x16718`, `0x17906/0x17924/0x179d4`, `0x1f01a`) que no se desglosaron. **SOLO MEDIBLE:** la duración real de S (09→0a), y quién reejecuta S tras la primera pasada (temporizador de hardware; no se siguió su ISR).

## 3. `0x1fee2` ← `0x1984e`: cadena completa — VERIFICADO con CORRECCIÓN

`0x1fee2` tiene **un único llamador**, `0x19880` dentro de `0x1984e`, y ningún puntero (`0x1fee3` ausente). `0x1984e` tiene cuatro llamadores en tres puntos de entrada y ningún puntero. Cadenas completas hasta el origen:

1. **Orden BIONZ `0x60`:** tabla de órdenes `0x2a39c` (95 entradas de 8 bytes, todas con `0x1bfb3`) → `0x1bfb2` → `0x1bfb6: bl 0x1f362` (rango `0x40–0x9f`, si no `0xfe`) → `0x1f36a: b 0x1f0a0` (conmutador de órdenes) → `tbb` `0x1f0ec`, índice 8 → `0x1f22c: movs r0,#1` → `0x1f22e: bl 0x1984e` → `0x19880: bl 0x1fee2`.
2. **Orden `0x67`:** igual hasta `0x1f0a0` → `beq 0x1f202 → b 0x1f24e` → bucle `0x1f260: movs r0,#1; bl 0x1984e` (`0x1f262`), N veces (`[0x20000300+0x304]`) separadas por `[+0x305]·10000`.
3. **Tabla `0x295c4`:** puntero `0x1b137` → `0x1b136` → `0x1b138: bl 0x197ce` (`movs r0,#1; b.w 0x1984e` en `0x197d0`).
4. **Tabla `0x25b70`:** puntero `0x75f1` → `0x75f0` → `0x765e: bl 0x1b260` → `0x1b274: bl 0xcee6` (`movs r0,#0; b.w 0x1984e` en `0xcee8`).

**CORREGIDO respecto a R77 §1** («API de rearme / callback de temporizador, fuera de la captura»): `0x1984e` es la pasarela única, pero sus raíces son las órdenes `0x60/0x67` y **dos handlers de tabla** (3 y 4) que R77 no distinguió; «callback de temporizador» no está verificado. **Fuera de la captura:** el cierre estático desde las 0x32 acciones de `0x28fdc` (602 funciones), `0x1961c`, `0x190fc`, `0x1811a` y los descriptores `0x296f0` y `0x28dd4` **no contiene `0x1984e` ni `0x1fee2`**. **Límite abierto:** no se resolvió cuándo se invocan los handlers 3 y 4 (la entrada `0x295c4` cae en la tabla `0x294f8` del descriptor `0x1a050` con campo `0x36b`, mientras las secuencias de modo `0x29388–0x293dd` solo usan ids `< 0x3c`; `0x25b70` pertenece a una lista de punteros `0x7151…` sin literal consumidor, probablemente del cargador `0x0000–0x41ff`, ausente). Por tanto «`0x1fee2` no se alcanza desde la captura» es VERIFICADO por llamadas directas y secuencias; el despacho por tabla de 3 y 4 queda **NO VERIFICADO**.

## 4. Estado

| Límite de R77 | Estado |
|---|---|
| Semántica de `0x1e4c2/0x1e4f6/0x1e4aa` | **VERIFICADO** (bytes + emulación): retener / avanzar y ceder / avanzar y seguir |
| 09/0a/13/14: P4B–P4E | **VERIFICADO** sin P4C/P4D/P4E; P4B solo por error de vigilancia (6 niveles) |
| 09/0a/13/14: retardo con T | **VERIFICADO**: ninguno; espera de hardware en 0a/14 (**SOLO MEDIBLE**) |
| `0x1fee2` solo por rearme | **VERIFICADO** (pasarela `0x1984e`), **CORREGIDO** (4 raíces) |

No altera la conclusión de R77 sobre E26-R75-T0 (P4D ← 1 tras el armado, sin T); añade que entre 09 y la acción `0x1f` hay una espera de hardware independiente de T que solo se mide.
