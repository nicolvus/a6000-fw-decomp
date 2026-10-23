# S329 — ¿Hay una tabla de tiempos por modo en el A7S? (carril B)

22-10-2026. Carril B (imager: estado, drive modes y gates). Sesión S329. **Solo investigación estática: sin ejecutar firmware, sin cámara, sin flasheo.** Autoridad = bytes de `av-cam.bin` (A7S fw3.20 `b857d338…`, A6000 fw3.21 `b60c845c…`), no REA.

## Pregunta

La cola pedía: «localizar la tabla de **tiempos** por modo del A7S (S202 §3) y comprobar si `0x4e`/`0x4f` difieren de `0x4c`/`0x4d`; si no aparece, cerrar la pregunta con un barrido de la región de tablas de modo».

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| **No existe una tabla de tiempos (frames/ms) por modo en el A7S** | **VERIFICADO (negativo acotado)** | Enumeración de todas las estructuras por modo + barrido de las dos regiones de tablas |
| La «tabla de tiempos» de S202 §3 es en realidad la **matriz de registros** de 69 filas: cada fila escribe **un** registro del sensor (valores, no tiempos) | **VERIFICADO** | `0x43fee598`, 69 × `0x14` B, 98 registros de 6 B en el pool; el consumidor escribe `fila[4+col]` |
| Las tablas T1/T2/T3 **no** contienen tiempos: sus filas son `(índice, máscara)` | **VERIFICADO** | Único consumidor `0x436f618c`: `ldr r2,[r3,#0x14]` → `mla 12*r2`; `ldrh r1,[r3,#0x18]` → `asrs` bit a bit |
| **`0x4e`/`0x4f` sí difieren de `0x4c`/`0x4d`**, y no en «1 registro» | **VERIFICADO** | Matriz de 69 filas: **14** registros distintos (`0x4e` vs `0x4c`) y **11** (`0x4f` vs `0x4d`) |
| `0x4c` ≡ `0x4d` | **VERIFICADO** | 0 registros distintos |
| Ningún registro tiene un valor **exclusivo** de las columnas silent 12/13 | **VERIFICADO** | La diferencia es la *combinación*; las 16 columnas son vectores distintos |
| **T2/T3 están 4 B por encima en S317/S326** | **VERIFICADO** | Bases del código `0x43bbf2e8`/`0x43bbef30`, no `0x43bbf2ec`/`0x43bbef34` |
| Semántica física de la máscara de 12 bits y del objeto `0x43dc02e0` | **NO_VERIFICADO** | Depende de runtime |
| Efecto de las bases corregidas sobre la selección de modo real | **INFERENCIA** | Índice ∈ {0,1} = 2 filas de B y espaciado exacto; sin ejecución |

**S51 no cambia (A = NO, B = NO, C = NO).**

## 1. Qué estructuras existen «por modo» en el A7S

| Estructura | Dirección | Forma | Contenido |
|---|---|---|---|
| Lista de códigos | `0x43fee370` | `u32[34]` | `0b 37 35 38 13 1f 05 18 … 4c 4d 4e 4f 50 51 08` (S324) |
| Mapa posición→columna | `0x43c9c5b5` | `u8[34]` | `0,0,1,1,3,3,4,…,12,13,12,13,14` (S325) |
| Matriz de registros | `0x43fee598` | `69 × {u32 dest; u8 v[16]}` | un registro del sensor por fila, 15 columnas usadas (S321) |
| Tablas T1/T2/T3 | `0x43bbeb70`, `0x43bbf2e8`, `0x43bbef30` | `34 × 0x1c B` | `(u32 @+0x00, u32 @+0x04, índice @+0x14, máscara @+0x18)` |
| Descriptores B | `0x43c9d09b` | `2 × 12 B` | fila 0 = identidad `0..11`; fila 1 = permutación `0,7,6,1,2,9,8,3,4,11,10,5` |

Ninguna contiene tiempos. La matriz contiene **valores de registro** (`data` de registros `{0x81,0,reg:u16,data,0}`); las T contienen **qué campos** se emiten.

## 2. El consumidor de T1/T2/T3: índice + máscara

Los cuatro literales PIC (`T1`, `T2`, `T3`, `B`) aparecen **una sola vez** en todo el blob → un único consumidor:

- `0x436f618c(obj, idx, flag)`: si `idx == 0xff` retorna; con `muls r5,r2,r5` (stride `0x1c`) recorre T1, T2 y T3 para el mismo `idx`, y para cada una:
  - `ldrh r1,[r3,#0x18]` → **máscara** (se extrae con `asrs r6,r1,r4` + `and #1`);
  - `ldr r2,[r3,#0x14]` → **índice** (`mla r6, r8=0xc, r2, B`) en la tabla B;
  - `0x436f5f30` (T1/T2) y `0x436f6140` (T3) escriben 12 pares `(flag, valor)` en `obj+0x16`, `obj+0x2e` y `obj+0xa5`; el valor sale de `[ip + 0x20 + off]` (T1/T2) o `[ip + 0x60 + off]` (T3) con `ip = *(0x44024808) = 0x43dc02e0`.

Consecuencias medidas:

- De los 28 B de cada fila, el código lee **6** (`+0x14..+0x17` y `+0x18..+0x19`); los otros **22 B no los lee nadie**. No hay hueco para tiempos.
- La tabla B tiene **2 filas**: `0x43c9d09b` y `+0x0c`; a partir de `+0x18` empieza la cadena `GCS2RxLink.SetInitParam unknown block se…`. Con las bases correctas, `+0x14` vale **0 o 1** en las tres tablas.
- Las máscaras son de 12 bits: T1 `{0x3ff, 0xc00, 0xf00, 0xffc}`, T2 `{0, 0x3ff}`, T3 `{0xf0, 0x1f8, 0xfff}`.

