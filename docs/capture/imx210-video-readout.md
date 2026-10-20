# IMX210: matriz de registros por modo (SetMode) — A6000 3.21

Fuente: av-cam.bin sha256 `b60c845c…6bb9`, base lógica `0x43541000` (ELF de análisis
`analysis/av-cam-analysis-view.elf`, sha256 `8906a46c17f7451c…`). Reproducible:
`python3 -I scripts/imx210_modes.py` → `analysis/imx210-setmode-register-matrix.json`;
test `python3 -I tests/test_imx210_modes.py`. Complementa [imager-exposure-p2s.md](imager-exposure-p2s.md).

## Estructura (VERIFICADO, bytes originales)
- Tabla de modos lógicos `0x43fea070` (13 palabras, ya conocida): `0b 01 05 10 07 12 03 0a 0f 18 1a 19 2f`.
  Orden = columna 0..12 de la matriz. Modo `0x11` se trata aparte en `0x436d6b8c` (**VERIFICADO en Sesión 6**: si `[0x43e0a390+0x7c]!=0xff`, antes de la búsqueda aplica por `vtable+0xa0` el índice del modo `0x05` (1996×1124); después la búsqueda de `0x11` en la tabla da `0xff` y la función devuelve error 2. Es un alias que fuerza el modo 5 y notifica fallo; el significado de `[0x43e0a390+0x7c]` NO VERIFICADO).
- Tabla de registros: GOT `0x4401eee4+0x40a8` = `0x44022f8c` → **`0x43fe9b74`**. 59 filas de 20 bytes:
  `u32 ptr` (campo valor en la imagen RAM del registro; `ptr-2` = dirección `u16`) + 13 bytes (valor por modo) + 3 de relleno.
  Lector: `0x436d6570`/`0x436d65b8`; el ptr de la fila de `+2` es `0x4401ca2e` (misma que E019: selector de exposición).
- Registros direccionados: `0x000–0x155` (bytes). Bus físico del sensor (SPI/I2C hacia IMX210) sin trazar en el esquema; P50–P52 (CAM_SI/SO/SCK_1) de IC5700 son el enlace con el ASIC, NO con el sensor.
- Segunda tabla (28 B/registro) en `0x43bc20dc`, usada por `0x436d8e6c` con `ptr@+0x14`, `u16@+0x18`: en el archivo está a cero salvo `+0x18` = `0x0fff` (modos `0b,0f,2f`) / `0x0f00` (resto). Semántica NO VERIFICADA.

## Agrupación de modos (VERIFICADO por igualdad de columnas)
| Grupo | Modos lógicos | Rasgo |
|---|---|---|
| Fotográfico | `0x0b`, `0x2f` | Idénticos en los 59 registros. `0x0b` es el que elige `0x437f7ff0` para captura (`captura+0x4d0`; `0x2f` si `+0x4b70==6`; `0x01` si `0x43a12c64()==3`). |
| Fotográfico, reloj distinto | `0x0f` | Igual que `0x0b` salvo `0x11–0x14`=`94 06 c4 02` y `0x001`. |
| «Vídeo» | `0x05 0x10 0x07 0x18 0x1a 0x19` | **Columnas idénticas** (regs `0x11–0x14`=`4c 01 74 04`, `0x2a=04`, `0x142–0x152` ≠ foto…). Resolución/fps no salen de esta tabla. |
| Variantes | `0x01`, `0x12`, `0x03`, `0x0a` | Difieren de «vídeo» en `0x000`,`0x015`,`0x016`,`0x04f`,`0x12a`,`0x155`; `0x0a` conserva parte de salida estilo foto (`0x142–0x152`=foto). |

Los nombres «fotográfico/vídeo» son **HIPÓTESIS** por correlación con el llamador de captura; no hay datasheet IMX210 público que dé el significado de los bits.
Tabla diferencial completa: ver JSON (`rows[].values`).

## Geometría (VERIFICADO como datos, vínculo con modo NO verificado)
Descriptores en `0x43bb7f3c…`: 6048×4152, 6024×4024 (offset 12,140), 6000×4000, 6028×4024, 1736×1250(?). 1920×1080 y 1440×1080 en `0x43fe60b8…` (tablas con 720×480/768×480). Falta la función que une modo→descriptor (`getDriveModeSizeRatio`, `0x43ad908e`→thunk `0x43ad9644`).

