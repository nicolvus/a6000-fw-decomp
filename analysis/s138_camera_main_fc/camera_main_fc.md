# S138 — el módulo `[CAMERA_MAIN_FC]` (9 trazas)

Hito de la línea de RE general. Solo análisis de bytes (`analysis/rea-independent/input/av-cam.bin`,
A6000 fw3.21). Convención: **vaddr = 0x43541000 + file_offset**.
Regla de referencias: **estricta** (cada `add rX,pc` con el `ldr rX,[pc,#imm]` más cercano;
`analysis/s106_imaging_cap/scan_pic_refs_strict.py`), y los 13 sitios se han **recalculado a mano**
(`analysis/s138_camera_main_fc/verify_sites.py` → 13/13 correctos).

## 1. Resumen

* **9 cadenas** con el prefijo exacto `[CAMERA_MAIN_FC]: `, en `0x43ca6944`–`0x43ca6aec`
  (9 textos distintos, 9 apariciones del token en toda la imagen).
* **13 sitios PIC** (regla estricta) repartidos en **7 funciones** emisoras, todas en el bloque
  de código `0x437b7200`–`0x437b821e` (dentro de la zona `CAMERA_MAIN`).
* Las 9 trazas son **exclusivas de la A6000 fw3.21**: 0 apariciones del token en la A7S fw3.20 y
  en el A6300 fw2.01; **ninguno** de los 9 núcleos de texto existe allí, y **0/8** fragmentos
  de código (48–64 B) del módulo se encuentran en esos dos firmwares.
* La **sigla `FC` tiene base textual**: es el *namespace* C++ `Camera::FC` (28 cadenas de
  aserción, p. ej. `Camera::FC::FCTop::ExecApiNotifyStartTouch` `0x43cefa06`) y el árbol de
  ficheros `FC/**/*.cpp` (99 ficheros, `0x43cef12a`–`0x43cf707a`). Esa biblioteca es
  **idéntica en los tres firmwares** (45 apariciones de `Camera::FC::` y 101 de `FC/` en cada uno).
  No se desarrolla la sigla más allá de ese namespace.
* **No participa en la cadena de disparo táctil** documentada en
  `docs/capture/shutter-trigger-chain-0x3011.md` / `shutter-trigger-state-machine.md`:
  ninguna función de esa cadena (`0x4379d838`, `0x4379e6a8`, `0x4379eba0`→`0x3011`,
  `0x43809ed8`, `0x437df640`, `0x437df338`, `0x437eabfc`, `0x437e4de4`) llama a la zona del
  módulo ni a la biblioteca `Camera::FC`. El módulo **sí** tiene su propia API de respuesta
  al disparo táctil (`ReplyForTouchShutter` / `SetRequestReplyForTouchShutter`), cableada por
  el wrapper de captura `wrapper/Face.cpp`, pero por un camino distinto del `0x3011` (§7).

## 2. Qué es `[CAMERA_MAIN_FC]`

Es la **capa de glue de `CAMERA_MAIN` hacia el subsistema de detección de caras/ojos `Camera::FC`**.
Contenido verificado de las 9 trazas:

| tema | trazas | qué se ha verificado en el código |
|---|---|---|
| datos de ojo y flag `lc` | `Eye data is invalid, but lc flag is true.` | dos flags del contexto, `[ctx+0xde]` y `[ctx+0xdf]`, deben valer 1; se comprueban 2 veces cada uno (`0x437b723e`, `0x437b7274`, `0x437b72c0`, `0x437b72fa`) |
| temporizador OSAL | `OSAL_ERROR: osal_alloc_timer`, `… osal_set_timer`, `… osal_free_timer` | `0x437b74a4` (alta/activación) y `0x437b7778` (baja) hablan con OSAL (`0x43561244` envío, `0x4356127c` recepción con timeout, `0x43561298` cierre) |
| modo de aplicación | `APP MODE ERROR: face_on, obj_on` | `0x437b7844`: error si `[ctx+0x49c]` (face) **y** `[ctx+0x49e]` (obj) están ambos activos |
| batería | `OSAL_ERROR: BatteryInfo` | `0x437b7d6c`: petición OSAL de información de batería (2 caminos de error) |
| disparo táctil | `ReplyForTouchShutter ERROR - NULL cb_func`, `SetRequestReplyForTouchShutter ERROR - multiple request`, `SetRequestReplyForTouchShutter ERROR - NULL cb_func` | `0x437b7ea0` y `0x437b81f0`: API de registro/invocación de un **callback de respuesta al disparo táctil** |

