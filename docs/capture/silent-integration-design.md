# SilentShutter integrado: ruta de fotografía normal y diseño propuesto (Sesión 7)

Solo análisis estático del firmware 3.21. Etiquetas: VERIFICADO, INFERENCIA, HIPÓTESIS, NO VERIFICADO, DESCARTADO.
Direcciones: av-cam (LIRO) = VA lógica `0x43541000`; bibliotecas Linux = VA ELF (Ghidra = VA + `0x10000`).
Herramientas: `scripts/libobj_dec.sh` + `analysis/ghidra/DecompAt.java` (proyecto `analysis/ghidra/a6000-libs`, sin autoanálisis, funciones creadas en la dirección pedida), `scripts/elf_thumb_callers.py`, `scripts/elf_string_xrefs.py`, `tests/test_elf_xrefs.py`.

## 1. Quién es quién

| Subsistema | Binario | Papel en una foto normal |
|---|---|---|
| LIRO (RTOS) | `av-cam.bin` (nflasha3) | Gestor de disparo `RelMgr`, captura (`Stage_*`), revelado, SDF/`ddl_jpeg`/SA, notificación final |
| Linux, aplicación | `libObj.so` (nflasha15) | `SeqStillCap` (secuencia de captura), `ObjStillRecorder` (pin), `ObjStillRecorderCore::RecordStill`, `MprCtrl` |
| Linux, medios | `libmpr.so` (10 MB) | `MprIf::WriteStill`, `StillWriterFilter`, `DCFStillWriter`, `dcf_Lib` (nombre DSC, EXIF, escritura, borrado, reproducción) |
| Linux, extras | `libInfraStreamingServer.so`, `libInfraScalarMpr.so` | LiveView por red (SFRA); puente ScalarA↔MPR (`GetContentInfo`, `GetExifData`, `DeleteContent`, `EditStillMetaData`) |
| Android | `nflasha16` (MediaProvider, libavindex) | NO usado por la cámara nativa para catalogar (NO VERIFICADO; solo apps Android) |

No hay una base de datos única inscrita por el firmware de captura: la cataloga el propio MPR al escribir (§3). `avi accsr REGISTER <n> <DCF> DCIM/100MSDCF/DSC<FILENO> <w> <h>` (comando de monitor de libmpr) demuestra que existe un registro explícito de contenido DCF dentro de MPR.

## 2. Ruta de una foto normal (disparo → reproducción)

