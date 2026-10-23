# S192 — el módulo `[STK]` (76 trazas): plataforma antigua, ausente en el A6300

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

`[STK]` es un módulo de la **plataforma antigua** (E-mount / pre-LIRO): presente en la A6000
fw3.21 y la A7S fw3.20, **ausente por completo en el A6300 fw2.01**. Las 76 cadenas de la
A6000 y la A7S son idénticas (con 8 variantes de sub-prefijo).

| etiqueta | apariciones | A6000 | A7S | A6300 |
|---|---|---|---|---|
| `[STK]` | — | 76 | 76 | 0 |

## Efecto en S51

Negativo acotado (0 menciones de obturador, disparo, lectura del sensor o exposición en el
conjunto de cadenas) → **sin efecto en S51** (A/B/C = NO).

Informe: `analysis/s192_stk/stk_strings.json` · test: `tests/test_s192_stk.py`.
