# libObj.so — punto de AF (`PARAMID_AF_AREA_POINT_CTRL`) y cajas de ojos (`[ObjEffect] leftEye*`)

Análisis **estático** (cero escrituras en cámara, firmware o RAM). Convención de cada afirmación:
**VERIFICADO** (bytes/instrucciones citadas), **INFERENCIA** (deducción con evidencia parcial),
**NO VERIFICADO** (no demostrado; se indica qué faltaría).

## 0. Objetos y método

| Objeto | Ruta (recortada) | sha256 | Tamaño |
|---|---|---|---|
| libObj.so (motor `ux::` de la app, fw 3.21) | `.../nflasha15_unpacked_unpacked/lib/libObj.so` | `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a` | 17 436 172 B |
| libScalarDaemon.so | `.../nflasha15_unpacked_unpacked/lib/libScalarDaemon.so` | `ca28cbf4c5c6402160ad80f6ad9f5e99052f42c3fabc382c557fcded18addc29` | 1 883 224 B |
| sdmon.elf | `.../nflasha15_unpacked_unpacked/bin/sdmon.elf` | `6818058ff4e7380bc7865d8104a15fdb7b38218a1442ad2878d2b898acd48372` | 142 720 B |
| libcameraex_jni.so | `.../nflasha16_unpacked_unpacked/lib/libcameraex_jni.so` | `f860c8849db2cb1169e9b646069d293adddeb04ac7eba40892647e6da6be54a8` | — |
| sony.cameraex.odex (API Java `com.sony.scalar.*`) | `.../nflasha16_unpacked_unpacked/framework/sony.cameraex.odex` | `af3b450ce48bd052de16b6e2f1264f8b743faab683dbfa7b823407737a24448f` | — |
| SmartRemote.odex (app) | `.../nflasha16_unpacked_unpacked/app/SmartRemote.odex` | `bba6646e760aa79e94bb97e7a5a65cb80c63d449b0bc8bace806be7850c0f594` | — |

ELF32 ARM EABI5, `EXEC`, Thumb-2, “stripped” pero con `.dynsym` (3 620 símbolos). Secciones de
libObj.so: `.text` `0xe2b70`+`0xae6a1c`, `.rodata` `0xbc9598`+`0x2c8a1a`, `.data.rel.ro` `0xfd29d0`
(fichero = vaddr − 0x8000 a partir de ahí), `.data` `0x1035320`.

Herramientas propias (nuevas, `analysis/eyeaf/tools/`): `libobj_refs.py` (localiza los sitios que
materializan una dirección de `.rodata` con `movw/movt` o `ldr rX,[pc]`+`add rX,pc`), `libobj_fns.py`
(límites de función desde `.ARM.exidx`: 54 510 funciones), `libobj_dis.py` (desensamblado anotado),
`libobj_callers.py`, `dex_dump_class.py` (campos/métodos de una clase DEX). REA/Ghidra abrió el
binario una vez y quedó como respaldo (su decompilador no termina dentro del presupuesto en este
ELF de 17 MB; todo lo decisivo se verificó contra instrucciones).

---

## 1. `PARAMID_AF_AREA_POINT_CTRL` y la familia de área/punto de AF

### 1.1 Tablas de nombres ⇒ valores numéricos (definición de los ids)

libObj.so lleva tres arrays contiguos de `const char*` en `.data.rel.ro` que indexan por valor de enum:

| Tabla | Base | Entradas | Evidencia |
|---|---|---|---|
| `MSGID_*` | `0xfe35f0` | 725 | primera entrada `MSGID_EE_START_CMD` (`0xfe35f0 → 0xd305b8`) |
| `PARAMID_*` | `0xfe4144` | 1 350 | `PARAMID_FOCUS_AREA_MODE` en `0xfe44cc` |
| `VALUEID_*` | `0xfe565c` | 1 288 | `VALUEID_AF_AREA_POINT_CTRL_AUTO` en `0xfe67bc` |

**VERIFICADO** que el índice del array es el número de enum, por tres cruces independientes en
código (ver §1.3): `VALUEID_HOUSING_MODE_OFF/ON/WATER_TYPE1_ON` = `0x18c/0x18b/0x4bf` usados como
tales en `0x9a1084-0x9a10aa`; `VALUEID_EYE_START_AF_OFF/ON` = `0x14c/0x14d` en `0x9a13ac/0x9a13b4`;
`VALUEID_AF_AREA_POINT_CTRL_AUTO/LV1` = `0x458/0x459` en `0x99af5c/0x99af64`.

