# G33-B: B/W Balance y Hi-Light Detail por la rama nativa del APC (12-11-2026)

Continúa [G33](g33-pp-black-knee-detail-still.md) §2 y [G34](g34-auditoria-estatica-pp-nucleo.md). **Trabajo offline**: capstone y bytes sobre `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21) y lectura del volcado de NVRAM `20261105-volcado-total-nvram` con `pmca.backup`. Sin REA, sin VM y sin cámara. No se instaló nada. Código: `scripts/gui/pp_bwhl_patch.py`; prueba: `tests/test_g33b_pp_bwhl.py` (4 pruebas con Unicorn sobre los sitios reales).

## 1. Origen de `ctx+0x139…0x13f` (VERIFICADO con bytes): son los bytes Detail del PP

| Eslabón | Evidencia |
|---|---|
| `cfg` → `cfgW` | `0x437dfd58`: `memcpy(0x43ed4d28+0x48, src, 0x560)`; el llamador `0x438088d6` toma `src` de `0x43804de8`, que devuelve `0x43EDF684` (el `cfg` de G34). `cfgW = 0x43ED4D70`, con la misma disposición |
| `cfgW` → instantánea | `0x438b83a0(dst, src)`: `src = cfgW` (getter `0x437dfe4c` + 0x40) y `dst = this+0x20` (llamadores `0x43afa124`/`0x43afa40a`, desde `0x43afa0ce`). En `0x438b8642…0x438b86be` hace `dst[0x130+i] = src[0x150+i]` para `i = 0…0xf` |
| Instantánea = `ctx` del APC | `0x438cb4ca`/`0x43b001fc` llaman a `0x437d8698(P+0x30e0, P+0x20)`, y la cadena `0x437d8732` → `0x43af6388` → `0x438b3ea8` → `FUN_438b11f0`/`FUN_438b177c`/`FUN_438b2070` pasa ese `P+0x20` como `ctx`. `P` y el `this` de `0x43afa0ce` son la misma clase: los dos usan `[this+0x4ad0]` con el mismo patrón (`≠0 → +0x20`) |
| Resultado | `ctx+0x139…0x13f = cfg+0x159…0x15f` = Detail **Mode, Level, V/H, B/W, Limit, Crispening, Hi-Light**. La semántica de los lectores lo confirma: Mode `== 1` (Manual), Level con signo (compara con 7, 3, 1, 5, −4…), B/W y Hi-Light con índice 0…4 |

G33 decía que «nadie las rellena»: el barrido lineal no veía la escritura porque pasa por la base `this+0x20`. Queda corregido.

## 2. La bandera `0x43f9a1c2` (VERIFICADO): propiedad de Backup `0x30136`, que vale 0 en la cámara

- La ranura GOT `0x44026284` (GOT `0x4401eee4` + `0x73a0`) apunta a `0x43f9a1c2`. Ocho funciones leen ese desplazamiento, y todas lo hacen en modo lectura (`ldrb r2,[r3]`): `0x438b0d20`, `0x438b0f16`, `0x438b154a`, `0x438b18ee`, `0x438b32b4`, `0x438b3ad8`, `0x438b4390` y `0x438b571c`. **En `av-cam` no hay ninguna escritura.**
- `0x43f9a1c2` es la entrada 133 de la tabla de punteros `0x43ff3200` (148 entradas). La tabla paralela de IDs de Backup (`0x43ff2fac`, o `0x43ff345c` según una bandera) le asigna la ID **`0x30136`** (variante `0x3003f`). `0x4378bb5c` registra las dos tablas en el servicio «LoadData» (`0x435613e8`, R58). Comprobación cruzada: la entrada 0 es `0x43e964a4` = `caps` de G27, con ID `0x30000`.
- En el volcado real, `0x30136` y `0x3003f` son idénticas (320 B): **`[0] = 0`**, `[1…0xa] = 01 01 00 01 01 01 10 10 10 10` y **`[0x12…0x16]` (B/W) y `[0x1b…0x1f]` (Hi-Light) a cero**. Sony no activa esta rama en la A6000 ni rellena sus tablas.

## 3. Qué hace la rama nativa (VERIFICADO; los nombres «yld»/«zoukou» son de G33)

| Sitio | Función | Condición | Efecto |
|---|---|---|---|
| `0x438b154a` | `FUN_438b11f0` | `[flag]==1`, Mode `==1` | **Hi-Light**: `sp+0x7c` (2.º umbral interpolado, `r0`) pasa a ser `sp+0x7a` (1.º, `r7`) + `T[0x1b+i]` (si `i>4`, se usa `0x1b`) |
| `0x438b18ee` | `FUN_438b177c` | ídem | **B/W**: `T[0x12+i]` → nibble bajo en `sp+0x34` y nibble alto en `sp+0x36` |
| `0x438b0d20` / `0x438b0f16` | `0x438b0a1c`/`0x438b0930` | ídem con `ctx2+0x412…0x418` | las mismas operaciones Hi-Light/B/W sobre otra copia (`0x437d80c4`, `0x437d91de` copian `+0x410…0x41c`). **NO_VERIFICADO**: de dónde sale esa copia |
| `0x438b32b4`, `0x438b3ad8`, `0x438b4390`, `0x438b571c` | coring, ganancias y otros | ídem | Limit/Crispening, Level y V/H nativos. Se dejan cerrados para no duplicar `pp_gain`/`pp_coring` de G33 |

La rama nativa no deja ningún índice sin efecto: en Manual **sustituye** valores que el núcleo calcula. Con las tablas de Sony a cero, abrir la bandera juntaría los dos umbrales de Hi-Light y anularía B/W. No conviene forzar la bandera.

## 4. Parche mínimo (construido offline, sin integrar en el CFW ni instalar)

`pp_bwhl_patch.patches(base, cave, hl=HL, bw=None)` no modifica código. Cambia el literal GOT de cada sitio elegido (`0x438b172c` para Hi-Light y `0x438b1a1c` para B/W, ambos con `0x73a0` original) por `cave − GOT`, de modo que `r3` apunte a una tabla propia `T` (`T[0] = 1`). Cada uno de esos literales tiene un solo lector, y los otros seis sitios conservan la bandera original. Ocupa 0x24 B de cueva (puntero + `T`). Por defecto solo activa Hi-Light; **B/W solo se activa si se pasan sus 5 bytes**, porque no hay ningún valor neutro conocido.

- La prueba (Unicorn sobre los sitios reales) comprueba: original con la rama cerrada (`sp+0x7c = r0`); con el parche en Manual, `sp+0x7c = r7 + HL[i]`; en Auto, sin cambios; B/W sin tocar salvo que se pida (con `0x43`, `sp+0x34 = 3` y `sp+0x36 = 4`); y las comprobaciones de los bytes originales.
- **No se asigna cueva**: el hueco de G18 está repartido entre G33, R86 y los trabajos en curso. La prueba usa `0x43faf290` solo dentro de la emulación.
- **Valores**: `HL = (0, 6, 12, 18, 24)` son estimaciones (`shortcut`). Ni Hi-Light ni B/W tienen valores de Sony para la A6000, porque la propiedad está a cero. Antes de integrarlo hay que leer `sp+0x7a/0x7c` y `sp+0x34/0x36` en ejecución (Auto) para elegir valores próximos a lo nativo.

## 5. G32-D: `caps[3]` (VERIFICADO el origen; sin parche)

- `caps = 0x43e964a4` es la entrada 0 de la misma tabla: propiedad de Backup **`0x30000`**. En el volcado real, `[3] = 0x40`, con el bit 1 a 0. El indicador monocromo (`0x437a2732`: `bl 0x43aeb0cc` = `(caps[3] >> 1) & 1`, luego `saturación < −7`) no se activa en la A6000.
- Hay dos opciones y no se ha hecho ninguna. (a) Escribir en NVRAM `0x30000[3] |= 2`: es un cambio de producción, necesita autorización y puede afectar a otros lectores del bit (no auditados). (b) Parchear el núcleo para que la condición sea «Color Mode = B&W» en lugar del bit, como la A7S (`id == 0x17`). Quitar solo el `bne` de `0x437a273a` **no es seguro**: cualquier Saturación PP ≤ −8 activaría el modo monocromo.

## 6. Límites

- Nada medido en cámara. Tampoco está verificado que las funciones APC se ejecuten con PP (G34 §3).
- La identidad `P` = `this` de `0x43afa0ce` se deduce del patrón común de campos y de la coincidencia semántica, no de una cadena de llamadas completa (NO_VERIFICADO del todo).
- Las escalas de Hi-Light y el significado de los nibbles B/W son NO_VERIFICADOS.
