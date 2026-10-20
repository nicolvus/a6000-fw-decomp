# Continuidad

Estado vigente: **S62** (20-10-2026), [PMCA: inyección, service shell y `modelName`](docs/capture/s62-pmca-injection.md), [checkpoint](knowledge/CURRENT.md). El mecanismo de PMCA y la propiedad BK4 `modelName` quedan verificados; el efecto «shell mode» de `ILCE-6001` no. S51 permanece. Las sesiones descritas a continuación son antecedentes.

Versión breve (18-10-2026). El historial íntegro de sesiones S1–S27 (y este mismo
archivo antes de reducirse) está preservado sin cambios en
[docs/history/CONTEXT-full-2026-10-18.md](docs/history/CONTEXT-full-2026-10-18.md),
con respaldo adicional verificado por SHA-256 en
`docs/history/CONTEXT.md.2026-10-18.bak` / `docs/history/CONTEXT.md.sha256.orig`.
Estado consolidado y restricciones: [docs/STATE.md](docs/STATE.md).
Correcciones y preguntas abiertas (generadas del grafo de conocimiento):
[docs/CORRECTIONS.md](docs/CORRECTIONS.md), [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md).

Este archivo conserva solo las sesiones más recientes (investigación activa).
No acumular aquí el historial completo de nuevo: cada sesión cerrada se traslada
a `docs/history/` y se referencia desde `docs/STATE.md`/`docs/CORRECTIONS.md`.

## S47 — entrada del payload y orden de C (19-10-2026)

VERIFICADO: registro `0x301d7` → callback `0x43789cc0`; fila `0x43ff29b8`
clave0xce → `0x43789708` copia0x140B a `0x43e95420` → `0x437d9f9c`
→ argumento4 `0x437da100` → payload `0x43ed4620` → `0x437dad78`.
La solicitud sintética `0x43ed44dc` es otra entrada. Dos llamadas nuevas
`0x437896ce/0x4378975a`, ausentes de xrefs por funciones no definidas.
Callback ANTES de copia: `0x43792f9c` domina `0x43794096`; memcpy
`0x43ae90ce`, desde `0x43e9d3b4` a `0x43e9b380`,0x1a4B incluye94/95.
PARCIAL: productor original antes de callback y valor2/B/G. Nuevo servicio
de registro+1ec, slot `0x435412a0=0`; no se reabre OSALbit31.
S48: proveedor/contrato de ese registro y stores paquete+1c/+1e para clave0xce.
Punto VD opcional aplazado; cierre físico/clases1–3 no demostrado; hito abierto.
[Informe S47](docs/capture/s47-payload-producer-and-order.md).

## S46 — base VD y escritor directo de C, antecedente (18-10-2026)

VERIFICADO: `0x436c6f3c`→`0x436c7950`→`0x43acee66` escribe
`0x43e16d2c=0xf3120000`; destino condicional de S45 `0xf3120220`.
Callback `0x437dad78`, clave `0xce`, tabla/fila `0x43ff8308/0x43ff8adc`,
escribe C=`0x43e9d3b4`+94/+95 desde payload4B en `0x43ed4620`:
primer u16!=0 → (1,low8(segundo u16)); cero → (0,0).
PARCIAL: valor2 por copias posteriores; productor/orden pendientes.
Sin alias P/C/snapshot demostrado ni cierre físico. Próximo S47:
argumento4 de `0x437da100`, productor de clave `0xce`, orden VD_Pre;
después semántica de `0xf3120220`.
[Informe S46](docs/capture/s46-vd-base-and-context-identity.md).

## S45 — contexto y consumidor de timing, antecedente (18-10-2026)

