# S633 — `[STK_*]`: etiquetas de error de los tres cálculos de `[STK]` y funciones de `[STK]`

**03-11-2026.** Documenta las cinco etiquetas pendientes de la familia STK del censo S178 (`[STK_AUTO_SAL]`, `[STK_COLOR_SIM]`, `[STK_C_SIM]`, `[STK_TOUCH_SIM]`, `[STK_T_SIM]`) y cierra las funciones contenedoras que [S501](s501-stk.md) dejaba sin resolver. **No son módulos**: son etiquetas de tres mensajes de error repetidos en tres funciones de `[STK]`.

Datos: [stk.json](../../analysis/s633_stk/stk.json). Verificador: `analysis/s633_stk/verify_stk.py` (A6000 fw3.21, base `0x43541000`; referencias PIC estrictas, barrido `bl` por patrón de halfwords, `analysis/camera_closure/`). Prueba: [test_s633_stk.py](../../tests/test_s633_stk.py).

## Evidencia comprobada (VERIFICADO contra bytes)

85 cadenas con prefijo `[TRK]: [STK…` (76 con el token `[STK]`, 9 con las etiquetas `[STK_*]`), 154 cargas `ldr`+`add pc` que resuelven a ellas, desde 8 funciones. Una cadena (`0x43cfc7ea`, `[TRK]: [STK] Stop Message Alloc Error`) no tiene ninguna referencia (ni `ldr`+`add pc`, ni literal de 32 bits en su rango).

| Función | Cadenas | Contenido (texto de las trazas) |
|---|---:|---|
| `0x43a35384` | 1 | `Message Alloc Error`; llamada `bl` desde `0x43a047ca` |
| `0x43a353d0` | 1 | `Message Alloc Error`; llamada `bl` desde `0x43a04b4a` |
| `0x43a3541c` | 3 | `Saliency CB is NULL (COMP)/(CANCEL)`, `Saliency Unexpected Interruption`; puntero Thumb en `0x4401b984` |
| `0x43a355d0` | 3 | `TouchSimilarity CB is NULL (COMP)/(CANCEL)`, `Touch Similarity Unexpected Interruption`; puntero Thumb en `0x4401b988` |
| `0x43a3574c` | 3 | `ColorSimilarity CB is NULL (COMP)/(CANCEL)`, `Color Similarity Unexpected Interruption`; puntero Thumb en `0x4401b98c` |
| `0x43a3588e` | 47 | `[STK_AUTO_SAL]` (3) y `PARAM ERR` de `p_yuv422`, `p_saturation_table`, `p_hsv_xyz`, `maps …`, `box …` |
| `0x43a36156` | 44 | `[STK_COLOR_SIM]` (2), `[STK_C_SIM]` (1) y `PARAM ERR` de `hsv …`, `premaps …`, `box …` |
| `0x43a36a06` | 52 | `[STK_TOUCH_SIM]` (2), `[STK_T_SIM]` (1) y `PARAM ERR` de `hsv …`, `premaps …`, `box …` |

Los punteros `0x4401b984`, `0x4401b988` y `0x4401b98c` son consecutivos (tabla de tres entradas con los bits Thumb de las tres funciones de callback).

## Las cinco etiquetas

Cada función grande abre con los mismos tres mensajes, con la etiqueta propia de su cálculo:

| Etiqueta | Mensajes | Función | A7S | A6300 |
|---|---|---|---:|---:|
| `[STK_AUTO_SAL]` | `CAM_MODE_CLOSE`, `CORE2 RESOURCE CONTENTION : %d`, `MEMORY ALLOC ERROR` | `0x43a3588e` | 3 | 0 |
| `[STK_COLOR_SIM]` | `CAM_MODE_CLOSE`, `CORE2 RESOURCE CONTENTION : %d` | `0x43a36156` | 2 | 0 |
| `[STK_C_SIM]` | `MEMORY ALLOC ERROR` | `0x43a36156` | 1 | 0 |
| `[STK_TOUCH_SIM]` | `CAM_MODE_CLOSE`, `CORE2 RESOURCE CONTENTION : %d` | `0x43a36a06` | 2 | 0 |
| `[STK_T_SIM]` | `MEMORY ALLOC ERROR` | `0x43a36a06` | 1 | 0 |

`[STK_C_SIM]` y `[STK_T_SIM]` son el tercer mensaje de `COLOR_SIM` y `TOUCH_SIM` con la etiqueta abreviada (el firmware las escribe así).

## Diferencial

`[STK]`: 76 coincidencias en A6000 fw3.21, 76 en A7S fw3.20 y 0 en A6300 fw2.01 (búsqueda exacta de bytes). Las cinco etiquetas `[STK_*]` tienen en A7S el mismo número de coincidencias que en A6000 y 0 en A6300. No se comparan cuerpos de función.

## Relación con el obturador

Desde cada una de las 8 funciones, por llamadas `bl` directas hasta profundidad 3, no se alcanza ninguna de las 7 funciones de obturador conocidas. Las llamadas indirectas (vtable/puntero) no se siguen. [S51](s51-decision.md) se mantiene.

## Alcance

Los nombres (`AUTO_SAL`, `COLOR_SIM`, `TOUCH_SIM`, `CORE2`, `CAM_MODE_CLOSE`) y los parámetros (`p_hsv_xyz`, `meanshift_*`, `af_island_*`…) son texto del firmware; este informe no atribuye significado a ninguno, ni unidades ni rangos, ni la relación con `[TRK]` y FC-FRC más allá de que las cadenas lleven el prefijo `[TRK]: `.

## Reproducción

```bash
.venv/bin/python analysis/s633_stk/verify_stk.py
.venv/bin/python -m pytest -q tests/test_s633_stk.py
```
