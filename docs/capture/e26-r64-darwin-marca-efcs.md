# E26-R64 — Qué hace Darwin con la marca EFCS `pkt[1]` (05-11-2026, estático)

Capstone sobre `darwin_core.bin` 3.21 (base `0x4200`). Continúa [R63](e26-r63-swd-efcs-on-off.md) §1 (`pkt[1]` = `0x02` EFCS on, `0x40` EFCS off).

Etiquetas: **VERIFICADO** (instrucciones) · **INFERENCIA**.

## 1. El analizador reescribe `S+0x31` según el tipo de mecanismo (VERIFICADO, `0x1807a–0x180fe`; corrige S53/E24-05a)

`t = [0x20003cd8+0x20]` (`0x19b5e → 0x202ba`):

| `t` | `S+0x31` tras el analizador | EFCS on (`0x02`) | EFCS off (`0x40`) |
|---|---|---|---|
| 1, 2 | `& ~3` (el bit 6 se conserva) | `0x00` | `0x40` |
| 3 | `(& ~3) + 1`, y **`& ~0x40`** | `0x01` | `0x01` |
| 4 | `(& ~3) + 2`, y **`& ~0x40`** | `0x02` | `0x02` |
| 0, ≥5 | sin cambio | `0x02` | `0x40` |

S53 decía «3 → +1; 4 → +2», pero no que esos tipos **borran el bit 6**. Con `t` = 3/4 la marca EFCS desaparece en Darwin.

## 2. Lectores de `S+0x31` (VERIFICADO)

* `0x196a2` (seis llamadores: `0x17e80`, `0x185ee`, `0x18610`, `0x1863a`, `0x18694`, `0x18832`) devuelve 1 si `& 3 == 0` o si el bit 6 está puesto. Es el **único** que lee el bit 6.
* El resto usa los bits 0–1 (`lsls #0x1e`, `ubfx #0,#2`), 2–3 (`tst #0xc`) y 4–5 (`tst #0x30`/`ubfx #4,#2`). El bit 7 solo se mira dentro de ramas con `& 0x30 ≠ 0`. Los lectores de `[rX,#0x31]` en `0x16af8–0x16bf0` (`0x20000600`, anillo), `0xa4e6` (`0x20000000`) y `0x17c3e` (`0x20003788−0xb0`) son **otras estructuras**.
* En el experimento de R61, `+0x88` cambió también la luz con EFCS activado. Eso exige `S+0x31 & 3 == 0` con EFCS on, es decir `t` ∈ {1, 2} (**INFERENCIA fuerte**). En ese caso:
  * on → `0x00`, off → `0x40`; `0x196a2` = 1 en ambos;
  * bits 0–5 iguales (0) en ambos; `0x18d6e` usa `r5 = 1` y `B+0x88` en ambos.
  * **Ningún lector de `S+0x31` encontrado distingue EFCS on de off.**

## 3. El tipo de mecanismo (VERIFICADO)

* Lo fija `0x205e6` (`[0x20003cd8+0x20] = t`, solo 1–4), llamado solo desde `0x19b62` ← `0x1f240`, que está en un despachador de órdenes (`0x1f23a/0x1f23e/0x1f246/0x1f24a` → t = 1/2/3/4). En R59 no apareció ninguna orden así durante los disparos (**INFERENCIA:** se fija al iniciar, no en cada foto).
* `0x202c2` (nueve llamadores) instala una lista según `t`: `t = 2` → `0x29d64`; 3/4 → `0x29d88`; 1 → ninguna.

## 4. Conclusión y límite

* Con la evidencia actual, **Darwin ejecuta la misma temporización con EFCS activado y desactivado**. La diferencia por modo está en el BIONZ y el sensor (ID1 `d4`/`c4`, R63), y quizá en el tipo `t`, que no cambia por disparo.
* **Contradicción abierta:** con EFCS desactivado la cortina delantera tiene que recorrer el cuadro y con EFCS activado no. Si Darwin no lo distingue por `S+0x31`, lo hace otra señal: otro campo, una orden fuera del paquete `0x0c` o una línea física. Para cerrarlo hay que seguir quién arranca la cortina delantera (bobina/motor) en la lista de estados (`0x1961c`) y si depende de algo distinto en cada modo.
* La palanca de la pérdida EFCS queda, con más probabilidad, en el **instante en que el sensor arranca el reinicio electrónico** (BIONZ), no en Darwin.

## 5. Lista de estados: `0x196a2` gobierna la cortina delantera mecánica (VERIFICADO, 05-11-2026)

