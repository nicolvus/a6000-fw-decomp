# Auditoría técnica del pipeline de LUTs — READ-ONLY

Worktree: `/home/nicolas/Documentos/a6000/a6000-main` · HEAD `aa618415` · 25/26-11-2026 ·
`.venv/bin/python` (CPython 3.14.8, pytest 9.1.1) · `CI` desactivado en todas las ejecuciones
(`env -u CI …`) · sin cámara, sin flasheo, sin escrituras en RAM/firmware.

No se ha modificado ningún fichero del repositorio. Este informe vive fuera del árbol
(`/home/nicolas/Documentos/a6000/lut-audit.md`).

---

## 0. Aviso imprescindible: el árbol estaba siendo modificado durante la auditoría

Al empezar (21:47) el árbol sólo tenía ficheros ignorados (`firmware/`, `.venv/`,
`analysis/rea-independent/input/`). A las **22:01** aparecieron cambios **no versionados de otra
sesión**:

```
 M scripts/lut/lut_patch.py
?? scripts/lut/lut_t.py           (11 228 B: curva 1D tras la gamma de LUT-T-1)
?? scripts/lut/cube_spec.py
?? tests/test_lut_spec.py
?? docs/gui/g114-lut-propios-especificacion.md
```

Consecuencia: durante la sesión hubo **dos pytest en paralelo** y los ficheros cambiaban entre
ejecuciones. Por eso el informe se ancla a **HEAD `aa618415` materializado aparte** con
`git archive HEAD` en `/tmp/audit-head` (+ symlinks de `analysis/` y `firmware/`), y todas las
cifras «de HEAD» se han medido ahí. Los números del árbol vivo se dan aparte y etiquetados.

Efecto medible del trabajo en curso: `lut_patch.apply_bytes` con la curva nueva se sale de
`ZONA_A` (`AssertionError: 0x43be4348` > `0x43be4330`) → **4 tests fallan** en el árbol vivo
(`test_g71_lut.py::test_empaquetado_21_bits_sin_perdida`, `test_g89_lut_sd.py::
test_avcam_usa_la_ranura_del_blob_y_cae_al_dat_o_a_fabrica`,
`test_g89_lut_sd.py::test_avcam_off_blob_invalido_y_sin_memoria_no_cambian_la_ruta`,
`test_g89_lut_sd.py::test_sin_modo_sd_el_parche_es_el_de_siempre`). No es un defecto de HEAD.

---

## 1. Suite de pruebas: números reales

Comando exacto (el pedido):

```
env -u CI .venv/bin/python -m pytest tests/test_g7*.py tests/test_g88*.py tests/test_g89*.py \
    tests/test_g9*.py tests/test_g10*.py tests/test_g11*.py -q
```

Resultado sobre **HEAD limpio** (182 casos recogidos, 346 s):

> **136 passed · 42 skipped · 4 errors · 0 failed**

Resultado sobre el **árbol vivo** (primera pasada, antes de que apareciera `lut_t.py`):
idéntico (136/42/4). Segunda pasada, con el trabajo en curso dentro: **4 failed · 66 passed ·
19 skipped** en el subconjunto LUT (los 4 fallos citados en §0).

### 1.1 Los 4 «errors» no son del pipeline de LUT

Todos en `tests/test_g105_builds_por_funcion.py` (fixture `usr`, que compila 5 variantes de
`build_cfw_film`). Causa exacta, reproducida a mano:

```
scripts/gui/build_cfw_film.py:196   pp = pp_dir                     # el parámetro booleano 'pp' se pisa con un Path
scripts/gui/build_cfw_film.py:141   ... ((pid["sel"], min(pps), max(pps)) if pp else (0, 1, 0))
KeyError: 'sel'
```

`pids_film()` recibe un `Path` (siempre verdadero) y busca `pid["sel"]`, que sólo existe si el menú
PP se configuró. La variante «film sin pp» —que es justamente `POR_DEFECTO = {film, exfine, iso}`—
no se puede construir. Es un subsistema ajeno a LUTs (Film/PP, G110): se reporta, no se toca.

### 1.2 Qué se salta y por qué (42 skips)

| Grupo | Nº | Motivo |
|---|---|---|
| `test_g91_lutjpg.py` (todo el módulo) | 12 | falta `zig` + `libjpeg-turbo` ARM + `qemu-arm` |
| `test_g74_cuevas_seguras.py` | 11 | falta el volcado de RAM viva (1 GiB, no versionado) y `libObj.so` |
| `test_g89_lut_sd.py` (3) | 3 | falta `viewUnified2.so` en `analysis/camera-extract/usr/lib/` |
| `test_g93_lut_geometria.py` | 2 | faltan `av-cam-a7s.bin` y `av-cam-a6300.bin` |
| `test_g94_lut_modos.py` | 1 | falta el volcado de RAM viva |
| `test_g76_sq_libobj.py` | 2 | falta `libObj.so` |
| `test_g97/g101/g102` (CFW 3.90/3.91/3.92) | 6 | CFW no construido |
| `test_g103` (3) / `test_g104` (1) / `test_g111` (1) | 5 | faltan `av-cam` 3.38, `base-380.tar`, `image_cmn_169.uxc` |

**Lo importante:** entre los 42 skips están **casi todas las pruebas que sostienen las
afirmaciones centrales** de la cadena LUT (§3): ConvSD inactivo (g94), mismo IP en A7S/A6300
(g93), cuevas a cero en memoria viva y «sin referencias» (g74), y **toda** la regresión de ΔE2000
(g91, que vive en un módulo con `pytestmark` global).

### 1.3 Detalle por fichero (HEAD)