## Llamadores de SetMode (wrapper `0x436d62e4`)
`0x438c79bc` (solo si `0x43a12c64()==3`), `0x438c84ec`, `0x438cc7ea`, y la cola `0x43795aaa` (estructura estática `0x43ff36d0`, modo `0x11`). Todos reciben `modo=captura+0x4d0` mediante `0x43795a60`. Llamadas por vtable slot `+0x20` aún sin enumerar.

## Siguiente comprobación
1. Enumerar llamadores indirectos de slot `+0x20`; atribuir modos a Live View / vídeo / foto.
2. Resolver `0x43a12c64` (valor global 0x01→3, 0x31–0x37/0xbc/0xee–0xef/0xfd–0xff→1, 0xbb→2).
3. Seguir `0x436d8c48/0x436d8e20` (aplican filas de 28 B) y `SetRead 0x436d7e08` para tamaño/fps.

## Sesión 2: pila de parámetros por modo (VERIFICADO salvo marca)
- **Vtable C_Imager IMX210** (`0x43fcc090`, slot `+0x28`=SetExposure `0x436d6f6c`): `+0x20` SetMode impl `0x436d6b50`; **`+0x24` GetModeInfo `0x436d96b8`**; `+0x28` SetExposure; `+0x2c` SetExposure_ZAF `0x436d67e4`; `+0x30` SetRead `0x436d7e08`; `+0x34` SetRead_ZAF `0x436d74b8`; `+0x38 0x436d839c`; `+0x3c 0x436d6a34`; `+0x44 0x436d7bc8`.
- `0x43a12c64` = clasificador de modelo/destino por valor global (0x01→3; 0x31–0x37, 0xbc, 0xee–0xef, 0xfd–0xff→1; 0xbb→2; resto 0). Solo elige el modo lógico en captura; no toca geometría.
- `getDriveModeSizeRatio` `0x43ad908e`→`0x43ad9644` llama **dos veces al slot `+0x24`** (GetModeInfo de dos modos) y calcula razón `(Camcore+0x2c · CS+4)/(…)` con `u8 +0x4/+0x5` y `u32 +0x48` del struct devuelto. El tamaño/razón NO sale de la matriz de 59 registros.
- **GetModeInfo(this, {modo u32, tipo u8@+4}, out)**: busca el modo en la lista `this+0x18` (índice `i`, 0xff = no existe → error 2), aplica el parche `0x436d9648(this,i)` (tabla global de 2 entradas ×8 B con `u16,u16,u8×3` e índice en `+0x87` → llamada virtual `+8` del objeto de parámetros: **escritura dinámica por modo**) y copia al struct de salida (≥0x104 B):
  `+0x00` **CSDrvParam** 28 B · `+0x1c` **CamcoreDrvParam** 100 B · `+0x80` **ECDrvParam** 48 B · `+0xb0` **LCDrvParam** 12 B · `+0xbc` 8 B · `+0xc4` u8 (`this+0x277`) · `+0xc8` **ECZafDrvParam** 48 B · `+0xf8` **LCZafDrvParam** 12 B. Tamaños = pasos de `0x436d939c/6f18/6f34/6f50/93b8`. Clase: `Camera::Imager::ImagerDrvParam_IMX210E` (typeinfo `0x43c94269`), `C_Imager::GetParam(ModeRsvParam*, DrvParam*)` (cadena `0x43c93624`), con `calcDrvParamWithArg` (cálculo dinámico, cadenas `0x43c94d53`/`0x43c94336`).
