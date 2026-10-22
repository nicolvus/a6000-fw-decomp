# S164 — el módulo `[CAMERA_IS]` (17 trazas): la capa de estabilización de imagen de la cámara

> Hito de la **línea de ingeniería inversa general**. Solo lectura de bytes del
> `av-cam.bin` de la **A6000 fw3.21** (`analysis/rea-independent/input/av-cam.bin`),
> con comparación contra la **A7S fw3.20** y el **A6300 fw2.01**.
> Convención: `vaddr = 0x43541000 + file_offset`.
> Referencias a cadenas: **regla estricta** (canónica del repo), ver
> `analysis/s106_imaging_cap/pic_xref_methodology.md`.
>
> VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

## 1. Resumen / veredicto

**`[CAMERA_IS]` es la etiqueta de traza del subsistema de estabilización de imagen (IS)
de la cámara** —no un módulo de diagnóstico ni un fichero de calibración— y **sí es la capa
que aplica la estabilización**: coordina el recurso RC de estabilización (alimentación EIS
y rejilla horizontal del sensor), lee el giroscopio, aplica la corrección de distorsión y
se sincroniza con la montura del objetivo y con la secuencia de exposición.

Cifras (todas VERIFICADAS, regla estricta):

| magnitud | valor |
|---|---|
| cadenas con el token `[CAMERA_IS]` | **17** (17 textos distintos) |
| sub-etiquetas | `MOUNT` 5, `DIST` 5, `AS` 3, `EIS` 4 |
| sitios de emisión (PIC) | **21** |
| cadenas referenciadas | **17 / 17** (0 muertas) |
| funciones emisoras | **13** |
| envoltorios de traza (copias del logger) | 7 (uno o dos por sub-capa) |

**Relación con S70**: S70 ya había localizado 12 de las 17 trazas y 12 de las 13 funciones.
S164 añade las **5 trazas que S70 no listaba** (`0x43c98dde`, `0x43c98e80`, `0x43c98ebc`,
`0x43c9a352`, `0x43c9a3e3`) y la **13.ª función** `0x4371e4cc` (máquina de estados del
estabilizador "AS", sitio `0x4371e738`). Los 13 contenedores coinciden con el mapa manual
de S70 → **validación cruzada** de la regla estricta en este módulo.

## 2. Qué es exactamente `[CAMERA_IS]` (evidencia)

1. **Cuatro sub-capas con prefijo propio**, cada una con su propia categoría de log
   (valor inmediato cargado en `r1` justo antes del puntero al formato, y `r0 = 0xf`
   constante):

   | sub-capa | categoría `r1` | envoltorio(s) de traza | contenido |
   |---|---|---|---|
   | `[DIST]` | **1** | `0x436ea3c4` | corrección de distorsión (parámetros, conversión de posiciones, tag RAW) |
   | `[EIS]` | **2** | `0x437026ac`, `0x437041dc` | estabilización electrónica: alimentación, rejilla y giroscopio |
   | `[AS]` | **4** | `0x436febc4`, `0x4371e39c` | estabilizador "activo" (`[STABILIZER]`): colas OSAL y parámetro UPM |
   | `[MOUNT]` | **6** | `0x436ea224`, `0x43705cb8` | interfaz IS ↔ montura de objetivo (servicio `LENS_MOUNT`) |

   Los envoltorios son el mismo logger duplicado (formatea con `vsnprintf` y publica un
   mensaje OSAL: `osal_try_valloc_msg` `0x435612d0`, tamaño `0x9a`, `memset` `0x439c5a04`).

2. **El módulo habla con el recurso RC de estabilización**: las cadenas nombran literalmente
   `rcct_SetStblzPower` y `rcct_SetStblzGridH`, y los dos "callbacks" de error son
   precisamente los que se disparan al fallar esas llamadas (§5, funciones `0x43702dac` y
   `0x43704d90`). Verificado **dentro de las funciones destino**: la cadena
   `rcct_SetStblzPower` `0x43ce190c` está referenciada en el sitio `0x439417ee`, dentro de
   la función `0x439417c8` a la que el módulo llama (`bl 0x439417c8` en `0x43702df2`); lo
   mismo con `rcct_SetStblzGridH` `0x43ce186a` → sitio `0x4394183a` dentro de `0x43941814`
   (`bl 0x43941814` en `0x43702e0c`). Ambas funciones RC viven en `src/api_rc.cpp`
   (`0x43ce15d1`).

3. **Lee el giroscopio**: `[CAMERA_IS][EIS]: GyroAD[p],GyroAD[y], %d, %d` (`0x43c9a324`) se
   emite en `0x437046a4` con los dos valores leídos por `0x4370665c` (que llama a
   `0x436eace0`, acceso ADC). La traza va precedida de un test de bit de depuración
   (`ldrb r3,[r6,#1]; tst.w r3,#1` en `0x437047f0`).

4. **Se sincroniza con la montura del objetivo**: el módulo se registra como cliente del
   servicio cuyo nombre literal es **`LENS_MOUNT`** (`0x43c9a39c`, referenciado en el sitio
   `0x43705a86`; y `0x43c9a58e` en `0x4370727a`). En `0x43707270` se compara el nombre del
   servicio con `"LENS_MOUNT"` (`movs r2,#0xa` = longitud 10, `blx 0x439c5d18`) y se fija un
   byte de estado global.

