# S118 — el módulo `[SFRA]` (ScalarInfra, lado cámara) del firmware A6000 fw3.21

**Hito:** S118 · **Módulo:** `[SFRA]` · **Firmware:** A6000 fw3.21 (`analysis/rea-independent/input/av-cam.bin`)
· **Convención:** `vaddr = 0x43541000 + file_offset`

Todo lo que sigue está comprobado contra los bytes del firmware; las direcciones
son `vaddr` y las citas son textuales. Lo que no se ha podido comprobar figura
en §10 (NO VERIFICADO).

---

## 1. Resumen

| magnitud | valor |
|---|---|
| trazas `[SFRA]` | **100** (100 textos distintos) |
| bloque de cadenas | `0x43ce5a16` – `0x43ce7723` |
| sitios de referencia (PIC, con flujo de datos) | **118** |
| funciones que las referencian | **47** |
| sub-bloques | **11** |
| comandos (`***…***`) | **17** (8 `[CMD]` + 9 `[CMP]`) |
| ficheros fuente embebidos del módulo | **11** |
| código del módulo | `0x439a1864` – `0x439a7bd4` (+ una copia aislada en `0x439ae838`) |
| diferencial A7S fw3.20 | **100/100 mensajes idénticos** (mismo conjunto, mismo orden) |

El módulo `[SFRA]` es la **fachada de cámara del framework `NS_SCALAR_INFRA`** (que
queda VERIFICADO por los nombres de clase de C++ de la zona `[SFR]`; el papel
concreto de "fachada de cámara" es inferencia del vocabulario de comandos): el
lado que recibe los mensajes del subsistema escalar, los despacha y devuelve las
completaciones. Su núcleo es `ScalarInfraAsyncMain` (`0x439a1864`), que contiene
el bucle de despacho de los 16 comandos con nombre.

---

## 2. Qué es `[SFRA]`

* Las 100 trazas empiezan por el prefijo literal `[SFRA]` y, en 79 de ellas, por
  un segundo nivel entre corchetes: `[SFRA][CMD]`, `[SFRA][CMP]`, `[SFRA][BUF]`,
  `[SFRA][RATECONTROL]`, `[SFRA][ERROR]`, `[SFRA][ERR]`, `[SFRA][RC]`,
  `[SFRA][NOTIFY]`, `[SFRA][WARNING]`, `[SFRA][SFR_ERR_NOTREADY]`.
* El nombre del módulo **no está expandido** por el firmware, pero el framework
  al que sirve sí lo está, en las cadenas de la zona `[SFR]`/`[SFRS]`
  (`0x43ce79ec`…`0x43ce90b7`), donde aparecen los nombres de clase de C++:

  * `virtual NS_SCALAR_INFRA::SFR_ERR NS_SCALAR_INFRA::SubsystemFactory::ExecCmd(const NS_SCALAR_INFRA::SFR_MSG_INFO*, OSAL_ID, OSAL_ID, __uint8_t)` — `0x43ce79ec`
  * `virtual NS_SCALAR_INFRA::SFR_ERR NS_SCALAR_INFRA::WaitQueue::Enqueue(const NS_SCALAR_INFRA::CmdBaseData*)` — `0x43ce7bad`
  * `virtual NS_SCALAR_INFRA::SFR_ERR NS_SCALAR_INFRA::SystemCmdIf::ExecCmd(NS_SCALAR_INFRA::MsgAccessorIf*, NS_SCALAR_INFRA::SubsystemAccessorIf*)` — `0x43ce8035`

  → **`SFR` = `SCALAR_INFRA` está VERIFICADO por el propio firmware** (nombres de
  clase), no es una hipótesis. `SFRA` es el *adaptador de cámara* de ese framework
  (el "A" final no aparece expandido en ninguna parte: NO VERIFICADO).
* La función que despacha los comandos usa el nombre de fichero embebido
  `ScalarInfraAsyncMain.cpp` (`0x43ce59fd`, referenciado en `0x439a18d6`), lo que
  identifica sin ambigüedad `0x439a1864` como `ScalarInfraAsyncMain`.

---

## 3. El protocolo: los dos niveles y el catálogo de comandos

