# S20 — cadena MPR/DCF posterior a WriteStill

**VERIFICADO:** recuperadas la frontera Obj→MPR, las dos APIs DCF con sus
referencias estáticas, una secuencia que escribe datos y después registra
JPEG/contenido DCF, y el receptor del callback `0x40000012`.
**NO_VERIFICADO:** cadena completa de una solicitud concreta entre los
despachadores asíncronos, selección efectiva del secuenciador, rollback
transaccional y persistencia/publicación real en SD/reproducción.

**VERIFICADO:** el orden de evaluación se conserva: **A > E > P ≈ E2**.
SilentShutter no se declara funcional.

## Alcance y trazabilidad

**VERIFICADO:** análisis estático local, sin cámara, flasheo, instalaciones,
ejecución del firmware, subagentes ni modificaciones de originales. Se leyeron
CONTEXT.md y los tres informes S20 indicados; se inventariaron analysis/,
analysis/session20/evidence/ y scripts/, incluida la evidencia S19-08.
Se reutilizaron `scripts/rtti_vtables.py`, `scripts/func_owner.py`, el RTTI
de libObj y `/tmp/s20work/libObj-full.disasm`. No se reextrajo el firmware.
Para libmpr, sin desensamblado completo reutilizable en el inventario, se
realizaron barridos LLVM y se conservaron ventanas nuevas en `codex-dcf-*.json`.

**VERIFICADO:** todas las VA siguientes son **ELF**, código Thumb salvo PLT ARM.
El ELF original está bajo `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/`.

| ELF | SHA256 comprobado |
|---|---|
| libmpr.so | `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30` |
| libObj.so | `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a` |

**VERIFICADO:** `llvm-nm` sitúa `FeaCore::WriteStill` en **0x440794**.
La decompilación antigua de `analysis/ghidra/libmpr-writestill.json` está
basada en `0x450794` y sus llamadas llevan `+0x10000`; aquí no se mezclan
esas VA con las ELF. Las etiquetas LLVM por símbolo anterior tampoco
atribuyen funciones: `PlayStill+…`, `FlashLib+…` y `FileAccCache+…` en los
JSON son texto del desensamblador, no identidad de clase.

## 1. APIs DCF: llamadores y destinos

**VERIFICADO:** se examinaron branches directos `bl/blx/b/b.w`, relocaciones
de todas las secciones SHT_REL —incluidos GLOB_DAT/JUMP_SLOT— y entradas RTTI.
El barrido de símbolos de `lib/*.so` encuentra solamente libObj como
importador de estas dos APIs. Esto acota el inventario; no excluye punteros
calculados, `dlsym`, otros ejecutables ni código ARM oculto al barrido Thumb.

| API / referencia | Llamador o despacho | Clase/método y relación con still | Clasificación |
|---|---|---|---|
| PreRegisterDcfContentSync **0x71eafc** | **0** branches directos, **0** relocaciones, **0** entradas virtuales hacia la API dentro de libmpr | API pública no virtual; no es un paso posterior invocado por WriteAndFlush | VERIFICADO |
| GetEntryIdFromDirectoryFileNumberSync **0x71eb70** | **0** branches directos, **0** relocaciones, **0** entradas virtuales hacia la API dentro de libmpr | API pública no virtual de consulta | VERIFICADO |
| PreRegister: import libObj | **0x900180 → PLT 0xdd1f0 → GOT 0x102d568** | Helper **0x900124**; cadenas MprAcsr.cpp/PreRegisterDcfContentSync, contexto MprIf en `this+0x18` | VERIFICADO (arista); INFERENCIA (atribución no exportada) |
| Lookup: import libObj | **0x93be94 → PLT 0xdb978 → GOT 0x102cda0** | Helper **0x93bd60**, cadena MprAcsr.cpp/GetEntryIdFromDirectoryFileNumber; consulta del entorno Pool | VERIFICADO (arista); INFERENCIA (atribución concreta) |
| PreRegister: helper de libObj | **0x8fd37e → 0x900124** | Función real **0x8fd2fc**: lee Struct `0x1012`, convierte LocalTime y arma flags JPEG/MPO/RAW | VERIFICADO; orden relativo a WriteStill NO_VERIFICADO |
| Lookup: helper de libObj | **0x932c20, 0x932fda, 0x933a64, 0x933d9e, 0x93459a → 0x93bd60** | Funciones contenedoras candidatas **0x932b40, 0x932ee8, 0x933958, 0x933c8c, 0x9342e0**; no hay nombres exportados exactos | VERIFICADO (sitios); NO_VERIFICADO (atribución/momento exactos de cada operación) |
| PreRegister: salida libmpr | **0x71eb50 → 0x455630 → blx en 0x45569e** | Objeto pasado como mediaId, slot virtual **+0x38**; NULL devuelve 5 | VERIFICADO |
| Lookup: salida libmpr | **0x71ebcc → 0x4555b2 → blx en 0x455612** | Objeto de medio, slot virtual **+0x34**; NULL devuelve 5 | VERIFICADO |

