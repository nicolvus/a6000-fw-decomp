# E26-R66 — Los bloques de ajuste de Darwin son las propiedades NVRAM `0x1850000/01`; `0x30102` no llega a Darwin (07-11-2026, estático)

Continúa [R65](e26-r65-darwin-efcs-on-resta-g42.md). REA sobre `av-cam.bin` 3.21, Capstone sobre `darwin_core.bin` 3.21 y lectura de los 28 `backup_flash.bin` de `analysis/camera-dumps/` (no versionados).
Prueba: `tests/test_e26_r66_bloques_darwin_nvram.py`.

Etiquetas: **VERIFICADO** · **INFERENCIA** · **MEDIDO** (datos de volcado).

## 1. Qué propiedad alimenta cada bloque de Darwin (VERIFICADOS la tabla y los tamaños; el flujo backup → manejador es INFERENCIA fuerte, R68)

La tabla del BIONZ `0x43fe8c38` (R65 §5) tiene registros `{0x185, banderas, id, 0x436bc515, 0, dir. Darwin, tamaño, asa, ocupado}`. `FUN_436bc7d4` registra en el sistema de backup cada registro con la bandera 8 (`FUN_435614ec([reg+0x1c])`). El manejador `0x436bc514` recibe `(id, longitud, búfer)` y busca el registro por `id`. Ese `id` es un **ID de propiedad de backup**: el grupo `0x185` (389) existe en la NVRAM y los tamaños coinciden uno a uno:

| Propiedad NVRAM | Tamaño | Registro | Darwin | RAM de Darwin |
|---|---|---|---|---|
| `0x1850000` | 128 | `0xf` | `0x10100` | **G** `0x20000480` |
| `0x1850001` | 384 | `0xf` | `0x20280` | **B** `0x20000300` |
| `0x1850004` | 256 | `0x1f` (lectura) | `0x20000500` | `0x20000500` |
| `0x1850005` | 256 | `0x1f` (lectura) | `0x30100` | `0x20000600` |
| `0x1850002`, `0x1850003` | 256, 512 | — | — | — |

`FUN_436bc804` solo atiende los registros con la bandera `0x10` (lecturas desde Darwin). B y G no la tienen: el BIONZ los **escribe** en Darwin y no los relee.

**Corrige:** R58 §13 (B = BK4 `0x30102`, INFERENCIA), R61, R62 §3–4, R63 §6 y R64 §5–6 (que tomaron esa asignación) y R65 §4–5 («G no está en la NVRAM»). BK4 `0x30102` (384 B, `0x43e97970`) es un bloque del propio BIONZ, que leen `FUN_438d49bc`/`FUN_438d509c`; no es el bloque B y no se ha encontrado que llegue a Darwin por otra vía. **Ningún experimento de NVRAM de R61–R64 tocó Darwin.** Los ≈ +0,15 ms medidos en ambos modos (R64 §6) no se explican por Darwin: deriva de escena, o un efecto del BIONZ sin identificar.

## 2. Valores reales e historia (MEDIDO en volcados)

* **G** (`0x1850000`): todo ceros salvo **`G+0x40 = −435`** (s16) y **`G+0x42 = 3407`** (u16) µs.
* **B** (`0x1850001`): `+0x84/+0x86/+0x88/+0x8a` = **6 / 6 / −22 / −21** µs; `+0xc6..c8` = 29 / 37 / 35; `+0xcd` = 0; `+0x12a..12f` = 0.
* **G, B, `0x1850002`, `0x1850003` y `0x1850004` son idénticos en los 28 volcados (20-10 → 05-11).** Solo cambia `0x1850005`, la imagen de `0x20000600` (anillo de 24 entradas y contadores, R62 §3) que el BIONZ relee de Darwin.
* Conclusión: **los ajustes de temporización de Darwin no han cambiado desde que EFCS funcionaba.**

## 3. Temporización de Darwin con EFCS activado y valores reales (VERIFICADO el código; `t` = 0, `S+0x60` = 0)

`S+0x48 = T − 3407`. Los eventos `A` (`0x202f2`) y `B` (`0x2041e`) son los dos disparos de `0x18d6e`; `B − A` es la separación que impone Darwin.

| Velocidad | T (µs) | `S+0x48` | Rama | `B − A` (µs) |
|---|---|---|---|---|
| 1/4000 | 250 | −3157 | A con retardo de 3151, B inmediato | −3151 |
| 1/1000 | 1000 | −2407 | A con retardo de 2401, B inmediato | −2401 |
| 1/500 | 2000 | −1407 | A con retardo de 1401, B inmediato | −1401 |
| 1/320 | 3125 | −282 | A con retardo de 276, B inmediato | −276 |
| 1/250 | 4000 | 593 | A inmediato, B con retardo de 572 | 572 |
| 1/200 | 5000 | 1593 | íd., 1572 | 1572 |
| 1/125 | 8000 | 4593 | íd., 4572 | 4572 |