1. **Pulsación (LIRO)**. `RelMgr` (clase del gestor de disparo, etiquetas `[IMAGING_REL]`). Manejador de mensajes `REL_EVT` `0x4379d83a` (VERIFICADO, `analysis/ghidra/liro-relmgr-exec.json`): `switch` con eventos `0xb..0x1f`; actualiza una tabla de estado de teclas (`0x4379d114`, «RelKey) %02d: %02d»), consulta `IsNeedForceS1ON` (`0x4379d37a`), bloqueo `RelLock` (`0x4379e5e4`) y emite avisos a `CamUser` (cola `0x40193`) con `0x4379d3f8/42c/460/498/4f8/52c/5e4/624` (mensajes tipo 6: ids `0x202e,0x2067,0x2038,0x205a,0x206d`; tipo 1: `0x404a,0x404b,0x4049`). INFERENCIA: S1 y S2 son los bits `1` y `0x10` de las máscaras `FUN_43aea210(...,1,..)/(...,0x10,..)`; NO VERIFICADO qué evento exacto es «pulsación completa».
2. **Inicio de captura (LIRO)**. `CaptureManager_FunctionIF` `0x437df338` → objeto de captura (`0x437dcfc8`), exposición `StrtExps 0x4381106c`→`SetExposure 0x436d6320`, clase de exposición en `0x43841070` (ver `efcs-capture-selector.md`), Darwin/obturador, `Stage_SACC` (`0x43782464`, lectura del sensor) → Raw/Develop → `Rcv_*` → `EncodeJpeg_MainYC` + `SCNEnc` + `THMEnc` (SDF/SA) → `ReadEnd`. NO VERIFICADO el enlace RelMgr→CaptureManager (mensaje exacto).
3. **Notificación a Linux (LIRO)**. Etapa `Stage_Notify` (función `0x437efe78`, VERIFICADO): construye mensaje de `0x2a8` B: `[0]=4` (TYPE_CAP_NOTIFY), `[2]=0x1006` (captura terminada con StillInfo), `+4`=id de secuencia, `+8=0xf000` (OK), y copia **`MPR::StillInfo` (0x28c B) en `+0x14`**; lo envía con `FUN_437feef8(msg,0x2a8,&0x20002)`. Tras el envío libera los handles locales.
4. **Secuencia de captura (Linux, `libObj.so`)**. `SeqStillCap` (`FUN_00a4b650` Ghidra = ELF `0xa4b650−0x10000`; cadenas `[CAMUSER]: SeqStillCap)`). Procesa mensajes de LIRO por id (`0x1000` inicio, `0x1005..0x1024`, `0x1006` fin con StillInfo). Para `0x1006` verifica los handles `still_info.jpg_info.mainJpg.memHandle`, `exifSrcInfo.exifSrcArea.memHandle`, `ycc_freeze`, `sds_ycc_freeze` y los libera si hay error (cadenas «Free Error»). Envía por pin (`PinMsgSend`) a `ObjStillRecorder`. Gatillos soportados: `m_TriggerMsgID` `0xa00b/0xa00c/0xa010`; otros dan «CapCmp is NON SUPPORT» (`0xa3b376`).
5. **Grabación (Linux)**. `ObjStillRecorderCore::RecordStill` (ELF `0x908afc`, único llamador directo `0x90bbdc`; VERIFICADO). Lee del mensaje: `0x1001` CapDate (10 B), `0x1002` OrgDate (10 B), `0x100e` StillRecCtrlInfo (8 B), `0x1007` GpsInfo (0x90 B, `MprCtrl+0x94`→`SetStillGpsInfo`), `0x1006` CamInfo (0x88 B → `SetStillCamInfo`), y llama a `MprCtrl::WriteStill` (ELF `0x8fe0a0`, que invoca `MprIf::WriteStill(WriteStillParam*, StillInfo*, n)`, espera un semáforo y devuelve un bloque de 0x48 B de resultado). Al terminar envía respuesta `0x3500/0x3002` con `0x1001`=error y `0x100f`=info de contenido (`FUN_0091b248`, ELF `0x90b248`).
6. **Escritura y catálogo (`libmpr.so`)**. `FeaCore::WriteStill` (ELF `0x440794`): hasta 2 `WriteStillParam` de 0x40 B (campo `[6]` = handle de memoria que debe coincidir con una «línea de grabación» registrada antes; `+0x34` = 10 B de nombre/fecha), copia a `param_1+0x9a8…`, resuelve la dirección del handle (`0x457810`) y encola. `dcf_Lib::WriteDcfMemory` escribe `exifData` + `mainDataReserve` + `mainData` + `thumData` y añade el APP del screennail (`MakeScreenNailAppOne`); `dcf_Lib::SetAppOneData(bValidFlg,bMakerNoteValidFlg,bReEncodedFlg)` compone el EXIF; la numeración/ruta `DCIM/100MSDCF/DSC#####.JPG` la gestiona el accesor DCF de MPR (`ChangeRecDirectory`, `ClearReserveEntryNumbers`). NO VERIFICADO: la función concreta que registra la entrada en el índice de reproducción (estructuralmente interna de `StillWriterFilter/DCFStillWriter`).
7. **Reproducción**. `viewUnified*`, `libInfraScalarMpr`, `MprIf::EnterStillPb/PlayStillSingle/ReadStillSingle/DeleteContent`: leen del mismo MPR (VERIFICADO por símbolos); por eso ampliar, borrar y transferir dependen solo de que MPR haya escrito/registrado el contenido.

## 3. Estructura `MPR::StillInfo.jpg_info` (volcador de libmpr, VERIFICADO)

`exifSrcInfo{exifSrcArea, model, software, publicMakerNote, pimInfo, secretMakerNote, mpfSrcArea}` + `mainJpg`, `thumJpg`, `screenNail`, cada uno como **(memHandle, offset, size)**; más `metaMemory*` y `metaOffsetInfo*`. Los handles son del mismo dominio DMM que los `hdl=0x%04x` de SFRA (`GET_JPEG`) y de `libInfraStreamingServer` («jpeg memHandle=…, size, ofs»). Además SFRA exige que el usuario libere los handles («user should free jpeg handles»), igual que `SeqStillCap` libera `mainJpg.memHandle`: coherente con que un buffer READY de SFRA pueda hacer de `mainJpg`. HIPÓTESIS: se aceptaría tal cual (falta comprobar si `mainJpg` espera bitstream sin SOI/APP; `ApiEncodeJpeg` tiene `addSoi`).