**Impresor**: logger privado del módulo en `0x437b7158` (11 llamadas, todas dentro del bloque).
Construye el mensaje por OSAL (`osal_try_valloc_msg` `0x435612d0`, envío `0x43561244`, formato
`0x439c5004`, `osal_free_msg` `0x435612ec`, `osal_snd_msg` `0x4356120c`) con la convención
`r0=3` (nivel), `r1=5` (módulo), `r2=1` (máscara), `r3` = puntero a la cadena — el mismo patrón
que el logger de `[CAMERA_MAIN_IM]` (S129, `0x437b85ac`).

**Mecanismo del callback de disparo táctil** (verificado byte a byte en `0x437b7f8a`–`0x437b7fb0`):

```
0x437b7f8a  ldr r3,[pc,#0x4c] / add r3,pc   -> flag global en 0x43f9a564
0x437b7f96  ldr r0,[pc,#0x44] / add r0,pc   -> ranura del callback en 0x43eb3bf0 (valor inicial 0)
0x437b7f9c  ldr r1,[r0]                     ; r1 = callback guardado
0x437b7f9e  str r2,[r0]                     ; se limpia la ranura
0x437b7fa0  cbz r1,#0x437b7fa6              ; si es NULL -> traza "NULL cb_func"
0x437b7fa2  blx r1                          ; si no, se invoca
```

## 3. Las 9 trazas

| # | vaddr | texto | sitios PIC (verificados a mano) |
|---|---|---|---|
| 1 | `0x43ca6944` | `[CAMERA_MAIN_FC]: Eye data is invalid, but lc flag is true.` | `0x437b7268`, `0x437b72a6`, `0x437b72ee`, `0x437b7326` |
| 2 | `0x43ca6980` | `[CAMERA_MAIN_FC]: OSAL_ERROR: osal_alloc_timer` | `0x437b7548` |
| 3 | `0x43ca69af` | `[CAMERA_MAIN_FC]: OSAL_ERROR: osal_set_timer` | `0x437b7570` |
| 4 | `0x43ca69dc` | `[CAMERA_MAIN_FC]: OSAL_ERROR: osal_free_timer` | `0x437b77f4` |
| 5 | `0x43ca6a0a` | `[CAMERA_MAIN_FC]: APP MODE ERROR: face_on, obj_on` | `0x437b787c` |
| 6 | `0x43ca6a3c` | `[CAMERA_MAIN_FC]: OSAL_ERROR: BatteryInfo` | `0x437b7db6`, `0x437b7df6` |
| 7 | `0x43ca6a66` | `[CAMERA_MAIN_FC]: ReplyForTouchShutter ERROR - NULL cb_func` | `0x437b7fae` |
| 8 | `0x43ca6aa2` | `[CAMERA_MAIN_FC]: SetRequestReplyForTouchShutter ERROR - multiple request` | `0x437b8200` |
| 9 | `0x43ca6aec` | `[CAMERA_MAIN_FC]: SetRequestReplyForTouchShutter ERROR - NULL cb_func` | `0x437b820e` |

**0 cadenas sin referencia** (las 9 están referenciadas).

## 4. Funciones que las referencian (mapa función→traza)

| función | rol | sitios | trazas | llamadores entrantes en `av-cam.bin` |
|---|---|---|---|---|
| `0x437b7200` | cálculo de área de cara/ojo | 4 | #1 | `0x437b7682`, `0x437b76d4` (internos) |
| `0x437b74a4` | alta/activación del temporizador OSAL | 2 | #2, #3 | `0x437b768c`, `0x437b76de`, `0x437b770c` (internos) |
| `0x437b7778` | baja del temporizador OSAL | 1 | #4 | **ninguno** |
| `0x437b7844` | `APP MODE` face_on/obj_on | 1 | #5 | `0x437b7ed4` (interno) |
| `0x437b7d6c` | `BatteryInfo` | 2 | #6 | `0x437b7ee6` (interno) |
| `0x437b7ea0` | `ReplyForTouchShutter` | 1 | #7 | `b.w` en el **thunk** `0x43aef72e` ← `bl` en `0x437b668c` |
| `0x437b81f0` | `SetRequestReplyForTouchShutter` | 2 | #8, #9 | `b.w` en el **thunk** `0x43aef736` ← `b.w` en `0x4380a4c8` ← `bl` en `0x43808058` |