Contexto43eaadd8, preparado desde43e993a4 enVD_Pre;
C=43e9b380←copia1a4 desde43e9d3b4. P/C aún sin copia demostrada.
Virtual+74=43ad9202 leeIMX210+3a0;438c828c usa el retorno hasta
436c74c8→43ad2bd6(base+220). Base de controlador43e16d28 pendiente
en43e16d2c; no afirmar MMIO/integración/cortinas. SerieS40–S45 terminada,
hito abiertoS46+, sin agotamiento/Línea E. Próximo:escritores43e9d3b4+94/+95
y43e16d2c. [Informe S45](docs/capture/s45-context-identity-and-physical-closure.md).

## S44 — consumidor y comparación de modos (18-10-2026)

VERIFICADO:436d839c→436d79b0→436d75f8 consume119 paresID/valor de43fe995c;
backend+298 empaqueta y436d5ed0 escribe MMIO,436d5f60 pulsa control.
Virtual+a8=436d65b8 compara nibble alto del registroID0 entre índices,
sin usar flags. PARCIAL:4385cf2c produceP+95=2, pero aliasP/C no probado.
Próximo:contexto de437b5b14,+50 hastaP=raíz+2bc/snapshot43ef2474;
después lectoresIMX210+3a0 y vínculo integración/VD/cortinas.
Sin agotamiento estático/Línea E; OSALbit31 y AF no reabiertos.
[Informe S44](docs/capture/s44-register-consumer-mode-table.md).

## S43 — tabla PIC y revisión de códigos (18-10-2026)

VERIFICADO: base PIC4401eee4; destinos4401c6xx–4401caxx contienen IDs
u16 pequeños y datos byte+2: b3, estructuras software, sin vtables/MMIO directo.
43ad9a40/43ad99d4 solo guardan estado en objeto+fc; no aplican timing físico.
RECHAZO códigos de bloqueo AF: cadenas SetSequenceMode/ImgMode/framerate
y consulta virtual+94 a tabla de modos; ACEPTO helpers de log/trace.
PARCIAL transporte de registros y lectores IMX210+3a0; escritor C+94/+95
pendiente. Virtual+10 436d8ff4 copia0x70B de estado, sin transporte.
Próximo: consumidores de registros y virtual+a8 desde436d92e0, luego productor C.
Sin reabrir OSAL bit31 ni activar Línea E; sin .git, sin commit.
[Informe S43](docs/capture/s43-exposure-mmio-and-lock-codes.md).

## S42 — identidad de exposición (18-10-2026)

VERIFICADO:436d6320 es wrapper virtual; slot+28 de vtable43fcc090 contiene
436d6f6d. Constructor436d72e8/factoría436d6504 instalan/publican el objeto.
Clase2 usa bytes+08/+14 y guarda cálculo en objeto+3a0; sincronía NO_VERIFICADO.
Control G43ea6ad4 llega por copia c14B desde B43eae270: productor4382dd78
lee C=*(contexto+50), C+94/+95→B+36/+37. Origen valor2 pendiente.
R43e9b548+5cc=ImgState43e9baec+28; enlace a bloque0x44B sin demostrar.
Próximo: escritores C+94/+95, lectores objeto+3a0 y alias ImgState+28;
parser3023 pendiente. OSAL bit31 no reabierto; sin agotamiento global.
[Informe S42](docs/capture/s42-exposure-call-identity.md).

## S41 — productores y snapshots (18-10-2026)

Colas30001/3030f.4000/4036 nacen en43816448/43818c1c/43817e20,
envío4381a138; tablas43bc59e0={1,0,5},43bc5a50={1,2,0,3}.
Case1 productor43b01026; case10 largo43b00f62 desde copia conservada,
corto43b00f22 sin bloque560B. Envía8003030f: bit31 sin resolver.
PARCIAL: origen3023, entrega extremo a extremo y vínculo de valores a sensor.
[Informe S41](docs/capture/s41-message-origin-imx210.md).

## S40 — origen del contexto (18-10-2026)

