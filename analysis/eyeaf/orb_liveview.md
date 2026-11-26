# Live View y `getEvent` en el Camera Remote API de la A6000 (fw 3.21)

Análisis **estático** de `orb-server` (A6000 fw3.21) y de los artefactos de la misma partición que completan el flujo.
Sin ejecución, sin cámara, sin escrituras. Marcas: **VERIFICADO** (bytes/instrucción o literal citado),
**INFERENCIA** (deducción a partir de la evidencia, no demostrada), **NO_VERIFICADO** (no demostrable en estático).

---

## 0. Objeto, método y trazabilidad

| Elemento | Valor |
|---|---|
| Binario principal | `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/bin/orb-server` |
| SHA-256 | `2ef500ba5871b8017b94ef2af4788eb8c27e1614e6510db8f8b1839ab70ad4c6` |
| Formato | ELF32 ARM EABI5, `EXEC`, *stripped* de `.symtab` pero **con `.dynsym` completo (12 862 símbolos, 10 472 FUNC)**: los nombres C++ se conservan (`readelf -sW` + `c++filt`) |
| Rangos | `.text` VA `0x183e88`–`0x2e34b0`; `.rodata` VA `0x2e34b8`–`0x379e64`; `.data` VA `0x39184c`; `.bss` VA `0x3921d8` |
| Herramientas | REA/Ghidra (MCP `mcp_rea`, `batch_decompile` — usada para todas las funciones citadas) + desensamblador *capstone* Thumb-2 propio para resolver literales `movw/movt` y `ldr [pc]` |
| Artefactos auxiliares | `.../nflasha16_unpacked_unpacked/app/SmartRemote.{apk,odex}` (app **Smart Remote Control**, `com.sony.imaging.app.srctrl`), `lib/libIMDB.so`, `lib/libInfraWebApi.so`, `bin/WebApiLauncher.sh` |

Nota de direcciones: en este ELF, para `.text` y `.rodata` **VA = offset de fichero + 0x8000**; para `.data`, **VA = offset + 0x10000**.
Todas las direcciones de este documento son VA del binario mapeado (espacio de Ghidra/REA).

---

## 1. `startLiveview` / `startLiveviewWithSize`

### 1.1 Contrato en `orb-server`

| Hecho | Evidencia | Marca |
|---|---|---|
| Existe el servicio `libj::node::orb::server::service::Remote::v1_0::StartLiveview` | símbolo `_ZN4libj4node3orb6server7service6Remote4v1_013StartLiveview6invokeEv`, VA `0x21f4f1` | VERIFICADO |
| **`startLiveview` no tiene parámetros** | `StartLiveview::parameterTypes()` @ `0x21fe2c`: crea un `TypedJsArray<String>` **vacío** (sin `addTyped`) y lo devuelve | VERIFICADO |
| El resultado es **una única cadena** (la URL) | `StartLiveview::resultTypes()` @ `0x21feac`: array de 1 elemento, descriptor `"string"` (literal `string` en VA `0x3749a0`) | VERIFICADO |
| El handler **no compone la URL**: la copia tal cual del mensaje de la cámara | `StartLiveview_invoke_cmd()` @ `0x1a3f8c`: `String::create(&local_40, param_2 + 0x14, 0, 0xffffffff)` (payload del `WebApiIntMsg`), y log `"(%04d)[INF:invoke_cmd: %04d][startLiveview cmd] url=%s\n"` @ `0x2fb034` imprimiendo `param_2 + 0x14` | VERIFICADO |
| Petición interna al *backend* de cámara | `StartLiveview::invoke()` @ `0x21f4f0`: `WebApiAddonUipc::setEvtParamId(msg, 0x1b3, 0xae)` → `LibOrbRelayPool::AddToPool(client)` → `sendMsgToServer(msg)` | VERIFICADO |
| **`startLiveviewWithSize` NO existe en esta versión de `orb-server`** | `grep -c "WithSize" orb-server` → **0**; la lista de APIs compilada (VA `0x2e7eec`) enumera `camera/startLiveview` pero **no** `startLiveviewWithSize`; no hay clase `StartLiveviewWithSize` en `.dynsym` | VERIFICADO (en este binario) |
| `liveviewChunkTransfer` tampoco existe en `orb-server` | 0 ocurrencias de la cadena en todo el binario | VERIFICADO (en este binario) |

**Lista de APIs compilada** (literal único, separado por `:`), VA `0x2e7eec`:

