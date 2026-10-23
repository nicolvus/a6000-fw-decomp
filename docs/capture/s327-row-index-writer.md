# S327 — `obj+0x2b4` es el índice del constructor paramétrico, no una posición de modo

Trigésimo séptima sesión del carril B. Cierra el TODO abierto por S326: ¿quién escribe
`obj+0x2b4`, el índice con el que S317 leyó las tres tablas T1/T2/T3?

**Resultado:** hay **dos** escritores y **ninguno** deriva el valor de un código de modo:

1. `0x436f2d74` (`str.w r3,[r4,#0x2b4]` con `r3 = 0`): inicialización en el constructor
   base `0x436f2d44`.
2. `0x436f40fe` (`str.w r6,[r4,#0x2b4]`): final del **constructor paramétrico**
   `0x436f3fc0(obj, idx)`, donde `r6 = r1` desde la entrada (`0x436f3fc8`).

Su único llamador estático (`0x436f2a8a`) hace `movs r1,#0` → **idx = 0**. En la única
instancia visible, `obj+0x2b4 = 0`, de modo que T1/T2/T3 se leen en la **fila 0**.

**Consecuencia:** la correspondencia *fila ↔ modo* que S326 dejó como INFERENCIA **no tiene
soporte en este escritor**; las filas 29/30 de T2 (identificadas con `0x4e`/`0x4f`) **no son
alcanzables** por esta vía en la instancia visible.

---

## 1. Escritores (VERIFICADO)

Barrido de `str* [#0x2b4]` en el rango de la clase (`0x436f2000..0x436f7000`): **2** sitios.

| Sitio | Instrucción | Contexto |
|---|---|---|
| `0x436f2d74` | `str.w r3, [r4, #0x2b4]` | constructor base `0x436f2d44`; `r3 = 0` (`0x436f2d62`) |
| `0x436f40fe` | `str.w r6, [r4, #0x2b4]` | constructor paramétrico `0x436f3fc0`; `r6 = r1` (`0x436f3fc8`) |

Bytes del segundo: `c4 f8 b4 62` (`0xF8C4`/`0x62B4`).

## 2. El constructor paramétrico guarda su argumento (VERIFICADO)

```
0x436f3fc0  push {r4,r5,r6,r7,lr}
0x436f3fc6  mov  r4, r0        ; obj
0x436f3fc8  mov  r6, r1        ; idx
0x436f3fca  bl   0x436f2d44    ; constructor base (pone +0x2b4 = 0)
...
0x436f40fe  str.w r6,[r4,#0x2b4]   ; +0x2b4 = idx
```

Es el mismo constructor que S318 documentó (`0x436f3fc0(obj,idx)` con la tabla
`0x43bbe1cc` y el mapeo `1→0x10`/`2→0x40` en `+0x2dc`).

## 3. Único llamador estático con `idx = 0` (VERIFICADO)

```
0x436f2a7c  push {r4,r5,r6,lr}
0x436f2a7e  movs r1, #0
...
0x436f2a8a  bl   0x436f3fc0
```

S318 ya había fijado este único llamador. No se ha encontrado otro `bl` ni una referencia
literal con el bit Thumb en todo el blob.

## 4. Lectores (VERIFICADO)

**9** lecturas del campo (`ldr* [#0x2b4]`, excluyendo los `[pc,#…]`): `0x436f3ad0`,
`0x436f3b2c`, `0x436f3bde`, `0x436f3f56`, `0x436f4476`, `0x436f4488`, `0x436f4492`,
`0x436f4546`, `0x436f5afa`. Todas leen el campo; ninguna lo calcula a partir del modo.

## 5. Corrección de la inferencia de S326

| Afirmación de S326 | Estado tras S327 |
|---|---|
| T2 tiene 34 filas; `0x4e`/`0x4f` (pos 29/30) difieren de `0x4c`/`0x4d` en 1–2 campos | **VERIFICADO** (no depende del escritor) |
| Igualdades `0x4e≡0x51`, `0x4f≡0x50`, `0x4c≡0x4d` | **VERIFICADO** |
| La fila indexada es la posición del modo | **NO_VERIFICADO / sin soporte**: el índice es el argumento del constructor y vale 0 |
| Las filas 29/30 son alcanzables en la instancia visible | **NO**: solo se alcanza la fila 0 |

No se retiran las mediciones de S326 (contenido de las tablas); se retira **su lectura como
correspondencia con los modos**.

## 6. Impacto en la pregunta del silent shutter

* **S51 no cambia (A=NO, B=NO, C=NO).**
* Con esto, la «tabla de 34» de S202/S204 no queda ligada a los códigos de modo por ningún
  camino estático localizado: T1/T2/T3 son tablas por **variante de construcción** (índice
  del constructor), no por modo. Quien quiera sostener que `0x4e`/`0x4f` cambian esos
  campos tendrá que demostrar una instancia construida con otro `idx` (dinámica o desde
  otro módulo).
* La única huella silent que queda en pie es la de la **matriz de 16 columnas** (S325):
  columnas 12/13, compartidas con `0x50`/`0x51`.

## 7. Límites

* Solo lectura estática; sin runtime, cámara ni flasheo.
* El constructor paramétrico **podría** invocarse de forma dinámica con otro `idx` (tabla de
  punteros o módulo externo): no se descarta, solo consta un llamador estático con `idx=0`.
* No se interpreta el índice de construcción: no se afirma que seleccione un modo, un canal
  ni una variante de lectura.
* S51 (A/B/C) no cambia.

## 8. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s327_row_index_writer/build_row_index.py
.venv/bin/python analysis/s327_row_index_writer/verify_row_index.py   # 24 comprobaciones
.venv/bin/python -m unittest tests.test_s327_row_index_writer          # 6 tests
.venv/bin/ruff check analysis/s327_row_index_writer tests/test_s327_row_index_writer.py
.venv/bin/mypy --ignore-missing-imports analysis/s327_row_index_writer
```

SHA-256 de los blobs:

* A7S fw3.20: `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`
* A6000 fw3.21: `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`

Evidencia: `analysis/s327_row_index_writer/row_index_writer.json`.
