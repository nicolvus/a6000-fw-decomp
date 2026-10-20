# S21 — Codex: exposición → imagen en biblioteca

Actualización S29: [WriteStill de entrada a cierre](s29-writestill-end-to-end.md)
cierra RecStill→FEA mediante el callback registrado en `0x43f57e` y el
handler `0x441644`, y enlaza el cierre Pool con `SetImageWrited` por
`0x6108/0x1007`. WriteStill responde `0x10000004`; no reutilizar la respuesta
`0x3002` de Execute. Siguen separadas las garantías físicas/de reproducción.

Fecha: 2026-10-17. A6000 3.21, análisis estático. **Resultado: PARCIAL**:
se amplía la cadena hasta escritura de JPEG/RAW y registro DCF, pero no se
demuestra una cadena completa hasta una imagen visible en reproducción.
**A > E > P ≈ E2 permanece sin cambios. SilentShutter no se declara funcional.**

Todas las direcciones de bibliotecas son VA ELF; en las extracciones Ghidra
antiguas de estas bibliotecas, VA Ghidra = VA ELF + `0x10000`. LIRO usa VA
directa, base del binario `0x43541000`. Una función existente y sus aristas
estáticas no acreditan que una toma concreta recorra ese camino.

## Material existente y comprobación independiente

**VERIFICADO:** se leyeron antes de investigar `CONTEXT.md`, `shutter-control.md`,
`silent-shutter-trace.md`, `capture-pipeline.md` y los once documentos de
`docs/capture/` solicitados, incluidos los veredictos S18–S20, Darwin, EFCS,
GPIO, topología y OSAL. Las rutas exactas constan en el
[inventario](../../analysis/session21/evidence/codex-inventory.json).

| Inventario | Existencia / reutilización | Clasificación |
|---|---|---|
| `analysis/` | Entradas de primer nivel listadas; no se generó otro firmware ni otro proyecto Ghidra | VERIFICADO |
| `analysis/session18/` | 13.664 archivos recursivos, principalmente material previo; entradas directas inventariadas. **No existe** `session18/evidence/` | VERIFICADO |
| `analysis/session19/` | 82 archivos; incluye `evidence/` (13 archivos) | VERIFICADO |
| `analysis/session20/` | 75 archivos; incluye `evidence/` (74 archivos) y checkpoint | VERIFICADO |
| `analysis/ghidra/` | 620 archivos; nombres listados, reutilizados los JSON indicados debajo | VERIFICADO |
| `scripts/` | 32 archivos contando cachés; leídos `rtti_vtables.py`, `func_owner.py`, `pin_signatures.py` | VERIFICADO |

**VERIFICADO — reutilización:** `analysis/stillinfo-layout.json`,
`objstillpool-100b-layout.json`, `s17-codex-c-yc-contract.json`, tabla de
topología, RTTI `libobj-rtti-vtables.json`, evidencia `codex-dcf-*.json` de S20,
`analysis/ghidra/liro-notify-stillinfo.json`, `libobj-recordstill-exec.json`,
`libobj-corewritestill.json`, informes Camera/Effect/PbCap/SFRA/Pool y la
corrección de EventReceiver de S20. Se consultaron los desensamblados existentes
`/tmp/s20work/libObj-full.disasm` y `avcam-thumb.disasm`; no se regeneraron.

**VERIFICADO — contraste nuevo:** ventanas LLVM acotadas contra los ELF,
relocaciones/vtables contra bytes originales, destinos Thumb de llamadas,
tablas TBB leídas como datos y 138 instrucciones de `Stage_Notify` comparadas
con `av-cam.bin`. El detalle reproducible está en
[codex-chain-audit.json](../../analysis/session21/evidence/codex-chain-audit.json)
y [su auditor](../../analysis/session21/evidence/codex-chain-audit.py):
**194 comprobaciones PASS**. Los JSON `codex-*.json` nuevos conservan las
ventanas, bytes y SHA256 antes/después; `existing_listing` identifica ventanas
S20 reutilizadas. Los nombres de símbolo anteriores impresos por LLVM no se
usan para atribuir funciones. Se ignoran las primeras medias instrucciones
de ventanas que comienzan dentro de una instrucción y el falso código de pools/TBB.

