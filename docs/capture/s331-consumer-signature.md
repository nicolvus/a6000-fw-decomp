# S331 — La fila de T1/T2/T3 es la posición del modo (corrige S317/S327/S330) (carril B)

22-10-2026. Carril B. Sesión S331. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Por qué esta sesión

S317 etiquetó `0x436f618c` como `(obj, idx, modo)`; S327 y S330 leyeron `obj+0x2b4` como **índice de fila** de T1/T2/T3 y concluyeron que solo se aplicaba la fila 0. Al revisar los **dos llamadores** con seguimiento de registros, la firma real es otra.

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| La fila de T1/T2/T3 la elige **r1 = posición del modo** (0..33) en `0x43fee370` | **VERIFICADO** | `mov r5,r1` + `muls r5,r2,r5` (r2=`0x1c`) en el consumidor; ambos llamadores pasan el índice de la búsqueda lineal |
| `obj+0x2b4` es un **flag de log**, no el índice de fila | **VERIFICADO** | Es `r2`; el consumidor hace `cmp r2,#1` y solo entonces llama a `0x438f7114`; después reutiliza `r2` como stride |
| `0x436f618c` y sus hermanos `0x436f61f8`/`0x436f60ac` comparten firma `(obj, posición, flag)` | **VERIFICADO** | Mismo prólogo `cmp r1,#0xff` + `mov r4,r0` + `mov r5/r8,r1` + `mov r6/r7,r2` |
| La búsqueda `0x43ada284` devuelve el índice (0..n−1) o `0xff` | **VERIFICADO** | `movs r0,#0`; `adds r0,#1`; `movs r0,#0xff` al agotar |
| **S327 queda refutado** en su lectura: el escritor de `obj+0x2b4` guarda el flag | **VERIFICADO** | Ver arriba |
| **S330 queda refutado**: T1/T2/T3 sí se aplican por modo | **VERIFICADO** | El índice no es `obj+0x2b4` |
| La diferencia silent en las tablas T es la **máscara de T2** (`0x3ff` → 0) | **VERIFICADO** | T2 `0x4c`/`0x4d` mask `0x3ff`; `0x4e`/`0x4f` mask 0; T1 y T3 idénticas |
| Que la máscara seleccione campos de un mensaje P2S | **INFERENCIA** | Los descriptores B solo dan offsets dentro de `0x43dc02e0` |

**S51 no cambia (A = NO, B = NO, C = NO).**

## 1. El consumidor

```
0x436f618c: cmp r1, #0xff
0x436f618e: push {r4, r5, r6, lr}
0x436f6190: mov r4, r0
0x436f6192: mov r5, r1        ; r5 = índice de fila
0x436f6194: beq 0x436f61e6    ; 0xff → retorna
0x436f6196: cmp r2, #1        ; r2 = flag
0x436f6198: bne 0x436f61a2
0x436f619a: ldr r0, [pc, #0x4c]
0x436f619c: add r0, pc
0x436f619e: bl 0x438f7114      ; solo si flag == 1
0x436f61a2: ldr r3, [pc, #0x48]
0x436f61a4: movs r2, #0x1c
0x436f61a6: muls r5, r2, r5    ; r5 = 0x1c * índice
```

## 2. Los dos llamadores

Setter de modo (slot 8, `0x436f3b44`):

```
0x436f3bc0: bl 0x43ada284       ; índice del código de modo en u32[34]
0x436f3bc6: mov r1, r0
0x436f3bc8: strb.w r0, [r4, #0x1b8]
...
0x436f3bce: ldr r3, [r4]
0x436f3bd2: ldr.w r3, [r3, #0xa0]   ; slot 40 = 0x436f3928 (matriz de registros)
0x436f3bd6: blx r3
0x436f3bd8: mov r0, r5              ; r5 = obj+0x1c
0x436f3bda: ldrb.w r1, [r4, #0x1b8] ; r1 = posición del modo
0x436f3bde: ldr.w r2, [r4, #0x2b4]  ; r2 = flag
0x436f3be2: bl 0x436f618c
```

