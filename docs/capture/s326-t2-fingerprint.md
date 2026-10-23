# S326 — La tabla de «34 columnas» de S202/S204 es T2 (34 filas): huella de `0x4e`/`0x4f`

Trigésimo sexta sesión del carril B. Cierra la búsqueda abierta por S324: la tabla de
«34 columnas» que S202/S204 midieron **existe**, pero es una tabla de **34 filas** (una
por modo), no de 34 columnas: es **T2** (`0x43bbf2ec`, stride `0x1c`), ya medida por S317
como una de las tres tablas paralelas indexadas por `obj+0x2b4`.

**Resultado:** en T2, `0x4c`/`0x4d` llevan `+0x14 = 0x3ff` y `+0x18 = 2`; `0x4e` lleva
`+0x14 = 0` (un solo campo de diferencia) y `0x4f` lleva `+0x14 = 0` **y** `+0x18 = 3`.
Se reproducen las igualdades exactas `0x4e ≡ 0x51`, `0x4f ≡ 0x50` y `0x4c ≡ 0x4d`. Pero
**ninguno de los dos campos es exclusivo del modo silent**: `0x3ff` agrupa
`{0x13, 0x1f, 0x4c, 0x4d}` y `3` agrupa `{0x0b, 0x35, 0x4f, 0x50}`.

---

## 1. T1, T3 y T2: 34 filas de 7 palabras (VERIFICADO)

| Tabla | Base | Stride | Filas | Filas distintas en 27..32 |
|---|---|---:|---:|---:|
| T1 | `0x43bbeb70` | `0x1c` | 34 | 4 |
| T3 | `0x43bbef34` | `0x1c` | 34 | 1 (constante) |
| T2 | `0x43bbf2ec` | `0x1c` | 34 | 3 |

`T3` y `T2` son **contiguas**: `0x43bbef34 + 34·0x1c = 0x43bbf2ec`. El orden de filas se
toma del array `u32[34]` de `0x43fee370` (S325), donde las posiciones 27..32 son
`0x4c, 0x4d, 0x4e, 0x4f, 0x50, 0x51`.

**INFERENCIA** (no runtime): que el índice de fila sea la posición en ese array. Se apoya
en las 34 filas medidas por S317, en que S204 llegó a la misma comparación 29/30 vs 27/28
de forma independiente, y en la coherencia de los grupos que aparecen (abajo).

## 2. T2 fila a fila en el rango silent (VERIFICADO)

| Código | Pos | `+0x14` | `+0x18` | Resto de campos |
|---|---:|---:|---:|---|
| `0x4c` | 27 | **`0x3ff`** | 2 | `01000101`, 0,0,0,0 |
| `0x4d` | 28 | **`0x3ff`** | 2 | idem |
| `0x4e` | 29 | **0** | 2 | idem |
| `0x4f` | 30 | **0** | **3** | idem |
| `0x50` | 31 | 0 | **3** | idem |
| `0x51` | 32 | 0 | 2 | idem |

Diferencias:

* `0x4e` vs `0x4c`: **1** campo (`+0x14`: `0x3ff → 0`).
* `0x4f` vs `0x4d`: **2** campos (`+0x14`: `0x3ff → 0`; `+0x18`: `2 → 3`).
* `0x4e` vs `0x4f`: **1** campo (`+0x18`: `2 → 3`).

Igualdades exactas (los 28 B idénticos): **`0x4e ≡ 0x51`**, **`0x4f ≡ 0x50`**,
**`0x4c ≡ 0x4d`**.

## 3. Los campos no son una firma «silent» (VERIFICADO)

* `+0x14 = 0x3ff` aparece **solo** en `{0x13, 0x1f, 0x4c, 0x4d}` (4 de 34 modos); el resto
  vale 0.
* `+0x18 = 3` aparece **solo** en `{0x0b, 0x35, 0x4f, 0x50}` (4 de 34).

Es decir: la diferencia `0x4e`/`0x4f` vs `0x4c`/`0x4d` **no marca el modo silent**; marca
que `0x4c`/`0x4d` pertenecen al pequeño grupo del `0x3ff` (junto con `0x13`/`0x1f`) y que
`0x4f` pertenece al grupo del `3` (junto con `0x0b`/`0x35`). Los pares `0x4e ≡ 0x51` y
`0x4f ≡ 0x50` son la estructura más informativa: silent se agrupa con `0x50`/`0x51`, igual
que ocurría en la matriz de 16 columnas de S325 (columnas 12/13 compartidas).

## 4. Veredicto sobre S204

| Afirmación de S204 | Estado |
|---|---|
| Tabla de 34 (llamada «columnas») con `0x4e`/`0x4f` en 29/30 | **REPRODUCIDO** como 34 **filas** (T2) con el orden de `0x43fee370` |
| «Difieren mínimamente de `0x4c`/`0x4d`» | **REPRODUCIDO**: 1 campo (`0x4e`) y 2 campos (`0x4f`) |
| «1 registro cada una: `0x000c` y `0x000a`» | **NO reproducido**: los campos son `+0x14` (`0x3ff→0`) y `+0x18` (`2→3`) |
| Que la diferencia sea propia del modo silent | **NO**: los valores 0x3ff y 3 son compartidos por otros modos |

## 5. Impacto en la pregunta del silent shutter

* **S51 no cambia (A=NO, B=NO, C=NO).**
* Queda **cerrada** la búsqueda de la tabla de 34 de S202/S204: es T2, y no contiene un
  parámetro que aísle el modo silent — su diferencia con `0x4c`/`0x4d` es la pertenencia a
  dos grupos pequeños de valores, y silent se alinea con `0x50`/`0x51`.
* Con S325 (columnas 12/13 compartidas con `0x50`/`0x51`) y S326 (filas idénticas a
  `0x50`/`0x51`), la lectura más consistente es que **`0x4e`/`0x4f` son variantes de
  `0x50`/`0x51`** en la A7S, no una clase funcional separada. Sigue **NO_VERIFICADO** qué
  distingue a `0x50`/`0x51` de los modos mecánicos y si alguno de los cuatro implica
  obturación electrónica (no hay ninguna traza ni cadena que lo diga: S135/S309).

## 6. Límites

* Solo lectura estática; sin runtime, cámara ni flasheo.
* El emparejamiento **fila ↔ posición de modo** es **INFERENCIA** (ver §1); no se ha
  localizado el escritor de `obj+0x2b4`.
* No se atribuye significado a `+0x14` (`0x3ff`/0) ni a `+0x18` (2/3); no se afirma que
  sean tiempos, límites ni contadores.
* No se afirma equivalencia entre `0x4e`/`0x4f` y `0x50`/`0x51` más allá de la identidad
  de sus filas en T2 y de sus columnas en la matriz.
* S51 (A/B/C) no cambia.

## 7. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s326_t2_fingerprint/build_t2_fingerprint.py
.venv/bin/python analysis/s326_t2_fingerprint/verify_t2_fingerprint.py   # 45 comprobaciones
.venv/bin/python -m unittest tests.test_s326_t2_fingerprint              # 7 tests
.venv/bin/ruff check analysis/s326_t2_fingerprint tests/test_s326_t2_fingerprint.py
.venv/bin/mypy --ignore-missing-imports analysis/s326_t2_fingerprint
```

SHA-256 de los blobs:

* A7S fw3.20: `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`
* A6000 fw3.21: `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`

Evidencia: `analysis/s326_t2_fingerprint/t2_silent_fingerprint.json`.