5. **Escribe un fichero de calibración por lente**: `/mnt/FILE_IS_%04x.dat` (`0x43c9a535`),
   con contador `u16` global en `0x43f65d3c` (verificado a mano: `ldrh r3,[r2]` /
   `adds r1,r3,#1` / `strh r1,[r2]` en `0x4370716c`–`0x43707170`), cabecera de 4 B y texto de
   hasta `0x80` B con la plantilla `"\nCh.0/00,01,02,03,04,05,06,07,Ch.1/00,01,…,Count,\n"`
   (`0x43c9a54b`). La escritura se pide al servicio de ficheros por mensaje OSAL.

6. **Se invoca desde la secuencia de exposición**: la función `0x43702dac` (EIS) es llamada
   desde `0x4354a97c`, dentro de la función `0x4354a678` de la capa `[CAMERA_MAIN_SYNC]`,
   justo tras la traza `[CAMERA_MAIN_SYNC]: Sync_EndExpose: DIST_RSLT_NG
   MakeDistortionCorrectionParamForSync error!` (`0x43cb0f80`). Y la otra vía
   (`0x43704d90`) se llama desde `0x4354e51c`, en la función `0x4354d740`, junto a la traza
   `b ee EIS_RC1V_SetPower` (`0x43cb2b9e`) y a `[CAMERA_MAIN_SYNC]: Sequence_HS:
   RC_ERR:0x%02x rcct_SetAicParam RCV error!`.

## 3. Las 17 trazas

Dirección = dirección de la cadena; sitio = dirección del `add rX,pc` (regla estricta);
función = contenedor (prólogo `push {…,lr}` más cercano, con test de alcanzabilidad lineal).

| # | cadena | sub-capa | sitio(s) | función | qué informa |
|---|---|---|---|---|---|
| 1 | `0x43c98da6` `[CAMERA_IS][MOUNT]: [Error] IS_LensMountExpStartCB (%x)` | MOUNT | `0x436ea2e6` | `0x436ea2d0` | código de mensaje **no aceptado**: el callback sólo admite `0xF0`/`0xF1` (`sub.w r3,r0,#0xf0; cmp r3,#1`) |
| 2 | `0x43c98dde` `[CAMERA_IS][MOUNT]: [Error] IS_LensMountExpStartCB - checkData` | MOUNT | `0x436ea312` | `0x436ea2d0` | el payload de 25 B (`0x19`) no valida (`bl 0x43ad9d58`) |
| 3 | `0x43c98e1d` `[CAMERA_IS][DIST]: ERR:MakeDistCorPrm prm=null` | DIST | `0x436ea492` | `0x436ea470` | `prm` nulo al construir los parámetros de corrección de distorsión |
| 4 | `0x43c98e4d` `[CAMERA_IS][DIST]: ERR:CnvPosInvDistCorr prm=null` | DIST | `0x436ea53c` | `0x436ea50c` | `prm` nulo al convertir una posición con la corrección inversa |
| 5 | `0x43c98e80` `[CAMERA_IS][DIST]: ERR:CnvPosInvDistCorr prm=inv1 (%d, %d)` | DIST | `0x436ea576` | `0x436ea50c` | posición fuera de los límites de la zona válida (comparación de rangos) |
| 6 | `0x43c98ebc` `[CAMERA_IS][DIST]: WRN:CnvPosInvDistCorr prm=inv2 (%d, %d) ` | DIST | `0x436ea600` | `0x436ea50c` | aviso: la corrección inv2 cambia el resultado |
| 7 | `0x43c98ef9` `[CAMERA_IS][DIST]: ERR:MakeDistRawAppliTag prm=null` | DIST | `0x436ea670` | `0x436ea65c` | `prm` nulo al generar el *tag* de aplicación sobre el RAW |
| 8 | `0x43c9a1f3` `[CAMERA_IS][AS]: [STABILIZER][AS][osal_reg_sync_msg_queue_cb] %x` | AS | `0x436fed7a`, `0x436fed9c` | `0x436fecbe` | código de error devuelto al registrar **dos** colas de mensajes síncronos (`0x435612b4`) |
| 9 | `0x43c9a234` `[CAMERA_IS][AS]: [STABILIZER][AS][upm_get_hcrn_ura] %x` | AS | `0x436ff098`, `0x4371e738` | `0x436fee80`, `0x4371e4cc` | error de la consulta UPM `upm_get_hcrn_ura` (`0x43561228`, ranura de vtable `+0x1d8`) |
| 10 | `0x43c9a26b` `[CAMERA_IS][AS]: [STABILIZER][AS][osal_unreg_sync_msg_queue_cb] %x` | AS | `0x436fface`, `0x436ffaec` | `0x436ffab4` | error al desregistrar las dos colas (`0x43561298`) |
| 11 | `0x43c9a2b2` `[CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzPower error!` | EIS | `0x43702e02`, `0x43704db0` | `0x43702dac`, `0x43704d90` | error de `rcct_SetStblzPower` (`0x439417c8`) — alimentación del EIS |
| 12 | `0x43c9a2eb` `[CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzGridH error!` | EIS | `0x43702e1c` | `0x43702dac` | error de `rcct_SetStblzGridH` (`0x43941814`) — rejilla horizontal del EIS |
| 13 | `0x43c9a324` `[CAMERA_IS][EIS]: GyroAD[p],GyroAD[y], %d, %d` | EIS | `0x43704802` | `0x437046a4` | valores **ADC del giroscopio** (p = pitch, y = yaw), sólo si el bit de depuración está activo |
| 14 | `0x43c9a352` `[CAMERA_IS][EIS]: %x, %d, %d` | EIS | `0x43704c02` | `0x437046a4` | contador + 2 valores del bloque EIS (el contador se incrementa en `0x43704c0a`) |
| 15 | `0x43c9a3a7` `[CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyroCB (%x)` | MOUNT | `0x43705d7a` | `0x43705d64` | código de mensaje no aceptado en el callback de panorama (sólo `0xF0`/`0xF1`) |
| 16 | `0x43c9a3e3` `[CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyroCB - checkData` | MOUNT | `0x43705db6` | `0x43705d64` | el payload de 38 B (`0x26`) no valida |
| 17 | `0x43c9a426` `[CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyro (%x)` | MOUNT | `0x43705e28` | `0x43705dd0` | el envío al objetivo del paquete de panorama devolvió `1` |

