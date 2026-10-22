# S316 — Clase dueña de las listas: constructor, vtable y slots `+0x38`/`+0x44` (carril B)

**Resultado en una línea:** el objeto que aplica las listas de S315 pertenece a una clase
cuyo constructor es **`0x436f27b4`**, cuya vtable (metadata) está en **`0x43fce048`** y cuya
tabla de **45** funciones empieza en **`0x43fce050`**. Los dos métodos que aplican listas
(`0x436f5a14` y `0x436f53f4`) ocupan los slots **`+0x38`** y **`+0x44`**. El constructor se
alcanza por el slot GOT **`0x4402ac80`** y se invoca desde el wrapper/vtable-slot `+0x04`
**`0x43ad9840`**. Toda la clase es **exclusiva A7S** (0 coincidencias en la A6000).

Verificado por bytes: `analysis/s316_class_vtable/` (`verify_class.py`, 81 comprobaciones;
6 tests).

---

## 1. Constructor `0x436f27b4` (VERIFICADO)

```
0x436f27b4  ldr r3,[pc,#0x28]     ; literal 0x436f27e0 = 0x00931d84
0x436f27b6  ldr r2,[pc,#0x2c]     ; literal 0x436f27e4 = 0x00006740
0x436f27b8  add r3,pc             ; PC=0x436f27bc -> r3 = 0x44024540 (base GOT)
0x436f27ba  push {r4,lr}
0x436f27bc  mov r4,r0
0x436f27be  ldr r3,[r3,r2]        ; [0x4402ac80] = 0x43fce048
0x436f27c0  adds r3,#8            ; r3 = 0x43fce050
0x436f27c2  str r3,[r0]           ; obj->vptr = 0x43fce050
0x436f27c4  add.w r0,r0,#0x394
0x436f27c8  bl 0x436f3644         ; inicializa el subobjeto +0x394
0x436f27ce  bl 0x436f279c
```

Por tanto: **vptr de los objetos = `0x43fce050`**; el slot GOT `0x4402ac80` contiene la
metadata `0x43fce048`.

## 2. Vtable `0x43fce048` (VERIFICADO)

| Campo | Valor |
|---|---|
| offset-to-top | `0` (`0x43fce048`) |
| typeinfo | `0x43feeb20` (`0x43fce04c`) |
| tabla de funciones | `0x43fce050 … 0x43fce100` |
| entradas | **45** |
| terminador | `0` en `0x43fce104` |

Slots relevantes (dirección = `0x43fce050 + slot`):

| Slot | Entrada | Destino | Papel |
|---|---|---|---|
| `+0x00` | `0x43fce050` | `0x436f27b4` | constructor (referencia circular de vtable) |
| `+0x04` | `0x43fce054` | `0x43ad9840` | wrapper: crea + registra |
| `+0x38` | `0x43fce088` | `0x436f5a14` | aplica listas con `modo` (S315) |
| `+0x44` | `0x43fce094` | `0x436f53f4` | aplica lista L1 con `modo 2` (S315) |

## 3. Wrapper `0x43ad9840` (VERIFICADO)

```
0x43ad9840  push {r4,lr}
0x43ad9842  mov r4,r0
0x43ad9844  bl 0x436f27b4      ; constructor
0x43ad9848  mov r0,r4
0x43ad984a  bl 0x439a2780      ; registro/publicacion
0x43ad984e  mov r0,r4
0x43ad9850  pop {r4,pc}
```

Es el slot `+0x04` de la misma vtable: crea el objeto y lo registra.

## 4. Campos del objeto usados por los métodos de listas (VERIFICADO)

| Campo | Uso | Sitio |
|---|---|---|
| `+0x13c` | subobjeto de trabajo | `0x436f44c8`, `0x436f450a` |
| `+0x1ac`, `+0x1b0` | comparados con `0x11`; `+0x1b0` se copia a `+0x1b4` | `0x436f5b14…0x436f5b64` |
| `+0x2b2` | byte de estado | `0x436f5a9c`, `0x436f5aa0` |
| `+0x2b4` | índice usado para seleccionar tabla | `0x436f4476`, `0x436f4546` |
| `+0x2dc` | subobjeto de aplicación | `0x436f4514` |
| `+0x394` | subobjeto inicializado en el constructor | `0x436f27c4` |
| `+0x3dc` | estado 0/1/2 con transiciones | `0x436f43c0…0x436f4414` |

El campo `+0x2b4` indexa una tabla de punteros (`ldr r0,[r3,r2,lsl#2]` en `0x436f4546`).
La tabla concreta y su dominio quedan **NO_VERIFICADOS** (no se confunde con la tabla de
34 códigos de S302 sin comprobarlo).

## 5. Contraste A7S ↔ A6000 (VERIFICADO)

Firmas: constructor 32 B, wrapper 16 B, métodos `0x436f5a14` (32 B) y `0x436f53f4` (24 B):
**0 coincidencias** en la A6000 3.21. La clase y su vtable son código exclusivo A7S, en
línea con S309/S312/S315.

---

## 6. Lectura y límites

* **VERIFICADO:** constructor, vptr, metadata de vtable, 45 entradas, slots `+0x04/+0x38/+0x44`
  y wrapper de creación/registro.
* **INFERENCIA:** la clase es el componente que aplica las listas de registros del sensor
  (S315); sus métodos `+0x38/+0x44` son los que eligen `modo`.
* **NO_VERIFICADO:** el nombre de la clase (no hay RTTI demangled en el blob); el significado
  del campo `+0x2b4`; quién instancia la clase en runtime; y que `modo 2` sea el silent.
* **NO_VERIFICADO:** la semántica física de los registros y del cluster `+0xae/+0xde..+0xea`.

No cambia S51 (A=NO, B=NO, C=NO).

---

## 7. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s316_class_vtable/build_class.py
.venv/bin/python analysis/s316_class_vtable/verify_class.py    # 81 comprobaciones
.venv/bin/python -m unittest tests.test_s316_class_vtable       # 6 tests
.venv/bin/ruff check analysis/s316_class_vtable tests/test_s316_class_vtable.py
.venv/bin/mypy --ignore-missing-imports analysis/s316_class_vtable
```

SHA-256: A7S `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`,
A6000 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.

**Límite global:** análisis estático; sin firmware ejecutado, sin cámara, sin flasheo y sin
pruebas físicas.
