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
- Cueva: ver §8 (propuesta `0x43faf290`).
- **Valores**: `HL = (0, 6, 12, 18, 24)` son estimaciones (`shortcut`). Ni Hi-Light ni B/W tienen valores de Sony para la A6000, porque la propiedad está a cero. Antes de integrarlo hay que leer `sp+0x7a/0x7c` y `sp+0x34/0x36` en ejecución (Auto) para elegir valores próximos a lo nativo.

## 5. G32-D: `caps[3]` (VERIFICADO el origen; sin parche)

- `caps = 0x43e964a4` es la entrada 0 de la misma tabla: propiedad de Backup **`0x30000`**. En el volcado real, `[3] = 0x40`, con el bit 1 a 0. El indicador monocromo (`0x437a2732`: `bl 0x43aeb0cc` = `(caps[3] >> 1) & 1`, luego `saturación < −7`) no se activa en la A6000.
- Opciones: (a) escribir en NVRAM `0x30000[3] |= 2` (producción, necesita autorización; otros lectores del bit sin auditar), descartada; (b) parche del núcleo por tipo B&W, hecho en §7. Quitar solo el `bne` de `0x437a273a` **no es seguro**: cualquier Saturación PP ≤ −8 activaría el modo monocromo.

## 7. G32-D: parche por tipo B&W (construido offline, sin integrar ni instalar)

- **A7S** (`av-cam` fw3.20, por bytes): en `0x438c3b7a…0x438c3ba2`, monocromo = (`caps[3]` bit 1 **y** saturación `[+0x25]` ≤ umbral de tabla `[GOT…]+0x44`) **o** `[resumen+0x22] == 0x17` (id B&W).
- **A6000**: no tiene id B&W (tabla de tipos 1–7, G27). El tipo sí llega al resumen: `0x437aa8f8` hace `resumen[+0x31] = cfg+0x138` y B&W es el tipo 8. `scripts/gui/pp_bw_mono_patch.py` reescribe en el mismo sitio `0x437a2728…0x437a2743` (28 B, sin cueva; bytes originales comprobados): monocromo = (`+0x31 == 8`). Conserva `r1 = 1`, `r7` = saturación y `r3 = [r4+8]`, y las dos salidas originales (`strb` 1 en `0x437a2744` o 0 en `0x437a279e`).
- Prueba `tests/test_g32d_pp_bw_mono.py` (Unicorn sobre el sitio real): en el original, B&W no activa el monocromo con `caps[3] = 0x40` y la saturación −8 sí lo hace con el bit 1; con el parche, B&W lo activa y la saturación −8 o −32 y los tipos 0, 1, 7 y 9 no.
- **Requisito de integración**: la `libObj` tiene que enviar el tipo 8. `patch_libobj_pp.patch_bw` lo convierte en Movie (5) + saturación −8, y con este parche esa combinación ya no da monocromo. Al integrarlo hay que quitar `patch_bw` del constructor (archivo de otros agentes; no se ha tocado). El tipo 8 en el núcleo se trata como Movie (G27 §2).
- NO_VERIFICADO: que el indicador `+0x88` baste por sí solo para la imagen monocroma (en la A7S sí, por B&W = id `0x17` sin saturación). No se ha medido en cámara.

## 8. Reparto del hueco de G18 (`0x43faf28c…0x43fb8ee0`) y cueva propuesta

| Rango | Uso | Fuente |
|---|---|---|
| `0x43faf28c…0x43faf300` | **libre** (0x74 B, a cero en el archivo) | — |
| `0x43faf300…0x43fb7400` | 8 curvas × 0x1020 | `pp_curves_patch` (`SLOT0`, `STRIDE`) |
| `0x43fb7400…0x43fb7500` | color | `pp_color_patch` |
| `0x43fb7500…0x43fb7982` | snapshot, caché, ASM y `pp_tone.bin` (0x3ca B) | `pp_tone_patch` (G33) |
| `0x43fb7982…0x43fb7e00` | libre dentro de la cueva declarada de G33 (que exige todo `0x43fb7500…0x43fb8ee0` a cero) | — |
| `0x43fb7e00…0x43fb7ec0` | Silent | `scripts/g22/patch_silent_r5.py` (R86) |
| `0x43fb7ec0…0x43fb8ee0` | copia `W` de la curva | G33 |
| — | G32-C (`pp_slog3_core_patch.py`) y G32-D | solo en sitio, sin cueva |

Propuesta: `pp_bwhl_patch.CAVE = 0x43faf290` (0x24 B, alineada, sin solape), aplicada **después** de `pp_curves_patch`, que exige todo el hueco a cero. G32-D no necesita cueva. Riesgo común a todo el hueco: G28 observó que se borra en ejecución (NO_VERIFICADO quién lo hace).

## 9. Qué depende de `patch_bw` (VERIFICADO con bytes, 12-11-2026)