| Nombre | Valor | Entrada de tabla | Evidencia |
|---|---|---|---|
| `PARAMID_TOUCH_SPOT_X` | 0x51 | `0xfe4288` | volcado de tabla |
| `PARAMID_TOUCH_SPOT_Y` | 0x52 | `0xfe428c` | idem |
| `PARAMID_FOCUS_AREA_MODE` | **0x0e2** | `0xfe44cc` | idem |
| `PARAMID_FOCUS_AREA_LOCAL_NUM` | **0x0e3** | `0xfe44d0` | idem |
| `PARAMID_FOCUS_AREA_MODE_SET` | 0x0e4 | `0xfe44d4` | idem |
| `PARAMID_TOUCH_SPOT_X_SET` | **0x0e5** | `0xfe44d8` | idem |
| `PARAMID_TOUCH_SPOT_Y_SET` | **0x0e6** | `0xfe44dc` | idem |
| `PARAMID_FOCUS_AREA_LOCAL_NUM_SET` | 0x0e7 | `0xfe44e0` | idem |
| `PARAMID_FOCUS_AREA_MODE_ACT` | 0x0e8 | `0xfe44e4` | idem |
| `PARAMID_TOUCH_SPOT_X_ACT` / `_Y_ACT` | 0x0e9 / 0x0ea | `0xfe44e8` / `0xfe44ec` | idem |
| `PARAMID_FOCUS_AREA_LOCAL_NUM_ACT` | 0x0eb | `0xfe44f0` | idem |
| `PARAMID_EYE_START_AF` | **0x0f4** | `0xfe4514` | idem |
| `PARAMID_EYE_START_AF_SET` / `_ACT` | 0x0f5 / 0x0f6 | `0xfe4518` / `0xfe451c` | idem |
| `PARAMID_FOCUS_AREA_LOCAL_SEMIWIDE` (+`_SET`/`_ACT`) | 0x24a / 0x24b / 0x24c | `0xfe4a6c`… | idem |
| `PARAMID_LENS_AF_AREA_CENTER_ONLY` | 0x271 | `0xfe4b08` | idem |
| `PARAMID_FOCUS_AREA_ALT` (+`_SET`/`_ACT`) | 0x2a3 / 0x2a4 / 0x2a5 | `0xfe4bd0`… | idem |
| `PARAMID_CAM_EXPAND_FOCUS_AREA_CENTER_X` | **0x2a7** | `0xfe4be0` | idem |
| `PARAMID_CAM_EXPAND_FOCUS_AREA_CENTER_Y` | **0x2a8** | `0xfe4be4` | idem |
| `PARAMID_CAM_EXPAND_FOCUS_AREA_ASPECT` | 0x2a9 | `0xfe4be8` | idem |
| `PARAMID_CAM_EXPAND_FOCUS_AREA_CENTER_X_REQ` / `_Y_REQ` | 0x333 / 0x334 | — | idem |
| `PARAMID_FOCUS_AREA_SEMIMULTI_NUM` (+`_SET`/`_ACT`) | 0x338…0x33a | — | idem |
| `PARAMID_FOCUS_AREA_SEMIWIDE_NUM` (+`_SET`/`_ACT`) | 0x48c / 0x48d / 0x48e | `0xfe5374`… | idem |
| **`PARAMID_AF_AREA_POINT_CTRL`** | **0x48f** | `0xfe5380` | idem |
| `PARAMID_AF_AREA_POINT_CTRL_SET` | 0x490 | `0xfe5384` | idem |
| `PARAMID_AF_AREA_POINT_CTRL_ACT` | 0x491 | `0xfe5388` | idem |
| **`PARAMID_AF_AREA_POINT_STATUS`** | **0x492** | `0xfe538c` | idem |

No existe un `PARAMID_FOCUS_AREA` “pelado”: la familia es `_MODE`, `_LOCAL_NUM`, `_LOCAL_SEMIWIDE`,
`_SEMIWIDE_NUM`, `_SEMIMULTI_NUM`, `_ALT` (**VERIFICADO**, barrido de las 1 350 entradas).

### 1.2 Qué transporta `PARAMID_AF_AREA_POINT_CTRL`: un **enum de control**, no coordenadas

`VALUEID_AF_AREA_POINT_CTRL_AUTO` = **0x458 (1112)**, `VALUEID_AF_AREA_POINT_CTRL_LV1` = **0x459 (1113)**
(tabla VALUEID, `0xfe67bc`/`0xfe67c0`). En el conversor `0x99af0c` (**VERIFICADO**):

```
0099af58  blx  #0xde360                 ; traduce el valor de entrada a VALUEID
0099af5c  cmp.w r0, #0x458              ; VALUEID_AF_AREA_POINT_CTRL_AUTO
0099af62  beq  0x99af6e                 ;   -> [r5,#8] = 0
0099af64  movw  r3, #0x459              ; VALUEID_AF_AREA_POINT_CTRL_LV1
0099af6a  bne  0x99af7a                 ;   otro valor -> error "UNKNOWN"
0099af74  strb  r3, [r5,#8]             ;   -> [r5,#8] = 1
```

Es decir: el parámetro lleva **{AUTO=0, LV1=1}** (2 estados; `VALUEID_AF_AREA_POINT_STATUS_LEVEL_0/_1`
= `0x45a`/`0x45b` son el estado correspondiente, ver §1.4). No hay punto x/y en este parámetro.

### 1.3 Quién lo escribe y quién lo consume (cadena app → BIONZ)

Convención del *envelope* `CAMUSER → Liro` que usan **todos** los conversores `…ForLiro`
(**VERIFICADO** en `0x99af0c`, `0x9b13f0`, `0x9a135c`, `0x9b8ac4`):

