# S179 — el módulo `[CAM_SCALAR]` (34 trazas) de la A6000 fw3.21

> Hito de la **línea de RE general por módulos de trazas**. Sólo análisis de bytes
> (sin REA/Ghidra, sin ejecutar firmware). Convención **vaddr = 0x43541000 + file_offset**.
> Referencias a cadenas: **regla PIC estricta** (canónica del repo,
> `analysis/s106_imaging_cap/scan_pic_refs_strict.py`; nota metodológica:
> `analysis/s106_imaging_cap/pic_xref_methodology.md`).
> VERIFICADO = contra bytes. INFERENCIA = lectura razonada. **NO VERIFICADO** = pendiente.

---

## 1. Resumen / veredicto

**`[CAM_SCALAR]` no es un módulo de código con nombre propio: es una ETIQUETA de traza
añadida en la fw3.21 de la A6000 a la capa de la cámara que atiende las peticiones HAPI
de imagen (el *HAPI Manager* + los filtros HAPI del pipeline TBOX).**

La etiqueta se antepone **en el sitio** a 34 mensajes que **ya existían, sin prefijo, en los
tres firmwares**: el texto original queda **intacto 14 bytes más allá** (`[CAM_SCALAR]: `
ocupa exactamente 14 B) y **sigue siendo referenciado** por el logger global. Es exactamente
el patrón «se reescribe el logging» de S128/S130, medido byte a byte.

| magnitud | valor |
|---|---|
| cadenas con el token `[CAM_SCALAR]` | **34** (34 apariciones = 34 textos) |
| rango de las cadenas | `0x43cb045a` – `0x43cc679a` (33 en un bloque + 1 aislada) |
| sitios de emisión PIC (regla estricta) | **47** en **14 funciones** |
| sitios PIC de los gemelos `+14` (traza vieja) | **47** |
| pares PIC verificados a mano | **94 / 94** (47 nuevos + 47 gemelos), 0 fallos, 0 reuso de registro |
| cadenas **sin ninguna referencia** | **3** (`Open Error`, `%s: AllocNewWait error`, `%s: %d Free error`) |
| punteros absolutos de 4 B a las 34 (+ gemelos) | **0** en los tres firmware |
| gemelo exacto en `+14` | **34 / 34** |
| núcleo sin prefijo presente en A7S / A6300 | **34 / 34** y **34 / 34** |
| id de módulo / nivel de la traza nueva | **5** / **6** (flag 1) en los 47 sitios |
| diferencial del token `[CAM_SCALAR]` | A6000 fw3.21 **34** / A7S fw3.20 **0** / A6300 fw2.01 **0** |

**Respuesta a la hipótesis del enunciado — «[CAM_SCALAR] = ¿la capa de cámara que usa el
acelerador escalar SA?» → REFUTADA por los bytes:**

1. Las 14 funciones emisoras hacen **0 llamadas** a la región `NS_SCALAR_INFRA`
   (`0x43990000`–`0x439c0000`, donde vive `[SAD]` — S167 —, `[SFRA]` y `[SFRS]`). Las únicas
   llamadas que caen en la banda `0x439xxxxx` son el **logger global** `0x43902718` y el
   emisor de respuestas `0x43901a8c` (códigos `0x16b`–`0x16d`): ninguna es el acelerador.
2. El código del módulo **no referencia ninguna cadena `sa_func_*`**: los filtros HAPI de
   esta zona no tocan el acelerador SA (el `sa_func_SPICA_acquire`/`sa_func_YKNR_*`etc. son
   de `[IMAGING_CAP]`, otra capa).
3. Todas las cadenas `SCALAR`/`Scalar` de la A6000 pertenecen a `NS_SCALAR_INFRA` (88
   apariciones de `Scalar`, 261 de `SCALAR`), **ninguna** a este módulo.
4. El contenido de los 34 mensajes es de **procesado de imagen**: recepción de peticiones HAPI,
   validación de imágenes de entrada, handles DMM (`YCC_FULL`, `RAW_FULL`), buffers
   YC/SDS-YC, clonado/parseo/inserción/extracción de imágenes, *develop* RAW→YC y parámetros
   de secuencia.

**La sigla NO tiene base textual.** `CAM_SCALAR` aparece **34 veces = exactamente las 34
trazas**; `CamScalar` = 0; `cam_scalar` = 0; `CAM_SCAL` = 34. **Se deja sin desarrollar**:
no se propone «SA-Camera», «Camera Scalar» ni ninguna otra expansión.

---

## 2. Qué es exactamente `[CAM_SCALAR]`

### 2.1 Anatomía del módulo (por los bytes)

El código que emite las 34 trazas vive en **dos bloques** contiguos dentro de
`av-cam.bin`:

| bloque | rango de código | contenido |
|---|---|---|
| **A — HAPI Manager + filtros** | `0x4380a688` – `0x4380c6f4` | bucle de recepción OSAL, despacho por `MSG_ID`, y los filtros `req_*` / `Start_*` |
| **B — control de RecordCount** | `0x438bbe4c` | una función aislada en la zona de `ImageParamCapture_SyncBranch.cpp` |

El bloque A es el **lado cámara de la API HAPI** (`libHapiLib.so`: `HapiLibMain`, `CamService`,
`CamApi`, `REQ_MSGE`/`EVT_MSGE`/`COMP_MSGE`, ver `analysis/s94_hapi/hapi_api.md`):