**VERIFICADO:** los `b` en la zona PLT de libObj son veneers de interworking;
no constituyen otros consumidores de negocio. Las dos relocaciones externas
son R_ARM_JUMP_SLOT (22); libmpr no tiene relocaciones por esos nombres.
La ausencia de entrada virtual de la API no elimina el despacho virtual
**dentro** de ella.

| Vtable / clase | +0x38, pre-registro | +0x34, lookup | Clasificación |
|---|---|---|---|
| **0x9067a8 AviMMgrIf** | **0x66aa14 → 0x619e84** | **0x66aa74 → 0x61b810** | VERIFICADO |
| **0x907c50 MMgrIf**; **0x9078b8 BgmMMgrIf** | **0x66c02a** | **0x66c022** | VERIFICADO: implementaciones predeterminadas devuelven `0x2c` |

**VERIFICADO:** la implementación AviMMgr de pre-registro sigue
`0x619e84 → 0x673b84 → 0x1d598a → 0x1d6d46 → 0x22e1a0`.
Las cadenas identifican `PreRegisterDcfContent` y `AviSeqRec.cpp`, con
RecMutex, flags de existencia y salida `ValidPreRegister`.
El lookup sigue `0x61b810 → 0x673b18 → 0x1d53da → 0x1d73aa → 0x22338c`;
este último se identifica como `GetEntryIDFromDirectoryFileNumber` en
`AviSeqPlay.cpp`. **DESCARTADO:** tratar el lookup como un commit.

Evidencia: [inventario inicial](../../analysis/session20/evidence/codex-dcf-mpr-initial.json),
[imports y llamadores Obj](../../analysis/session20/evidence/codex-dcf-obj-preregister.json),
[helpers Obj](../../analysis/session20/evidence/codex-dcf-obj-handlers.json),
[gestor](../../analysis/session20/evidence/codex-dcf-media.json),
[destinos](../../analysis/session20/evidence/codex-dcf-downstream.json),
[pre-registro](../../analysis/session20/evidence/codex-dcf-index.json),
[lookup](../../analysis/session20/evidence/codex-dcf-endpoints.json).

## 2. Frontera ObjStillRecorder → WriteStill

| Arista | Evidencia / interpretación | Clasificación |
|---|---|---|
| RecordStill **0x908afc**, llamada **0x908d9c → 0x8fe0a0** | Camino nativo ya descrito en pool-write-completion; confirmado en desensamblado reutilizado | VERIFICADO |
| ObjStillRecorderCore::WriteStill **0x909a84**, llamada **0x90a172 → 0x8fe0a0** | Entrada alternativa por orden **0x10000003**, imagen previamente disponible en Pool; semántica de orden reutilizada del informe anterior | VERIFICADO (arista y evidencia previa) |
| **0x8fe0f0 → MprIf::WriteStill@PLT 0xe0f70** | Llamada de función C++ con WriteStillParam/StillInfo/count; no entra un ObjMsg directamente a libmpr | VERIFICADO |
| Nombre de **0x8fe0a0** | Log `[MprAcsr] WriteStill`, fuente MprAcsr.cpp y layout del constructor **0x8fda70**. La etiqueta anterior «MprCtrl::WriteStill» no es símbolo exportado de esta función | INFERENCIA: MprAcsr::WriteStill |
| **0x71cfb4**, tail-call **0x71cfd2**; **0x71cfd6**, llamada **0x71cffa** | Son los dos llamadores de negocio recuperados de **FeaIf::WriteStill 0x44f784**, por PLT/GOT **0x9c3744**, entradas **0x11ddcc/0x11ddd0** | VERIFICADO |
| FeaIf::WriteStill | Encola por interfaz virtual; no tiene entrada de vtable ni relocación directa recuperada hacia su cuerpo | VERIFICADO |
| FeaCore::WriteStill **0x440794** | Recibe desde llamadas **0x42a236** y **0x43fc86** vía PLT **0x120060**; valida y prepara el escritor | VERIFICADO |
| **0x440aee → 0x34b1be → 0x34adb4**; **0x440b50 → 0x34b1cc → 0x34a92c** | StillRecorderIf, preparación y lanzamiento; el segundo envía comando **9** por **0x2d7d20** | VERIFICADO (código); INFERENCIA (nombres de métodos privados) |

