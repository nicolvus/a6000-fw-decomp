# G38 — Objetivo «Obturación máxima 1/8000» (origen ≈Sony α7): REABIERTO, parche Silent probado en el arnés, sin CFW (15-11-2026)

Sin cámara ni CFW nuevo. Sustituye al descarte inicial del mismo día, que daba por hechas dos cosas sin verificar: que el piso de 564 µs del Silent es del sensor y que 1/4000 mecánico es un límite físico. Ninguna de las dos está demostrada.

## 1. Veredicto por estado de obturador

| Estado | Veredicto | Razón cuantitativa |
|---|---|---|
| **Silent** | **Reabierto. Parche escrito y emulado; falta medir en cámara (G38-C).** El «piso» de 0,58 ms es el tope de nuestra cueva, no del firmware ni demostrado del sensor | Ver §2: `min(r5, 4218)` en `patch_silent_r5` ⇒ E = 17,135 µs·(4252 − 4218) = 583 µs. Con el tope en 4251, 1/8000 → `r5` = 4245 → E ≈ 120 µs (1/8000 = 125 µs) |
| **EFCS** | Sin parche posible hoy: la segunda cortina es mecánica (misma física que Mecánico) y, en esta unidad, la pérdida de 1,0–1,26 ms (R83) supera por 8–10× la exposición de 1/8000 | §3; ni el firmware de Darwin ni la pérdida medida cambian por una lista de velocidades |
| **Mecánico** | **No descartado por firmware; inviable en esta unidad y no verificable offline.** Darwin acepta T = 125 µs sin clamp; el límite es la repetibilidad del imán: ±33 µs para ±⅓ EV | §3: rendija ≈ 0,57 mm (3,7 % del recorrido); el residuo medido en esta unidad es ±190 µs |

## 2. H1 — Silent: ¿es configurable el piso de 564 µs?

**Evidencia de código (bytes de `av-cam` 3.21/3.75):**
* `SetExposure` (`0x436d6f6c`) escribe `r5` (`shd`) en los registros ID5/ID6 con una máscara de 14 bit (`0x436d7000..0x436d701e`: `uxtb` + `and #0x3f`) y en `blk+0x52` (`0x43ad9a4e`, `strh`). **No hay ninguna comparación ni clamp sobre `shd`**; tampoco en el escritor `0x43ad9a40` ni en el accesor de registros.
* El productor nativo `0x4383fa40` calcula `L = µs/período` (división truncante), `R = max(suelo + L, VTS)` y `shd = R − L`. Sin mínimo de `L`: para L = 0 devuelve `shd = VTS`.
* Quien acota es **`patch_silent_r5`**: `r5 = 4252 − T/17,135 µs` y `r5 <= 4218` (`R5_FULL − 1`). `4252 = 4219 + 33` (`R5_LAG` = 564 µs / 17,135). Es decir, **564 µs es el intercepto del ajuste** (E = 17,135·(4252 − r5)), no una constante leída del sensor, y los «0,58 ms con n = 1» de R87 §3 son en realidad el valor del tope (n = 34 líneas, no 1): 17,135 × 34 = 583 µs. (G38 original decía «≈ 1/600» como umbral de línea ≤ 0: el tope se alcanza a T < 583 µs, ≈ 1/1715.)

