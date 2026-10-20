# Veredicto continuo Claude — Sesión 20 (investigación directa, sin Codex)

## S20-CORRECTIONS

**COMPLETADO.** Se verificaron y corrigieron tres inconsistencias de sesión 19
señaladas al inicio de sesión 20: (C1) ObjId 53 es el objeto ORIGEN de la fila
de topología `0xb4`, no la clase `ObjStillRecorder` — esa es el objeto
DESTINO (ObjId 11/0x0b), ya corroborada por su constructor real `0x9178f0`;
la clase de ObjId 53 sigue NO_VERIFICADA. (C2) La tabla `0x43edccf8` SÍ es
reconstruible estáticamente vía su inicializador `0x437ebed8` + resolución de
punteros GOT — esto ya estaba demostrado en sesión 18 (`s18-main-init-437ebed8.md`)
y confirmado en S19-07; la afirmación de S19-12 de que "no son recuperables
de la imagen estática" quedaba retirada por contradecir evidencia ya presente
en el proyecto. (C3) Los modos 2/4/5 de ObjEffect declarados inválidos por
S19-11 lo son solo en el dispatcher/filtro concreto examinado (`0x176294`/
`0x176cc6`); los resúmenes en `RESEARCH_TASKS.md`/`CONTEXT.md` generalizaban
sin ese calificador y fueron corregidos. Detalle completo:
`docs/capture/s20-s19-corrections.md`.

## S20-RAWPLAY (S19-14 retomada)

**PARCIAL, con la cadena principal CERRADA.** Las cadenas de diagnóstico
`Stage_RawPlayInit`/`ycc_rawplay`/`sds_ycc_handle` no tienen ninguna
referencia de código registrada en el proyecto Ghidra
(`QuerySilentReferences.java`); esto no prueba ausencia de uso, solo ausencia
de referencia estática localizada. El clúster de etapas con nombre vecino —
`Stage_DevLater`, `Stage_Notify`, `Stage_Apollo` (nombre no documentado en
sesiones previas), `Stage_Orientation` (tampoco documentada) — sí se
decompiló realmente y comparte la misma estructura de contexto
(`ctx+0x4ad0`, `ctx+0x4ad4`, `ctx+0x4b54..0x4fe0`) que las filas LIRO
convencionales ya caracterizadas en S19-07/S19-12.

Se decompiló la cadena completa hacia `Stage_DevLater`:
`FUN_43afe192 → FUN_437edd44 → FUN_437edd1c → FUN_437edd04 → FUN_43561604 →
FUN_437edaf8`. **Resultado VERIFICADO y decisivo**: `FUN_437edd44` abre y
parsea un archivo **`.ARW` real desde la tarjeta SD** (ruta
`DCIM/100MSDCF/DSC%05d.ARW`), localizando las etiquetas TIFF `0x111`
(StripOffsets) y `0x117` (StripByteCounts) para extraer el strip crudo. El
bloque de 0x70 B que `FUN_437edd04` entrega a `Stage_DevLater` es
configuración/ruta, no píxeles. **Esto responde negativamente, para esta
ruta concreta, la pregunta central de S19-14**: Stage_RawPlayInit/DevLater
revela (`develop`) un `.ARW` que ya debe existir en la tarjeta —escrito por
una captura RAW previa—, no un buffer YC de Live View en memoria. No es una
vía para generar una fotografía nueva sin haber ejecutado antes una
adquisición de sensor.

