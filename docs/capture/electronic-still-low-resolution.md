# Captura electrónica a resolución reducida — estado y plan

**Conclusión actual (honesta):** NO hay todavía evidencia directa de una ruta de foto electrónica.
Hay (a) mapa verificado del hardware de cortinillas ([fm3-gpio-shutter-mapping.md](fm3-gpio-shutter-mapping.md)) y
(b) matriz verificada de modos del sensor ([imx210-video-readout.md](imx210-video-readout.md)).

| Pregunta | Estado | Evidencia |
|---|---|---|
| ¿Las cortinillas se mueven por GPIO P4D/P4E (no serie)? | VERIFICADO (estático+esquema) | PDOR4 b13/b14 → 1ST/2ND_CURTAIN_MG → FET Q6832 → bobinas 1C/2C |
| ¿Silent condiciona esas escrituras en A6000? | NO (VERIFICADO estático) | `0x20C90/B2/D4/D00` solo filtran por tipo HW 1..3 vía `0x20C74` |
| ¿Existen modos de sensor de lectura continua? | VERIFICADO que hay 13 conjuntos de registros; vídeo/Live View ↔ ID NO verificado | matriz de 59 regs |
| ¿Puede un frame de vídeo guardarse como foto sin cortina? (2 MP) | HIPÓTESIS plausible, no probada | el vídeo FHD60 existe; falta el empalme con el guardado JPEG |
| ¿6/12 MP nativos (skip/bin/window)? | NO VERIFICADO | falta mapear regs de la matriz a ventana/binning |
| ¿24 MP con fin electrónico de exposición? | NO VERIFICADO (no descartado) | `0x0b` programa el sensor en modo foto; el fin de integración depende de 2ª cortinilla en la ruta actual, sin demostrar necesidad física |

## Ruta de menor esfuerzo propuesta (teórica, sin desplegar)
1. Identificar la función de «grabar fotograma de Live View» (captura de frame del pipeline de vídeo → JPEG; p. ej. «AutoReview»/«Still from movie»/ guardar fotograma).
2. Si existe, gatillarla desde la ruta de disparo evitando `Darwin` secuencia mecánica (comando CAIF de captura sin bit de movimiento): requeriría parche en LIRO (ruta A/B divergente) — hay que localizar el punto de divergencia (`captura+0x4d0`, `0x437f7ff0`).
3. Alternativa: llamar SetMode con modo «vídeo» (`0x05`) justo antes de la exposición y bloquear las 4 funciones `0x20C90/B2/D4/D00` (solo análisis).
Riesgos: rolling shutter, sin control de ISO/obturación como foto.

