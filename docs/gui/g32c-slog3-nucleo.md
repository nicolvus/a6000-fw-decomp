# G32-C — S-Log3 (gamma `0x17`) en las ramas por gamma del núcleo (12-11-2026)

Análisis estático por bytes y capstone de `analysis/rea-independent/input/av-cam.bin` (base `0x43541000`), sin REA, sin cámara y sin instalar nada.

## 1. Dónde está la gamma y qué calculan las dos funciones

Único llamador común: `0x43867acc`. Lee la gamma de `YC+0xbd9` (`0x43867b00`/`0x43867b32`), llama a `0x438678ac` (`0x43867b16`/`0x43867b2a`) y a `0x438677e0` (`0x43867b38`), y guarda los dos bytes resultantes en los punteros de salida y en `[global+0x58c]`/`[global+0x58d]` (`0x43867b6e`/`0x43867b72`).

- `0x438678ac` elige una **clase** `r7` (0…13, guardada en `[global+0x58e]`, `0x43867982`) y con ella un grupo de 6 bytes del bloque de ajustes (`+0x194…+0x3cf`) cuya suma, limitada a 15, pasa a `0x43b084f8`. Es un desplazamiento por gamma (previsiblemente de exposición o ganancia), **no** la selección de curva.
- `0x438677e0` devuelve un nivel (`0x80` neutro, escala `0xef`) según la gamma y el modo `[+0x193]`.

Ninguna de las dos lee ni escribe la tabla de curvas (`0x44001404`) ni el selector (`0x43cb56e6`). Por tanto, **la ausencia de casos para `0x17` no puede explicar por sí sola que la curva S-Log3 no se aplique**; solo explica que S-Log3 no recibe la compensación de S-Log2.

## 2. Ramas que excluyen `0x17` frente a `0x14/0x15/0x16`

| Lugar | `0x14` S-Log2 | `0x15` ITU709(800 %) | `0x16` | `0x17` S-Log3 (original) |
|---|---|---|---|---|
| `0x438677e0`, `[+0x193]`=2 con bandera (`0x43867836`: `subs #0x14; cmp #2; bhi`) | rama `0x4386783e` | `0x4386783e` | `0x4386783e` | defecto `0x4386784c` (`0x7f80`) |
| `0x438677e0`, `[+0x193]`=1 sin bandera (lista `0x0a,0x16,0x18–0x1b`) | defecto | defecto | `0x4386783e` | defecto (igual que `0x14`) |
| `0x438677e0`, otro modo (`0x4386785c`: `≤1` → `+0x1cb`, si no `+0x1cc`) | `+0x1cb` | `+0x1cb` | `+0x1cc` | `+0x1cc` |
| `0x438678ac`, `r5`=1: tabla `0x43bc8630[gamma]` | 8 | 10 | 11 | **0** |
| `0x438678ac`, `r5`≠1 (`0x43867910…`) | 8 / 9 (9 si `r3` ∈ `0x20,0x26–0x29`) | 10 | 0 | **defecto** `0x4386794c` (1, 2 o 0 como gamma ordinaria) |

## 3. Parche mínimo (`scripts/gui/pp_slog3_core_patch.py`)

Hace que `0x17` tome las ramas de `0x14` donde difieren; el resto de gammas no cambia.

| Dirección | Original | Nuevo | Efecto |
|---|---|---|---|
| `0x4386783a` | `02 2d` `cmp r5,#2` | `03 2d` `cmp r5,#3` | `0x14…0x17` comparten `0x4386783e` |
| `0x43867924` | `12 d3` `blo 0x4386794c` | `05 d3` `blo 0x43867932` | ese `blo` solo se alcanza con `0x17` (`>0x16`, `<0x18`): pasa a la clase de S-Log2 |
| `0x43bc868c` | `00000000` | `08000000` | tabla de clases, entrada `0x17` = la de `0x14` |

`apply()` comprueba los bytes originales antes de escribir. Uso: `pp_slog3_core_patch.py BASE_AVCAM SALIDA`. Es aditivo: **no está integrado** en `build_base_pp`/`build_cfw_completo` ni sube la versión del CFW (otro agente trabaja en el constructor).

Prueba: `tests/test_g32c_slog3_core.py` (Unicorn, 14 casos) emula solo los tramos de decisión: en el original `0x17` difiere de `0x14`; parcheado coincide en las tres ramas (con `r3` = 0, `0x20`, `0x29`), y las gammas 0, 1, `0x0a`, `0x13`–`0x16`, `0x18`, `0x1b`, `0x1e` no cambian.

## 4. NO_VERIFICADO

- Que la tabla `0x43bc8630` no tenga otros lectores (solo se buscó el `ldr` pc-relativo de `0x43867902`).
- Qué representan exactamente los grupos `+0x194…+0x3cf` y la bandera `0x43b09420`; si la compensación de S-Log2 es adecuada para la curva S-Log3.
- Efecto en imagen, y la causa real de «sin efecto»: la curva no pasa por estas funciones. Antes conviene descartar G36-A (el selector del 3.77 no pasa de la 7.ª opción; S-Log3 es la 12.ª) y leer en cámara `cfg+0x153` = 2 y `YC+0xbd9` = `0x17`.