* **`0x4380a688` — despachador del «HAPI Manager»** (21 de los 47 sitios).
  Recibe un mensaje OSAL, valida tamaño y contenido, y despacha por **`MSG_ID`**
  con una tabla `tbh` de **23 entradas** (`0x4380a72c`), ids **`0x5001`–`0x5017`**:

  ```
  0x4380a716  ldrh.w  r3, [sp, #0x182]   ; msg id
  0x4380a71a  ldr     r4, [sp, #0x188]
  0x4380a71c  sub.w  r3, r3, #0x5000     ; - 0x5000
  0x4380a720  subs   r3, #1              ; - 1   -> 0x5001..0x5017
  0x4380a722  cmp    r3, #0x16           ; 22  -> 23 casos
  0x4380a724  bhi.w  0x4380adf8          ; fuera de rango
  0x4380a728  tbh    [pc, r3, lsl #1]    ; base 0x4380a72c
  ```
  Destinos medidos de la tabla: `0x5001`→`0x4380a75a`, `0x5002`→`0x4380a776`,
  `0x5003`/`0x500e`/`0x500f`→`0x4380adf8`, `0x5004`/`0x5006`/`0x500a`–`0x500d`→`0x4380ae0e`
  (rama por defecto), `0x5005`→`0x4380a9be`, `0x5007`→`0x4380a850`, `0x5008`→`0x4380ab2c`,
  `0x5009`→`0x4380a808`, `0x5010`→`0x4380ac36`, `0x5011`→`0x4380ac78`, `0x5012`→`0x4380acbe`,
  `0x5013`→`0x4380ad06`, `0x5014`→`0x4380a7bc`, `0x5015`→`0x4380a7ce`, `0x5016`→`0x4380ad6e`,
  `0x5017`→`0x4380adb4`.

* Los **filtros** implementados (nombre embebido en el binario, referenciado por PIC justo
  antes de la traza de error, y usado como `%s`):

  | nombre embebido | vaddr | función que lo referencia | qué hace |
  |---|---|---|---|
  | `req_sequence_create_stream` | `0x43cb04d6` | `0x4380a792` | crea el *stream* de una secuencia |
  | `req_tool_get_image_info` | `0x43cb0515` | `0x4380a7dc` | info de imagen (herramienta) |
  | `req_filter_develop` | `0x43cb0551` | `0x4380a824` | *develop* RAW→YC |
  | `req_filter_face_nr` | `0x43cb068b` | `0x4380a9d8` | filtro de reducción de ruido de cara |
  | `req_filter_miniature` | `0x43cb06d3` | `0x4380a86c` | filtro miniatura |
  | `req_filter_soft_focus` | `0x43cb040f` | `0x4380ab46` | filtro desenfoque suave |
  | `req_image_parse` | `0x43cb06b0` | `0x4380ad7c` | parseo de imagen |
  | `req_raw_image_parse` | `0x43cb0425` | `0x4380adc2` | parseo de imagen RAW |
  | `req_image_clone` | `0x43cb044a` | `0x4380ac86` | clonado de imagen |
  | `req_image_insert` | `0x43cb0439` | `0x4380ad14` | inserción de imagen |
  | `req_image_extract` | `0x43cb069e` | `0x4380accc` | extracción de imagen |
  | `req_image_destruct` | `0x43cb06c0` | `0x4380ac44` | destrucción de imagen |
  | `Start_Develop` | `0x43cb075e` | `0x4380b034` | |
  | `Start_FaceNr` | `0x43cb078a` | `0x4380b212` | |
  | `Start_SoftFocus` | `0x43cb0797` | `0x4380b56a` | |
  | `Start_Miniature` | `0x43cb07a7` | `0x4380b726` | |
  | `Start_Extract` | `0x43cb0988` | `0x4380b904` | |
  | `Start_Insert` | `0x43cb07e4` | `0x4380b9f8` | |
  | `Start_Parse` | `0x43cb07d8` | `0x4380bb5a` | |
  | `Start_RawParse` | `0x43cb09bd` | `0x4380bc04` | |
  | `Start_Clone` | `0x43cb07cc` | `0x4380be32` | |
  | `Start_CreateStream` | `0x43cb09dd` | `0x4380c1ca` | |
  | `CheckMemory` | `0x43cb06e8` | `0x4380b078` | |
  | `CheckDMMforClone` | `0x43cb09cc` | `0x4380be10` | |
  | `ShareDMMforClone` | `0x43cb0996` | `0x4380bf36` | |
  | `ConvertAspectForStill` | `0x43cb09a7` | `0x4380bac4` | |
  | `SetSpecialSequence` | `0x43cb09f0` | `0x4380c362` | |
  | `copyStdYc` | `0x43cb0b43` | `0x4380c52c` | |
  | `ToolGetImageInfo` | `0x43cb0b4d` | `0x4380c650` | |

  Los nombres `req_*` / `Start_*` / `Check*` son **el `%s` de las trazas de error**: el código
  carga la cadena del nombre y la pasa como primer vararg (p. ej. `0x4380a86c` →
  `req_filter_miniature`; `0x4380c362` → `SetSpecialSequence`).

* **`0x4380c344` — `SetSpecialSequence`**: valida un bloque de parámetros de 6 bytes
  leído de `r0`:
  * `p[0] == 1` → el parámetro es de tipo «secuencia especial»;
  * `p[4]` = `ExposureCount`: debe ser **1** (`cmp r7,#1` en `0x4380c352`; si no,
    traza `ExposureCount parameter value is invalid.` en `0x4380c360`);
  * `p[5]` = `RecordCount`: debe ser **≤ 5** (`cmp r3,#5` en `0x4380c37a`; si no, traza
    `RecordCount parameter value is invalid.` en `0x4380c388`);
  * tras pasar los bytes a `0x437dfbd8`, si devuelve 0 → traza
    `CapMode is not CAP_SINGLE` (`0x4380c3d6`).