| Fichero | Resultado (HEAD) | Nota |
|---|---|---|
| `tests/test_g71_lut.py` | **12 passed** (69,7 s) | Unicorn + 3 tablas en ΔE |
| `tests/test_g88_sd_lut.py` | **11 passed** (122,5 s) | el más lento del grupo LUT |
| `tests/test_g89_lut_sd.py` | **16 passed · 3 skipped** (76,6 s) | skips: `viewUnified2.so` ausente |
| `tests/test_g90_lut_opt.py` | **5 passed** (7,2 s) | |
| `tests/test_g91_lutjpg.py` | **12 skipped** | falta zig/libjpeg ARM/qemu-arm |
| `tests/test_g92_tono_post.py` | **4 passed** (0,4 s) | |
| `tests/test_g93_lut_geometria.py` | **1 passed · 2 skipped** | skips: `av-cam-a7s`/`a6300` ausentes |
| `tests/test_g94_lut_modos.py` | **3 passed · 1 skipped** | skip: volcado de RAM viva |
| `tests/test_g95_lut_pkg.py` | **3 passed** (24,7 s) | |
| `tests/test_g96_peliculas.py` | **2 passed** (0,2 s) | |
| `tests/test_g97_films.py` | **13 passed · 1 skipped** | skip: CFW 3.90 no construido |
| **Subtotal LUT (11 ficheros)** | **70 passed · 19 skipped · 0 failed** | 89 casos |
| `test_g70_hd120` (6) · `g74` (16, **11 skips**) · `g76_sq_libobj` (2, **2 skips**) · `g76_sq_vfr` (5) · `g77` (2) · `g78` (3) · `g79` (1) | **22 passed · 13 skipped** | `g74` no puede comprobar «cero en vivo» |
| `g101` (6, 1 skip) · `g102` (11, **4 skips**) · `g103` (6, **3 skips**) · `g104_iso_avcam` (4, 1 skip) · `g104_iso_filas` (9) · `g104_iso_ui` (3) · `g106` (3) · `g107` (3) · `g108` (2) · `g111` (6, 1 skip) | **43 passed · 10 skipped** | skips: CFW 3.90–3.92, `av-cam` 3.38, `base-380.tar`, `image_cmn_169.uxc` |
| `test_g105_builds_por_funcion.py` (5) | **1 passed · 4 errors** | `KeyError: 'sel'` (§1.1) |
| **TOTAL** | **136 passed · 42 skipped · 4 errors · 0 failed** | 182 casos, 346 s |

---

## 2. Las piezas: qué hacen de verdad, formatos y límites numéricos

### 2.1 `scripts/lut/cube_a6000.py` — modelo de la cadena en el PC (G71/G90)

**Qué hace.** Referencia numérica de todo el pipeline. Modela
`RGB pantalla → lineal (EOTF sRGB) → M (3×3, 9 s16 Q10) → T (2048 u16, entrada lineal i·0,00271,
valores 0…1023) → YCbCr BT.601 rango completo → LUT 3D 5×9×9 de deltas s7 → salida`.
`descompone()` ajusta la tabla por mínimos cuadrados (`metodo="mc"`, G71) o en ΔE2000
(`metodo="de"`, G90, por defecto) y `empaqueta_hw()` produce los 0x654 B en el orden del hardware.

**Formatos aceptados (`.cube`).** Adobe 3D: `LUT_3D_SIZE n` con `n ≥ 2` y **sin tope superior**
(`cube_a6000.py:47` sólo exige `n ≥ 2` y `len(filas) == n³`). Acepta `DOMAIN_MIN/MAX` en coma
flotante, `TITLE`, `LUT_3D_INPUT_RANGE`. **Rechaza** cualquier fichero con `LUT_1D_SIZE`
(`cube_a6000.py:42-43`). Comentarios `#`, líneas en blanco, filas con más de 3 columnas: ignoradas
a partir de la 3.ª.

**Límites numéricos.**
- Deltas s7 con signo en `[-64, +63]` (`cube_a6000.py:183-188`); los que se salen se recortan y se
  cuentan (`ch.rec`).
- Paso de 1 unidad: ΔY = 1/256 → ±63/256 = **±24,6 %** del fondo de escala. ΔCb/ΔCr = 0,75/256 →
  ±0,1846 en la escala normalizada de croma (±0,5), es decir **±18,5 % del rango completo** o
  **±36,9 % del semirrango**. Ojo: los documentos mezclan las dos bases (G71 §1(b) usa «% del
  semirrango», G93/G96 usan «±18 %» del rango completo); son el mismo número —
  `cube_a6000.py:22`.
- `T` son 2048 entradas con valores **0…1023** (10 bits) — `cube_a6000.py:25,136`.
- M se cuantiza a Q10 y se recorta a int16.
- ΔE2000 con `a_lab` sobre sRGB/D65, sin recorte previo en las derivadas (sí en la salida de la
  cadena: `np.clip(...,0,1)`).

**ΔE2000: comprobado a fondo en esta auditoría** contra los **34 pares de Sharma, Wu y Dalal
(2005)**: error máximo **4,95·10⁻⁵**, 0 fallos, y `ΔE(x,x) = 0` exacto.

### 2.2 `scripts/lut/lut_opt.py` — ajuste directo en ΔE2000 (G90 §B)

**Qué hace.** `ajusta_de(c, y, w, modelo)`: (1) arranque por mínimos cuadrados
(`cube_a6000.ajusta_lut3d`); (2) Gauss-Newton sobre
`ε = (ΔL/SL, ΔC'/SC, ΔH'/SH)` con Jacobiana numérica de Lab, respetando el recorte de canal RGB, y
caja `[-64, +63]` — resuelto con `np.linalg.solve` y, si la caja muerde, con L-BFGS-B sobre el
cuadrático; (3) descenso por coordenadas **enteras** (±1, ±2) sobre el ΔE2000 exacto ponderado, sólo
con las muestras que tocan cada nodo.

**Límites.**
- `LO, HI = -64.0, 63.0` (`lut_opt.py:23`); regularización laplaciana `lam=1e-7` (× 3 canales).
- Muestras **sintéticas**: uniformes 45 %, eje neutro 20 %, nube de piel HSV 20 %, foto real 15 %
  (`lut_opt.muestras`). Si no hay foto se reescalan a 1/0,85 → **el 15 % «foto» se convierte en
  ruido sintético cuando no se pasa imagen**.
- `MODELO_DEFECTO = "ambos"` (`lut_opt.py:21`): promedia trilineal y tetraédrica. Medido en los
  informes: cuesta ≈ 0,2 ΔE bajo trilineal y recupera 1,48 → 1,12 bajo tetraédrica.
- Coste ≈ 15 s por tabla (memoizado por proceso en `sd_lut`, `lut_patch` y `lut_pkg`).
- `iters=6`, `pasadas=3`, `entero=True` por defecto.

### 2.3 `scripts/lut/sd_lut.py` — lote de `.cube` a las 3 tablas del `.dat` (G88, ruta PC)

**Qué hace.** `lee_cubes(carpeta)` (alfabético, `*.cube`) → `convierte()` devuelve 3 tablas de
0x654 B, 3 nombres y (ΔE medio, p95) frente al `.cube` exacto; los huecos se rellenan con la tabla
identidad etiquetada «Neutro». `ajustes_con_nombres()` reescribe las opciones del ajuste «LUT».

**Límites.** `MAX_LUTS = 3` (`sd_lut.py:15`, por la cueva de 3×1064 B en `ZONA_B`), `MAX_NOMBRE = 11`
(truncado, `sd_lut.py:16`), memo por md5 de la tabla + dominio. **No hay tope de tamaño del `.cube`**
(hereda el de `cube_a6000`). Docstring obsoleto: dice «la cámara NO lee la SD: g88 §1», superado por
G89.