## 4. SFRA frente a la ruta normal

- [DESCARTADO por línea B, 2026-10-16: esas cadenas pertenecen a `jobSetPictureInfoCmd` (entrada de ISS para fotos de tarjeta), no a GET_JPEG; SFRA solo entrega {handle,size>>7}; no hay EXIF/thumb/scn] CORRECCIÓN respecto a lo supuesto al empezar: `libInfraStreamingServer` registra por fotograma tres conjuntos de handles (`jpeg count/memHandle`, `exif count/memHandle`, `scn count/memHandle`; cadenas «%s - jpeg|exif|scn count=%d, memHandle=%x, size=%d, ofs=%x»). Es decir, la respuesta de SFRA puede incluir JPEG, EXIF y screennail (HIPÓTESIS: coinciden con `mainJpg`, `exifSrcArea` y `screenNail` de `StillInfo`). NO VERIFICADO qué contienen exif/scn ni si `GET_JPEG` (`0x439a282c`, que devuelve pares {handle,tamaño}) los entrega todos; falta `thumJpg`. Si el EXIF de SFRA es utilizable cambia el diseño (menos trabajo en LIRO). El EXIF de la captura normal viene de `CaptureUtilityExifMkNote.cpp` / `SR::api_SR_CreateExif` / `CS_ExifMakerNote_dslr.cpp` (VERIFICADO por cadenas, no analizado).
- SFRA solo lo abre `InfraStreamingServer` (LiveView por Wi-Fi/PTP); en ese servicio ancho solicitado ∈ {320, 640, 1024}.

## 5. Diseño propuesto (concepto, sin ejecución)

Dos puntos de integración, ambos reutilizando todo lo posterior (SeqStillCap → RecordStill → WriteStill → DCF):

**A (recomendado en principio): sustituir la fase de adquisición en LIRO.** En el coordinador de captura (clase de exposición `0x43841070`/secuencia `0x43b1xxxx`) añadir, bajo el ajuste Silent, una secuencia que no llame a Darwin ni `Stage_SACC`: toma el YC de LV (SDS), ejecuta `EncodeJpeg_MainYC/SCNEnc/THMEnc` y termina en `Stage_Notify` `0x437efe78`. Existe precedente de captura sin sensor: `Stage_RawPlayInit`/`Stage_DevLater` (revelado de ARW desde tarjeta) usa `ycc_rawplay`/`sds_ycc_handle` y llega a los mismos `*Enc` y a `Stage_Notify` (VERIFICADO por cadenas; no se ha trazado la tabla de etapas).
**B: generar el mensaje `0x1006` desde otro origen** (p. ej. SFRA en LIRO): el mensaje se construye con `StillInfo` propio (mainJpg = handle SFRA, thumb/screennail por SDF, exif de LIRO). Requiere reproducir lo que `Stage_Notify` hace con el estado de captura (`iVar1+0x4b..`).
**C (descartada como primera opción)**: escribir desde Linux con `fopen` en `/DCIM`: no pasa por el accesor DCF ni el índice de MPR; NO se demuestra reconocimiento en reproducción. Solo sería viable llamando a `MprIf::WriteStill` desde `libObj` (misma API que `RecordStill`), que de hecho es la variante «B en Linux» y no necesita escribir ficheros.

Decisión Silent vs normal: en `CamUser`/LIRO ya existe el ajuste (`pvt_ActionSetSilentShutterMode`, cmd `0x40e3` guardado en un bloque de parámetros; ver `silent-shutter-status.md`); el punto de decisión natural es la selección de clase de exposición del coordinador (`0x43841070`), no los eventos del botón (RelMgr se conserva intacto: S1/S2/bloqueos/AF).

Evitar: `Stage_SACC`, ejecución Darwin/CAIF de exposición, cualquier secuencia `0x43b1xxxx` que mande fases de obturador. El grafo directo de SFRA no los alcanza (`analysis/sfra-outcalls.json`), pero la entrada de YC y las llamadas indirectas de A/B no están trazadas.

## 6. Requisitos de metadatos (estado)

