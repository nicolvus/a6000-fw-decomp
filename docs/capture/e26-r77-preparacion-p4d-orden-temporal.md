# E26-R77 — Preparación, P4D y orden temporal hasta B (07-11-2026, estático)

> **Nota R78 (07-11-2026):** los tres límites de §4 quedan cerrados en [R78](e26-r78-cierre-limites-r77.md). Cambios: (1) las acciones 02/03/04/06 «inertes» con EFCS **avanzan y ceden**, no retienen (fila 6 de §2); (2) 09/0a/13/14 arrancan y esperan la máquina S (`0x28dd4`), sin escrituras en P4C/P4D/P4E y sin retardo con T; P4B solo por la ruta de error de vigilancia a 6 niveles (corrige «≤ 4 niveles»); (3) `0x1fee2` solo se alcanza por `0x1984e`, pero esta tiene 4 raíces (órdenes BIONZ `0x60/0x67` y dos handlers de tabla), no solo «API de rearme/temporizador».

Cierra lo que [R75](e26-r75-verificacion-r74-y-darwin-b-a.md) §3 dejó sin mirar («cuándo se activa P4D en la preparación») y acota **E26-R75-T0**. Capstone sobre `darwin_core.bin` 3.21 (base `0x4200`). Método de [R70](e26-r70-cierre-pendientes-r65-r69.md) §1 (descriptores y secuencias antes del descriptor) y [R67](e26-r67-eventos-a-b-p4c-p4e.md). Prueba: `tests/test_e26_r77_preparacion.py`. Sin REA ni cámara.
Etiquetas: **VERIFICADO** (bytes/instrucciones) · **INFERENCIA** · **SOLO MEDIBLE** (con el motivo).

## 1. Quién escribe P4D ← 1 (`0x20c90`)

`0x20c90` hace `0x20c74()`; si es 0 o 3 no escribe; si es 1 o 2 escribe `0x234 ← 1` (`0x20c96–0x20cac`). Tipo = `[0x20000050] & 7`; `0x1fe66` (clase) = el mismo byte `>> 4` si está en 1..5, si no 0 (`tbb` de `0x1fe7a`). **VERIFICADO.** EFCS (`S+0x31`) no se consulta dentro de `0x20c90`.

| Llamador | Función | Máquina (descriptor, estado) | Id | Condición propia |
|---|---|---|---|---|
| `0x1f694` | `0x1f68a` | P4D (`0x297c0`, `0x200037d8`; tabla `0x29868`) | 0x00 | incondicional; luego P4E ← 0 (`0x20cd4`) |
| `0x1f8a2` | `0x1f88a` | P4D | 0x0a | `0x1fd8c(1)==0` y clase ∈ {1,2} |
| `0x1f914` | `0x1f8fc` | P4D | 0x0d | `0x1fd8c(1)≠0` y clase ∉ {1,2} |
| `0x20154` | `0x2014c` | control (`0x29cf0`, `0x200037f8`; tabla `0x29d0c`) | 0x07 | tras temporizador `[0x200036d8+0x128]`; después espera `0x5dc0` = 24 ms |

Secuencias (VERIFICADO): P4D-A = `0x297c0−0x29` = `18 19 00 15 05 06 …` (arranca `0x1f396`, desde la acción 2 de la máquina de control, `0x20126`); P4D-B = `0x297c0−0x14` = `01 05 06 07 08 09 0a …` (`0x1f3b6`, acción 4, `0x2013a`). Control: S_a `0x29cf0−0x13` = `00 02 03 06 09` (`0x1fee2`), S_b `−0xd` = `00 04 05 06 09` (`0x1ff72`), S_c `−7` = `00 01 04 05 06 09` (`0x1ffce`), S_d `−0x18` = `00 07 08 09` (rama sin clase, las tres). **Los únicos que arrancan P4D-A/B son esas dos acciones y los únicos que arrancan el control son `0x1fee2/0x1ff72/0x1ffce`** (VERIFICADO: llamadores directos y sin punteros a esas funciones).

Arranque de esos tres:

| Entrada | Llamadores | Ocurre… |
|---|---|---|
| `0x1ffce` ← `0x199b8` | `0x191ec` (dentro de la acción 0x1f `0x190fc`, solo si tipo ≠ 3: `0x191e2/e4`), `0x18668` (acción 05, solo si tipo == 3), `0x17ac2` (preparación alterna `0x17a44` ← `0x18202`, ruta tipo 3) | tipo 1/2: **después** del armado |
| `0x1ff72` ← `0x19998` | `0x18642` (acción 04), `0x17e8e` (final de `0x17cee`, ráfaga `S+0x44` b0 = 1) — ambos exigen `0x196a2 ≠ 0` | **solo EFCS apagado** |
| `0x1fee2` ← `0x1984e` | API de rearme/callback de temporizador (E24-05: fuera de la captura) | no en la captura |

