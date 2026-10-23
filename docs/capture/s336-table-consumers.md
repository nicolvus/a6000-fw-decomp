# S336 — Mapa completo de consumidores de T1/T2/T3 (carril B)

22-10-2026. Carril B. Sesión S336. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

S331/S334 afirmaron que de cada fila de 28 B el código solo lee `+0x14` y `+0x18` (22 B sin leer). ¿Es cierto para todas las tablas o solo para un consumidor?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| Las cuatro tablas (T1, T2, T3 y B) tienen **13 referencias PIC** en **7 funciones** | **VERIFICADO** | Barrido exhaustivo `ldr rD,[pc,#imm]` + `add rD,pc` → base |
| **Cinco** de esas funciones leen campos de la **fila**: `op_code_w0`, `copy_row_patch`, `sum_w0`, `index_and_mask`, `row_selectors_entry` | **VERIFICADO** | Reparto 2/3/2/3/1 referencias |
| «Solo `+0x14` y `+0x18`» vale **únicamente** para `0x436f618c` | **VERIFICADO** | `0x436f5f7c` copia `+0x00..+0x13`; `0x436f6240` lee `+4/+5/+6` |
| `0x436f5f7c` copia 20 B de la fila, parchea `+5`/`+7` si `[estado+0x18]&1` y los pasa a `0x43ada310` | **VERIFICADO** | `ldm.w lr!,{r0-r3}` + `ldr.w r3,[lr]`; `ldrb r3,[r7,#0x18]`; `strb.w r3,[sp,#0xb]`; `bl 0x43ada310` |
| `0x436f6240` usa los bytes `+4/+5/+6` de la fila para elegir un puntero de una de dos tablas | **VERIFICADO** | `ldrb r3,[r0,#5]`, `ldrb r2,[r0,#6]`, `ldrb r2,[r0,#4]`, `ldr.w r0,[r3,r2,lsl#2]` |
| `0x436f605c` suma `0x43ada4d8(w0 de T1) + 0x43ada4d8(w0 de T2)` | **VERIFICADO** | Dos `ldr r1,[r3,r5]`, dos `bl 0x43ada4d8`, `adds r0,r0,r6`, `uxth` |
| El **significado** de `w0` y de `+4/+5/+6` | **NO_VERIFICADO** | `0x43ada4d8 → 0x436f74c0` sin resolver |

**S51 no cambia (A = NO, B = NO, C = NO).**

## 1. Las 13 referencias

| Tabla | Sitio (`ldr`) | Función | Campos |
|---|---|---|---|
| T1 | `0x436f5ebe` | `op_code_w0` | `w0` |
| T2 | `0x436f5ee8` | `op_code_w0` | `w0` |
| B | `0x436f5f48` | `mask_helper_1` | — (descriptor) |
| T1 | `0x436f5f98` | `copy_row_patch` | `+0x00..+0x13` |
| T2 | `0x436f5fd6` | `copy_row_patch` | `+0x00..+0x13` |
| T3 | `0x436f600e` | `copy_row_patch` | `+0x00..+0x13` |
| T1 | `0x436f6072` | `sum_w0` | `w0` |
| T2 | `0x436f6084` | `sum_w0` | `w0` |
| B | `0x436f6158` | `mask_helper_3` | — (descriptor) |
| T1 | `0x436f61a2` | `index_and_mask` | `+0x14`, `+0x18` |
| T2 | `0x436f61ba` | `index_and_mask` | `+0x14`, `+0x18` |
| T3 | `0x436f61ce` | `index_and_mask` | `+0x14`, `+0x18` |
| T1 | `0x436f628e` | `row_selectors_entry` | fila completa |

## 2. `0x436f5f7c`: copia y parcheo

```
0x436f5f98: ldr r3, [pc, #0xb0]      ; base de T1/T2/T3 según la rama
0x436f5f9a: mov.w lr, #0x1c
0x436f5fa2: mla lr, lr, r6, r3       ; fila = base + 0x1c * índice
0x436f5fa6: ldm.w lr!, {r0, r1, r2, r3}
0x436f5faa: stm r7!, {r0, r1, r2, r3} ; copia 16 B a la pila
0x436f5fac: ldr.w r3, [lr]
0x436f5fb0: str r3, [r7]             ; +4 B → 20 B copiados
0x436f5fb8: ldrb r3, [r7, #0x18]     ; flag global [estado+0x18]
0x436f5fba: tst.w r3, #1
0x436f5fc0: ldrb.w r3, [sp, #9]      ; fila +5
0x436f5fc6: strb.w r3, [sp, #0xb]    ; fila +7 = 0 si el flag está puesto
0x436f5fd2: bl 0x43ada310            ; escritor de obj+0x16 / obj+0x2e
```

Es decir: la fila no es un registro opaco `(índice, máscara)`, sino una **tabla de campos** que se copia y se ajusta antes de escribirla.

## 3. `0x436f6240`: selectores `+4/+5/+6`

```
0x436f6240: ldrb r3, [r0, #5]
0x436f6242: cbz r3, 0x436f624a
0x436f6244: cmp r3, #1
0x436f6246: bne 0x436f6266            ; otro valor → 0
0x436f6256: ldrb r2, [r0, #4]         ; rama [+5]==1
0x436f6258: cmp r2, #2
0x436f625c: ldr r3, [pc, #0x18]       ; tabla A
0x436f6260: ldr.w r0, [r3, r2, lsl #2]
...
0x436f624a: ldrb r2, [r0, #6]         ; rama [+5]==0
0x436f624c: cmp r2, #1
0x436f6250: ldr r3, [pc, #0x20]       ; tabla B
```

## 4. Correcciones

- **S331/S334**: «22 B por fila sin leer» es cierto **solo** para `0x436f618c`; el resto de consumidores lee `+0..+0x13` (copia), `+4/+5/+6` (selectores) y `w0`.
- **S334**: `w0` no es solo un código de operación comparado con 1/2/3; también se pasa a `0x43ada4d8` y se **suman** los de T1 y T2 (`0x436f605c`).

## Límites

- Solo estático: no se ejecuta ninguno de los consumidores.
- El significado de `w0` y de `+4/+5/+6` sigue sin interpretar; no se afirma que sean ids, contadores ni modos.
- `0x43ada4d8` y `0x436f74c0` no se han resuelto.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s336_table_consumers/build_table_consumers.py
.venv/bin/python analysis/s336_table_consumers/verify_table_consumers.py  # 47 comprobaciones
.venv/bin/python -m unittest tests.test_s336_table_consumers               # 9 tests
```

Artefactos: `analysis/s336_table_consumers/table_consumers.json`, `build_table_consumers.py`, `verify_table_consumers.py`, `tests/test_s336_table_consumers.py`.