- Registro de campos (cadenas de log, solo orden, sin nombres): CS `%02x` + 16 campos; Camcore 31 campos (`0x43c94c49`); EC 17 (`0x43c94ce9`/`0x43c948f5`); LC 6×u16.
- **Tabla de 28 B `0x43bc20dc` (14 filas)** = filas de `0x436d8e6c`: `u32 +0x14` es **índice** (no puntero; 0 salvo fila 13 = 4) hacia filas de 12 B de `0x436d8c48`, y `u16 +0x18` es máscara de 12 bits (0x0fff en filas 0, 8, 12 — coincide con los modos 0b/0f/2f —; 0x0f00 en el resto) que `0x436d8c48/0x436d8e20` expanden a pares (bit, byte) de 12 canales. INFERENCIA: enrutado de canales/carriles del receptor serie (CS = camera serial), no filas ni fps.
- Las tablas con 1920×1080/1440×1080/1280×720/720×480 de `0x43fe60b8` (registros de 0x44 B) son formatos de salida/pantalla, **no** modos del sensor (DESCARTADO como geometría IMX210).
- **Bloqueo**: los arrays de CS/Camcore/EC/LC (objeto `this+0x294`, punteros `+0x10…+0x20`, número `+4`) no están en la imagen estática; se rellenan en la construcción de `ImagerDrvParam_IMX210E`. Resolución, fps y filas están ahí (no en la matriz). Siguiente paso: localizar vtable/constructor de esa clase (typeinfo `0x43c94269`) y volcar los valores.

## Sesión 2b: constructor y tablas por modo (reproducible: `scripts/imx210_param_tables.py`, `tests/test_imx210_param_tables.py`, `analysis/imx210-drvparam-inputs.json`, `analysis/ghidra/imx210-calc-drvparam*.json`)
**Constructor (VERIFICADO)**: vtable `ImagerDrvParam_IMX210E` `0x43fcc150` (GOT `0x44022e64`); ctor `0x436d8774` (base `0x436d99b8`, vtable base `0x43fcc230`); lo invoca el ctor de C_Imager `0x436d72e8` en `0x436d7378` sobre `this+0x350` con N=13 y `0x43fea070` (lista de modos). Argumentos (campo del objeto ← dirección): `+0x10` CS `0x43e7f870` · `+0x14` Camcore `0x43e7f9dc` · `+0x18` EC `0x43e7fef0` · `+0x1c` LC `0x43f616cc` · `+0x20 0x43bc2044` · `+0x24 0x43bdbd78` · `+0x28` filas 36 B `0x43bc1d58` · `+0x2c 0x43bdbe70` · `+0x30` filas 24 B `0x43bc1c20` · `+0x34` filas 72 B `0x43bc16dc` · `+0x38/+0x3c` A/B `0x43bc1ae8`/`0x43bc1b84` · `+0x40/+0x44` ECZaf/LCZaf `0x43e80174`/`0x43f61768` · `+0x48 0x43bc1604`.
Los arrays de **salida** (CS/Camcore/EC/LC/ZAF) están a cero en la imagen (solo los referencia el ctor); los calcula `calcDrvParam` `0x436d9d00(this, sys, arg, idx)` (vtable `+8` `0x436d88cc` la llama y recalcula ECZaf/LCZaf): CS←`0x43ad975e` (fila 24 B + razón con `float`), Camcore←`0x43ad97e0` (**copia casi literal de la fila 72 B**, `[0]`=id de modo, `[+0x59]`=`sys+0x12`-1), EC←`0x43543dc8`, LC←`0x43543fa0` (ambas con doble precisión, dependen de `arg`, tomado de la tabla de 2 entradas de `0x436d9648`). Por tanto las **entradas** rodata fijan geometría y periodo; EC/LC añaden exposición/temporización derivadas.