```
guide/getServiceProtocols:camera/getApplicationInfo:camera/getAvailableApiList:camera/setShootMode:
camera/getShootMode:camera/getSupportedShootMode:camera/getAvailableShootMode:camera/setSelfTimer:
camera/getSelfTimer:camera/getSupportedSelfTimer:camera/getAvailableSelfTimer:camera/setPostviewImageSize:
camera/getPostviewImageSize:camera/getSupportedPostviewImageSize:camera/getAvailablePostviewImageSize:
camera/startRecMode:camera/stopRecMode:camera/startLiveview:camera/stopLiveview:camera/actTakePicture:
camera/awaitTakePicture:camera/startMovieRec:camera/stopMovieRec:camera/actZoom:camera/getEvent:
accessControl/actEnableMethods
```

**INFERENCIA:** esta cadena es el conjunto de métodos que este `orb-server` puede anunciar; el subconjunto realmente
activo depende del estado de la cámara (`getAvailableApiList`).

### 1.2 URL devuelta

`orb-server` se limita a retransmitir la URL; el literal está en la app de cámara que la produce
(`SmartRemote.odex`, fichero de la misma partición `nflasha16`, offsets de fichero):

| Offset | Cadena | Marca |
|---|---|---|
| `0x247b67` | `http://192.168.122.1:8080/liveview/liveviewstream` | VERIFICADO |
| `0x24bcfb` | `liveviewstream` | VERIFICADO |
| `0x1d47ce` / `0x1d47da` | `/liveview/` · `/liveview/*` (patrones de servlet) | VERIFICADO |
| `0x247b9a` / `0x247bbf` | `http://192.168.122.1:8080/postview/` · `http://192.168.122.1:8080/postview/memory` | VERIFICADO |
| `0x247beb` | `http://192.168.122.1:8080/sony` | VERIFICADO |
| `0x1e759a` | `Accepted HTTP GET for Liveview` (log del servlet de stream) | VERIFICADO |
| `0x1f52f0` / `0x1f52e1` | claves `LIVEVIEW_URL` · `LIVEVIEW_SIZE` | VERIFICADO |

Y, en el lado nativo, el documento raíz estático que sirve `orb-server` fija el puerto JSON en 10000
(`share/network/remotecontrol/index.html`): `'url': 'http://10.0.0.1:10000/sony/camera'` → **VERIFICADO**
(`.../share/network/remotecontrol/index.html`, líneas 13/18/23; también `/sony/guide` y `/sony/accessControl`).

- **VERIFICADO:** conviven dos listeners: **10000** = JSON-RPC del Camera Remote API (`orb-server`, `-p 10000`),
  **8080** = servidor de la app (`com.sony.imaging.app.srctrl`), que sirve `/liveview/liveviewstream`, `/postview/` y `/sony`.
- **INFERENCIA:** la IP `192.168.122.1` es la del AP Wi-Fi de la cámara en modo "Smart Remote Control";
  la IP real sólo puede confirmarse en cámara.

### 1.3 Formato de frame

| Hecho | Evidencia | Marca |
|---|---|---|
| Transferencia **HTTP chunked**, un **JPEG por chunk** | `SmartRemote.odex`: clase `Lcom/sony/mexi/orb/server/OrbChunkedOutputStream;`, `Lorg/apache/http/impl/io/ChunkedOutputStream;`, cabeceras `Transfer-Encoding`/`chunked` (offsets `0x2302c8`, `0x2391dc`), `Content-Type` (`0x1e47dc`) ↔ valor `image/jpeg`, logs `Start chunked transfer.` (`0x22e780`), `End chunked transfer.` (`0x1e8c80`), `Force disconnect chunked transfer.` (`0x1ec18b`), `JPEG data size (=` (`0x1f3573`) | VERIFICADO |
| **No es MJPEG multipart**: no existen `multipart`, `boundary` ni `x-mixed-replace` en `orb-server` ni en `SmartRemote.odex` | `grep -icE "multipart\|boundary\|mixed-replace"` → 0 en ambos | VERIFICADO |
| Cada parte **no lleva metadatos** (ni timestamp ni nº de frame) en el lado nativo: el servlet se llama `LiveviewChunkTransfer` y sólo escribe el JPEG con el *framing* chunked de HTTP | `Lcom/sony/imaging/app/srctrl/webapi/servlet/LiveviewChunkTransfer;` (`0x2103b7`) + `OrbChunkedOutputStream` | VERIFICADO (nombres/clases) / **INFERENCIA** (ausencia de struct de metadatos) |
| El *decoder* del PC debe: `GET /liveview/liveviewstream`, leer `Transfer-Encoding: chunked`, y por cada chunk concatenar hasta tener `FFD8 … FFD9` | deducido de lo anterior | INFERENCIA |

### 1.4 Tamaños

- **VERIFICADO:** `orb-server` **no** ofrece selección de tamaño de liveview (`startLiveview` sin parámetros; no hay literal
  `liveviewQuality`, ni tabla de dimensiones L/M/S de liveview, ni `startLiveviewWithSize`).