## Sesión 2c: mapa del pipeline (P2) — herramientas: `scripts/string_xrefs.py`, `scripts/ghidra_dec.sh` (QuerySilentLiro con `!addr` = entrada exacta), `scripts/thumb_callers.py` (ahora también B.W)
VERIFICADO (cadenas + decompilado, `av-cam.bin` A6000 3.21):
- **SetMode real**: `0x43795a60(modo, flip1, flip2, out)` arma el descriptor (`out[0]`=modo, `[4]`=`DAT_43f9a4c1` = selector de tabla A/B ≈ sistema 60/50 Hz, `[5]`,`[6]` = flips XOR `DAT_43e9d5bc/bd`) y lo pasa a `0x436d62e4` (SetMode). `0x437957ec` (GetDriveInfo) rellena un bloque de 0x104 B con `GetModeInfo` (vtable+0x24 vía `0x436d61a4`) y 0x28 B con `DFECore::getDrvParam` (`0x43ae92ee`→`0x4381b4b0`); `0x43795d44` lo cachea en `0x43e9d600` (0x104 B). Es decir, **DrvParam CS/Camcore/EC/LC = configuración del receptor DFE/CamCore (ASIC) por modo**, no registros del sensor.
- **Ejecución de lectura** `ReadExecuteBase` `0x438c7800` (variantes `0x438c8474`, `0x438cc7a0`; llamadas desde secuencias `0x43b1ae54…0x43b1e7d0`): flags de `param_2`: `&1` sensor (SetMode `0x43795a60`+`0x436d62e4`; `0x436d6320`, `0x436d6398` = exposición/lectura; `0x436d61a4`), `&0x20` salida «view» (`AfterViewContRcStart`, `IIB_Acquire`), `&0x40` otra salida a memoria; luego `getDrvParam` del DFE, `DFE Start`, `CamCore Start` y espera de callback (`+0x4eec`). Cadenas: «Cap core mode», PGA/SHD/28Limit/LongOb, SnrCtrlMode, opb_out.
- **Etapas de captura** (clase Capture, tags `IMAGING_CAP`, `Stage_*`): `Stage_SACC` `0x43782464` = adquisición del sensor con motor NFLASH (`sa_func_NFLASH_acquire` `0x43b6da42`, start `0x439d4cc4` con mailboxes canal A/B, release `0x439d4be8`; buffers de RAW por `AsyncAllocNew` 0x167) → `Stage_Raw`/`Develop`/`SPICA`/`MARBLE`/`Rch_*`/`Rcv_*` (resize/distorsión) → `SCNEnc`/`THMEnc`/`EncodeJpeg_MainYC` → `ReadEnd`. Hay `EnterCapturing`/`EnterCapturingLv` (`0x437284c0`, estado `DAT_43f94449`) y volcados de depuración de RAW e YC con `canvasSize/validOffset/validSize`.
- **JPEG**: módulo SDF, mensajes `MSG_ID_SDF_ENCODE_JPEG[_REC|_WITH_WORK]`, `ApiEncodeJpeg` (`0x43653d34`): entrada = imagen **YC** (stream unit type/handle/offset; `wholeYcSdsArea`), parámetros `jpegImageSizeX/Y`, `primaryImageSizeX/Y`, `encodeQuality`, `outputYRange`, `outputYuvColorSpace`, `addSoi`; motor HW vía `ddl_jpeg_*` (strips `Tanz`). Por tanto **el JPEG toma YC ya revelado**, no RAW ni la salida cruda del sensor.
- `stillPictureRec`/`hsMovieRec` pertenecen al codificador de vídeo AVC (I-frame), no a JPEG.
INFERENCIA: un still silencioso necesita RAW del sensor → Develop → YC → SDF Encode; la etapa SACC arranca la lectura con `SetMode/SetExposure/SetRead` y NFLASH, y no se ha encontrado en ella ninguna orden Darwin/obturador (las cortinillas se mandan por otro camino, Darwin).
NO VERIFICADO: formato de píxel del RAW en memoria, tamaños de buffer, qué stage corresponde a Live View, si hay camino LV→SDF, cómo se secuencia Darwin respecto a `ReadExecuteBase`, EC/LC (`0x43543dc8`/`0x43543fa0` sin decompilar a fondo).

## Sesión 3 — Live View, vídeo y rutas frame→JPEG (estático, sin cámara)

Evidencia: `analysis/ghidra/{mode-pick-4380e43c,mode-pick-helpers,mode-compute,mode-request-writers,seqmode-callers,setmode-callers2,lv-capmgr,lv-enter,capture-prepare-437f87b2,lv-jpeg-exec,ddl-jpeg-driver,jpeg-ring-encode,imx210-ec-lc,imx210-setexposure-setread,view-cont-rc}.json`; extractor `scripts/string_xrefs.py` (test `tests/test_string_xrefs.py`).

### Respuestas a las preguntas del encargo

| Pregunta | Estado | Respuesta |
|---|---|---|
| ¿Qué modo es 1080p? | VERIFICADO (código) | Caso «vídeo» de `0x4380e43c`: **0x1A o 0x10** en IMX210 (0x1A si `ctx.b[+0xb1]==0`); 24p: **0x19 o 0x07**; formato 4 → 0x12. Detalle en `imx210-video-readout.md` «Sesión 3». |
| ¿Qué modo es Live View? | VERIFICADO (código) | **0x01 (2000×570) o 0x03 (2000×800)**; 0x0F (1024×684) en el caso 0 con `FUN_43794a44≠0`. Los 1996×1124 son solo vídeo. |
| ¿Cómo llega el modo a `SetMode`? | VERIFICADO | `0x4380e43c` → `DAT_43eea2e4` → petición `0x43e994d0` → estado vigente `0x43e99320` → `ImgState+0x44` (`0x43e9bb30`) → `SetSequenceMode_img 0x4378e334` → `0x43795a60`. La captura usa un camino distinto: `captura+0x4d0` en `0x437f87b2` (preparación) y `ReadExecuteBase`. |
| ¿Dónde se almacenan los frames y en qué formato? | NO VERIFICADO | Los buffers de salida pasan por el gestor de memoria (`dmm AllocNew/ALOCK`, mensajes tipo `0x61003c` que devuelven pares de direcciones Y/C). El formato YC con planos Y y C separados es INFERENCIA (estructura `{Y, …, C}` del JPEG de LV y `ApiEncodeJpeg`). Formato RAW y tamaños: sin resolver. |
| ¿Existe JPEG sin obturador? | VERIFICADO que existe hardware/código; HIPÓTESIS de reutilización | Ver rutas A–C. |

