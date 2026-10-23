# S325 — El mapa de columnas se indexa por **posición**, no por código de modo

Trigésimo quinta sesión del carril B. **Corrige** la interpretación del mapa
`0x43c9c5b5` que hicieron S302 y S321 y, con ella, el veredicto «la matriz no distingue
el modo silent».

**Resultado:** `0x43c9c5b5` es una tabla **`posición -> columna` de 34 entradas**, no un
mapa `modo -> columna` de 82. El accesor recibe una **posición** (0..33) obtenida por una
búsqueda lineal del código de modo en el array `u32[34]` de `0x43fee370`. Consecuencia
directa: `0x4e` (posición 29) usa la **columna 12** y `0x4f` (posición 30) la **columna
13**, mientras que `0x4c`/`0x4d` (27/28) usan la **columna 5** → **la matriz sí distingue
el modo silent** (14 y 11 registros distintos).

---

## 1. El ayudante `0x43ada284` devuelve un índice (VERIFICADO)

```asm
0x43ada284  push {r4, lr}
0x43ada286  movs r0, #0
0x43ada288  b    0x43ada298
0x43ada28a  ldr r4, [r2], #4     ; siguiente u32 del array
0x43ada28e  cmp r1, r4
0x43ada290  bne  0x43ada296
0x43ada292  uxtb r0, r0
0x43ada294  pop  {r4, pc}        ; devuelve el INDICE
0x43ada296  adds r0, #1
0x43ada298  cmp r0, r3           ; r3 = numero de entradas
0x43ada29a  blo  0x43ada28a
0x43ada29c  movs r0, #0xff       ; no encontrado
```

Es una **búsqueda lineal** que devuelve la posición del valor buscado (o `0xff`). No
devuelve el valor: devuelve el índice.

## 2. La cadena de llamada pasa ese índice al accesor (VERIFICADO)

En el setter de modo/sub (`0x436f3b44`, slot 8 de la vtable):

```asm
0x436f3bb4  ldr r3,[pc]          ; offset 0x2cf0 -> slot 0x44027230
0x436f3bbc  ldr r2,[r6,r3]       ; array = 0x43fee370
0x436f3bbe  movs r3,#0x22        ; 34 entradas
0x436f3bc0  bl   0x43ada284      ; r1 = 0x44  -> indice en r0
0x436f3bc4  cmp  r0,#0xff
0x436f3bc6  mov  r1,r0           ; r1 = INDICE (0..33)
0x436f3bc8  strb.w r0,[r4,#0x1b8]
0x436f3bcc  beq  0x436f3c78      ; 0xff -> error
0x436f3bd2  ldr.w r3,[r3,#0xa0]  ; slot 40
0x436f3bd6  blx  r3              ; accesor(obj, INDICE, ...)
```

El accesor `0x436f3928` hace entonces `ldrb r1,[0x43c9c5b5, r1]`: el mapa se indexa con
una **posición**.

## 3. La tabla tiene 34 entradas, no 82 (VERIFICADO)

* `0x43c9c5b5[0..33]` = `00 00 01 01 03 03 04 04 04 04 04 04 05 05 05 06 09 0a 07 08 0b 0b
  02 09 0a 07 08 05 05 0c 0d 0c 0d 0e` — **todas ≤ 14**, coherentes con columnas de una
  fila de 16 B.
* Los **48 bytes siguientes** (`0x43c9c5d7..`) son una tabla distinta: periódica de 10
  (`7 × 1`, `3 × 0`), no una continuación del mapa.
* Con 34 valores posibles y un payload de 16 B, la lectura «modo→columna de 82 entradas»
  de S302/S321 queda **descartada**: usaría índices hasta `0x51` en un mapa de 34.

## 4. Mapeo corregido (VERIFICADO)

| Código | Posición | Columna |
|---|---:|---:|
| `0x4c` | 27 | **5** |
| `0x4d` | 28 | **5** |
| `0x4e` | 29 | **12** |
| `0x4f` | 30 | **13** |
| `0x50` | 31 | **12** |
| `0x51` | 32 | **13** |