| Offset del buffer de salida | Contenido | Evidencia |
|---|---|---|
| `+0x00` | `5` (tipo/categoría de mensaje) | `movs r3,#5; strb r3,[r5]` |
| `+0x02`,`+0x03` | sub-ids de campo (`0x5a`,`0x40` / `0x64`,`0x40`) | `adds r3,#0x55; subs r3,#0x1a` |
| `+0x04` (u32) | id de mensaje `0x75xx` (eco del MsgID) | 4 `strb` con `lsr #8/#16/#24` |
| `+0x08` | **valor** (u8 para enums, u16 LE para coordenadas) | `strb` (o `strb`+`strb` alto) |

Quién escribe cada parámetro (**VERIFICADO**, caller ⇒ conversor ⇒ valor):

- **`PARAMID_AF_AREA_POINT_CTRL`** ← `CamMsgConv::SetAfAreaPointCtrlForLiro` **`0x99af0c`**
  (`"[CAMUSER]: CamMsgConv) ##### ERROR!!!  SetAfAreaPointCtrlForLiro NON SUPPORTED MsgID[0x%04x]#####"`
  en `0xe071ce`, ref. `0x99af40`; `"… PARAMID_AF_AREA_POINT_CTRL UNKNOWN[0x%04x]"` en `0xe07230`,
  ref. `0x99af84`). Acepta MsgID `0x7692` y `0x75e6`; si el MsgID no es válido o el parámetro es
  `NULL` (`"… PARAMID_AF_AREA_POINT_CTRL is NULL"`, `0xe07290`) aborta.
- Consumidor final: el **mensaje Liro** (capa CAMUSER hacia BIONZ). El buffer `r5` lo construye el
  llamador (secuencia CamUser) y el valor queda en `+0x08`; no hay relectura del `PARAMID` en esta ruta.
  **INFERENCIA fuerte** (el nombre `…ForLiro` + el envelope común), **NO VERIFICADO** el punto exacto
  de entrega al SoC (está en la parte `CamUser`/Infra, fuera de libObj).
- `PARAMID_AF_AREA_POINT_STATUS` es la dirección **inversa**: el *notify* del Liro lo consume
  `CamMsgConv` **`0x9a4e84`** (**VERIFICADO**): comprueba `pMsg[0]==6`, `pMsg[2..3]==0x206f`, y traduce
  `pMsg[8]` (`uc_AfAreaPointStatus`): `0 → VALUEID 0x45a` (`LEVEL_0`), `1 → 0x45b` (`LEVEL_1`), y
  llama a `0xe01a8(obj, 0x9992, &valor)` (**VERIFICADO** la llamada y los argumentos;
  **INFERENCIA** que publica el NID `0x9992` hacia la capa superior). Otro si no: `"… NID_AF_AREA_POINT_STATUS(uc_AfAreaPointStatus) UNKNOWN[0x%04x]"` (`0xe110b8`) o
  `"Receive Msg : [TYPE_PARAM_NOTIFY(NG), NID_AF_AREA_POINT_STATUS]"` (`0xe1112c`).
- **Coordenadas del punto de AF** (lo que de verdad “mueve el punto”): no viajan en
  `AF_AREA_POINT_CTRL` sino en `PARAMID_TOUCH_SPOT_X_SET/Y_SET` (0x0e5/0x0e6) +
  `PARAMID_TOUCH_SPOT_X/Y` (0x51/0x52):
  - `CamMsgConv::SetTouchSpotMeterForLiro` **`0x9b13f0`** (acepta MsgID `0x7528`, `0x7526`, `0x75e6`;
    cadena `0xe1667b`, ref. `0x9b1430`) y `CamMsgConv::SetTouchSpotFocusForLiro` **`0x9b14bc`**
    (MsgID `0x7528`, `0x7524`, `0x75e6`; cadena `0xe166dc`, ref. `0x9b14fc`) escriben **dos u16**:
    `[+8..9]` = campo `NID 0x9551`, `[+0xa..0xb]` = campo `NID 0x9552`
    (**VERIFICADO** en `0x9b151a-0x9b1524`: `blx 0xdc92c` → `uxth` → `strb [r5,#8]`/`[r5,#9]`;
    en `0x9b146c-0x9b1478` el mismo patrón para `[r5,#0xa]`/`[r5,#0xb]`). Si el valor no está, escribe 0.
  - Emisor lado app/UI: `pvt_ChangePosition` **`0x4bba48`** (lee dos enteros de un `ParamList` id `0x10e`
    vía `0xfe9ae`/`0xfe9b6`, valida y envía `ChPosIn` `ObjMsg(0x3400, 0x2033)`).
  - Relay de cámara: **`0x4c6008`** = `"Issued ObjCamera::MSGID_TOUCH_SPOT_METER_FOCUS_CMD (relay, x, y)"`
    (`0xcf129a`, ref. `0x4c6160`); vuelve a emitir `ObjMsg(0x3100, 0x7528)`.
  - Rango/unidades: en esta capa son **enteros de 16 bits** sin normalización visible
    (`uxth` + almacenamiento directo). El escalado a “tanto por ciento” ocurre antes, en la API remota
    (`setTouchAFPosition`, 0..100 → `(u16)(x*100)`), según `analysis/eyeaf/orb_touchaf.md`; el paso de
    esa escala a la escala interna de la cámara es **NO VERIFICADO**.