### Rutas frame→JPEG encontradas

- **A. SDF (captura estándar)**: `ApiEncodeJpeg 0x43653d34`, entrada YC con `wholeYcSdsArea`; hay `ModuleEncodeJpegBase` con *NoResize*, *WithWork* (redimensiona internamente) y *Tanz*; motor `ddl_jpeg`. VERIFICADO.
- **B. SFRA LiveView** (`ScalarInfraSequenceLiveView`, etapa `Autoexec_jpeg` `0x439a3b50`): recibe del gestor de buffers (mensaje `0x61003c`, `0x439a677c`) el frame ya en JPEG y lo analiza con `dgis_jpeg_decode_analyze_header` (`0x43935d04`, inicialmente 640×360, límite de salida `0x3f000` B) para enviarlo por la cola `0x56000f` (tamaño 0x58 B). NO es un codificador: el JPEG de Live View lo produce otra etapa (productor NO identificado). VERIFICADO el consumo; productor NO VERIFICADO.
- **C. Codificador directo `jpeg encode syncFirst/syncNext`** (`0x4379b180`, `0x4379b058`, `0x4379aaf4`, resto `0x4379a8xx–0x4379b3xx`): construye un descriptor de ~0xA0 B con ancho/alineado a 64, alto alineado a 8, direcciones de entrada/salida y llama a `0x43b4c83e` (`ddl_jpeg_encode_syncFirst`). Anillo de 2000 entradas de `0x2c` B (`JpegRingBuf.cpp`, `0x43e9f074`), con 240/200 imágenes por segundo según el flag. Lo usan `Sequence_HSRecGolfshot` (`0x4354c7xx–0x4354eaxx`) y rutas de panorama. VERIFICADO el mecanismo; HIPÓTESIS que sea alcanzable en A6000 (código compartido de familia; no se ha verificado la habilitación por modelo). Es el candidato más cercano a «cuadro electrónico → JPEG sin Develop ni obturador».

### Correcciones a la Sesión 2c

- `AfterViewContRcStart*` (`0x437f94d8`, `0x437f96f0`, `0x438c7bea`) pertenece a `CaptureUtilityPreReview.cpp`: es la **revisión automática posterior a la captura** (resize/RC), no Live View. El flag `&0x20` de `ReadExecuteBase` (salida «view») es, por tanto, salida de revisión; INFERENCIA, no probado el flag.
- `EnterCapturing`/`EnterCapturingLv` (`0x437284c0`, `0x43728570`) son solo marcas de estado (un byte global y un log); las llama `0x437df338` (gestor de captura `CaptureManager_FunctionIF`, que crea el objeto `captura` con `0x437dcfc8` y consulta `CaptureManager_ModeInfo` en `0x437e067c`). No inician la lectura.
- `CaptureManager_ModeInfo` (`0x437e067c`) mapea «tipo de captura» (0,3..9 → 1/9/0x18/0x1b/0x1c…) a un identificador de captura **distinto** del modo IMX210; no confundir ambos espacios de numeración.

### Exposición (P3) — estado parcial

- VERIFICADO: `calcDrvParam` EC (`0x43543dc8`) y LC (`0x43543fa0`) generan temporizaciones en coma fija Q8 del receptor (DFE/CamCore) a partir de las tablas por modo y de la tasa `0x43ad986e`; no contienen el tiempo de exposición.
- VERIFICADO: `SetExposure 0x436d6f6c` recibe una estructura con tres valores (14, 12 y 12 bits) que escribe en registros sombra por pares «byte bajo + nibble/6 bits alto», y un campo de submodo `+9` (0..4) que combina los bits `0x04/0x80/0x10/0x40` de un registro de control; en los submodos 1–3 calcula además una duración en ms (`+0x3a0`). Direcciones de registro y significado: NO VERIFICADO (punteros sombra cargados en tiempo de ejecución). `SetRead 0x436d7e08` escribe cuatro registros a partir de `*param_2` (si >0x1000 resta `0x1000 - tabla[+0x1c]`).
- Pendiente: relacionar submodos 1–3 con exposición larga/sincronizada con obturador y con el periodo de cuadro (66,8 ms a 24 MP).

### Evaluación para un JPEG silencioso de ~2 MP (INFERENCIA)