Comandos API4000/4036/3023 escriben staging43edf684+24/+48/+458 desde
solicitud+0a/+09/+0e.43804c5c copia560B a raíz43e9b548; alternativa
43b00d06 copia objeto+8. Ceros condicionales438040e8/437935ae.
Tabla43fff30c:220filas×12B; selector43ca3c21={1,1,0,1}.
PARCIAL alias/productores alternativos; exposición/read-enable/generación
de cuadro NO_VERIFICADO.43804cc8 toma staging;43806a80/43806d50,
mensaje+4/+8. Próximo: productores originales de esos mensajes case1/10
de438069f0. [Informe S40](docs/capture/s40-context-origin-imx210.md).

## S30 — EncodeStill y corrección del supuesto origen YC (17-10-2026)

Informe `docs/capture/s30-pipelines-capture-encode.md`; auditor
`analysis/session22/evidence/s30_pipeline_audit.py` (12/12 PASS).
No declarar completados los tres pipelines funcionales solicitados.
436d6118 es getter GOT; 437f7ff0/43ad908e calculan drive/relación de tamaño.
Stage_Notify llama4372a3c4→40193/d008→tabla4400024c (fila12B)
→43aea99a→RelMgr4379d838 evento15→4381c6cc CapIdTblMgr GetCaptureID.
4379d6cc responde; +4b54=CaptureId, +4b58/5c=8B auxiliares, +4b94=estado.
4372a45c→d001→evento16→4381c568 IncrementRP. No es productor raster.
EncodeStill:90b248→90a810→90ad20→8fe6f8→71cf58→44f834.
429764 copia78B a FeaCore+11c;4000007c→42a1dc→4406d4→717ebc→718848.
2c5db4 configura,2c5cbc manda1500/2 payload48B→2c0c18→cola55001f.
InfraAvbbcIf ctor26e8fc, hilo26e438 (GOT102f4d8=26e439),
vtableff7238=26e5d1:1500/2→cola550123→InfraStillEncoder ctor46bed0.
Worker46bb60→49cde4→vtable1008230=46bcc5→464200 SeqResizeEnc.
465fac envía50B a56000f. BizFw tabla46340 cid3→2000;
tabla4752e cmd304→4. Receptor avcam43638308→435a9f4c Receive/Free
→43639c78→436399d8→43a8aa00→4363a1cc→4363ca28/4363a78c.
Retorno464154:4e0/2002→c70047 callback2c82f0→evento3001→2c3e3c
→worker2c3f5c→slotA4B14C (set2c2d78)→71c8a8→5fdc84(*AD38E8).
718848 espera mismoobjeto con5fe58a(-1), luego4000007c/12B
→900648/900974→Struct/3500/0→8febd0 WaitEvent(-1).
Resultado+dos paresdimensiones; Execute sigue912b4c Pool y después
liberaentradas1018/1032 víaDmmCloseAndFree(dc180), terminal3500/3002.
Corregido S20: StillConverter ctor920c8c Sender+4c/Receiver+50/Handler+54,
thread+8;91618c es ObjStillRecorderThread,916140 no es constructor.
Fronteras pendientes: adquisición sin cortinas; productor/fin DMA YC;
formato/planos/pitch y caché/reciclaje del buffer de captura.
Siguiente ruta concreta del motor:4363ca28→4363c730/c378 y
4363a78c→4363a668/4363cc7c/4363cd20 (selección de trabajo SDF).
Comando4→objeto43e51450+índice*10c; init4363d156/16e llama43653c2c
IDs4/24; GOT44021f98→vtable43fc4e10. 4363a668 envíae8B aexecutor560010.
Executor43638474→43a8ac06→4363a12c→API+8→43a9d2d0,
estado7→43a8fbaa→slot78 (43fc4e90)=43a9d320→4365b6ec
→43aa1930 wrapperconpila→43aa1746→43a94a10→43a949c8→43b4c46e
→43936f34. Native43937246 callbackPCrel43936b35; clear4 en43937286,
43933874 op31→43b5e832 ddl_saJpegCalcStart(request101,18B).
43933300 esperaSAFIN con43560de0 flagsC/8(tabla43bd2de8),timeout10000.
43936b34 actualizareporte+3c y439332b0(4,unit)→43560da8 signalflag.
Después chequeoreporte→tamaño enparam14c; API4363bb3c comunicacompletion.
Memoria43a96c70→43a975d8 consulta44B porhandle436519c0 yclose43651694.
43aa8558 copia8parescondcontador<=8; no llamarlos8planos sin evidencia.
Ruff src/tests mantiene9 avisos previos en4tests sin tocar; mypy src PASS.
No hay `.git`; sin commit. Sin cámara, instalaciones ni push.