### 1.4 `PARAMID_FOCUS_AREA_MODE` / `_LOCAL_NUM` y `CAM_EXPAND_FOCUS_AREA_CENTER_X/Y`

- Conversor **`0x9b8ac4`** = `SetAFAreaForLiro` (`"… SetAFAreaForLiro NON SUPPORTED MsgID[0x%04x]"`,
  `0xe1c34b`, ref. `0x9b8b10`). Acepta MsgID `0x7566`, `0x7620`, `0x75e6` (**VERIFICADO**).
  Escribe en el envelope: `[+8]=3` (`0x9b8b68-0x9b8b6c`), luego **u16** en `+9/+0xa`, `+0xb/+0xc`,
  `+0xd/+0xe` tomados de los campos `NID 0x983b/0x95e9`, `0x983c/0x95ea`, `0x983d/0x95eb`, `0x974c`
  (`0x9b8b6e-0x9b8c0c`). Traduce además el valor de modo con la tabla de `VALUEID_*` (bloque
  `0x9b8b2e-0x9b8b5c` comparando con `0x322`/`0x323`).
- `PARAMID_FOCUS_AREA_MODE_SET`/`_ACT` y `LOCAL_NUM_SET`/`_ACT` **también** se procesan en
  **`0x4e8910`** (`"Invalid ObjMsg (PARAMID_FOCUS_AREA_MODE_SET)"` `0xcfc724`, ref. `0x4e89b4`;
  `"… (PARAMID_FOCUS_AREA_MODE_ACT)"` `0xcfc8a3`, ref. `0x4e8be8`) — es el aplicador de parámetros
  hacia el objeto cámara (**VERIFICADO** las cadenas y sus sitios; **NO VERIFICADO** el detalle del
  `switch` interno).
- `PARAMID_CAM_EXPAND_FOCUS_AREA_CENTER_X/Y/ASPECT`: emisor de petición **`0x4d1c08`**
  (`"PARAMID_CAM_EXPAND_FOCUS_AREA_CENTER_X_REQ:%d"`, `0xcf3198`, refs `0x4d1d10` y `0x4d1d5c`) y
  conversor **`0x9b11f8`** (`SetCamExpandFocusModeForLiro`, `"… NON SUPPORTED MsgID[0x%04x]"`, `0xe16427`,
  ref. `0x9b1230`). Valores: ver el par `… is NULL`/`UNKNOWN` de `0xe1654b`/`0xe165af`.
  Son **centro en coordenadas de recorte** (x, y) + aspecto; unidades exactas **NO VERIFICADO**.

---

## 2. Cajas de ojos `[ObjEffect] leftEyeLeft/Top/Width/Height` (+ rightEye…)

### 2.1 Función que las imprime y estructura de origen

**`0x20c08c`** es el volcado de parámetros de `ExecCmdSdfBeautyEffect::ExecuteCommand()`
(cadena `": [ObjEffect]ExecCmdSdfBeautyEffect::ExecuteCommand()"` en `0xc17c78`, usada por el propio
`0x20cac0`). Inicio y fin del bloque `"=============SDF BEAUTY_EFFECT PARAM…"` en `0x20c0c0` /
`0x20c950`, cierre `"… PARAM=======end======"` en `0x20c968`. **VERIFICADO**: para cada línea hay
`ldr r3,[pc,#d]` + `add r3,pc` que materializa la cadena, seguida de una llamada a log
`blx 0xe290c` (logger global con prefijo `[%4d]:`), y el valor se carga con `ldrh`/`ldrsh`
desde el registro base `r4` (el argumento `r1` de la función):

| Offset del struct | Campo (cadena exacta) | Carga | Sitio de log |
|---|---|---|---|
| `+0x30` | `[ObjEffect] faceLeft` | `ldrh` | `0x20c686` |
| `+0x32` | `[ObjEffect] faceTop` | `ldrh` | `0x20c6ba` |
| `+0x34` | `[ObjEffect] faceWidth` | `ldrh` | `0x20c6ee` |
| `+0x36` | `[ObjEffect] faceHeight` | `ldrh` | `0x20c722` |
| `+0x38` | `[ObjEffect] faceAngle` | `ldrsh` (s16) | `0x20c758` |
| `+0x3a` | `[ObjEffect] faceYawAngle` | `ldrsh` (s16) | `0x20c78e` |
| **`+0x3c`** | **`leftEyeLeft`** | `ldrh` | `0x20c7c2` |
| **`+0x3e`** | **`leftEyeTop`** | `ldrh` | `0x20c7f6` |
| **`+0x40`** | **`leftEyeWidth`** | `ldrh` | `0x20c82c` |
| **`+0x42`** | **`leftEyeHeight`** | `ldrh` | `0x20c862` |
| **`+0x44`** | **`rightEyeLeft`** | `ldrh` | `0x20c898` |
| **`+0x46`** | **`rightEyeTop`** | `ldrh` | `0x20c8ce` |
| **`+0x48`** | **`rightEyeWidth`** | `ldrh` | `0x20c904` |
| **`+0x4a`** | **`rightEyeHeight`** | `ldrh` | `0x20c93a` |