Faltaría: (1) demostrar que el modo 0x05/0x10 (1996×1124) o 0x01 puede activarse fuera del estado de vídeo; (2) formato/estride de los buffers de salida del ISP en ese modo; (3) llamada a la ruta C (o SDF) con ese buffer; (4) una exposición real independiente (los frames de LV usan la integración del bucle continuo, no una por disparo); (5) evitar la secuencia Darwin de captura (`0x43841070`, paquete de 22 B por `0x437db858 → 0x436b8a50`) o demostrar que la ruta C nunca la dispara. Ninguno está probado.

## Sesión 4 — ruta C (codificador directo) reconstruida

Exports: `analysis/ghidra/jpeg-ring-encode.json`, `golfshot-encode-caller.json`, `golfshot-gate.json`, `jpeg-ring-ctx.json`, `jpeg-ring-init.json`, `rcv-dataset.json`, `movie-rcv.json`, `model-init.json`. Test: `tests/test_jpeg_ring_callers.py`.

**Mapa productor → buffer → consumidor (VERIFICADO en decompilado, sin ejecución)**
1. CamCore/ISP entrega cuadros YC por un trabajo RCV: `job_RCV_dataset_main` = `0x43798ccc` (`RCVDataSet`). Lo llaman la secuencia HS (`0x4354e62e`) y la película normal (`0x4381592c`/`0x43815a28`, llamadas `0x43815a12`/`0x43815b22`); la película usa el mismo bloque de parámetros (`obj+0x668`…).
2. Buffers de entrada: dos direcciones (Y, C) en `obj+0x6a8/+0x6ac` de la secuencia (`FUN_4354d740`). Origen: `obj+0x24/+0x28` tras `AllocRendezvous` (`0x439035e0`) o `CamMGetRCV` (`0x4381c04c(2,…)`). Tamaños de plano por `FUN_43b03bf8(w,h,fmt)`; ancho en `obj+0x19e`, alto en `obj+0x1a0`.
3. Consumidor: `0x4379b180` (`syncFirst`) y `0x4379b058` (`syncNext`) → `ddl_jpeg_encode_syncFirst` `0x43b4c83e`. Descriptor ~0xA0 B: stride Y = ancho alineado a 64, alto alineado a 8, stride C = ancho alineado a 16, `0x0b` y `2/2` fijos (muestreo no resuelto), calidad = `obj_ctx+0x88` o `*(DAT_4402546c+0x4c)`, tabla `DAT_440241f0`.
4. Salida: área de bitstream en el contexto global `0x43e9f014` (`+8` base, `+0xc` capacidad). Cada JPEG entra en el anillo `JpegRingBuf` (2000 × 0x2c B, `DAT_43e9f074`; entrada: `+0` puntero, `+4` tamaño, `+8` longitud alineada a 0x800) con `syncGetParam` `0x43b4c882` y `0x4379aaf4`. Pre-roll de 240 (`f0`) o 200 imágenes por segundo según `*(…+0x14)`.
5. El tamaño de plano YC es el del cuadro RCV; no hay Develop, `Stage_SACC` ni Darwin en esta ruta.

**Quién la llama (VERIFICADO)**: solo `FUN_4354d740` (casos de etapa 1, 3 y 4: `EncFirst`, `EncNext1st`, `EncNext`). No hay más llamadores directos. Las funciones de secuencia (`0x4354c6d0`, `0x4354d740`) no tienen BL entrantes: solo aparecen como puntero en la tabla de datos `0x44022478` (región `0x44022300–0x4402251c`, mezcla de punteros a código y datos). El despachador no está resuelto.

**¿Funciona en A6000? NO VERIFICADO.** Evidencia parcial:
- `Golfshot` se llama en las cadenas `[ADF][SAN]…GolfShot` a un analizador de sonido (función de Action Cam), y las secuencias `HS`/`SuperSlowMotion` son de alta velocidad: la A6000 no declara HFR.
- (CORREGIDO en Sesión 5: NO es un modelo, es el código de mensaje en curso) Control: `**FUN_4378f9b4()` (contexto `0x43e99208`, BSS; inicializador no localizado) es un `short` comparado con `0x120`, `0x127` y `0x129` en `FUN_4354d740`. Se desconoce el código de la A6000; `fdat.model` del firmware es `0x41030035` (otro espacio). Con el flag `DAT_4402546c[0x1c]&0x40` las etapas abortan si el modelo no es `0x127`/`0x129`.
- No hay evidencia de que un cuadro RCV de **Live View** (0x01/0x03) o de vídeo 1996×1124 entre aquí; la secuencia pide su propio modo por `FUN_43799a94(1,…)`.