> Las 5 cadenas de la sub-capa `[DIST]` terminan en `\n` en el binario (no se ve en la tabla);
> el texto exacto está en `camera_is.json` (`text`) y en los tests.

### Verificación manual de los pares PIC (regla metodológica §2)
Los 17 pares `ldr rX,[pc,#imm]` + `add rX,pc` se comprobaron **a mano** (desensamblando y
resolviendo el *pool* de literales), no sólo con el escáner: **17/17 correctos**. Ejemplos:

| ldr | pool | W | add | destino | texto |
|---|---|---|---|---|---|
| `0x436ea2dc` | `0x436ea328` | `0x005aeabc` | `0x436ea2e6` | `0x43c98da6` | `IS_LensMountExpStartCB (%x)` |
| `0x436ea48a` | `0x436ea500` | `0x005ae987` | `0x436ea492` | `0x43c98e1d` | `MakeDistCorPrm prm=null` |
| `0x436fed70` | `0x436fee40` | `0x0059b475` | `0x436fed7a` | `0x43c9a1f3` | `osal_reg_sync_msg_queue_cb %x` |
| `0x43702df8` | `0x43702e38` | `0x005974ac` | `0x43702e02` | `0x43c9a2b2` | `rcct_SetStblzPower error!` |
| `0x437047f8` (`ldr.w`) | `0x43704ca0` | `0x00595b1e` | `0x43704802` | `0x43c9a324` | `GyroAD[p],GyroAD[y], %d, %d` |
| `0x43705d70` | `0x43705dc4` | `0x00594629` | `0x43705d7a` | `0x43c9a3a7` | `IS_LensMountPanoramaGyroCB (%x)` |

## 4. Mapa función → traza (13 funciones) y llamadores

| función | trazas | sub-capa | llamadores `bl` directos | contexto del llamador |
|---|---|---|---|---|
| `0x436ea2d0` | 1, 2 | MOUNT | **ninguno** | callback registrado (indirecto) |
| `0x436ea470` | 3 | DIST | `0x437d34a2`, `0x43af5942` | `0x437d3484` = capa `[CAMERA_MAIN_TC]` (DIST) |
| `0x436ea50c` | 4, 5, 6 | DIST | `0x43810a0c`, `0x439f3030`, `0x439f355e`, `0x439f4e1a`, `0x439f5054`, `0x439f54bc`, `0x439f54c8`, `0x439f58bc`, `0x439f58ce`, `0x439f59f6`, `0x439f5a04`, `0x43b71fe6`, `0x43b71ff2` | `0x438106ec` = `[CAMERA_MAIN_SYNC]` (`Sync_Cam_Setting: DIST_RSLT_NG ConvertPosInvDistor…` `0x43cb10f7`); `0x439f3000`–`0x439f57a0` = módulo **`[IDT]`/`[IDT_OPD]`** (`Invlid distortion area` `0x43cf3588`, `GetIDTSA Unknown aspect` `0x43cf3306`) |
| `0x436ea65c` | 7 | DIST | `0x437d76b4` | `0x437d765c` = `[CAMERA_MAIN_TC]` (`TC:DIST:Err:WriteRawAppliTagValue1/2` `0x43ca8816`/`0x43ca884b`) |
| `0x436fecbe` | 8 | AS | **ninguno** | registro de las dos colas de sincronización |
| `0x436fee80` | 9 | AS | **ninguno** | inicialización del estabilizador |
| `0x436ffab4` | 10 | AS | `0x43b7c71c` | `0x43b7c700` (región sin trazas propias) |
| `0x43702dac` | 11, 12 | EIS | `0x4354a97c` | `0x4354a678` = **`[CAMERA_MAIN_SYNC]`**, tras `Sync_EndExpose…` `0x43cb0f80` |
| `0x437046a4` | 13, 14 | EIS | `0x4371f6a6`, `0x4371f6ec` | `0x4371f658` (propio del subsistema IS) |
| `0x43704d90` | 11 | EIS | `0x4354e51c`, `0x438159ba`, `0x43815aa6` | `0x4354d740` = `[CAMERA_MAIN_SYNC]`, junto a `b ee EIS_RC1V_SetPower` `0x43cb2b9e` y `Sequence_HS: RC_ERR…` `0x43cb2c17`; `0x4381592c`/`0x43815a2a` = `Sequence_HSRecGolfshot` |
| `0x43705d64` | 15, 16 | MOUNT | **ninguno** | callback de panorama registrado (indirecto) |
| `0x43705dd0` | 17 | MOUNT | `0x43b7c492` | `0x43b7c470` |
| `0x4371e4cc` | 9 | AS | `0x43b7c5ac` | `0x43b7c4fc` — máquina de estados del estabilizador "AS" |