**Tabla por modo (VERIFICADO como datos; significado = INFERENCIA salvo nota)**
| modo | cols (fila72 w7) | filas (w15) | CS float | a·b NTSC / PAL | periodo (54,054 MHz) |
|---|---|---|---|---|---|
| 0x0b, 0x2f | 6000 | 4000 | 143 | 864·4176=3 608 064 (ambos) | 14,98 Hz (66,8 ms) |
| 0x01 | 2000 | 570 | 81 | 693·1300 / 720·1500 | 59,94 / 50 Hz |
| 0x05, 0x10, 0x18, 0x1a | 1996 | 1124 | 82 | 693·1300 / 720·1500 (0x05,0x10: 800·1350 PAL) | 59,94 / 50 |
| 0x07 | 1996 | 1124 | 82 | 875·1287 | 48 Hz |
| 0x19 | 1996 | 1124 | 82 | 693·1625 | 48 Hz |
| 0x12 | 2000 | 570 | 69 | 693·650 / 720·750 | 119,9 / 100 Hz |
| 0x03 | 2000 | 800 | 82 | 693·1300 / 720·1500 | 59,94 / 50 |
| 0x0a | 2000 | 232 | 43 | 693·300 | ≈260 Hz |
| 0x0f | 1024 | 684 | 112 | 858·1050 / 864·1250 | 59,94 / 50 |
- VERIFICADO aritmético: a·b=900 900 en todos los modos de 59,94 Hz (=54,054 MHz/59,94) y 1 080 000 en los PAL (=54 MHz/50). Eso fija que `(a,b)` de las tablas A/B `0x43bc1ae8/0x43bc1b84` son longitud de línea y líneas totales del cuadro; variante 0 = 60 Hz, variante 1 = 50 Hz (selector `r6` del ctor, `0x436d7478`).
- **Lectura completa 24 MP (0x0b/0x2f)**: 6000×4000 útiles en 4176 líneas, periodo de cuadro ≈66,8 ms (≈15 fps) en ambos sistemas. Es el tiempo de barrido de rolling shutter electrónico a resolución completa (INFERENCIA: unidad de reloj coherente con 59,94 Hz; no hay datasheet).
- **Modos «vídeo» 0x05/0x10/0x18/0x1a/0x19/0x07**: 1996×1124 ≈ 2,24 MP (6000/3 columnas, 16:9; 1080p sale de aquí tras escalado, 1124≥1080). Distinción entre ellos: fps (0x07, 0x19 = 48 Hz, el resto 59,94/50) y bytes de las filas 24/36 B; NO identificado qué modo es 1080p60 frente a 1080p24/50.
- **0x01/0x03/0x12/0x0a/0x0f**: 2000×570 (60 y 120 Hz), 2000×800 (rel. 6000×4000 = ÷3 horiz, ÷5 vert → campo completo 3:2, candidato Live View/AF, HIPÓTESIS), 2000×232 (≈260 Hz, candidato medición/AF rápido), 1024×684 (ventana pequeña a 60 Hz con reloj 112).
- Uso real por función: VERIFICADO (decompilado `0x437f7ff0`, `0x437f7f98`, `0x43affd86`, `0x43affda2`): el selector de captura pone `captura+0x4d0` = 0x2f si `+0x4b70==6`; 0x01 si `0x43a12c64()==3`; si no, 0x0b cuando `0x43affd86` ≠ 0, o `0x437f7f98(+0x1e0,+0x6c8)`: clase 5→0x0c, 0x1b→0x1b, sub 1→0x35, sub 2→0x17, sub 0→0x0b, otro→0x0b+log. Un byte global (`[DAT_4402546c+0x86]`≠0) lo sobrescribe (override de depuración). **0x0c, 0x17, 0x1b y 0x35 NO están en la lista de 13 modos IMX210** (GetModeInfo devolvería error 2): código compartido con otros sensores/cámaras. `+0x6c4=min(modo,1 si >0x47)`; `+0x6d0` = razón de `getDriveModeSizeRatio(ref=0x35|0x0b, modo)`.
**CORRECCIÓN (DESCARTADO)**: el handler del mensaje `0x4019` (`0x43803780`) no fija el modo del sensor: guarda un byte en el global `DAT_43edfb54` (objeto de ajustes `0x43edf684`) y notifica `0x437dfba0`. El emisor (`0x43818a80`, msg tipo 5 id `0x4019`) envía `0x4381a6fc(b)` = identidad para 0..3, 2 si >3 (tabla `0x43bc55b0`). Es un enum 0–3, no un modo 0x05/0x10/…; la pista `captura+0x4D0` del plan era un offset homónimo de otro objeto.
**Qué modos 1996×1124 se usan y quién los selecciona: RESUELTO en «Sesión 3» (más abajo).** Lo anterior («ninguna ruta de captura los produce») sigue siendo cierto solo para el selector de captura; el selector de vídeo/Live View es otro (`0x4380e43c`).