Los 34 códigos completos están en `position_map.json` (`mapping`). Pares que comparten
columna: `{0x4e, 0x50} → 12` y `{0x4f, 0x51} → 13` (posiciones 29/31 y 30/32).

## 5. La matriz **sí** distingue el modo silent (VERIFICADO)

Comparando los valores de las columnas sobre las 69 filas de S321:

| Comparación | Registros distintos |
|---|---|
| `0x4e` (col 12) vs `0x4c` (col 5) | **14** (`0x01,0x08,0x09,0x0a,0x0b,0x0c,0x11,0x1f,0x28,0x3c,0x50,0x51,0x55,0x9a`) |
| `0x4f` (col 13) vs `0x4d` (col 5) | **11** (`0x08,0x0a,0x0c,0x11,0x1f,0x28,0x3c,0x50,0x51,0x55,0x9a`) |
| `0x4e` (12) vs `0x4f` (13) | **4** |

Es el **primer indicio estático positivo** de que el modo silent de la A7S escribe valores
de registro distintos de los modos mecánicos vecinos: no es solo un código de modo
distinto, cambia el contenido de la matriz.

## 6. Correcciones que esta sesión publica

| Documento | Afirmación anterior | Corrección |
|---|---|---|
| S302 §3, S321 §4 | «mapa modo→columna de 82 B» | **posición→columna de 34 B** útiles |
| S302 §3 tabla | `0x4e`/`0x4f` → columna **1** | `0x4e` → **12**, `0x4f` → **13** |
| S321 §4 | «ninguna columna es exclusiva de silent; la matriz no lo distingue» | **SUPERSEDED**: las columnas 12/13 no las usan `0x4c`/`0x4d`; la matriz **sí** distingue |
| S321 (resto) | 69 filas, destino de escritura, pool de 98 registros, A6000 sin mapa | **sigue vigente** |

La afirmación de S204 «1 registro (`0x000c`/`0x000a`)» **sigue sin reproducirse**: con esta
matriz las diferencias son 14 y 11 registros. Su tabla de 34 columnas continúa
**NO_VERIFICADA** (S324).

## 7. Impacto en la pregunta del silent shutter

* **S51 no cambia (A=NO, B=NO, C=NO)**: no se demuestra lectura electrónica ni integración
  a resolución completa; sigue siendo una diferencia de valores de registro del sensor,
  no un mecanismo.
* Pero se corrige un negativo: la A7S **sí** tiene un conjunto de valores de registro
  propio para `0x4e`/`0x4f`. Es el lugar natural donde mirar si el modo silent cambia
  tiempos de lectura (la tabla de 34 columnas de S202/S204) — siguiente paso.
* En la A6000 el setter corta en `0x47` (S324), de modo que estos códigos no existen en su
  interfaz; su matriz de 59 filas no recibe columnas 12/13 por esta vía.

## 8. Límites

* Solo lectura estática; sin runtime, cámara ni flasheo.
* No se atribuye significado físico a ningún registro ni valor; solo se constata que
  difieren.
* No se verifica que la ruta del setter sea la única que aplica la matriz: hay otros
  llamadores del slot 40 no atribuidos (el listado genérico de `blx` tras `[vt,#0xa0]`
  incluye muchas clases).
* La tabla de 34 columnas de S202/S204 sigue **NO_VERIFICADA**.
* S51 (A/B/C) no cambia.

## 9. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s325_position_map/build_position_map.py
.venv/bin/python analysis/s325_position_map/verify_position_map.py   # 41 comprobaciones
.venv/bin/python -m unittest tests.test_s325_position_map             # 7 tests
.venv/bin/ruff check analysis/s325_position_map tests/test_s325_position_map.py
.venv/bin/mypy --ignore-missing-imports analysis/s325_position_map
```

SHA-256 de los blobs:

* A7S fw3.20: `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`
* A6000 fw3.21: `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`

Evidencia: `analysis/s325_position_map/position_map.json`.