### Qué hace cada función (resumen del desensamblado)

* `0x436ea2d0` — **callback de «exposición»**: valida el código de mensaje (`0xF0`/`0xF1`),
  valida el payload de 25 B con `0x43ad9d58`, y si todo es correcto continúa por
  `bl 0x436e91dc` / `b.w 0x436f961c`.
* `0x436ea470` — `MakeDistCorPrm`: comprueba `r0`, `r2` y `r3` no nulos; calcula los
  parámetros de corrección de distorsión y **escribe dos `u16` en el global `0x43f61884` /
  `0x43f61886`** (`strh r3,[r5]` / `strh r4,[r5,#2]` en `0x436ea4ce`/`0x436ea4d0`), además
  de `+0x30` / `+0x32` del objeto destino (`0x436ea4d8`/`0x436ea4e0`).
* `0x436ea50c` — `CnvPosInvDistCorr`: convierte una posición aplicando la corrección
  inversa: `pos -= (coef · (pos − centro)) >> 10` (`muls r3,r1,r3` / `sub.w r2,r2,r3,asr #10`
  en `0x436ea594`/`0x436ea596`), con el coef leído del global `0x43f61886` y el centro de
  `0x43f61884` (`ldrh r1,[r3,#2]` en `0x436ea58e`).
* `0x436ea65c` — `MakeDistRawAppliTag`: construye el *tag* de aplicación del RAW con el
  valor de distorsión (`bl 0x4370061c` en `0x436ea68c`).
* `0x436fecbe` — registra **dos** colas de mensajes síncronos (`0x435612b4`); los nombres de
  cola son punteros a cadenas inicializadas en runtime (`0x43e851e0`, `0x43e851e4`, vacías
  en el blob).
* `0x436fee80` — inicialización del estabilizador: consulta UPM, copia 16 B de respuesta,
  mapea el código de resultado (`cmp r3,#7` en `0x436ff0a4`).
* `0x436ffab4` — desregistra las dos colas (`0x43561298`) y libera el mensaje.
* `0x43702dac` — **EIS**: `rcct_SetStblzPower` (`0x439417c8`) y `rcct_SetStblzGridH`
  (`0x43941814`); el tamaño de rejilla se redondea a múltiplo de 8 (`adds r4,r0,#7` /
  `lsrs r4,r4,#3` en `0x43702db0`/`0x43702db6`); guarda el error en `+0x14c` y el modo en
  `+0x1b8` del bloque EIS (singleton `0x4371f64c`).
* `0x437046a4` — **giroscopio**: canales ADC `[cfg+0x8]` y `[cfg+0x9]` (pivote `p`/guiñada
  `y`), con intercambio si `[cfg+2]&1`; escribe 16 palabras en `+0x1b8 … +0x1e4` del bloque
  EIS; incrementa un contador global tras cada traza `%x, %d, %d`.
* `0x43704d90` — segunda vía de `rcct_SetStblzPower` (precedida de `0x43adc81e`).
* `0x43705d64` — **callback de panorama**: mensaje `0xF0`/`0xF1`, payload de 38 B; si es
  válido compone dos valores de 16 B con los bytes `[1],[2]` y `[3],[4]` del payload y los
  guarda en un global (`strh r1,[r3,#2]` / `strh r2,[r3]` en `0x43705da6`/`0x43705da8`).
* `0x43705dd0` — `IS_LensMountPanoramaGyro`: comprueba el estado (`[obj+8]==3`), prepara un
  paquete de 38 B (`0x43ada044`) y lo **envía al objetivo** por el canal de no-comandos
  (`bl 0x436e1254` = `[MOUNT_DEBUG]: [BL ERR]SendingLensNonCommand ID[%d]`, `0x43c965b9`);
  si el envío devuelve `1` emite la traza de error.
* `0x4371e4cc` — máquina de estados del estabilizador "AS": lee el byte de estado
  `[obj+0x2b]`, consulta UPM (`0x43561228`) y, si el código de resultado es `7`, fija un flag
  (`0x4371e74c`).

## 5. Ficheros fuente

### 5.1 Del propio módulo `[CAMERA_IS]`

