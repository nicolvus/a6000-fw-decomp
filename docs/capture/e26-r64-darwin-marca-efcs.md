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