* **`0x438bbe4c` — control de `RecordCount`**: lee `p[0x20]` y `p[0x28]`; si difieren emite
  `RecordCount Unmatch! : remain %d` (`0x43cc679a`, sitio `0x438bbe62`) con la diferencia.

### 2.2 La estructura de datos que gestiona

**Handles de imagen del gestor de memoria DMM** (el módulo abre, comparte y libera
handles, no pixels):

| concepto | evidencia |
|---|---|
| `DMM_HANDLE_YCC_FULL` | constante embebida en el propio formato de la traza `0x43cb07f1` (`dmm_handle[DMM_HANDLE_YCC_FULL] error`) |
| `YCC_FULL` (imagen Y/C completa) | trazas `No YCC_FULL handle` `0x43cb0865`, `dmm_handle[DMM_HANDLE_YCC_FULL] error` `0x43cb07f1` |
| `RAW_FULL` (imagen RAW completa) | traza `No RAW_FULL handle` `0x43cb088a` |
| handle DMM genérico (`dmm_handle[%d]`) | trazas `0x43cb08af` y `0x43cb093d` |
| compartir handles entre clones | `CheckDMMforClone` `0x43cb09cc`, `ShareDMMforClone` `0x43cb0996`, trazas `ShareCheck error` `0x43cb08d6`, `dmm_handle[%d] Share error` `0x43cb093d`, `Share error` `0x43cb096a` |

**Objetos de imagen**: `input image` (imagen de entrada), `outImage` (`0x43cb091c`),
`stdYcHandle` (`0x43cb0631`, «standard YC» — el objeto `stdYc` de la cámara), `sdsYC`
(`0x43cb0588`, «SDS YC» = YC en formato *Standard Data Structure*; base textual:
`[ADF]AdfSdsYcParser::GetEntrySize` `0x43c2ced3`, `::Open err` `0x43c2cef6`,
`::Close err` `0x43c2cf18`).

**Parámetros**: `p_newparam` (`0x43cb08f9`), `p_param` (en `outImage error`).

**Buffers YC**: `copyStdYc` (`0x43cb0b43`), `Alloc SDS YC error` (`0x43cb0829`),
`YC(develop) DMM allocation error[%d]` (`0x43cb0726`), `SdsYc error` (`0x43cb076c`).

**Parámetros de secuencia**: `ExposureCount`, `RecordCount`, `CapMode`/`CAP_SINGLE`.

### 2.3 La base textual (lo que sí se puede verificar)

* **Ficheros fuente** (§4): `HAPI_Filter_TBOX.cpp`, `CS_Command.cpp`,
  `ImageParamCapture_SyncBranch.cpp`.
* **Nombres de método** (§2.1): 29 nombres `req_*` / `Start_*` / `Check*` / `Share*` /
  `Convert*` / `Set*` embebidos y referenciados por PIC.
* **RTTI**: en la zona de código del módulo **no hay ninguna clase RTTI referenciada por
  PIC**; la única clase RTTIFt Limitada es `N6Camera7CamCore13SplitRdcImageE` (`0x43cb0b94`),
  que pertenece a `Camera::CamCore` y es compartida por los tres firmware.
  **No hay RTTI propio del módulo** → NO VERIFICADO si existe una clase con ese nombre.

---

## 3. Las 34 trazas (dirección exacta + sitio de referencia)

`addr` = dirección de la cadena; `gemelo` = dirección del **literal original sin prefijo**
(siempre `addr + 14`); `sitio` = dirección del `add rX,pc` (regla PIC estricta, verificada a
mano en §7).

