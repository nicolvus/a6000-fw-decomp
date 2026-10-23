# S333 — Vocabulario de modos y columnas de matriz: A6000 vs A7S (carril B)

22-10-2026. Carril B. Sesión S333. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

Contrastar el vocabulario de modos: la A6000 acepta hasta `0x47` con **13** códigos y el A7S hasta `0x51` con **34**. ¿Cuántas configuraciones de registro distintas produce cada uno? ¿Hay algún modo «silent-like» en la A6000?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| El vocabulario de la A6000 tiene **13** códigos y el del A7S **34** | **VERIFICADO** | `0x43fea070` (A6000) y `0x43fee370` (A7S) |
| **12 de los 13** códigos de la A6000 existen también en la lista del A7S | **VERIFICADO** | Intersección de ambas listas |
| `0x2f` es **exclusivo de la A6000** | **VERIFICADO** | No está en los 34 del A7S |
| **22** códigos del A7S no existen en la A6000, entre ellos `0x4c`–`0x51` | **VERIFICADO** | Diferencia de conjuntos |
| La A6000 produce solo **7** vectores de registro distintos para sus 13 modos | **VERIFICADO** | Matriz `0x43fe9b74`, 59 filas × 13 columnas |
| El A7S produce **15** vectores distintos para sus 34 modos | **VERIFICADO** | Matriz `0x43fee598`, 69 filas × 15 columnas usadas |
| Dos modos que comparten columna escriben los mismos valores de registro | **VERIFICADO** | La matriz es la fuente de los bytes |
| Que compartir columna implique equivalencia funcional | **NO_VERIFICADO** | Las tablas T y el resto del flujo pueden diferenciarlos |

**S51 no cambia (A = NO, B = NO, C = NO).**

## 1. Cómo se elige la columna

- **A6000** (`0x436d6570`, slot 40): el setter pasa como `r1` la **posición del modo** (0..12) y el bucle escribe `matriz[i].data[r1]` en `matriz[i].dest`. No hay mapa intermedio: columna = posición.
- **A7S** (`0x436f3928`, slot 40): el setter pasa la posición, pero el applier la traduce con el mapa `0x43c9c5b5` (34 entradas) a una columna 0..14; la columna 15 no se usa.

## 2. Alias medidos

| Modelo | Modos | Vectores distintos | Grupos de alias |
|---|---:|---:|---|
| A6000 | 13 | **7** | `{0x05,0x07,0x10,0x18,0x19,0x1a}` y `{0x0b,0x2f}` |
| A7S | 34 | **15** | 12 grupos; p. ej. `{0x4c,0x4d}~{0x32,0x33,0x34}`, `{0x4e,0x50}`, `{0x4f,0x51}`, `{0x13,0x1f}`, `{0x0b,0x37}` |

Lectura: el vocabulario de la A6000 es más **grueso** (13 códigos → 7 configuraciones) y el del A7S más fino (34 → 15). Los modos silent del A7S **no** tienen una configuración de registro exclusiva: `0x4c`/`0x4d` comparten fila con tres modos «normales» y `0x4e`/`0x4f` con `0x50`/`0x51`. Su distinción, medida en S329/S331, está en la **máscara de la tabla T2**, no en la matriz.

## 3. Vocabulario

- Compartidos (12): `01 03 05 07 0a 0b 0f 10 12 18 19 1a`.
- Solo A6000 (1): `2f`.
- Solo A7S (22): `08 13 1f 30 31 32 33 34 35 36 37 38 3f 44 45 46 4c 4d 4e 4f 50 51`.

Los seis códigos silent (`0x4c`–`0x51`) están en el conjunto exclusivo del A7S, coherente con S324 (el setter de la A6000 corta en `0x47`).

## Límites

- Solo estático: no se ejecuta ningún modo ni se observa el sensor.
- Que dos modos compartan columna solo dice que la matriz escribe los mismos valores; las tablas T (S331) y el resto del pipeline pueden diferenciarlos.
- No se asigna semántica física a los registros ni a los vectores.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s333_mode_vocabulary/build_mode_vocabulary.py
.venv/bin/python analysis/s333_mode_vocabulary/verify_mode_vocabulary.py  # 20 comprobaciones
.venv/bin/python -m unittest tests.test_s333_mode_vocabulary               # 9 tests
```

Artefactos: `analysis/s333_mode_vocabulary/mode_vocabulary.json`, `build_mode_vocabulary.py`, `verify_mode_vocabulary.py`, `tests/test_s333_mode_vocabulary.py`.