**NO_VERIFICADO / no embebido.** Las 17 trazas **no** imprimen `file=%s` y **ningún** nombre
de fichero `.cpp`/`.c` es referenciado por un sitio PIC en las tres regiones de código del
módulo (`0x436e8000`–`0x43708000`, `0x4371d000`–`0x43721000`, `0x43b7b000`–`0x43b7e000`).
Por tanto **no se puede atribuir un fichero fuente propio al módulo** con los bytes
disponibles.

### 5.2 De las capas que el módulo invoca (sí embebidas)

| fichero | cadena | referencia |
|---|---|---|
| `src/api_rc.cpp` | `0x43ce15d1` | `0x439417ee` (dentro de `rcct_SetStblzPower`), `0x4394183a` (`rcct_SetStblzGridH`) |
| `src/RcDriver.cpp` | `0x43ce1b1d` | `0x43945536` (`SetStblzGridHSeqCt` `0x43ce1a40`) |
| `WrapRcctSetStblzPower.cpp` | `0x43c8056e` | `0x43669864`, `0x436698c6`, `0x43669914`, `0x4366993e` |
| `WrapRcctSetStblzGridH.cpp` | `0x43c7fe02` | `0x43666692`, `0x436666dc` |
| `WrapRcctSetStblzParamV.cpp` | `0x43c7fe32` | `0x43666780`, `0x436667cc`, `0x436667f4` |
| `WrapRcctSetStblzVectorH.cpp` | `0x43c7fe91` | `0x436668ac`, `0x43666902`, `0x4366692e` |
| `ModuleDistBase.cpp` | `0x43c80183` | `0x436686ee` … `0x436688ca` (8 sitios) |
| `WrapRcctDistCorrectionH.cpp` / `…V.cpp` / `…Calc.cpp` / `…CalcRotate.cpp` | `0x43c7fc88` / `0x43c7fcb9` / `0x43c7c1b6` / `0x43c7c232` | capa de corrección de distorsión del driver RC |
| `WrapRcctSetDistParam.cpp` / `…Base.cpp` / `…Calc.cpp`, `WrapRcctRcNormalizeDistParam.cpp`, `src/RcNormalizeDist.cpp` | `0x43c8053f`, `0x43c7fdb4`, `0x43c7c379`, `0x43c7fd43`, `0x43ce1d84` | capa de distorsión del driver RC |

Las clases de código neighbours (`Camera::Lens::job_Mount_*AberrationDataHndl`,
`Camera::Lens::ODL::*`, `Camera::Lens::Initialize(UPM_BOOT_FACTOR*)`) están en la misma
región de código que el módulo IS (`0x436fd9de`–`0x436fdb6a`, `0x43c99f7a`–`0x43c9b2f5`),
lo que sitúa al IS **dentro del subsistema de objetivo (`Camera::Lens`) y de la montura**.

## 6. Qué escribe: memoria del sensor, fichero de traza y globales

| destino | dirección / campo | qué se escribe | estado |
|---|---|---|---|
| **recurso RC de estabilización (→ sensor)** | `rcct_SetStblzPower` `0x439417c8` | alimentación del EIS (`EIS_RC1V_SetPower` `0x43cb2b9e` es el rail relacionado) | VERIFICADO el camino; destino físico = INFERENCIA |
| | `rcct_SetStblzGridH` `0x43941814` | **rejilla horizontal del EIS**, tamaño = `(x+7)>>3` (`0x43702db0`/`0x43702db6`) | VERIFICADO el camino; destino físico = INFERENCIA |
| **globales del subsistema IS** | `0x43f61884` / `0x43f61886` (`u16` + `u16`) | centro y coeficiente de corrección de distorsión (fijo 1/1024) | VERIFICADO |
| | `0x43f65d3c` (`u16`) | contador incremental del fichero de calibración por lente | VERIFICADO |
| | `0x43e851dc` / `0x43e851e0` / `0x43e851e4` | handle y nombres de las dos colas de sincronización del AS | VERIFICADO (vacíos en el blob) |
| **bloque EIS** (singleton `0x4371f64c`) | `+0x14c` (código de error), `+0x1b8` (modo), `+0x1bc`…`+0x1e4` (16 palabras de datos del giroscopio/EIS), `+0x24`, `+0x26`, `+0x2c`, `+0x2e`, `+0x30`, `+0x32` | valores de giroscopio y parámetros de distorsión | VERIFICADO |
| **fichero de calibración por lente** | `/mnt/FILE_IS_%04x.dat` `0x43c9a535` | cabecera de 4 B + texto de hasta `0x80` B `"\nCh.0/00,…,Ch.1/00,…,Count,\n"` (`0x43c9a54b`); 2 canales × 8 valores + contador | VERIFICADO (función `0x43707152`) |
| **objetivo (CAIF, canal de no-comandos)** | `0x436e1254` (`SendingLensNonCommand`) | paquete de 38 B con los datos de giroscopio para el barrido panorámico | VERIFICADO |

> El **patrón de `%2x,%2x,…`** (`0x43c9a460`, 16 valores) está en la misma zona y es el
> volcado hexadecimal de los 16 B que preceden a la ruta del fichero; **NO_VERIFICADO** a qué
> bloque concreto corresponde.

## 7. Relación con `[CAMERA_IS][AS]`, `[EIS]`, `[DIST]` (S70) y con la montura (S66/S133)

