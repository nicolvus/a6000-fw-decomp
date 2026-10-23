# S198 — el módulo `[ERR]` (288 trazas): 43 mensajes nuevos en la A6000 fw3.21

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

`[ERR]` tiene **contenido parcialmente nuevo** en la A6000 fw3.21: de las 288 cadenas, 245 son
comunes con la A7S y 43 son exclusivas de la A6000. El A6300 tiene 238 comunes con la A6000 y
415 exclusivos propios.

| etiqueta | cadenas | A6000 | A7S | A6300 |
|---|---|---|---|---|
| `[ERR]` | 288 | 288 | 281 | 655 |

## Efecto en S51

Negativo acotado (0 menciones de obturador, disparo, lectura del sensor o exposición en el
conjunto de cadenas) → **sin efecto en S51** (A/B/C = NO).

Informe: `analysis/s198_err/err_strings.json` · test: `tests/test_s198_err.py`.