* `B − A = T − 3401` (rama corta) y `T − 3428` (rama larga): **continua**, con un salto de 27 µs entre ramas. La rama intermedia (`0x20544`) hace los dos flancos con esperas activas (`0x20d26/0x20e0e/0x20e98`). Lectura (INFERENCIA fuerte; R67: A = P4C ← 0, B = P4E ← 1, y P4E ← 0 lo pone después el seguimiento ADC `0x207c2/0x207ec`): B suelta la segunda cortina mecánica, que tarda ≈ 3,4 ms en llegar al cuadro; A marca el arranque del reinicio electrónico. La exposición vale `T + (latencia real de la cortina − 3407) − (retardo real del reinicio)`.
* **El cambio de régimen de la pérdida (5 → 8 ms, R62 §2) no sale de Darwin:** de 1/250 a 1/125 Darwin sigue la misma rama, y la pérdida pasa de 1,29 ms a ≈ 0. Tampoco hay discontinuidad en el cambio de rama de Darwin (≈ 3,3 ms): las pérdidas a 2,86 y 4,0 ms son iguales (1,30/1,29). **La pérdida y su desaparición vienen del lado BIONZ/sensor** (cuándo arranca el reinicio respecto a A), o de una latencia física de la cortina que ya no es la de fábrica.
* Candidato BIONZ de R62 (`r8 = max([rec+0x1c] + sb, VTS)` en `0x4383fa40`): E25-16 vio que el registro se pone a cero en `0x437b441e` y no encontró escritor de `+0x1c`. Con `+0x1c = 0` ese umbral no existe; el candidato **se debilita**. NO VERIFICADO.

## 4. Palancas reales de compensación (VERIFICADO el flujo; efecto NO MEDIDO)

Barrido completo de `darwin_core.bin`: `B+0x84..0x8a` solo se leen en `0x18d6e` (`0x18e54/5a/a6/ac`). `G+0x42`, en cambio, tiene cinco lectores (`0x182d8`, accesor usado por `0x22a3e/0x22aaa/0x22ac8/0x23a5e`; `0x18398`, que lo devuelve al BIONZ; `0x18a2e`; `0x18d6e`; `0x18fbc`). Por eso **no conviene tocar G**.

| Palanca (propiedad NVRAM) | Rama | Efecto con EFCS activado | Otros modos |
|---|---|---|---|
| `0x1850001+0x86` (hoy 6) | `S+0x48 < −150` (T ≲ 3,26 ms: 1/320 y más rápido, **incluye el negro**) | +Δ adelanta A → +Δ de exposición | ninguno (solo `r5 = 0`) |
| `0x1850001+0x8a` (hoy −21) | `S+0x48 > 50` (T ≳ 3,46 ms) | +Δ retrasa B → +Δ de exposición | ninguno; pero a 1/125 no hay pérdida que corregir |

**Corrección ([R68](e26-r68-auditoria-r65-r67.md)): `+0x86` se satura.** En `0x18e6a–0x18e7c`, si `S+0x48 + B86 ≥ 0` el retardo de A vale 1 µs (`mov r0,#-1; rsbs`). Con B86 = 1276 solo se compensa T < 3407 − 1276 = 2131 µs (≈ 1/470 y más rápido). Entre 2131 y 3257 µs A y B salen a la vez y la exposición queda fija en ≈ 2,1 ms (a 1/320, −32 %). Entre 3257 y 3457 µs no se aplica ninguna corrección. La palanca coherente en todas las ramas es **`G+0x42` (`0x1850000+0x42`, 3407 → ≈ 2137)**, pero tiene otros lectores (§4): solo actúa con EFCS desactivado (`ip`, `0x18fbc`), en un accesor sin identificar (`0x182d8`) y en la respuesta al BIONZ (`0x18398`). Compensar sobreexpone además 1/125 y más lentas, donde hoy no hay pérdida.

Propuesta original (sustituida por la corrección anterior): `+0x86` de 6 a ≈ 1276 (+1270) con `scripts/e26_r61/bk4_variante.py ENTRADA SALIDA 0x1850001 0x86 1270`, que vale para cualquier ID, y restauración del volcado. Criterio: con EFCS activado, 1/500 y 1/1000 en pares on/off de la misma serie dan luz con una razón ≈ 1; 1/250 no cambia (otra rama). Riesgo: el atributo de `0x1850001` es 8 (G = 10); no consta que se reescriba al apagar (no tiene la bandera de lectura `0x10`).

## 5. Estado de los pendientes

* **E26-R65-G42:** CERRADO. G = propiedad `0x1850000`, `G+0x42 = 3407`, sin cambios desde el 20-10.
* **E26-R65-8A:** SUSTITUIDO por E26-R66-B86. `0x30102+0x8a` no llega a Darwin.
* **E26-R62-UMBRAL:** sigue ABIERTO; la causa está en el BIONZ (§3) y el candidato `0x4383fa40` se debilita.
* Lo que queda abierto es físico o de BIONZ en ejecución: cuándo arranca el reinicio electrónico respecto a A (SWD de BIONZ o del sensor) y la latencia real de la segunda cortina.