| # | addr | gemelo | texto | n | sitio(s) | función(es) |
|---|---|---|---|---|---|---|
| 1 | `0x43cb045a` | `0x43cb0468` | `[CAM_SCALAR]: HAPI Manager:Recieve error` | 1 | `0x4380a6b8` | `0x4380a688` |
| 2 | `0x43cb0483` | `0x43cb0491` | `[CAM_SCALAR]: HAPI Manager:Message size 0` | 1 | `0x4380a6e6` | `0x4380a688` |
| 3 | `0x43cb04ad` | `0x43cb04bb` | `[CAM_SCALAR]: HAPI Manager:Empty Message` | 1 | `0x4380a70a` | `0x4380a688` |
| 4 | `0x43cb04d6` | `0x43cb04e4` | `[CAM_SCALAR]: req_sequence_create_stream: input image is null.` | 1 | `0x4380a792` | `0x4380a688` |
| 5 | `0x43cb0515` | `0x43cb0523` | `[CAM_SCALAR]: req_tool_get_image_info: input image is null.` | 1 | `0x4380a7dc` | `0x4380a688` |
| 6 | `0x43cb0551` | `0x43cb055f` | `[CAM_SCALAR]: req_filter_develop: input image is null.` | 1 | `0x4380a824` | `0x4380a688` |
| 7 | `0x43cb0588` | `0x43cb0596` | `[CAM_SCALAR]: %s: input image and sdsYC is invalid.` | 3 | `0x4380a872`, `0x4380a9e0`, `0x4380ab4c` | `0x4380a688` |
| 8 | `0x43cb05bc` | `0x43cb05ca` | `[CAM_SCALAR]: %s: copyStdYc error.` | 3 | `0x4380a8a0`, `0x4380aa70`, `0x4380ab7a` | `0x4380a688` |
| 9 | `0x43cb05df` | `0x43cb05ed` | `[CAM_SCALAR]: %s: warning. NR Level OFF` | 1 | `0x4380aa12` | `0x4380a688` |
| 10 | `0x43cb0607` | `0x43cb0615` | `[CAM_SCALAR]: %s: input image is invalid.` | 6 | `0x4380ac4a`, `0x4380ac8c`, `0x4380acd2`, `0x4380ad1a`, `0x4380ad82`, `0x4380adc8` | `0x4380a688` |
| 11 | `0x43cb0631` | `0x43cb063f` | `[CAM_SCALAR]: %s: input stdYcHandle is invalid.` | 1 | `0x4380ad3c` | `0x4380a688` |
| 12 | `0x43cb0661` | `0x43cb066f` | `[CAM_SCALAR]: HAPI Manager:Unknown MSG_ID` | 1 | `0x4380ae00` | `0x4380a688` |
| 13 | `0x43cb06f4` | `0x43cb0702` | `[CAM_SCALAR]: %s: input image unsupported format.` | 3 | `0x4380b032`, `0x4380c1c8`, `0x4380c6a2` | `0x4380afec`, `0x4380c180`, `0x4380c638` |
| 14 | `0x43cb0726` | `0x43cb0734` | `[CAM_SCALAR]: %s: YC(develop) DMM allocation error[%d].` | 1 | `0x4380b074` | `0x4380afec` |
| 15 | `0x43cb076c` | `0x43cb077a` | `[CAM_SCALAR]: %s: SdsYc error` | 3 | `0x4380b210`, `0x4380b568`, `0x4380b724` | `0x4380b1a8`, `0x4380b500`, `0x4380b6bc` |
| 16 | `0x43cb07f1` | `0x43cb07ff` | `[CAM_SCALAR]: %s: dmm_handle[DMM_HANDLE_YCC_FULL] error` | 2 | `0x4380b902`, `0x4380b9f6` | `0x4380b8d4`, `0x4380b9c4` |
| 17 | `0x43cb0829` | `0x43cb0837` | `[CAM_SCALAR]: %s: Alloc SDS YC error` | 1 | `0x4380b93c` | `0x4380b8d4` |
| 18 | `0x43cb084e` | `0x43cb085c` | `[CAM_SCALAR]: %s fatal` | 1 | `0x4380baca` | `0x4380b9c4` |
| 19 | `0x43cb0865` | `0x43cb0873` | `[CAM_SCALAR]: %s: No YCC_FULL handle` | 1 | `0x4380bb58` | `0x4380bb30` |
| 20 | `0x43cb088a` | `0x43cb0898` | `[CAM_SCALAR]: %s: No RAW_FULL handle` | 1 | `0x4380bc02` | `0x4380bbd8` |
| 21 | `0x43cb08af` | `0x43cb08bd` | `[CAM_SCALAR]: %s: dmm_handle[%d] error` | 2 | `0x4380be0c`, `0x4380bf34` | `0x4380bdbc` |
| 22 | `0x43cb08d6` | `0x43cb08e4` | `[CAM_SCALAR]: %s: ShareCheck error` | 1 | `0x4380be30` | `0x4380bdbc` |
| 23 | `0x43cb08f9` | `0x43cb0907` | `[CAM_SCALAR]: %s: p_newparam error` | 1 | `0x4380be52` | `0x4380bdbc` |
| 24 | `0x43cb091c` | `0x43cb092a` | `[CAM_SCALAR]: %s: outImage error` | 1 | `0x4380be88` | `0x4380bdbc` |
| 25 | `0x43cb093d` | `0x43cb094b` | `[CAM_SCALAR]: %s: dmm_handle[%d] Share error` | 2 | `0x4380bf66`, `0x4380bfa6` | `0x4380bdbc` |
| 26 | `0x43cb096a` | `0x43cb0978` | `[CAM_SCALAR]: %s: Share error` | 1 | `0x4380bfce` | `0x4380bdbc` |
| 27 | `0x43cb0a03` | `0x43cb0a11` | `[CAM_SCALAR]: %s: ExposureCount parameter value is invalid.` | 1 | `0x4380c360` | `0x4380c344` |
| 28 | `0x43cb0a3f` | `0x43cb0a4d` | `[CAM_SCALAR]: %s: RecordCount parameter value is invalid.` | 1 | `0x4380c388` | `0x4380c344` |
| 29 | `0x43cb0a79` | `0x43cb0a87` | `[CAM_SCALAR]: %s: CapMode is not CAP_SINGLE` | 1 | `0x4380c3d6` | `0x4380c344` |
| 30 | `0x43cb0aa5` | `0x43cb0ab3` | `[CAM_SCALAR]: Open Error` | **0** | — (muerta) | — |
| 31 | `0x43cb0abe` | `0x43cb0acc` | `[CAM_SCALAR]: %s: AllocNewWait error` | **0** | — (muerta) | — |
| 32 | `0x43cb0ae3` | `0x43cb0af1` | `[CAM_SCALAR]: %s: %d Free error` | **0** | — (muerta) | — |
| 33 | `0x43cb0b5e` | `0x43cb0b6c` | `[CAM_SCALAR]: %s: input image is null.` | 1 | `0x4380c64e` | `0x4380c638` |
| 34 | `0x43cc679a` | `0x43cc67a8` | `[CAM_SCALAR]: RecordCount Unmatch! : remain %d` | 1 | `0x438bbe62` | `0x438bbe4c` |

**Total: 47 sitios en 14 funciones.** Las 34 cadenas ocupan **dos bloques** en `.rodata`:
33 consecutivas (`0x43cb045a`–`0x43cb0b6c`, intercaladas con los nombres `req_*`/`Start_*`)
y **1 aislada** (`0x43cc679a`), en la zona de `ImageParamCapture_SyncBranch.cpp`.