### 3.1 Los dos niveles

Cada comando aparece con dos marcas:

* `[SFRA][CMD] ***NOMBRE***` — el **comando** (petición).
* `[SFRA][CMP] ***NOMBRE_CMP***` — su **finalización** (*completion*).

En el bucle de `ScalarInfraAsyncMain` (`0x439a1864`) el nombre `[CMD]` se imprime
cuando se recognise el mensaje entrante y el `[CMP]` correspondiente se imprime
después de ejecutar la acción. Ejemplo verificado byte a byte:

```
439a1a70  ldr r0, [pc, #0xf0]      ; 0x43ce5ac5  "[SFRA][CMD] ***SET_SA_NOTIFY***"
439a1a72  add r0, pc
439a1a74  bl  #0x435ab880         ; printf
…
439a1b74  bl  #0x439a42a0         ; acción (envía la finalización)
439a1b78  ldr r0, [pc, #0x310]     ; 0x43ce5ae5  "[SFRA][CMP] ***SET_SA_NOTIFY_CMP***"
439a1b7a  add r0, pc
439a1b7c  bl  #0x435ab880         ; printf
```

### 3.2 Catálogo completo de los 17 comandos

La columna *id* está **decodificada de los bytes**: cada comando está protegido
por una función-predicado de la familia `0x43b63xxx` que compara el **tipo de
mensaje** (16 bits en el offset `+0x02` del mensaje) y, para la clase `0x0100`,
el **id de sub-comando** (8 bits en el offset `+0x0f`).

| nivel | nombre | vaddr de la traza | tipo de mensaje | id de sub-comando | predicado | línea en `ScalarInfraAsyncMain.cpp` |
|---|---|---|---|---|---|---|
| CMD | `GET_INFO` | `0x43ce5a16` | `0x0100` | `0x10` | `0x43b632ca` | 116 |
| CMP | `GET_INFO_CMP` | `0x43ce5a31` | `0x9010` | — | `0x43b632b6` | 124 |
| CMD | `SET_PATH(CLOSE)` | `0x43ce5a50` | `0x8110` | — | `0x43b63226` | 133 |
| CMD | `SET_PATH(OPEN)` | `0x43ce5a72` | `0x8120` | — | `0x43b63216` | 139 |
| CMP | `SET_PATH_CMP(OPEN)` | `0x43ce5aa0` | — | — | — | 64 |
| CMD | `SET_SA_NOTIFY` | `0x43ce5ac5` | `0x0100` | `0x32` | `0x43b63334` | — |
| CMP | `SET_SA_NOTIFY_CMP` | `0x43ce5ae5` | — | — | — | 84 |
| CMD | `GET_SA_RESULT` | `0x43ce5b09` | `0x0100` | `0x30` | `0x43b6331a` | — |
| CMP | `GET_SA_RESULT_CMP` | `0x43ce5b29` | — | — | — | — |
| CMD | `SET_JPEG_PARAM` | `0x43ce5b4d` | `0x0100` | `0x22` | `0x43b63300` | — |
| CMP | `SET_JPEG_PARAM_CMP` | `0x43ce5b6e` | — | — | — | — |
| CMD | `GET_JPEG` | `0x43ce5b93` | `0x0100` | `0x20` | `0x43b632e4` | — |
| CMP | `GET_JPEG_CMP` | `0x43ce5bae` | — | — | — | — |
| CMD | `LiveView SET_JPEG` | `0x43ce5bcd` | `0x0100` | `0x42` | `0x43b63384` | 250 |
| CMP | `LiveView SET_JPEG_CMP` | `0x43ce5bf1` | — | — | — | — |
| CMP | `SET_PATH_CMP(CLOSE)` | `0x43ce5caa` | — | — | — | — |
| CMP | `SET_PATH_CMP(SA CLOSE)` | `0x43ce6f65` | — | — | — | — |

Decodificación de los predicados (ejemplos literales de las instrucciones):

