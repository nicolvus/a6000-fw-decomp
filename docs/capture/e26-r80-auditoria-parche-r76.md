# E26-R80 — Auditoría del parche de calibración EFCS (R76/R76b): errores, mejoras, valores y espacio (07-11-2026, estático)

Revisa `scripts/e26_r76/` y [R76](e26-r76-calibracion-propia-efcs.md)/[R76b](e26-r76b-verificacion-parche.md) contra [R74](e26-r74-conclusion-final-efcs-negro.md), [R75](e26-r75-verificacion-r74-y-darwin-b-a.md) y [R78](e26-r78-cierre-limites-r77.md). Ambos autotests pasan tras las correcciones (`e26_r76_parche_darwin_tabla.py selftest`, `e26_r76_calibrar_efcs.py selftest`). No se tocó la cámara.

## 1. Errores encontrados y corregidos en este commit

| # | Problema | Corrección |
|---|---|---|
| 1 | Los scripts subidos en `77da6565` **no funcionaban en el repo**: `keystone` solo estaba en el scratchpad (`kslib`), y `e26_r76_calibrar_efcs.py` importaba `e26_r76_parche_darwin_tabla` (nombre de v1), que no existía | `keystone-engine` instalado en `.venv`; el generador renombrado a `e26_r76_parche_darwin_tabla.py`; `ROOT` relativo al repo |
| 2 | Docstrings y mensajes con la tabla en `G+0x44` y la compuerta «bit 1» (de v1) | `G+0x48` y `(S+0x31 & 3) ≠ 0` |
| 3 | **El bucle del cave no tenía límite**: con la NVRAM sin terminador seguiría leyendo más allá de G (bloque `0x20000500`) | Límite de `TAB_MAX` = 13 entradas (`add r3, r1, #52; cmp r1, r3; bhs done`) |
| 4 | **`c` sin validar**: un valor corrupto en la NVRAM movería libremente A/B de los imanes | `c` fuera de `[0, 2000] µs` se ignora y queda el comportamiento original |

El cave pasa de 54 a **74 B**, dentro de la función muerta `0x13d5a..0x13dc0` (102 B). El autotest añade dos casos: tabla con `c = 30000` y tabla sin terminador. En los dos el resultado es idéntico al original.

## 2. Límite fundamental: el gradiente vertical no se corrige desde Darwin (MODELO)

R57 §8 midió la pérdida 1,1 → 1,6 ms de arriba abajo, unos ±0,25 ms alrededor de la media. Darwin solo mueve A y B, iguales para todo el cuadro. Con `c` = pérdida media:

| Velocidad | Arriba | Abajo | Diferencia |
|---|---|---|---|
| 1/4000 | 500 µs | 0 µs | **negro abajo** |
| 1/2000 | 750 | 250 | 1,6 EV |
| 1/1000 | 1250 | 750 | 0,74 EV |
| 1/500 | 2250 | 1750 | 0,36 EV |
| 1/250 | 4250 | 3750 | 0,18 EV |

**Consecuencia:** el parche hace utilizable 1/1000 y más lentas (con 0,74 EV de degradado a 1/1000), pero no 1/2000 ni 1/4000. Corregir el degradado exige cambiar la velocidad del barrido de reinicio del sensor en el BIONZ (vía (d) de R76: `0x30097+0x15 = 1` o un parche del planificador), que no se ha estudiado. El error de «≤ 1,7 %» de R76 es de la exposición **media**.

## 3. Valores a revisar o cambiar

| Parámetro | Hoy | Propuesta | Motivo |
|---|---|---|---|
| Último tramo `(9834, 169)` | +169 µs hasta 1/100 | **0** a partir de ≈ 7 ms, o medirlo | el modelo de R74 fija δ ≈ 160 µs en la cola, pero R62 mide ≈ 0 a 8 ms: sobreexpondría un 2 % |
| Tramo de guarda `(1953, 1263) (2099, 1117) (2245, 1398)` | error de hasta 9,3 % entre 1/512 y 1/445 | aceptarlo (no hay velocidades de la escala ahí) o reducir `MARG` | `0x19a12` da el T exacto de cada Tv; 40 µs de margen es holgado, y con 10 µs la banda se estrecha |
| `G42 = 3407`, `B86 = 6`, `B8A = −21` | constantes en el código | **leerlos del volcado NVRAM** (`0x1850000+0x42`, `0x1850001+0x86/0x8a`) en `calibrar` | son datos de esta unidad (R66 §2); si cambian, la tabla queda mal |
| Modelo δ(B−A) `_X/_D` | 7 puntos de R74 | sustituirlo por la medida del pase 0 (`calibrar ajustar`) | R75 corrige la variable: es `max(B−A, 0)`. Coincide con R74 en ambas ramas, así que la tabla no cambia, pero el ajuste debe usar esa variable |
| `C_MAX = 2000 µs` | nuevo | dejarlo | cubre el máximo previsto (≈ 1,42 ms en el pase 2) con margen |

## 4. Espacio disponible para mejoras (VERIFICADO salvo lo indicado)

* **Código:** quedan 28 B libres en la función muerta (102 − 74). Otras funciones sin referencias: `0x14fd4` (86 B), `0xaba2` (84 B) y `0x11d6c` (68 B), en total ≈ 266 B más. Que estén muertas se ha comprobado sin REA (ramas, punteros, `adr` y `ldr pc-rel`); antes de usarlas, confirmar con REA o Ghidra.
* **Datos:** `G+0x48..0x7f` = 56 B = 13 entradas más terminador. Hoy se usan 11. Si hiciera falta más, haría falta otro bloque escribible desde la NVRAM con bytes que nadie lea; no se ha verificado ninguno (B mide 0x180 B, pero `0x18d6e` lee `+0x84..0x8a`, `+0xc6..c8` y `+0x12a..0x12f`).
* **Mejoras que caben en esos 28 B:** (1) una palabra de firma en la tabla (p. ej. `G+0x48 = 'EF'` y versión) para que ninguna NVRAM ajena la active (≈ 8 B); (2) que el cave sume `c` solo en la rama corta y larga y no cerca de la ventana intermedia, en vez de los tramos de guarda (≈ 12 B).

## 5. Riesgos que no cambian (solo en cámara)

* Que el BIONZ acepte la propiedad `0x1850000` modificada y la copie a Darwin (premisa nunca probada; la vía (a) de R76 es la prueba).
* Que el cargador acepte el `darwin_core` parcheado. El tamaño no cambia y `darwin.sum` se regenera; hay que ampliar `allowed_addresses` en `scripts/e25_27/build.py` con `0x18d7c..0x18d7f` y `0x13d5a..0x13da3`.
* `S+0x48` compensado también llega al paquete de estado `0x18394` (acciones de registro 09/0f de S, R78). Es solo registro, inocuo según el código visto.
* La lógica `S+0x94`, que puede anular `S+0x48`, no está modelada.

> **Corrección ([R81](e26-r81-auditoria-opus-parche-efcs.md)):** el hueco `0x13d5a` pertenece a la función viva `0x13d58` (llamada desde `0x1516c`), y las alternativas de R80 §4 también están vivas. El parche está BLOQUEADO hasta encontrar otra ubicación.
