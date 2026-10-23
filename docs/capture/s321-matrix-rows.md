# S321 — la «tabla de 68 filas» de `0x43fee5ac` es la fila 1 de la matriz de 69 filas de `0x43fee598`

Trigésimo primera sesión del carril B. La cola pedía identificar el índice/consumidor de
una supuesta tabla de **68 filas** `{ptr, 16 B}` en `0x43fee5ac` y su relación con los
drive modes (S302).

**Resumen:** esa tabla **no existe como objeto independiente**. `0x43fee5ac` es la
**fila 1** de la matriz de registros por modo que ya midió S302, cuya base real es
`0x43fee598` con **69 filas** de `0x14 B` (`{u32 destino; u8 valores[16]}`) y terminador
`0` en `0x43feeafc`. El campo de 4 B no es un puntero a un descriptor: es el **destino**
donde el accesor escribe el byte del modo, y apunta al campo `data` de un registro de 6 B
`{dev, 0, reg:u16, data, 0}` de un pool contiguo de 98 registros.

---

## 1. La base: 69 filas, no 68 (VERIFICADO)

* Base real `0x43fee598`, stride `0x14`, cabecera 4 B + payload 16 B, terminador 0 en
  `0x43feeafc` = `0x43fee598 + 69·0x14`.
* Desde `0x43fee5ac` (`base + 0x14`) se cuentan exactamente **68** filas y se llega al
  **mismo** terminador: la cifra «68» de S314/cola es correcta pero la base está
  desplazada una fila.
* **Ninguna instrucción referencia `0x43fee5ac`**: 0 literales absolutos y 0 sitios
  `ldr/add pc`. La base `0x43fee598` solo aparece como **dato** en su propio slot
  (`0x44028844`), que es lo que lee el accesor; tampoco hay sitios `ldr/add pc` hacia ella.
  Es decir: la tabla se alcanza **solo** por el slot, y `0x43fee5ac` no se alcanza nunca.

Con esto queda **retirada** la premisa de una segunda tabla de 68 filas junto a la de 69.

**Contraste REA (una consulta, sesión ya abierta por el carril):** `xrefs(0x43fee5ac)`
devuelve `0x436f3942`, un punto **interior del bucle consumidor** (`ldr r4,[r2]`), no una
tabla; REA tampoco reconoce la entrada Thumb `0x436f3928` como procedimiento. La identidad
del consumidor se fija por bytes (vtable `0x43fce0f0 = 0x436f3929`, GOT
`0x44028844 = 0x43fee598` y el bucle `0x436f393a..0x436f3946`). Una consulta vacía no prueba
ausencia.

## 2. Formato de fila: el campo de 4 B es un destino de escritura (VERIFICADO)

`{u32 destino; u8 valores[16]}`. El accesor hace, por cada fila:

```
col  = mapa[modo]            ; solo en la A7S
val  = fila[4 + col]
*((u8*)fila.destino) = val
```

El destino apunta siempre al **byte `data`** (registro + 4) de un registro de 6 B
`{dev, 0, reg:u16, data, 0}`. Verificado en las 69 filas:

| Hecho | Valor |
|---|---|
| Destinos únicos | **69** |
| `registro = destino − 4` con `dev ∈ {0x81, 0x83}` y relleno 0 | **69/69** |
| Alineación `(registro − 0x44021ec2) mod 6` | **{0}** |
| Pool contiguo | `0x44021ec2 … 0x44022108`, **98** registros |
| Reparto de `dev` en el pool | **97 × `0x81`**, **1 × `0x83`** |
| Registro `0x83` | `0x440220d8`: reg `0x0017`, data `0x4a` (fila 68) |
| Registros del pool no alcanzados por la matriz | **29** |

Esto **corrige la lectura** de S302/S314 («cabecera = puntero a descriptor»): el puntero
no describe el registro, **es el lugar donde se escribe el valor**. La relación con el
registro es `destino = registro + 4`.

## 3. Consumidor: método virtual slot 40 de la clase de S316 (VERIFICADO)

A7S `0x436f3928`:

```
0x436f3928  ldr r2,[pc]  ; -> 0x43c9c5b5 (mapa modo->columna)
0x436f392a  ldr r3,[pc]  ; -> base de slots 0x44024540
0x436f3930  ldrb r1,[r2,r1]        ; col = mapa[modo]
0x436f3936  ldr r2,[r3,#0x4304]    ; slot 0x44028844 -> 0x43fee598
bucle:      ldrb r5,[r2,r1]  ... ldrb r5,[r5,#4] ; strb r5,[r4]
```

* **Tres instrucciones clave** re-decodificadas: `ldrb r1,[r2,r1]` (mapa),
  `ldrb r5,[r5,#4]` (payload), `strb r5,[r4]` (escritura al destino).
* El terminador del bucle es la cabecera 0 (`ldr r4,[r2]; cmp r4,#0`).
* **Slot 40** de la vtable `0x43fce050` (la clase de S315/S316): entrada
  `0x43fce0f0 = 0x436f3929` (Thumb) → offset `0xa0`. Es el **único** sitio que referencia
  la función (0 `bl`, 0 literal de código).
* **Segundo bucle** con la misma trama, tras la puerta `ldrb.w r2,[r0,#0x2b0]`
  (`cbz` → fin), aplicando una segunda matriz desde el slot `0x44026088` →
  **`0x43e8de00`, 64 B a cero en el blob**. Contenido y poblador **NO_VERIFICADOS**.

## 4. Relación con los drive modes: la matriz NO distingue el modo silent (VERIFICADO)

