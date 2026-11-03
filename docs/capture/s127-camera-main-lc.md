# S127 — `[CAMERA_MAIN_LC]` no calibra la lente: es el motor de AF de `Camera::LC`

**Hito:** línea general de RE · **Binario:** A6000 fw3.21 (`analysis/rea-independent/input/av-cam.bin`, vaddr = `0x43541000` + offset) · **Regla de referencias:** estricta (canónica). **Sin efecto en S51.**

Informe: [`camera_main_lc.md`](../../analysis/s127_camera_main_lc/camera_main_lc.md) · Datos: [`camera_main_lc.json`](../../analysis/s127_camera_main_lc/camera_main_lc.json) · Test: [`tests/test_s127_camera_main_lc.py`](../../tests/test_s127_camera_main_lc.py)

## Hallazgo

- **72 cadenas** `[CAMERA_MAIN_LC]:` de `0x43c9c6f6` a `0x43ca7e0b`; **78 sitios** PIC y **37 funciones** emisoras. **1 cadena sin referencia**: `0x43c9c779` `[ERROR!!] lc_Movie_DM_AF_Util_getBufferAddr()`.
- **Ninguna es una traza de calibración óptica.** El bloque emite estado/errores del motor de AF: buffers y MMU del *DM AF* (`miniRAW`, `resizedY`, `saIf`, `ESRAM/DDR_Bank`), volcado *scan/predict* (`pre position…`, `0x43c9ced2`), `lc_HybridAF`, `LC_SendMessage`, el resultado ZPD (`LC_GetZpdResultInfo`, `0x437c1e48`) y los hooks `zpd_HybridMovieAF`.
- La palabra "calibración" está en el bloque vecino de S126 (`calibration_fc_pos` `0x43c9c57b`, `Calibration start` `0x43c9c6d5`); esas funciones **llaman** a helpers de este bloque (`bl 0x4373c7f8`, `0x4373c478`, `0x4373c4e4`, `0x4373c558`, `0x4373c8e8`).
- El nombre del módulo es **`Camera::LC`** (RTTI: `MarioAfcState` `0x43c9d11a`, `CPafState` `0x43ca7b17`, `CPAFCoordControl` `0x43cb60e5`). **`LC` no está expandido** y la etiqueta no cubre todo el módulo (hay trazas `[CAMERA_MAIN]` del mismo módulo, S126).

## Reparto medido

| bloque | cadenas | sitios | funciones tocadas |
|---|---:|---:|---:|
| `0x43c9c6f6`–`0x43c9d646` | **32** | 37 | 22 (19 propias + 3 *still* por 3 mensajes compartidos) |
| `0x43ca71fa`–`0x43ca7e0b` | **40** | 41 | 18 (15 propias + 3 compartidas) |

13 sub-bloques: DM AF *movie* (14), `lc_AF_Scan` (2), scan/predict (7), `lc_HybridAF` (2), `LC_SendMessage` (2), `MS_Writer` (1), housing (2), OSAL (2), rlog (10), DM AF *still* (10), `LC_GetZpdResultInfo` (10), mlog (3), `zpd_HybridMovieAF` (7).

## ZPD (`LC_GetZpdResultInfo` = `0x437c1e48`, 10 trazas)

Gate: `ldrb.w r3,[rX,#0xc0]` `0x437c1e5a` + `tst.w r3,#2` `0x437c1e5e` + `beq` `0x437c1e64`; si falla, `LC_GetZpdResultInfo:Error` `0x43ca78b6`. Llamador medido: `bl` desde `0x439d9d82`.

Layout (corregido): `[r4]+0x00` `buffer_user_id`; `+0x3c4/+0x3c8` `zpd_flags/defocus`; `+0x3cc/+0x3d0` `selected_ym/selected_contrast`; `+0xce4` `base_defocus`; `+0xce8` `zaf_now_shut_cycle`; `+0xcec` `iris_cur`; `+0xcf0` `select_area` (byte); `+0xcf1` `mario_use_ng_flag` (byte). `full_count` viene del **primer argumento** (`r7`), no de `[r4]`.

Puente al AF híbrido: `NOT_DETECT from ZPD MODULE… lc_HybridAF.cpp %d` `0x43c9d07e` lo emite `0x43754be0`, el mismo `lc_HybridAF` que decide el *scanless manymode* (`0x43c9d0d5`); enlace ya documentado en S75.

## Diferencial

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---:|---:|---:|
| cadenas con el prefijo | 72 | **0** | **0** |
| mensajes interiores idénticos como cadena independiente | 72/72 | **0/72** | **0/72** |

La etiqueta es nueva en la fw3.21; los conceptos existen sin etiqueta (`lc_HybridAF.cpp`, `fc_pos`, `MarioAfc`, `zpd_`, `LC_GetZpdResultInfo`). Matiz: `************` `0x43c9d03e` sí aparece como **subcadena** en A7S/A6300, pero solo como cola/relleno de otras cadenas, no como traza LC independiente; el 0/72 se mantiene.

## Cierre CAM-01 (03-11-2026, medido en bytes)

- Ficheros fuente: 37 funciones con traza; 1 citan un fichero fuente (`lc_wrap_upm.cpp`); 36 ninguno.
- `watkao` (1 cadena), `kinbou` (1), `yosoku` (1) y `mario_use_ng_flag` (1) existen solo como texto de trazas.
- Token `[CAMERA_MAIN_LC]`: 72 en A6000, 0 en A7S y A6300.
- Nada medido toca la línea del obturador: **S51 se mantiene**.

Método: `analysis/camera_closure/sources.py` (cadenas `.cpp/.h/.c` desnudas cargadas con la regla PIC estricta dentro de cada función; fin de función = siguiente `push {…,lr}`) y `closure2.py` (referencias a una función: `bl`/`b.w`, literal de 32 bits con o sin bit Thumb, `ldr`+`add pc` en la misma función, `movw`+`movt`). Siglas, nombres de fichero y significados de campos que el firmware no declara **no son afirmaciones de este informe**: no se atribuye ni se infiere ninguno.