**Evidencia medida que contradice un piso intrínseco ([figura](img/g38-r5-ley.png)):**
* T046 (RAW, ShutMode 0 forzado en `SetExposure`): `r5` = 4200 → **0,3 ms**, 4100 → 1,8 ms; ley `E = 15,2 µs·(4219 − r5)` con intercepto cero a ±0,1 ms ([E25-10 §3](../capture/e25-10-exposicion-por-fila.md)). Por tanto el sensor integró 0,3 ms < 0,564 ms.
* El intercepto cambia entre campañas: T046 ≈ 0 líneas, R87 = 33 líneas (564 µs, pendiente 17,135), R56 = 97 líneas (pendiente 15,5). Una constante del sensor no cambiaría. Lo más probable es una diferencia de flujo (Silent con Darwin/`pkt[0x0e]`, ISO, referencia mecánica) aún no aislada.
* Lo que **no está medido**: `r5` en (4218, 4299). T046/T039 barrieron ≤ 4200 y 4300 (sin efecto = cuadro completo, 64,9 ms ≈ 4270 líneas). Si el sensor trata `shd` ≥ VMAX (≈ 4266–4270) como inválido, el rango intermedio es válido o cae a cuadro completo según el sensor. [T052-A §7.1](../capture/t052-a-parametros-reales.md) lo marca como «no representable (hipótesis)».

**Clasificación:** (a) clamp de firmware **propio** (de la cueva), ampliable con un parche; (b) un desfase del flujo Silent que no es intrínseco al sensor; (c) **no demostrado** (T046 lo refuta para el flujo RAM). Falta saber si el sensor acepta `r5` > 4218: ahí la hipótesis es «sí hasta VMAX − 1», **NO_VERIFICADO**.

### Parche y prueba (sin CFW)
`scripts/g38/patch_silent_r5_sublinea.py` reutiliza `patch_silent_r5` con base 4252 y tope 4251 (el módulo original queda intacto). Prueba `tests/test_g38_silent_sublinea.py`, emulada con Unicorn sobre el `av-cam` del 3.75 parcheado, Tv real de cada velocidad:

| Velocidad | Tv | `r5` actual (tope 4218) | E (ley R87) | `r5` nuevo (tope 4251) | E (ley R87) | Nominal |
|---|---|---|---|---|---|---|
| 1/1000 | `0x19f7` | 4194 | 994 µs | 4194 | 994 µs | 1000 µs |
| 1/2000 | `0x1af7` | 4218 | 583 µs | 4223 | 497 µs | 500 µs |
| 1/4000 | `0x1bf7` | 4218 | 583 µs | 4238 | 240 µs | 250 µs |
| **1/8000** | **`0x1cf7`** | 4218 | 583 µs | **4245** | **120 µs** | 125 µs |
| 1/16000 | `0x1df7` | 4218 | 583 µs | 4249 | 51 µs | 62,5 µs |

La ruta Silent con Tv `0x1cf7` escribe `cap+0x64c = 4245` y `cap+0x655 = 0` (ShutMode 0); con Silent apagado no toca nada. Velocidades ≤ 1/1000 no cambian (misma `r5` que el 3.77). Riesgo: si el sensor no acepta `r5` > 4219, sale negro o cuadro completo (+9 EV) a 1/2000–1/8000; por eso es un parche **solo de prueba** y no va al CFW hasta G38-C.

**Límite de la prueba en el arnés:** `av-cam` corre en el arnés pero no hay cadena de foto completa (`g22-avcam-puente §5.16`: el disparo lo lanza el anfitrión y no produce imagen del firmware), y el panel ISP «Silent por bandas» solo tiene cocientes medidos de 1/1250 a 1/50 (`r87*/medidas.json`). Por eso la evidencia es emulación de los bytes reales (que es lo que el arnés ejecutaría) más la figura del modelo; no hay captura PNG de una foto a 1/8000.

## 3. H2 — Mecánico/EFCS: ¿tabla o límite físico?