Cadenas: `0xc17a7f` (`leftEyeLeft`…), `0xc17ab5`, `0xc17aeb`, `0xc17b21`, `0xc17b57`, `0xc17b8d`,
`0xc17bc3`, `0xc17bf9`; formato `"[%4d]: [ObjEffect] leftEyeLeft               [0x%04x]"`.
Cabecera del mismo struct: `+0x00 cateId`, `+0x02 msgId`, `+0x04 msgLength`, `+0x06 version`,
`+0x0c ackCateId`, `+0x0e ackMsgId`, `+0x10 cmpCateId`, `+0x12 cmpMsgId` (log `0x20c0da`…`0x20c280`).

Conclusión estructural (**VERIFICADO**): las 4+4 “cajas de ojos” son **u16 (no normalizadas en el
volcado)**, en el mismo bloque que el **rectángulo de cara** (`+0x30..+0x36`) y los ángulos
`faceAngle/faceYawAngle` — es decir, **resultado del detector de caras** empaquetado como parámetros
de *beauty effect*. Unidades: valores de 16 bits tal cual; la escala real (píxeles del YC/SDS, o
coordenadas normalizadas del bloque de detección) **NO VERIFICADO**.

### 2.2 De dónde llegan: `PARAM_ID_INFRA_STRUCT` (0xE001) ⇒ `SetRecAspect` ⇒ volcado

Llamador único de `0x20c08c`: **`0x20cc2e`**, dentro de **`0x20cac0`** = `ExecCmdSdfBeautyEffect::ExecuteCommand`
(**VERIFICADO** por barrido de `bl` directos en `0x15e000-0x215000`).
Secuencia relevante:

```
0020cac0  push… (this, pObjMsgInput=r5, pAvbbcCmn=r4)
0020cba0  mov r0, r4 ; movw r1, #0xe001 ; r2=&out ; bl 0x145ba0
          ; fallo -> "GET PARAM_ID_INFRA_STRUCT ERR [%x]" (0x20cbc2)
0020cbe2  ldr r0,[r7,#4] ; blx plt:MprIf::SetRecAspect(VAspectParam*, ulong)   ; 0xdb9ac
0020cbe8  r4 = ret ; escribe cabecera (+0,+2,+4=0x4c,+6,+8=7,+0xc,+0xe=0x8321,+0x12=0x8322)
0020cc2e  bl 0x20c08c                 ; volcado con el struct completo (incl. +0x30..+0x4a)
0020ccf4  blx plt:MWF::ObjIf::CreateObject(name, ObjMsg*, ErrCd*)  con r3=0x4c (tamaño del msg)
```

- El identificador del mensaje/estructura es **`PARAM_ID_INFRA_STRUCT` = `0xE001`** (literal
  `movw r1,#0xe001` en `0x20cba2`, mensaje de error en `0x20cbc2`). **VERIFICADO** el literal y el uso.
- El mismo objeto lleva además la vía `PARAMID_BEAUTY_EFFECT_LIST`
  (`"[ObjEffect]GET PARAMID_BEAUTY_EFFECT_LIST ERR [%x]"`, `0xbf5acd`), `PARAMID_BEAUTY_EXTRACT_FACE_ID`,
  `PARAMID_BEAUTY_EFFECT_LAYOUT_MODE`, `PARAMID_BEAUTY_LAYOUT_HANDLE_LIST` — **VERIFICADO** que esas
  cadenas existen en `.rodata`; **NO VERIFICADO** su número de PARAMID (no figuran en la tabla
  `PARAMID_*` de libObj, luego pertenecen a otro espacio de ids: `PARAM_ID_INFRA_*`).
- Conclusión: las cajas **no** llegan por ninguno de los `PARAMID_*` de la tabla de 1 350; llegan por el
  bloque de parámetros de *infra/AVBBC* que la propia cámara calcula y entrega al efecto de imagen
  (**INFERENCIA fuerte**, con los literales y el flujo anteriores **VERIFICADOS**).

---

## 3. ¿Puede una app Android leer esas cajas?

### 3.1 API Java disponible (dex de `sony.cameraex.odex`, 126 clases)