### 2.4 `scripts/lut/userland/lutsd.c` + `lut_sd_userland.py` — hilo en la cámara (G89/G95)

**Qué hace.** Hilo nuevo dentro de `viewUnified2.so` (proceso de `libObj`), arrancado desde
`DT_INIT`; resuelve `Fsys_*`, `Backup_*`, `malloc/free/sleep` por `dlsym`. Por cada ranura 1…6:

1. `lee_paquete()`: abre **`X:/LUT/LUT<n>.LUT`** (sólo barra `/`), lee hasta 1081 B, valida firma,
   versión, longitud y CRC32, y copia 1064 B.
2. Si falla, `lee_ranura()`: 4 variantes de ruta —`/` o `\`, `.cube` o `.CUB`— en
   `X:/LUT/LUT<n>.*`.
3. Remuestrea a 405 nodos: muestreo directo del nodo en Q16 + corrección de 2.ª diferencia
   (`v = z − Σ_ejes Δ²z/12`, en 1/16 de unidad, saturación a s7).
4. Empaqueta 21 bits/nodo y escribe el bloque de 16 KB en el Backup `0x150005`.

**Formatos.** `.cube` 3D: `LUT_3D_SIZE` con **`n` entre 2 y 64** (`lutsd.c:111`); números decimales
con signo, fracción y exponente (`q16()`); `DOMAIN_MIN/MAX`; **rechaza** `LUT_1D*`; exige
`filled == n³`. El parser es de línea con búfer de 96 B (`struct ctx.line`), así que una línea de
más de 95 caracteres se corta.

**Límites numéricos.**
- Dominio en Q16 (`lo`, `hi` por canal, por defecto 0…65536 = 0…1).
- `u` saturado a 65536 → la entrada fuera de dominio se recorta, no extrapola.
- Deltas finales: `satura()` a `[-64, 63]` (`lutsd.c:172`).
- Corrección: `21·l >> 8` = 21/256 ≈ 1/12, sólo con ambos vecinos.
- Sin coma flotante, sin `udiv` (división propia de 64 bits), sin libc, sin globales.
- Blob: `LUTS` en +0, versión 1 en +4, ranuras 6 en +6, máscara de válidas +8…+13, letra de unidad
  en +14, tablas desde +16 con paso 1064, diagnóstico en +0x2000 (6×4 enteros + 6 enteros) y
  +0x2060.
- Sondeo cada 5 s sobre `/dev/mmca` y `/dev/msm`; barrido **una vez** al insertar la tarjeta;
  escritura al Backup sólo si el blob cambia.
- Código ARM 3,6 KB (4,2 KB con el paquete).

### 2.5 `scripts/lut/lut_pkg.py` — paquete `.LUT` precalculado (G95)

**Qué hace.** `desde_cube()` = `descompone(usa_M=False, usa_T=False, usa_L=True)` →
`empaqueta_hw` → `empaqueta_21` → `paquete()`. **Formato v1, 1080 B little-endian**:

| Offset | Campo |
|---|---|
| 0 | `0x544C3641` = `"A6LT"` |
| 4 | versión `1` (u8) |
| 5 | `0` (u8, reservado) |
| 6 | `1064` (u16) |
| 8 | CRC32 IEEE del payload (u32) |
| 12 | `0` (u32, reservado) |
| 16 | 405 nodos × 21 bits en orden lógico |

**Verificado en esta auditoría**: 405·21 = 8505 bits → caben en **1064 B** (8512 bits, 7 sin usar) y
el ida/vuelta `empaqueta_21 ↔ desempaqueta` es **exacto** para valores aleatorios en ±64.

**Límites.** Sólo tabla (sin curva T; «versión 2» pendiente de LUT-T-1). El lector C comprueba
`n == 1080`, `p[4] == 1`, `(p[6]|p[7]<<8) == 1064` y el CRC; **no** valida los 5 B reservados
(offset 5 y 12…15).

### 2.6 `scripts/lut/lut_patch.py` + `scripts/gui/avcam_dinamico.py` — cueva en `av-cam` (G71/G73/G89)

**Qué hace.** Tres ganchos de 4 B: `0x4381D2FE` (`ldr.w r3,[r5,#0xc4]`, ruta **SA** → `0x43b67a68`),
`0x4381D372` (ruta **MOV/MON/CAP** → `memcpy`) y `0x437A2502` (entrada de la máquina
`0x437a24fc`, cambio en caliente). La cueva lee el byte del ajuste por `Backup_read`; con Off o
valor fuera de rango devuelve el puntero original (fábrica). Con LUT *n* entrega una tabla
desempaquetada de 21 bits a un búfer de `malloc(0x654)` (una sola reserva, celda de 4/8 B); si
`malloc` falla, puntero original.

**Dónde escribe** (esto es lo grave, ver §4.1): código en `ZONA_A` desde `0x43BE3F28`
(= `ZONA_A[0]+0x400`, `avcam_dinamico.py:36`), 3 tablas de 1064 B en `ZONA_B = 0x43C1FF24`
(3192 B de los 3432 disponibles), y el blob de 16 KB en Backup `0x150005` cuando `sd=True`.

**Límites.** `TAM = 0x654` = 1620 B = 405 palabras; `SIZE = 11 427 236` B (tamaño exacto de
`av-cam.bin`); `comprobar_zonas()` rechaza solapes y zonas prohibidas; con `sd=True` reserva
`0x654` **y** 16 384 B.

### 2.7 `scripts/lut/tono_post.py` — curva 1D tras la gamma (G92)

**Qué hace.** Ejecuta `FUN_438538e4` en Unicorn con un objeto mínimo y comprueba la cadena de tono:
`gamma[bd9·2+bd6] → c5c[bdb] (bd1) | c5c[bdb]∘c60[bdd] (bd3) | c68[be1] (bd5)`.
`c68` = 14 punteros en `0x440013cc`; las ranuras 0, 6 y 8…13 apuntan a la identidad
`0x43bfaf2a`. `curva_post(cadena)` convierte la `T` de una `Cadena` en una tabla de
**1024 u16** sobre el código de gamma.

**Límites.** 14 ranuras, `be1 ≤ 13`; **1024 entradas** (la tabla real es de 512 puntos × 11 bits en
`obj+0x26e`, pero la fuente `c68` es de 1024 u16); prioridad `bd1`/`bd3` sobre `bd5`; una sola
curva para R, G y B. Ganancia medida (G92 §4, métrica corregida): película 0,79 → 0,19 ΔE medio.

### 2.8 `scripts/lut/lutjpg.py` + `userland/lutjpg.c` — `.cube` completo por software (G91)

**Qué hace.** Binario ARM estático (musl + libjpeg-turbo, `cortex_a5-neon-d32` sin NEON) que aplica
el `.cube` **completo** al JPEG: interpolación tetraédrica entera en Q16, 6 tetraedros. Conserva
EXIF y submuestreo, omite APP2/MPF y JFIF.

**Formatos y límites.** `2 ≤ n ≤ 129` (`lutjpg.c:40`); valores **recortados a 0…1** (`lutjpg.c:73`);
`DOMAIN_MIN/MAX` en coma flotante; rechaza `LUT_1D_SIZE`; exige `n³` filas; `-q 1…100`; no permite
salida == entrada (código 2), `.cube` inválido (3), entrada ilegible (4), JPEG corrupto (5), fallo de
escritura (6). Memoria: 129³ × 3 × 2 B ≈ **12,9 MB** de tabla + 24 Mpx de RGB. Sólo foto; nunca
afecta a la vista en vivo.

### 2.9 `film_a6000.py` / `film_patch.py` / `film_userland.py` / `userland/films.c`

**Qué hacen.** `film_a6000` hornea una entrada Apple Log y ajusta 5×9×9; `film_userland`/`films.c`
es un hilo en `viewUnified2.so` con 38 looks (menú «Film Simulation», lista única y 12 ranuras Fn)
que deja el look activo en un blob «FILM» del Backup `0x150005` (+ ACK de 1 B); `film_patch` pone en
`av-cam`, **en `ZONA_G18`** (no en `ZONA_A`, por G108), la LUT + la curva 1D tras la gamma
(`bd5=1`, `be1=8`, `c68[8]`) + la máquina de cambio en caliente con reintento cada 32 pasadas.

**Límites.** Tabla 21 bits/1064 B + curva de 1024 u16 en `+0x1000` del blob; 6 IDs de fila + 1 de
lista única + ACK; `REC` de la curva; comparte los **4 ganchos** de `FUN_43852f7c` con la curva de
LUT-T-1.

---

## 3. Verificación de las 7 afirmaciones

### 3.1 «Geometría 5×9×9 fija e imposible de ampliar»

**Fija: VERIFICADO en bytes.** Desensamblado de `0x43b67918` (capstone, `av-cam.bin`): `tbb` de 8
casos con `add.w r0, r0, #0x17000/#0x17200/#0x17300/#0x17400/#0x17500/#0x17600/#0x17700/#0x17800` y
`movs r2` = 0x12c, 0xf0, 0xf0, 0xc0, 0xc8, 0xa0, 0xa0, 0x80 (8 valores, 6 distintos); suma
300+240+240+192+200+160+160+128 = **1620 = 0x654** = 405 palabras. `movw #0x654` aparece **17 veces**
en la imagen. La permutación de
`0x43BEF2AC` es una permutación válida de 0…404 (comprobado).

**«5×9×9 es el máximo del mapa de bancos»: REFUTADO tal como está escrito.** Con el propio modelo de
bancos del proyecto (`test_g93_lut_geometria.bancos()`, ventana `[128,64,64,64,64,64,64,512]`),
**8×8×8 = 512 nodos caben exactamente** (64 en cada uno de los 8 bancos; el banco 0 admite 128) y
también 2×16×16 o 32×4×4. `cabe(8, 8)` es `True` y **el test nunca lo comprueba**: sólo prueba
`cabe(6,9)`, `cabe(5,10)`, `cabe(9,9)` y `cabe(17,17)`. Lo que sí es cierto es que **ninguna
(ny, 9, 9) con ny > 5 ni (5, nc, nc) con nc > 9** cabe, y que el producto 405 sólo se alcanza con
(5, 9, 9) dentro de la familia «razonable».

**«Imposible de ampliar»: INFERENCIA fuerte.** El argumento válido no es el mapa de bancos sino que
el generador (`Create3DLUT`) recorre bucles fijos 9×9×5, copia 0x654 B fijos y los 18 registros de
control son de 1 o 6 bits (ninguno codifica tamaño). Eso sí es estático; que el HW no tenga otro
modo sólo lo cerraría una medida en cámara.

### 3.2 «LUT 21 bits / 405 nodos»

**VERIFICADO.** 405 × 21 = **8505 bits** → **1064 B** (8512 bits, 7 de margen). Roundtrip exacto con
`avcam_dinamico.empaqueta_21` + desempaquetado por la permutación del núcleo (comprobado con valores
aleatorios en ±64). 3 × 1064 = 3192 ≤ 3432 B de `ZONA_B`. `empaqueta_21` usa un entero de precisión
arbitraria de Python (no hay desbordamiento); en el lado ARM el desempaquetado lee 4 B por nodo con
`lsrs`/`ubfx` (`avcam_dinamico.lut_unpack_asm`), correcto hasta i = 404 (`21·404+21 = 8505`).

### 3.3 «T de 1024 u16 tras gamma»

**VERIFICADO sólo para la curva posterior a la gamma (LUT-T-1).** `c68[8]` = tabla de **1024 u16**
aplicada tras el código de gamma, con `bd5 = 1`, `be1 = 8`, `bd1 = bd3 = 0`; ejecutado en Unicorn
sobre `FUN_438538e4` real (`tests/test_g92_tono_post.py`: `len(t) == 1024`, monótona, identidad de
fábrica en las ranuras 0/6/8…13).

**Matiz importante:** hay **dos** T distintas y los documentos las mezclan.
- La T de `cube_a6000` es de **2048 entradas** con valores 0…1023 (`N_CURVA = 2048`,
  `ESCALA_CURVA = 0,00271`) y va **antes** de la LUT 3D, no tras la gamma del usuario.
- La T de `c68[8]` es de **1024 entradas** u16 y va **después** de la gamma.
La propuesta de G94 §4 («curva T (1024 u16 sobre el código de gamma) 2048 B») es la segunda; la
tabla publicada en G71/G90 es la primera. Pasar una a la otra no es un `resize`: `tono_post.curva_post`
hace la conversión real (linealiza sRGB y aplica T).

### 3.4 «Empaquetado/CRC del `.LUT`»

**VERIFICADO.** Cabecera `struct "<IBBHII"` = 16 B: `A6LT` (0x544C3641 little-endian), versión 1,
reservado, 1064, CRC32 IEEE (zlib), reservado; payload de 1064 B. En C: `crc32()` con polinomio
reflejado `0xEDB88320`, init/final `~0` — equivalente a `zlib.crc32`. `lutsd_paquete` rechaza
longitud ≠ 1080, firma, versión, longitud declarada y CRC. `tests/test_g95_lut_pkg.py` compara el
ARM compilado con la referencia Python y prueba 6 mutaciones (byte de menos, byte de más, firma,
versión, longitud, payload). **Verificado además por mí**: paquete generado desde un `.cube` = tabla
ajustada en ΔE, byte a byte.

**Reservas no validadas:** los 5 B a 0 (offset 5 y 12…15) no se comprueban ni en `valida()` ni en
`lutsd_paquete()`. No es explotable hoy (la versión se valida), pero es un hueco de
compatibilidad futura.

### 3.5 «ConvSD inactivo»

**Código: VERIFICADO.** `lut_modos.convsd_activable(ids, caps)` devuelve `True` sólo si algún id
tiene el bit 4 activo **y** los bits 5–6 a cero (y no es 0xFF), o si el bit 1 del byte de
capacidades está a 1. Los 16 B de ids leídos en la RAM viva son `00 00 01 01 00 00 01 01 00 00 ff ff
00 00 ff ff` (ninguno con bit 4) y el byte de capacidades vale `0x40` (bit 1 a 0; el bit 4 de `0x40`
también es 0).

**EVIDENCIA NO RE-EJECUTABLE AQUÍ: INFERENCIA.** El volcado de 1 GiB
(`analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin`) **no está en este worktree**, así
que `test_convsd_inactivo_en_la_ram_viva` se **salta**. Además el test comprueba los GOT vivos de
`FUN_437a1d14`/`FUN_437a4358` y las dos tablas, **no** `cfg+0xd9` en sí, y el propio informe admite
que es **un solo estado de arranque**. La consecuencia práctica («misma tabla para todos los modos
es exacta») depende de una lectura única que aquí no se puede repetir.

### 3.6 «ΔE2000 corregido (LUT-DE-1)»

**VERIFICADO en el código.** `cube_a6000.py:113` → `dL, dC = L2 - L1, C2p - C1p` (usa **C′**, no C).
Los **34** pares de Sharma pasan con error máximo **4,95·10⁻⁵** y `ΔE(x,x) = 0`. Es la única
implementación de ΔE2000 de `scripts/` (grep: no queda copia con el fallo).

**Pero la regresión no se ejecuta en este entorno:** `tests/test_g91_lutjpg.py` tiene
`pytestmark = pytest.mark.skipif(not J.disponible())` a nivel de módulo y la prueba de Sharma vive
dentro → sin `zig` + libjpeg ARM + `qemu-arm`, **0 pruebas de ΔE2000 corren**. Y la prueba sólo usa
4 pares de los 34. `PENDIENTES` mantiene LUT-DE-1 «ABIERTO» porque faltan las cifras, no por el
código.

### 3.7 «Rutas de la SD y nombres LUT1…LUT6»

**VERIFICADO en el código (no en la cámara).** `lutsd.c:217-231`: `char path[24] =
"X:/LUT/LUT1.cube"`, con `path[0]` = letra de la unidad (`Fsys_GetDriveLetter("/dev/mmca")`, luego
`/dev/msm`), `path[2] = path[6]` = `/` o `\`, `path[10] = '1' + slot`, y variante `.CUB`
(`path[12..15]`). El paquete `.LUT` usa **una sola** variante, sólo con `/` (`lutsd.c:280-285`),
como admite G95 §3.
Menú: `AJ_SD` = Off + «LUT 1»…«LUT 6» (`lut_patch.py`, 7 opciones = el tope medido de la fila en
G36); el nombre del fichero **es** la ranura. En `av-cam`, `lut_unpack_sd_asm` lee la tabla en
`blob + 16 + (k-1)·1064` y sólo para `1 ≤ k ≤ 6`; para `k ≤ 3` sin fichero cae a la tabla del
`.dat` y para 4…6 al puntero de fábrica.

---

## 4. Incoherencias docs↔código, errores latentes y tests que no prueban lo que dicen

### 4.1 GRAVE — `ZONA_A` y `ZONA_B` no son huecos: la cueva LUT se escribe dentro de tablas que el núcleo lee

`docs/gui/g107-causas-pp-ids-zonas.md:53-70` (**posterior** a G71/G73 y a la fila `LUT-C`) demuestra
que:

- **`ZONA_A` = `0x43be3b28…0x43be4330` es la tabla T1 de estabilización** (1025 u16), la lee
  `0x43705a34` y **su lectura se usa en un modo EIS**.
- **`ZONA_B` = `0x43c1ff24…0x43c20c8c` son dos tablas `s16` 6×13×11 del YC de captura `BOKS`**,
  descritas en `0x438f6fa4` (dimensiones 1, 6, 13, 11) e interpoladas en `0x43881290`.

**Lo he confirmado yo en `av-cam.bin`:**

```
0x43705a34  cmp.w r0,#0x400
0x43705a3a  ldr   r3,[pc,#0x14]      ; literal 0x4de0e8
0x43705a3c  add   r3, pc             ; pc = 0x43705a40 → r3 = 0x43BE3B28  == ZONA_A[0]
0x43705a3e  ldrh.w r3,[r3, r0, lsl #1]   ; T1[r0], r0 ≤ 0x400
0x438f6fa4  ... strb 1, 6, 13, 11 ...    ; descriptor de las tablas BOKS
            punteros 0x43C1FEF0 / 0x43C1FF08 / 0x43C205D4 (≈ 0x43c1ff22 / 0x43c205d6 de G107)
```

Y la aritmética del parche LUT:

| Elemento | Dirección | Qué pisa |
|---|---|---|
| Código de la cueva LUT | `0x43BE3F28` (= `ZONA_A[0]+0x400`) | **T1[512…1024]** de la tabla EIS (513 entradas) + 3 de T2 |
| 3 tablas de 1064 B | `0x43C1FF24` | primera mitad de la **tabla BOKS** del YC de captura |

Sin embargo **cuatro fuentes siguen afirmando lo contrario**:

1. `scripts/lut/lut_patch.py:3` → «la cueva va en el fragmento libre verificado `0x43BE3B28`».
2. `scripts/gui/avcam_dinamico.py:23-24` → «2056 B, ceros idénticos fichero/vivo (G72)».
3. `docs/PENDIENTES.md` fila **`LUT-C`** → «**CERRADO** (offline, 15-11-2026)».
4. `docs/gui/g71-lut3d-formato-y-cube.md §3` → «zona verificada (G73)».

Y la fila **`ZONA-1`** (`docs/PENDIENTES.md:886`) dice explícitamente que el arreglo **de LUT** sigue
pendiente: «Queda: LUT (G73), HLG, S&Q…». El **CFW 3.86 instalado** lleva exactamente esto (G95 §4:
«frente a la 3.83, `av-cam` sólo difiere en `ZONA_B`»). Conclusión del propio G107: «Con el CFW, la
estabilización en ese modo y el YC de captura reciben valores basura». Que no se haya notado no
prueba que sea inocuo: el modo EIS concreto y la captura BOKS no se han ejercitado.

**La contradicción es literal dentro de `scripts/lut/`**: `film_patch.py:5` dice «Aquí, todo en
`ZONA_G18` (G108: la zona A de G72 es la tabla T1 que el núcleo lee al arrancar)», y usa
`D.ZONA_G18[0]` (`film_patch.py:34`); `lut_patch.py:3` sigue diciendo que `0x43BE3B28` es «el
fragmento libre verificado». Film se mudó; LUT no.

### 4.2 Tests que no prueban lo que dicen

| Test | Qué dice | Qué prueba de verdad |
|---|---|---|
| `test_g71_lut.py:19 test_ganchos_originales_y_zona_a_cero` | «zona A cero» | Sólo que los bytes son 0 **en el fichero** `av-cam.bin`. G107 demuestra que estar a cero ≠ estar libre. |
| `test_g71_lut.py:73 test_parche_solo_toca_ganchos_y_zonas_verificadas` | «zonas verificadas» | Sólo acota el diff a esas direcciones. Las llama «verificadas» cuando ya no lo están. |
| `test_g74_cuevas_seguras.py:42 _refs()` | «sin referencias» | Sólo busca literales de 32 bits y pares `movw/movt`. **No ve `ldr rX,[pc]; add rX,pc`**, que es justo el mecanismo con el que el núcleo llega a T1 y a BOKS (ver §4.1). Además está **skipped** aquí (falta el volcado vivo). |
| `test_g93_lut_geometria.py:37 test_capacidad_de_las_sram` | «5×9×9 es el máximo del mapa» | Sólo 4 geometrías concretas; `cabe(8,8)` = `True` y no se prueba. `17³ > sum(VENTANA)` es trivial. |
| `test_g91_lutjpg.py:109 test_de2000_pares_de_sharma` | «regresión de ΔE2000» | Correcta en contenidos, pero **el módulo entero está skipped** sin zig+qemu → en la práctica no protege nada. Sólo 4 de los 34 pares. |
| `test_g90_lut_opt.py:70 test_lutsd_correccion_baja_el_error_en_pelicula` | «la corrección baja el error en película» | `assert mean < 1.2` con la cifra publicada 1,09 → 10 % de holgura… y en realidad la holgura es 52 % respecto al valor previo. |
| `test_g89_lut_sd.py:111 test_error_de_ΔE_frente_al_cube_exacto` | «error de ΔE frente al .cube exacto» | `mean < 1.5 and p95 < 5` frente a 1,05/2,42 publicados: no fija nada. |
| `test_g88_sd_lut.py:55` | «ΔE de la conversión» | `< 1.5 / 1.5 / 1.0` frente a cifras de 0,2–0,9. |
| `test_g95_lut_pkg.py:70` | «el hilo usa el paquete antes que el .cube» | Sí, pero **sólo** si el Fsys simulado expone `acepta`; si no, se salta (hay un `skip` condicional dentro). |
| `test_g93_lut_geometria.py:29` | «mismo IP en A7S/A6300» | **Skipped** aquí (faltan los binarios). |

### 4.3 Errores latentes (código)

1. **`film_a6000.py:88` aplica `a_lab` dos veces**: `C.de2000(C.a_lab(a), C.a_lab(b))`, y
   `de2000` ya llama a `a_lab` dentro. **Todas** las cifras ΔE del `informe.json` de ese script son
   falsas. No lo importa nadie ni lo cita ningún documento (herramienta huérfana), pero es el único
   camino con la familia Fujifilm/ACROS/ASTIA.
2. **`build_cfw_film.py:196`**: `pp = pp_dir` pisa el booleano; `pids_film()` recibe un `Path`
   (siempre verdadero) y hace `pid["sel"]` → `KeyError: 'sel'`. Rompe la variante «film sin pp», que
   es la de **por defecto**. (Subsistema Film: se reporta, no se toca.)
3. **`BK_ID 0x150005` compartido por dos hilos userland independientes**:
   `lutsd.c:16` («LUTS»: ranuras en `+16+s·1064`, diagnóstico en `+0x2000`) y
   `film_userland.py:24` («FILM»: tabla en `+0`, curva en `+0x1000`). Ambos escriben el **mismo**
   registro de 16 KB con magia y diseño distintos. Ningún test lo comprueba y ningún documento lo
   menciona; hoy no se cruzan sólo porque `build_cfw_objetivos --sd-lut` y `build_cfw_film` producen
   firmwares diferentes. Un build combinado rompería los dos en silencio. Añadido: comparten
   **idénticos 4 ganchos** de `FUN_43852f7c` para la curva (`film_patch` y el `lut_t` en curso);
   el `lut_patch.py` modificado sí lo detecta ahora, pero ese control es **no versionado**.
4. **Tope de `.cube` incoherente entre piezas**: `cube_a6000` no tiene tope, `lutsd.c` corta en
   **64** y `lutjpg.c` acepta hasta **129**. G71 §2 y G114 anuncian 17³/33³/65³; un **65³ se acepta
   en el PC y en `lutjpg` pero el hilo de la cámara lo rechaza** y la ranura cae a `.dat`/fábrica sin
   avisar más que por el diagnóstico del blob.
5. **`lutsd.c` recorta la línea a 95 caracteres** (`struct ctx.line[96]`). Un `.cube` con las tres
   coordenadas en una línea muy larga (p. ej. exponentes largos) se parsea a medias → `filled`
   incompleto → ranura inválida. Ningún test lo cubre.
6. **Diagnóstico ambiguo del blob**: `diag[]` se pone a 0 al principio y `0` es también el valor de
   éxito de `Fsys_Open`; una ranura que entra por `.LUT` deja sus 4 variantes a 0, indistinguible de
   «abrió a la primera».
7. **`lut_pkg`/`lutsd_paquete` no validan los 5 B reservados** de la cabecera.
8. **`tono_post.gamma(img, idx, foto=0)`** indexa `idx*2 + foto`; por defecto lee la curva de **foto**
   (modo 0). G94 §3 bis avisa de que las curvas de foto y vídeo difieren entre 134 y 437 niveles de
   1023: cualquier análisis que use el valor por defecto está mirando sólo una de las dos.

### 4.4 Incoherencias menores docs↔código

| Documento | Dice | Realidad |
|---|---|---|
| `g71 §1(a)` | ConvSD convierte «601→709» | G94 lo corrige a **709→601**; el texto de §1(a) sigue con el error y la corrección va sólo en una nota al final. |
| `g71 §2` | «`.cube` 17³/33³/65³» | `lutsd.c:111` rechaza `n > 64`. |
| `sd_lut.py:2` | «la cámara NO lee la SD (g88 §1)» | Superado por G89: sí la lee. |
| `g89` cabecera | «tests `test_g89_lut_sd.py` (17)» | 17 funciones, **19 casos** (una parametrizada ×3); G95 dice 19. |
| `LUT-PKG-1` (PENDIENTES) | «CFW 3.84 construido el 23-11, sin instalar» | `g95 §4` termina: «**Instalado** el 23-11-2026 como 3.86». Contradicción dentro del mismo informe. |
| `g93 §2` | escritor «0x6a B con sus constantes» | Correcto (verificado: 0x6a B desde `0x43b67918`). |
| `avcam_dinamico.py:36` | `LUT_CODE = ZONA_A[0] + 0x400` | Correcto, y por eso cae en **T1[512]** (§4.1): el comentario no lo advierte. |

### 4.5 Filas `LUT-*` de `docs/PENDIENTES.md`: ¿siguen abiertas de verdad?

| Fila | Estado declarado | Veredicto de la auditoría |
|---|---|---|
| `LUT-A` | ABIERTO | **Abierta de verdad.** M no tiene hueco y empeora (M≈I); T no tiene ranura en Backup/`.dat`. En curso con `lut_t.py`. |
| `LUT-B` | ABIERTO | **Abierta.** `lutjpg` resuelve «exacto por software» pero **después del JPEG**; lo pedido era sobre el YC antes del JPEG. |
| `LUT-C` | **CERRADO** | **Debe reabrirse.** §4.1: la zona no está libre (G107 + verificación propia). La propia fila `ZONA-1` lo contradice. |
| `LUT-INT-1` | ABIERTO (cámara) | **Abierta** y bloqueante: `MODELO_DEFECTO = "ambos"` es un parche provisional. |
| `LUT-INT-2` | ABIERTO | **Abierta**; depende de INT-1. Cuesta ≈ 0,2 ΔE bajo trilineal. |
| `LUT-OPT-1` | ABIERTO | **Abierta**: pesos sintéticos (sin foto → 15 % convertido en ruido), y la corrección de `lutsd.c` empeora neutros (1,15→1,24; 1,58→2,53). |
| `LUT-C2` | CERRADO | **Cerrada en lo esencial** (geometría fija: verificado en bytes) pero **hay que corregir la coletilla** «5×9×9 es el máximo del mapa de bancos» (§3.1). |
| `LUT-SD-1` | HECHO offline | **Correcto.** El ARM compilado = referencia Python (17³/32³/33³/64³) y el blob se lee con `av-cam` real. |
| `LUT-SD-2` | ABIERTO (cámara) | **Abierta** y es **el** bloqueante real de todo el pipeline. |
| `LUT-SW-1` | HECHO offline | **Correcto** (pero sus tests están skipped sin zig/qemu). |
| `LUT-SW-2` | ABIERTO (cámara) | **Abierta.** |
| `LUT-DE-1` | ABIERTO | **Código cerrado y verificado** (34 pares de Sharma). Queda sólo re-medir las cifras de G71/G88/G90 → conviene partir la fila en «código» (hecho) y «cifras» (abierto). Ojo: la regresión no corre en este entorno (§3.6). |
| `LUT-T-1` | ABIERTO | **En curso ahora mismo, sin commitear** y **no cabe** en `ZONA_A` (0x43be4348 > 0x43be4330) → 4 tests en rojo. |
| `LUT-T-2` | ABIERTO (cámara) | **Abierta.** |
| `LUT-2C-1` | ABIERTO | **Abierta**: la segunda curva de 512 puntos (identidad) no tiene consumidor localizado. |
| `LUT-MODO-1` | EN ESPERA | **Correcto dejarla en espera**, pero su evidencia (§3.5) es un volcado único que **no está** en el worktree. |
| `LUT-PKG-1` | HECHO offline | **Correcto**, con la contradicción «sin instalar / instalado como 3.86» (§4.4). |
| `LUT-FILM-1` | HECHO offline | **Correcto offline**; arrastra el conflicto de `BK_ID` (§4.3-3) y el build roto (§4.3-2). |
| `FN-LUT-1/5/6`, `ZONA-1` | ABIERTO / PARCIAL | `ZONA-1` **abierta para LUT** explícitamente. |

---

## 5. Tabla final: afirmación → estado → evidencia

| # | Afirmación | Estado | Evidencia (fichero:línea / test / medida propia) |
|---|---|---|---|
| 1 | Geometría **5×9×9 fija** en el ISP | **VERIFICADO** | `0x43b67918` desensamblado (8 casos `tbb`; `add.w` a `+0x17000…+0x17800`, `movs r2` = 0x12c/0xf0/0xf0/0xc0/0xc8/0xa0/0xa0/0x80 = 1620 B = 405 palabras); `movw #0x654` ×17; `avcam_dinamico.py:36,186`; `test_g90_lut_opt.py::test_perm_es_8_bancos_por_paridad` |
| 2 | «5×9×9 es el **máximo** del mapa de bancos» | **REFUTADO** | modelo de `test_g93_lut_geometria.py:21-41`; cálculo propio: `bancos(8,8)` = 64×8 ≤ ventana → **8³ = 512 cabe**; el test no prueba `cabe(8,8)` |
| 3 | Ampliarla es imposible por parche | **INFERENCIA** | bucles fijos 9×9×5 y copias 0x654; 18 registros de control de 1/6 bits (g90 §C); no hay campo de tamaño. Sólo cámara lo cerraría |
| 4 | LUT de **21 bits / 405 nodos** = 1064 B | **VERIFICADO** | `avcam_dinamico.py:186-192`; medida propia: 8505 bits, roundtrip exacto; 3×1064 ≤ 3432 B |
| 5 | **T de 1024 u16 tras la gamma** | **VERIFICADO** (sólo para esa T) | `tono_post.py:23-27,64`; `test_g92_tono_post.py::test_cadena_aplica_T_tras_la_gamma` / `test_curva_post_de_una_cadena` (len 1024). La T de `cube_a6000` es de **2048** (`cube_a6000.py:25`) y va antes de la LUT |
| 6 | Empaquetado y **CRC32** del `.LUT` | **VERIFICADO** | `lut_pkg.py:22-37`; `lutsd.c:260-291`; `test_g95_lut_pkg.py` (ARM = referencia, 6 mutaciones). Reserva: 5 B sin validar |
| 7 | **ConvSD inactivo** en esta cámara | **INFERENCIA** | `lut_modos.py:19-27` (lógica correcta); `test_g94_lut_modos.py:34 test_convsd_inactivo_en_la_ram_viva` **SKIPPED** (falta el volcado de 1 GiB); un solo estado de arranque |
| 8 | ConvSD es 709→601 en la croma | **VERIFICADO** (Unicorn) | `test_g94_lut_modos.py::test_convsd_de_fabrica_es_croma_709_a_601` (pasa); `lut_modos.convsd_fabrica` ejecuta el generador real |
| 9 | **ΔE2000 corregido** (LUT-DE-1) | **VERIFICADO** | `cube_a6000.py:113` (`C2p - C1p`); **medida propia: 34 pares de Sharma, error máx 4,95·10⁻⁵**; `de2000(x,x) = 0`. La regresión `test_g91…::test_de2000_pares_de_sharma` está **skipped** (módulo con `pytestmark`) |
| 10 | Rutas `X:/LUT/LUT<n>.cube` y `.LUT`; ranuras **LUT 1…6** | **VERIFICADO** en código | `lutsd.c:217-231` (4 variantes `/`/`\`, `.cube`/`.CUB`), `lutsd.c:280-285` (`.LUT` sólo `/`); `lut_patch.py` `AJ_SD` = Off + 6; `test_g89_lut_sd.py::test_ruta_alternativa_y_diagnostico_en_el_blob` |
| 11 | Calidad del paquete del PC vs `.cube` (evaluada en trilineal) | **VERIFICADO** (re-medido) | medida propia con `U.referencia` y `lut_pkg`: teal&orange **0,40/1,41** en cámara vs **0,07/0,16** en PC; película **1,05/2,38** vs **0,79/1,80** — coincide con G95 §2 (0,40/0,07 y 1,05/0,79) |
| 12 | `ZONA_A`/`ZONA_B` son huecos libres | **REFUTADO** | G107 §3 + verificación propia: `0x43705a3a-3e` → base `0x43BE3B28` (= `ZONA_A[0]`) y `ldrh [r3, r0<<1]`, `r0 ≤ 0x400`; `0x438f6fa4` descriptor dims 1/6/13/11 con punteros a 0x43C1FEF0/0x43C1FF08/0x43C205D4. La cueva LUT ocupa T1[512…1024] |
| 13 | `test_g74::_refs` demuestra «sin referencias» | **REFUTADO** | `test_g74_cuevas_seguras.py:42-57` sólo ve literales y `movw/movt`; el núcleo usa `ldr [pc]` + `add pc` |
| 14 | El ARM de `lutsd.c` = referencia Python | **VERIFICADO** | `test_g89_lut_sd.py::test_arm_igual_a_la_referencia` (17³/32³/33³) y `::test_arm_64_cubed_igual_a_la_referencia` (64³) — pasan |
| 15 | `.cube` «17³/33³/65³» en toda la cadena | **REFUTADO** | `cube_a6000.py:47` (sin tope), `lutsd.c:111` (**n ≤ 64**), `lutjpg.c:40` (n ≤ 129) |
| 16 | «Nada de esto se ha visto en cámara» | **VERIFICADO** (es el estado honesto) | LUT-SD-2 / LUT-SW-2 / LUT-T-2 abiertos en `PENDIENTES`; ningún informe muestra una medida en cámara |
| 17 | El build «film sin pp» funciona | **REFUTADO** | `build_cfw_film.py:196` + `:141` → `KeyError: 'sel'`, reproducido; 4 `errors` de la suite |

---

## 6. Los 5 riesgos mayores para llevarlo a la cámara

1. **La cueva y las tablas LUT se escriben dentro de tablas que el núcleo lee**
   (EIS T1 en `ZONA_A`, BOKS del YC de captura en `ZONA_B`), y el **CFW 3.86 ya instalado** las
   lleva ahí. G107 lo demuestra, yo lo he confirmado en bytes, y ni `lut_patch.py` ni la fila
   `LUT-C` lo reflejan. Es la causa más probable de un síntoma raro (estabilización o color de
   captura) atribuido a cualquier otra cosa. **Antes de cualquier prueba nueva: reubicar
   (ZONA-1) o no instalar LUT.**
2. **Nada del pipeline ha funcionado nunca en la cámara.** Los tres cierres reales
   (LUT-SD-2, LUT-SW-2, LUT-T-2) siguen abiertos y todo el ΔE publicado viene de un **modelo del
   PC**: matriz BT.601 fija, EOTF sRGB supuesta, **evaluado en trilineal** (`aplica_lut3d`) mientras
   el ajuste por defecto es «ambos», y sin medir el orden gamma/matriz/LUT. Si ConvSD se activa, si
   la matriz no es la que se supone o si el modelo de interpolación es tetraédrico, las cifras se
   mueven 0,2–1,5 ΔE sin que ninguna prueba lo note.
3. **El modelo de interpolación está sin decidir (LUT-INT-1)** y el ajuste por defecto
   (`"ambos"`) entrega tablas que no son óptimas para ninguno de los dos: se paga ≈ 0,2 ΔE bajo
   trilineal y sólo se recupera si se acierta. Es una decisión que necesita **una** foto por rampa
   con `exp_interp.py` y que arrastra a INT-2, OPT-1 y a la corrección de 2.ª diferencia de
   `lutsd.c` (derivada de la base trilineal).
4. **Recursos compartidos sin control de exclusión mutua**: un único `BK_ID 0x150005` para los hilos
   «LUTS» y «FILM» (diseños incompatibles), los mismos 4 ganchos de la curva tras la gamma y la misma
   `ZONA_A` para la cueva. Hoy se evita sólo por construir firmwares distintos; no hay test ni
   documento que lo fije, y el árbol actual **no compila la variante film-only** (`KeyError: 'sel'`).
5. **Ilusión de cobertura.** En esta máquina se saltan justo las pruebas que sostienen lo afirmado
   (ConvSD en RAM viva, mismo IP en A7S/A6300, cuevas a cero en vivo, ΔE2000 completo y **todo**
   `lutjpg`), los umbrales de ΔE son un 30–50 % más laxos que las cifras publicadas, y el test que
   «demuestra» que las zonas están libres es ciego al mecanismo real. Un verde de 136 passed no dice
   que el pipeline esté listo: dice que las piezas offline son consistentes entre sí.

---

### Reproducibilidad

```bash
# HEAD limpio e inmutable
mkdir -p /tmp/audit-head && cd /home/nicolas/Documentos/a6000/a6000-main
git archive HEAD | tar -x -C /tmp/audit-head
cd /tmp/audit-head            # + symlinks a analysis/ y firmware/ del worktree
env -u CI /home/nicolas/Documentos/a6000/a6000-main/.venv/bin/python -m pytest \
  tests/test_g7*.py tests/test_g88*.py tests/test_g89*.py tests/test_g9*.py \
  tests/test_g10*.py tests/test_g11*.py -q
# → 136 passed, 42 skipped, 4 errors in 346 s
```