- **VERIFICADO:** el tamaño de liveview sí existe en la app: clases `GetSupportedLiveviewSize` / `GetAvailableLiveviewSize` /
  `GetLiveviewSize` (`SmartRemote.odex` `0x1ec5c9`, `0x1ec7b9`, `0x1ec90a`) y constantes
  `LIVEVIEW_COMPRESS_RATE_FOR_DEFAULT(-VGA)`, `LIVEVIEW_COMPRESS_RATE_FOR_LARGE(-VGA)`,
  `LIVEVIEW_MAXIMUM_SIZE_IN_KB_FOR_DEFAULT(-VGA)`, `LIVEVIEW_MAXIMUM_SIZE_IN_KB_FOR_LARGE(-VGA)`
  (offsets `0x1f5155`–`0x1f5298`). **NO_VERIFICADO:** los valores numéricos de esas constantes y las dimensiones en píxeles
  no aparecen como literales estáticos (no hay `1024`, `680`, `480` en el *string pool*).
- **Ojo:** la tabla de tamaños **de foto** de `orb-server` en VA `0x2e5bec`–`0x2e5c28`
  (`16:9`/`17M`/`13M`/`7.5M`/`4.2M`/`2M`, `4:3`/`18M`/`5M`, `3:2`/`20M`, `1:1`/`3.7M`, tras `basic_string::at` y
  `AddonUtils`) es una **tabla genérica de conversión**, no la lista de la A6000 (24M/12M/6.0M). **INFERENCIA:** no usarla
  como verdad de modelo; la lista real la devuelve la cámara en `getSupportedStillSize`.
- `postviewImageSize`: único literal de valor en `orb-server`: `Original` (VA `0x2e6520`). **NO_VERIFICADO** el resto de valores.

### 1.5 Límite de fps

- **NO_VERIFICADO.** No hay constante de fps, ni `sleep`/temporizador de generación en el camino `startLiveview` de `orb-server`
  (la función sólo retransmite la URL). Las claves `LIVEVIEW_GENERATING_FRAMERATE` y `LIVEVIEW_OBTAINING_INTERVAL`
  (`SmartRemote.odex` `0x1f51fd`, `0x1f52c4`) existen como **nombres de clave** de configuración, sin valor estático localizable.
- **INFERENCIA:** el ritmo lo impone la cadena de captura/JPEG de la cámara; el PC no puede fijarlo por API en esta versión.

---

## 2. `liveviewChunkTransfer` / transferencia por trozos

| Hecho | Evidencia | Marca |
|---|---|---|
| No hay variante "chunk transfer" en el servidor nativo | 0 ocurrencias en `orb-server` | VERIFICADO |
| La implementación está en la app | `Lcom/sony/imaging/app/srctrl/webapi/servlet/LiveviewChunkTransfer;` (`0x2103b7`), `Lcom/sony/mexi/orb/android/servlet/OrbAndroidChunkTransfer;`, `Lcom/sony/mexi/orb/server/OrbChunkedOutputStream;`, `OrbDivisionOutputStream` | VERIFICADO |
| Ruta | patrón `/liveview/*` (`0x1d47da`) bajo el servidor de la app (puerto 8080) | VERIFICADO |
| Cabecera por parte | `Transfer-Encoding: chunked` (HTTP/1.1) + `Content-Type: image/jpeg`; tamaño de chunk en hexadecimal + CRLF, terminador `0\r\n\r\n` | VERIFICADO (literales) / **INFERENCIA** (semántica RFC 7230 estándar del `ChunkedOutputStream` de Apache) |
| Metadatos por parte | ninguno identificado | **INFERENCIA** |
| Cierre | `End chunked transfer.` / `Force disconnect chunked transfer.` / `Liveview Loader is not generating liveview data.  Stop chunked transfer.` (`0x21e4de`) | VERIFICADO |

---

## 3. `getEvent`

### 3.1 Naturaleza: *polling*, no notificación