**VERIFICADO:** `0x8fe110..0x8fe15e` espera `WaitEvent(-1)`, recibe un
ObjMsg, obtiene Struct paramId **0** y copia **0x48 bytes** al resultado.
Es una espera de respuesta asíncrona. **DESCARTADO:** equiparar el retorno
inmediato de FeaIf::WriteStill con esa respuesta o con un archivo durable.

Evidencia: [frontera](../../analysis/session20/evidence/codex-dcf-obj-boundary.json),
[recepción](../../analysis/session20/evidence/codex-dcf-callback.json),
[StillRecorderIf](../../analysis/session20/evidence/codex-dcf-media.json).
No se analizaron ni modificaron topologías `0xae–0xb4`, SequenceStillCaptureStart
ni documentos `s20-claude-*`.

## 3. Quién escribe y quién registra DCF

**VERIFICADO:** el dispatcher virtual de **StillWriterFilter** está en
**0x5144e4**, vtable **0x882e28**, slot **+0xc**. Su rama
`0x514530 → 0x5144b0 → 0x5141ec` llega a
**0x514366 → dcf_If::WriteDcfFile 0x3a2e74**.
Este wrapper serializa la operación y llama al objeto `this+4`, slot **+0x48**
(`0x3a2ec8`). No se elige una clase solo porque tenga ese mismo número de slot.

| Receptor concreto del slot +0x48 | Evidencia | Clasificación |
|---|---|---|
| **dcf_AVISequence**, vtable **0x82df28**, método **0x396dcc** | Fábrica **0x3a8508 → ctor 0x39b9c4**; el ctor instala esa vtable desde literal **0x39b9e8** y guarda AVI en `+0x71c` | VERIFICADO |
| **dcf_Sequence**, vtable **0x832050**, método **0x3a8e24** | Fábrica **0x3a8554 → 0x3a9740/0x3a9758**; método selecciona variantes de **0x38c220** por tipo de imagen | VERIFICADO |
| **dcf_Lib +0x48 = 0x37ac74** | Pertenece a otra interfaz; lleva a reserva/backup de tabla **0x35a420**, no al WriteDcfFile buscado | DESCARTADO como destino por mera coincidencia de slot |

**VERIFICADO:** hay dos fábricas distintas, y los constructores dcf_If
**0x3a83bc/0x3a842c** pueden invocar ambas usando el mismo campo de salida.
**NO_VERIFICADO:** cuál queda instalada para cada solicitud still concreta.
La secuencia AVI siguiente está verificada como implementación existente,
no como ejecución de una toma Silent.

| Operación en dcf_AVISequence::WriteDcfFile | Sitio y destino | Clasificación |
|---|---|---|
| Inicia registro | **0x396e42 → 0x1d6c4a → 0x22bcbc**, `RecStartDcfContent` | VERIFICADO |
| Escribe datos | **0x396e24 → 0x38c220**, identificado por `dcf_Lib::WriteDcfFile Start/End`; se comprueba el retorno antes de continuar | VERIFICADO |
| Registra JPEG | **0x397116 → 0x1d6c76 → 0x22c190**, `RegisterJpegContent`, fuente AviSeqRec.cpp, RecMutex y EntryId | VERIFICADO |
| Confirma conjunto DCF | **0x397494 → 0x1d6cc6 → 0x22d648**, `RegisterDcfContent`, después de las ramas JPEG/RAW/MPO | VERIFICADO (orden/arista); INFERENCIA (equivalencia a commit transaccional durable) |
| Error | El retorno no cero de RegisterJpegContent salta al diagnóstico **0x3974ac**, que pasa por **0x393928** y conversión **0x3a1554** | VERIFICADO; no demuestra rollback |
| Cancelación disponible | **0x22bd90**, identificada como `CancelRecStartDcfContent` | VERIFICADO (operación existente); NO_VERIFICADO (arista desde cada fallo de escritura/registro) |