```
43b632ca  ldrh  r3, [r0, #2]      ; tipo de mensaje
43b632cc  cmp.w r3, #0x100        ; clase 0x0100
43b632d2  ldrb  r0, [r0, #0xf]    ; sub-comando
43b632d4  sub.w r1, r0, #0x10     ; GET_INFO  -> 0x10
43b632de  bx    lr

43b632b6  ldrh  r0, [r0, #2]
43b632b8  movw  r3, #0x9010       ; GET_INFO_CMP -> tipo 0x9010
43b632bc  rsb   ip, r3, r0
43b632c8  bx    lr

43b63216  ldrh  r0, [r0, #2]
43b63218  movw  r3, #0x8120       ; SET_PATH(OPEN)
43b63226  ldrh  r0, [r0, #2]
43b63228  movw  r3, #0x8110       ; SET_PATH(CLOSE)
```

**Familia de ids de sub-comando de la clase `0x0100`** (predicados contiguos en
`0x43b632ca`–`0x43b6339c`): `0x10` GET_INFO, `0x20` GET_JPEG, `0x22`
SET_JPEG_PARAM, `0x30` GET_SA_RESULT, `0x32` SET_SA_NOTIFY, `0x34`
(predicado `0x43b6336a`, sin traza con ese nombre), `0x40` (predicado
`0x43b6334e`, sin traza con ese nombre), `0x42` LiveView SET_JPEG.

**Sub-ids de `SET_PATH(OPEN)`** (tipo `0x8120`, campo 16 bits en `+0x0c`):
`0x01` (predicado `0x43b63244`), `0x20` (`0x43b6327e`), `0x30`/`0x31`
(`0x43b63260`), `0x42` (`0x43b6329a`).

### 3.3 El despachador de finalizaciones

`0x439a1640` es el manejador de las finalizaciones: conmuta sobre el **byte
`+0x02` del mensaje** (valores 1..5) mediante una tabla `TBB` de 5 bytes en
`0x439a1654` (`03 1a 29 43 91`), con destinos `0x439a165a`, `0x439a1688`,
`0x439a16a6`, `0x439a16da` y `0x439a1776` (rama de error). La instrucción de
salto es `tbb [pc, r3]` en `0x439a1650` (`e8df f003`), precedida de
`ldrb r3,[r0,#2] / subs r3,#1 / cmp r3,#4`.

---

## 4. Inventario por sub-bloque (las 100 trazas)

| sub-bloque | n | rango |
|---|---|---|
| `[RATECONTROL]` (18 de ellos `[RATECONTROL][OPTION]`) | 26 | `0x43ce5f4e`–`0x43ce682c` |
| sin etiqueta de 2.º nivel | 21 | `0x43ce5c19`–`0x43ce73f6` |
| `[ERROR]` | 14 | `0x43ce6302`–`0x43ce75d8` |
| `[BUF]` | 11 | `0x43ce5da2`–`0x43ce665d` |
| `[CMP]` | 9 | `0x43ce5a31`–`0x43ce6f65` |
| `[CMD]` | 8 | `0x43ce5a16`–`0x43ce5bcd` |
| `[ERR]` | 4 | `0x43ce6e7e`–`0x43ce6ef3` |
| `[RC]` | 4 | `0x43ce76b8`–`0x43ce7723` |
| `[NOTIFY]` | 1 | `0x43ce6c99` |
| `[SFR_ERR_NOTREADY]` | 1 | `0x43ce6e35` |
| `[WARNING]` | 1 | `0x43ce6f8e` |

**Vocabulario de respuestas** (lo que el módulo *contesta*, no los nombres de
comando):

* `[BUF]` — gestión del anillo de JPEG: `getReadyBuf`, `getWriteBuf`
  (`Alloc WRITE/EMPTY/READY`), `freeReadyBufAll`, `freeWriteBuf`
  (`FreeOnly`), `dumpBufState`, `FATAL ERROR fname=%s, line=%d`.
* `[RATECONTROL]` — control de calidad/tamaño del JPEG comprimido:
  `set compressRate=%d`, `compressRate=%d`,
  `size=%d, tsize=%d, minf=%2d, maxf=%2d, qscl=%d.%d`, y los desenlaces
  `SUCCEEDED (SIZE =%d, LIMIT=%d)`, `SKIP (…)`, `RETRY(%d) (…) LIMIT SIZE OVER`,
  `RETRY(%d) (…) WORK SIZE OVER`, `ERROR SKIP (…) UNEXPECTED ERROR(0x%08x)`.