## 3. Corrección: las bases de S317/S326 están 4 B altas

S317 tomó como `add` las direcciones `0x436f61c2` (T2) y `0x436f61d6` (T3), que son las **lecturas de campo** (`ldrh r1,[r3,#0x18]`), no los `add r3,pc` reales (`0x436f61be` y `0x436f61d2`). Resultado:

| Tabla | Base del código | Base de S317 | Índices con la base del código | Índices con la de S317 |
|---|---|---|---|---|
| T1 | `0x43bbeb70` | `0x43bbeb70` | `{0}` | `{0}` |
| T2 | `0x43bbf2e8` | `0x43bbf2ec` | `{0}` | `{0, 0x3ff}` |
| T3 | `0x43bbef30` | `0x43bbef34` | `{0, 1}` | `{0xf0, 0x1f8, 0xfff}` |

Con las bases de S317 el «índice» cae fuera de las 2 filas de B; con las del código encaja exactamente y **T3→T2 = 0x3b8 = 34 × 0x1c**. Entre T1 y T3 quedan 8 B (`06 00 00 00 05 00 00 00`).

El sesgo se recalibró contra cadenas conocidas: de los pares `ldr rD,[pc,#imm]` + `add rD,pc`, **10 370** destinos son el inicio de una cadena solo con `PC=(add+4)` bit0 a 0 y **6** solo con `PC` alineado a 4 → se mantiene el sesgo vigente del carril. (Los 6 casos son `add` de otro idioma, p. ej. `ADR`; se listan en el JSON.)

**Consecuencia para S326:** las igualdades `0x4e ≡ 0x51` y `0x4f ≡ 0x50` **desaparecen** con la base correcta: difieren en `w0` (`0x02` frente a `0x03`). `0x4c ≡ 0x4d` sí se mantiene. También desaparece el «`+0x14 = 0x3ff`»: era el `+0x18` real (máscara) leído con 4 B de desplazamiento.

## 4. ¿Difieren `0x4e`/`0x4f` de `0x4c`/`0x4d`? (matriz de 69 filas)

Comparando el vector completo de 69 registros con el mapa de columnas de S325 (columna de `0x4c`/`0x4d` = 5; `0x4e`/`0x50` = 12; `0x4f`/`0x51` = 13):

| Par | Registros distintos |
|---|---:|
| `0x4e` vs `0x4c` | **14** |
| `0x4f` vs `0x4d` | **11** |
| `0x4e` vs `0x51` | 4 |
| `0x4f` vs `0x50` | 4 |
| `0x4c` vs `0x4d` | **0** |
| `0x4e` vs `0x4f` | 4 |

Además:

- Las **16** columnas son vectores distintos; las columnas 12 y 13 (silent) son únicas.
- **Ningún** registro tiene un valor exclusivo de las columnas silent: la diferencia es la combinación completa. (Comprobado: 0 valores exclusivos.)
- Por tanto la afirmación de S201/S204 «1 registro (`0x000c`/`0x000a`)» **no se reproduce** ni en la matriz ni en las tablas T; S324 ya lo había señalado para otra tabla, y aquí se confirma en la matriz.

## 5. Barrido de las regiones de tablas

Regiones barridas con paso de 4 B: `0x43bbd000..0x43bc0000` (tablas T) y `0x43fee000..0x43ff0000` (lista, mapa y matriz). Candidatos = arrays de **34 o 69** elementos `u16`/`u32` con valores ≤ `0xffff` y ≥ 3 distintos.

| Región | Candidatos | Referenciados por PIC | Con pinta de tiempo (1..20000, ≥ ⅓ distintos) | Estricto (≥ 30 distintos) |
|---|---:|---:|---:|---:|
| Tablas T | 7 722 | 80 | 0 | **0** |
| Lista y matriz | 3 760 | 60 | 2 | 1 |

El único candidato estricto es `0x43fef404` (`u16[69]`, valores 1..78): es una tabla de índices, no de tiempos (un tiempo de exposición/lectura no cabe en 1..78 y el consumidor no la escala). **No aparece ninguna tabla de 34/69 tiempos en frames ni en ms.**

## 6. A6000 (contraste)

`0x436d6b50` rechaza `modo > 0x47` (`cmp r2,#0x47` en `0x436d6b62`, bytes `47 2a`), frente a `cmp r3,#0x51` en el A7S (`0x436f3b54`, bytes `51 2b`). `0x4e`/`0x4f` quedan fuera del rango de la A6000 → no hay columna silent que comparar. Coherente con S324/S201.

## Límites

- Solo lectura estática: sin runtime, sin cámara, sin flasheo.
- Una consulta vacía no prueba ausencia: el negativo se sostiene en la enumeración de estructuras y en el barrido de bytes, no en falta de xrefs.
- No se asigna semántica física a ningún registro ni a la máscara de 12 bits: el mapeo bit→campo depende del objeto `0x43dc02e0` en runtime.
- La corrección de bases se apoya en (a) el sesgo calibrado (10 370 vs 6), (b) el rango del índice frente a las 2 filas de B y (c) el espaciado exacto `0x3b8`. No se ha ejecutado el consumidor.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s329_mode_timing_tables/build_mode_timing.py
.venv/bin/python analysis/s329_mode_timing_tables/verify_mode_timing.py   # 1202 comprobaciones, 0 fallos
.venv/bin/python -m unittest tests.test_s329_mode_timing                  # 13 tests
```

Artefactos: `analysis/s329_mode_timing_tables/mode_timing.json` (filas completas, desensamblado del consumidor, calibración de sesgo, barrido), `build_mode_timing.py`, `verify_mode_timing.py`, `tests/test_s329_mode_timing.py`.