`0x196a2` = 1 si `S+0x31 & 3 == 0` o bit 6 activo; con EFCS activado (`0x02`) vale 0 (VERIFICADO). Las acciones 02, 03, 04 y 06 llaman a `0x196a2` y con 0 no ejecutan su cuerpo (02 sería `0x203b2 → 0x20d00`: P4E ← 1).

**Respuesta 1 (VERIFICADO):** con EFCS activado y tipo 1/2, P4D ← 1 **no** se ejecuta en la preparación (`0x1811a`) ni en ninguna acción de la lista anterior a la 0x1f. La primera ocasión es después del armado: `0x190fc` → `0x18fa0/0x18d6e` (arma A y B) → `0x1e6ba` → `0x191ec: 0x199b8(r4·100)` → control S_c (o S_d). Antes de la 0x1f solo hay **P4D ← 0** (acciones 1a/1d: `0x18bc4 → 0x198d6 → 0x2027c`: con argumento 0 llama a `0x20cb2`; con ≠ 0 arma temporizador). No hay P4D ← 1 «previo» que A deba bajar en esta ruta: la bajada de A (`0x20cb2`) es idempotente salvo que otra ruta (rearme, ráfaga, tipo 3, comandos de BIONZ) lo haya subido antes. Respecto a P4C ← 1: ocurre en `0x17cee` (primera instrucción, `0x17cf0 → 0x16e7a`), **antes** de `0x1961c` y por tanto antes de todo lo demás. Cond. por tipo: solo la escritura (`0x20c90`); la ruta de arranque ya bifurca por tipo 3. Cond. por EFCS: solo vía las compuertas `0x196a2` de 04 y `0x17e8e`.

## 2. Secuencia de preparación con EFCS (lista `0x1961c`)

Lista según `S+0x44` b0, `S+0x32`, `S+0x3c` (VERIFICADO): `0x28f88` (S+0x32 = 0 o `S+0x3c ∉ 1..4`) `02 09 03 04 0d 0a 0f 06 13 14 1a 1c 1f 20 30`; `0x28f98` y `0x28fba` (`b0=0`, S+0x3c = 1 / 2..4, idénticas) `02 09 03 04 0a 06 13 14 1a 1c 1f 21 22 20 30`; `0x28fa8` y `0x28fca` (`b0=1`) `0b 0c 07 17 05 08 15 16 18 19 1d 1e 1f 21 22 20 30`. El paquete observado (T022: `pkt[0x0c]=0`) usa `0x28f88`.

Orden estático (lista `0x28f88`, EFCS on):

| # | Dirección | Efecto | Puertos / esperas |
|---|---|---|---|
| 1 | `0x1811a` → `0xd116(1<<9)` | marca de evento | escribe P4B `0x22c ← 1` solo si la máscara coincide (`0xd170–0xd17a`) |
| 2 | `0x196b6`, `0x19816` | limpian bits de `S+0x44`; `0x2060c` | escriben puertos `0x14`, `0x2c`, `0x30` (no P4B–P4E) |
| 3 | `0x17f8c` | comprobación de ocupación | solo lecturas (`0x22c,0x230,0x234,0x204,0x11c,0x310,0x120,0x314,0x124`) |
| 4 | `0x17cee` | **P4C ← 1** (`0x16e7a`, `S+0x10` = ahora) | tras él, con `S+0x44` b0 = 0, sondeos de hardware en bucle (`0x1667a`, `0x16718`, `0x16932`, `0x199d0`, `0x16e26`) según flags |
| 5 | `0x1961c` | elige lista y arranca | — |
| 6 | 02 03 04 06 | inertes con EFCS (`0x196a2 = 0`) | ningún puerto |
| 7 | 09 0a 13 14 | arrancan/esperan otras máquinas (`0x16cd8/0x16ca4`, `0x17900`, `0x16da2/0x16d84/0x16d9e`) | sin escrituras P4B–P4E a ≤ 4 niveles; las acciones de esas máquinas no se siguieron |
| 8 | 0d 0f | compuertas por `0x196a2`, esperas de 500 µs (`0x1f4`) y consultas `0x165c8/0x16718` | sin escrituras P4B–P4E |
| 9 | 1a (y 1c) | calcula `S+0x48` (`0x19a12`, `0x18a2e`: resta `G+0x42`), `0x198d6` → P4D ← 0 / temporizador | puertos `0x298` (P56, `0x1b174`) y `0x1b308/0x1a738` (R70 §3) |
| 10 | 1f `0x190fc` | **armado** (`0x18d6e`, `cpsid`); `0x1e6ba`; `0x199b8(r4·100)` | ver §1; bucle `0x19204` espera `(0x19a3e()+1000)·5` desde el armado |
| 11 | A / B | A: P4D ← 0, P4C ← 0; B: P4E ← 1 … P4E ← 0 a +5 ms (R75 §2.2) | — |
| 12 | control S_c (o S_d) | espera `r4·100` µs (`0x1e3d2`), P4D-B → ids 0a/0d: P4D ← 1 | S_d: `0x8ca0 + r4·100` µs (≈ 36 ms) antes del id 7 |