| Original | SHA256 contrastado | Clasificación |
|---|---|---|
| `libObj.so` | `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a` | VERIFICADO |
| `libmpr.so` | `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30` | VERIFICADO |
| `av-cam.bin` | `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9` | VERIFICADO |

## Tabla de cadena y propiedad de los buffers

«Dueño» distingue reserva, acceso y vida útil; abrir/mapear un handle no
demuestra transferencia de propiedad ni una barrera DMA/caché. Las filas
marcadas como evidencia previa conservan sus límites: no se recomprobó en S21
cada instrucción de esos subsistemas.

| Etapa | VA / archivo y productor → consumidor | Buffer / dueño / cierre | Clasificación |
|---|---|---|---|
| Fin de exposición y lectura IMX210 | Informes EFCS/Darwin; interfaz con el tramo Claude | No se recuperó aquí el callback de última línea/DMA que entrega el frame a Camera o a los productores JPEG/RAW LIRO | NO_VERIFICADO |
| Entrega nativa de still LIRO | `av-cam.bin:0x437efe78`; serializa en `0x437effe6 → 0x43afe932`, copia en `0x437efff6 → 0x439c5320`, envía en `0x437f0004 → 0x437feef8` | Copia `0x28c` B a mensaje+`0x14`, longitud `0x2a8`, selector `0x20002`; son descriptores/metadatos, no copia del raster. El productor físico y la última lectura del buffer no quedan identificados | VERIFICADO (bytes/mensaje); NO_VERIFICADO (producción y fin DMA) |
| Live View SFRA → ISS, camino separado | `libInfraStreamingServer.so:0xcc58`, `0x1230c`, `0x14568`; evidencia S19/SFRA reutilizada | SFRA produce JPEG comprimido DMM; respuesta `{handle:u16, bloques128:u16}`; ISS mapea `/dev/mem`, reemplaza/libera frame anterior. No hay transferencia demostrada a MPR | VERIFICADO (contrato previo); NO_VERIFICADO (puente still) |
| ObjCamera → ObjEffect | `libObj.so:0xcc4210`, fila `0x0a`; ctor Camera `0x98c380` | Camera.out0 es pin YC. Tipo DMM, planos, stride, color, productor y reciclaje efectivos de ese YC permanecen abiertos | VERIFICADO (topología previa); NO_VERIFICADO (buffer) |
| Effect/PbCap → SDF | `libObj.so:0x15fd50`, `0x15fa74`, `0x15ebfc`; S17/S19 reutilizados | PbCap reserva raster `0x50b3f` y SDS `0xe0b00` (cabecera `0x800` B); SDF recibe descriptores, canvas/región; publica PlayData tras resultado `0x111`. No demuestra Camera→ese holder ni ownership final | VERIFICADO (ruta previa); NO_VERIFICADO (unión Camera/fin de lectura) |
| Variante ObjScalar | Tabla de topología, filas `0xb0/0xb1` y `0xb4`; informe S20 reutilizado | En `SCALAR_STILL_REC` intercala STILL_DATA; `0xb4` lleva YC out2 de Scalar a Recorder en ModelScalarPb. No es prueba de un disparo por YC Live View | VERIFICADO (topología previa); NO_VERIFICADO (captura sin mecánica) |
| YC → ObjStillRecorder → EncodeStill | `libObj.so:0x90b248`, reserva `0x90a810`, codificación `0x90ad20 → 0x8fe6f8`; `libmpr.so:0x44f834` | Recorder reserva áreas de salida, FEA recibe descriptores YC/RegionInfo. Copiar `0x40` B de descriptor no copia píxeles ni retiene por sí solo el raster. Vida útil completa abierta | VERIFICADO (ruta y reserva; ventanas nuevas y evidencia previa); NO_VERIFICADO (último acceso) |
| StillConverter, callback de codificación | Ctor `libObj.so:0x916140`; rama `0x91ebe0` | `ctx+0x48/+0x4c` son EventSender/EventReceiver locales; `ObjMsg(0x3a48,…)` reencola trabajo. No es un pin a DCF. Traducción y registro exactos del callback EncodeStill pendientes | VERIFICADO (clase/loopback); NO_VERIFICADO (cierre EncodeStill) |
| Traducción DMM → StillInfo Linux | `libObj.so:0x92980c`, `0x92a140`, `0x930508`; `stillinfo-layout.json` | LIRO: descriptores `{handle,offset,size,reuse}` de `0x10` B. Linux: puntero+tamaño, StillInfo `0x6b0`. Pool/traductor abre/reutiliza y mantiene lista de accesos; refcount terminal no recuperado | VERIFICADO (ABI previo); NO_VERIFICADO (ownership terminal) |
| Pool y preparación DCF | `libObj.so:0x90ba24 → 0x908084 → 0x90fcd4 → 0x91bbd0 → 0x8fd2fc → 0x900124` | Después de preparar la imagen se puede pre-registrar DCF; `0x900180` llama API síncrona. No escribe los píxeles ni acredita publicación | VERIFICADO (aristas nuevas y orden condicional) |
| Obj → MPR, escritura | `libObj.so:0x90bb86 → 0x90f698`, `0x90bbdc → 0x908afc`, `0x908d9c/0x90a172 → 0x8fe0a0 → PLT 0xe0f70` | WriteStillParam `0x40` B × 1/2 y StillInfo; wrapper espera evento y copia resultado `0x48` B. No pasa ObjMsg como ABI de MPR | VERIFICADO |
| MPR/FEA → Recorder | `libmpr.so:0x440794`, `0x34b1be`, `0x34b1cc → 0x34a92c` | Prepara descriptores y envía comando 9; Recorder posee cola/controlador, no un raster copiado por ese comando | VERIFICADO |
| Recorder → RecStill → StillWriterFilter | `libmpr.so:0x32d5b2`, `0x32ed34`, vtable RecStill `0x81c0b8`, `0x34cc34` | Controlador RecStill crea dos filtros concretos (`+0x968/+0x96c`); bandera `+0x956` para orden 9, avance condicionado por estado/completados, comando 5 para escribir | VERIFICADO (unión estática nueva; precondiciones necesarias) |
| Filtro → secuenciador DCF | `libmpr.so:0x5144e4 → 0x5144b0 → 0x5141ec → 0x3a2e74` | `dcf_If` serializa y despacha `this+4`, slot `+0x48`; AVI/no AVI depende de argumento del ctor. La instancia usada por toda toma no está propagada | VERIFICADO (despacho/selector); NO_VERIFICADO (selección por toma) |
| Formato y archivo | `libmpr.so:0x396dcc`, JPEG `0x38b064`, RAW `0x381a18`, escritor compartido `0x3816bc` | Lee áreas EXIF/reserva/main/thumb/screennail o RawInfo; prepara JPEG/ARW y escribe por bloques. La construcción requiere buffers válidos y reservas suficientes | VERIFICADO (implementaciones y bifurcación) |
| Escritura al backend de archivos | `libmpr.so:0x381594 → 0x3bd3bc → 0x3bcfbc`; adaptadores `0x3b85a8/0x3b85da` | Tabla de operaciones dfs/FileAcc, alternativas Write y WriteAndFlush; estas últimas llaman Fsys importadas. Falta propagar la tabla y flags concretos de esta escritura hasta su backend | VERIFICADO (aristas/alternativas); NO_VERIFICADO (ruta completa de una toma) |
| SD | `libInfraFsys.so:Fsys_WriteAndFlush 0x15bcc`, `Fsys_Flush 0x16328` | API existente y con despacho interno indirecto. No se demostró nodo SD, montaje, driver, fsync/fdatasync ni durabilidad por captura | VERIFICADO (API); NO_VERIFICADO (persistencia física) |
| Alta del catálogo DCF/AVI | `libmpr.so:0x397116 → 0x22c190` JPEG; `0x39746e → 0x22d1cc` RAW; `0x397494 → 0x22d648` conjunto | Escrituras comprobadas antes de registrar sus contenidos; RecMutex y EntryId en AVI. Registro de conjunto no es por sí mismo commit durable del archivo/índice | VERIFICADO (orden/aristas); NO_VERIFICADO (atomicidad/durabilidad) |
| Respuesta y devolución de recursos | Filtro `0x51458c`, RecStill `0x34c848`, FEA `0x441960/0x441b00`, Obj `0x900648`, `0x8fe110` | Filtro responde con 4 B; RecStill agrega `0x84` B para evento `0x66`; FEA tiene callback `0x40000012` de `0x48` B; falta unir registro/handler de ambos dominios | VERIFICADO (contratos separados); NO_VERIFICADO (correlación completa) |
| Entrada visible en reproducción | APIs MPR `GetContentsCountSync/GetDcfFileInfo/ReadThumbnail/PlayThumbnail`; respuesta Obj `0x3500/0x3002` | Falta consumidor de la respuesta/invalidador de catálogo y consulta por el EntryId recién registrado; tampoco está probado el instante seguro de liberar todos los buffers | NO_VERIFICADO |