* **S70** ya había detectado las tres capas (`AS`, `EIS`, `DIST`) y el fichero por lente.
  S164 **confirma** las 12 funciones de S70, añade la 13.ª (`0x4371e4cc`) y las 5 trazas que
  S70 no listaba. No hay contradicción con S70.
* **Con la montura (S66/S133)**: el módulo IS vive **en el mismo rango de código** que el
  driver de la montura (`BL`) y el de la lente:
  * `.rodata`: `0x43c98da6`–`0x43c9a426`, entre las trazas `[MOUNT_*]` (`0x43c98621`–) y las
    de `Camera::Lens` (`0x43c99f7a`–`0x43c9b2f5`).
  * `.text`: `0x436ea2d0`–`0x43707152`, junto al bucle principal de la tarea BL
    (`0x436e5e3c`–`0x436e7bf0`, S66/S133) y a `Camera::Lens::job_Mount_*`.
  * El módulo se registra como cliente del servicio **`LENS_MOUNT`** y recibe de él dos
    callbacks (`IS_LensMountExpStartCB`, `IS_LensMountPanoramaGyroCB`) con códigos `0xF0`/`0xF1`.
  * A la inversa, `IS_LensMountPanoramaGyro` **envía** datos al objetivo por el canal de
    no-comandos del driver de la montura.
* **Con el TC (`[CAMERA_MAIN_TC]`, S122)**: `MakeDistCorPrm` y `MakeDistRawAppliTag` son
  llamadas desde la capa TC (`0x437d3484`, `0x437d765c`), que escribe el valor de distorsión
  en el RAW (`TC:DIST:Err:WriteRawAppliTagValue1/2`).
* **Con el IDT (S120)**: la conversión `CnvPosInvDistCorr` es usada por el módulo IDT/IDT_OPD
  (`0x439f3000`–`0x439f57a0`) para corregir las posiciones de las areas de undistorsión
  (`Invlid distortion area` `0x43cf3588`).

## 8. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

