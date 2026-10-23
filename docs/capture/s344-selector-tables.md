# S344 — las dos tablas de 3 entradas de `0x436f6240` (selector de fila T1)

22-10-2026. Carril B. Sesión S344. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

S336 detectó que `0x436f6240` usa los bytes `+4/+5/+6` de la fila T como selectores de dos tablas de punteros, sin identificar las tablas ni el uso del valor devuelto.

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| Las tablas son `0x43bbeb64 = [0, 1, 4]` y `0x43bbef28 = [6, 5, 4]` | **VERIFICADO** | 3 u32 cada una |
| La primera **termina** en la base de T1 (`0x43bbeb70`); la segunda **empieza** al terminar T1 (`34×0x1c`) | **VERIFICADO** | aritmética de las direcciones |
| Selección: `row[5]==0` → `B[row[6]]` (si `row[6] ≤ 1`); `row[5]==1` → `A[row[4]]` (si `row[4] ≤ 2`) | **VERIFICADO** | árbol de comparaciones del cuerpo |
| `0x436f6278(idx)` selecciona la fila T1 (`mla` stride `0x1c`, límite `0x21`) y hace *tail-call* | **VERIFICADO** | `cmp r0,#0x21`, `movs r0,#0x1c`, `b.w 0x436f6240` |
| Con las filas reales, **32 de los 34 modos A7S dan 1** y solo `0x37`/`0x38` dan **4** | **VERIFICADO** | barrido de las 34 filas de T1 |
| En la A6000 los **13** modos dan 1 | **VERIFICADO** | barrido de las 13 filas |
| Ni `0x436f6240` ni `0x436f6278` tienen llamador estático | **VERIFICADO (negativo acotado)** | 0 `bl`, 0 literales de `…41`/`…79` |
| Qué significa el valor (`0/1/4/5/6`) | **NO_VERIFICADO** | sin llamador, no se puede seguir |
| Relación con el obturador silent | **NO** | los modos con valor 4 son `0x37`/`0x38`, exclusivos A7S y no silent |

**S51 no cambia (A = NO, B = NO, C = NO).**

## Detalle

```
43bbeb64  00000000 01000000 04000000            ; tabla A = [0, 1, 4]
43bbeb70  ...                                    ; T1 (34 filas × 0x1c)
43bbef28  06000000 05000000 04000000            ; tabla B = [6, 5, 4] (fin de T1)
43bbef30  ...                                    ; T3
```

Cuerpo de `0x436f6240`:

```
436f6240  4379       ldrb r3, [r0, #5]
436f6242  13b1       cbz r3, 0x436f624a        ; row[5]==0 -> tabla B
436f6244  012b       cmp r3, #1
436f6246  0ed1       bne 0x436f6266             ; otro  -> 0
436f6256  0279       ldrb r2, [r0, #4]          ; row[5]==1 -> tabla A
436f6258  022a       cmp r2, #2
436f625a  08d8       bhi 0x436f626e             ; >2 -> 0
436f625c  064b/7b44  ldr+add pc -> 0x43bbeb64
436f6260  53f82200   ldr.w r0, [r3, r2, lsl #2]
```

Envoltorio `0x436f6278`:

```
436f627c  2128       cmp r0, #0x21              ; índice de modo <= 33
436f6290  1c20       movs r0, #0x1c
436f6294  00fb0430   mla r0, r0, r4, r3         ; r3 = 0x43bbeb70 (T1)
436f629c  fff7d0bf   b.w #0x436f6240
```

## Reparto por modo

| Cámara | Modos | Valor 1 | Valor 4 |
|---|---|---|---|
| A7S fw3.20 | 34 | 32 | `0x37`, `0x38` |
| A6000 fw3.21 | 13 | 13 | — |

`0x37`/`0x38` son dos de los 22 códigos exclusivos del A7S (S333); no son silent (`0x4c`–`0x51`, que dan 1 como el resto).

## Límites

- Solo lectura estática; sin runtime, cámara ni flasheo.
- El negativo de llamadores es acotado: 0 `bl` y 0 literales no excluyen entrada por puntero calculado.
- No se asigna significado a `0`, `1`, `4`, `5`, `6`.
- El patrón exacto del cuerpo no aparece en la A6000; una implementación equivalente con otros registros no queda excluida.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s344_selector_tables/build_selector_tables.py
.venv/bin/python analysis/s344_selector_tables/verify_selector_tables.py   # 29 comprobaciones
.venv/bin/python -m unittest tests.test_s344_selector_tables               # 7 tests
```

Artefactos: `analysis/s344_selector_tables/selector_tables.json`, `build_selector_tables.py`,
`verify_selector_tables.py`, `tests/test_s344_selector_tables.py`.