## Hallazgos nuevos y revisión de afirmaciones anteriores

### 1. Pre-registro DCF antes de WriteStill: cierre condicional

**ACEPTO — VERIFICADO:** en Execute, el sitio `0x90ba24` llama `0x908084`.
Su rama `0x908154` exige argumento de pre-registro no nulo; `0x90817a` llama
`0x90fcd4`, que decide por modo/medio y alcanza `0x91bbd0 → 0x8fd2fc`.
`0x8fd37e → 0x900124 → PreRegisterDcfContentSync` ya era conocido en S20;
ahora queda situado antes de `0x90bb86` (obtención StillInfo) y `0x90bbdc`
(RecordStill) en este recorrido de Execute. No se convierte en paso universal:
el guard, modos/medios y rutas alternativas pueden omitirlo.

**ACEPTO — VERIFICADO:** `0x93bd60` sigue siendo helper de consulta
`GetEntryIdFromDirectoryFileNumberSync`, no pre-registro ni commit. La frontera
libObj↔libmpr usa funciones C++ y estructuras traducidas. El recorrido AVI
de pre-registro de S20 se reutiliza: `0x71eafc → 0x455630`, AviMMgrIf `+0x38`,
`0x619e84 → 0x673b84 → 0x1d598a → 0x1d6d46 → 0x22e1a0`.