* `[RATECONTROL][OPTION]` — volcado de 18 parámetros de la tabla de opciones
  (`keyCode`, `en_iqscaleInit`, `iqscaleMin/Max`, `targetSizeMin0/1/2Nume`,
  `targetSizeMax0/1/2Nume`, `iqscaleMin0/1/2Diff`, `iqscaleMax0/1/2Diff`,
  `retryCount`).
* `[ERROR]` / `[ERR]` / `[WARNING]` — `MEMORY SHORTAGE!!!`, `fcmdSetJpeg:handle NG`,
  `fcmdSetJpeg:Enqueue`, `fcmdSetJpeg:Old CMD Delete`,
  `replaceYcSdsYcData: saYcData|rcbuf|ycSds|ycData`,
  `DrvCallDmm::UtilityGetAddr(handle=0x%04x)`.
* `[RC]` — `rc result=0x%08x`, `rcrt result error:%x`, `FATAL ERROR!! %s(%d)`.
* `[NOTIFY]` — `check SA Notify(mask=0x%02x,intfct=0x%02x,mbx=0x%08x)`.
* sin etiqueta — la familia `stdYc2sfrYc_*` (`XXX`, `IMAGE_OUT_CREATE_TIM`,
  `IMAGE_OUT_TRANS_TIM`, `SUBJECT_DATA`, `FACE_DATA`, `FACE_INFO`,
  `REC_CAM_PARAM`, `CAMERA_INFO`, `MOVIE_QUALIY_INFO`, `FOCUS_INFO`),
  `init_SFR_YC_COMMON_HEADER( header=NULL )`, `getSeq() Invalid Seq!!!`,
  `Disp SA Ycin/Ycout`, `Free RC`, `Free SAYC`, `dump %s`,
  `ScalarInfraAsyncMain: Unknown Message(%d)!!!`.

---

## 5. Mapa función → traza

47 funciones; las más densas:

| función | sitios | trazas |
|---|---|---|
| `0x439a1864` (`ScalarInfraAsyncMain`) | 16 | los 16 nombres de comando + `Unknown Message(%d)!!!` |
| `0x439a24b8` | 18 | las 18 líneas de `[RATECONTROL][OPTION]` |
| `0x439a2bd8` | 5 | `[BUF] getWriteBuf` ×3 + `FATAL ERROR` + `ERROR(user should free jpeg handles.)` |
| `0x439a32b8` | 5 | desenlaces de `[RATECONTROL]` (`SUCCEEDED`/`SKIP`/`RETRY`×2/`ERROR SKIP`) |
| `0x439a4974` | 6 | `replaceYcSdsYcData` ×4 + `Disp SA Ycin/Ycout` |
| `0x439a7bd4` | 6 | `[RC] FATAL ERROR!! / ERROR!! / rcrt result error` |
| `0x439a4458` | 4 | `debugNotifyEnable`, `errNotifySaResult`, `YC OUT DISABLED` ×2 |
| `0x439a58e4`, `0x439a59d4`, `0x439a26ba`, `0x439a2cf4`, `0x439a2d60`, `0x439a3756`, `0x439a5638`, `0x439a56e4`, `0x439a4d0c`, `0x439a4ac0`, `0x439a3b50`, `0x439a235c`, `0x439a23d0`, `0x439a2440`, `0x439a3184`, `0x439a5794` | 2–3 cada una | — |
| 15 funciones con 2–3 trazas | 2–3 cada una | — |
| 25 funciones más | 1 cada una | una traza por función |

Y una copia aislada del mismo chequeo en `0x439ae838`
(`[SFRA][SFR_ERR_NOTREADY] updateSaResult: context.saInfo.handle == 0x%04x`),
fuera del bloque principal del módulo.

Mapa completo en `analysis/s118_sfra/func_map.json` (47 entradas, 118 pares).

---

## 6. Ficheros fuente que implementan el módulo

11 nombres de fichero embebidos, **contiguos** en el blob (`0x43ce59fd`–
`0x43ce76fb`), lo que delimita el módulo:

| vaddr | fichero |
|---|---|
| `0x43ce59fd` | `ScalarInfraAsyncMain.cpp` |
| `0x43ce5e45` | `SfrJpegBuffer.h` |
| `0x43ce6320` | `ScalarInfraSequenceJpeg.cpp` |
| `0x43ce6693` | `ScalarInfraSequenceJpegStage.cpp` |
| `0x43ce68e9` | `ScalarInfraSequenceLiveView.cpp` |
| `0x43ce6ad9` | `ScalarInfraSequenceLiveViewStage.cpp` |
| `0x43ce6c15` | `ScalarInfraSequenceSa.cpp` |
| `0x43ce6e16` | `ScalarInfraSequenceSaStage.cpp` |
| `0x43ce7126` | `ScalarInfraSequenceUtility.cpp` |
| `0x43ce73ec` | `SfrYc.cpp` |
| `0x43ce76fb` | `DrvCallRc.cpp` |

Inmediatamente **antes** del bloque (familia del *resource controller*):
`api_rc.cpp` `0x43ce15d5`, `RcDriver.cpp` `0x43ce1b21`, `RcFill.cpp` `0x43ce1d23`,
`RcRequest.cpp` `0x43ce1db5`, `RcResourceMgr.cpp` `0x43ce2309`, `RcCalc.cpp`
`0x43ce23d7`, `RcCopy.cpp` `0x43ce2903`, `RcResize*.cpp` `0x43ce216a`–`0x43ce2280`.
Inmediatamente **después**: `SystemCmdNotfound.h` `0x43ce7f74`, `SystemCmdIf.h`
`0x43ce8027`, `SystemCmdAsyncCmdSetPin.cpp` `0x43ce8d13`,
`SystemCmdAsyncGetPin.cpp` `0x43ce8d67` (el framework `[SFR]`/`[SFRS]`, S116).

---

## 7. Relación con los demás subsistemas

| subsistema | evidencia en las trazas `[SFRA]` |
|---|---|
| **Framework `NS_SCALAR_INFRA` (`[SFR]`/`[SFRS]`, S116)** | `SET_PATH(OPEN/CLOSE)`, `SET_PATH_CMP(OPEN/CLOSE/SA CLOSE)`, `GET_INFO`/`GET_INFO_CMP`; en la zona `[SFRS]` el mismo vocabulario aparece como `[SFRS][CMD] ***SET_PATH(0x%02x)***` `0x43ce9ab9` y `[SFRS][CMP] ***SET_PATH_CMP(0x%02x)***` `0x43ce9a92`, y `ScalarInfraPathCmdSetPath::Execute()` `0x43ce9af3`. |
| **Acelerador escalar / "SA"** | `SET_SA_NOTIFY`/`GET_SA_RESULT` (+`_CMP`), `[SFRA][NOTIFY] check SA Notify(mask=…,intfct=…,mbx=…)` `0x43ce6c99`, `[SFRA][SA COMMAND] YC OUT DISABLED` `0x43ce6dae`, `context.saInfo.handle` `0x43ce6e35`, `replaceYcSdsYcData: saYcData` `0x43ce6e7e`, `Disp SA Ycin/Ycout`, `Free SAYC`. |
| **Motor de imagen YC (`[CAMERA_MAIN_YC]`, S110)** | `SfrYc.cpp` `0x43ce73ec` y la familia `stdYc2sfrYc_*` (convierte YC estándar → YC de SFR), `init_SFR_YC_COMMON_HEADER` `0x43ce73f6`, `replaceYcSdsYcData: ycData|ycSds` `0x43ce6ecd`/`0x43ce6ef3`. |
| **Gestor de memoria dinámico (`[CAM_DMM]`, S113)** | `[SFRA][ERROR] DrvCallDmm::UtilityGetAddr(handle=0x%04x)` `0x43ce75d8` y `…(list->handle=0x%04x)` `0x43ce759a`; las direcciones de los buffers JPEG se piden al DMM. |
| **Resource controller (`[RC]`)** | `DrvCallRc.cpp` `0x43ce76fb`, `[SFRA][RC] rc result=0x%08x` `0x43ce76b8`, `[SFRA][RC] rcrt result error:%x` `0x43ce7723`, `Free RC` `0x43ce6f45`, y la familia `Rc*.cpp`/`api_rc.cpp` embebida justo antes del módulo. |
| **Codificador JPEG / anillo de buffers** | `SfrJpegBuffer.h` `0x43ce5e45`, `ScalarInfraSequenceJpeg.cpp` `0x43ce6320`, `ScalarInfraSequenceJpegStage.cpp` `0x43ce6693`, `fcmdSetJpeg:*` `0x43ce6909`–`0x43ce696f`, y el bloque `[BUF]` completo. |
| **LiveView / captura** | `ScalarInfraSequenceLiveView.cpp` `0x43ce68e9`, `ScalarInfraSequenceLiveViewStage.cpp` `0x43ce6ad9`, `LiveView SET_JPEG` `0x43ce5bcd`, `ScalarInfraSequenceLiveViewStageAutoexec_jpeg*` `0x43ce6a85`/`0x43ce6b0c`. |
| **Gestor de captura / ruta (path)** | `SET_PATH(OPEN/CLOSE)` abre y cierra el *path* de datos hacia el escalar; `context.pathParam.payload.debugNotifyEnable=%d` `0x43ce6cf6` y `Notify disabled (IDLE path)` `0x43ce71cb`. |

