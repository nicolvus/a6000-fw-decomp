# S317 — `obj+0x2b4` indexa tres tablas de `0x1c` B por modo (carril B)

**Resultado en una línea:** el campo `obj+0x2b4` de la clase de S316 se usa como índice
(`stride 0x1c`) en **tres tablas paralelas** (`T1 0x43bbeb70`, `T2 0x43bbf2ec`,
`T3 0x43bbef34`); de cada registro se leen `u32 @+0x14` y `u16 @+0x18` y se aplican a tres
destinos del objeto (`+0x16`, `+0x2e`, `+0xa5`). `T3→T2` dista exactamente **34 filas**.
La base se calcula con `PC = (add + 4)` con bit0 a 0 (no alineado a 4); es la lectura
correcta, confirmada por REA/Ghidra (`DAT+0x436f61ae/0x436f61c2/0x436f61d6`) y por las tablas
de enum 1/2 que consumen `0x43ad9162`/`0x436f2350`. La entrada es **exclusiva A7S**.

Verificado por bytes: `analysis/s317_mode_tables/` (39 comprobaciones; 6 tests).

---

## 1. Entrada `0x436f618c` (VERIFICADO)

Firma: `0x436f618c(obj /*r0*/, idx /*r1*/, modo /*r2*/)`.

| Dirección | Instrucción | Papel |
|---|---|---|
| `0x436f618c` | `cmp r1,#0xff` | `idx==0xff` → retorno |
| `0x436f6196` | `cmp r2,#1` | log si `modo==1` |
| `0x436f61a4` | `movs r2,#0x1c` | **stride 0x1c** |
| `0x436f61a6` | `muls r5,r2,r5` | `offset = idx * 0x1c` |
| `0x436f61ae` | `ldrh r1,[r3,#0x18]` | campo **u16** |
| `0x436f61b0` | `ldr r2,[r3,#0x14]` | campo **u32** |
| `0x436f61b6` | `bl 0x436f5f30` | aplica a `obj+0x16` (T1) |
| `0x436f61ca` | `bl 0x436f5f30` | aplica a `obj+0x2e` (T2) |
| `0x436f61e2` | `b.w 0x436f6140` | aplica a `obj+0xa5` (T3) |

## 2. Las tres tablas (VERIFICADO el cálculo de la base)

Las bases se recalculan desde los literales de `add pc`:

| Tabla | Literal | PC del `add` | Base calculada | Destino |
|---|---|---|---|---|
| T1 | `0x436f61ec` = `0x004c89c2` | `0x436f61ac` | `0x43bbeb70` | `obj+0x16` |
| T2 | `0x436f61f0` = `0x004c9126` | `0x436f61c4` | `0x43bbf2ec` | `obj+0x2e` |
| T3 | `0x436f61f4` = `0x004c8d5a` | `0x436f61d8` | `0x43bbef34` | `obj+0xa5` |

**Espaciado:** `T3→T2 = 0x3b8 = 34 × 0x1c` (34 filas exactas). `T1→T3 = 0x3c4 =
34 × 0x1c + 0xc` (34 filas más 12 B de separación). El índice `obj+0x2b4` se mueve, por
tanto, en el rango de 34 valores por tabla; el límite exacto no se observa estáticamente.

### 2b. Regla de PC y validación (VERIFICADO)

Para `add rX,pc` de 16 bits el valor es `(dirección + 4)` con bit0 a 0, **no** alineado a 4.
Con la fórmula alineada a 4 se obtendrían `0x…e6e/0x…2ea/0x…f32`, un sesgo de 2 B que además
produce valores `0x10003…` incompatibles con los consumidores. La lectura correcta
(`0x…e70/0x…2ec/0x…f34`) da valores 0/1/2, que es lo que comparan `0x436f2350` y `0x43ad9162`.
REA/Ghidra calcula las mismas bases.

## 3. Campos leídos (VERIFICADO)

De cada registro de `0x1c` B se leen `u32 @+0x14` y `u16 @+0x18`; la entrada los pasa a
`0x436f5f30(obj_destino, u32, u16, ...)` o a `0x436f6140`. Los campos `+0x00`, `+0x04` y
`+0x1a` no se leen en esta ruta.

## 4. Escritores de `obj+0x2b4` (NO_VERIFICADO)

El barrido de instrucciones `str* [rX,#0x2b4]` encuentra **111** sitios en el blob; la
mayoría pertenecen a otros objetos con el mismo offset. No se puede atribuir ninguno a esta
clase sin resolver la identidad del objeto (S314 dejó abierto el escritor de `[ctx]`).
Consecuencia: **quién fija `idx` y en qué rango** sigue NO_VERIFICADO.

## 5. Contraste A7S ↔ A6000 (VERIFICADO)

La firma de 24 B de `0x436f618c` tiene **0 coincidencias** en la A6000 3.21. La ruta de
tablas por modo es exclusiva A7S, coherente con S315/S316.

---

## 6. Lectura y límites

* **VERIFICADO:** entrada, stride `0x1c`, tres bases calculadas, espaciado de 34 filas entre
  T3 y T2, campos `+0x14`/`+0x18`, destinos `+0x16/+0x2e/+0xa5`, exclusividad A7S.
* **INFERENCIA:** las tres tablas son juegos paralelos por modo (misma longitud y estructura);
  el índice `+0x2b4` es el modo/columna.
* **NO_VERIFICADO:** la alineación real de las tablas, el rango válido del índice, el escritor
  de `+0x2b4`, la semántica de los campos y el enlace con el silent shutter.
* **NO_VERIFICADO:** que las 34 filas coincidan con los 34 códigos de S302 (`0x43fee370`):
  es otra dirección y otra estructura; no se afirma identidad.

No cambia S51 (A=NO, B=NO, C=NO).

---

## 7. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s317_mode_tables/build_mode_tables.py
.venv/bin/python analysis/s317_mode_tables/verify_mode_tables.py   # 39 comprobaciones
.venv/bin/python -m unittest tests.test_s317_mode_tables            # 6 tests
.venv/bin/ruff check analysis/s317_mode_tables tests/test_s317_mode_tables.py
.venv/bin/mypy --ignore-missing-imports analysis/s317_mode_tables
```

SHA-256 A7S `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`,
A6000 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.

**Límite global:** análisis estático; sin firmware ejecutado, sin cámara, sin flasheo y sin
pruebas físicas.