Evidencia nueva: `codex-preregister-{entry,xrefs,execute-callers}.json`,
`codex-obj-buffer-boundary.json`; controles de llamada en el auditor.

### 2. Comando 9: unión Recorder → escritor, con estados intermedios

**ACEPTO — VERIFICADO:**

1. `0x34a934..0x34a93a` envía 9 por `0x2d7d20`, que encola en `this+0x18`
   y despierta el receptor. `0x32d5b2` es **bucle trabajador**, no el switch del comando.
2. El bucle llama `0x32ed34` para esa cola; el comando recibido se entrega por
   slot `+0x30` del controlador. RecStill instala vtable `0x81c0b8`;
   `+0x30 → 0x34b2e4`. TBB[9] alcanza `0x34b310`: pone `+0x956=1`.
3. El slot periódico `+0x28 → 0x34cfa0` despacha por **estado** `this+0x18`.
   En estado 3 llega a `0x34bc58`, consume `+0x956`, configura trabajo y,
   cuando corresponde, cambia a estado 7 (`0x34bd66 → 0x32ee30`).
4. Estado 7 lleva a `0x34cc34`. Su bucle espera estados de cada elemento;
   solo un elemento en estado 2 se configura para escritura. `r6` se inicia
   en `this+0x968` (`0x34cf48/58`) y recorre los punteros a escritor.
   `0x34ceca..0x34ced2` envía comando **5** por su slot `+8`.
