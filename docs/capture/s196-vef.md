# S196 — el módulo `[VEF]` (149 trazas): 8 mensajes nuevos en la A6000 fw3.21

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

`[VEF]` es mayormente un **cambio de etiqueta, no de código**: 140 de las 149 cadenas de la A6000
son idénticas en la A7S y el A6300. La A6000 añade 8 mensajes exclusivos; el A6300 añade 3.

| etiqueta | cadenas | A6000 | A7S | A6300 |
|---|---|---|---|---|
| `[VEF]` | 149 | 149 | 141 | 144 |

## Efecto en S51

Negativo acotado (0 menciones de obturador, disparo, lectura del sensor o exposición en el
conjunto de cadenas) → **sin efecto en S51** (A/B/C = NO).

Informe: `analysis/s196_vef/vef_strings.json` · test: `tests/test_s196_vef.py`.