Censo de llamadas desde las 47 funciones `[SFRA]`: **31 destinos distintos** y
**58 llamadas** en total: 35 caen dentro del propio módulo
(`0x439a0000`–`0x439affff`), 8 en la biblioteca C (`0x435ab880` = `printf`, 5
veces, más 3 auxiliares), 7 en la capa de mensajes OSAL/SFR (`0x43b6xxxx`:
`0x43b62a24`, `0x43b62e38`, `0x43b63214`, `0x43b63416`, `0x43b6348e`,
`0x43b63506`, `0x43b6358a`), 4 en `0x439cxxxx`, 3 en `0x43a3xxxx`/`0x43a4xxxx`
(OSAL) y 1 en `0x43b4xxxx`. **El módulo no llama directamente al imager ni al
codificador**: habla con ellos a través del framework `NS_SCALAR_INFRA` y de la
capa de mensajes.

---

## 8. Diferencial A6000 fw3.21 vs A7S fw3.20

**Corrección de una premisa del encargo:** la A7S fw3.20 **sí lleva el prefijo
`[SFRA]`**. No hay dos “niveles de etiquetado” entre cámaras: el módulo está
etiquetado igual en ambas.

| | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| ocurrencias de `[SFRA]` | 100 | 100 |
| mensajes idénticos texto a texto | **100 / 100** | **100 / 100** |
| `only_a6000` / `only_a7s` | — | **vacías** |
| orden de las cadenas | idéntico | idéntico |
| sitios de referencia PIC (flujo de datos) | 118 | 118 |
| funciones que las referencian | 47 | 47 |
| bloque de cadenas (offset de fichero) | `0x7a4a16`–`0x7a6723` | `0x7998c4`–`0x79b46b` |
| código (offset de fichero) | `0x46097a`–`0x46d858` | `0x44e1c6`–`0x4590a8` |

→ **El módulo `[SFRA]` es idéntico entre la A6000 fw3.21 y la A7S fw3.20**: los
100 mensajes, los 17 nombres de comando, los 118 sitios de referencia y las 47
funciones coinciden. Sólo cambia la posición dentro del blob.

**A6300 fw2.01** (referencia): 108 trazas `[SFRA]`. Las 100 de la A6000 están
**todas** presentes en la A6300, y la A6300 tiene **8 adicionales** con la
nomenclatura antigua (genérica) en lugar de la específica:

* `[SFRA][CMD] ***CMD_JPEG***`, `[SFRA][CMP] ***CMD_JPEG_CMP***`
* `[SFRA][CMD] ***CMD_LIVEVIEW***`, `[SFRA][CMP] ***CMD_LIVEVIEW_CMP***`
* `[SFRA][CMP] ***SET_PATH_CMP(JPEG CLOSE)***`
* `[SFRA] ScalarInfraSequenceLiveViewStageIdle::exec openReq` / `… closeReq`
* `[SFRA] getCloseSeq() Invalid Seq!!!`