5. La identidad del escritor no se deduce del slot: ctor RecStill `0x34b5c8`
   llama `0x34b5a6` y guarda resultados en `+0x968/+0x96c`;
   `0x34b5a6 → 0x513268` instala vtable **StillWriterFilter `0x882e28`**.
   Su hilo `0x5144e4` recibe el comando; TBB para 5 llega a
   `0x51452e → 0x5144b0 → 0x5141ec → dcf_If::WriteDcfFile`.

**NO_VERIFICADO:** que cualquier comando 9 llegue a escribir: necesita
configuración, controlador instalado y completados de los pasos previos.
El camino incluye lectura/procesamiento y estados 1/2/3 por elemento; no se
puede sustituir por «orden 9 = escritura inmediata».

Evidencia: `codex-recstill-{writer-link,command5,dispatch}.json`,
`codex-filter-{command,dispatch-verify}.json`, `codex-command9-followup.json`.

### 3. JPEG, RAW y orden de registro

**ACEPTO — VERIFICADO:** el selector de esta implementación es el word
**StillInfo Linux +`0x6ac`** (no el recMode LIRO en +`0x274`).

| Selector Linux | Implementación recorrida en dcf_AVISequence | Clasificación |
|---|---|---|
| 0 | Rama JPEG: `0x396e78..0x397164` | VERIFICADO |
| 1 | Rama RAW: `0x39735e` acepta 1/2; WriteDcfFile tipo 1 en `0x397376` | VERIFICADO |
| 2 | JPEG y RAW, con reconstrucción del descriptor temporal en `0x397164` | VERIFICADO |
| 3 | JPEG y MPO; WriteDcfFile tipo 2 en `0x39719a` y RegisterMpoInfo `0x39732e` | VERIFICADO |

**VERIFICADO:** rama de archivo JPEG `0x38b064` y RAW `0x381a18` convergen en
`0x3816bc`, desde llamadas `0x38b7e4` y `0x38225e`. El segundo construye ARW
con reserva, thumbnail, información de revelado/registro y datos RAW; no es
«EncodeStill sobre YC renombrado a .ARW». Las rutas DCF `.JPG`/`.ARW` ya
están documentadas; no se ha verificado un archivo materializado.

**ACEPTO — VERIFICADO:** JPEG llama `0x397116 → 0x1d6c76 → 0x22c190`
`RegisterJpegContent`. RAW llama `0x39746e → 0x1d6cb6 → 0x22d1cc`.
El literal de entrada en `0x22d3c8` y el log de mutex identifican
**RegisterRawContent**. Ambas ramas convergen antes de
`0x397494 → 0x1d6cc6 → 0x22d648` RegisterDcfContent.

**RECHAZO — DESCARTADO:** identificar `0x39746e` como RegisterMpoContent
porque su rama de error utiliza esa cadena (`0x82cc2d`). El destino real
y los literales del callee contradicen esa atribución. También hay dos
sobrecargas MPO en `0x22c614/0x22c9b0`; no son los destinos RAW anteriores.

**ACEPTO — VERIFICADO:** en el prólogo de la secuencia AVI, `0x396e24`
llama al escritor antes de `0x396e42` RecStartDcfContent. Después vienen las
escrituras por formato y sus registros. El pre-registro Obj anterior no
altera este orden local. No equivale a una única transacción atómica.

Evidencia: `codex-jpeg-raw-branch.json`, `codex-raw-mode-filewrite.json`,
`codex-raw-fileacc-edges.json` y ventanas S20 `codex-dcf-registration.json`.