Segundo llamador (`0x436f4472`):

```
0x436f4472: bl 0x43ada284
0x436f4476: ldr.w r2, [r4, #0x2b4]  ; flag
0x436f447a: mov r6, r0              ; índice
0x436f447e: mov r1, r6
0x436f4480: bl 0x436f618c
0x436f4486: mov r1, r6
0x436f4488: ldr.w r2, [r4, #0x2b4]
0x436f448c: bl 0x436f61f8           ; hermano
0x436f4492: ldr.w r2, [r4, #0x2b4]
0x436f4498: bl 0x436f60ac           ; hermano
```

Los tres aplicadores comparten `(obj, posición, flag)` y se invocan seguidos al cambiar de modo.

## 3. Consecuencia: diferencias por modo en las tablas T

Con las bases corregidas en S329 (`T1 0x43bbeb70`, `T2 0x43bbf2e8`, `T3 0x43bbef30`) y la fila = posición:

| Modo | Pos | T1 (idx, mask) | T2 (idx, mask) | T3 (idx, mask) |
|---|---:|---|---|---|
| `0x4c` | 27 | (0, `0x3ff`) | (0, **`0x3ff`**) | (1, `0xfff`) |
| `0x4d` | 28 | (0, `0x3ff`) | (0, **`0x3ff`**) | (1, `0xfff`) |
| `0x4e` | 29 | (0, `0x3ff`) | (0, **0**) | (1, `0xfff`) |
| `0x4f` | 30 | (0, `0x3ff`) | (0, **0**) | (1, `0xfff`) |
| `0x50` | 31 | (0, `0x3ff`) | (0, 0) | (1, `0xfff`) |
| `0x51` | 32 | (0, `0x3ff`) | (0, 0) | (1, `0xfff`) |

- `0x4e` vs `0x4c` y `0x4f` vs `0x4d`: **solo** cambia la máscara de T2 (`0x3ff` → 0). T1 y T3 son idénticas.
- `0x4e` vs `0x51` y `0x4f` vs `0x50`: difieren en `w0` (`0x02` vs `0x03`), no en la máscara.

Esto cierra la pregunta de S326 con la base correcta: la huella silent **existe** y es la máscara de T2, no un «campo `+0x14` = `0x3ff`» (eso era el `+0x18` real leído con 4 B de desplazamiento).

## 4. Correcciones

- **S317**: el tercer argumento no es el modo; es un flag de log.
- **S327**: `obj+0x2b4` no es el índice de fila; el índice es la posición del modo. El escritor del campo (constructor `0x436f3fc0`) guarda el flag.
- **S330**: la conclusión «solo se aplica la fila 0» queda **refutada**. El hallazgo del singleton sigue siendo válido, pero su efecto es que el flag vale 0 (sin log).
- **S326**: la lectura por posición era correcta; con la base corregida se mantiene `0x4c ≡ 0x4d` y caen `0x4e ≡ 0x51` / `0x4f ≡ 0x50`.

## Límites

- Solo estático: no se ejecuta el setter ni se observa el efecto de la máscara.
- El mapeo bit→campo depende de `0x43dc02e0` (runtime); no se atribuye semántica física.
- No se ha identificado quién consume los bloques `obj+0x16`, `obj+0x2e`, `obj+0xa5` (queda como S334).
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s331_consumer_signature/build_consumer_signature.py
.venv/bin/python analysis/s331_consumer_signature/verify_consumer_signature.py  # 157 comprobaciones
.venv/bin/python -m unittest tests.test_s331_consumer_signature                  # 10 tests
```

Artefactos: `analysis/s331_consumer_signature/consumer_signature.json`, `build_consumer_signature.py`, `verify_consumer_signature.py`, `tests/test_s331_consumer_signature.py`.
