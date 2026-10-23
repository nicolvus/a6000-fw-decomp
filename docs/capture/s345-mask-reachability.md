# S345 — la aplicación de la máscara no está condicionada por el modo (A7S ↔ A6000)

22-10-2026. Carril B. Sesión S345. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

La cadena `modo → fila T → pares → máscara u16 → 0x436f822c → MMIO` (S334/S335/S338) termina en una escritura de 12 bits. ¿Se aplica esa escritura en todos los modos o solo en algunos? ¿Hay un camino exclusivo del A7S para los modos silent?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| En el A7S, el tramo `0x436f4476..0x436f449c` llama **en línea recta** a `0x436f618c`, `0x436f61f8` y `0x436f60ac` | **VERIFICADO** | 0 ramas condicionales; tres `bl` consecutivos |
| `0x436f61f8` aplica la máscara **op 0** (`bl 0x43ada370` → `b.w 0x436f822c`) y `0x436f60ac` la **op 1** (`b.w 0x43ada402` → `b.w 0x436f822c`) | **VERIFICADO** | `0x436f6216`, `0x436f6234`, `0x43ada3a0`, `0x43ada42c` |
| Hay un **segundo sitio** en `0x436f5afe`, con puerta `0x43ad9b50(obj) != 0` | **VERIFICADO** | `bl 0x43ad9b50; cbz r0; … bl 0x436f61f8` |
| En la A6000 el tramo equivalente `0x436d8f46..0x436d8f6e` aplica las **mismas dos operaciones** (`0x43ad94d8` op 0, `b.w 0x43ad9512` op 1) también en línea recta | **VERIFICADO** | 0 ramas condicionales; `bl 0x43ad94d8`, `bl 0x436d8bd8`, `b.w 0x43ad9512` |
| Los cuerpos de `0x43ada370`/`0x43ada402` se reutilizan **byte a byte** en la A6000 (`0x43ad94d8`/`0x43ad9512`) | **VERIFICADO** | búsqueda de los primeros 16 B |
| Existe un camino de máscara exclusivo de los modos silent en el A7S | **NO** (refutado) | la aplicación es la misma para todo modo que pase por el tramo |
| La diferencia A7S/A6000 está en los **datos** (pares/máscaras), no en la alcanzabilidad | **INFERENCIA (alta)** | coherente con S329/S335/S341 |

**S51 no cambia (A = NO, B = NO, C = NO).**

## Detalle

### A7S — tramo rectilíneo

```
436f4476  ldr.w r2, [r4, #0x2b4]     ; flag de log
436f447a  mov r6, r0                 ; posición de modo (0x43ada284)
436f447e  mov r1, r6
436f4480  bl #0x436f618c             ; lee fila T (descriptor + máscara)
436f4484  mov r0, r5
436f4486  mov r1, r6
436f4488  ldr.w r2, [r4, #0x2b4]
436f448c  bl #0x436f61f8             ; pares -> máscara (op 0)
436f4490  mov r1, r6
436f4492  ldr.w r2, [r4, #0x2b4]
436f4496  mov r0, r5
436f4498  bl #0x436f60ac             ; pares -> máscara (op 1)
```

No hay ninguna rama entre las tres llamadas: se aplican las dos operaciones para **cualquier** modo que llegue a este tramo.

Aplicación efectiva:

```
436f6216  bl #0x43ada370     ; op 0
43ada3a0  b.w #0x436f822c

436f6234  b.w #0x43ada402    ; op 1 (tail)
43ada42c  b.w #0x436f822c
```

### A7S — segundo sitio (con puerta)

```
436f5aec  bl #0x43ad9b50
436f5af0  cbz r0, #0x436f5b04
436f5af6  ldrb.w r1, [r4, #0x1b9]
436f5afa  ldr.w r2, [r4, #0x2b4]
436f5afe  bl #0x436f61f8
```

Sólo la op 0, y sólo si `0x43ad9b50(obj) != 0`. Qué mide esa puerta: **NO_VERIFICADO**. Si no, y `[obj+0x1b0] == 0x11`, llama a `0x43ada3a4`.

### A6000 — tramo equivalente

```
436d8f46  mov r0, r4
436d8f48  add.w r1, r4, #0x14
436d8f4c  bl #0x43ad94d8            ; op 0 sobre el bloque obj+0x14
436d8f56  bl #0x436d8bd8
436d8f5c  add.w r1, r4, #0xa1
436d8f60  add.w r2, r4, #0xd4
436d8f64  movs r3, #1
436d8f6a  b.w #0x43ad9512           ; op 1 sobre obj+0xa1
```

Mismo patrón (dos operaciones, sin condicionales en el tramo), con los bloques `obj+0x14` y `obj+0xa1` que S332 ya documentó.

## Límites

- Solo lectura estática; sin runtime, cámara ni flasheo.
- «No condicionada por el modo» se refiere al **tramo rectilíneo** medido; no se ha probado la alcanzabilidad de la función que lo contiene hasta su origen.
- El equivalente del escritor de máscara en la A6000 no se sigue: solo se verifica que las dos operaciones están presentes y que reutilizan los mismos cuerpos.
- La puerta `0x43ad9b50` del segundo sitio del A7S no se ha identificado.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s345_mask_reachability/build_mask_reachability.py
.venv/bin/python analysis/s345_mask_reachability/verify_mask_reachability.py   # 18 comprobaciones
.venv/bin/python -m unittest tests.test_s345_mask_reachability                  # 6 tests
```

Artefactos: `analysis/s345_mask_reachability/mask_reachability.json`, `build_mask_reachability.py`,
`verify_mask_reachability.py`, `tests/test_s345_mask_reachability.py`.