**API exportada por thunks**: el subsistema FC expone su API con *colas de ramificación*
(thunks) en `0x43aef72e`–`0x43aef736`:

| thunk | destino | nombre | quién lo llama |
|---|---|---|---|
| `0x43aef72e` | `0x437b7ea0` | `ReplyForTouchShutter` | `bl` en `0x437b668c` (área `CAMERA_MAIN` 0x437b6xxx) |
| `0x43aef732` | `0x437b7fe4` | copia del estado de áreas de cara/ojo | `bl` en `0x4378f6a6` (área `CAMERA_MAIN` 0x4378fxxx) |
| `0x43aef736` | `0x437b81f0` | `SetRequestReplyForTouchShutter` | `b.w` en `0x4380a4c8` ← `bl` en `0x43808058` (dispatcher de captura) |

Además, `0x437b7598` (cálculo de áreas de cara) se alcanza por una cola de ramificación
`b.w` en `0x43aef9ca`.

El barrido de entrantes se hizo por **cinco mecanismos independientes** sobre toda la
imagen: `bl` directo, `b`/`blx`/`b.w` inmediato (incluidas las colas de ramificación),
puntero absoluto de 32 bits (con y sin bit Thumb), materialización PIC `ldr`+`add`
(regla estricta **y** ancha) y tablas de salto `tbb`/`tbh`.

**Única función sin referencia entrante**: `0x437b7778` (la que emite
`OSAL_ERROR: osal_free_timer`). No se puede afirmar que sea código muerto: podría
invocarse desde otro binario del paquete de firmware.

> Nota metodológica: un primer barrido que solo miraba `bl` daba "módulo sin arista de
> entrada". Era **falso**: las entradas del módulo llegan por *colas de ramificación*
> (`b.w`), no por `bl` directo. El barrido inverso definitivo es
> `analysis/s138_camera_main_fc/scan_branches.py`.


## 5. Ficheros fuente

| elemento | vaddr | estado |
|---|---|---|
| fichero propio del módulo `[CAMERA_MAIN_FC]` | — | **NO VERIFICADO**: ninguna de las 9 trazas cita un `.cpp` (a diferencia de `[SFRA]`, `[IMAGING]` o `[MOUNT_DEBUG]`) |
| namespace `Camera::FC` (28 cadenas de aserción) | `0x43cef20d`–`0x43cf7137` | **VERIFICADO** en los bytes (p. ej. `Camera::FC::FCTop::ExecApiNotifyStartTouch` `0x43cefa06`, `Camera::FC::FeatureTouch::SendTouchResultToMonFace` `0x43cefef0`, `Camera::FC::SequenceTouch::Error` `0x43cf0fae`) |
| árbol `FC/**/*.cpp` (99 ficheros) | `0x43cef12a`–`0x43cf707a` | **VERIFICADO** (S111): `FC/fc_top.cpp` `0x43cf02f6`, `FC/fc_api.cpp` `0x43cf02e8`, `FC/Seq/fc_seq_touch.cpp` `0x43cf082f`, `FC/Feature/fc_feature_capture.cpp` `0x43cf0779`, `FC/Alg/fc_alg_exif_face_data.cpp` `0x43cf0737` |
| código de la biblioteca `Camera::FC` | ~`0x439d0000`–`0x439fffff` | **VERIFICADO** por los sitios PIC de esas cadenas (`0x439d6c7e`–`0x439d9f26`, `0x439d985e`, `0x439daf06`, `0x439df57c`, `0x439ff222`–`0x439ff952`) |
| lado captura de la detections | `wrapper/Face.cpp` `0x43cb03e3` (sitios `0x4380a33a`, `0x4380a3d2`, `0x4380a472`) y `UInt32 Face::RcvFaceIFCmd(FaceSetParam*)` `0x43c62753` (sitios `0x43603ae2`, `0x43603b74`) | **VERIFICADO** |
| enlace `wrapper/Face.cpp` → biblioteca FC | las funciones `0x4380a384` y `0x4380a424` llaman a `0x439d95bc`/`0x439d953c`, dentro del bloque que referencia `FC/Api/fc_api_tracking.cpp` `0x43cefa43` (5 sitios PIC `0x439d9510`–`0x439d9614`) | **VERIFICADO** |