## S29 — WriteStill de entrada a cierre (17-10-2026)

Informe `docs/capture/s29-writestill-end-to-end.md`. Orden10000003:
dispatcher9162d0/TBB91631a[0]=7→916328→916338→909a84.
UniqueId=10000011/12; CaptureId=1000 dentrogrupo10000003 (IDinterno1000).
Pool→StillInfo6b0B yWriteStillParam40B×1/2→90a172→8fe0a0→MPR/FEA→cmd9
→Recorder/RecStill→StillWriterFiltercmd5→DCF→escritor/registro.
NUEVO enlace completado:43f57e..58e registraStillRecorderIf slot0=34b138,
target1020,fn428bad (Thumb428bac),ctxFeaCore. 2d7db0 guarda +c/+4/+8.
RecStill34c848→2d7dd0 emite66/84B→428bac encolaFea+34→4299d8→42b9ac.
TBB42bbf2[66-64]=14→42bc1a→42bc26→441644 (441694 era interior).
Handler→40000012/48B→900648→90081c→EventSender90084c→8fe110/15e.
NUEVO cierrePool:90a318→910f28→91bb84→8fd738→8fc7b0(6108/100b)
→8fc484(6108/1007)→tabla101f838/844=1007/939dd9→939dd8→932a44 SetImageWrited.
Tabla1009→939da8, por tanto identificaciónS12 de1009 comoSetImageWrited eraerrónea.
Copiada40registros×1cB enctor93957c. PT_LOAD obligatorio para leer tablasVA.
Tras limpieza/helpers estados/database:respuesta3500/10000004, literal90a608;
1001=resultado,1002=CaptureId,100f reenviado de solicitud. NO3002 deExecute.
Evento adicionalcondicional10000007,literal90a60c. Retorno90a558.
No confundir respuesta deoperación conpersistenciafísica ni publicaciónplayback.
Auditor `analysis/session22/evidence/s29_writestill_audit.py`, 6pruebas.
Resultado6/6PASS;mypysrc+auditorPASS;ruffsinavisosnuevos,9previosen4testsajenos.
ExportsGhidra auxiliares con consultasinteriores/PIC no prueban límites; usarLLVM.
NuevoQueryLibraryExisting.java evitaContextChangeException alconsultar funcionesexistentes.
Sin instalaciones,cámara,ejecuciónfirmware,git ni push. SilentShutter sinvalidar.

## S28 — cierre OSAL, propietarios y contrato YC (17-10-2026)