**DESCARTADO**: ctx `0x43e9f014 +8/+0xc` no son buffers YC de entrada (son base y capacidad del bitstream); corrige una lectura provisional.

**Conclusión de esta ronda**: existe una ruta ISP→JPEG que no pasa por `Stage_SACC`, Develop ni obturador, pero depende de la secuencia HS, de un despachador sin identificar y de un código de modelo desconocido. Siguiente: localizar el despachador de `0x44022478`, el origen de `FUN_4378f9b4()[0]` (código de modelo) y los consumidores de `0x43e9f014` fuera de HS (`4379a9fc`, `4379aa3c`).


## Sesión 5 — despachador de la ruta C, «modelo» y JPEG de SFRA

**1. Despachador (VERIFICADO con bytes y desensamblado)**
- Los punteros de `0x44022300–0x4402251c` son la **GOT PIC** del módulo, no una vtable. El código la usa como `ldr r5,[pc]; add r5,pc` (base `0x4401eee4`, p. ej. `0x4354c6e0`) y `ldr r1,[r5,r3]` con el offset de 32 bits en el literal. La entrada `0x44022478` (offset `0x3594`) solo se carga en `0x4380ee0c` (literal `0x4380f098`). Por eso no aparecían BL ni xrefs absolutas.
- Quien la carga es el selector `FUN_4380e43c` (el mismo de vídeo/LV). `switch((cfg[+0x264]&0xfffff)>>15)` elige la clase de secuencia y escribe `DAT_43eea2e4` (modo IMX210). Tabla completa: `analysis/seq-dispatch-table.json` (`scripts/seq_dispatch.py`, `tests/test_seq_dispatch.py`).

| caso | secuencia | modo IMX210 |
|---|---|---|
| 7 | `0x435503b0` (película normal) | 0x1a/0x10/0x19/0x07… |
| 8 | `0x435503b0` | 5 / 0x32 |
| 9 | **`0x4354d740`** (HSRecGolfshot, codifica) | **0x08** |
| 10 | **`0x4354c6d0`** (HSRecGolfshot) | **0x11** |
| 0xb–0xf | `0x438133b8`, `0x4354c0e0`, `0x4381381c`, `0x4354cec0`, `0x4354ea98` | 0x11 |
| 0x10/0x11 | `0x43554590` (SuperSlowMotion) | 0x21–0x2e |
| 0x12 | `0x43b03b00` | 0x01 |

- El campo (`cfg+0x264>>15`) solo se lee (`0x4378e49a`, `0x4380d364`, `0x4380e4ae`, `0x4380e524`); no hay `bfi` que lo escriba. Lo trae el mensaje de configuración del host. VERIFICADO que ninguna rama de av-cam lo pone a 9..0xf por su cuenta. NO VERIFICADO qué envía la app de la A6000.
- Los modos 0x08 y 0x11 NO están en el conjunto soportado por el IMX210 (`{01,03,05,07,0A,0B,0F,10,12,18,19,1A,2F}`, sesión 3). INFERENCIA fuerte: la secuencia HS/Golfshot no configura el sensor de la A6000. El código existe también en A6300 (`Sequence_HSRecGolfshot` y `JpegRingBuf` presentes).

**2. «Modelo» (CORRECCIÓN, DESCARTADO como modelo)**
- `*(short*)*FUN_4378f9b4()` es el código del **mensaje en curso**: `FUN_4380ca5c` hace `switch(*(short*)*ctx)` con `0x139/0x13b/0x13d/0x13f/0x145`, y `FUN_43815210` rellena un mensaje con `0x11a` y lo envía con `FUN_43acb8ae`. Los valores `0x11a/0x120/0x126–0x129/0x13e` se comparan en distintas secuencias. Los de `0x126…` coinciden con el índice bajo de IDs `0x69xxxx/0x5e0126/0x3010126`. El contexto es `{mensaje, par_modos, cfg, …}` (`ctx[2]`=cfg, `+0x264`).
- Consecuencia: la etapa 0 de `FUN_4354d740` NO filtra por modelo. Con `DAT_4402546c[0x1c]&0x40` (flag de depuración/parada, BSS=0) solo acepta mensajes `0x127/0x129`; sin él sigue, solo exige `FUN_43795b04()!=0` y `FUN_43799a94(1,…)`, y reserva `JpgRingBuf` (`0x172f17`) e `JPG_INFO_BUF` (`0x2d2`, mínimo 88 000 B). La A6000 no se descarta por el gate; se descarta (INFERENCIA) por el modo de sensor.