### 4. WriteAndFlush, cleanup y límites de rollback

**ACEPTO — VERIFICADO:** el escritor común abre por `0x3533bc`; divide datos
y llama `0x381594` en `0x381958`. El tramo de escritura es
`0x3815c8 → 0x3bd3bc → 0x3bcfbc`; este último selecciona operaciones de la
tabla dfs, incluidos slots `+0x150/+0x17c/+0x180` según sus ramas.
El adaptador `0x3b85be` llama **Fsys_WriteAndFlush@PLT `0x11e604`**
en `0x3b85da`; `0x3b858c` llama **Fsys_Write@PLT `0x11f970`** en `0x3b85a8`.
La tabla relocada contiene `0x9d4100 → 0x3b5161` y
`0x9d4104 → 0x3b5041`, funciones con esas alternativas de escritura.

**NO_VERIFICADO:** propagación de la tabla/flags de la captura hasta uno de
esos adaptadores; no se etiqueta por semejanza de slots como una selección
concreta. La API pública `MprFileIfCore::WriteAndFlush 0x726138` es una
frontera diferente; no se ha unido al escritor JPEG/RAW anterior.

**ACEPTO — VERIFICADO:** hay cleanup real de errores de escritura, más allá
de logs: en `0x38164e` se libera el bloqueo, `0x381658 → 0x3810a0` intenta
cerrar; `0x38166a → 0x3bc1e4` intenta eliminar el archivo y comprueba error
(`Err Remove ec`). La ruta normal también cierra por `0x3819c4 → 0x3810a0`.
No se infiere borrado únicamente de una cadena: las llamadas son explícitas.

**NO_VERIFICADO:** qué fallos llegan a cada rama de cleanup, si un fallo del
registro AVI posterior elimina el archivo ya escrito, o si compensa toda
reserva/alta DCF. `CancelRecStartDcfContent 0x22bd90` existe; el inventario de
branches al wrapper `0x1d6c58` no encontró una arista desde los errores de esta
secuencia. Eso no excluye otras llamadas indirectas ni demuestra cancelación.
`FlushAVIndexFile 0x5135ac` tiene un wrapper `0x5135e8`; no se probó una barrera
de índice por foto anterior al callback de éxito.

Evidencia: `codex-write-content-core.json`, `codex-fileacc-close-write.json`,
`codex-dfs-write-{and-flush,virtual,routing}.json`, `codex-fsys-{callers,adapter}.json`,
`codex-infra-fsys-boundary.json`. La durabilidad SD continúa **NO_VERIFICADA**.

### 5. Completion, Pool y publicación: qué está cerrado y qué no

**ACEPTO — VERIFICADO:** tras procesar la orden 5, el hilo de StillWriterFilter
entrega un resultado de **4 B** por `0x51458c → 0x455b08`; este usa el callback
instalado por `0x455af0`. RecStill instala IDs `0x700/0x800` para sus dos
escritores (`0x34b7aa/ba`), con callback/context del controlador.
Al completar su trabajo, RecStill emite **evento `0x66`, payload `0x84` B**
en `0x34c848 → 0x2d7dd0`. Eso es más preciso que asumir un retorno directo del filtro a Obj.

**ACEPTO — VERIFICADO:** se conserva el tramo S20 de FEA a Obj:
callback `0x40000012`, payload `0x48`, registro en ctor MprAcsr `0x8fda70`,
receptor `0x900648`, construcción `ObjMsg(0x3500,0)` en `0x90081c` y entrega
local por `0x90084c`. Wrapper `0x8fe110` espera y copia esos `0x48` B.

**NO_VERIFICADO:** registro exacto que une el evento Recorder `0x66/0x84`
al handler FEA que procesa el resultado y emite `0x40000012/0x48`. La función
`0x34b138` se obtiene mediante vtable de StillRecorderIf (relocación
`0x81bb50`), no por branch directo. Falta seguir su llamador virtual y la
función/context que registra. No se equiparan ambos payloads.