| Hecho | Evidencia | Marca |
|---|---|---|
| `getEvent` es una llamada JSON-RPC normal (petición/respuesta HTTP); **no hay canal de push al PC** | `GetEvent` es una `MethodBase` más (`GetEvent::create` @ `0x229ef4`, `GetEvent::invoke` @ `0x2299c0`) | VERIFICADO |
| `receiveEvent` (el push de WebAPI 1.x) está **explícitamente no soportado** | literal VA `0x2fa9ec`: `"(%04d)[ERR:invoke_cmd: %04d][LibOrb::ReceiveEvent_invoke_cmd] do NOT support after WebAPI2.0 "` | VERIFICADO |
| Internamente sí hay *relay* por cliente: `getEvent` registra el cliente en un pool y la cámara empuja al pool | `GetEvent::invoke` @ `0x2299c0`: `setEvtParamId(msg, 0x205, 0x100)` → `LibOrbRelayPool::AddToPool(client)` → `sendMsgToServer(msg)`, con `relay = AddToPool(...)` en el mensaje | VERIFICADO |
| El pool marca lo ya enviado y devuelve sólo lo pendiente | símbolos `LibOrbRelayPool::SetSentFlagInPool` (`0x186225`), `GetUnSentPoolDataListInPool` (`0x186b0d`), `IsRelayIDInPool`, `RemoveFromPool`; `GetUnSentPoolDataListInPool` recorre entradas con flag `[0x14]`/`[0x24]` | VERIFICADO (símbolos + pseudocódigo) |
| `GetEvent::invoke(bool)` propaga ese `bool` a la cámara | pseudocódigo REA: `local_6b0 = (uint)param_1; sendMsgToServer(...)` | VERIFICADO |
| Significado exacto del `bool` (¿"primera petición"/"forzar todo"?) | no determinado | **NO_VERIFICADO** |

**Conclusión operativa:** desde el PC todo es *polling*. `getEvent` devuelve, tras la primera respuesta completa, sólo los
grupos con cambios (**INFERENCIA** basada en el pool "un-sent"), lo que permite un bucle cerrado con `getEvent` en cada iteración.

### 3.2 Grupos publicados (35) y campos exactos

Orden y composición **VERIFICADOS** por dos vías independientes:
(a) firma de `GetEvent::sendResult` (VA `0x1e342c`, 35 parámetros en ese orden exacto);
(b) tabla de declaraciones de tipo en `.rodata` VA `0x33ccf8`–`0x33d8xx`, 35 literales en el mismo orden.

| # | Grupo (`type`) | Declaración literal (VA) | Campos |
|---|---|---|---|
| 1 | `availableApiList` | `0x33ccf8` `{"type":"string", "names":"string*"}` | `names` |
| 2 | `cameraStatus` | `0x33cd20` `{"type":"string", "cameraStatus":"string"}` | `cameraStatus` |
| 3 | `zoomInformation` | `0x33cd4c` `{"type":"string", "zoomPosition":"int", "zoomNumberBox":"int", "zoomIndexCurrentBox":"int", "zoomPositionCurrentBox":"int"}` | 4 campos |
| 4 | `liveviewStatus` | `0x33cdc8` `{"type":"string", "liveviewStatus":"bool"}` | `liveviewStatus` |
| 5 | `liveviewOrientation` | `0x33cdf4` `{"type":"string", "liveviewOrientation":"string"}` | `liveviewOrientation` |
| 6 | `takePicture` | `0x33ce28` `{"type":"string", "takePictureUrl":"string*"}*` | `takePictureUrl` (lista) |
| 7 | `continuousError` | `0x33ce58` `{"type":"string", "continuousError":"string", "isContinued":"bool"}*` | `continuousError`, `isContinued` |
| 8 | `triggeredError` | `0x33cea0` `{"type":"string", "triggeredError":"string*"}` | `triggeredError` |
| 9 | `sceneRecognition` | `0x33ced0` `{"type":"string", "sceneRecognition":"string", "steadyRecognition":"string", "motionRecognition":"string"}` | 3 campos |
| 10 | `formatStatus` | `0x33cf3c` `{"type":"string", "formatResult":"string"}` | `formatResult` |
| 11 | `storageInformation` | `0x33cf68` `{"type":"string", "storageID":"string", "recordTarget":"bool", "numberOfRecordableImages":"int", "recordableTime":"int", "storageDescription":"string"}*` | 5 campos (lista) |
| 12 | `beepMode` | `0x33d004` | `currentBeepMode`, `beepModeCandidates` |
| 13 | `cameraFunction` | `0x33d054` | `currentCameraFunction`, `cameraFunctionCandidates` |
| 14 | `movieQuality` | `0x33d0b0` | `currentMovieQuality`, `movieQualityCandidates` |
| 15 | `stillSize` | `0x33d108` | `checkAvailability`, `currentAspect`, `currentSize` |
| 16 | `cameraFunctionResult` | `0x33d168` | `cameraFunctionResult` |
| 17 | `steadyMode` | `0x33d19c` | `currentSteadyMode`, `steadyModeCandidates` |
| 18 | `viewAngle` | `0x33d1f0` | `currentViewAngle`, `viewAngleCandidates` |
| 19 | `exposureMode` | `0x33d23c` | `currentExposureMode`, `exposureModeCandidates` |
| 20 | `postviewImageSize` | `0x33d294` | `currentPostviewImageSize`, `postviewImageSizeCandidates` |
| 21 | `selfTimer` | `0x33d2f4` | `currentSelfTimer`, `selfTimerCandidates` |
| 22 | `shootMode` | `0x33d340` | `currentShootMode`, `shootModeCandidates` |
| 23 | `aeLock` | `0x33d390` | `currentAELock`, `aeLockCandidates` |
| 24 | `bracketShootMode` | `0x33d3d8` | `checkAvailability`, `currentBracketShootMode`, `currentBracketShootModeOption` |
| 25 | `creativeStyle` | `0x33d454` | `checkAvailability`, `currentCreativeStyle`, `…Contrast`, `…Saturation`, `…Sharpness` |
| 26 | `exposureCompensation` | `0x33d518` | `currentExposureCompensation`, `max…`, `min…`, `stepIndexOfExposureCompensation` |
| 27 | `flashMode` | `0x33d5bc` | `currentFlashMode`, `flashModeCandidates` |
| 28 | `fNumber` | `0x33d60c` | `currentFNumber`, `fNumberCandidates` |
| 29 | `focusMode` | `0x33d658` | `currentFocusMode`, `focusModeCandidates` |
| 30 | `isoSpeedRate` | `0x33d6a8` | `currentIsoSpeedRate`, `isoSpeedRateCandidates` |
| 31 | `pictureEffect` | `0x33d700` | `checkAvailability`, `currentPictureEffect`, `currentPictureEffectOption` |
| 32 | `programShift` | `0x33d778` | `isShifted` |
| 33 | `shutterSpeed` | `0x33d7a0` | `currentShutterSpeed`, `shutterSpeedCandidates` |
| 34 | `whiteBalance` | `0x33d7f8` | `checkAvailability`, `currentWhiteBalanceMode`, `currentColorTemperature` |
| 35 | `touchAFPosition` | `0x33d86c` `{"type":"string", "currentSet":"bool", "currentTouchCoordinates":"double*"}` | `currentSet`, `currentTouchCoordinates` |

