# S195 — el módulo `[ENCOUCSTAT]` (49 trazas): 21 mensajes extra en el A6300

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

`[ENCOUCSTAT]` es mayormente un **cambio de etiqueta, no de código**: las 49 cadenas de la A6000
son idénticas en la A7S (con 5 exclusivas de la A7S). El A6300 comparte 47 con la A6000 y
añade 21 exclusivas.

| etiqueta | cadenas | A6000 | A7S | A6300 |
|---|---|---|---|---|
| `[ENCOUCSTAT]` | 49 | 49 | 54 | 68 |

## Efecto en S51

Negativo acotado (0 menciones de obturador, disparo, lectura del sensor o exposición en el
conjunto de cadenas) → **sin efecto en S51** (A/B/C = NO).

Informe: `analysis/s195_encoucstat/encoucstat_strings.json` · test: `tests/test_s195_encoucstat.py`.