Independientemente de esa cadena, se verificó un mecanismo general de
guardar/recuperar un descriptor de 3 palabras (función `0x437ef8cc`, llamada
desde los dispatchers genéricos `0x43afe9f4`/`0x43afe11a` ya citados por
nombre en S19-07, y gateada por `0x43ae7648`), compartido por
`Stage_Notify`/`Stage_Apollo`/`Stage_Orientation`. No se determinó si, en
algún caso distinto de la cadena RawPlay ya cerrada, ese descriptor puede
apuntar a un buffer YC de Live View — éste es el bloqueo que queda abierto
(decompilar `FUN_43ae75dc`, el getter de contexto común a todas las
etapas). También se halló una conexión nueva entre este clúster y la unidad
SDS `0xe0b00` (ya confirmada en S19-05) a través de una ruta de parámetros
SPICA/TAP, y una familia de unit-types de raster `0x50b0b`/`0x50b2e`
distinta de `0x50b3f`. SilentShutter no se declara funcional. Detalle
completo: `docs/capture/s20-rawplay-stage-reuse.md`.

## S20-ROW78 y extensión

**COMPLETADO.** `FUN_43ae75dc` es un getter trivial. Los 6 llamadores reales
de `FUN_43afe9f4` son las filas LIRO `0x50/0x64/0x78/~0xf0/~0x118`. La fila
`0x78` llama en su estado inicial al selector real de sensor `0x437f7ff0` —
no es independiente del sensor. `ctx+0x4b70` conecta Stage_DevLater con la
espera "RawDevInit_WAIT_IMG_PARAM" de esta fila. `FUN_43afe11a` (hermano de
`43afe9f4`) resultó ser la preparación de dimensiones previa a Stage_Apollo;
se detectó una segunda instancia paralela del mecanismo de descriptor sobre
`ctx+0x6e4/8/c`. Detalle: `docs/capture/s20-row78-sensor-selector-link.md`.

## S20-P3 (contrato YC de ObjCamera.out0): intento sin cierre

**PARCIAL, limitado por herramienta.** Ghidra no decompila correctamente
`libObj.so` en el proyecto `a6000-libs` (resultado inválido, patrón de
excepción C++). Con `llvm-objdump` directo: **VERIFICADO** que ninguna de
las 464 llamadas a `MWF::ObjPin::Send` en todo `libObj.so` cae dentro del
código de construcción ya verificado de `ObjCamera`. Un sitio candidato
(`0x98f974`) no pudo atribuirse con confianza a la clase `ObjCamera` por
falta de límites de función recuperados en este binario *stripped*. P3
sigue NO_VERIFICADO. Detalle: `docs/capture/s20-p3-objcamera-pin-attempt.md`.

## S20-P1 (puente S2 → CaptureStart): progreso mayor sobre el buzón `0x40193`

**PARCIAL, con avance sustancial.** **VERIFICADO**: el buzón `0x40193` es
la entrada de un **servicio RPC síncrono** (helpers genéricos
`FUN_43b04cd4`/`FUN_43b04ca2`: envían una petición a `0x40193` con un
`reply_to` propio y esperan la respuesta en su propio buzón) — no un simple
sumidero. **VERIFICADO**: se identificó un cliente real y nombrado,
`CapIdTblMgr` (`FUN_4381cc7c`), con su propio buzón `0x4015e`, que despacha
cuatro comandos (`GetTblAddr/StartAccess/StopAccess/Init_End`) vía la tabla
`0x43bf3800` — la misma región que la tabla de despacho de `0x3011` ya
citaba como destino de punteros constantes, conectando ambos hallazgos por
primera vez. **DESCARTADO**: que CapIdTblMgr sea el puente hacia
CaptureStart. **NO_VERIFICADO**: la identidad del servidor real de `0x40193`
(no está entre las 55 funciones que lo referencian — todas son clientes); si
algún `reply_to` de otro cliente coincide con el dominio `0x100`.