* **Darwin no limita T.** `0x18d6e`: `S+0x48 = T − u16[G+0x42]` con `G+0x42` = 3407 µs ([R74 §3](../capture/e26-r74-conclusion-final-efcs-negro.md), [R83 §3](../capture/e26-r83-informe-final-efcs-negro.md)). Con T < 3,26 ms (rama corta) la segunda cortina (B) se suelta de inmediato y se **retrasa la primera** (A): `B − A = T − 3401`. A 1/8000 (125 µs) A se retrasa 3,28 ms: es una cuenta sin clamp y sin tabla.
* `3407 µs` es, además, la mejor estimación del recorrido de cortina: R74 §4 mide un gradiente de 0,5 ms arriba-abajo con una cortina ≈ 15 % más rápida que el barrido de reinicio (⇒ recorrido ≈ 3,3 ms); la sincronía de flash 1/160 (6,25 ms) incluye el desfase del imán y no es el recorrido. El Level 3 SM (`docs/references/sony-ilce-6000-level3-sm.txt`) solo trae esquemas (`1ST_/2ND_CURTAIN_MG`): no hay tiempo de recorrido ni tolerancia del imán documentados.
* **Cuentas (recorrido 3,4 ms, alto del sensor 15,6 mm ⇒ 4,6 m/s):**

| Velocidad | T | Rendija | Fracción del recorrido | Tolerancia de ±⅓ EV (+26 %/−21 %) |
|---|---|---|---|---|
| 1/4000 | 250 µs | 1,14 mm | 7,3 % | ±65 µs |
| 1/8000 | 125 µs | 0,57 mm | 3,7 % | ±33 µs |

* **Conclusión cuantitativa:** la rendija a 1/8000 es la mitad que a 1/4000 y la precisión absoluta exigida pasa a ±33 µs (≈ 1 % del recorrido). El único dato de repetibilidad del repo es el residuo del ajuste EFCS de R87 §4 (**±190 µs**, esta unidad) y la pérdida de 1,0–1,26 ms de R83: 6× y 10× la exposición de 1/8000. Con una diferencia de velocidad entre cortinas de 3 % (la del EFCS es 15 %) el gradiente ya sería 100 µs, comparable a T. A 1/4000 el EFCS de esta unidad sale negro por abajo (R83 §5). Es decir, EFCS no puede ayudar y el mecánico depende de una repetibilidad de imán que nadie ha medido en una unidad sana.
* **Tabla/lista de velocidades: no localizada.** La lista del dial llega a la UI como `SHUT_SPEED_MIN/MAX_NUMER/DENOM` (`0x2014`, [g22-avcam-puente §5.18](g22-avcam-puente.md)) desde `av-cam`; la tabla de denominadores `…2000, 2500, 3200, 4000, 5000, 6400, 8000…` que contiene el `av-cam` de la A6000 (`0x683940`, `0x684fdc`, `0x6850a4`) es idéntica a la de A7S y A6300 (hasta 204 800), así que no es el tope. Un barrido de constantes `#0x1bf7/#0x1cf7/#0x1bf8…` solo da un inicializador de tabla (`0x439e92be`) y un `movw #0x1cf8` + `0x4382fa94` en la ruta en vivo (`0x437b531e`, compara con `[r4+0x108]`). Sin el generador del `0x2014` no hay parche de «lista de velocidades» que probar: **no se afirma que 1/4000 sea tope de tabla**, ni lo contrario.
* **Parche H2: no escrito** (no hay tabla localizada); no se puede probar el dial en el arnés. Queda como G38-D.

## 4. Límites
* Las dos calibraciones de `r5` (T046, R87) no coinciden en el intercepto y no cubren 4219–4299: todo lo de Silent por debajo de 583 µs es extrapolación hasta G38-C.
* La pendiente 17,135 (R87) frente a 15,2 (T046) y el residuo ±10 % limitan la absoluta: ±1 línea = ±17 µs es el 14 % de 125 µs.
* El riesgo mecánico solo se valida en cámara. Esta unidad tiene además un fallo físico sospechoso de EFCS (R83), así que cualquier prueba mecánica o EFCS de ≥ 1/2000 aquí no representa una cámara sana.
* El EFCS «degradado desde 1/1000» del descarte inicial viene de esta unidad (R85/R87); Kasson (a7R II) lo sitúa en 1/4000 con 1/3 de luz arriba, sin que sea comparable.