**Las 3 cadenas muertas** tienen **también muerto su gemelo** (`+14`: 0 referencias PIC y 0
punteros absolutos). Sus dos caminos de código, en la A6000, se registran con **otra**
etiqueta: `[IMAGING_CAP]: Open Error` (`0x43cb0b03`, sitio `0x4380c4fc`, que usa el texto
compartido `Open Error` `0x43cbd3a5`) y `[IMAGING_CAP]: %s: AllocNewWait error`
(`0x43cb0b1d`, sitio `0x4380c52a`, texto compartido `0x43ced0cf`). En la **A7S** el mismo
código (`0x4382ea7a`) registra `%s: AllocNewWait error` (`0x43cb2745`) **sin** etiqueta y
con **un solo** logger (`0x438f7114`). `%s: %d Free error` está muerta en **ambos**.

---

## 4. Ficheros fuente

| fichero | vaddr | referenciado desde | atribución |
|---|---|---|---|
| `HAPI_Filter_TBOX.cpp` | `0x43cb07b7` | `0x4380b79a` (traza `[IMAGING]: FATAL! %s:%d` con **línea 99** = `0x63`) | **dentro** del bloque A (`Start_Miniature` `0x4380b6bc` y siguientes) |
| `CS_Command.cpp` | `0x43cb0b85` | `0x4380c80e` (traza `[IMAGING]: FATAL! %s:%d` con **línea 112** = `0x70`) | inmediatamente **después** del bloque A |
| `ImageParamCapture_SyncBranch.cpp` | `0x43cc6779` | `0x438bbc50` | **bloque B** (`0x438bbe4c`, `RecordCount Unmatch!`) |

* El **fichero propio del bloque A no está embebido** en él: la referencia a fichero más
  próxima por detrás es `wrapper/Face.cpp` (`0x43cb03e3`, sitio `0x4380a33a`) y la más
  próxima por delante es `HAPI_Filter_TBOX.cpp`. → **NO VERIFICADO** cuál es el `.cpp` del
  despachador `0x4380a688`.
* En la **A7S** y el **A6300** la estructura es idéntica: `HAPI_Filter_TBOX.cpp` referenciado
  en `0x4382e126` (A7S) / `0x438c9b02` (A6300) y `CS_Command.cpp` en `0x4382ebbe` /
  `0x438ca6d2`. Es el **mismo bloque de código**, no uno nuevo.

---

## 5. El mecanismo de «logging» de la fw3.21 (patrón S128/S130)

En cada uno de los 47 sitios, la A6000 hace **dos** llamadas:

```
0x4380a864  ldr   r3, [pc, #0x104]     ; 'req_filter_miniature'  (el %s)
0x4380a866  movs  r0, #5               ; ID DE MÓDULO = 5
0x4380a868  movs  r1, #6               ; NIVEL = 6
0x4380a86a  movs  r2, #1               ; flag
0x4380a86c  add   r3, pc               ; -> 0x43cb06d3
0x4380a86e  str   r3, [sp]             ; %s en la pila
0x4380a870  ldr   r3, [pc, #0xfc]
0x4380a872  add   r3, pc               ; -> 0x43cb0588 '[CAM_SCALAR]: %s: input image and sdsYC is invalid.'
0x4380a874  bl    #0x4380a5d0          ; TRAZA NUEVA (logger de módulo)
0x4380a878  ldr   r0, [pc, #0xf8]      ; pool -> 0x43cb0596 '%s: input image and sdsYC is invalid.'
0x4380a87a  ldr   r1, [pc, #0xfc]      ; pool -> 0x43cb06d3 'req_filter_miniature'
0x4380a87c  add   r0, pc
0x4380a87e  add   r1, pc
0x4380a880  bl    #0x43902718           ; TRAZA VIEJA (logger global), texto sin prefijo
```

* **Logger de módulo** `0x4380a5d0` (y sus copias `0x4380c28c`, `0x4380c434`, `0x4380c74c`,
  `0x4380b610`, `0x438bbda0`): firma `(u16 módulo, u16 nivel, u16 flag, const char *fmt, …)`;
  reserva el mensaje con `osal_try_valloc_msg` `0x435612d0` (tamaño `0x9a`), escribe
  `módulo` en `msg+2`, `nivel` en `msg+4`, `flag` en `msg+0x10`, formatea con
  `0x439c5a04`/`0x439c5004` y envía con `osal_snd_msg` `0x4356120c`/`0x43561244`.
* **Logger global (viejo)** `0x43902718`: el que usan las 47 trazas gemelas.
* En los **47 sitios**: `módulo = 5`, `nivel = 6`, `flag = 1`. Verificado mecánicamente con
  el patrón de bytes `movs r0,#5` / `adds r0,#5` / `adds r0,#0x20`, `movs r1,#6` /
  `adds r1,#6` y `movs r2,#1` / `adds r2,#1` / `mov r2,r6` en la ventana de 40 B previa al
  sitio (`analysis/s179_cam_scalar/scan_levels_bytes.py`: **44/47**; los 3 restantes se
  resolvieron a mano: `0x4380a70a` → `adds r0,#0x20` sobre el código de error `-27` → `5`;
  `0x4380c360` y `0x4380c388` → `mov r2,r6` con `r6 = p[0] = 1` → flag `1`).
  El orden de las tres constantes varía de un sitio a otro (`0x4380b074` las fija en el
  orden inverso).
* **La A7S sólo hace la llamada vieja.** En `0x4382d4c4` (el mismo `HAPI Manager:Recieve
  error`):

  ```
  0x4382d4c4  ldr   r0, [pc, #0x278]    ; pool 0x4382d740 = 0x00484d6d
  0x4382d4c6  add   r0, pc              ; -> 0x43cb2237 'HAPI Manager:Recieve error'
  0x4382d4c8  b     #0x4382da62
  ```

  → **mismo código, una sola traza, sin prefijo**.