**Hallazgo adicional (registro de `FUN_43aeaa4a`)**: la función que clasifica
eventos del dominio `0x40193`/`0x1502c7` y llama directamente a RelMgr
(`FUN_43aeaa4a`) está **registrada declarativamente con ID `0x4044`** en una
tabla real de 35 filas `{id,fn,pad}` en `0x43ffff84` (única ocurrencia del
puntero Thumb en todo el blob). Se verificó que esta tabla **no es** la
tabla de 220 filas ya conocida (`0x43fff30c`, leída por el dispatcher ya
documentado `FUN_438052d8`, confirmado cableado a esa dirección exacta y a
220 iteraciones) — son dos tablas de despacho independientes con el mismo
formato, y la tabla nueva también contiene el set completo de 23 comandos
`0xd0xx` (CapIdTblMgr solo usa 4 de ellos en su propia tabla). El dispatcher
real que lee la tabla nueva sigue sin identificarse. Se descubrió además un
desfase de direccionamiento de +0x1F0 en `analysis/av-cam-analysis-view.elf`
frente a la convención de direcciones del proyecto (documentado y
corregido), y se descartó una pista de búsqueda por literal `0x4044` que
resultó ser una coincidencia con un offset GOT no relacionado. No se declara
cerrado el puente S2→CaptureStart.

**Cierre de la ambigüedad (a)/(b)**: se decompilaron los 52 sitios
restantes de referencia a `0x40193` — todos son wrappers que envían
`{tag=5, id_u16, 0}` (familia `0x40xx/0xd0xx`). **Hallazgo decisivo**:
`0x4379e6a8` (puerta de admisión de RelMgr) envía `0x4045` a `0x40193`
condicionalmente y registra el diagnóstico nuevo `0x3012`; el handler de
`0x4045` en la tabla (`0x43aea9f0`) es estructuralmente idéntico al de
`0x4044` (clasifica → correla → llama a RelMgr). **Los únicos llamadores de
`0x4379e6a8` son 5 sitios dentro de la propia `FUN_4379d838` (RelMgr)** —
confirma que es un sub-helper interno. **Se resuelve la ambigüedad a favor
de (a): es retroalimentación interna de RelMgr sobre sus propias
autoconsultas, NO la entrada de hardware S2.** Se precisa
`shutter-trigger-chain-0x3011.md`: el mensaje final `{tipo=2, id=0x3011,
corr, idx}` (enviado por `0x4379eba0`) y esta familia de autoconsultas son
dos formatos distintos hacia el mismo buzón — el bloqueo original (receptor
real del mensaje `0x3011`) permanece exactamente igual de abierto. Detalle:
`docs/capture/s20-p1-mailbox40193-rpc-pattern.md`.

## S20-P4 (CBID_ENCODE_STILL / StillConverter): código real localizado por primera vez

> Corrección posterior: S30 rechaza la atribución de `0x916140` como
> constructor StillConverter y `+0x4c` como Receiver. El constructor
> `0x920c8c` crea Sender `+0x4c`, Receiver `+0x50`, Handler `+0x54`.
> `0x91618c` corresponde a ObjStillRecorderThread. [S30](s30-pipelines-capture-encode.md).

**PARCIAL, con progreso real.** Continuación de `s19-fea-encodestill-completion.md`
(bloqueo: "no se halló el `AddCallbackFunc`... ni una arista registro→instancia").
Se usó `thumb_pc_strings.py` sobre todo `.text` de `libObj.so` para resolver
la xref de la cadena `" Receive CBID_ENCODE_STILL"`, localizando por primera
vez el **código real** (no solo la cadena) en `0x91ebe0`. **VERIFICADO**: es
un despachador interno que compara un ID local traducido (`0x4000007c`), no
necesariamente igual al `0xc0000004` crudo de FEA — límite explícito, sin
generalizar la igualdad. Ambas ramas del despachador construyen
`ObjMsg(0x3a48,...)` + `Struct` + `AddParam` y llaman al **mismo slot de
vtable `+0xc`** sobre un objeto en `ctx+0x4c` (patrón consistente con
`ObjPin::Send`, no verificado el layout exacto). Atribución a
`StillConverter` por densidad de cadenas `StillConverter.cpp`, no por
límites de función recuperados — el label `ObjStillRecorder_UnregisterCommand+offset`
que imprime `llvm-objdump` es, otra vez, un artefacto de proximidad (mismo
patrón que P3). Sigue NO_VERIFICADO el destino del pin en `ctx+0x4c` y la
igualdad numérica con `CBID_ENCODE_STILL`. Detalle:
`docs/capture/s20-p4-stillconverter-encodestill-dispatch.md`.