## 6. Relación con los módulos ya documentados

* **`[CAMERA_MAIN]` (S126)**: el bloque de código del módulo es la misma zona "contenedor" de
  `CAMERA_MAIN` (0x437b7xxx), y el módulo es una de las sub-etiquetas de ese contenedor, como
  `[CAMERA_MAIN_LC]`, `[CAMERA_MAIN_IM]`, `[CAMERA_MAIN_CC]`, `[CAMERA_MAIN_SYNC]` o
  `[CAMERA_MAIN_TC]`.
* **`[CAMERA_MAIN_IM]` (S129)**: su despachador está en `0x437b8384`, a menos de 0x200 B del
  final del bloque FC (`0x437b81f0`): son **módulos hermanos** en el mismo área de código.
* **`[CAMERA_MAIN_LC]` (S127)**: la traza #1 nombra un flag `lc` (`Eye data is invalid, but lc
  flag is true.`); el flag leído es `[ctx+0xdf]` (y su gemelo `[ctx+0xde]`). Es la **única
  mención cruzada** entre FC y LC en todo el firmware (las 72 trazas de `[CAMERA_MAIN_LC]` no
  mencionan `face`/`eye`/`obj`/`touch`/`shutter`: 0 coincidencias).
* **`[CAMERA_MAIN_SYNC]` (S112)**: 9 de sus 429 trazas hablan de caras (`SendFaceFocusYCPin0`
  `0x43ca51fc`, `Sequence_Face` `0x43cb16ae`, `Face Memory Alloc Error` `0x43cb0ee4`, …), es
  decir, la cara está repartida entre varios submódulos de `CAMERA_MAIN`.
* **`[CAMERA_MAIN]` (S126)**: `Scanless NG because of Face AF` `0x43c9cd3f` (relación con el AF
  de cara).
* **`[TRK]` (S111)** y la biblioteca `Camera::FC`: son el nivel de detección; el módulo FC de
  este hito es el nivel de * glue* de `CAMERA_MAIN` con ese nivel.
* **Sin relación directa** con `[CAMERA_MAIN_CC]` (S123) ni `[CAMERA_MAIN_TC]` (S122): ni una
  sola dirección compartida y ninguna traza común.

## 7. Relación con la cadena de disparo táctil

`docs/capture/shutter-trigger-chain-0x3011.md` y `docs/capture/shutter-trigger-state-machine.md`
documentan la cadena: `RelMgr` `0x4379d838` → `0x4379e6a8` → `0x4379eba0` (tipo 2, id `0x3011`,
cola `0x40193`) → `CamUser` `0x43809ed8` → `CaptureStart` `0x437df640` → `0x437df338` →
selector `0x437eabfc` → `Image` `0x4381bd4c`.

**Verificado (negativo)**: desensamblando las 8 funciones de esa cadena y listando **todos**
sus destinos de rama (`bl`, `b.w`, `blx`, `b`), **ninguna** apunta a la zona del módulo
(`0x437b6000`–`0x437b8400`), ni a la biblioteca `Camera::FC` (`0x439d0000`–`0x43a00000`),
ni a sus thunks (`0x43aef72e`/`0x43aef732`/`0x43aef736`). Y a la inversa, las funciones del
módulo no llaman a ninguna de las direcciones de la cadena.

**Matiz importante**: el módulo **sí implementa una API propia de respuesta al disparo táctil**
(`ReplyForTouchShutter` / `SetRequestReplyForTouchShutter`, §2), con un puntero a callback
almacenado en la ranura global `0x43eb3bf0` e invocado indirectamente (`blx r1` en `0x437b7fa2`).
Esa API **está cableada**:

* el **wrapper de captura** `wrapper/Face.cpp` (`0x4380a384` y `0x4380a424`; la traza
  `wrapper/Face.cpp` se referencia en `0x4380a33a`, `0x4380a3d2` y `0x4380a472`) llama a la
  biblioteca `Camera::FC` —concretamente a `FC/Api/fc_api_tracking.cpp` (`0x43cefa43`, 5 sitios
  PIC en `0x439d9510`–`0x439d9614`)— y el **dispatcher de captura** (función que empieza en
  `0x43807f4c`) llama a `0x4380a4c4` → thunk `0x43aef736` → `SetRequestReplyForTouchShutter`;
* `0x437b6670` (área `CAMERA_MAIN` 0x437b6xxx) llama al thunk `0x43aef72e` →
  `ReplyForTouchShutter`, que toma el callback de la ranura global y lo invoca.

**Conclusión**: `[CAMERA_MAIN_FC]` **no participa en la cadena de disparo táctil documentada**
(`0x3011`): su API de respuesta táctil existe y funciona, pero por un **camino distinto**
(capa de captura / `wrapper/Face.cpp`), no por `RelMgr → 0x3011 → CamUser → CaptureStart`.
Que ese camino alternativo fuera el previsto es NO VERIFICADO.


## 8. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

| magnitud | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---:|---:|---:|
| apariciones del token `[CAMERA_MAIN_FC]` | **9** | 0 | 0 |
| cadenas completas iguales | 9 | **0/9** | **0/9** |
| núcleos de texto (sin prefijo) presentes | 9 | **0/9** | **0/9** |
| fragmentos de código del módulo (8 de 48–64 B) | 8 | **0/8** | **0/8** |
| apariciones de `TouchShutter` | **3** (las 3 trazas #7–#9) | 0 | 0 |
| cadenas con prefijo `[CAMERA_MAIN*]` | 1806 | 0 | 0 |
| `Camera::FC::` (namespace de la biblioteca) | 45 | 45 | 45 |
| `FC/` (nombres de fichero de la biblioteca) | 101 | 101 | 101 |

**Lectura**: el material es **propio de la A6000 fw3.21**, en línea con la salvedad de S130 §4
(version y modelo mezclados: no hay una fw anterior de la A6000 en el repositorio). La
**biblioteca `Camera::FC` sí es preexistente e idéntica en los tres firmwares**: lo nuevo en la
fw3.21 es la **capa `[CAMERA_MAIN_FC]`** (y, dentro de ella, la API de respuesta al disparo
táctil, que no existe en ninguna otra cámara del repositorio).

## 9. NO VERIFICADO / abierto

1. **Fichero fuente del módulo `[CAMERA_MAIN_FC]`**: ninguna traza cita un `.cpp`.
2. Si `0x437b7778` (traza `osal_free_timer`) se invoca desde **otro binario** del paquete de
   firmware: no es descartable con los bytes de esta imagen (es la única función del módulo
   sin referencia entrante).
3. Significado exacto del flag `lc` (`[ctx+0xdf]`) y su relación con `[CAMERA_MAIN_LC]` (S127).
4. Destinatario de los mensajes OSAL del módulo (servicio de temporizadores y de `BatteryInfo`).
5. Semántica de `face_on` (`[ctx+0x49c]`) y `obj_on` (`[ctx+0x49e]`).
6. Si el camino de disparo táctil del módulo FC (vía `wrapper/Face.cpp`) es el previsto o
   deveria enlazar con la cadena `0x3011`.
7. Las 99 correspondencias fichero↔función de `FC/**/*.cpp` (ya abiertas en S111).


## 10. Revisión del agente principal

_(vacío — pendiente de revisión)_

## 11. Reproducción

```bash
.venv/bin/python analysis/s138_camera_main_fc/scan_fc_strings.py      # las 9 cadenas en los 3 firmwares
.venv/bin/python analysis/s138_camera_main_fc/scan_fc_refs.py         # sitios PIC (mapa global estricto)
.venv/bin/python analysis/s138_camera_main_fc/verify_sites.py         # 13/13 sitios recalculados a mano
.venv/bin/python analysis/s138_camera_main_fc/scan_refs_all.py 0x437b7200 0x437b74a4 0x437b7598 \
    0x437b7778 0x437b7844 0x437b7d6c 0x437b7ea0 0x437b81f0 0x437b7c8c