* El mapa `0x43c9c5b5` tiene **82 B** (códigos de modo `0x00..0x51`) y valores `0..14`:
  **15 columnas útiles**; el byte 15 del payload es 0 en las 69 filas (columna sin uso).
* Los **34 códigos** de S302 caen en solo **10 columnas** distintas
  (`0,1,3,4,6,7,8,9,10,12`).
* `0x4c`, `0x4d`, `0x4e` y `0x4f` → **columna 1**, compartida con **35 códigos más**
  (`0x02,0x03,0x22..0x28,0x2c..0x32,0x36..0x3c,0x40..0x46,0x4a..0x50` menos
  `0x4e`/`0x4f`; la columna 1 tiene 37 modos en total).
* **Ninguna columna es exclusiva de `0x4e`/`0x4f`**; por construcción, el modo silent
  escribe **exactamente los mismos valores de registro** que `0x4c`/`0x4d` y que los
  demás modos de la columna 1.
* La fila cuenta **registros**, no modos: la frase de la cola «los 69 drive modes de
  S302» mezcla las dos dimensiones. La matriz es `69 registros × 16 columnas (modo)`.

Confirma S302 en el punto exacto de discrepancia con S204: para **esta** matriz, silent
no se distingue; si S204 midió otra tabla (timings), ambas cosas pueden ser ciertas.

## 5. Contraste A6000: la misma clase, sin mapa (VERIFICADO)

| Hecho | A7S 3.20 | A6000 3.21 |
|---|---|---|
| Vtable | `0x43fce050`, **45** entradas | `0x43fcc090`, **45** entradas |
| Entrada 40 (offset `0xa0`) | `0x436f3929` → `0x436f3928` | `0x436d6571` → `0x436d6570` |
| Matriz primaria (slot) | `0x43fee598` (69 filas) vía `0x44028844` | `0x43fe9b74` (59 filas) vía `0x44022f8c` |
| Segundo bucle (puerta) | `[obj+0x2b0]`, slot `0x44026088` → `0x43e8de00` (ceros) | `[obj+0x266]`, slot `0x44026694` → `0x43e80160` (ceros) |
| Mapa modo→columna | **sí** (`0x43c9c5b5`, `ldrb r1,[r2,r1]`) | **no**: recibe la columna como argumento |
| Registro destino | 6 B `{dev,0,reg,data,0}`, `dest = reg+4` | **4 B** `{reg:u16, data:u8, 0}`, `dest = reg+2` |

Ambas cámaras tienen la **misma clase y el mismo mecanismo** (matriz por columna +
segunda matriz opcional). Lo que cambia es el **vocabulario de modos** (la A7S traduce
código→columna; la A6000 recibe la columna ya resuelta), el número de filas (69 vs 59) y
el layout del registro (la A7S lleva byte de dispositivo `0x81`/`0x83`).

Esto **no contradice** S315/S312: lo que allí tenía «0 firmas» son las **listas** L95/L5/L1
y sus aplicadores concretos, no esta clase, que existe en las dos.

## 6. Relación con las listas del mismo objeto (VERIFICADO)

* Pool de 98 registros; **L95** tiene 95 punteros a registros del pool.
* Quedan fuera de L95 **4** registros: `0x44021fac`, `0x44022018`, `0x44022072`,
  `0x44022090`.
* La matriz escribe en **66** registros que están en L95 y en **3** que solo están en L5
  (`0x44022018`, `0x44022072`, `0x44022090`).
* **L5** = esos 4 excluidos de L95 **más** `0x4402204e` (que sí está en L95); **L1** =
  `L95[0]` = `0x44021fee` (reg `0x0000`, data `0x04`).

Lectura (INFERENCIA, no verificada en runtime): la matriz **inicializa** los bytes `data`
de los registros y las listas **deciden qué registros se envían**; los 3 registros
solo-L5 existen precisamente porque la matriz también los necesita.

## 7. Impacto en la pregunta del silent shutter

* **No cambia S51 (A=NO, B=NO, C=NO).**
* La matriz **no es** una tabla de tiempos ni un selector de mecanismo: es un inicializador
  de valores de registro indexado por columna de modo, y el modo silent comparte columna
  con modos mecánicos. No hay aquí ningún indicio de lectura electrónica ni de
  integración a resolución completa.
* Tampoco es una vía de parche: escribir otra columna no crea un modo nuevo, porque el
  mapa modo→columna y el vocabulario de 34 códigos son los que limitan.

## 8. Límites

* Solo lectura estática de los blobs; sin runtime, cámara ni flasheo.
* La **segunda matriz** está a cero en el blob: su contenido, su poblador y la condición
  real de `[obj+0x2b0]`/`[obj+0x266]` son **NO_VERIFICADOS**.
* No se atribuye significado físico a ninguna columna, registro ni valor; «columna» es
  solo el índice del byte de payload.
* No se afirma equivalencia entre modos de la A7S y de la A6000, ni capacidad del IMX210.
* El destino se interpreta como `&data` por la alineación y el contenido del pool; no se
  ha observado la escritura en runtime.

## 9. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s321_matrix_rows/build_matrix_rows.py
.venv/bin/python analysis/s321_matrix_rows/verify_matrix_rows.py   # 138 comprobaciones
.venv/bin/python -m unittest tests.test_s321_matrix_rows            # 14 tests
.venv/bin/ruff check analysis/s321_matrix_rows tests/test_s321_matrix_rows.py
.venv/bin/mypy --ignore-missing-imports analysis/s321_matrix_rows
```

SHA-256 de los blobs:

* A7S fw3.20: `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`
* A6000 fw3.21: `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`

Evidencia completa: `analysis/s321_matrix_rows/matrix_rows.json`.