- **Núcleo**: un barrido capstone de `0x43600000…0x43d00000` busca `cmn #7`/`cmn #8`/`cmp #0xf8` a menos de 8 instrucciones de una lectura de `+0x24` (saturación del resumen) o de `cfg+0x14e`. Sale **un único** sitio, `0x437a273e`, que es el que reescribe G32-D. Fuera de él, la saturación −8 solo llega al proveedor `0x438280d0` (grupo `0x30`, G34) como un valor de color más: sin `patch_bw`, B&W conserva la saturación que elija el usuario.
- **`libObj`**: `patch_bw` solo toca `SAT_SITE 0x9b35a2` (pasa a ser `b.w` a la cueva) y su cueva `0x9b328c` (20 B que `patch_color` deja como `nop`). En el 3.80 (`pkg-380w/files/lib/libObj.so`) están aplicados los dos: `fff773be` y `237a082b…`. Ningún otro parche lee esa cueva, y `COLOR.index(0x504) = 8`: es el tipo que compara G32-D.
- **Conclusión**: con G32-D, `patch_bw` sobra y además estorba, porque convierte B&W en Movie con saturación −8, que ya no da monocromo. Hay que quitarlo. La cueva vuelve a quedar en `nop`.

## 10. Plan de integración conjunta (G32-C, G32-D y G33-B)

Imagen del núcleo (`build_base_pp.bionz_cfw`, sobre el BIONZ del CFW), en este orden:
1. `pp_curves_patch.main(…, color, tone)`: curvas, color y G33 (`pp_tone_patch`). Exige todo el hueco de G18 a cero, así que va primero.
2. `patch_silent_r5.apply_bytes` (R86, cueva `0x43fb7e00…0x43fb7ec0`), como hasta ahora.
3. `pp_slog3_core_patch` (G32-C): tres cambios en sitio, sin cueva.
4. `pp_bw_mono_patch.patches` (G32-D): en sitio, `0x437a2728…0x437a2743`.
5. `pp_bwhl_patch.patches(img, pp_bwhl_patch.CAVE)` (G33-B): cueva `0x43faf290…0x43faf2b4` y dos literales. Solo Hi-Light (`bw=None`) mientras no haya valores de B/W calibrados.
Cada `patches()` comprueba sus bytes originales: si algún paso anterior tocara su sitio, la construcción falla en vez de mezclar parches.

`libObj` (`build_pp_menu.py:140`): dejar `patch_libobj_pp.patch_color(lo)` **sin** `patch_bw`. Actualizar `tests/test_g26_color_libobj.py::test_bw_envia_movie_y_saturacion_menos_8` (retirarla o invertirla) y el texto de G27 §3.

Pruebas que hay que ejecutar: `tests/test_g25_gamma_curves.py`, `test_g31_base_pp.py`, `test_g33_pp_tone.py`, `test_e26_r86_silent_r5.py`, `test_g32c_slog3_core.py`, `test_g32d_pp_bw_mono.py`, `test_g33b_pp_bwhl.py`, `test_g26_color_libobj.py`, `test_g30_libobj_ppeco.py` y `test_g23_pp_menu.py`; después, `audit_package_nflasha15.py` sobre el `.dat`. En cámara: B&W con Saturación 0 (debe salir monocromo), Movie con Saturación −8 (debe salir en color) y Detail Manual con Hi-Light 0…4.

## 11. G35-A sigue vigente en la serie 3.79/3.80 (VERIFICADO con bytes)

- `libObj.so` es **idéntica** en `pkg-375w`, `pkg-379w` y `pkg-380w` (sha256 `7937a86e34b7…`, 17 439 312 B). Están los 5 límites `≤ 9 → ≤ 10` (`0x4a7860`, `0x4b4184`, `0x4b73de`: `0a2b`; `0x4c0ae0`, `0x4c0b08`: `b8f10a0f`), los ganchos de Reset `0x4c0e62`/`0x4c0ea2` y la tabla de `pp_factory.tabla()` (1 364 B, 1 aparición). Es decir, `ppinit`, PP10 y Reset con valores de fábrica viajan sin cambios en el 3.79/3.80.
- Menú: cumple el tope de G36. El selector es `Off/PP4` + `PP5/PP10` (6 opciones), y Copy y Reset se quitaron del menú (G36 §8). Reset ya no es accesible desde la UI, pero no hace falta: `ppinit` carga los valores de fábrica en el primer arranque.
- Veredicto: **no hay que portar nada** (ya está en el 3.79/3.80) **ni descartarlo**. La fila no se cierra porque lo que queda es medir en cámara: que la marca y los valores persistan tras apagar, que PP10 se guarde y que los valores de `pp_factory.py` (de memoria) sean los deseados. Lo de Reset por slot queda fuera de alcance mientras no vuelva al menú.

## 12. Límites

- Nada medido en cámara. Tampoco está verificado que las funciones APC se ejecuten con PP (G34 §3).
- La identidad `P` = `this` de `0x43afa0ce` se deduce del patrón común de campos y de la coincidencia semántica, no de una cadena de llamadas completa (NO_VERIFICADO del todo).
- Las escalas de Hi-Light y el significado de los nibbles B/W son NO_VERIFICADOS.