- EXIF: lo compone libmpr desde `exifSrcInfo` (model/software opcionales: «model is NULL», «software is NULL» son rutas previstas), CamInfo/GpsInfo/fechas del mensaje y MakerNote público/privado (hay rutas de error «Err Public/Private MakerNote Data»). Orientación: «Err Orientation Tag None!». Miniatura y screennail embebidos: `thumData`/`MakeScreenNailAppOne`.
- NO VERIFICADO: cuáles son estrictamente obligatorios para que la reproducción acepte el fichero.

## 7. Bloqueos concretos

1. Trazar RelMgr → `CaptureManager` (qué mensaje/estado inicia la captura y dónde se elige la clase de exposición).
2. Mapa de etapas por tipo de captura (qué secuencia usa `Stage_RawPlayInit` y cuál es su lista de etapas), para saber si se puede entrar con un YC de LV.
3. Contenido mínimo válido de `StillInfo` (`exifSrcInfo`, `thumJpg`, `screenNail`) y registro en el índice de reproducción dentro de `StillWriterFilter/DCFStillWriter` (no exportado; requiere reconstruir la vtable por RTTI).
4. Origen del YC de `pin` en SFRA.

- Sesión 9 P1: MakeWriteStillImage sólo construye el contenedor (EXIF+miniatura+JPEG) en memoria; útil para EXIF, no para persistir. Ver record-still-image-route.md.

## Apéndice sesión 10
- No usar `0x930464`/`MakeWriteStillImage` como camino de grabación. El punto de integración a estudiar es `0x1027` → `ObjStillRecorder` (ELF `0x919ca0`, `+0x128=4`) → `RecordStill::Execute` (ELF `0x90b248`). Contrato mínimo aún NO VERIFICADO (ticket `0x131f/0x1320`, anillo `+0xdc`).

## Apéndice sesión 11
- Punto de integración a estudiar: Pool (`InfraStillPool::RegisterImage`), no `0x1027`. Contrato: mensaje con `0x1000`, `0x100e` (tipo), `0x100b` (tabla de handles DMM u16), `0x1001` (fecha), `0x1006/0x1007/0x3009` (descriptores). Los handles de SFRA (u16 DMM) son del mismo tipo; faltan miniatura/EXIF. Sin parche: solo contrato teórico. Detalle en `objstillrecorder-mode4.md`.

## Apéndice sesión 12
- Punto de integración candidato E: el mensaje de orden `0x10000005` de `ObjStillRecorder` (contenedor `0x10000006`: `0x1017` YcDataMemInfo+Colorimetry+yRange, `0x1031` DecodeCanvasInfo, `0x1041` MetaInfo, más `0x1000` captureId y `0x1012`). Linux no tendría que codificar JPEG: `MprIf::EncodeStill` genera JPEG, miniatura, screennail y maker note.
- Responsabilidades: LIRO/Live View aporta el YC en DMM con handle+tipo+phys; Linux envía la orden y espera `0x3500/0x3002`; MPR codifica y escribe; el Pool numera y registra.
- Pendiente de demostrar: formato YC admitido, remitente, `MediaMgr` ≠ None, tamaño objetivo (`ImageSize`), fallo de escritura (código en `0x3500/0x1001`), vuelta a Live View.
- Ruta secundaria para escribir una imagen ya presente en el Pool: orden `0x10000003` (`ObjStillRecorderCore::WriteStill`).

## Sesión 13 — punto de integración de E
- Mínimo conceptual (HIPÓTESIS): desde el manejador de disparo en Linux, en vez de iniciar la captura, (a) activar el recorder (`0x3500/0x2001`), (b) enviar `0x3500/0x3001` con modo 0 (Pbcap), (c) responder a `YcPinReqDeliver` entregando un `PlayData` con un YC del EE (handle, unitType, phys, canvas, colorimetría, rango Y).
- Responsabilidades: el productor del YC (por localizar) es quien debe retener el buffer; el recorder abre/cierra el handle al preparar.
- Bloqueos: topología del pin YC, estado de ObjRenderer en disparo, interceptar la captura mecánica sin tocar Darwin. NO VERIFICADO.