Tabla de nombres de campo usada por el *parser* de la respuesta de cámara: `.rodata` VA `0x2faa58`–`0x2faf6c`
(`type`, `cameraStatus`, `formatResult`, …, `currentSet`, `currentTouchCoordinates`, `set`, `touchCoordinates`).

Subconjunto con **nombre de grupo literal confirmado** en la ruta `GetEvent_invoke_cmd` (`.rodata` VA `0x2fe53c`–`0x2fe7d4`,
22 literales): `formatStatus`, `exposureMode`, `flashMode`, `shootMode`, `cameraFunction`, `postviewImageSize`, `stillSize`,
`zoomInformation`, `availableApiList`, `selfTimer`, `beepMode`, `takePicture`, `viewAngle`, `storageInformation`,
`movieQuality`, `steadyMode`, `focusMode`, `touchAFPosition`, `exposureCompensation`, `fNumber`, `whiteBalance`, `shutterSpeed`.
Los 13 restantes (#1–#9 salvo los citados, más `aeLock`, `bracketShootMode`, `creativeStyle`, `pictureEffect`, `programShift`,
`isoSpeedRate`, `cameraFunctionResult`) se infieren de la firma de `sendResult` y de la tabla de declaraciones → **INFERENCIA**.

### 3.3 Campos de seguimiento pedidos