Los cuatro puntos encargados quedan cerrados en
`docs/capture/s28-osal-pin-contract-closure.md`, empezando por el receptor.
`av-cam:4379744c` recibe OSAL50004, opcode1000; fuente InfraImaging.cpp.
Inicializador43797c34 crea cinco DataflowInfraPin desde ROM43ff36e4/f4/3704/3728/3738;
tabla43ff3714 víaGOT44025f2c. Alta del delegado receptor437970d4,
trabajo47; callbackGOT4402005c=4379744d. No confundir trabajo47 conOSAL50004.
VEF::SubsystemMain=5a0048, ctor436a4b1c (6YCout+6YCin).
ScalarInfra/SFRA=1670464, ctor439a6104 (4YCout+4YCin).
PostProcess desconectaVEFout0/2 yScalarout0/1, conectaVEFout0/2→Imagingin0/1.
Las cuatro palabras de PIN_PROPERTY son categoría/dirección/índice/OSAL.
Los cuatro ParamStd de YC0 son ENTRADAS que alimentan propiedad remota de
REQUEST_CONNECT(1000,1,28,2), no raster ni cuatro retornos gráficos.
CORRIGE S23: a14f88 envía20B y copia32B, dos paresLDM/STM en a150c8..d2.
CORRIGE S25: response+1c→out+1c, no response+20; +18=estado,+1c=resultado.
WriteStill909a84 consultaPool,UniqueId ymetadatos; preparaWriteStillParam40B y
StillInfo6b0B; llamada90a172→8fe0a0. PIN_PROPERTY no satisface ese contrato.
ExportS22 enARM conhalt_baddata inválido; nuevo s28-writestill-contract enThumb.
Auditor `analysis/session22/evidence/s28_dataflow_contract_audit.py` reproduce
tablas,SHA y ensamblador. No firmware ejecutado ni paquetes instalados.
Sin repositorio.git disponible; no commit/push. SilentShutter sinvalidar.
Las secciones S23–S27 históricas sobre receptor/alta desconocidos quedan superadas.

## Próximo paso de investigación vigente

S48: productor de los dos u16 anteriores a entrada `0x43789cc0`,
registro ID `0x301d7`, clave `0xce`; contrato/proveedor importado `+0x1ec`
en slot `0x435412a0`. Entrada recibida `0x43e95420`, distinta de solicitud
sintética `0x43ed44dc`. Orden callback→copia y cobertura94/95 resueltos S47.
Los párrafos siguientes conservan próximos pasos históricos.

S47: productor del payload4B `0x43ed4620`, argumento4 de `0x437da100`,
clave `0xce`; demostrar los dos u16 y orden frente a VD_Pre/copia C.
Base VD resuelta en S46; semántica eléctrica de `0xf3120220` pendiente.
Los párrafos siguientes conservan próximos pasos históricos.

S41: slots OSAL+1d4/+1e0 cero; bit31 no resuelto en el blob.
Línea C activada: seguir productores de argumento1+36/+37 de43842158
(valor2) y argumentos+8/+14 de clase2 IMX210; cierre físico pendiente.
A/B abiertas: metadatos3023 y R+5cc hasta argumentos tipados del sensor.
Ver [S41](docs/capture/s41-message-origin-imx210.md).
Los párrafos siguientes conservan próximos pasos históricos.

S39 sigue los tres consumidores del conversor hasta detección de cambio
y reinicialización APL; no encuentra bits de formato ni stride asociados.
Origen context[2]+28 identificado en43e9bb14, con cuatro escrituras VD_Pre;
inicialización context[2]=root+5a4 demostrada. P e input usan índices distintos.
Próximo vigente: escritores/copias de context[0]+24/+48/+458 hasta tabla o
solicitud tipada; nombres de píxel y dependencia de FPS siguen sin demostrar.
Prioridad física acumulada: productor/handle/VD y cierre de integración.
Ver [S39](docs/capture/s39-image-format-apl.md). S38 debajo es antecedente.

S38 limita la vía DMM de S37: 61003c es pool compartido, servidor y escritor
de respuesta no recuperados; av-cam es blob LIRO, no ELF. Slot +2e4=0,
resolución externa fuera de este blob. Frontera agotada solo para resolución
ELF/valor del slot, no ausencia universal de receptor. Próximo vigente:
enum de formato S33 desde input+38/P+1b4/context[2]+28 y 43814d24 hasta
campos APL, stride y tamaño. Captura física NO_VERIFICADO.
Ver [S38](docs/capture/s38-dmm-osal-static-frontier.md).
Los próximos pasos S37/S36 siguientes se conservan como antecedentes.

