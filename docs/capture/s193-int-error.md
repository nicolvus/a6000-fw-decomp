# S193 — el módulo `[INT_ERROR]` (53 trazas): etiqueta nueva de la fw3.21

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

`[INT_ERROR]` es un **cambio de etiqueta, no de código**: las **53 cadenas** son **idénticas texto a texto**
en las tres firmwares (A6000 fw3.21, A7S fw3.20, A6300 fw2.01). La fw3.21 antepone el prefijo
`[INT_ERROR]: ` a mensajes que ya existían sin etiqueta → otra instancia de la política de la
fw3.21 (S128): «se reescribe el logging, no el firmware».

| etiqueta | cadenas | A6000 | A7S | A6300 |
|---|---|---|---|---|
| `[INT_ERROR]` | 53 | 53 | 53 | 53 |

## Efecto en S51

Negativo acotado (0 menciones de obturador, disparo, lectura del sensor o exposición en el
conjunto de cadenas) → **sin efecto en S51** (A/B/C = NO).

Informe: `analysis/s193_int_error/int_error_strings.json` · test: `tests/test_s193_int_error.py`.
