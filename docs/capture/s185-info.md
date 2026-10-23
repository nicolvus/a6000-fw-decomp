# S185 — el módulo `[INFO]` (58 trazas): contenido propio de la A6000 fw3.21

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

`[INFO]` es un módulo con **contenido mayormente propio de la A6000 fw3.21**: de las 58 cadenas,
solo **1** es común con la A7S y el A6300; las otras 57 son exclusivas de la A6000. El A6300
tiene 37 de las 58 (1 común + 36 propias del A6300).

| etiqueta | cadenas | A6000 | A7S | A6300 |
|---|---|---|---|---|
| `[INFO]` | 58 | 58 | 1 | 37 |

## Efecto en S51

Negativo acotado (0 menciones de obturador, disparo, lectura del sensor o exposición en el
conjunto de cadenas) → **sin efecto en S51** (A/B/C = NO).

Informe: `analysis/s185_info/info_strings.json` · test: `tests/test_s185_info.py`.