**3. Película normal (P4)**: `FUN_4380ca5c` construye el objeto de secuencia común (dims `+0x19e/+0x1a0`, p. ej. 0x780×0x438 en 1080). Es el mismo objeto base que usa la secuencia HS. Esa película no llama a `0x4379b180`: su consumidor es el codificador de vídeo. No hay evidencia de un JPEG que consuma esos YC.

**4. JPEG de Live View / SFRA (P2) — correcciones**
- `0x61003c` NO es un mensaje del productor: es un ID de pool de mensajes genérico (≈55 `alloc 0x435612d0` / `submit 0x43561228` / `free 0x435612ec` en `0x4366f2xx` y otros). `0x439a677c` solo pide la dirección de un handle DMM.
- `FUN_43b4c4e2` = `ddl_jpeg_analyze_stream_info` (llama a `dgis_jpeg_decode_analyze_header`): la etapa `Autoexec_jpeg` de LiveView **analiza** un JPEG ya hecho (dims de salida) y lo notifica por `0x56000f`. VERIFICADO consumidor.
- SFRA es un servicio de comandos (`ScalarInfraAsyncMain`, `FUN_439a1864`, cola `0x167046a`): `GET_INFO`, `SET_PATH(OPEN/CLOSE)`, `SET_SA_NOTIFY`, `GET_SA_RESULT`, `SET_JPEG_PARAM`, `GET_JPEG` (`FUN_439a282c`, devuelve lista de handles+tamaños en múltiplos de 128 B), `LiveView SET_JPEG` (`FUN_439a3754`). `ScalarInfraSequenceJpeg` hace control de tasa (iqscale, `targetSize`, reintentos en `0x439a318a`) y gestiona buffers `WRITE/EMPTY/READY` (`getReadyBuf`/`getWriteBuf`). No llama a `ddl_jpeg` directamente. HIPÓTESIS: el JPEG lo genera un bloque de HW en la ruta (path) de YC y SFRA solo lo controla. Productor concreto y emisor de los comandos: NO VERIFICADOS.

**Clasificación de la ruta C en A6000**: NO ACCESIBLE por el selector con la evidencia disponible (INFERENCIA; modo 0x08/0x11 ajeno al IMX210); sin descartar que el host pida el formato. El codificador `0x4379b180` en sí (sin la secuencia) no está descartado, pero necesitaría un productor RCV propio.

**Mejor candidato siguiente**: el servicio SFRA (`SET_PATH(OPEN)` + `SET_JPEG_PARAM` + `GET_JPEG`) sobre el YC de vídeo/LV; solo dependería del path y no del obturador. NO VERIFICADO que se pueda iniciar desde la A6000 ni a 2 MP.

**Bloqueos**: (a) quién envía los comandos SFRA/qué formato de película manda el host (código fuera de av-cam); (b) productor HW del JPEG de la ruta SFRA; (c) independencia mecánica de esa ruta (`SET_PATH` no trazado hasta CAIF/Darwin).

Exports: `analysis/ghidra/{fmt-idx-readers,sfra-jpeg-seq,sfra-jpeg-encode-stage,sa-jpeg-enc}.json`, `analysis/seq-dispatch-table.json`.

## Sesión 6 — productor del JPEG de SFRA, cliente y dependencias

Etiquetas: VERIFICADO (bytes/desensamblado), INFERENCIA, HIPÓTESIS, NO VERIFICADO, DESCARTADO.

**1. Qué es SFRA (VERIFICADO)**: *ScalarA-ScalarInfra*, infraestructura del acelerador Scalar (SA: `sa_dfdet.bin` detección de caras, programas `SA_JPEG_ENC/DEC`). Servicio de comandos en av-cam (`FUN_439a1864`, recibe en `0x167046a`, responde a `0x1670464`; mensajes con cabecera `0x2009/0x1100`). Secuencias: `Info`, `Jpeg`, `LiveView`, `Sa`. `FUN_439a5794` elige secuencia por el tipo de mensaje de `SET_PATH`.