**RECHAZO — DESCARTADO:** el callback `0x40000012` prueba por sí solo éxito
de archivo/DCF: se emite también en rechazo de parámetros/estado.
**ACEPTO — VERIFICADO:** corrección S20 sobre el rango de `0x45030a`:
`0x40000001..0x40000091`, por aritmética modular, no el rango `0xc000…` de S19.

**RECHAZO — NO_VERIFICADO:** la identificación automática de los clientes
`0x8fc538/0x8fc62e` como «SetImageWrited después de WriteStill» en S12.
Ambos construyen sobre **`0x6108/0x1009`**, pero llevan selector `0x3001=1/2`
y datos de contexto `0x1002`; el primero, vía `0x8fd38e`, devuelve incluso
**StillInfo `0x6b0`** al llamador `0x90f698`. También hay una llamada a
`0x90f804` antes de RecordStill (`0x90bae8`). El número externo del sobre
no basta para asignar su operación efectiva ni su orden respecto al commit.
**ACEPTO — VERIFICADO:** el handler Pool `0x939dd8 → 0x932a44` sí existe y
marca imagen/libera referencias; el enlace concreto desde esos clientes
necesita resolver el despachador y selectores, no se da por cerrado.

**NO_VERIFICADO:** invalidación/actualización de biblioteca a partir de
RegisterDcfContent o de la respuesta final Recorder `0x3500/0x3002`, con
`0x1001` resultado y `0x100f` información de contenido. Las APIs de consulta
y reproducción pueden leer el catálogo; falta probar que leen esta entrada
tras la escritura. No se ha demostrado el primer instante en que el JPEG/RAW
puede verse ni en que el productor pueda reciclar todos los buffers.

## Interfaz con adquisición/mecánica y posible fuente alternativa

**VERIFICADO:** esta mitad consume descriptores YC o StillInfo, identificación
de captura, metadatos, sesión/medio y objetos/líneas de grabación activos.
Las ventanas de escritura estudiadas no incluyen una orden directa a Darwin
ni GPIO de cortinas. **NO_VERIFICADO:** que toda su preparación sea independiente
del estado mecánico o que permita comenzar sin el recorrido nativo de captura.

**INFERENCIA:** la API que escribe una imagen ya disponible en Pool
(`ObjStillRecorderCore::WriteStill 0x909a84`, orden `0x10000003`) y las rutas
PbCap/edición son candidatas para reutilizar esta mitad sin adquirir otra
imagen en ese momento. No constituyen evidencia de adquisición electrónica
de foto completa. **HIPOTESIS:** un frame electrónico compatible podría
alimentarlas si satisface contrato YC, geometría, caché, vida útil, metadatos,
estado y registro; ninguna instancia así está validada.

**DESCARTADO:** dar el JPEG de SFRA como entrada YC de Execute, inferir el
YC Camera a partir de registros IMX210, atribuir raster a la SDS de `0x800` B,
o presentar RawPlay/DevLater como adquisición RAW nueva: S20 lo sigue desde
un `.ARW` existente en tarjeta. No se ha demostrado una ruta sin movimiento
mecánico de extremo a extremo.

## Diagrama del tramo

