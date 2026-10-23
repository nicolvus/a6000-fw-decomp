# S191 — el módulo `[GOLFSHOT]` (65 trazas): sub-etiqueta con prefijo adicional en la A6000

> Hito de la **línea de RE general**. Solo bytes: A6000 fw3.21, con A7S fw3.20 y A6300 fw2.01
> como comparación.

## Veredicto

`[GOLFSHOT]` aparece como **sub-etiqueta** dentro de otros módulos (p. ej.
`[IMAGING_RSRC]: [GOLFSHOT]…` en la A6000). Las 65 cadenas de la A6000 tienen un prefijo
adicional respecto a la A7S y el A6300, cuyos textos interiores (tras `[GOLFSHOT]`) son idénticos.
El A6300 tiene 64 de las 65.

| etiqueta | apariciones | A6000 | A7S | A6300 |
|---|---|---|---|---|
| `[GOLFSHOT]` | — | 65 | 65 | 64 |

## Efecto en S51

Negativo acotado (0 menciones de obturador, disparo, lectura del sensor o exposición en el
conjunto de cadenas) → **sin efecto en S51** (A/B/C = NO).

Informe: `analysis/s191_golfshot/golfshot_strings.json` · test: `tests/test_s191_golfshot.py`.