## S20-PRIORIDAD1 (receptor real de `0x40193`): arquitectura OSAL reconstruida, receptor exacto no localizable estáticamente

**COMPLETADO con resultado negativo bien evidenciado.** Ampliado el
alcance por primera vez a los módulos `.ko` del firmware (no solo
`av-cam.bin`). **VERIFICADO (nuevo, resuelve ambigüedad de larga data)**:
`liro.ko` ejecuta `av-cam.bin` como un **hilo real del kernel Linux**
(`kthread_create_on_node`+`tsk_entry`, que llama los punteros de entrada
del blob) — LIRO **no** es un procesador separado. **VERIFICADO**: el OSAL
real (`osal_snd_msg`, `osal_rcv_msg_tmo`, `osal_reg_msg_queue_cb`) vive en
`osal_uipc.ko`; los wrappers de `av-cam.bin` son *tail-calls* a un vtable
poblado por `liro.ko` al cargar. **VERIFICADO, decisivo**: desensamblado
directo de `osal_snd_msg`/`osal_reg_msg_queue_cb` confirma que el ID de
cola real es de **16 bits** (`uxth`); `0x40193` se descompone en
cola=`0x193` + campo extra `[16:30]`=`0x4` (`ubfx` confirmado). **Esto
explica por qué 4 sesiones de búsqueda literal de `0x40193` fracasaron**:
nunca fue un ID de cola válido como tal. Se buscó `0x193` en los 44
receptores reales, los 38 creadores reales y las dos tablas de despacho
conocidas (220 y 35 filas): 0 coincidencias en todos los casos. Se
descartó que `osal_subsystem_id`/`osal_thread_id`/`osal_dynamic_id`
expliquen la composición del ID. **Bloqueo real identificado por primera
vez con precisión**: el registro de colas↔callbacks (`osal_dir`) vive en
BSS de `osal_uipc.ko`, poblado en tiempo de ejecución — no reconstruible
desde la imagen estática sin traza dinámica (prohibida en este proyecto).
Detalle: `docs/capture/s20-mailbox40193-osal-architecture.md`.

## S20-P4-CORRECCIÓN: `ctx+0x4c` es `MWF::EventReceiver`, no `ObjPin`

**COMPLETADO (corrección).** Se localizó el constructor real de
`StillConverter` (`0x916140`, `libObj.so`): `ctx+0x44`=`ObjThread` propio
(arrancado en construcción), `ctx+0x48`=`EventSender`,
`ctx+0x4c`=`EventReceiver`, `ctx+0x50`=`EventHandlerWrapper`.
`EventSender::SetEventReceiver` conecta `ctx+0x48` con `ctx+0x4c` **del
mismo objeto** — un *loopback* local, no una conexión a un pin externo.
**Corrige** la inferencia de ayer (P4): el slot de vtable `+0xc` llamado
sobre `ctx+0x4c` es un método de `EventReceiver`, no `ObjPin::Send`.
Implicación: el mecanismo de "Receive CBID_ENCODE_STILL" es
auto-notificación hacia el propio `ObjThread` de `StillConverter`, no un
reenvío hacia DCF/MPR — este camino **no** lleva a P5. Detalle:
`docs/capture/s20-p4-correction-eventreceiver-not-pin.md`.

## Veredicto de arquitectura

Sin cambios: **A > E > P ≈ E2**. Ninguno de los hallazgos de esta sesión
reversa la jerarquía ni la cierra; narrowing adicional dentro de A (la rama
RawPlay/DevLater no demostró independencia del sensor) y una conexión nueva,
pero no decisiva, entre el clúster Stage_Notify y la unidad SDS ya conocida
de la ruta E (PbCap/SDF).