S37 localiza el definidor DmmAccess en `libmprctrl.so` y los getters originales
en DmmAccessPLA. Dirección/tamaño son palabras de respuesta remota; no hay
dominio físico/lógico probado. AllocDmmMemory devuelve un paquete distinto.
Cliente OSAL 0x61003c, payload 0x18, parcialmente compatible con S33 pero sin
identidad del slot av-cam. PLT S30 0xdc180 sí importa el símbolo definido aquí.
Siguiente: receptor 0x61003c y proveedor tabla+0x2e4, escritor de extents y
misma clave/handle hasta Rendezvous/APL. Productor físico YC NO_VERIFICADO.
Ver [S37](docs/capture/s37-libmprctrl-dmm-extents.md). S36 debajo es antecedente.

S36 separa memoria SysV de DMM en `libInfraScalarMpr.so`: `void**` viene de
`shmat`, con uso como destino de copia still; las APIs DMM son importaciones
UND. Localizar definidor de `_ZN9DmmAccess14AllocDmmMemoryEiPt` y
`_ZN9DmmAccess13FreeDmmMemoryEi`, sin atribuirle aún el slot av-cam ni
Rendezvous. [S36](docs/capture/s36-libinfra-scalar-mpr-memory.md).
Productor físico YC NO_VERIFICADO; lo siguiente conserva antecedentes.

S35 resuelve los cuatro objetos DFE y sus métodos virtuales: Ofmt/Ifmt y
subobjetos SGC con registros `0xfc0a…`, sin lectura/ack APL recuperado.
FRONTERA ESTATICA AGOTADA para esta vía; no se demuestra fin físico ni
imposibilidad universal. Siguiente investigación: proveedor DMM `0x43561524`,
entrada `tabla+0x2e4`, productor Rendezvous y consumo del handle YC.
Ver [S35](docs/capture/s35-dfe-objects-static-frontier.md). Las fronteras
S34/S33 siguientes se conservan como antecedentes.

S34 continúa la frontera física: helper APL con tres BL, programación/kick
síncronos en Image; ruta VD_Sequence y selección condicional de categoría HS.
Evento Drive `0x80` inmediato o por timer 4, sin fin DMA demostrado.
Registrador DFE de cuatro callbacks y conversión de causas recuperados;
resolver objetos de slots `0x44023400/0x44024d10/0x44021914/0x4402603c`
hasta registros/IRQ y contrastar con bancos APL antes de unir a EC/LM.
Cuadro físico propio/siguiente y fin electrónico siguen NO_VERIFICADO.
Ver [S34](docs/capture/s34-apl-dma-vd-interrupts.md). La frontera DMM S33
siguiente sigue abierta y se conserva.

S33 continuó esta frontera: los 26 llamadores construyen 13 inputs locales de
0x104 bytes; `+0x10` referencia handles de trabajo y `0x43814ea0` puede
escribir `+0xd4=P+0xbc`, varios obtenidos por AllocRendezvous.
Falta resolver el proveedor importado DMM
de `0x43561524` y quien satisface las claves de `P+0x18c/+0x194`, para enlazar
extents/raster y fin DMA. Ver [S33](docs/capture/s33-yc-rendezvous-producer.md).
El párrafo S32 siguiente conserva su frontera histórica.

S32 resolvió los registradores de las listas VD (`0x4379704c`/`0x43797090`),
el adaptador `0x43b03a48` y seis destinos concretos. `0x4379b44c` prepara
un bloque YC con referencia `MemoryHandle::AllocShare`, geometría y configuración.
El overflow en `0x4379cb2e` mide tiempo, no fin DMA. Falta resolver el handle
de entrada `+0x10/+0xd4` a píxeles/pitch/formato y al consumidor final;
ver [S32](docs/capture/s32-vd-callbacks-sync-ycout.md).

El alta/callback de `0x50004` ya quedó cerrado en S28 (receptor InfraImaging,
`4379744c`); no reabrir esa parte. Pendiente real: localizar el **productor
sensor/DMA** del YC de captura — ver "Fronteras pendientes" en S30 arriba y la
tabla de flujos incompletos en [docs/STATE.md](docs/STATE.md).