| elemento | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAMERA_IS]` | **17** | **0** | **0** |
| textos interiores coincidentes | 17/17 | **0/17** | **0/17** |
| `GyroAD` | 2 | 0 | 0 |
| `IS_LensMountExpStartCB` | 2 | 0 | 0 |
| `IS_LensMountPanoramaGyro` | 3 | 0 | 0 |
| `MakeDistCorPrm` | 1 | 0 | 0 |
| `CnvPosInvDistCorr` | 3 | 0 | 0 |
| `MakeDistRawAppliTag` | 1 | 0 | 0 |
| `upm_get_hcrn_ura` | 1 | 0 | 0 |
| `osal_reg_sync_msg_queue_cb` / `…unreg…` | 3 / 2 | 0 / 0 | 0 / 0 |
| `[STABILIZER]` | 3 | 0 | 0 |
| `rcct_SetStblzPower` / `GridH` / `ParamV` / `VectorH` | 6 / 5 / 4 / 3 | 5 / 4 / 4 / 3 | 5 / 4 / 4 / 3 |
| `WrapRcctSetStblz*.cpp` (4 ficheros) | 4 | 4 | 4 |
| `EIS_RC1V_SetPower` | 2 | 2 | 2 |
| `LENS_MOUNT` | 2 | 2 | 2 |
| `/mnt/FILE_IS_%04x.dat` + texto `Ch.0/…` | 1 + 1 | 1 + 1 | 1 + 1 |
| `src/api_rc.cpp` | sí | sí | sí |

**Lectura del diferencial (VERIFICADO):**

1. La **etiqueta** `[CAMERA_IS]` y la **capa de aplicación del IS a nivel de cámara**
   (giroscopio propio, matemática de distorsión, callbacks con la montura, cola del
   estabilizador "AS") **sólo existen en la A6000 fw3.21**.
2. La **infraestructura de estabilización del driver RC** (`rcct_SetStblz*`,
   `WrapRcctSetStblz*.cpp`, `SetStblzGridHSeqCt`) y el **fichero de calibración IS por
   lente** `/mnt/FILE_IS_%04x.dat` **existen en los tres firmwares** → no es una novidade de
   la fw3.21 ni una exclusividad del modelo A6000: la diferencia está en la *capa de
   cámara*, no en el driver.
3. **Salvedad metodológica (S130 §4)**: la comparación mezcla **versión de firmware y
   modelo de cámara**; con los tres blobs disponibles no se puede separar «nuevo en la
   fw3.21» de «propio del A6000».

## 9. Interés para la línea del obturador

**Negativo verificado (importante):**

* **Ninguna** de las 17 trazas de `[CAMERA_IS]` menciona obturador, lectura del sensor,
  *rolling shutter*, tiempo de exposición ni solapamiento EIS/obturador.
* En toda la imagen de la A6000 fw3.21 hay **0 apariciones** de `rolling` y de `readout`
  (igual en la A7S fw3.20). **El A6300 fw2.01 sí tiene 1**: `position num in rolling is
  strange %d` (`0x43d9fe03`), junto a `position num in vd is strange %d` (`0x43d9fde2`) —
  es decir, el A6300 implementa el concepto de **rolling shutter** (número de posiciones por
  frame) en la capa del imager, y la A6000/A7S no. Está **fuera de `[CAMERA_IS]`** (no es una
  traza del módulo) pero es un dato de primera mano para la línea del obturador.
* Los únicos términos `SHUT*` de la zona (`b16_SHUT_cont_dst` `0x43c99e99`,
  `uc_ShutStat_mb` `0x43c990a7`, `b1_ShutAgc_HoldReq` `0x43c99e74`) pertenecen al
  **control del diafragma (iris/AGC)**, no al obturador, y **no** están en ninguna traza de
  `[CAMERA_IS]`.

**Lo que sí aporta el módulo a la línea del obturador (todo VERIFICADO):**

1. **El IS se sincroniza con el disparo**: `IS_LensMountExpStartCB` (`0x436ea2d0`) es el
   callback de **«exposición empezada»** que el módulo recibe de la montura (`0xF0`/`0xF1`,
   payload de 25 B). Es el punto donde el IS se engancha al ciclo de exposición.
2. **El EIS se programa desde la secuencia de exposición**: `0x43702dac` se llama en
   `0x4354a97c`, dentro de `0x4354a678` de `[CAMERA_MAIN_SYNC]`, justo después de la traza
   `Sync_EndExpose: DIST_RSLT_NG MakeDistortionCorrectionParamForSync error!`
   (`0x43cb0f80`): al **final de la exposición** la capa de sincronización fija la
   **rejilla horizontal del EIS** (tamaño = `(u16 en ctx+0xbda + 7) >> 3`, redondeado a
   múltiplo de 8) y llama a `rcct_SetStblzPower`. El valor de `ctx+0xbda` se escribe en
   `0x4354a7ec` desde `[ptr+0x1e]` (y su hermano `ctx+0xbd8` desde `[ptr+0x1c]`).
   **NO_VERIFICADO** si esas dos `u16` son el tamaño de imagen o el margen de EIS.
3. **El rail del EIS** se enciende/apaga desde la secuencia de alta velocidad: `0x43704d90`
   se llama en `0x4354e51c`, junto a la traza `b ee EIS_RC1V_SetPower` (`0x43cb2b9e`), y
   también desde `Sequence_HSRecGolfshot` (`0x438159ba`, `0x43815aa6`).
4. **Dato diferencial para el obturador electrónico**: el **A6300 fw2.01** tiene la API de
   driver **`GetImagerStabilizationTime`** (`0x43d9ce7f`, dentro de la zona de parámetros del
   driver del imager, junto a `ECDrvParam`/`LCDrvParam`/`calcDrvParamWithArg Skip`), que
   **no existe ni en la A6000 fw3.21 ni en la A7S fw3.20** (0 apariciones de
   `GetImager*` salvo temperatura y `GetImagerDriveMode`). Es decir: **sólo el A6300 pide al
   imager el tiempo que consume la estabilización** — el dato que un obturador electrónico
   necesitaría para calcular el tiempo de lectura. Y **sólo el A6300 implementa el concepto
   de *rolling shutter*** en esta capa (`position num in rolling is strange %d`
   `0x43d9fe03`, ausente en la A6000 y la A7S). Refuerza, desde otro ángulo, la lectura de
   S135/S51 (el A6000 no implementa esa capa), pero **queda fuera del alcance de este hito**
   (no pertenece a `[CAMERA_IS]`).

**Conclusión para S51:** `[CAMERA_IS]` no introduce ni menciona el obturador electrónico; el
estado de **S51 (A/B/C = NO) se mantiene**.

## 10. NO VERIFICADO / abierto

1. El **fichero fuente propio** del módulo `[CAMERA_IS]` (no está embebido; §5.1).
2. Qué significan exactamente las dos `u16` `ctx+0xbd8` / `ctx+0xbda` (¿tamaño de imagen?,
   ¿margen de EIS?) y quién las escribe en el resto del firmware (sólo se han located 4
   escrituras en el módulo `[CAMERA_MAIN_SYNC]`).
3. El significado de `upm_get_hcrn_ura` (sigla **sin desarrollar** en los bytes: no hay
   ningún `hcrn`/`ura` expandido en el firmware) y de las sub-capas `AS` y `DIST`.
4. El **significado físico** de la rejilla `SetStblzGridH` y de la ruta
   `rcct_SetStblz* → RC → sensor`: el camino hasta el driver RC está verificado; el destino
   en el sensor es INFERENCIA (no se ha seguido el RC hasta el imager en este hito).
5. El **formato binario** de `/mnt/FILE_IS_%04x.dat` más allá de la cabecera de 4 B y del
   texto `Ch.0/…`; y **quién escribe** ese fichero en fábrica (no está en el firmware).
6. El **significado del bloque `%2x,%2x,…`** (`0x43c9a460`) y su relación con los 16 B que
   preceden a la ruta del fichero.
7. Si las 4 funciones sin llamadores `bl` directos (`0x436ea2d0`, `0x436fecbe`,
   `0x436fee80`, `0x43705d64`) se registran como callbacks en una tabla de offsets
   relativos (no se han encontrado punteros absolutos de 32 B a sus direcciones).
8. La **región `0x43b7c000`** (callers `0x43b7c470`, `0x43b7c4fc`, `0x43b7c700`) y la
   `0x43af58f8` / `0x43b71fa8` no emiten ninguna traza propia: no se ha identificado su
   módulo.
9. Si el "rolling shutter" es un concepto presente en la A6000 con otra grafía (0 hits de
   `rolling`/`readout` en los tres blobs).

## 11. Revisión del agente principal

_(vacía)_

## 12. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s164_camera_is/make_prologues.py      # cache de prólogos Thumb
.venv/bin/python analysis/s164_camera_is/scan_camera_is.py       # -> camera_is.json (base)
.venv/bin/python analysis/s164_camera_is/scan_is_details.py      # -> camera_is.json (+detalles)
.venv/bin/python -m pytest tests/test_s164_camera_is.py -q
```

