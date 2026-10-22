# S315 — Tres listas de registros aplicadas por `0x436f44c4` (carril B)

**Resultado en una línea:** el consumidor `0x436f44c4(obj, modo, lista)` recorre listas
terminadas en NULL y aplica registros de 5 B lógicos (6 B almacenados). Tiene **tres**
llamadas: `modo 2` → lista de **95** registros (`0x43fee3f8`), `modo 0` → lista de **5**
(`0x43fee578`), y `modo 2` → lista de **1** (`0x43fee590`). Las tres listas están en el
blob A7S; el consumidor y su getter son **código exclusivo A7S** (0 coincidencias de firma
en la A6000). El enlace de `modo 2` con el silent shutter queda **NO_VERIFICADO**.

Todo verificado por bytes: `analysis/s315_register_lists/` (`verify_lists.py`, 139
comprobaciones; 8 tests).

---

## 1. El consumidor `0x436f44c4` (VERIFICADO)

Entrada (push `2d e9 f0 41`), firma `void apply(obj /*r0*/, int modo /*r1*/, const void **lista /*r2*/)`.

| Dirección | Instrucción | Papel |
|---|---|---|
| `0x436f44d6` | `bl 0x436f5db8` | consulta de capacidad/modo |
| `0x436f450a` | `bl 0x43ad9230` | preparación |
| `0x436f450e` | `cmp r5,#2` | selección por `modo` |
| `0x436f451a` | `bl 0x436f2278` | ruta `modo==2` |
| `0x436f4526` | `ldrb r1,[r3]` | **dev** del registro |
| `0x436f452a` | `ldrh r2,[r3,#2]` | **reg:u16** |
| `0x436f452c` | `ldrb r3,[r3,#4]` | **data:u8** |
| `0x436f452e` | `bl 0x436f25f0` | aplica (ruta `modo==2`) |
| `0x436f4564` | `bl 0x43ad968a` | aplica (ruta `modo!=2`) |
| `0x436f4532` | `ldr r3,[r6],#4` | avanza el array de punteros |
| `0x436f4538` | `bne 0x436f4526` | hasta puntero NULL |

El registro lógico es de 5 B (`dev`, `reg`, `data`), pero el almacenamiento es de 6 B:
`u8 dev | u8 0 | u16 reg | u8 data | u8 0` (S314).

---

## 2. Las tres llamadas y sus listas (VERIFICADO)

| Llamada | `modo` (r1) | Lista (r2) | Cómo se resuelve |
|---|---|---|---|
| `0x436f5422` | `2` (`movs r1,#2` en `0x436f541e`) | **L1** `0x43fee590` | `ldr r2,[r4,r3]`, slot GOT `0x440292b0` |
| `0x436f5b32` | `2` (`0x436f5b2c`) | **L95** `0x43fee3f8` | `r0` del getter `0x436f4588` |
| `0x436f5b52` | `0` (`0x436f5b4e`) | **L5** `0x43fee578` | `ldr r2,[r6,r3]`, slot GOT `0x44025ec0` |

### 2b. Getter de L95 (VERIFICADO)

```
0x436f4588  ldr r3,[pc,#8]     ; literal 0x436f4594 = 0x0092ffb0
0x436f458a  ldr r2,[pc,#0xc]   ; literal 0x436f4598 = 0x00008400
0x436f458c  add r3,pc          ; PC=0x436f4590 -> r3 = 0x44024540 (base GOT)
0x436f458e  ldr r0,[r3,r2]     ; r0 = [0x4402c940] = 0x43fee3f8
0x436f4590  bx lr
```

Slots GOT comprobados directamente: `[0x4402c940]=0x43fee3f8`,
`[0x44025ec0]=0x43fee578`, `[0x440292b0]=0x43fee590`.

---

## 3. Contenido de las listas (VERIFICADO)

Todas terminan en NULL y sus registros tienen el mismo formato de 6 B con padding cero.

| Lista | Nº | Terminador | Registros (`reg`, `data`) |
|---|---|---|---|
| L95 | 95 | `0x43fee574` | 94×dev `0x81` + 1×dev `0x83`; `reg` 0x00…0xfc (ver JSON) |
| L5 | 5 | `0x43fee58c` | `(0x5f,0x00) (0x61,0x33) (0x88,0x00) (0x94,0x1d) (0xe3,0x00)` |
| L1 | 1 | `0x43fee594` | `(0x00,0x04)` |

**L5 no es subconjunto de L95:** comparte `0x5f` y `0x94`, pero añade `0x61`, `0x88` y
`0xe3`, que no aparecen en L95. L1 sí es un registro de L95 (el primero).

---

## 4. Contraste A7S ↔ A6000 (VERIFICADO)

Firmas de 24 B (consumidor) y 16 B (getter y llamadas): **0 coincidencias** en la A6000
3.21. Es decir, el mecanismo «lista de punteros + aplicar registros» tal como lo usa la
A7S no existe con ese código en la A6000; la A6000 tiene su propia tabla en la misma VA
(S314) pero otro consumidor.

| Elemento | A7S | A6000 |
|---|---|---|
| `0x436f44c4` (consumidor, 24 B) | presente | 0 |
| `0x436f4588` (getter L95, 16 B) | presente | 0 |
| `0x436f5422` / `0x436f5b32` / `0x436f5b52` (16 B) | presentes | 0 / 0 / 0 |

---

## 5. Lectura y límites

* **VERIFICADO:** existen tres listas, con esos tamaños, modos de llamada y resolución por
  GOT; el bucle lee 5 B lógicos y avanza por un array de punteros terminado en NULL.
* **INFERENCIA:** L95 es la lista «completa» de registros de sensor y L5/L1 son juegos
  reducidos usados en rutas concretas. No se afirma que L5 sea un subconjunto.
* **NO_VERIFICADO:** que `modo 2` de `0x436f44c4` sea el modo silent. Es un argumento
  distinto del selector `0x43826d58` (S314); la conexión no está demostrada.
* **NO_VERIFICADO:** la semántica física de cada `reg/data` (sin datasheet ni traza).
* **NO_VERIFICADO:** el escritor/origen de las listas y si cambian en runtime.

No cambia S51 (A=NO, B=NO, C=NO).

---

## 6. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s315_register_lists/build_lists.py
.venv/bin/python analysis/s315_register_lists/verify_lists.py    # 139 comprobaciones
.venv/bin/python -m unittest tests.test_s315_register_lists       # 8 tests
.venv/bin/ruff check analysis/s315_register_lists tests/test_s315_register_lists.py
.venv/bin/mypy --ignore-missing-imports analysis/s315_register_lists
```

SHA-256: A7S `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`,
A6000 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.

**Límite global:** análisis estático; sin firmware ejecutado, sin cámara, sin flasheo y sin
pruebas físicas.