| Clase / miembro | Firma | Fuente |
|---|---|---|
| `com.sony.scalar.meta.FaceInfo` | campos: `int id`, `int score`, `android.graphics.Rect rect`, `android.graphics.Point leftEye`, `android.graphics.Point rightEye`, `android.graphics.Point mouth`, `android.graphics.Point mouthLeft`, `android.graphics.Point mouthRight`, `FaceAngle faceAngle`, `SmileStatus smile`, `EyeBlinkStatus leftEyeBlink`, `EyeBlinkStatus rightEyeBlink`, `GenderStatus gender`, `GenerationStatus generation` | volcado DEX de la clase (`class_data`) |
| `CameraEx$FaceDetectionListener` | `void onFaceDetected(FaceInfo[] faces, CameraEx camera)` | idem |
| `CameraEx$FocusAreaListener` | `void onChanged(CameraEx$FocusAreaInfos, CameraEx)` | idem |
| `CameraEx$FocusAreaInfos` | `String focusAreaMode`, `FocusAreaRectInfo[] rectInfos` | idem |
| `CameraEx$FocusAreaRectInfo` | `boolean enable`, `int index`, `android.graphics.Rect rect` | idem |
| `CameraEx$FocusPosition` | `int currentPosition`, `int maxPosition` | idem |

Campos que resuelve el JNI (`libcameraex_jni.so`, nombre de campo entrecomillado y símbolos
`com_sony_scalar`): `faceinfo`, `faceangle`, `smilestatus`, `eyeblinkstatus`, `genderstatus`,
`generationstatus`, `histogram`, `lensinfo`, `analizedata`, `reviewinfo`, `point`, `rect`,
`focusareainfos`, `focusarearectinfo`, `focusposition` (`0x1f6f8`–`0x1f894`, **VERIFICADO** por
`strings`), con conversores `com_sony_scalar::FaceInfo_CppToJAVA`,
`…FaceInfoArray_CppToJAVA`, `…FaceAngle_CppToJAVA`, `…EyeBlinkStatus_CppToJAVA`,
`…SmileStatus_CppToJAVA` (`.dynsym`, offsets `0x68e1`, `0x406f`, `0x662f`, `0x6893`, `0x6459`).
Clases que el JNI busca explícitamente: `com/sony/scalar/hardware/CameraEx`,
`CameraEx$AnalizedData`, `…$FocusAreaInfos`, `…$FocusAreaRectInfo`, `…$FocusPosition`,
`…$LensInfo`, `…$ReviewInfo`, etc.

### 3.2 Contraste con lo que imprime libObj

| Dato | En libObj (`0x20c08c`) | En la API Java | ¿App? |
|---|---|---|---|
| Rectángulo de **cara** (x,y,w,h) | `+0x30..+0x36` (u16×4) | `FaceInfo.rect` (`Rect`) | **sí** |
| **Ángulo** de cara / yaw | `+0x38`, `+0x3a` (s16) | `FaceInfo.faceAngle` (`FaceAngle`), y `faceangle` en el JNI | **sí** (ángulo; yaw: **NO VERIFICADO** que el objeto Java lo exponga) |
| **Ojos**: punto | — | `FaceInfo.leftEye` / `rightEye` (**`Point`**, x,y) | **sí** |
| **Ojos**: caja (left/top/**width**/**height**) | `+0x3c..+0x42`, `+0x44..+0x4a` | **no existe** en `FaceInfo` (sólo `Point`) | **NO** |
| Parpadeo / sonrisa | — | `EyeBlinkStatus`, `SmileStatus` | **sí** |
| Áreas de AF (rects con `index`/`enable`) | — (no es su cometido) | `FocusAreaInfos`/`FocusAreaRectInfo` | **sí** |
| `PARAMID_*` crudos (0x48f, 0x492, 0x2a7…) | sí (ids internos) | **no** hay API por paramid | **NO** |

**VERIFICADO**: `FaceInfo` **no** declara `leftEyeWidth/Height` ni equivalente; los ojos viajan como
`android.graphics.Point` (centro) y el rectángulo disponible es el de la **cara**. Por tanto una app
puede leer **posición** de ojos (y el rectángulo facial, y las **áreas de AF** como `Rect`), pero **no**
las cajas `leftEyeLeft/Top/Width/Height` que libObj registra en el volcado de beauty effect.
`INFERENCIA fuerte`: esas cajas son consumo interno del pipeline de imagen (SDF/BEAUTY_EFFECT) y se
pierden al convertir a `FaceInfo`.

### 3.3 ¿Y para *mover* el punto de AF desde una app?

- Las cajas/coordenadas internas (`PARAMID_TOUCH_SPOT_X_SET/Y_SET`, `PARAMID_AF_AREA_POINT_CTRL`)
  **no** tienen API Java por paramid: la única vía es un **mensaje** que acaba en el conversor
  `CamMsgConv` (`0x9b13f0` / `0x99af0c`) y de ahí al Liro (**VERIFICADO** el lado libObj).
- La vía remota existente es `setTouchAFPosition` (orb-server → `WebApiIntMsg` `0x192`/`0x8d`), que
  produce `ObjMsg(0x3100, 0x7528)` en `0x4c6008` y termina en `0x9b13f0` (**VERIFICADO** el tramo
  libObj; el tramo orb→cámara está en `analysis/eyeaf/orb_touchaf.md`).
- `PARAMID_AF_AREA_POINT_CTRL` **no** es un mecanismo para mover el punto: es un enum de 2 estados
  (§1.2). **INFERENCIA fuerte**: “AF area point control” = habilitar/controlar el punto de AF
  automático (AUTO/LV1), no su posición.