Orden estático relativo (VERIFICADO): P4C ← 1 < (P4D ← 0 en 1a/1d) < armado < {A, B} y P4D ← 1 del control. **El orden entre A/B y el P4D ← 1 del control no se cierra** (§3).

## 3. ¿Intervalo preparación→armado dependiente de T o del mecanismo?

* **VERIFICADO — no depende de T por código:** `r4` de `0x199b8(r4·100)` sale de bytes del bloque `0x20000300` (offsets `0x124/0x125/0x126` ×5, `0x80`, `0x83`; elección por `S+0x46` bits 2–3 y `S+0x3c`, del paquete de BIONZ). Las duraciones del control y de P4D-A/B son bytes del mismo bloque (`+0x1c`, `+0x1d`, `+0x24`·1000 µs, `+0x10`·10 µs, `[0x200036d8+0x128]`). T solo entra por `S+0x32` (elegir `0x18fa0` frente a `0x18d6e`, y la lista) y por `S+0x48` en el armado, no en esos retardos.
* **VERIFICADO — depende del tipo de mecanismo:** `0x20c90` (¿escribe?), la rama tipo 3 (arranca el control antes del armado con retardo 0, sin escribir P4D) y la clase `0x1fe66` (S_c frente a S_d, ids 0a/0d). No depende de EFCS salvo las dos compuertas de §1.
* **SOLO MEDIBLE:** (a) valor de `[0x20000050]`: lo escribe el cargador `0x0000–0x41ff`, ausente de los volcados; (b) valores efectivos de `+0x124..0x126`, `+0x80`, `+0x83`, `+0x1c/0x1d/0x24` (¿vienen de NVRAM?; el bloque `0x20000300` se rellena fuera del binario: INFERENCIA R66); (c) el intervalo real preparación→0x1f: lo fijan los sondeos de `0x17cee`, `0x17f8c` y el momento en que BIONZ manda la orden `0x0c`/disparo; (d) bits `pkt[0x0c]` y `S+0x44` b0 en un disparo con EFCS (solo un paquete visto); (e) esperas de pines del rearme (R75 §2.3).

## 4. Correcciones y estado

* **CORRECCIÓN a R75 §2.3:** `0x1f68a` pertenece a la tabla `0x29868` (id 0, puntero en `0x2986c`), no a `0x298bc`; `0x298bc` es el id 0x0a (`0x1f88a`) y `0x298d4` el 0x0d. Tampoco es «acción de otra máquina fuera de captura»: es la máquina P4D, que solo arranca tras el armado (o por rearme/ráfaga/tipo 3).
* **E26-R75-T0 acotado:** la preparación (P4C ← 1) precede a todo y es independiente de T; el único P4D ← 1 de la captura con EFCS cae **después** del armado y tras un retardo de configuración fijo. Así, el tiempo `B − prep` no tiene componente de firmware que dependa de T; si la pérdida varía con T, la dependencia viene del propio `B − t0` (ya programado por `0x18d6e`) o de hardware. Sigue pendiente la medición con analizador lógico (P4C/P4D/P4E) para fijar el origen del transitorio y el orden A/B frente a P4D ← 1.
* Límites: no se siguieron las acciones de las máquinas que 09/0a/13/14 arrancan (sin escrituras P4B–P4E a ≤ 4 niveles); la semántica de `0x1e4c2/0x1e4f6/0x1e4aa` (bits `0x80/0x40` de `[m+0x10]`) no se cerró, por eso no se afirma si una acción inerte «avanza» o «espera».
