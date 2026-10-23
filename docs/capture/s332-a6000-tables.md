# S332 — El mecanismo por modo del A6000 frente al A7S (carril B)

22-10-2026. Carril B. Sesión S332. **Solo lectura estática de los blobs; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

S331 demostró que en el A7S la fila de T1/T2/T3 la elige la **posición del modo** y que cada fila es `(índice a descriptores, máscara de 12 bits)`. ¿Tiene el A6000 el mismo mecanismo? ¿Qué cambia?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| **El A6000 tiene el mismo mecanismo**: setter → búsqueda lineal → índice → matriz de registros → consumidor `(obj, posición, flag)` | **VERIFICADO** | `0x436d6b50` = [[disasm completo en el JSON]]; `0x436d8e6c` lee `+0x14`/`+0x18` con stride `0x1c` |
| La lista de modos del A6000 tiene **13** códigos (`0b 01 05 10 07 12 03 0a 0f 18 1a 19 2f`) | **VERIFICADO** | Puntero en el slot `0x44020c64 → 0x43fea070` |
| El consumidor del A6000 rellena **2** bloques (`obj+0x14`, `obj+0xa1`), el del A7S **3** (`obj+0x16`, `obj+0x2e`, `obj+0xa5`) | **VERIFICADO** | `0x436d8ebc..0x436d8edc`; S331 para el A7S |
| La tabla de descriptores del A6000 está en `0x43c949a7`, es **compartida** por los dos helpers y tiene **3** filas | **VERIFICADO** | Identidad, permutación (idéntica a la del A7S) y `1,1,1,1,0,…` |
| El A6000 usa **solo** el descriptor 0 (identidad) y **ninguna** máscara cero | **VERIFICADO** | 13 filas × 2 tablas: `+0x14 = 0`; máscaras `{0xf00, 0xfff}` |
| El A7S usa descriptores 0 y 1 y tiene **30** máscaras cero | **VERIFICADO** | T1/T2/T3, 34 filas cada una |
| El A6000 no tiene `0x4e`/`0x4f` | **VERIFICADO** | Lista de 13 códigos + límite `cmp r2,#0x47` en `0x436d6b62` |
| Que los bloques rellenados sean el mismo tipo de mensaje en ambos | **INFERENCIA** | Los offsets destino difieren |

**S51 no cambia (A = NO, B = NO, C = NO).**

## 1. El setter del A6000 replica el del A7S

```
0x436d6b62: cmp r2, #0x47              ; límite de modo (A7S: 0x51)
0x436d6b68: str.w r2, [r0, #0x170]     ; modo  (A7S: +0x1ac)
0x436d6b70: strb.w r1, [r0, #0x266]    ; sub   (A7S: +0x2b0)
0x436d6bb8: bl 0x43ad9438              ; búsqueda lineal (A7S: 0x43ada284)
0x436d6bc0: strb.w r0, [r4, #0x17c]    ; índice  (A7S: +0x1b8)
0x436d6bce: blx r3                     ; slot 40 = 0x436d6570 (matriz)
0x436d6bd0: mov r0, r5                 ; r5 = obj+0x18
0x436d6bd2: ldrb.w r1, [r4, #0x17c]    ; r1 = posición del modo
0x436d6bd6: ldr.w r2, [r4, #0x26c]     ; r2 = flag (A7S: +0x2b4)
0x436d6bda: bl 0x436d8e6c
```

Es la misma secuencia que S331 midió en el A7S (`0x436f3b50`), con los offsets del layout del A6000.

## 2. El consumidor del A6000

```
0x436d8eb0: ldr r3, [pc, #0x44]        ; tabla TA1
0x436d8eb2: movs r2, #0x1c
0x436d8eb4: muls r5, r2, r5            ; fila = 0x1c * posición
0x436d8ebc: ldrh r1, [r3, #0x18]       ; máscara
0x436d8ebe: ldr r2, [r3, #0x14]        ; índice de descriptor
0x436d8ec0: add.w r3, r4, #0x14        ; destino 1
0x436d8ec4: bl 0x436d8c48              ; helper con ventana ip+0x20
0x436d8ed0: add.w r3, r4, #0xa1        ; destino 2
0x436d8ed4: ldrh r1, [r5, #0x18]
0x436d8ed6: ldr r2, [r5, #0x14]
0x436d8edc: b.w 0x436d8e20             ; helper con ventana ip+0x60
```

Los dos helpers (`0x436d8c48`, `0x436d8e20`) son idénticos en forma a los del A7S: `mla 12*índice` sobre la tabla de descriptores, `ldrb [ip+off]` y 12 pares `(flag, valor)`.

## 3. Tablas del A6000

| Tabla | Base | Destino | Filas | `+0x14` | Máscaras | `w0` | `w4` |
|---|---|---|---:|---|---|---|---|
| `TA1` | `0x43bc20dc` | `obj+0x14` | 13 | 0 | `0xfff` (3 modos), `0xf00` (10) | 0 | `0x01000101` |
| `TA2` | `0x43bc2248` | `obj+0xa1` | 13 | 0 | `0xfff` (todas) | 4 | `0x01000001` |

Separación exacta `0x16c = 13 × 0x1c`. Descriptor `0x43c949a7`: fila 0 identidad, fila 1 permutación `0,7,6,1,2,9,8,3,4,11,10,5` (la misma del A7S), fila 2 `1,1,1,1,0,0,0,0,0,0,0,0`.

## 4. Comparación medida

| Magnitud | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| Modos en la lista | **13** | **34** |
| Límite del setter | `0x47` | `0x51` |
| Tablas por modo | **2** | **3** |
| Destinos | `obj+0x14`, `obj+0xa1` | `obj+0x16`, `obj+0x2e`, `obj+0xa5` |
| Filas de descriptor | **3** | **2** |
| Descriptores usados | `{0}` | `{0, 1}` |
| Máscaras | `{0xf00, 0xfff}` | `{0, 0xf0, 0x1f8, 0x3ff, 0xc00, 0xf00, 0xffc, 0xfff}` |
| Máscaras cero | **0** | **30** |
| Códigos silent | no | sí (`0x4e`/`0x4f`) |

Lectura: el **mecanismo** no es exclusivo del A7S; es la misma máquina con otro juego de datos. La diferencia de vocabulario (13 vs 34 modos) y la ausencia de `0x4e`/`0x4f` ya estaban en S324; lo nuevo es que el A6000 **nunca** desactiva los campos (ninguna máscara cero) y **nunca** usa la permutación de descriptores, mientras el A7S sí hace ambas cosas (la permutación en T3 y las máscaras cero en 30 de sus 34 modos).

## Límites

- Solo estático: no se ejecuta ninguno de los dos setters.
- Que los bloques sean el mismo tipo de mensaje (P2S u otro) es INFERENCIA: los offsets destino difieren y no se ha seguido su consumidor.
- No se asigna semántica física a las máscaras ni a los descriptores; el mapeo bit→campo depende de `0x43dc02e0` (A7S) y su análogo en el A6000, ambos en runtime.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s332_a6000_tables/build_a6000_tables.py
.venv/bin/python analysis/s332_a6000_tables/verify_a6000_tables.py   # 343 comprobaciones
.venv/bin/python -m unittest tests.test_s332_a6000_tables             # 11 tests
```

Artefactos: `analysis/s332_a6000_tables/a6000_tables.json`, `build_a6000_tables.py`, `verify_a6000_tables.py`, `tests/test_s332_a6000_tables.py`.
