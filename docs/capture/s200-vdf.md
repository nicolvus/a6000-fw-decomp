# S200 — el módulo `[VDF]` (243 trazas): 81 mensajes nuevos en la A6000 fw3.21

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

`[VDF]` tiene **contenido parcialmente nuevo** en la A6000 fw3.21: de las 243 cadenas, 162 son
comunes con la A7S y el A6300, y 81 son exclusivas de la A6000. El A6300 comparte 161 con la
A6000 y tiene 1 exclusivo propio.

| etiqueta | cadenas | A6000 | A7S | A6300 |
|---|---|---|---|---|
| `[VDF]` | 243 | 243 | 162 | 162 |

## Efecto en S51

Negativo acotado (0 menciones de obturador, disparo, lectura del sensor o exposición en el
conjunto de cadenas) → **sin efecto en S51** (A/B/C = NO).

Informe: `analysis/s200_vdf/vdf_strings.json` · test: `tests/test_s200_vdf.py`.