---

## 6. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

### 6.1 Tokens y textos

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| ocurrencias del token `[CAM_SCALAR]` | **34** | **0** | **0** |
| textos interiores (núcleo sin prefijo) presentes | — | **34 / 34** | **34 / 34** |
| gemelo exacto en `+14` | **34 / 34** | — | — |
| código equivalente | bloque A `0x4380a688`–`0x4380c6f4`, bloque B `0x438bbe4c` | bloque A `0x4382d49c`–`0x4382e…`, `HAPI Manager` `0x4382d49c` | bloque A `0x438c8d…`–`0x438ca…` (`HAPI Manager:Recieve error` `0x438c8e3a`) |
| ficheros `HAPI_Filter_TBOX.cpp` / `CS_Command.cpp` | sí / sí | sí / sí | sí / sí |
| tabla `MSG_ID` `0x5001`–`0x5017` | sí (23 entradas, `tbh` en `0x4380a72c`) | sí (estructura idéntica) | sí (estructura idéntica) |
| nombres `req_*` / `Start_*` | 29/29 | 29/29 | 29/29 (salvo `req_image_clone` → `req_yc_image_parse`) |

### 6.2 Diferencias de **contenido** entre firmware (no de etiqueta)

* La A6300 **no** tiene `req_image_clone` sino `req_yc_image_parse` (`0x43dcb670`).
* La A6300 sustituye dos mensajes: en lugar de `%s: YC(develop) DMM allocation error[%d].`
  tiene `%s: Develop(RAW->YC) fail.` (`0x43dcb8dc`), y en lugar de `%s: SdsYc error` tiene
  `%s: invalid parameter on simple develop.` (`0x43dcb91b`).
* La A7S añade `Err_Develop_Sequence` (`0x43cb2429`), que no existe en la A6000.

### 6.3 Lectura del diferencial

Lo **propio de la fw3.21 de la A6000** es **sólo la instrumentación**:

1. el prefijo literal `[CAM_SCALAR]: ` (14 B) antepuesto a 34 mensajes;
2. una **traza duplicada** con *id de módulo* (5) y *nivel* (6) emitida por un logger de
   módulo propio, mientras la traza vieja (sin prefijo) **sigue emitiéndose** por el
   logger global;
3. tres literales `[CAM_SCALAR]` **muertos** (residuos de compilación) y tres caminos de
   error que en la A6000 se registran con la etiqueta `[IMAGING_CAP]` en lugar de `[CAM_SCALAR]`.

**El código del subsistema HAPI de la cámara no cambia**: misma tabla de `MSG_ID`, mismos
ficheros, mismos nombres de método, mismos mensajes. Es el mismo patrón que S177 midió para
`[CAM_FUNC_MGR]` (allí con prefijo de 16 B y fichero/línea; aquí con prefijo de 14 B y
**sin** fichero/línea).

**S128 ya lo había clasificado** como `RENOMBRADO` (33/34 núcleos comunes en la A7S); este
hito lo **refina a 34/34** y explica el mecanismo exacto (prefijo de 14 B + gemelo intacto
en `+14` + traza duplicada).

---

## 7. Verificación y método

* **Regla de referencias**: estricta (canónica del repo). El escaneo **local** de este hito
  (`analysis/s179_cam_scalar/scan_pic_full.py`, misma regla) reproduce **exactamente** el
  mapa global `analysis/s106_imaging_cap/pic_refs_strict_global.json`:
  **17 525 destinos, 0 discrepancias**. No se re-barrió la imagen con otro criterio.
* **Verificación a mano de los pares PIC** (`analysis/s179_cam_scalar/verify_pic.py`,
  Capstone Thumb con `detail=True`): **94/94 correctos** (47 de la traza nueva + 47 de la
  traza gemelo), **0 fallos**, **0 reutilizaciones de registro** entre el `ldr` y el `add`.
  Se comprobó en cada par: (a) el `ldr rX,[pc,#imm]` **más cercano** del mismo registro,
  (b) el literal del pool, (c) `destino = literal + (add + 4)`, (d) que el registro no se
  reescribe entre `ldr` y `add`.
  Ejemplo (sitio `0x4380a872`): `ldr r3,[pc,#0xfc]` @`0x4380a870` → pool `0x4380a970` =
  `0x004a5d12`; `add r3,pc` @`0x4380a872` → `0x004a5d12 + 0x4380a876 = 0x43cb0588` =
  `'[CAM_SCALAR]: %s: input image and sdsYC is invalid.'` ✓.
* **Gemelos**: comprobado byte a byte que en las **34** cadenas los bytes en `vaddr+14`
  son exactamente el texto sin el prefijo, y que ese texto existe en la A7S y en el A6300.
* **Punteros absolutos**: buscado el patrón de 4 B de las 68 direcciones (34 prefijadas +
  34 gemelos) en los tres firmware → **0 coincidencias** en todos los casos.
* **Scripts del hito** (`analysis/s179_cam_scalar/`): `scan_strings.py`, `scan_pic.py`,
  `scan_pic_full.py`, `scan_twins.py`, `scan_funcmap.py`, `scan_region_strings.py`,
  `scan_region2.py`, `scan_diff_names.py`, `scan_acronym.py`, `scan_absptr.py`,
  `scan_levels3.py`, `scan_levels_bytes.py`, `scan_levels_flow.py`, `scan_calls.py`, `scan_tbh.py`, `scan_negativo.py`, `scan_filenames.py`,
  `verify_pic.py`, `dasm.py`, `dasm2.py`, `dump_range.py`, `dump_block.py`, `resolve.py`,
  `build_json.py`.