| Campo pedido | ¿Existe? | Grupo / evidencia |
|---|---|---|
| `liveviewStatus` | **Sí** | grupo #4, `bool`, VA `0x33cdc8`; nombre de campo en `0x2facfc` |
| `cameraStatus` | **Sí** | grupo #2, `string`, VA `0x33cd20`; además `GetEvent_invoke_cmd` registra `cameraStatusID:%x` (VA `0x2fe4f0`) leído de un bloque `MP_get_ptr` |
| `touchAFPosition` | **Sí** | grupo #35: `currentSet` + `currentTouchCoordinates` (`double*`), VA `0x33d86c` |
| `focusStatus` | **No** | 0 ocurrencias de `focusStatus` en el binario |
| `focusMode` | **Sí** | grupo #29: `currentFocusMode` + `focusModeCandidates`, VA `0x33d658` |
| `zoomInformation` | **Sí** | grupo #3: `zoomPosition`, `zoomNumberBox`, `zoomIndexCurrentBox`, `zoomPositionCurrentBox`, VA `0x33cd4c` |
| `currentShootMode` | **Sí** | dentro del grupo `shootMode` (#22), VA `0x33d340` |
| `storageInformation` | **Sí** | grupo #11 (lista), VA `0x33cf68` |
| `postviewImageSize` | **Sí** | grupo #20: `currentPostviewImageSize` + candidatos, VA `0x33d294` |

Valores de `cameraStatus` (`orb-server` `.rodata` VA `0x2e62f8`–`0x2e63c8`, **VERIFICADO**):
`NotReady`, `IDLE`, `StillCapturing`, `StillSaving`, `MovieWaitRecStart`, `MovieRecording`, `MovieWaitRecStop`,
`MovieSaving`, `IntervalWaitRecStart`, `IntervalRecording`, `IntervalWaitRecStop`, `Formatting`, `ContentsTransfer`.

Cadenas `AFResult` / `AFType` (VA `0x2fad3c`, `0x2fad48`) existen en la tabla de nombres pero **ninguna declaración de tipo
ni símbolo de esta versión las usa** (`touchAFPosition` sólo publica `currentSet`/`currentTouchCoordinates`).
→ **NO_VERIFICADO** su exposición por la API en fw3.21; en la app sí hay un enum interno
`CameraOperationTouchAFPosition$CameraNotificationListener$AFType` (usado por la UI, no por el JSON).

### 3.4 Qué es "polling" y qué es "notificación"

- **Notificación lógica** (la cámara avisa a `orb-server` y éste la entrega como delta en el siguiente `getEvent`):
  los 35 grupos anteriores. Los útiles para tiempo real son `liveviewStatus`, `cameraStatus`, `touchAFPosition`,
  `focusMode`, `shootMode`, `zoomInformation`, `takePicture`, `triggeredError`, `storageInformation`.
- **Polling puro** (no viajan en `getEvent`; requieren llamada propia): `getApplicationInfo`, `getAvailableApiList`,
  `getSupported*`, `getAvailable*`, `getTouchAFPosition`, `getStorageInformation`, `getShootMode`, `getFocusMode`, `getVersions`.
- **No hay notificación real al PC** (`receiveEvent` no soportado) → el PC debe llamar `getEvent` en bucle (recomendado:
  sin esperas, `getEvent` ya devuelve vacío si no hay cambios; **INFERENCIA**).

---

## 4. Modos: `getSupportedShootMode` y `getSupportedFocusMode`

**Los valores dependen del estado de la cámara en ejecución** (los produce el backend vía `WebApiAddonUipc`).
`orb-server` sólo contiene las **tablas de conversión id↔cadena**; lo que devuelve la A6000 no es demostrable en estático
(**NO_VERIFICADO** para el subconjunto real).

| Vocabulario presente en `orb-server` | Dirección | Cadena exacta |
|---|---|---|
| shootMode | `0x2e6400` | `movie` |
| shootMode | `0x2e6408` | `intervalstill` |
| shootMode | `0x2e6410` | `still` (sólo como sufijo del literal `intervalstill`; **no** hay entrada independiente) |
| focusMode | `0x2e6cdc` | `MF` |
| focusMode | `0x2e6ce0` | `AF-S` |
| focusMode | `0x2e6ce8` | `A-Macro` |
| focusMode | `0x2e6cf0` | `AF-C` |
| focusMode | `0x2e6cf8` | `AF-A` |
| focusMode | `0x2e6d00` | `AF-D` |
| focusMode | `0x2e6d08` | `DMF` |
| focusMode | `0x2e6d0c` | `MF-R` |

- **INFERENCIA:** la A6000 devolverá un subconjunto de esa tabla (típicamente `AF-S`, `AF-C`, `AF-A`, `DMF`, `MF`;
  `A-Macro`/`AF-D`/`MF-R` son entradas de otros modelos compiladas en el binario genérico).
- **Touch AF:** `setTouchAFPosition` / `cancelTouchAFPosition` / `getTouchAFPosition` existen como métodos
  (`SetTouchAFPosition`, `CancelTouchAFPosition`, `GetTouchAFPosition` en `.dynsym`; logs VA `0x327cf8`
  `"touch AF position x=%f y=%f val=%x"`, `"parameter err"`). Validación observada: sólo parámetros `x`,`y`
  (`"parameter err"`, VA `0x327cb4`); **no se encontró ninguna compuerta sobre `shootMode`** en `orb-server`.
  → **NO_VERIFICADO** si exige `shootMode == "still"`; **INFERENCIA:** requiere la app Smart Remote Control activa y AF
  disponible (modo foto), porque el backend de cámara decide.

---

## 5. Arranque de `orb-server`

### 5.1 Lanzador

`.../nflasha15_unpacked_unpacked/bin/WebApiLauncher.sh` (fichero completo, **VERIFICADO**):

```sh
#!/bin/sh
echo "busybox killall orb-server"
busybox killall orb-server
echo "Starting orb-server!"
LD_LIBRARY_PATH=/usr/glib orb-server -f /usr/share/network/remotecontrol -p 10000 -D -1 &
echo "... Started!"
```

- Puerto **10000** (`-p 10000`) y raíz de contenido `-f /usr/share/network/remotecontrol` (existe en la partición:
  `share/network/remotecontrol/index.html` + `orbjs/dist/orb-client.min.js`).
- `main()` @ `0x184140` confirma el contrato: `getopt(argc, argv, "f:p:D:")` (literal `f:p:D:` VA `0x2e3870`),
  logs `fsPath <= %s` (`0x2e3878`), `port <= %d` (`0x2e38ac`), `debug_level <= %d` (`0x2e38e0`); **si no se pasa `-p`,
  el puerto por defecto es 10000** (instrucción `movwlt r6, #0x2710` en `0x18428a` y `movw r3, #0x2710` en `0x1843ea`).
- Configuración del transporte con claves literales `host` (VA `0x3703f0`) y `port` (VA `0x370414`) —el otro `port`
  de `.rodata` en `0x358359` es sufijo de `transport` (VA `0x358354`)—, más `root` (`0x353b4c`), `backlog` (`0x353b54`),
  `maxBodySize` (`0x353b6c`), `timeout` (`0x353b78`), `listen` (`0x2e7534`), `server` (`0x2e7e64`), `http` (`0x2e8314`)
  y la raíz de rutas `/sony/` (VA `0x2e3914`).

### 5.2 Quién lo lanza

| Hecho | Evidencia | Marca |
|---|---|---|
| La tabla de recursos de infraestructura referencia el script | `lib/libIMDB.so` contiene la cadena `/usr/bin/WebApiLauncher.sh` (junto a `/usr/bin/network.sh`, `libInfraRemoteControlNet.so` + `InfraRemoteControlNet_Init`, `libInfraWebApi.so` + `InfraNetWebApi_init`) | VERIFICADO |
| El servicio de control remoto de red es quien arranca el *web api* | `lib/libInfraRemoteControlNet.so` exporta `InfraRemoteControlNet_Init/Exit`; `libIMDB.so` es la tabla `IMDB_*` (`IMDB_find_entry`, `IMDB_get_entries`) | VERIFICADO (símbolos) / **INFERENCIA** (orden de arranque) |
| `libInfraWebApi.so` ("iwaJobs") **mata** `orb-server` al salir | literales `"(%04d)[ERR:iwaJobs: %04d]I will Kill orb-server by \"killall\""` y `"### /bin/busybox killall orb-server"` | VERIFICADO |
| La app que habilita el modo es **Smart Remote Control** | `app/SmartRemote.apk` → `package com.sony.imaging.app.srctrl`; componente `com.sony.imaging.app.srctrl.webapi.service.OrbAndroidService`; permisos `ACCESS_WIFI_STATE`, `CHANGE_WIFI_STATE`, `CHANGE_WIFI_MULTICAST_STATE`, `INTERNET` | VERIFICADO |
| Descubrimiento en red por SSDP | `app/ScalarWebAPIDdService.odex`: `SsdpDeviceJni`, claves `SSDP_SCPDURL`, `SSDP_DEVICE_TYPE`, `SSDP_WEBAPI_SERVICE_TYPE`, `ssdpPort`; ruta `/scalarwebapi_dd.xml` | VERIFICADO |
| `orb-server` se autodescribe en `/sony/index.html`, y expone bucles internos `/sony/localloopback` y `/sony/shutdown` (`{"method":"actShutdown"}`) | `.data` VA `0x391e68`, `0x391e98` (`Content-Type: application/json`), `0x391ec0` (`{"method":"`), `0x391ef8` | VERIFICADO |

**Respuesta operativa:** hay que **abrir la app "Smart Remote Control"** (`com.sony.imaging.app.srctrl`) en la cámara y tener
la Wi-Fi de la cámara activa; eso hace que la capa de infraestructura (`libInfraRemoteControlNet` → `libIMDB`) ejecute
`/usr/bin/WebApiLauncher.sh`, que mata y relanza `orb-server -f /usr/share/network/remotecontrol -p 10000 -D -1`.
El stream de liveview lo sirve la propia app en **8080**. **INFERENCIA** (no verificado en cámara): sin esa app no hay
`orb-server` ni liveview; `network.sh` sólo lanza `/usr/bin/WS_SubProcess.elf`.

---

## 6. Detección de caras en los eventos

- **NO. Esta versión no publica `faceDetection` ni `faceInfos` en `getEvent`.**
  `grep -icE "faceDetection|faceInfos|focusStatus"` sobre `orb-server` → **0**. No hay grupo ni campo de caras entre los 35
  (ver §3.2) y no existe ninguna clase `GetEvent…Face…` en `.dynsym`.
- En la app sí existe maquinaria interna de caras (`getFaceInfos`, `Lcom/sony/scalar/meta/FaceInfo;`,
  `[Lcom/sony/scalar/meta/FaceInfo;` en `SmartRemote.odex`), **pero no se publica como campo de evento**
  (no existen los literales `faceDetection`/`faceInfos`). → **INFERENCIA:** uso interno de la UI de la app.

---

## 7. Receta de bucle cerrado desde el PC (derivada de lo anterior)

1. Wi-Fi a la cámara; abrir "Smart Remote Control" en la cámara. Comprobar `GET http://<ip>:10000/sony/camera` (`getVersions`).
2. `startRecMode` (necesario en la A6000 para habilitar foto; está en la lista de APIs, VA `0x2e7eec`).
3. `getEvent` → leer `type:"availableApiList".names` para saber qué está habilitado en ese momento.
4. `setShootMode("still")`, ajustes (`setFNumber`, `setShutterSpeed`, `setIsoSpeedRate`, `setWhiteBalance`…).
5. `startLiveview` → usar la URL devuelta (`http://<ip>:8080/liveview/liveviewstream`) con `GET` y *chunked*: un JPEG por chunk.
6. Bucle de control: `getEvent` en cada iteración; vigilar `liveviewStatus`, `cameraStatus` (`IDLE`→`StillCapturing`→`StillSaving`),
   `touchAFPosition`, `focusMode`, `zoomInformation`, `takePicture`.
7. Enfoque puntual: `setTouchAFPosition {x, y}` (log `x=%f y=%f val=%x`), `getTouchAFPosition` para confirmar
   `currentSet`/`currentTouchCoordinates`, `cancelTouchAFPosition` para liberar.
8. Disparo: `actTakePicture` → `awaitTakePicture` (o `takePictureUrl` del evento).
9. `stopLiveview` y `stopRecMode` al terminar; `actShutdown` existe en `/sony/shutdown` (**no usar**: apaga el servidor).

**Latencia:** no determinable estáticamente; depende del empaquetado JPEG y del *chunking* de la app (**NO_VERIFICADO**).

---

## 8. Límites de este análisis (pendientes de verificación física)

1. Subconjunto real de `getSupportedShootMode` / `getSupportedFocusMode` / `getSupportedLiveviewSize` en la A6000 (requiere cámara).
2. Dimensiones en píxeles y fps efectivos del stream de 8080 (no hay literales).
3. Significado del `bool` de `GetEvent::invoke(bool)` y confirmación de que el primer `getEvent` es completo.
4. Si `setTouchAFPosition` exige `shootMode == "still"`.
5. IP real del AP (`192.168.122.1` es literal de la app, no medido).

---

## Anexo A — Direcciones citadas (VA)

```
0x184140  main
0x18428a  movwlt r6,#0x2710            ; puerto por defecto 10000
0x1a3f8c  Remote::v1_0::StartLiveview_invoke_cmd
0x21f4f0  Remote::v1_0::StartLiveview::invoke
0x21fe2c  Remote::v1_0::StartLiveview::parameterTypes   ; sin parámetros
0x21feac  Remote::v1_0::StartLiveview::resultTypes      ; ["string"]
0x2299c0  Remote::v1_0::GetEvent::invoke(bool)          ; setEvtParamId(0x205,0x100) + AddToPool
0x229ef4  Remote::v1_0::GetEvent::create
0x1e342c  Remote::v1_0::GetEvent::sendResult            ; 35 grupos
0x1bd2f8  Remote::v1_0::GetEvent_invoke_cmd             ; 40 330 B, tabla de grupos 0x2fe53c
0x186b0c  LibOrbRelayPool::GetUnSentPoolDataListInPool  ; semántica delta
0x186224  LibOrbRelayPool::SetSentFlagInPool
0x2e7eec  literal: lista de APIs (26 entradas)
0x33ccf8  tabla de declaraciones de tipo de getEvent (35 literales, 0x33ccf8-0x33d8xx)
0x2fe53c  tabla de nombres de grupo usada por GetEvent_invoke_cmd
0x2faa58  tabla de nombres de campo (type, cameraStatus, …, currentSet, currentTouchCoordinates)
0x2fb034  "[startLiveview cmd] url=%s"
0x2fa9ec  "LibOrb::ReceiveEvent_invoke_cmd] do NOT support after WebAPI2.0"
0x2e62f8  valores de cameraStatus (NotReady … ContentsTransfer)
0x2e6ce0  tabla focusMode (AF-S, A-Macro, AF-C, AF-A, AF-D, DMF, MF-R; MF en 0x2e6cdc)
0x2e6400  tabla shootMode (movie, intervalstill; "still" sólo como sufijo)
0x2e5bec  tabla genérica de tamaños de foto (16:9/17M…, 4:3/18M…, 3:2/20M, 1:1/3.7M)
0x2e3870  "f:p:D:"  0x2e3878 "fsPath"  0x2e38ac "port"  0x2e38e0 "debug_level"
0x2e3914  "/sony/"
0x3703f0  "host"    0x370414 "port"    (claves del transporte HTTP interno)
0x391e68  "/sony/localloopback"   0x391ef8 "/sony/shutdown"
```