**2. Productor del JPEG de la secuencia `Jpeg` (VERIFICADO salvo el ID exacto del mensaje)**
- Etapa `Autoexec_jpeg` (`0x439a2f8c`): toma el YC de un *Standard Data Structure* (SDS; parser `FUN_439a2b44`, mismo tipo `wholeYcSdsArea` que `ApiEncodeJpeg`), reserva un buffer de salida (`getWriteBuf`, estados EMPTY→WRITE) y envía un mensaje de 0x54 B a **SDF (`0x56000f`)**, etiqueta «Msg to SDF», con ancho/alto (`+0x1c/+0x28/+0x50`), tamaño máximo de salida `min(KB<<10, 0x3f000)` (`+0x34/+0x3c`) y qscale (byte `+0x4e`, de `[ctx+0x1d4]`). Respuesta a `0x167046a`.
- Etapa `Autoexec_jpeg_comp` (`0x439a32b8`): lee estado (`msg+8`) y tamaño comprimido (`msg+0xc`); si excede `limit` o falta área de trabajo reintenta con otra qscale (`candidate_439a318a`, `RETRY … LIMIT/WORK SIZE OVER`, hasta `retryCount`); si cabe, marca el buffer READY (`SUCCEEDED`). Por tanto el mensaje a SDF es una **codificación** (devuelve tamaño, y se ajusta la calidad).
- `SET_JPEG_PARAM` (`0x439a2918`) solo guarda `compressRate` (byte `msg+8` → `ctx+0x2b`) y responde `fcmdSetJpegParam COMP`. No fija dimensiones.
- `GET_JPEG` (`0x439a282c`) NO pide codificar: recorre los buffers READY (`FUN_439a23d0`) y devuelve hasta N pares {handle, tamaño en múltiplos de 128 B}. Buffers: 2–256 (`param_1[0xc]` limitado), reservados en `SET_PATH(OPEN)` (`0x439a26ba`, pool `0x276`).
- SDF → codificador (VERIFICADO por cadenas/estructura): `ModuleEncodeJpeg*` ejecuta `ExecJpegEncode/OpenJpegOpen/ddl_jpeg_*`. La API `ddl_jpeg` (`dgi_jpeg_*`) envía el mensaje `0x640100` a la tarea `tsk_jpeg.c`; las rutinas `dgi_jpeg_open/close_tskproc_sa_ack/_sa_comp` y los programas preinstalados `SA_JPEG_ENC/DEC` (`0x4399eef2`, SAD «Scalar Accelerator Driver», mensaje `0x53`) indican que **el motor es el acelerador SA**. Es el **mismo motor** que `ApiEncodeJpeg 0x43653d34` (SDF) y que la ruta C (`ddl_jpeg_encode_syncFirst`). INFERENCIA: ID del mensaje SDF concreto (`MSG_ID_SDF_ENCODE_JPEG`≈id 4 por el orden de la tabla `0x436393b0`); NO VERIFICADO que SFRA use `NoResize` o `WithWork`.
- Corrección: `LiveView SET_JPEG` (`0x439a3b50`, `fcmdSetJpeg`) es la dirección contraria: analiza un JPEG recibido (`ddl_jpeg_analyze_stream_info`), reserva un SDS de salida (marcador `SSYC` `0x43595353`, 640×360 por defecto, 0xe0b00 B) y envía otro mensaje (0x58 B) a SDF. INFERENCIA: es un **decode** (JPEG→YC para mostrar), no el productor.

**3. Tamaños (VERIFICADO)**: `candidate_439a2dd0` (alto según ancho y aspecto): anchos 0x140/0x280/0x400/0x500/0x5a0/0x780 (=320/640/1024/1280/1440/1920); a 1920 el alto es 1440/1280/1080/1920/1152 según el aspecto de la trama (`SDS+0x2e`, 0=4:3 … 3=1:1). Es decir, el firmware admite 1920×1080 ≈ 2,07 MP. Límite por JPEG: 0x3f000 B (258 048 B) en el mensaje. El ancho viene de `SET_PATH(OPEN)`. El cliente actual solo acepta 320/640/1024 (ver §4).

**4. Quién abre el path: cliente en Linux (VERIFICADO)**: `libInfraStreamingServer.so` (nflasha15 `/lib`, clase `InfraStreamingServer`): `jobLiveViewStartCmd` (`0xd2bc`) → `pvtSfrSetPath` (`0xd068`) que arma el mensaje `0x2009` (tipo `0x20`=abrir, 0x40 B; otro tipo 0x10 B), `pubSfrGetJpeg`/`jobGetLiveView` (`0xce48/0xcd0c`), `ContentHandlerEEImpl::GetLiveViewJpeg/MmapLiveViewJpeg`. Es el *Live View por Wi-Fi/PTP* (contenedor `DefLiveViewContainer` con ancho/alto). `jobLiveViewStartCmd` solo acepta ancho 0x140/0x280/0x400; otro valor usa el predeterminado (con aviso). Parámetros de «EE»/backup: `compressrate`, `picx`, `framerate`, `jpeg max size`. También `libInfraPtpControl.so` (PTP-IP/USB) referencia la cola `0x167046a` (función ≈`0x30xx`, sin analizar). NO VERIFICADO: qué estado de cámara/alimentación exige (Wi-Fi remoto, PC Remote USB).