Es decir, entre fw2.01 (A6300) y fw3.20/3.21 (A7S/A6000) los nombres de comando
se hicieron **específicos** (`CMD_JPEG` → `SET_JPEG_PARAM`/`GET_JPEG`,
`CMD_LIVEVIEW` → `LiveView SET_JPEG`) y se añadieron las trazas de la *stage*
`LiveViewStageIdle`. La A7S fw3.20 y la A6000 fw3.21 ya están alineadas.

---

## 9. Método (reproducible)

Todo con scripts de este directorio, sólo análisis de bytes (memoria < 3 GB; el
binario se lee entero en memoria, 11 MB):

```bash
# 1. referencias PIC con la regla canónica del repo (sólo la zona de código)
.venv/bin/python analysis/s106_imaging_cap/scan_pic_refs.py \
        0x43900000 0x439C0000 analysis/s118_sfra/pic_refs.json
# 2. re-resolución con kill analysis  -> pic_refs_dataflow.json + site_best.json
.venv/bin/python analysis/s118_sfra/pic_dataflow.py
# 3. decodificación de los predicados -> command_table.json
.venv/bin/python analysis/s118_sfra/command_table.py
# 4. diferencial con la A7S (independiente de la base) -> a7s_diff.json
.venv/bin/python analysis/s118_sfra/a7s_diff.py
# 5. cadenas, sub-bloques, mapa función→traza, catálogo -> sfra.json / summary.json
.venv/bin/python analysis/s118_sfra/extract_sfra.py
# 6. censo de llamadas -> call_census.json
.venv/bin/python analysis/s118_sfra/call_census.py
```

Auxiliares: `audit_pic.py` (auditoría de ambigüedades del PIC), `annotate.py`
(desensamblador anotado), `cmd_ids.py`, `protocol.py`.

**Advertencia metodológica (importante para los hitos siguientes).** La regla
canónica del repo (probar *todos* los `ldr` del registro en 4 KB y aceptar los
destinos en el inicio de una cadena) **produce falsos positivos** cuando el
registro se reutiliza: 186 pares frente a los 118 reales. Ejemplos comprobados:

* `0x4398f06a`: el `add r3,pc` resuelve a `0x43ce5356` (tabla de contadores), no a
  `0x43ce5a50` (`SET_PATH(CLOSE)`); `r3` había sido recargado en `0x4398efb0`.
* `0x439a175a`: el `add r3,pc` resuelve a `0x43d8605c` (variable global), no a
  `0x43ce5b93` (`GET_JPEG`).
* `0x439a17e8` / `0x439a1808`: están en una **tabla de punteros**, no en código;
  el "predicado" `push {r4,lr}` es un byte de datos.

Recomendación: aplicar *kill analysis* (o equivalente) en S110/S112/S113/S115 y
revisar sus recuentos de sitios.

---

## 10. NO VERIFICADO / abierto

* **Significado de las siglas.** El firmware **no expande** `SFRA`, `SA`, `RC`,
  `YC`, `SFR` como siglas dentro de las cadenas `[SFRA]`. Sólo `SFR` está
  verificado como `SCALAR_INFRA` gracias a los nombres de clase de C++ de la
  zona `[SFR]`. `SA` y `RC` se dejan tal cual.
* **Significado de los ids.** El **qué** significa cada id (0x10, 0x20, …,
  0x8110/0x8120, 0x9010) está **decodificado**, pero su **significado funcional**
  (por ejemplo, si `0x8110`/`0x8120` son "cerrar/abrir path" o "path 0x10/0x20")
  no está documentado por el firmware. La correlación nombre↔id es la que da la
  traza, y es circumstantial.
* **Correspondencia de los 5 casos de finalización** (`0x439a1640`, byte `+0x02`
  = 1..5) con los nombres `[CMP]`: los casos del `TBB` **no llevan el nombre**
  dentro del bloque; la correlación con `SET_PATH_CMP(OPEN)`,
  `SET_SA_NOTIFY_CMP`, `SET_JPEG_PARAM_CMP` y `GET_JPEG` se hizo por el mapa
  canónico (que da un artefacto del reuse de registro) y **no está confirmada**.