- `PARAMID_CAM_EXPAND_FOCUS_AREA_CENTER_X/Y` **sí** son coordenadas, pero de la **zona de ampliación
  de foco** (MF assist / *expand focus*), no del punto de AF (**INFERENCIA** por nombre, emisor
  `0x4d1c08` y conversor `0x9b11f8`; **NO VERIFICADO** el consumidor en el SoC).

---

## 4. `PARAMID_CAMSETTING_EYE_START_AF`: ¿escritor/consumidor o sólo espejo?

| Binario | Qué hay | Evidencia |
|---|---|---|
| `libObj.so` | **no** existe el nombre `PARAMID_CAMSETTING_*` (0 apariciones). Usa `PARAMID_EYE_START_AF` = **0x0f4** (+`_SET` 0xf5 / `_ACT` 0xf6) | tabla `PARAMID_*` `0xfe4514`; `strings` sin `CAMSETTING` |
| `libScalarDaemon.so` | tabla `{u32 id, const char* name}` en `.data.rel.ro` `0x1b9eb0` (2.ª copia en `0x1b1fxx`): **`PARAMID_CAMSETTING_EYE_START_AF` = `0x5007`** (entrada `0x1ba018`, cadena `0x14daff`) | volcado de la tabla completa `0x3001..0x5077` |
| `sdmon.elf` | misma pareja `{0x5007, "PARAMID_CAMSETTING_EYE_START_AF"}` en `.data.rel.ro` (fichero `0x1d1b8`, cadena vaddr `0x1e2cc`) | búsqueda de la pareja id/cadena |

Búsqueda de uso real (**VERIFICADO**: negativo acotado):
- en `libScalarDaemon.so` **no hay** ningún `movw rX,#0x5007` en `.text` y **no hay** ningún puntero a la
  tabla ni al nombre fuera de la propia tabla; `0x5007` como u16/u32 sólo aparece en las dos copias de
  la tabla (`.data.rel.ro` `0x1b2018`, `0x1c1fe8`).
- en `sdmon.elf` idéntico: la única aparición de `0x5007` es la entrada de tabla.
- ⇒ En fw 3.21 **nadie lee ni escribe** `PARAMID_CAMSETTING_EYE_START_AF` en esos dos binarios: es una
  entrada de **catálogo de nombres**, coherente con “sólo copia al espejo” de
  `docs/gui/g83-barrido-objetivos-restantes.md`. **VERIFICADO** para estos binarios;
  **NO VERIFICADO** que otro proceso (o el propio BIONZ) lo use (no hay más ficheros con ese literal:
  el grep de todo `fw321` sólo devuelve esos dos).

Cadena real de Eye-Start AF en libObj (**VERIFICADO**):

```
pvt_ActionSetEyeStartAf        0x4c3670   UI/app -> ObjMsg(0x3100, 0x756e)          [0x4c369a/0x4c369e]
  (error: "Err (pvt_SetParamEyeStartAf)")
CamMsgConv::SetEyeStartAFForLiro 0x9a135c  acepta MsgID 0x756e (y 0x75e6)
                                          VALUEID 0x14c (EYE_START_AF_OFF) -> [+8]=0
                                          VALUEID 0x14d (EYE_START_AF_ON)  -> [+8]=1
                                          otro -> "PARAMID_EYE_START_AF UNKNOWN[0x%04x]" (0x9a13d2)
ObjCamera::MSGID_SET_EYE_START_AF_CMD (índice MSGID 110 = 0x6e)
  "Failed ObjCamera::MSGID_SET_EYE_START_AF_CMD (err)"   0xcf0201  ref 0x4c3720
  "Issued ObjCamera::MSGID_SET_EYE_START_AF_CMD (relay)" 0xcf0234
```

Nota estructural (**VERIFICADO**): los MsgID que usan estas acciones son `0x7500 | MSGID_*`
(`0x7566` ↔ `MSGID_SET_AF_AREA_CMD`=102=0x66; `0x756e` ↔ `MSGID_SET_EYE_START_AF_CMD`=110=0x6e;
`0x7528` ↔ `MSGID_TOUCH_SPOT_METER_FOCUS_CMD`=40=0x28; `0x7524` ↔ `MSGID_TOUCH_SPOT_FOCUS_CMD`=36=0x24;
`0x7526` = 38, coherente con `MSGID_TOUCH_SPOT_METER_CMD`), y `0x75e6` aparece como comodín en todos
los conversores. **INFERENCIA fuerte** la regla `0x7500 | MSGID`; los cuatro pares citados son
**VERIFICADOS** uno a uno.

---

## 5. Tabla de funciones (libObj.so)

