# S199 — el módulo `[ERROR]` (213 trazas): etiqueta nueva de la fw3.21

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

`[ERROR]` es un **cambio de etiqueta, no de código**: las 213 cadenas de la A6000 son idénticas
en la A7S. El A6300 comparte 207 y añade 1 exclusiva.

| etiqueta | cadenas | A6000 | A7S | A6300 |
|---|---|---|---|---|
| `[ERROR]` | 213 | 213 | 213 | 214 |

## Efecto en S51

Negativo acotado (0 menciones de obturador, disparo, lectura del sensor o exposición en el
conjunto de cadenas) → **sin efecto en S51** (A/B/C = NO).

Informe: `analysis/s199_error/error_strings.json` · test: `tests/test_s199_error.py`.