Ayudas: `analysis/s164_camera_is/disasm.py 0x436ea2d0 40` (desensamblado anotado con las
cadenas resueltas) y `analysis/s164_camera_is/scan_context.py 0x436e8000 0x43708000`
(cadenas referenciadas desde una región).

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (18 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 17 cadenas `[CAMERA_IS]` en la A6000 fw3.21 entre `0x43c98da6` y
   `0x43c9a426` (5 `MOUNT`, 5 `DIST`, 4 `EIS`, 3 `AS`); **0** en la A7S fw3.20 y el A6300
   fw2.01 → comprobado con `bytes.count()`; también `[CAMERA_IS][AS]` 3/0/0, `[EIS]` 4/0/0,
   `[DIST]` 5/0/0, `GyroAD` 2/0/0, `[STABILIZER]` 3/0/0.
2. **Los 17 pares PIC verificados a mano** (17/17), y los 13 contenedores coinciden con el
   mapa manual de **S70** → **validación cruzada** de la regla estricta en este módulo; S164
   añade las **5 trazas** que S70 no listaba y la **13.ª función** `0x4371e4cc`.
3. **La infraestructura RC del estabilizador NO es nueva**: el token exacto
   `rcct_SetStblzPower` es **2/1/1** y `rcct_SetStblzGridH` **2/1/1**, y
   `/mnt/FILE_IS_%04x.dat` es **1/1/1** → el driver de estabilización y el fichero de
   calibración por lente **existen en los tres firmware**; lo propio de la fw3.21 de la A6000
   es la **capa de cámara** (giroscopio propio, matemática de distorsión, callbacks con la
   montura, cola del estabilizador "AS").
4. **Negativo verificado**: 0/17 trazas mencionan obturador, lectura del sensor, *rolling
   shutter*, tiempo de exposición o solapamiento EIS/obturador → **sin efecto en S51**.
5. **Hallazgo colateral con valor para la línea del obturador (verificado)**: la imagen de la
   A6000 fw3.21 tiene **0 apariciones** de `rolling` y de `readout` (igual en la A7S fw3.20),
   mientras que el **A6300 fw2.01 sí tiene 1**: `position num in rolling is strange %d`
   (`0x43d9fe03`), junto a `position num in vd is strange %d` (`0x43d9fde2`) → el concepto de
   *rolling shutter* **existe en el A6300 y no en la A6000/A7S**, y la cadena `vd`/`VD` (S90,
   visor) aparece **en el A6300 pero no en la A6000**: otro punto a favor de que el A6300 es
   el cuerpo con más funciones de lectura, y de que **la ausencia en la A6000 es una
   limitación del modelo, no del firmware**. Esto **no** cambia S51 (A/B/C = NO): la
   ausencia estática de una cadena **no** demuestra incapacidad del hardware.
6. **Salvedad metodológica**: la comparación mezcla versión de firmware y modelo de cámara;
   con los tres blobs disponibles no se puede separar «nuevo en la fw3.21» de «propio del
   A6000» (heredada de S130 §4).

---

### Corrección posterior (hito S168, 22-10-2026) — la cadena del *rolling* del A6300 está **muerta**

El punto 5 de la revisión de arriba queda **matizado**: la cadena
`position num in rolling is strange %d` del A6300 fw2.01 (`0x43d9fe03`) **no la referencia
ningún código** (0 referencias PIC por la regla estricta, 0 punteros absolutos, 0 pares
`movw`/`movt`; control cruzado con un método inverso independiente). Es una **cadena muerta**.

Lo que **sigue en pie** es el dato bruto: la cadena está en el A6300 fw2.01 y **no** en la A6000
fw3.21 ni en la A7S fw3.20, y las 36/37/40 apariciones de `roll` en las tres son casi todas
`Controller`/`Scroll` (nombres de clase RTTI), no el concepto de *rolling shutter*.

Lo que **cae** es la inferencia «el A6300 implementa *rolling shutter*». El único código vivo
en esa banda es el cálculo de ancho del **número de posición del VD** (`0x4372914c`).

**No cambia S51** (A=NO, B=NO, C=NO) ni S135 (control positivo del subsistema `ElecShutter/`
en el HAL del A6300, que es un hallazgo **independiente** de esta cadena); de hecho **debilita**
un argumento potencial. Detalle y herramientas: `analysis/s168_a6300_rolling/`.