```text
fin exposición / última línea / DMA
          ? contrato y entrega efectiva
          +--> LIRO JPEG/RAW --> Stage_Notify [0x28c descriptores]
          |                            ? receptor/traducción completa
          +--> Camera YC --> Effect/SDF ? --> PlayData
          |                                  |
          +--> SFRA --> JPEG DMM --> ISS      +--> Recorder EncodeStill
                 (rama Live View separada)         ? completion codificación
                                                  v
                          Pool / StillInfo Linux 0x6b0
                          | pre-registro DCF condicional
                          v
                Obj RecordStill --> MprIf/FeaCore WriteStill
                          --> StillRecorderIf --> comando 9 en cola
                          --> Recorder worker --> RecStill flag +0x956
                          --> estado 3 --> pasos intermedios --> estado 7
                          --> StillWriterFilter comando 5
                          --> dcf_If [AVI != NULL ? AVISequence : Sequence]
                          --> WriteJpgFile / WriteRawFile
                          --> escritor común --> dfs/FileAcc
                                                 ? tabla/flags concretos
                                                 --> Fsys Write[AndFlush]
                                                     ? backend SD / durabilidad
                          --> RegisterJpegContent / RegisterRawContent
                          --> RegisterDcfContent
                          --> filtro resultado 4 B --> RecStill 0x66/0x84
                                                     ? registro/handler FEA
                          --> FEA 0x40000012/0x48 --> MprAcsr --> Obj respuesta
                                                                            ?
                                                catálogo / DCIM / reproducción
errores de escritura --> close/remove (rutas existentes)
errores de registro  --> ? compensación de archivo, pre-registro e índice
```

## Huecos restantes y siguiente paso concreto

| Hueco | Estado | Comprobación estática siguiente |
|---|---|---|
| Último frame sensor/DMA → descriptor válido | NO_VERIFICADO | Tramo Claude: entregar productor, evento final y contrato DMM efectivo; distinguir still nativo, YC Camera y SFRA |
| Completion EncodeStill y vida útil YC | NO_VERIFICADO | Propagar AddCallbackFunc de StillConverter, ID local `0x4000007c`, su hilo/EventReceiver y liberadores hasta el resultado que usa Pool |
| Selección concreta AVI y FileAcc/Fsys | NO_VERIFICADO | Seguir campo Writer+`0x78` y objeto DCF del medio desde `0x34b878/0x34b9de`, luego tabla dfs cargada en `0x3bcfbc`; resolver slots `0x150/0x17c/0x180` y flags |
| Resultado Recorder → FEA | NO_VERIFICADO | **Prioridad inmediata:** localizar quien carga `0x81bb50`/llama su slot 0 (`0x34b138`), resolver fn/target/context y seguir evento `0x66` de `0x34c848` hasta handler `0x441694…` |
| Pool SetImageWrited y orden real | NO_VERIFICADO | Seguir receptor de `0x8fc184` y selectores del sobre `0x6108/0x1009`; unirlos explícitamente con `0x939dd8 → 0x932a44` |
| Rollback de alta DCF y archivo | NO_VERIFICADO | Seguir errores posteriores a `0x397116/0x39746e/0x397494`, no solo errores de Write; comprobar compensación de `0x22e1a0` y llamadas a cancelación/remove/flush |
| Primera visibilidad en biblioteca | NO_VERIFICADO | Resolver consumidor de `0x3500/0x3002`/`0x100f` y el cambio de catálogo desde `0x22d648`; correlacionar EntryId con consultas de reproducción |

**VERIFICADO — validación:** auditor estático PASS; JSON de evidencia válido;
ruff/mypy sobre los dos scripts propios: **PASS, sin avisos**. Se ejecutaron
también las órdenes solicitadas sobre `src tests`/`src` del proyecto actual;
su resultado se registra en [codex-validation.json](../../analysis/session21/evidence/codex-validation.json):
mypy src **PASS**; ruff src/tests encuentra **9 avisos en cuatro tests ajenos
no modificados**. No se instalaron paquetes. No se conectó/flasheó cámara ni se modificaron originales,
no se usaron subagentes ni se ejecutó firmware. Sin commit ni push: el
directorio no es un repositorio Git. Contexto y checkpoint se actualizan
añadiendo una entrada, preservando el historial anterior.

**VEREDICTO: CAMBIOS** — faltan las aristas indicadas para considerar completo
el objetivo exposición → biblioteca; los cierres parciales nuevos no cambian
la arquitectura **A > E > P ≈ E2**.