* **Tests**: `tests/test_s179_cam_scalar.py` (comprueban bytes reales: si cambia una
  dirección, un texto o un conteo, el test falla).

---

## 8. Interés para la línea del obturador

**Negativo acotado: el módulo `[CAM_SCALAR]` NO habla de obturación, de obturador
electrónico, de lectura del sensor de imagen ni de tiempos de exposición.**

Comprobación literal sobre las 34 trazas (`analysis/s179_cam_scalar/scan_negativo.py`):

| término | coincidencias |
|---|---|
| `shutter`, `silent`, `curtain`, `electro`, `mech`, `obtur` | **0** |
| `expos` | **1** → `ExposureCount parameter value is invalid.` (`0x43cb0a03`) |
| `iso`, `apert`, `sensor`, `readout` | **0** |
| `shut`, `svd`, `shd`, `spl`, `frame`, `imager`, `drive` | **0** |
| `brack`, `sweep`, `interval`, `still`, `movie`, `focus` | **0** |
| `sync`, `vsync`, `scan`, `ae `, `af ` | **0** |

Matices que **sí** conviene registrar (son de **nivel de secuencia**, no de mecanismo):

* `ExposureCount` (`0x43cb0a03`), `RecordCount` (`0x43cb0a3f`), `CapMode is not CAP_SINGLE`
  (`0x43cb0a79`) y `RecordCount Unmatch! : remain %d` (`0x43cc679a`) son **parámetros de la
  secuencia de captura** validados en `0x4380c344`: `ExposureCount` debe ser 1,
  `RecordCount` ≤ 5 y `CapMode` = `CAP_SINGLE`.
  Son **órdenes de alto nivel** de la API HAPI; **no** son parámetros del obturador
  (ni velocidad, ni cortina, ni tiempo de lectura del sensor).
* El «develop» que hace el módulo (`req_filter_develop`, `Start_Develop`) es la
  **conversión software RAW→YC** (`copyStdYc`, `SdsYc`, `YC(develop) DMM allocation`):
  **no** toca el imager ni el obturador.

⇒ **Para la línea del obturador: S51 (A = NO / B = NO / C = NO) se mantiene.** Este módulo
no aporta ninguna ruta al obturador. Su valor para la línea es *indirecto*: documenta que
la capa HAPI de la A6000 sólo admite `CAP_SINGLE` con `ExposureCount = 1` y `RecordCount ≤ 5`
en la secuencia especial, es decir, **la API de imagen no es un camino alternativo para
disparar con el obturador electrónico**.

---

## 9. NO VERIFICADO / abierto

1. **Significado de la sigla `CAM_SCALAR`** — NO VERIFICADO. No hay base textual
   (34 apariciones = 34 trazas; `CamScalar`/`cam_scalar` = 0). La hipótesis del enunciado
   («capa de cámara del acelerador escalar SA») queda **refutada** por §1; **no se propone
   ninguna expansión alternativa**.
2. **Fichero fuente propio del bloque A** (`0x4380a688`–`0x4380c6f4`) — NO VERIFICADO: no
   está embebido; los nombres de fichero más próximos son `wrapper/Face.cpp`
   (`0x4380a33a`), `HAPI_Filter_TBOX.cpp` (`0x4380b79a`) y `CS_Command.cpp` (`0x4380c80e`).
3. **RTTI/clase propia del módulo** — NO VERIFICADO: no hay ninguna clase RTTI
   referenciada por PIC desde la zona del módulo.
4. **Significado de `SDS` / `sdsYC`** — Parcialmente verificado: existe el parser
   `[ADF]AdfSdsYcParser` (`0x43c2ced3`), lo que apunta a *Standard Data Structure*; la
   acronym `SDS` en sí **no se desarrolla** en ninguna cadena → NO VERIFICADO.
5. **Significado de `stdYc` / `stdYcHandle`** — NO VERIFICADO (existen convertidores
   `[SFRA] stdYc2sfrYc_*` en `0x43ce7254`–`0x43ce73c2`, pero no hay definición del tipo).
6. **Tabla de `MSG_ID` `0x5001`–`0x5017`**: los **23 destinos** de la tabla `tbh` están
   medidos y las 15 peticiones/respuestas que se loguean están identificadas, pero **la
   equivalencia exacta `MSG_ID` ↔ nombre de petición NO está establecida** para los 6 ids
   whose destino es la rama por defecto (`0x4380ae0e`) o la rama «imagen inválida»
   (`0x4380adf8`). NO VERIFICADO.
7. **Los 3 literales muertos** (`0x43cb0aa5`, `0x43cb0abe`, `0x43cb0ae3`): se ha verificado
   que **ni ellos ni sus gemelos** tienen referencia (0 PIC, 0 punteros absolutos) y que los
   caminos correspondientes se registran con `[IMAGING_CAP]` en la A6000; **por qué**
   quedaron en `.rodata` sin usar (compilación de una versión anterior del literal) es
   NO VERIFICADO.
8. **`CapMode`**: se ha verificado la comparación con `CAP_SINGLE` y que la validación la
   hace `0x437dfbd8`; **la lista completa de modos y su relación con S66/S123** es
   NO VERIFICADA.
