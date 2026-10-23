# S324 — Auditoría de la contradicción «34 columnas» (S202/S204) vs «15 columnas» (S302/S321)

Trigésimo cuarta sesión del carril B. La cola pedía resolver la discrepancia entre dos
mediciones del mismo objeto aparente:

* **S202/S204**: la matriz de modos tiene **34 columnas**; `0x4e`/`0x4f` son las columnas
  **29 y 30**, y sus filas de registro difieren de `0x4c`/`0x4d` en **un** registro
  (`0x000c` y `0x000a`).
* **S302/S321**: la matriz de `0x43fee598` tiene **15 columnas útiles** (payload de 16 B),
  el mapa `0x43c9c5b5` asigna a `0x4e`/`0x4f` la **columna 1** y no hay columna exclusiva
  de silent.

**Resultado:** no son la misma tabla. El «29/30» de S204 es la **posición dentro del array
`u32[34]` de códigos de modo** (`0x43fee370`), no una columna de la matriz de 16 B; la
tabla de 34 columnas que S204 pudo medir **no se localiza** en esta sesión. Además se
cierra, por instrucciones, el **setter de modo/sub** (slot 8 de la vtable), que en la A6000
**rechaza** los códigos `0x4e`/`0x4f` con un límite exacto `0x47`.

---

## 1. `0x43fee370` es un `u32[34]`, no una lista de 34 bytes (VERIFICADO)

* 136 B (`0x43fee370 … 0x43fee3f7`), 34 palabras little-endian: `0b 00 00 00`,
  `37 00 00 00`, … La «lista de 34 códigos» de S302 son los **bytes bajos** de esas
  palabras; la coincidencia es exacta pero el objeto es un array de `u32`.
* Termina exactamente en `0x43fee3f8`, que es la base de **L95** (S315): no hay relleno ni
  una tabla intermedia.
* Posiciones verificadas: **27 → `0x4c`**, **28 → `0x4d`**, **29 → `0x4e`**, **30 → `0x4f`**.
  Es decir, el «29 y 30» de S204 coincide con la **posición en este array**, no con un
  índice de columna de la matriz de 16 B (que solo llega a 15).
* El array solo se referencia por su slot: un único literal, `0x44027230`.

## 2. El array es un recurso de la clase de S315/S316 (VERIFICADO)

El slot `0x44027230` se resuelve como `0x44024540 + 0x2cf0`, y el offset literal `0x2cf0`
aparece en **7** sitios, **5 de ellos dentro de la clase** de la vtable `0x43fce050`:

| Sitio | Contexto |
|---|---|
| `0x436f39b4` | constructor de mensaje de modo (`0x436f3990`) |
| `0x436f3b12` | método que combina `+0x1b0`/`+0x2b4` |
| `0x436f3bb4` | aplicación de modo (`0x436f3b44`…`0x436f3c0c`) |
| `0x436f403a` | constructor de estructura (`bl 0x436f365c`) |
| `0x436f4468` | aplicador de listas `0x436f44c4` (S315) |

`0x436f365c` guarda en `struct+0x00` el puntero **`0x43fee378`** (array + 8) y el
constructor de mensaje `0x436f36ac` copia **16 campos** (offsets `+4 … +0x1c`). No se
observa ninguna fila de 34 columnas ni un stride de 34/35/36/38 asociado a este array.

## 3. Setter de modo/sub = slot 8 de la vtable (VERIFICADO)

**A7S `0x436f3b44`** (vtable `0x43fce050`, entrada 8 = `0x436f3b45`):

```
cmp r3,#0        ; modo == 0 -> salir
cmp r3,#0x51     ; modo > 0x51 -> salir      (rango 1..0x51)
str.w r3,[r0,#0x1ac]        ; obj+0x1ac = modo
ldrb r1,[r1,#4]             ; sub
cmp r1,#1
strb.w r1,[r0,#0x2b0]       ; obj+0x2b0 = sub
bls  skip                   ; sub <= 1 -> conservar
... log ...
strb.w r3,[r4,#0x2b0]       ; sub > 1 -> 0
```

**A6000 `0x436d6b50`** (vtable `0x43fcc090`, entrada 8 = `0x436d6b51`): idéntico con
`cmp r2,#0x47` (rango **1..0x47**), `str.w r2,[r0,#0x170]` y `strb.w r1,[r0,#0x266]`.

Consecuencias verificadas:

* El campo que abre la **segunda matriz** (`+0x2b0` A7S / `+0x266` A6000) es el **`sub`**
  del par (modo, sub), no un flag booleano independiente. En el accesor de S321,
  `cbz` sobre ese campo ⇒ la segunda matriz se aplica solo con `sub != 0`.
  **INFERENCIA fuerte** (los dos setters coinciden); runtime **NO_VERIFICADO**.
* La A6000 **rechaza** `0x4e`/`0x4f` en el setter porque superan `0x47` — es el límite
  exacto que S204 describía como «`SetMode` los rechaza». **VERIFICADO**.

## 4. Censo de diferencias entre las columnas de la matriz de 16 B (VERIFICADO)

Sobre las 69 filas × 15 columnas de S321:

| Hecho | Valor |
|---|---|
| Pares de columnas comparados | **105** |
| Diferencia **mínima** entre dos columnas | **2 registros** (`0x00` y `0x0e`, columnas 7 y 9) |
| Pares que difieren en **1** registro | **0** |
| Registros escritos en cada aplicación | **69** (el bucle recorre todas las filas) |

Por tanto la afirmación de S204 «difieren en 1 registro (`0x000c`/`0x000a`)» **no es
reproducible con esta matriz**: ni existe un par con una sola diferencia, ni la aplicación
escribe un subconjunto de registros por modo. Medir «filas de registro» por modo exige una
tabla **distinta** (con una lista o una columna por modo), que esta sesión no ha localizado.

## 5. Veredicto sobre la contradicción

| Afirmación | Estado |
|---|---|
| `0x43fee370` es una lista de 34 bytes | **CORREGIDO**: es `u32[34]` (136 B) |
| `0x4e`/`0x4f` son «columnas 29/30» | **ACLARADO**: son **posiciones** en `u32[34]`, no columnas de la matriz de 16 B |
| La matriz tiene 34 columnas | **NO_VERIFICADO**: la de `0x43fee598` tiene 15 útiles; no se localiza otra de 34 |
| `0x4e`/`0x4f` difieren en 1 registro de `0x4c`/`0x4d` | **NO_VERIFICADO**: incompatible con la matriz de 16 B |
| A6000 rechaza `0x4e`/`0x4f` | **VERIFICADO**: límite `0x47` en el setter |
| `+0x2b0`/`+0x266` es el `sub` | **VERIFICADO** (setter); su efecto en la segunda matriz es **INFERENCIA** |

Es decir: S202/S204 y S302/S321 **no se contradicen sobre el mismo objeto**, porque el
«34» y el «29/30» de S204 pertenecen al array de códigos y a una tabla aún no localizada.

## 6. Impacto en la pregunta del silent shutter

* **No cambia S51 (A=NO, B=NO, C=NO).**
* Se refuerza, con un límite numérico exacto, que **la A6000 no admite los códigos de modo
  silent** en esta interfaz: su setter corta en `0x47`. No es solo ausencia de cadenas
  (S135/S309): el valor se rechaza en la puerta de entrada del modo.
* La única diferencia funcional encontrada entre los dos códigos silent de la A7S es que
  `0x4e` (sub 0) **no** aplica la segunda matriz y `0x4f` (sub 1) **sí**. Eso es materia de
  S323 (matriz dinámica), no de esta sesión; aquí solo queda documentado el mecanismo.

## 7. Límites

* Solo lectura estática; sin runtime, cámara ni flasheo.
* **No se localiza** la tabla de 34 columnas que S204 pudo medir: su existencia, contenido y
  correspondencia con los registros `0x000c`/`0x000a` quedan **NO_VERIFICADOS**.
* No se afirma que `0x4e`/`0x4f` no tengan diferencias de temporización en otra tabla; solo
  que **esta** matriz no las distingue.
* El mensaje de 16 campos (`0x436f36ac`) no se interpreta: no se afirma qué representan sus
  campos ni su relación con las columnas.
* S51 (A/B/C) no cambia.

## 8. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s324_columns_audit/build_columns_audit.py
.venv/bin/python analysis/s324_columns_audit/verify_columns_audit.py   # 53 comprobaciones
.venv/bin/python -m unittest tests.test_s324_columns_audit             # 8 tests
.venv/bin/ruff check analysis/s324_columns_audit tests/test_s324_columns_audit.py
.venv/bin/mypy --ignore-missing-imports analysis/s324_columns_audit
```

SHA-256 de los blobs:

* A7S fw3.20: `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`
* A6000 fw3.21: `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`

Evidencia: `analysis/s324_columns_audit/columns_audit.json`.
