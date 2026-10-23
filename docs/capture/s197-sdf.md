# S197 — el módulo `[SDF]` (477 trazas): 11 mensajes extra en el A6300

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

`[SDF]` es mayormente un **cambio de etiqueta, no de código**: las 477 cadenas de la A6000 son
idénticas en la A7S (con 2 exclusivas de la A7S). El A6300 comparte 464 con la A6000 y añade
11 exclusivas.

| etiqueta | cadenas | A6000 | A7S | A6300 |
|---|---|---|---|---|
| `[SDF]` | 477 | 477 | 479 | 488 |

## Efecto en S51

Negativo acotado (0 menciones de obturador, disparo, lectura del sensor o exposición en el
conjunto de cadenas) → **sin efecto en S51** (A/B/C = NO).

Informe: `analysis/s197_sdf/sdf_strings.json` · test: `tests/test_s197_sdf.py`.
