# S189 — el módulo `[DEBUG]` (67 trazas): 32 mensajes nuevos en la A6000 fw3.21

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

`[DEBUG]` tiene **contenido parcialmente nuevo** en la A6000 fw3.21: de las 67 cadenas, 35 son
comunes con la A7S y el A6300, y 32 son exclusivas de la A6000. La A7S y el A6300 comparten
35 cadenas (con 2 exclusivas cada uno).

| etiqueta | cadenas | A6000 | A7S | A6300 |
|---|---|---|---|---|
| `[DEBUG]` | 67 | 67 | 37 | 37 |

## Efecto en S51

Negativo acotado (0 menciones de obturador, disparo, lectura del sensor o exposición en el
conjunto de cadenas) → **sin efecto en S51** (A/B/C = NO).

Informe: `analysis/s189_debug/debug_strings.json` · test: `tests/test_s189_debug.py`.