**VERIFICADO:** el inicio `RecStartDcfContent` aparece **después** de la
llamada inicial a **0x38c220** en la rama examinada (`0x396e24` antes de
`0x396e42`); la tabla enumera las operaciones, no implica una reserva previa
a esa escritura. En cambio RegisterJpegContent y RegisterDcfContent sí
ocurren después. **NO_VERIFICADO:** si la etapa previa ya reservó DCF por
otra operación antes de entrar aquí.

**VERIFICADO:** **0x38c220** llama auxiliares de escritura y manejo de tabla
`0x38bf14/0x38b958/0x35f49c`; esto no se sustituye por una llamada asumida
a MprFileIf::WriteAndFlush. **NO_VERIFICADO:** contrato durable de esos
auxiliares y reversión de sus efectos si falla después el registro AVI.

**VERIFICADO:** el filtro expone por separado
**0x5135ac → 0x3a32ec**, `dcf_If::FlushAVIndexFile`.
**NO_VERIFICADO:** que se ejecute tras cada still y antes del callback de
éxito. La operación existe; no constituye una barrera demostrada aquí.

**VERIFICADO:** la frontera antigua `MprFileIfCore::WriteAndFlush 0x726138`
se acota por RTTI: slot **+0x290** de **AviMMgr**
(`vtable 0x8e6e58`) apunta a **0x649364**; las bases MMgr/DiscMMgr apuntan
a **0x64befc**, implementación de error. **NO_VERIFICADO:** que el handle
del still llegue a esa ruta. No se conectó `0x13df20` con el commit DCF;
sus auxiliares siguen siendo diagnóstico y conversión, según el informe previo.

Evidencia: [filtro y WriteDcfFile](../../analysis/session20/evidence/codex-dcf-index.json),
[RTTI y secuencias](../../analysis/session20/evidence/codex-dcf-sequence-real.json),
[constructor](../../analysis/session20/evidence/codex-dcf-rollback.json),
[registro JPEG/DCF](../../analysis/session20/evidence/codex-dcf-registration.json),
[implementaciones AVI y escritor](../../analysis/session20/evidence/codex-dcf-avi-register.json),
[salida/error](../../analysis/session20/evidence/codex-dcf-finish.json),
[flush](../../analysis/session20/evidence/codex-dcf-filewrite.json).

## 4. Callback de finalización y corrección numérica

| Paso | Evidencia VA | Clasificación |
|---|---|---|
| Emisión FEA | En error de validación **0x440bde..0x440be6**, y en tratamiento posterior **0x441960..0x44196a / 0x441b00..0x441b0c**, slot virtual **+0x1c**, ID literal **0x40000012**, payload **0x48** | VERIFICADO |
| Método del slot | Vtable FeaCore **0x858008 +0x1c → 0x429000**; **0x42917e..0x42918c** invoca callback almacenado en `this+0x10` con target/context de `+0x14/+0x18` | VERIFICADO |
| Registro del receptor Obj | Ctor **0x8fda70** crea loopback EventSender `+8` → EventReceiver `+0xc`, handler `+0x10`; tabla de 12 entradas en pila, **0x8fdb1c/1e** fija eventId `0x40000012`; **0x8fdb98** llama AddCallbackFunc | VERIFICADO |
| Función registrada | GOT **0x10329cc → 0x900649** (Thumb **0x900648**), resuelto desde base GOT **0x102cbd0** y offset **0x5dfc** | VERIFICADO |
| Consumo ID12 | **0x9006b0..0x9006b4 → 0x90081c**; construye ObjMsg **0x3500/0**, Struct **0x48**, paramId **0**; **0x90084c** llama EventSender local | VERIFICADO |
| Retorno al solicitante | **0x8fe110..0x8fe15e**, recepción y copia del mismo tamaño/paramId | VERIFICADO (contrato); INFERENCIA (correlación de una solicitud concreta sin traza) |

**VERIFICADO, corrección de S19-06:** en **0x45030a..0x450312**,
`add.w r3,r4,#0xc0000000; subs r3,#1; cmp r3,#0x90; bhi ...`
acepta **0x40000001..0x40000091**, no `0xc0000001..0xc0000091`.
Se trata de aritmética módulo 2^32. El callback **0x40000012** entra en ese
rango; no hace falta inventar una traducción desde `0xc0000012` para unirlo
a EventSwitcher. El registro genérico de MprCtrl y el despacho de FeaIf
se reutilizan de S19-06; no se ha vuelto a decompilar libmprctrl.