9. **Relación con la capa `[IMAGING]`/`[IMAGING_CAP]`**: los tres caminos de error que la
   A6000 registra con `[IMAGING_CAP]` están **dentro del bloque A** (`0x4380c4e0`,
   `0x4380c7f8`), pero esos dos loggers usan el **mismo id de módulo 5** con nivel 0/1 y
   formato `[IMAGING]: FATAL! %s:%d` con fichero y línea. El criterio de reparto entre
   `[CAM_SCALAR]` y `[IMAGING_CAP]`/`[IMAGING]` **NO VERIFICADO**.

---

## 10. Revisión del agente principal

*(vacía — pendiente de revisión)*

---

## 11. Reproducir

```bash
.venv/bin/python analysis/s179_cam_scalar/scan_strings.py      # 34 cadenas + diferencial de token
.venv/bin/python analysis/s179_cam_scalar/scan_pic.py           # sitios PIC desde el mapa global
.venv/bin/python analysis/s179_cam_scalar/scan_pic_full.py      # escaneo local estricto (nuevos + gemelos)
.venv/bin/python analysis/s179_cam_scalar/scan_twins.py         # gemelos +14 y diferencial A7S/A6300
.venv/bin/python analysis/s179_cam_scalar/scan_funcmap.py       # mapa función -> traza
.venv/bin/python analysis/s179_cam_scalar/verify_pic.py         # verificación a mano (94 pares)
.venv/bin/python analysis/s179_cam_scalar/scan_tbh.py           # tabla MSG_ID 0x5001-0x5017
.venv/bin/python analysis/s179_cam_scalar/scan_negativo.py      # negativo acotado obturador
.venv/bin/python analysis/s179_cam_scalar/build_json.py         # genera cam_scalar.json
.venv/bin/python -m pytest tests/test_s179_cam_scalar.py -q
```

Ficheros de datos: `strings_raw.json`, `pic_sites.json`, `pic_full.json`, `twins.json`,
`func_map.json`, `pic_verified.json`, `abs_ptrs.json`, `levels.json`, `calls.json`,
`region_strings.json`, `cam_scalar.json`.

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (38 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 34 cadenas `[CAM_SCALAR]` en la A6000 fw3.21 entre `0x43cb045a` y
   `0x43cc679a` (33 en un bloque + 1 aislada); token **34 / 0 / 0** (A6000/A7S/A6300).
2. **Estructura**: **47 sitios** (regla estricta) en **14 funciones**; de las 34 cadenas, **31**
   están en el mapa global y **vivas**, y **3 están muertas** (`0x43cb0aa5`, `0x43cb0abe`,
   `0x43cb0ae3`, cuyos gemelos `+14` también mueren). **0 punteros absolutos** de 4 B. Los
   **94/94 pares PIC** (47 nuevos + 47 gemelos) verificados a mano, **0 fallos** y **0
   discrepancias** contra el mapa canónico (17 525 destinos).
3. **Segunda confirmación de la firma del rewrite de logging**: **34/34** cadenas tienen
   **gemelo exacto en `+14`** (el prefijo `"[CAM_SCALAR]: "` ocupa **14 B** antepuesto y el
   literal original **queda intacto y referenciado** por el logger global `0x43902718`); la
   fw3.21 **duplica** la traza (nueva con logger de módulo `0x4380a5d0`, **id de módulo 5**,
   **nivel 6**, flag 1 + la vieja). Es el mismo mecanismo que en **S177** (prefijo de 16 B) →
   **el prefijo no tiene longitud fija: se ajusta al nombre del módulo**.
4. **Hipótesis del enunciado REFUTADA (bien hecho)**: **no** es la capa del acelerador escalar
   «SA» — **0 llamadas** al rango `NS_SCALAR_INFRA` (`0x43990000`–`0x439c0000`, donde viven
   `[SAD]`/`[SFRA]`/`[SFRS]`) y **0** referencias a `sa_func_*`; todas las cadenas `SCALAR`/
   `Scalar` de la A6000 (88 + 261) son de `NS_SCALAR_INFRA`. La sigla **se deja sin desarrollar**
   (`CAM_SCALAR` = 34 apariciones = 34 trazas; `CamScalar`/`cam_scalar` = 0).
5. **Qué es**: la **capa HAPI de imagen** de la cámara: despachador `0x4380a688` con `tbh` de
   **23 entradas** (base `0x4380a72c`) → `MSG_ID` **0x5001–0x5017**; `SetSpecialSequence`
   `0x4380c344` valida `ExposureCount`=1, `RecordCount`≤5 y `CapMode`=`CAP_SINGLE`; handles DMM
   `YCC_FULL`/`RAW_FULL`; ficheros `HAPI_Filter_TBOX.cpp` `0x43cb07b7` (línea 99),
   `CS_Command.cpp` `0x43cb0b85` (línea 112), `ImageParamCapture_SyncBranch.cpp` `0x43cc6779`.
6. **Es ETIQUETADO, no contenido nuevo (refina a S128)**: los **núcleos** sin prefijo están
   presentes **34/34** en la A7S y **34/34** en el A6300 (mismo código: A6000 `0x4380a688`, A7S
   `0x4382d49c`, A6300 `0x438c8dxx`; mismos ficheros y mismos 29 nombres `req_*`/`Start_*`/`Check*`).
   Los cambios de contenido **propios del A6300** son `%s: Develop(RAW->YC) fail.`,
   `%s: invalid parameter on simple develop.` y `req_image_clone` → `req_yc_image_parse`.
7. **Negativo acotado**: 0 de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/
   `readout`/`shut`/`svd`/`shd`/`spl`/`frame`/`imager`/`drive`/`brack`/`sweep`/`still`/`movie`/
   `focus`/`iso`/`apert`/`sync`/`vsync`/`scan`; el único `expos` es `ExposureCount` → **sin efecto
   en S51** (A/B/C = NO).