| Dirección | Tamaño (hasta siguiente en `.ARM.exidx`) | Qué hace | Evidencia |
|---|---|---|---|
| `0x20c08c` | — (bloque `0x20c08c`–`0x20c9xx`) | Volcado `"SDF BEAUTY_EFFECT PARAM"`: cara + ángulos + 4+4 cajas de ojos, desde struct base `r4` (`+0x30..+0x4a`) | sitios de log `0x20c0c0`…`0x20c968`; `ldrh/ldrsh [r4,#0x30..#0x4a]` |
| `0x20cac0` | — | `ExecCmdSdfBeautyEffect::ExecuteCommand`: obtiene `PARAM_ID_INFRA_STRUCT (0xE001)` (`bl 0x145ba0`), `MprIf::SetRecAspect`, rellena el msg de 0x4c B y llama al volcado | `0x20cba2`, `0x20cbe2`, `0x20cc2e`, `0x20ccf4` |
| `0x99af0c` | — | `CamMsgConv::SetAfAreaPointCtrlForLiro`: MsgID `0x7692`/`0x75e6`; `0x458→0`, `0x459→1` en `+8` | `0x99af1e-0x99af74`, cadenas `0xe071ce`, `0xe07230`, `0xe07290` |
| `0x9b13f0` | — | `CamMsgConv::SetTouchSpotMeterForLiro`: MsgID `0x7528`/`0x7526`/`0x75e6`; u16 x (NID `0x9551`) en `+8`, u16 y (NID `0x9552`) en `+0xa` | `0x9b146c-0x9b1478`; cadena `0xe1667b` |
| `0x9b14bc` | — | `CamMsgConv::SetTouchSpotFocusForLiro`: MsgID `0x7528`/`0x7524`/`0x75e6`; mismo par u16 x,y en `+8`/`+0xa` | `0x9b151a-0x9b1524`; cadena `0xe166dc` |
| `0x9b8ac4` | — | `SetAFAreaForLiro`: MsgID `0x7566`/`0x7620`/`0x75e6`; `+8=3`; u16 en `+9..+0xe` desde NID `0x983b..0x974c` | `0x9b8b10`, `0x9b8b68`, `0x9b8b6e-0x9b8c0c` |
| `0x9a135c` | — | `SetEyeStartAFForLiro`: MsgID `0x756e`/`0x75e6`; `0x14c→0`, `0x14d→1` en `+8` | `0x9a136e-0x9a13c8`, cadena `0xe0de3a` |
| `0x9a4e84` | — | Consumidor `NID_AF_AREA_POINT_STATUS`: `uc_AfAreaPointStatus 0/1 → VALUEID 0x45a/0x45b`, luego `0xe01a8(obj,0x9992,&v)` | `0x9a4e94-0x9a4ee0` |
| `0x4c3670` | — | `pvt_ActionSetEyeStartAf` (app→`ObjMsg(0x3100,0x756e)`) | `0x4c369a`, `0x4c369e` |
| `0x4c38b8` | — | `prv_ActionSetAfAreaMode` (app→`ObjMsg(0x3100,0x7566)`) + `err (pvt_SetParamAfAreaMode)` | `0x4c38e6`, `0x4c3922` |
| `0x4c6008` | — | `ObjCamera` relay de `MSGID_TOUCH_SPOT_METER_FOCUS_CMD (x,y)` → `ObjMsg(0x3100,0x7528)` | `0x4c6090`, cadenas `0xcf1261`, `0xcf129a` |
| `0x4bba48` | — | `pvt_ChangePosition`: valida y envía `ChPosIn` `ObjMsg(0x3400,0x2033)` | `0x4bba5c`, `0x4bba8c`, `0x4bbaa2` |
| `0x4e8910` | — | aplica `PARAMID_FOCUS_AREA_MODE_SET/_ACT`, `LOCAL_NUM_SET/_ACT`, `TOUCH_SPOT_X/Y_SET/_ACT` | cadenas `0xcfc724`…`0xcfc9f1` |
| `0x4d1c08` | — | petición `PARAMID_CAM_EXPAND_FOCUS_AREA_CENTER_X/Y_REQ` | cadena `0xcf3198`, refs `0x4d1d10`, `0x4d1d5c` |
| `0x9b11f8` | — | `SetCamExpandFocusModeForLiro` (centro + aspecto del *expand focus*) | cadena `0xe16427`, ref `0x9b1230` |

---

## 6. Límites (NO VERIFICADO)

1. Escala/units exacta de las cajas de ojos `+0x3c..+0x4a` (u16) y del centro `CAM_EXPAND_FOCUS_AREA`.
2. Punto exacto de entrega del envelope `+8` al SoC (capa `CamUser`/Infra, fuera de libObj); se verificó
   el productor y el formato, no el consumidor final BIONZ.
3. `PARAMID_BEAUTY_EFFECT_LIST` / `PARAMID_BEAUTY_EXTRACT_FACE_ID`: existen como cadenas de log, pero
   **no** en la tabla `PARAMID_*` de libObj ⇒ su id numérico no está establecido.
4. Que la app `SmartRemote` use realmente `CameraEx.FaceDetectionListener` (la cadena `faceinfo` aparece
   en su DEX, pero no se siguió el método que la consume).
5. Uso de `PARAMID_CAMSETTING_EYE_START_AF (0x5007)` por procesos distintos de `libScalarDaemon.so` y
   `sdmon.elf` (ningún otro fichero de fw 3.21 contiene ese literal).
