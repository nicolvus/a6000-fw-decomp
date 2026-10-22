# S318 — Constructor paramétrico `0x436f3fc0`, tabla `0x43bbe1cc` y mapeo `0x43ad9162` (carril B)

**Resultado en una línea:** la clase de S316 tiene **dos** constructores: el ligero
`0x436f27b4` (sin argumento) y el **paramétrico `0x436f3fc0(obj, idx)`**. Éste fija el mismo
vptr (`0x43fce050`), lee `tabla[idx]` de **`0x43bbe1cc`** y lo pasa a **`0x43ad9162`**, que
traduce `1→0x10`, `2→0x40`, otro→`1` en `obj+0x2dc`. El único llamador directo localizado
(`0x436f2a8a`) usa **`idx = 0`**. La tabla deja de ser homogénea a partir del índice 7
(pares `u16`), por lo que el rango válido es **NO_VERIFICADO**. Todo exclusivo A7S.

Bytes + REA: `analysis/s318_ctor_mode/` (24 comprobaciones; 6 tests).

---

## 1. Constructor paramétrico `0x436f3fc0` (VERIFICADO)

```
0x436f3fc0  push {r4,r5,r6,r7,lr}
0x436f3fc4  ldr r5,[pc,#0x164]     ; base GOT
0x436f3fc6  mov r4,r0              ; obj
0x436f3fc8  mov r6,r1              ; idx
0x436f3fca  bl 0x436f2d44
0x436f3fce  ldr r3,[pc,#0x160]
0x436f3fd0  add r5,pc              ; r5 = 0x44024540
0x436f3fd2  movs r2,#8
0x436f3fd4  add.w r0,r4,#0x2dc
0x436f3fd8  movs r1,#0
0x436f3fda  ldr r3,[r5,r3]         ; [0x4402ac80] = 0x43fce048
0x436f3fdc  adds r3,#8             ; 0x43fce050
0x436f3fde  str r3,[r4]            ; vptr
0x436f3fe0  ldr r3,[pc,#0x150]     ; literal 0x436f4134 = 0x004ca1e6
0x436f3fe2  add r3,pc              ; PC=0x436f3fe6 -> 0x43bbe1cc
0x436f3fe4  ldr.w r3,[r3,r6,lsl#2]; tabla[idx]
0x436f3fe8  str r3,[sp]
0x436f3fea  mov r3,r2
0x436f3fec  bl 0x43ad9162          ; (obj+0x2dc, 0, 8, 8, tabla[idx])
```

El vptr coincide con el de S316 (`0x43fce050`), así que ambos constructores construyen la
misma clase. La diferencia es que éste inicializa `obj+0x2dc` con el código de modo.

## 2. Mapeo `0x43ad9162` (VERIFICADO)

```
0x43ad9162  push {r4,lr}
0x43ad9164  ldr r4,[sp,#8]     ; arg4 = tabla[idx]
0x43ad916a  cmp r4,#1
0x43ad916c..0x43ad9172  escribe arg1..arg3 y 0x81 en el objeto
0x43ad9174  beq 0x43ad917c
0x43ad9176  cmp r4,#2
0x43ad9178  bne 0x43ad9184
0x43ad917c  movs r3,#0x10       ; arg4 == 1
0x43ad9180  movs r3,#0x40       ; arg4 == 2
0x43ad9184  movs r3,#1          ; otro
0x43ad9188  str r3,[r0,#8]
0x43ad918a  adds r3,r3,r3
0x43ad918c  str r3,[r0,#0xc]    ; 2*valor
```

| `tabla[idx]` | `obj+0x08` | `obj+0x0c` |
|---|---|---|
| `1` | `0x10` | `0x20` |
| `2` | `0x40` | `0x80` |
| otro | `0x01` | `0x02` |

## 3. Tabla `0x43bbe1cc` (VERIFICADO el acceso; rango NO_VERIFICADO)

| Índice | `u32` | Comentario |
|---|---|---|
| 0 | `0x00000001` | usado por el único llamador (`idx=0`) |
| 1 | `0x00000002` | |
| 2 | `0x00000001` | |
| 3 | `0x00000000` | |
| 4 | `0x00000001` | |
| 5 | `0x00000000` | |
| 6 | `0x00000001` | |
| 7 | `0x01EC0000` | **empaqueta dos `u16`** (`0x0000`, `0x01EC`) |
| 8 | `0x00000001` | |
| 9 | `0x01EC0000` | |

Hasta el índice 6 los valores son códigos pequeños (0/1/2) compatibles con `0x43ad9162` y
con `0x436f2350` (S317). Desde el índice 7 la palabra empaqueta dos `u16`, de modo que la
lectura `lsl#2` deja de tener sentido como código. **NO_VERIFICADO:** cuántos índices usa el
firmware en runtime y si hay otra tabla/interpretación para 7+.

## 4. Llamador localizado (VERIFICADO)

`0x436f2a7c`:

```
0x436f2a7c  push {r4,r5,r6,lr}
0x436f2a7e  movs r1,#0            ; idx = 0
0x436f2a80  ldr r4,[pc,#0x28]     ; base GOT
0x436f2a82  ldr r3,[pc,#0x2c]
0x436f2a84  add r4,pc
0x436f2a86  ldr r5,[r4,r3]        ; objeto
0x436f2a88  mov r0,r5
0x436f2a8a  bl 0x436f3fc0
0x436f2a98  bl 0x439a2794         ; registro
0x436f2aa6  b.w 0x43ad96ca        ; fija el puntero global
```

Es el único `BL` a `0x436f3fc0` en el blob. El valor de `idx` en otras rutas no se observa.

## 5. Contraste A7S ↔ A6000 y relación con S316/S317

* Firma de 32 B de `0x436f3fc0`: **0 coincidencias** en la A6000 3.21.
* **S316 queda completado:** `0x436f27b4` es la variante ligera; `0x436f3fc0` es la
  paramétrica con la misma vtable.
* **S317 queda reforzado:** la misma tabla `0x43bbe1cc` se indexa en `0x436f4546` con
  `obj+0x2b4`; ambos consumidores coinciden en que los índices 0..6 son códigos 0/1/2.

## 6. Límites

* **VERIFICADO:** constructor, vptr, GOT, tabla y desplazamiento, mapeo 1/2/otro, llamador
  único con `idx=0`, exclusividad A7S.
* **NO_VERIFICADO:** rango válido de `idx`, significado de la tabla para índices ≥7, otras
  rutas de construcción en runtime, y relación con el silent shutter. S51 sin cambios.

---

## 7. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s318_ctor_mode/build_ctor_mode.py
.venv/bin/python analysis/s318_ctor_mode/verify_ctor_mode.py   # 24 comprobaciones
.venv/bin/python -m unittest tests.test_s318_ctor_mode          # 6 tests
.venv/bin/ruff check analysis/s318_ctor_mode tests/test_s318_ctor_mode.py
.venv/bin/mypy --ignore-missing-imports analysis/s318_ctor_mode
```

SHA-256 A7S `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`,
A6000 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.

REA: sesión única sobre el A7S (`analysis/rea-independent/input/av-cam-a7s.bin`), 626,5 s de
análisis; `procedure_pseudo_code(0x436f3fc0)` y `xrefs(0x4402ac80)` = `0x436f27be`,
`0x436f3fda`; cerrada al acabar.

**Límite global:** análisis estático; sin firmware ejecutado, sin cámara, sin flasheo y sin
pruebas físicas.