* Lista ejecutada con `pkt[0xc] = 0` (ambos modos, R63): `0x28f88` = `02 09 03 04 0d 0a 0f 06 13 14 1a 1c 1f 20 30 31` (tabla `0x28ff8`).
* Estado **2** (`0x185ea`): si `0x196a2() ≠ 0` y `[B+0xcd]` bit 2 = 0 → `0x1991e`. Estado **3** (`0x1860c`): mismo filtro → espera `0x19974`. Estado **4** (`0x18636`): si `0x196a2() ≠ 0` → `0x19998(1)` (rearme L2, motor) y marca de tiempo en `S+0x98`. Los estados 6 y 0x0d también dependen de `0x196a2`.
* Es decir, **`0x196a2` = «hay acciones de cortina delantera mecánica»**. Para que EFCS funcione, debe dar 0 con EFCS activado. Con la tabla del §1, eso solo ocurre si el tipo `t` **no** es 1/2: con `t` = 0 (o ≥5), on `0x02` → 0 y off `0x40` → 1. Los tipos 3/4 darían 0 también con EFCS desactivado.
* El tipo lo fijan las órdenes BIONZ `0x62/0x63/0x64/0x65` → `t` = 1/2/3/4 (`0x1f0ac–0x1f126` → `0x1f23a–0x1f24a` → `0x205e6`). Las despacha `0x1f362` (órdenes `0x40–0x9f`), llamado desde `0x1bfb6`. El lado BIONZ que las envía **no está localizado**.

### Contradicción con R61 y cómo resolverla

`B+0x88` solo se lee en `0x18ea6` (rama `r5 = 1`, `S+0x31 & 3 == 0`). Si BK4 `0x30102` se copia 1:1 en `B`, que `+0x88` cambiara la luz con EFCS activado (R61) implica `t` ∈ {1,2}. Con ese tipo, `0x196a2 = 1` también con EFCS activado, y Darwin ejecutaría las acciones y la temporización **mecánicas** con EFCS. **Sería una causa candidata del fallo** (INFERENCIA). La alternativa es `t` = 0 (lo normal) con un desplazamiento entre BK4 y `B`, y que el cambio de EFCS desactivado en R61 fuera de la escena (su referencia era de otra serie).

Prueba que lo decide (NVRAM, reversible; cada variante con pares on/off **en la misma serie**):

| Resultado | BK4 `+0x88` +500 µs | BK4 `+0x8a` +500 µs | Lectura |
|---|---|---|---|
| A | cambian ambos modos | ninguno | 1:1 y `t` ∈ {1,2} → Darwin trata EFCS como mecánico (fallo candidato) |
| B | solo EFCS desactivado | solo EFCS activado | 1:1 y `t` = 0 (normal) |
| C | solo EFCS activado | ninguno | BK4 desplazado 2 B respecto a `B`, `t` = 0 |

## 6. Prueba A/B/C en curso (05-11-2026)

* `+0x88` restaurado a 334 y comprobado tras reiniciar con la batería fuera (`20261105-r64-tras-bateria-334`).
* Base con 334 (`20261105-r64-fotos/base334`, `DSC03563–66`): 1/500 on/off **0,353** (franjas 0,44 → 0,13); 1/1000 negro.
* **Estado actual de la cámara: variante `+0x88` = 834 escrita** (`20261105-r64-post-var088`, SHA-256 `727e41ff…`). Revertir con `20261105-r64-tras-bateria-334/backup_flash.bin` y reiniciar con la batería fuera.
* Las fotos «(1)» entregadas para la variante son **copias idénticas** de las de la base (mismo SHA-256): falta la serie real con 834, y después `+0x8a`.

### Resultado con `+0x88` = 834 (MEDIDO, misma escena; fotos `DSC03564 (1)`, `03565 (1)`, `03566 (1)`, `03567`)

Las fotos «(1)» de antes eran copias de la base; las reales son las de esta tabla. Copias en `20261105-r64-fotos/var088-real/` (la carpeta `var088/` contiene por error copias de la base).

| | 334 (base) | 834 | Cambio | Equivale a |
|---|---|---|---|---|
| Off 1/500 (media) | 135,1 | 146,4 | +8 % | ≈ +0,17 ms |
| Off 1/1000 | 64,0 | 74,4 | +16 % | ≈ +0,16 ms |
| On 1/500 | 47,7 | 57,0 | +20 % | ≈ +0,14 ms (a la tasa de off) |
| On 1/1000 | negro | negro | — | — |
| on/off 1/500 | 0,353 | 0,389 | | |

* **Los dos modos ganan casi lo mismo en tiempo absoluto (≈0,15 ms), no 0,5 ms**, y 1/1000 con EFCS sigue negro. Tiende al resultado A (`+0x88` actúa en los dos modos), pero con un efecto 3 veces menor que el valor escrito. No hay una referencia independiente de la luz, así que una deriva de la escena del 8–16 % no está descartada.
* **No reproduce R61** (EFCS activado ×3 a 1/1000). Aquel resultado comparaba con una base de otra serie y no es fiable.
* Unidad de `+0x88`: si el efecto es real, ≈0,3 de lo escrito. Puede no estar en µs (temporizador `0x93e6`, unidad sin determinar).
* Estado: la cámara **sigue con 834**. Pendiente: variante `+0x8a` con la misma serie, y restaurar 334 con reinicio sacando la batería.