* **Los 5 ids de sub-comando sin nombre** (`0x34` en `0x43b6336a`, `0x40` en
  `0x43b6334e`, y la familia `0x8120` con sub-ids `0x01/0x20/0x30-0x31/0x42`):
  no hay traza `[SFRA]` con ese nombre; puede que sus trazas vivan en `[SFRS]`
  (S116).
* **Funciones mal delimitadas.** `0x439a17ca`/`0x439a17ea` son *thunks* dentro de
  una tabla de punteros; el bloque `0x439a1640`–`0x439a1860` mezcla código y
  datos. El recuento de 47 funciones depende de la heurística de prólogo
  (`push {..,lr}` … `pop {..,pc}`) y puede variar ±1–2.
* **Copias duplicadas.** `updateSaResult` aparece en `0x439a4914` y en
  `0x439ae838` (a 100 KB de distancia). No se ha determinado si es código
  duplicado por el compilador o dos instancias distintas.
* **Relación con el imager y con la captura.** No hay ninguna llamada directa
  desde `[SFRA]` al driver del imager (`[CAM_IMAGER]`, S115) ni al gestor de
  captura (`[IMAGING_CAP]`, S106): el enlace es **indirecto**, a través del
  framework `NS_SCALAR_INFRA` (`[SFR]`/`[SFRS]`).

---

## 11. Revisión del agente principal

*(vacío — pendiente de revisión)*

---

## Revisión del agente principal (21-10-2026)

**Corrección de la premisa del encargo (el subagente la detectó):** se le pidió medir el
diferencial asumiendo que la A7S **no** tenía el prefijo `[SFRA]`. **Falso**: la A7S fw3.20
tiene las **100** cadenas `[SFRA]`, **idénticas texto a texto y en el mismo orden** que la
A6000 (100 apariciones en ambos blobs) → el módulo es el mismo y solo cambia su posición
(cadenas `0x7a4a16` en la A6000 frente a `0x7998c4` en la A7S). El A6300 fw2.01 tiene **108**
trazas: las 100 de la A6000 más 8 con nomenclatura antigua (`CMD_JPEG`, `CMD_LIVEVIEW`,
`SET_PATH_CMP(JPEG CLOSE)`, `LiveViewStageIdle::exec openReq/closeReq`, …). Es un acierto del
subagente: verificó la premisa en vez de darla por buena.

**Hallazgo metodológico (el más importante de la ronda):** la regla PIC "ancha" (probar **todos**
los `ldr` del registro en 4 KB) produce **falsos positivos**: 186 pares donde la verificación
manual encuentra **118**. La causa es la **reutilización del registro**: entre el `ldr` y el
`add` puede reescribirse ese registro, y entonces el `add` no suma el valor que se cargó.

**Consecuencia asumida en el repo**: se ha añadido el escáner canónico
`analysis/s106_imaging_cap/scan_pic_refs_v2.py` con **kill analysis** (descartar el par si
alguien escribe el registro entre `ldr` y `add`) y una nota de metodología
(`analysis/s106_imaging_cap/pic_xref_methodology.md`) con la calibración de este caso; los
recuentos publicados de S106, S110, S112, S113 y S115 se han rectificado con ella.

**Verificado por el subagente y aceptado**: los 17 comandos con sus **ids decodificados de los
bytes** en los predicados (`0x0100`/`0x10` GET_INFO, `/0x20` GET_JPEG, `/0x22` SET_JPEG_PARAM,
`/0x30` GET_SA_RESULT, `/0x32` SET_SA_NOTIFY, `/0x42` LiveView SET_JPEG, `0x8110`
SET_PATH(CLOSE), `0x8120` SET_PATH(OPEN), `0x9010` GET_INFO_CMP), el despachador de
finalizaciones `0x439a1640` con `TBB` de 5 bytes en `0x439a1654`, el núcleo
`ScalarInfraAsyncMain` `0x439a1864` y la identification de `SFR` = `NS_SCALAR_INFRA` **por los
nombres de clase C++** (no por conjetura).