.venv/bin/python analysis/s138_camera_main_fc/scan_branches.py 0x437b7200 0x437b74a4 0x437b7598 \
    0x437b7778 0x437b7844 0x437b7d6c 0x437b7ea0 0x437b7fe4 0x437b81f0 0x437b7158 \
    0x43aef72e 0x43aef732 0x43aef736
.venv/bin/python analysis/s138_camera_main_fc/scan_func_strings.py 0x439d9500 0x120
.venv/bin/python analysis/s138_camera_main_fc/scan_diff.py            # diferencial
.venv/bin/python analysis/s138_camera_main_fc/scan_code_diff.py       # 8 fragmentos de código
.venv/bin/python analysis/s138_camera_main_fc/scan_pic_pointers.py 0x437b7598 0x437b7778 0x437b7ea0 0x437b81f0
.venv/bin/python analysis/s138_camera_main_fc/scan_tables.py 0x437b7598 0x437b7778 0x437b7ea0 0x437b81f0
.venv/bin/python analysis/s138_camera_main_fc/build_json.py           # camera_main_fc.json
```

Tests: `tests/test_s138_camera_main_fc.py`.

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (53 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 9 apariciones de `[CAMERA_MAIN_FC]` en la A6000 fw3.21 entre
   `0x43ca6944` y `0x43ca6aec`; **0** en la A7S fw3.20 y el A6300 fw2.01 → confirmado con
   `bytes.count()` en los tres blobs.
2. **La sigla `FC` tiene base textual** (no inventada): es el *namespace* C++ `Camera::FC`
   (**45** apariciones de `Camera::FC::` y **101** de `FC/` en **los tres** firmwares) con el árbol
   `FC/**/*.cpp` (99 ficheros) → la biblioteca es común; lo propio de la A6000 es el *logging* del
   *glue* `CAMERA_MAIN` → `Camera::FC`.
3. **Negativo bien acotado y útil**: el módulo **no participa** en la cadena de disparo táctil
   documentada (`0x4379d838`, `0x4379e6a8`, `0x4379eba0`→`0x3011`, `0x43809ed8`, `0x437df640`,
   `0x437df338`, `0x437eabfc`, `0x437e4de4`): ninguna de esas funciones llama a la zona del módulo
   ni a `Camera::FC`. El módulo sí tiene **su propia** API de respuesta al disparo táctil
   (`ReplyForTouchShutter` / `SetRequestReplyForTouchShutter`), cableada por
   `wrapper/Face.cpp` → **camino distinto**, lo que evita un falso positivo de correlación.
4. **13 sitios PIC** en 7 funciones, recalculados a mano por el subagente (`verify_sites.py`,
   13/13) → coherente con la regla estricta canónica.

### Detalle final del subagente (22-10-2026, incorporado en la revisión)

- **Funciones emisoras (7)**: `0x437b7200`, `0x437b74a4`, `0x437b7778`, `0x437b7844`, `0x437b7d6c`,
  `0x437b7ea0`, `0x437b81f0`; **`0x437b7778` es la única sin referencia entrante** (la baja del
  temporizador OSAL).
- **API exportada por thunks** `0x43aef72e` / `0x43aef72e+4` / `0x43aef72e+8` (`0x43aef72e/32/36`).
- **Disparo táctil**: su API de respuesta existe y está cableada por `wrapper/Face.cpp` →
  **`FC/Api/fc_api_tracking.cpp`** `0x43cefa43` → camino **distinto** del `0x3011`.
- **Sigla**: base textual = namespace `Camera::FC` (28 cadenas) y árbol `FC/**/*.cpp` (99 ficheros);
  no se desarrolla más.
- **NO VERIFICADO (final)**: fichero fuente del propio módulo; si `0x437b7778` se invoca desde otro
  binario; el flag `lc` (`[ctx+0xdf]`); el destinatario de los mensajes OSAL; la semántica de
  `face_on`/`obj_on`; si el camino táctil del FC *debía* enlazar con `0x3011`.