## Sesión 3 — selector de modo de vídeo/Live View (`0x4380e43c`)
- VERIFICADO (decompilado `analysis/ghidra/mode-pick-4380e43c.json`): `FUN_4380e43c(ctx, ..., flag)` calcula el modo en el global `DAT_43eea2e4` mediante `switch((ctx.cfg[+0x264] & 0xfffff) >> 15)` (estado de operación 0..0x12; nombres `REQ_MOVIE`, `REQ_MOVIE_REC`, `REQ_STILL_EE`, … en la tabla de cadenas `0x43ca1300`, correspondencia caso↔nombre NO verificada). Cadena de escritura: `0x4380f440` copia `DAT_43eea2e4` (0x44 B) a la petición `DAT_43e994d0`; `0x43792a0c` la compara con la vigente `DAT_43e99320`; `0x4378ea78`/`0x437957ec` la pasan a `SetSequenceMode_img` (`0x4378e334`), que llama a `SetMode` `0x43795a60` con `*(estado+0x44)` (estado de imagen en `0x43e9baec`, modo en `0x43e9bb30`, flips en `+0x1bc/+0x1bd`).
- VERIFICADO: la comprobación «¿soporta el imager el modo X?» es `FUN_43ad909c` (= vtable[`+0x94`] del imager). Para IMX210 el conjunto soportado es el de los 13 modos: {01,03,05,07,0A,0B,0F,10,12,18,19,1A,2F}; los modos 0x08, 0x11, 0x20…0x44 del selector pertenecen a otros imagers.
- **Vídeo (caso 7, campo de formato `cfg[+0x1d4]`)** — VERIFICADO en código:
  - formato 2 o por defecto (1080 normal): si el imager soporta 0x10 → 0x1A si `ctx.b[+0xb1]==0` y soporta 0x1A; si no 0x10. Si no soporta 0x10 → 0x18 / 0x05 análogamente. En IMX210 (soporta 0x10 y 0x1A): **0x1A o 0x10**. Con ranura de memoria alta velocidad (`cfg[+0x20c]!=0`): 0x32/0x34 (no IMX210).
  - formato 3 (24p): soporta 0x19 y `b[+0xb1]==0` → **0x19**; si no **0x07**. Con `[+0x20c]!=0`: 0x33.
  - formato 4 → **0x12** (2000×570, 120/100 Hz); formato 5 → 0x08 (no IMX210).
- **Live View / EE de foto (casos 0–6)** — VERIFICADO: modo 0x01 o 0x03 vía `FUN_4380de60` (3 si el byte `[DAT_4402546c+0x35]` o `ctx+0x80` lo piden y el imager soporta 3; si no 1/3 según `[DAT_4401f1d0+0x36]`; 0x39 si lo soporta, no IMX210); 0x0F en el caso 0 cuando `FUN_43794a44(ctx)!=0` (1024×684, ventana pequeña); 0x44/0x30 no existen en IMX210 y se degradan a 1. Es decir, **Live View de IMX210 = 0x01 (2000×570) o 0x03 (2000×800), no los 1996×1124**.
- Resumen: los 1996×1124 (0x05/0x10/0x18/0x1A = 1080 a 60/50 Hz, 0x07/0x19 = 24p/48 Hz) son **solo de vídeo**; Live View de foto usa 2000×570/2000×800. El selector de captura (`0x437f7ff0`) es independiente y produce 0x0B/0x2F/0x01.
- INFERENCIA: 1996×1124 = recorte 16:9 de 6000 columnas con binning 3×3 (no anamórfico). 2000×570 y 2000×800 son anamórficos (÷3 horizontal, ÷7 / ÷5 vertical) y se reescalan en el ISP.
- NO VERIFICADO: significado de `ctx.b[+0xb1]` (elige 0x1A/0x19 frente a 0x10/0x07); nombres exactos de los estados 0..0x12.


Véase también «Sesión 4» de `electronic-still-low-resolution.md` (ruta C: ISP → RCV → JPEG sin obturador, alcance en A6000 NO VERIFICADO).
- Sesión 5: ver docs/capture/electronic-still-low-resolution.md (despachador y SFRA); los modos 0x08/0x11 de las secuencias HS no son del IMX210.
- Sesión 6: SetMode lógico `0x436d6b54` (VERIFICADO): devuelve 1 si modo 0, 2 si modo>0x47 o no está en la tabla de 13; el caso `0x11` programa antes el modo 5. Ver «Sesión 6» en `electronic-still-low-resolution.md`.