**5. Independencia mecánica**
- VERIFICADO (grafo directo): `scripts/sfra_outcalls.py` (`analysis/sfra-outcalls.json`, test ok): la región SFRA `0x439a1000–0x439b0000` no tiene BL/B.W directos hacia captura Darwin `0x43841070`, `ReadExecuteBase`, `SetMode`, CAIF (`0x436fa784/0x436bcef4/0x436ba234/0x437db858`), el codificador de ruta C ni `ApiEncodeJpeg`. Solo llama a servicios de SO/mailbox/DMM/SA/ddl_jpeg. Posibles falsos positivos de BL sobre datos.
- NO VERIFICADO: llamadas indirectas (vtable, `blx`, mailbox) y la ruta de **entrada**: quién genera/entrega el SDS YC a la etapa `pin` (disparo `0x8011`, `SendExecTrigger`; `ScalarInfraSequenceSa` YC IN/OUT). Esa ruta no usa cortinillas por lo visto, pero no se ha trazado hasta el ISP.
- Clasificación: A (lectura continua + codificación JPEG) por estructura: los fotogramas se codifican uno a uno mientras el path está abierto y `GET_JPEG` solo recoge los READY. No hay ninguna rama de captura fotográfica.

**6. Resultado frente a un fotograma «independiente»**: lo que da SFRA es un **snapshot de Live View** (YC del bucle continuo, exposición de LV), no una exposición independiente. Para ≈2 MP el firmware lo permite (1920×1080) pero el cliente lo limita a ≤1024 de ancho. NO VERIFICADO: formato YC de entrada y escalado previo (SDF `WithWork` reescala).

**7. Caso 10 / modo 0x11 (VERIFICADO)**: `SetMode` lógico `0x436d6b54`: modo 0 → 1; modo >0x47 → 2; si `[0x43e0a390+0x7c]!=0xff` y modo==0x11 aplica primero el índice del modo 5 (1996×1124) por `vtable+0xa0`; después la búsqueda de 0x11 en la tabla de 13 falla (`0xff`) → devuelve 2. Por tanto 0x11 no es un modo propio del IMX210 sino un alias que fuerza el modo 5 y devuelve error. NO VERIFICADO si `0x4354c6d0` continúa tras el error 2. Ruta C sigue sin evidencia de accesibilidad; no se invierte más en Golfshot.

**8. Comparación de entradas YC**: SFRA y `ApiEncodeJpeg` comparten SDS YC y el mismo motor SA; la ruta C toma dos punteros YC del trabajo RCV (`obj+0x6a8/+0x6ac`). Reutilizar SFRA es más simple que conectar un buffer YC a otro codificador, porque ya gestiona buffers, calidad y límite de tamaño.

**9. Punto de integración teórico más simple (HIPÓTESIS)**: no cambiar av-cam. El JPEG READY ya está en memoria DMM mapeable (`MmapLiveViewJpeg`); el punto natural es el consumidor Linux `GetLiveViewJpeg`/`pubGetJpegData`, que guardaría el primer JPEG READY en la tarjeta. Es un snapshot de LV, no disparo independiente; el control de exposición/disparo queda para otra etapa.

**Bloqueos**: (a) productor y formato del YC que entra por `pin` (SA/ISP); (b) estado de cámara en el que el servidor abre el path (¿solo Wi-Fi/USB remoto?); (c) trazar `libInfraPtpControl`; (d) ID exacto del mensaje SDF de SFRA; (e) exposición independiente.

Exports: `analysis/ghidra/{sfra-dispatch-sad,sfra-msg-helpers,sfra-jpeg-open,sfra-jpeg-open2,sfra-stage-pin-ack-comp,sfra-pin-trigger,sdf-msg-build,sdf-msg-dispatch,sdf-msgname,sdf-site1,ddl-jpeg-open,ddl-jpeg-drv,ddl-jpeg-send}.json`, `analysis/sfra-outcalls.json`; scripts `scripts/sfra_outcalls.py` (+ `tests/test_sfra_outcalls.py`).