## Sesión 14 — punto de integración de E (revisado)
- Cambia el diseño conceptual de sesión 13: no basta con «responder a `YcPinReqDeliver`». El respondedor natural es **ObjEffect** y exige la topología `0x2a` activa (`TopologyManager`, modelo con lista `{…,0x2a}`) y un modo interno que acepte `REQ_DELIVER` en la salida nº1.
- Responsabilidades: ObjEffect fabrica las unidades (`0x50b3f`/`0xe0b00`) por SDF; el recorder abre/cierra al preparar y encola `EncodeStill`; el productor libera después de `CBID_ENCODE_STILL` (momento NO VERIFICADO).
- Opciones de menor riesgo (HIPÓTESIS): (a) modelo de disparo que añada `0x2a` a `{0xa,7}` y envíe `0x3500/0x3001` modo 0; (b) mantener A y usar E solo como sustituto de la fase JPEG.
- Bloqueos: modo de ObjEffect en EE, tipo de unidad del visor, momento de liberación del `RecYc`, y no tocar GPIO ni Darwin al interceptar el disparador (punto `0x3011`/RelMgr/CaptureManager, aún no estudiado).

## Sesión 15 — punto de integración de E, sin cambios de diseño

Detalle: `docs/capture/liveview-encodestill-parallel-verdict.md`. El diseño conceptual de sesión 14 (activar `0x2a` + modo de Effect que acepte `REQ_DELIVER` con Camera) no cambia. Lo nuevo:

- Confirmado que `EffectInternalMode` es un holder indirecto (no un byte plano en `this`) con un escritor localizado (`0x173158`) que solo lo usa en el camino de PbCap (lee el campo `0x1025` del propio `REQ_DELIVER`). **No existe, hasta donde se buscó, ningún escritor equivalente para Live View** — lo que sugiere que la pieza que falta no es "qué valor de modo poner", sino "qué mensaje/modelo tendría que escribirlo en absoluto" durante EE.
- Confirmado (identidad de ObjCamera) que cualquier diseño debe pasar forzosamente por Effect: Camera no tiene pin de entrada y no puede recibir `YcPinReqDeliver` ni ningún otro mensaje de pin directamente.
- Los bloqueos de integración siguen siendo los mismos tres de sesión 14 (modelo que cree `0x2a` en disparo, modo de Effect, tipo de unidad del visor), ahora con mejor caracterización del mecanismo que habría que activar pero sin el emisor identificado.

## Sesión 16 — el escritor de modo 1 existe pero no transporta imagen; el candidato de arbitraje cambia de capa

Detalle: `docs/capture/s16-liveview-recorder-verdict.md`. El diseño conceptual no cambia (sigue exigiendo activar `0x2a` + un modo de Effect compatible con `REQ_DELIVER` desde Camera), pero dos piezas se precisan:

- La pregunta de sesión 15 ("qué mensaje/modelo escribiría el modo durante EE") tiene ahora una respuesta parcial: **sí existen** dos escritores dinámicos de `EffectInternalMode=1` (`ExecCmdAppFaderEfctEndEvt`, `SequencePinDeliverBase`), pero ambos pertenecen a fundidos de efecto y edición de pin, no a Live View — y, más importante, el modo 1 (mensaje `0x600d`) **no instancia ningún objeto de secuencia con estado** (a diferencia del modo 2–5, que sí lo hace vía la factoría `0x17b004`), lo que sugiere que no transporta imagen. Si esto se confirma, el diseño debería descartar el modo 1 como vía de entrega y centrarse en los modos 2–5, que siguen sin escritor conocido desde EE.
- El candidato de "quién arbitra el acceso al pin único de StillRecorder" se traslada de ObjEffect (sin guard hallado, revisado explícitamente esta sesión) al `StsViewer` compartido por `StsId=6`, dado el hallazgo de una segunda fila (`0xb4`) con el mismo destino. Cualquier diseño de intercepción debería considerar este objeto como punto de control, no solo la topología o ObjEffect.
- Bloqueos sin cambios: modelo que cree `0x2a` en disparo fotográfico; tipo de unidad del visor; momento de liberación tras `CBID_ENCODE_STILL` (ahora más caracterizado: FEA solo encola y copia un descriptor de 0x40 B, no el raster).

## Sesión 17 — el `StsViewer` no es un cerrojo; el diseño pasa a depender de un modelo de disparo, no de un arbitraje a vencer

Detalle: `docs/capture/s17-parallel-research-verdict.md`, `docs/capture/s17-a-e-p-architecture-comparison.md`. Cambio relevante para el diseño conceptual:

- El candidato de arbitraje que sesión 16 trasladó al `StsViewer` compartido (`StsId=6`) **queda descartado como cerrojo activo**: `GetStsViewer` es un *get-or-create* de caché, y `ObjPin::Connect` (su consumidor real, en `libMWF.so`) no consulta el viewer para aceptar o rechazar una conexión — solo registra notificación. Esto significa que **no hay ningún arbitraje de software que un diseño de integración deba "vencer" o "redirigir"** entre `0x2a` y `0xb4`; la única restricción es estructural (un puntero escalar de "pin conectado", no una lista), que se resuelve simplemente por orden de llamada a `Connect()`, no por permiso.
- Consecuencia directa para el diseño: la pieza que falta sigue sin ser "cómo convencer a un árbitro", sino, igual que en sesión 16, "qué modelo/mensaje de disparo fotográfico invocaría `createLifeCycles`/`Connect()` para la fila `0x2a` en absoluto durante EE" — el diseño conceptual no cambia de forma, pero pierde una capa de complejidad hipotética (no hace falta diseñar una estrategia de arbitraje, porque no existe tal mecanismo que esquivar).
- Nueva vía alternativa documentada (no sustituye el diseño E, se añade como referencia): la API pública `CameraSequence` ofrece una ruta de JPEG electrónico ya operativa en el firmware (aunque no demostrada como disparo S2 en este proyecto), que no depende de ninguna de las piezas internas de LIRO/ObjEffect aquí diseñadas. Un diseño de integración alternativo (arquitectura P) requeriría una aplicación Android nueva que conecte `onShutterKeyDown` con `CameraSequence.getPreviewSequenceFrames()`, fuera del alcance de los binarios LIRO/`libObj.so` que cubre este documento.

## Sesión 18 — la pieza que falta sigue siendo "qué dispara `Connect()`/la fila `0x2a`", ahora acotada a 5 bibliotecas candidatas; sin aporte de diseño desde fuentes Sony OSS

Detalle: `docs/capture/s18-parallel-research-verdict.md`. El diseño conceptual **no cambia de forma**: sigue exigiendo un modelo/mensaje de disparo que invoque `createLifeCycles`/`Connect()` para la fila `0x2a` durante EE, mecanismo que esta sesión tampoco localizó. Lo que se añade es **acotación del espacio de búsqueda**, no una pieza de diseño nueva:

- El sitio real que invoca `ObjPin::Connect` desde un `LifeCycle` construido queda acotado a 5 bibliotecas concretas (`libBizFw.so`, `libBizFw2.so`, `libInfraCacheMgr.so`, `libInfraScalarMpr.so`, `libmprctrl.so`) — ninguna es `libObj.so` directamente. Cualquier diseño de integración que dependa de interceptar esa llamada debería mirar primero en esas 5 bibliotecas, no en todo el stack.
- Confirmado (Claude D) que `libObj.so` no tiene una tabla de constructores por ObjId que un diseño pudiera "rellenar" para forzar la creación de un objeto con ObjId 53 o similar — la resolución es por auto-registro en runtime. Esto **descarta** una vía de diseño que hubiera consistido en "escribir en la tabla GOT/BSS correcta" (viable en LIRO, no en `libObj.so`).
- Las fuentes oficiales Sony OSS (kernel Linux 3.0.27) **no aportan ninguna pieza de diseño**: confirman que la plataforma usa `ashmem` (no ION/DMA-BUF) para memoria compartida y FAT/VFAT para el medio, pero nada de esto cambia el diseño conceptual de la ruta E, que sigue dependiendo enteramente de componentes propietarios no publicados.
- El bloqueo de disparo en LIRO (consumidor de la cola `0x40193`/`0x3011`) se acerca un nivel: se identificó el dispatcher inmediatamente inferior (`0x43807f4c`, dominio `0x100..0x207`), pero el puente hacia el dominio `0x3011` sigue sin probarse — sigue siendo la pieza de diseño más concreta pendiente de resolver antes de poder proponer cualquier integración real.
- Bloqueos sin cambios: modelo que cree `0x2a` en disparo fotográfico; `unitType`/formato del YC de Camera; consumidor real de `0x3011`/`0x40193`; receptor real de `CBID_ENCODE_STILL`.
