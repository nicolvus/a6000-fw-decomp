# S194 — el módulo `[PNL]` (41 trazas): 4 mensajes exclusivos por firmware

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

`[PNL]` tiene **contenido mayormente común** con variantes por firmware: de las 41 cadenas de
cada firmware, 37 son comunes a los tres y 4 son exclusivas de cada uno.

| etiqueta | cadenas | A6000 | A7S | A6300 |
|---|---|---|---|---|
| `[PNL]` | 41 | 41 | 41 | 41 |

## Efecto en S51

Negativo acotado (0 menciones de obturador, disparo, lectura del sensor o exposición en el
conjunto de cadenas) → **sin efecto en S51** (A/B/C = NO).

Informe: `analysis/s194_pnl/pnl_strings.json` · test: `tests/test_s194_pnl.py`.