**DESCARTADO:** considerar ese evento certificado de escritura/DCF por sí
solo: también se emite al rechazar parámetros o estado **antes** de escribir.
Debe comprobarse el resultado del payload y la ruta que lo generó.

Evidencia: [emisor](../../analysis/session20/evidence/codex-dcf-mpr-initial.json),
[dispatch FEA](../../analysis/session20/evidence/codex-dcf-endpoints.json),
[registro Obj](../../analysis/session20/evidence/codex-dcf-obj-events.json),
[callback Obj](../../analysis/session20/evidence/codex-dcf-callback.json),
[constantes y contrato](../../analysis/session20/evidence/codex-dcf-audit.json).

## 5. Fronteras abiertas y siguiente paso concreto

| Falta | Clasificación | Siguiente comprobación estática |
|---|---|---|
| Unir StillRecorderIf/cola del Recorder al filtro concreto | NO_VERIFICADO | Seguir comando **9** de **0x34a92c → 0x2d7d20** y el despacho heredado **Recorder 0x32d5b2**, hasta la creación/selección de StillWriterFilter y su comando de escritura |
| Selección efectiva dcf_AVISequence/dcf_Sequence | NO_VERIFICADO | Propagar parámetros del ctor dcf_If **0x3a83bc/0x3a842c** y del llamador hacia las fábricas **0x3a8508/0x3a8554**; contrastar el campo `this+4` usado en **0x3a2ec8** |
| Retorno exacto del escritor hacia el handler FEA posterior | NO_VERIFICADO | Recuperar entrada y registro del handler que contiene **0x441694..0x441b82**, sin atribuirlo por cercanía a MakeWriteStillImage; seguir el payload del Recorder hasta ID **0x40000012** |
| Rollback de archivos parciales y del índice AVI tras error | NO_VERIFICADO | Seguir la arista de cancelación **0x1d6c58 → 0x22bd90** y errores **0x397124 / 0x3974ac**; comprobar unlink/reversión, no solo el mapeador **0x3a1554** |
| Persistencia, flush de índice y reproducción | NO_VERIFICADO | Seguir **0x38bf14/0x38b958** al filesystem, y llamadores de **0x5135ac**; unir después el EntryId confirmado con invalidación/publicación del catálogo |
| Orden SetImageWrited/0x3500–0x3002 | NO_VERIFICADO | Reutilizar pool-write-completion y seguir **0x8fd3b0/0x8fd498/0x8fd4b4 → 0x8fc538/0x8fc62e**; no confundir marca Pool con commit DCF |
| Llamadores indirectos calculados de las APIs públicas | NO_VERIFICADO | Resolver flujos que carguen sus direcciones fuera de relocaciones/RTTI; el inventario negativo no prueba ausencia universal |

**INFERENCIA:** el registro final está en el secuenciador DCF/AVI que coordina
la escritura y el índice, no en el post-procesado diagnóstico de `0x13df20`.
**NO_VERIFICADO:** que las piezas estáticas descritas completen una toma
Silent concreta o hagan visible una imagen durable en SD/reproducción.

## Validación y reproducción

**VERIFICADO:** `python3 -B analysis/session20/evidence/codex-dcf-audit.py`
comprueba RTTI con controles positivos, relocaciones completas por nombre,
imports de las bibliotecas, vtable instalada por el ctor, callback GOT,
constantes/eventos y SHA256 antes/después. Resultado **PASS** en
[codex-dcf-audit.json](../../analysis/session20/evidence/codex-dcf-audit.json).

**VERIFICADO:** el sondeo reproducible
`python3 -B analysis/session20/evidence/codex-dcf-probe.py libmpr.so 0x71eafc 0x71eb70 0x71eafc:0x71ebe8`
emite callers, relocaciones, RTTI y ventanas. Para libObj reutiliza el
desensamblado indicado; debe conservarse ese temporal para repetir su barrido.
Los `window_owners` son candidatos de func_owner; las atribuciones aceptadas
son las contrastadas en este informe/audit, no cualquier export anterior.

**VERIFICADO:** ruff y mypy, con los ejecutables del entorno indicado,
sin avisos en los dos scripts de evidencia nuevos. Se aplicaron al alcance
modificado; no se ejecutaron `src/tests` de otro proyecto ni se corrigió
código ajeno. JSON de evidencia/checkpoint validado; checkpoint releído antes
del append. Sin commit ni push: `git status` informa que este directorio no
es un repositorio Git utilizable.
