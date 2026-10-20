# Continuidad

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

## Trabajo activo posterior: sin informes intermedios (16-10-2026)

FRONTERA MÁS RECIENTE: `analysis/ghidra/darwin-mechanical-enable-checkpoint.json`.
Nueva comparación A6000: callbacks de la secuencia principal17 registros decompilados
(`a6000-darwin-primary-sequence-seeded.json` y
`a6000-darwin-sequence-remaining-callbacks.json`). Clave3 207be y clave4
207e8 llaman20cd4, que baja MMIO+238 a0 si20c74 devuelve tipo1..3.
La secuencia alternativa7 registros, clave4 20aa4, llama20d00, que sube
MMIO+238 a1 con la misma puerta. 51c0 es escritor MMIObase+offset; la
asignación de+238 a una cortina sigue SIN verificar. 2089c discrimina
estado+153 tipos0..3 medianteTBB208e0; LLVM confirma sus cuatro destinos,
que Ghidra no recupera. Tipos1/3 llaman21014 con modos0/1; tipo2 llama20fde.
REA abrió Darwin A6000 con hash5f2be... y confirmó20d00; 207e8 no estaba
registrada en su análisis automático, por lo que se usó el proyecto Ghidra
persistente y LLVM para esa entrada. REA xrefs de20d00 resultan parciales:
reportó203c2/20448 pero LLVM también muestra llamada20ac0; no tratar el
inventario automático como completo. No hay parche ni foto física validada.
REA también abrió Darwin A6300 con hash6249d4... y confirmó24730(enable):
24720() yenable deben ser distintos de0. Su análisis automático NO registró
248be (devolvió una función ajena,28a44), mientras Ghidra persistente y LLVM
sí la localizan. No usar ese resultado de REA como decompilación de248be.
A6000 2089c→21014(0/1,timing)→9854 configura flags/compare de un
registro de temporizador y espera mediante941e; 21014 además invoca funciones
de interrupción y, condicionalmente,1b498. Esta última configura ADC DMA
(cadena literal `[ERR]ADC DMA`). El camino mezcla temporización, interrupción
y sensor de posición, pero no asigna eléctricamente una cortina ni prueba
lectura final totalmente electrónica. Export`a6000-darwin-phase-hardware-events.json`.
A6000 descriptor secundario29dc8 (7 callbacks) se activa por2041e(param≠0);
param=0 activa descriptor0 y llama20d00(+238=1). Envoltorios19932
(fuerza0) y19948(pasaR0) dependen de19b9e. Control de exposición18d6e
invoca ambos según ramas de tiempo/compensación; LLVM18ec8 confirma R0
calculado hacia19948. 18fa0 también llama19932. En estas rutas examinadas
no hay prueba de puertaSilent: propagación de bit por sí sola no basta para
suprimir secuencia secundaria. Exports`a6000-darwin-secondary-*.json`.
Gate19b9e: requiere state+170bit0 limpio y165c8(0x10) distinto de0;
165c8 comprueba state+444 bit0x10 limpio. No consulta Silent.
Exports`a6000-darwin-secondary-dispatch-gate.json` y
`a6000-darwin-secondary-interlock.json`.
ROM confirma DAT1661c=DAT19bbc=DAT205a0=200036d8, por tanto ambas
condiciones miran la misma estructura S. DAT55a0=42668000;
51c0(0x238,v) escribe42668238, puertoP4E, net física aún desconocida.
A6300 parser1943e importa31bytes desde17f5c→219fa(6), buffer20003940.
Byte12 bit20→S200034e4+d0 bit20 (escritura1956a con baseS+30 yoffseta0).
Selector1b146 devuelve inversa de ese bit; llega a1a6a6→1b598→23556 y
patrones248ee/24a4e/24b1e, además21052/1b60e. STRB+d0de18d30solo limpia.
Ingreso184ce→21aac(6)→127ac(0c), copia31desde2000324c.
Tabla2d6f4 entrada0c: TX0,RX2000324c,len31,header f0 03 01 02 1f 00 00 00;
Darwin12660/1261c administra encabezado/cuerpo porSIO3.
LIRO436fba6c recibe8bytes en44105540 (full-duplex,TX44105548);436faae0
si header[3]==2 pasa a estado2/subestado2 de envío. Handlersfb860/fab68
entregan cuerpo del anillo mediantefa9f8. Esto explica diferenciabyte3=0/2:
hay petición remota de lectura y ruta de entrega explícitas. Fuerte evidencia
de protocolo emparejado, NO conexión física medida ni foto electrónica probada.
A6000 parser17f8c importa22bytes; copia byte12 bit0 ybit3 pero NO bit20 aS+d0.
Esta omisión ya verificada; no concluir incapacidad del IMX210.
Siguiente: contrastar salida equivalenteA6000, demás consumidores del bit,
condiciones de variantes y modo/exposición; completar enlace sin asumir cortinas.
Helpers:24dd4 guarda contador;23394 puede escribirGPIO+30=0;22f4e agenda
otra secuencia. Por ello selector desactivado NO prueba ausencia total de movimiento.
Exports nuevos `a6300-darwin-capture-*`, `a6300-caif-peer-request-handshake.json`,
`a6000-darwin-capture-request-parser.json`. No informe nuevo ni cambios de fuentes.
Consultas no canónicas21aaa/21954 resolvieron funciones contenedoras existentes;
usar21aac/218b4 respectivamente. Continúan válidos los hashes originales.
Los párrafos históricos siguientes sobre receptor desconocido quedan superados
por estos checkpoints; conservarlos para trazabilidad.

Emulación NUEVA `EmulateDarwinCaptureBits.java`: 512/512 por modelo, sin
warnings/errores tras inicializarCY. A6300slice194c8→1956e,A600017fc0→18056;
256valoresbyte12×2estadospreviosd0(84/a4), RAM/pila sintéticas, sin llamadas.
Verifica bits0/5 ybit3enS+42, bytes13..15. JSONs `*-capture-bit-emulation.json`.
Darwin hashes originales comprobados de nuevo y checkpointJSON válido.
A6000 salida20544(time,mode)→20d26/20e0e/20e98 carece deenableadicional;
A630023556(time,mode,enable) usa24730(enable). No es un solo interruptor UI.

Puente EFCS→paquete: bajo bank4bc/50c bit20limpio, clase1→packet1lowbits0;
clase3→lowbits2 en ambos; clase0 también→2 SOLO en A6300. EnA6000clase0→0.
Flags40 y sumas14/OR80 preservanlowbits. Parserscopianpacket1→S31.
LLVM43841342..398 y4391aa66..aabe lo confirman, juntoexports existentes.
No equiparar bit de sensor, clase de exposición y política mecánica.

Secuencia22f4e: descriptor2f93c,callbacks24564/578/59c/5ce/602/636
→24caa→GPIO+2c. Arranca0/1 según CAMPO20003b04 (2 o3/4), NO asumir
igualtipoHW24700. Setter23652 recibe1..4, otrovalor→0. Thunk1b8f6;
dispatcher21b94 operaciones62/63/64/65 fijan1/2/3/4. Wrapper21ea4 acepta
40..9f y adaptador1df10 llama21ea4 trasuxtb; sus apariciones estáticas son
en tabla indirecta, por tanto origen/rol externo siguen pendientes. No llamar
esa ruta captura normal ni diagnóstico sinprueba.
Ghidra21b94 conservaTBBincompleto; destinos62/63reconstruidosbytes21bb2.
24700 tipofísicocandidato lee1cf34(0): si200002c0[0]válido devuelve
20000050[0]&7, admite1..4; inicialización/origen de estosbytes pendiente.
Export `a6300-darwin-control-operation-dispatch.json` contieneadvertencia
de propagación y no reemplaza contrasteLLVM. 21d48noregistradoantesdecrear21b94.

NUEVA validaciónsecuencia secundaria: 1aabe pasa selector1b146 como param2a1b60e.
Enrama tipo4,enable=1 registra timing y agenda descriptor mediante20a3c→24666(3);
enable=0 solo actualizaflags y omiteese dispatch. Rol físico del descriptor sigue
sin identificar. Export`a6300-darwin-silent-secondary-consumers.json`.
Detalle: descriptor2f920 iniciaenpaso6(*2f898), tabla2fb48(10 callbacks):
6→2464a,7→244f8,8→24524→2317a→230f0,9→2454e. Este ramal queda omitido
conselector0. Aun así, captura conselector0 llama1b54a(0) desde1a7ac y
agenda descriptor0; 1b494 desde1a812 llama22f4e. Por tanto no afirmar que
Silent anula toda secuencia o toda actuación. Evidencia nuevos JSON
`a6300-darwin-type4-sequence-callbacks.json`, `*-helpers.json`,
`a6300-darwin-sequence-2317a.json`; contraste LLVM 1a79a..1a812.
REA sobre av-cam.bin A6300 (13 MB, tres funciones) agotó el tiempo de 300 s;
no inferir resultado de ese intento. Continuar con proyecto Ghidra persistente.
Secuencia principal con selectorSilent0: 1b54a(0) sí agenda descriptor0 2f8cc
desde clave3 (*2f8a1), tabla2f958; claves3..7→23af4/23bb0/23bf6/23c52/23c82.
20c2a busca por clave y20b20 la avanza. 23af4 pasa22ebe(bit80=0) a24730 y
omite rama28244. 23bb0 aún llama248be(1), que en tipo4 baja GPIO+238 y+38;
23bf6 omite248be(0) pero invoca28304/236a4; 23c52 ejecuta puerta24730(1).
23c82 inicia con22ebe→24730 y su rama principal queda cerrada conbit80=0.
Es una traza parcial: escritura GPIO a0 ni llamadas a temporizadores identifican por
sí solas cortina o desplazamiento. Exports`a6300-darwin-primary-sequence*.json`.
Comparación de descriptores ROM (base4200, binarioshashes del checkpoint):
A6000 29d90/29dac tienen17 registroscallback cada uno, A6300 2f8cc/2f8e8
tienen30. A600029dc8 tiene7, A63002f920 tiene10; ambos poseen otro de6
(29de4/2f93c). A6300 añade en este grupo2f904 de30. Sus punterosRAM y
colas de estructura hacen plausible correspondencia, pero no equivalencia de
cortinas. Las tablas incluyen claves repetidas: buscar por clave, no índice.

NUEVA FRONTERA SIO: leer analysis/ghidra/a6300-caif-sio-endpoint-checkpoint.json.
Canal3 ya VERIFICADO: init436fd478→GOT441ff578=3 (90-8d).
MMIOf2405600/FIFOf2405700. Backupdefaultschipselectf900b1/f9006d=5/14,
ambosmodelos; seleyóBK4conparserLOCAL /home/nicolas/.local/share/Sony-PMCA-RE,
abiertorb, checksumválido. Detalles/hashesJSONcheckpoint. PMCAvenvsolo
dependencias, importpmca/fworkflowrequiereañadircheckoutlocalsys.path.
Noinstalado ni ejecutadoconcámara. MainDest seleccionaCX79100_UC2(A6300),
CX77500_UC2(A6000). Defaultsf90455/56 difieren10/3vs7/16; otros7paresiguales.
Noasumirdefaults=estadorealcámara. HostCAIFCS5/14noidentificachipremoto.

Receptor LOCAL de740017 identificado: init43a24cf4 registra por43559b7c
(740017,440d06c0,43a24ad1,0), receptor43a24ad0. REAosal_uipc.ko confirma
ABI4argsosal_reg_sync_msg_queue_cb y llamada synca callbackregistrado.
RutaCAIF+10==0copiamensaje64→440d06c4+channel40, descriptores440d0804,
43a24a9c→43a246d8→43a2439c→43a2550c configura MMIO f2405000+ch200;
43a24878→43a245c4→43a252b0 copiaFIFO f2405100+ch200;
43a24568→43a2513c→43a25200 configura yARRANCA bit20000000.
Canal0..4: global44147d20 víaGOT441ff578. Falta productorvaloractual y
receptorREMOTO; NO asumirDarwin. Las colas async74001a..1e son otra ruta.
Header normalizado103f0, bytespreviosFIFO f0 03 01 00 1f 00 00 00,
noafirmarordenfísico porSPIaún. Helperfa454logging,fac60/ fd420diagnóstico.
Export fa4b8 es interiorcandidatoerróneo, no usarABI/entrada.
REAactualosal_uipc.ko; 5funcionescorrectas exportsosal-queue-routing ysync-registration.
componentes0630_ca/0631_ca_sum vacíosambos. A6300bonobo.bin172144 SHAfee387d9...
sinstrings, formatoNOidentificado; A6000nflasha3 no contiene bonobo.
No se importókernel ni bonobo; noinstalaciones nihardware.

Última instrucción: continuar hasta resultado, no preparar más informes mientras
se investiga. Conservar evidencia y checkpoints; no tocar cámara ni instalar.
Nuevo `analysis/ghidra/darwin-dma-gpio-checkpoint.json` contiene cadenas completas.
IRQ44/excepción60: vector primario A60006809/A63006b93 entra trampolín6808/6b92;
leeICSR e000ed04 y usa tabla SOFTWARE4300+(VECTACTIVE-1)*4. NO es otra VTOR.
Entrada43ec: A6000ff8f→fea8(6)→1b44c→20220(1)→20c06→1e33e(29dac)→2089c;
A63005f9f→5f36(6)→1d3a8→22e3e(1)→24666→20c2a(2f8e8)→23e16.
Dispatch condicional variante y secuencia/ID. Canal6 extrae/limpiaestadoDMA
pero no discrimina éxito/error antes de notificar fases. No prueba movimiento.

Mapa bit-band coincide con header original Fujitsu FM3 de FreeRTOS:
42668230=P4C,234=P4D,238=P4E,4266811c=P27,42668038=P0E (PDOR).
Modelo exacto MCU y conexiones cortinas NO verificados. Referencias oficiales
en JSONcheckpoint; main manual Infineon002-05586revC confirmaDMAC40060000,
canal6regs70/74/78/7c e IRQ44 segúnheader. No extrapolar todo mapaFM3:
DMAfuente24d1a→1d48a→90fc devuelve40023004, bloque aún por identificar.

Inhibición+444 aclarada: escritor1781c(category,...) añade1<<(category-2).
Categoría6 da bit10, guarda primererror+440..443 yregistra. Error de cierre
23c82→1781c(6,1,20,phase) puede bloquear1b988 vía1788c(10).
No es selecciónSilent demostrada. Gate+170 es otra condición.

CAIF nuevo: 436fa784 fuerza byte4 del mensaje a f0 tras guardar opcode10300,
de modo que el campo lógico transmitido parte de103f0. Headerhandler436fb974
copia8bytes del anillo. 436fa454 es logging, no transforma cabecera.
Pendiente comprobar si436fd420/436fac60 o handlers mutan campos antes del
anillo/copia, antes de fijar bytes definitivos del cable. Query436fa4b8fue
candidato interior (unaff regs), conservar como inválido para límites/ABI.

Exports nuevos: a6300-darwin-adc-interrupt-root, error-inhibit-origin,
vector-installation, dma-timestamp-source, shutter-output-patterns;
a6000-darwin-adc-phase-notification,dma-vector-dispatch; a6300-caif-wire-header.
Actuales acciones: seguir patrones248ee/24a4e/24b1e hacia callers y equivalentes
A6000; distinguir GPIOacción de monitoreo. ReceptorCAIF sigue pendiente.

## Checkpoint vigente: fases Darwin y frontera serie (16-10-2026)

Leer primero `docs/capture/darwin-state-machine.md` y las dos secciones nuevas
de `silent-caif-transport.md`. Encargo vigente: análisis estático/local, sin
acciones sobre cámaras; informe técnico al cerrar la sesión. No instalaciones.
No es necesario resolver toda la viabilidad en una sesión.

TBB recuperados directamente con SHA estricto y contrastados con LLVM:
A6000 tabla208e4 bytes44022349 → 2096c/208e8/2092a/20976;
A6300 tabla23e5c bytes4c022351 → 23ef4/23e60/23ea2/23efe.
Fases1/2/3 guardan mediciones+156/+158/+15a, rearman umbral bajo/alto,
y llegan a fase4. MonitorADC separado solo marca bits, no cambia fase.
IMPORTANTE: bit80 de callback+10 RETIENE etapa en scheduler20b20;
NO es finalización física. Bit40 pide otra iteración. Preservados exports
anteriores con decompilación TBB incompleta; no usarla para estos destinos.

Ruta A6300 verificada desde helper de notificación1d3a8: pone
[20002abc+4]=1; si2486e()!=0 →22e3e(1)→24666(1)→20c2a(descriptor2f8e8).
Literal246f4=2f904, resta38 y suma1c. Tabla2fa28, IDs3/5/7→23e16.
Todavía falta instalación/IRQ que invoca1d3a8 y equivalente A6000.
Descriptores primario/secundario: A63002f8cc/2f8e8, A600029d90/29dac.

Inhibición A63001b988: S200034e4+170 bit0 limpio y S+444 bit10 limpio.
1b318 limpia+170; ce40→1d1b4 llamado porOn main7c74.
1b906 pone bit0 y reinicia secuencias/salidas; ce7c desde d48a.
INFERENCIA ciclo de subsistema, NO demostrado Silent. Seguir d48a y+444.
Escritores reales: A600051c0 /A63005248 guardan palabra en42668000+offset.
Comparados +234 y+238; A6300tipo4 usa además+11c. NO asignar cortinas,
GPIO/bobina ni enumSilent a esas direcciones sin más evidencia.

CAIF: nueve bytes+16..+1e A6300 ya caracterizados por productor4391a6f4;
fuente*442017f8, tres condiciones seleccionanushort; +18/+19=0;
+1a indicador80 yORglobal4415af72, +1b..1e copia globales73..76 bajo
objeto*44201b74+178==1. En rama contraria no se asignan esos4bytes aquí.
Semántica física/receptor/compatibilidad22vs31bytes siguen pendientes.
REA abrió nfc.ko SHA5c7942c9839e9bb24f05eb7480da80c08b391a82baa7ed3f2ff6dd0516142684,
4funciones correctas. Otro PRODUCTOR de cola740017 con ABI/descriptoresSIO,
no receptorCAIF demostrado. Exports a6300-nfc-sio[-message]-rea.json.
REA activo nfc.ko; no reanalizar bibliotecas globales.

Nuevo extractor `src/darwin.py`, tests `tests/test_darwin.py` (6 casos),
exports *-darwin-phase-table-verified.json y contraste independiente
darwin-phase-caif-independent-disassembly.txt. ScriptsQueryDarwin siguen
sin reanálisis global. Query20dae resuelve contenedor1afce; usar LLVMlocal.
Consultas SIO a cinco posiciones sin funciones existentes conservadas como
cobertura negativa limitada; no crear funciones desde datos.
Hipótesis A/B/C continúan NO VERIFICADAS; no parche funcional propuesto.

La revisión automática que había agotado cuota permitió de nuevo las
consultas dirigidas en esta sesión. No queda un bloqueo de aprobación vigente.
Validación final: 32 tests correctos, Ruff y Mypy sin avisos nuevos;
SHA ambasROM/LIROA6300 intactos, vistasELF idénticas/base4200, enlacesOK.
Sin commit: git rev-parse confirma que no hay repositorio Git; no inicializado.

## Darwin verificado tras interrupción (16-10-2026)

Imports ROM4200 amboscompletos,sinERROR. SeedDarwinAdc separócorrectamente
wrappercola8:A60002109c→1b400 yA630024da2→1d35c. Hashestrictoambos,
guardainstruccionespushb510/retbd10/wrapper2008 ysinUSER_DEFINED.
EliminóSOLOmetadatosdelwrapperinferido,recreólectoracotadoywrapper6bytes;
noalteróbytes. Noejecutarotravez:guardaunusorechazarálectorregistrado.
Exportsvigentes a6000-darwin-rom-adc-separated.json y a6300...igual,
rom_base4200; entradasexactasdecompiladas. Lectorescapability5ec4(2)/62f8(2),
ADCgenérico97ba/96e4, alternativacanal8leeRAMushort>>2.
RefsA6000wrapper2067a/206a6/206c8;A630023770/2379c/237be.
Nativequeriesenprogreso sesiones65300(A6300) y53949(A6000),
outputs*-darwin-shutter-position-consumers.json; incluyenworkersMain
A630078aa/7b50/7d82/8786/893e. TablaMain2b534=file27334,5filascompletas,
fila5tiene2callbacksyluegoNULL; nodarporterminadaenumeraciónsinusos.
ScriptsválidosSeedDarwinVectors/QueryDarwinrequierenROM4200; antiguosexports
basadosenceroNOvalidanpunterosabsolutos. NohaycámaraSonyUSBvisible.

## CORRECCIÓN CRÍTICA DARWIN: BASE ROM 4200 (16-10-2026)

La hipótesisbase0esINCORRECTA. NOusarviejosproyectosa6000/a6300-darwin
para punterosabsolutos/indirectos. Seconservancomoanálisisfallido.
PruebaA6300:vectorreset45f9correspondearchivo3f8(inicializaciónBL,bx),
vectorNMI4601correspondefile400(handlerobtieneMSP/PSP), yrestovectores
contiguoscoinciden; tablaabsoluta2b534→file27334 tienecallbacks768d,
7839,78ab,78c5. Base0tablamostrabaIDs10/11quenoeranfunciones.
NuevaROMbase4200, proyectos a6300-darwin-rom / a6000-darwin-rom.
Importsesiones57204/71684pendientesconsultarlog. AmbosusanSeedDarwinVectors
corregido (hashestricto,requierebloqueinicie4200, vectoresleídos4200+offset).
QueryDarwin.java tambiénexigebase4200yexportarom_base4200, soportacandidate:
entradaverificadaexplícita; previosJSONsinrom_base4200sonoffsetsbase0,
NOevidenciadepunterosabsolutos. Todoslosbytesoriginalesintactos.
ADCdireccionesROMcorrectasA60001b400,A63001d35c;strings1b5c0/1d518;
enfirmwarearchivoseguirrestando4200. SeedDarwinAdc actualizadoabase4200
peronoejecutarnuevoproyectosidescubrelectorautomáticamente.
MainA6300file710→ROM4910; exportviejo a6300-darwin-main-seeded.json
noesvigenteparatablaindirecta. Consultaahora4910,1d35c,12154,1261c.
Docs/capture/darwin-shutter-entrypoints.mdcorregido. CAIF/IMXyKikiLog
resultadosanterioresNOdependendeDarwinbaseincorrecta.

## Frontera nueva: CAIF y Darwin (16-10-2026)

IMPORTANTE nueva diferencia protocolo: A6000evento1 437db858→436b8a50
copiayencola22bytes(16hex) a43f91e32, opcode10300. A6300son31(1f).
BitSilent+12cabeen22, peronuevebytesfinalesA6300noenviadosporA6000.
NoafirmarqueMCUrechaceotraslongitudesocamposfinalesnecesariosSilent.
Exports a6000-caif-event-dispatch.json y a6000-caif-parameter-payload.json
correctosentradasexactas; docs/capture/silent-caif-transport.md actualizado.
A6300Darwinmainstring814 ADR758; QueryDarwin main en sesión62290,
exporta6300-darwin-main.jsonpendienteleerparaestablecerreceptorhost.

Actualización: importA6000Darwin completóSeedVectors+autoanálisis+save.
LectorADC A6000yaexistente17200 (ADR17222→string173c0), export
a6000-darwin-shutter-adc-inventory.json. ADCcomparaciónendocs/capture/
darwin-shutter-entrypoints.md. A6300callbacksserial df54/e41c decompilados;
sonmsssync/async, conexiónCAIFpendiente. a920 helperregistraeventos,
noatribuirleparserCAIF. Refsimparesdf55/e41d/1915dvacías, nocoberturacompleta.
Otroavance: A6000constructor43841070param5+12 asigna0/1 (también1diag),
NOañadebit20Silent; caller437f87ac lepasapaquete*(capture4ad8)+40.
Reutilizados efcs-algorithm-arguments.json yefcs-capture-sequence-switch.json.
Seccióncomparativaen silent-caif-transport.md. NuevoqueryA6000eventoCAIF
437db858 PICantespush85e: sesión25789exporta6000-caif-event-dispatch.json
pendienteleer, seguiráhandlerparamset para comparar31bytes.

Leer docs/capture/silent-caif-transport.md. Señal adicional Silent en
4391a6f4 quintoarg: paquete+12 bit20 para captura804==2, salvo diag
*441fe1e0!=0; otroflag añade1. Quintoarg=*(captura4ed0)+40 por438bfcd8.
437e0508 evento1→436f9714 copia31bytes a44147b18;436fa784 encola
tipo2,código10300,long1f,puntero44147b18 a1502c7. 436fa350(122,..)
esruta aparte, NO sustituir cuerpo encolado. Receiver436fa630→436fc6c8,
tabla5estados441ad85c, mensaje2. Estado2/sub1→436fb974; otrosestados
usan43b7e2c0→436fb7d8 (anillo10registros43ff1fb0). fb974 envíacabecera
8bytes porcola740017. Estado2/sub2 handlersfb860/fab68esperanflags3;
fb860→fa9f8 descriptororigen44147b18,long31,base43ff1cb0. fad78avanzaanillo
yfa934callbacks. Transporte NOdemostradoSPI ni receptorDarwin todavía.
Exports a6300-caif-*.json nuevos; fuenteshashverificadas.

Darwinhalladoen0640_darwin/darwin_core.bin deambosfirmwares. NOasumir
quelarecepciónCAIFesDarwin. A6300181040bytesSHA6249d4b7f70d31c50048c85ca39e61c1872b547a26fd4b4ad0343ca9811433ac;
A6000157276bytesSHA5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4.
VectoresCortex-Mbase0,SRAM2000...,ThumbResetA630045f8/A600045c8.
Proyectoa6300-darwin.gpr (programdarwin_core.bin),1508funcsautoanálisis
completo60s, coberturaaúnparcial. SeedDarwinVectors.java admite2hashes,
lenguajeARM:LE:32:Cortex, ROMreadonly. PrimerimportfallópreScriptpor
escribirTModeencódigoexistente; eliminadooverrideyaCortexfijaThumb.
ReejecuciónSeedVectorscorrecta,vectores1..63,noalterabytes.
QueryDarwin.java consultasSOLOfuncionesexistentes,hashestrictoambos.
ShutPIADC A6300string19318 ADR16en1917e (noLDRliteral), función1915c..1918f
nohabíasidodescubierta. SeedDarwinAdc.java defineexactamenteesoslímites
verificadosLLVM (sineliminarfuncsexistentes). Exportválido
a6300-darwin-shutter-adc-verified.json:capability20f8(2); sinoADCcanal8
leeushort*20002abc>>2; otroscanalesretorna0ylogShutPIAdValue; alternativagenérico
por56e8. NOesfuncióndemotor. Intentoa6300-...-corrected.jsonsinfunción:
sehabíasupuestoerróneamentesolapamiento19066; guarda rechazósinmodificar,
scriptRepairDarwinAdc eliminadoyremplazadoporSeedDarwinAdc.
19066 incluyeleafNVIC192deperoNO1915c; noquitar19066.
Nueva vistaELFa6300-darwin-analysis-view.elf .textigualoriginal,base0.
QueryDarwin serialrefsADR e1d8→df66, e5ec→e42c, adjust24664→2463a,
exporta6300-darwin-serial-handlers.jsonsesión65590pendienteleer.
ImportA6000Darwinprojecta6000-darwin sesión38512pendienteverificar.
Frontera:identificarreceptorCAIF, analizarserial/mss deDarwin sinpresuponer
relación, comparara6000. PreguntarecursosUSB/IMX210sinrespuesta.

## Frontera corregida: mensajes KikiLog (16-10-2026)

Leer docs/capture/silent-kikilog.md. Ruta43919c04→43ba72ba→4380fc78
NO es control mecánico: cola0110027c recibida por kikilog.ko.
Descriptor.data+c0 arg+cc=0110027c; resume.text+c84..c98 instala
main_thread; record_log→record_acm conflags22 actualiza contador/fechas.
REA confirmó4funciones del módulo, exports a6300-kikilog[-acm]-rea.json.
Hashmóduloa2ce89c05b3d4cc2b133f547e7a613419412ad163e0608c4a2634c02edac3fe0.
REA.textbase1002c; direcciones relativas módulo:mainb8,resumebf4,
record_log1c04,record_acm19e8. Reparacionesmetadata flag-consumer y
timed-command ya aplicadas; no repetir guardas de un solo uso.
Export a6300-silent-timed-command-corrected.json preferido; dosanteriores
con fusiones conservados. Consumer+10 esrelativoarg1, no asumirbasecaptura.
Auditoría17callbacksA6000 completa: a6000-all-exposure-sequences.json,
entradas exactas,0avisos; helperscompartidos todavíapendientes.
Siguiente: seguir4415af79/banco+16f por consumidores distintos deKikiLog;
noinferirsemánticamecánicadelflag. PreguntarecursosUSB/IMX210sinrespuesta.

## Frontera A6300: modo y secuencias Silent (16-10-2026)

Nueva frontera de secuencias: A6000 tabla `43eddd08`, inicializador
`capture-exposure-sequence-initializer.json` (`437ebed8`), 17 filas.
Consultados callbacks filas8/9/10 en `a6000-exposure-sequence-row-comparison.json`:
43b1b024 / 43b1b0c8 / 43b1b114, entradas exactas, 0 avisos de decompilación.
NO confundir fila9 A6000 con Silent: selector437ea8cc la elige con
capture73a==0, contador4b84!=0 y tipo4b80==1. En A6300 ese caso va a fila10;
la fila9 nueva se elige por Silent804==2 antes de evaluar la otra política.
Caso8 normal A6000/A6300 es `Stage_NotifyLongExpNRCapturing` (tag5c), no
acción mecánica demostrada. SilentA6300 omite esa etapa y añade en estado9
repetición de438b5364/SetExposure segúnshortcapture678 ycontador4f98.
Siguiente: auditar las17filas A6000 para no inferir ausencia desde3callbacks.

Biblioteca A6300 nueva: `analysis/ghidra/a6300-libObj.gpr`, importado sin
autoanálisis. REA abrió libObj SHA c70b... correctamente; search_strings
SilentShutter agotó300s sin evidencia, no repetir importación global.
`QueryA6300Library.java` cargaSHAestricto, bias10000 y acepta entradasELF
ARM.exidx o `candidate:` si división verificada. EHABI puedeagruparfunciones:
960294 es40e4; Silentreal96034c (noentradaexidx) comprobadoLLVM.
Software: action66e27c→setter66aedc→modelconv68efc8:1/2→450/451.
seqExecadbf58 limpia9bytes por memset@pltELFef5c8, llama97cca4(40e3)→96034c,
paquete05 00 e3 40 rrrr mm (450→0,451→1), sender941860→osal_snd_msg@pltf3f68.
NON SUPPORTED en96034c rechazaMsgIDno768e/75e6; noespruebadeincapacidadsilicio.
Retorno sender corregidoR0u32+5args porABI (9418c2..cc conservaR0) en
`a6300-silent-library-send-abi.json`; mapper94180c devuelve0inclusoerrores
desconocidos despuésdediagnóstico. Larespuesta9502=f000y85f6 seforma
despuésdeenvío enadbf58, noesperafotograma. Callback680b14msg768flee9984/9985.
RTTISilenttypeinfo100c488/vtable100c478:adbf10/18 retornan0,adbf20/44dtores,
NOsonexec:esteesadbf58(no confundirslots). Docs:a6300-silent-software.md.
Se conservan exports inicialmentevoid ytipo-retorno-sinargs; usar*-send-abi.

EMULACIÓN nueva: `EmulateImagerMode.java`, perfiles hash estrictos, Ghidra
`-readOnly`, 7 casos por firmware, 14 correctos. Outputs válidos
`a6000-mode-emulation-verified.json` y `a6300-mode-emulation-verified.json`.
A6300 Silent2/crop0-1 devuelve4e/4f; A6000 mismoR2 devuelve0b/35.
Arnés acotado512instrucciones/caso; TMode se fuerza a1 en cada paso
COMBINANDO contexto actual para conservar otrosbits. Detiene antesPOPpc,
compruebaR0 yretorno guardadopila45002001; NOejecutaelretorno/cambioISA.
Baselines*-mode-emulation[-thumb/-tb/-step-context/-epilogue].json fallan
porlimitaciónarnés/contexto/retorno, NOsonfallosfirmware. NoinstalarUnicorn:
noestádisponibleyusuarioúltimoinstruyenopaquetes. GhidraEMUexistenteesusado.
Pendienterecurso: nueva pregunta asíncrona concreta A6000USB/documentación
IMX210/soloarchivos; sin respuesta. No asumirmodificacióncámara autorizada.
ÚltimocambioCPUscript7casos verificadosambos; Python26testsruffmypyyaaprobados.
Siguiente línea: comparar restricciones en libObjA6300. readelfdynsymsSilent=0,
archivo17352524bytes, SHAenanalysis/a6300-source.json; usarstrings/PICstatic.

Última validación: 26 tests, Ruff y Mypy correctos. Ambos originales conservan
sus hashes; `.text` del ELF A6300 coincide byte a byte con el original.
Las tres reparaciones recuperaron entradas independientes y decompilaron bien.
No hay cámara Sony visible por USB en este entorno ni autorización nueva
para modificar una cámara. La pregunta de disponibilidad sigue sin respuesta.

Próximo paso: consultar `a6300-exposure-mobius-initialization.json`, función
`437109c8`, en ejecución. LLVM verificó llamada `43710be2`: carga GOT
`441fe5d4` (offset `43c0` de GOT `441fa214`) y llama a `43714910(obj,0)`.
Este constructor entrega `obj+4, fc000000` a `43b8b1e6` (setter de base).
La otra instancia usa argumento1 y base `fc001000`; no confundir objetos.
`43b8c62e` escribe exactamente `base+a1b80`; falta confirmar por export
del inicializador y constructor (este ya está en *-constructor.json).
Se sigue `43804c50 → 43712a38 → 43b8c8aa → 43b8c62e` con indicador
`ExpParam[9] == 3`. Los 41 temporizadores van por `43b8c92c`.
La coincidencia numérica de registros entre sensores no prueba equivalencia:
primera fila IMX210 modo0b=0c; IMX284 modo0b=04 y Silent4e=0c.
Consultar `a6300-silent-comparison.md` para las condiciones completas.

NUEVO enlace completo de clase: 438bfcd8(captura) llama4391a6f4(capture12f0,
capture20,...). Este copia*(param2+7e4)=capture804 aconfig+430.
4391d150(configarg3) evalúa+50c bitsE0: si0, arranca clase0; si+430==2
conserva0 y omiteEFCS. SinoEFCS+45c elige1/3. Flagsanteriores1/5;
diag+7e yarg1+36/+37 sobrescriben. Otra salida44097928=0paraSilent2.
Clase0global44097924→getter4391d440→43918ed0→44096d68→4391a6f4 banco+f5
→4391bd40 copia16bytes+ec a*param3=capture674→selectorcapture67d
→438b5364→43717de4→IMX284SetExposure4371917c(case0),condicionesdoc.
Corrección2: la función de enlaceempezaba438bfcd8 (PIC6bytesANTESpushfcde).
RepairA6300Sequence.java capture-prelude quitóSOLOcandidate438bfcde y
exporta6300-exposure-policy-capture-link-corrected.json tieneentrada438bfcd8
yUNargumento,antesargumentos3/4eranartefacto. No usarprimerexportlinkp/ABI.
IMX284controlrecordGOT441fa530→441ed9bc addrushort1,valinit20.
Tabla441aecd0 fila1 destino441ed9be pone04paramodos0bY4e; clase0máscaraD4
→40ambos. Ese registroNOidentificaSilent;51otrosvaloresmode0vs3difieren.
DFE A6300:4380447c→43804c50 retornaSIEMPRE1; ramaif(ret==0)heredadanoactiva.
43804c50 pasaushortíndice3=(ExpParam+9==3) a43712a38 y41temporizadoresa43712a54.
FaltaresolverMMIOaquí siútil. Noatribuir“cortinatrasera”alflag sinsemánticaeléctrica.
437e0508/0628 sonCaifCom SndEvent/RcvEvent,mensajescapturaNOmecánicademostrada.
438bc800/8b4esperanflags deCAIFsi capture7b3!=0;noatribuirlosamecha.
Últimoconsultadoa6300-exposure-mobius-program.jsonsession14601completado.
LecturaUSBsoloidentificación: sinSony054cvisibleenentorno;noacciónsobrecámara.
Internet: búsquedaIMX210AQLnoaportóhojadatosSony;noafirmarinexistencia.
SonyprimaryA6300spec https://www.sony.jp/ichigan/products/ILCE-6300/spec.html
yhelpguideSilentTP0000824870ja confirmanopciónoficial, nohardwareIMX210.

Leer docs/capture/a6300-silent-comparison.md. No entregar informe final;
seguir trabajando hasta resultado demostrable, sin afirmar parche funcional.
438be684 recibe modo/crop/tipoSilent: tipo2→modo4e(crop0)/4f(crop1),
salvo modo5→c,1b→1b antesdeSilent. TablaIMX284441afd10(21modos):4eíndice3,
0bíndice0,4f ausente. SetMode4371949c→virtualc0→43718c2c escribe124registros
stride28 tabla441aecd0;51valores difieren entreíndices0/3. Noatribuirbitsfísicos.
Captura804==2 selecc438af40c fila9tabla4407ee78,438afa10fila15tabla4407fa8c.
Init438afc0c→43bbaf2e→438a7b58 ponecallbackregistro+8. GOT44200800→43bda463
Silentprimera;44201af4→43bdc8e5Silentsegunda;normal8→43bda3b3/14→43bdc7ed.
Callback43bda462,estado2 llega43803c78(capture4e0,...)→43717dbc→slot20SetMode.
Primerexportinit fusionófunciones/375avisosPIC: inválidoparaflujo. RepairA6300Sequence
quitaSOLOmetadatos funciónerróneainit,hashestricto,sinborrarinstrucciones/bytes.
Sembrar438a7b58,43bbaf2e,438afc0c recuperó3entradas,0avisos. Exports*init-repaired.
A6000equivGetImagerDriveMode437f7f98 llamador437f7ff0→capture4d0,solo2args;
sinramaSilent. SetMode436d6b50 rechaza>47hex,tabla43fea07013modos:
0b,01,05,10,07,12,03,0a,0f,18,1a,19,2f. Virtuala0→436d6570 stride20.
Modo4eA6300NOsepuedeportarcomonúmeronibytes. NOdemuestraimposibilidadsilicio.

CORRECCIÓNpropia: wrapperSetExposureA6300 es43717de4;43717df8esinterior!
LLVMverificópush43717de4+branchnulo,slot28endfc. RepairA6300Sequence.java
argexposure-interiorquitósolofuncióncandidate43717df8 (sinbytes). Nuevoexport
a6300-exposure-wrapper-corrected.json entrada43717de4correcta. Noseguirrefsdf8.
LLVMllamadoresdirectosde4:438b42a4(fn438b4038),438b5414(fn438b5364),
438b5af2(fn438b597c),4394ed62(fn4394ec54). A6300proyecto~60funciones,coberturaparcial.
438b5364callbackSilentestado4 llama438c0008 quecopiaExpRsvParamal capture674
(selector+9=capture67d). Después fuerza0 sidispositivoclase2/3, SetExposure
si capture4f98==0. Fuente backend*(GOT441fb840+28)==1:
4391bd40 luego439199e8; ambos exportados en a6300-exposure-packet-copy.json.
4391bd40 copia16bytes banco+ec (o17c si capture7ad!=0) a*param3=capture674;
clase viene banco+f5 (o185alternativo). 439195e4 seleccionaGOT441fca48/441feb50.
4391a6f4 escribe banco+f5 desde44096d68;43918ed0 escribe44096d68 desdegetter
4391d440→44097924 despuésde4391cd24. Este último invoca4391d90c y4391cb58;
cb58estemporización,noescribeclase24. Últimaquery a6300-exposure-policy-input.json
func4391d90c en curso. No confundir cantidadesdeargumentosinferidascomoABIprobada.
43919f80 ajuste claseporotrosmodos,notipoSilentdemostrado.
Nohayprocesodecámara,paquetesnuevosnicommit. Pythonintacto;26tests/ruff/mypy
aprobados en esta continuación, originales A6000/A6300hashidéntico.
REA61evidenciasprevias, nuevosJSONsnativosGhidra.

## Instrucción vigente 16-10-2026: comparar únicamente serie A6000

Ya extraído A6300; origen/hashes exactos en analysis/a6300-source.json.
av-cam13382836bytes,sha6a5a25728dc378c99d5b883c9743b69faa5f719ff844b4e1788e73bd5ae7be16.
ProyectoNUEVO analysis/ghidra/a6300-liro.gpr; sin autoanálisis amplio.
QuerySilentLiro.java ampliado a2perfiles estrictos (tamaño+hash); A6300
readonlyhasta43d00000, A6000conserva43bc0000. Baseline scriptviejo rechazó
A6300 porhash antesdeeditar; nuevoexportA6300correcto yregresiónA6000
a6000-query-profile-regression.json correcta. No se alteró firmware.
Envoltorioanalysis/a6300-av-cam-analysis-view.elf: llvm-objcopy requiere
--change-section-address=.data=0x43541000 ANTESderenombrar a.text;
el intento con.text quedóVMA0yse corrigió. readelfahoramuestra43541000.
A6300tablaSilent40e3fila filec78d08→437ef611/entry437ef610 guarda
44018e64=common44018c00+264. EFCS4099filec788c8→437f0a55 guarda+23c.
Gettercommon437f4824 retorna44018c00. CheckSilent438c81bc compara+264.
Mapper438c41c8: tabla43c9e530{0,2}, estado0→tipo0,estado1→tipo2;
diagnósticoGOT441fe6c0+7a fuerza2. NO confundir tipoSilent2 conselectorExp2.
Caller438a5d90 (equivalenteestructural capturaInit43afa0ceA6000) obtienejob
438a68c8, leejobgetter+2ac, mapper→capture+804; inhibe tipo si+4f6c!=0,
byte7f8!=0 o+1f0==19hex; tipo2→campo7a4=1. Setter común43800e90
lee(*psRam4401ed70)+264 (punteroshort+132), mapper→global440243cc.
Exportsa6300-silent-receiver/type-check/capture-silent-configuration/
silent-common-producer. No nuevoanálisisREA: proyectoGhidranativo separado.
IMX284RTTI typeinfo441afca4→name43d9d416; vtablemethodpoint4418c4d8;
slot20→4371949c(SetMode),28→4371917c(SetExposure),30→4371ab84(SetRead).
SetExposureIMX284 acepta0/1/3/4, RECHAZA2 por defecto! TipoSilent2 NOes
selector2delIMX210: seguirtransformación ymodolecturaantesdeetiquetarnúmeros.
Última consulta puede seguirsession7063: a6300-silent-capture-readers.json,
entradas438af40c,438afa10,438be470,438be6f0,438c0dc4, lectorescampo804.

El usuario descartó A7S y pidió usar la primera de la serie A6000 con
obturación electrónica completa. Referencia elegida: ILCE-6300, Silent Shooting
documentado por Sony; anuncio03-02-2016. NO continuar analizando A7S.
Se conserva su descarga/extracción ya realizada, sin usarla para conclusiones.
Descarga A6300 2.01 oficial en curso: Update_ILCE6300V201.exe, URL obtenida
del data-url de support.d-imaging.sony.co.jp/www/cscs/firm/?mdl=ILCE-6300.
Objetivo: resolver el consumidor de Silent y contrastar clase de exposición,
secuencia y controlador con A6000. No entregar informe final mientras siga
abierto el resultado solicitado. La pregunta asíncrona de disponibilidad de
cámara sigue sin respuesta; no asumir autorización de escritura a cámara.
Usar Python existente /home/nicolas/.local/share/pmca-venv/bin/python para
fwtool: sistema carece de Crypto; no instalar paquetes. El EXE A7S fue
reempacado2022 y fwtool rechazaUnknownexe; había DAT UFU sin comprimir dentro.
Extracción alternativa validóCRC por fwtool.sony.dat.readDat antesdeguardar
subrango hastaDEND. Si A6300 tiene igualwrapper, repetir método, no ejecutarexe.

## Continuación E020: EFCS unido al selector IMX210

Extensión DFE:437f8a50→43ae9462→43b04658. Este helper programaMobius y
retornaSIEMPRE1: noatribuirlallamadaalDFEheredado dentroif(ret==0).
Selector==3 enushortíndice3→436d055c→43ad78c2→43ad766e guarda32bits
enbase+0xa1b80. GOT44025254→obj43e7efe0,+4base. Inicializador436d06d8
llama436d2004(obj,0)→43ad6f32(obj+4,0xfc000000), destinoFC0A1B80.
41temporizadores→436d0578→43ad7944→43ad76a6. Sinsemánticaeléctrica.
Caso2IMX210 ademásmodifica registrosGOT4401f790/44025b0c conargs+8/+14,
ytemporizacióndiferente; NOreduciracambiarbit40.
REA get_evidence_bundle confirmóIDev_2891468c... retención61/hashoriginal.
26tests/ruff/mypy aprobadossinavisosnuevos enesta continuación; Pythonintacto.

Leer docs/capture/efcs-capture-selector.md. Copia que faltaba:437b5b14 pasa
43eb2680 como param14 de4384b268; llamada4384cb38→437b03c8 copia0x92c a
GOT44021ba8→43ea976c. Incluye EFCS+41c.4383fc48 selecciona ese banco u
otro43eee9d4 (origen alternativo pendiente).43842158 lee+41c: clase normal
1/3, con otros flags5; diagnósticos permiten0..7.4383f5e4 guarda getter43842404
en43eedecc.43841070 escribe clase registro de4383fb6c+6d.4383fd6c copia
registro+64(16bytes) a *param3.437f8a50 establece *param3=captura+64c,
si backend*(GOT44020e90+24)==1: clase llega captura+655/ExpRsvParam+9.
438c828c llama437f8a50→SetExposure, pero sobrescribe selector0 si43a12c64
devuelve2/3; llamada depende+4b9c==0. No omitir condiciones ni afirmartrazaHW.
IMX210 clase1 máscaraC4,3 D4,2 94 sobrebitsD4. NO probar2comoSilent.
La anulación diagnósticaNOesinterfazvalidada de SilentShutter.
437ea8cc nuevaentradaThumbverificada porprólogo,paddingypoolprevio; string
CaptureExposure_Selector.cpp PIC437ea95e/a9b6/a9e0. La consulta@interiorfalló
antes yseconserva capture-exposure-selector.json; recuperada en *-recovered.
Selectorusa campos73a/4b84/4b80/4ee4/4ee8, filas20bytes GOT44025f60.
73a procede437f87ac→43aef26a, NOlecturaSilent. Proyecto37691funciones.
438b83a0 switchfinal ahoraresuelto: diagnósticoGOT4402546c+75,noSilent238.
Bancosprevios:437b5e70→4383bc6c/4383bf2c→4383c9dc/b790/bfd4.
436ef534/570/600 soloalmacenanestado43e849c0, noMMIO.
Guardar nuevasconsultas efcs-*.json yshutter-source-bank-*.json. No repetir
análisis yaexportado. Silent238y fin electrónico trasero siguenpendientes.

## Continuación tras límite de uso — E018 y ruta P2S en curso

Corroboraciónexterna nueva:TechInsights DEF-1412-801, ficha primaria de su
desmontajea6000, identificaIMX210/SON-IMX210AQL. URLen docs/sensor-investigation.md.
No esinspeccióndelusuario nihojadatosregistros. InventarioHW01actualizado S-HW-02.
SonyespecificacionesoficialesILCE6000 yguíaEFCSreconsultadas15-10-2026.

Leer docs/capture/silent-imager-consumers.md además del informe E015–17.
Proyecto Ghidra ampliado: 220 entradas de despacho sembradas y 37677 funciones
registradas. Autoanálisis limitado a300s terminó por TIMEOUT: NO llamarlo completo.
Se guardó correctamente y las consultas posteriores usan -noanalysis; no reimportar.
NO ejecutar ExportSilentLiro.java: borra metadatos. Usar QuerySilentLiro.java,
que verifica SHA original y conserva funciones. Prefijo @0x... consulta SOLO función
existente contenedora, sin crear función desde una instrucción interior.
Export contiene query y entry: pueden diferir por colas compartidas; no ignorarlo.
Query divide bloque en43bc0000 y marca región anterior readonly en proyecto,
con DecompileOptions RespectReadOnly=true: hipótesis estática, bytes sin cambiar.

Vtable IMX210 punto43fcc090, typeinfo43fea0a4→nombre43c941b0 ybase43fea23c.
Wrappers diagnósticos: SetMode436d62e4→slot20→436d6b50;
SetExposure436d6320→slot28→436d6f6c; SetRead436d6398→slot30→436d7e08.
ZAF: wrapper436d635c→slot2c→436d67e4;436d63d4→34→436d74b8.
CORRECCIÓN E017:436d67ec/74bc eran interiores y variantesZAF. RepairImagerEntries
los retiró y creó entradas vtable. Flags436d9f70 1/8 son filtrado diagnóstico,
NO aplicación física. Modo11hex no etiquetado; SetExposure/Read lo rechazan.

SetExposure normal leeExpRsvParam byte+9, casos0..4. Modifica bits04/80/10/40
enregistro de tabla43? pointer4401ca2c, obtenido GOTbase4401eee4+
literal436d72d4=slot44020f9c→4401ca2c. ushort inicial1,bytevalor+2=40.
Sin datasheet/formato completo, NO nombrar esos bits cortinas ni asignar enum.
Capturaobjeto+64c→ExpRsvParam y+655→selector+9 en438c7800/438c828c
y rama43b1af3a que pasa por438c87f0. Valores escritos4/0/1 segúnfase,
NO modos identificados de obturación. Otro escritor4389cb8c copia datos genéricos;
no asumir misma identidad solooffset655. Exports silent-exposure-mode-writers,
imager-exposure-verified, efcs-hardware-commit, imager-p2s-transport.

Transporte nuevo:436d839c (vtable+38) prepara y aplica listas de registros:
436d75f8→436d5e04/43ad9004→formateador→43ad8de4→436d5ed0.
436d5ed0 escribe bytes a baseP2S+(index+10hex)*4. TablaGOT440202b0→43bc14e8,
3tripletas: f3c00300/f3c00800/f3c00900;fc088300/fc088800/fc088900;
fc089300/fc089800/fc089900. Direcciones estáticas, no mapa físico medido.
436d5bcc espera bandera0x18, diagnósticoP2SWaitTransComp; no ACKdeimagen.
Wrapper43ad911c flag!=0→vtable38,0→3c;43ad9132→vtable48 (43ad9232
espera436d5bcc). Hay vínculo driver→P2S, pero NO Silent→driver demostrado.

Alias comunes resueltos:43792a0c copia560 desde43edf684 a43e9b548 vía43804c5c
(ramaalternativa43b00d06 copiaobj+8). Inicializador4378fa70 llama43ae8eae
(base43e9b548, tabla43e99208);43ae8d56 asignatabla[0]=base,[2]=base+5a4.
DESCARTAR43792fb4 como lectorSilent: lee tabla[2]+238=base+7dc, FUERAde560.
Es común/imagerconfig diferente; igualoffset NOindicaSilent.
Trabajo:slot44023bbc inicialmente43ed4d28;copyjob+48,Silentjob+280;
getter437dfe4c retornajob+8→Silent+278,EFCS+250.
43afa0ce pasa getter+40 (=job+48) a438b83a0, destinoobjcaptura+20;
traducciónexplícita no leeSilent238/EFCS210, con switchfinalno recuperado.

EFCSlector437cac5c usa (*contexto+210) ysalidas+11c/11d en43af30e0.
43844e80 lee (*contexto+210) yguarda param6ushort*+20e=byte41c.
Caller437b5b14 pasaGOT44023eb4→43eb2680 como param6, campo43eb2a9c.
Lector43842158 usa param3+41c, escribeestado43eefb7c yglobals; su caller43841070
reutiliza iVar14: primero437b0610 devuelve CONTADOR43ea6ad0, luego4383fc48
devuelve el puntero real (GOT44021ba8→43ea976c o440249a4→43eee9d4).
NO es el mismo bloque43eb2680 delbuilder; falta seguir copias. VerE019.
Silentoffset-readers export12consultas:11decompiladas,43abb770sinfunción;
variasestructurasdistintas, no consumidorSilentconfirmado. LLVMlineal34LDRword238,
sinLDRDoffset234/238 en esa pasada; no coberturaexhaustiva ni prueba de campo muerto.

E018 yE019 escritos; README, plan, índices yvalidación actualizados.35exports
de funciones conhashoriginal;26tests,ruff,mypycorrectos. SinGit/sincommit.
Pruebaextra:436d79b0→slotGOT44023598→43fe995c,119punteros+NULL;
índice1=4401ca2c controlmodificadoSetExposure.436d839c llama75f8(modo2,list).
Exposiciónselector→registrolista→P2Squedaunidoestáticamente, sinsemánticafísica.
RsvParamout43e9d034+9←builder43849fb8 fuenteGOT44020c9c→43eb35d0+cd.
43b08750→43b0893c seleccionabanco *sourcebyte0, copiafila16a+ c4..d0;
selector viene fuente+banco*10hex+0d. NO confundir fuenteconGOT4401efbc:
43eae21c esotrobloquedecálculo.43843a44 fuenteconfigbancos=
GOT44020b20→43eb05d8 +224; ramaestado3copiacuatrofilasdesde+2c.
Seguirproduccióndeestosbancos ycoordinaciónmecánica; Silent238noenlazado.
RemoveInteriorQueries ejecutado: retiró3definiciones,JSONrechazadosconservado.
Nuevo4381106c diagnósticoStrtExps:copiashared[9]16bytes→stack, ajustaSVD y
llama43ae935a→436d6320 SetExposure. shared[9]=base43e9b548+1aec=43e9d034.
Main4378fef4 llama437b4e88(&43e99208,&43e9d034);437b4e88→437b617c,
este→4386b5ec(...,out) y43849fb8(...,out,...). Sigue exportshutter-exposure-selector.
MechaCommon:4386d3b4 construyecmd16bit desdecommon+0xe,437cfe94 adapta
campospormodos900/910/911/912/920/930/931/940/941/950/960. Sinmapacortinas.
Exportshutter-mecha-common; no atribuir esosIDs a comandosfísicossinreceptor.
Consultasmalas interiores creadas:437b4ed2,436d6520,4378f4d0. NOusarlascomo
entradas; conservarJSONperoretirarfuncionescandidate delproyecto ymarcarlas.
Última sesiónheadless puede seguir: consultar session_id del últimoresultado.
26tests,ruff,mypy pasaban antes de esta continuación; no códigoPythoncambiado.
REAimportó61registrosprevios convalidaciónID; no nuevoanálisisREA vivo delblob.
No cámara, no firmwareejecutado, no instalación, sinGitutilizable/sincommit.

## Último encargo: terminar SilentShutter — E015/E016/E017

Leer docs/capture/silent-shutter-status.md antes de continuar. Avance mayor:
LIBOBJ factory Ghidra función que contiene ae81b6 compara768e, construye
988fa0(param,msg,CamMgr,relay); constructor instala ejecución988e0d. Base
a25ee0 conserva mp_CamMgr enseq+20; accessor a25fd0→CamMgr+20, constructor
aeade4 configuraqid30001. Asociaciones de E012/E014 ya resueltas estáticamente.
Acción ELF689ea4 lee291 y llama686d10; initGhidra68e48c transforma291→9983;
callback68984c lee9984SET/9985ACT y publica768f. Modelo1/2↔450/451.
Lookup Ghidrab04d20 indexa tablaff565c (filefdd65c), prueba450=Off/451=On.
On→byte1, Off→0, no son ya hipótesis.

Receptor fuera del atlas ELF: nflasha3_unpacked_unpacked/av-cam.bin,
11427236bytes SHA b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9.
LIROmagic4c49524f/version4; baselógica43541000 porvectores. NO es dirección
física medida. Liroko verifica/copiaAPIs. RAW direcciones NO suman10000.
Cola30001 en bucle437fee08→wrapper43561260→APItable1bc=liro_osal_rcv_msg_tmo.
Tipo5→438052d8, busca220tripletas12bytes. Tabla fileabe30c..abed5c; Silent
fileabec60 {40e3,438032d5,0}, handler438032d4 guarda byte8 en43edf684+238
=43edf8bc; EFCS4099→43802e4c guarda+210. Flag0→4375dcd4 marca un byte.
Snapshotparam437dfd58 copia560bytes deglobalalobjeto+48, incluyeSilent a+280.
NO se identificó consumidor físico. Desplazamiento238 en otras estructuras
no acredita mismoestado. No declarar campo muerto por xrefs vacías.

RTTI IMX210 driver enavcamfile7531b0, ImagerDrvParam_IMX210 en753269;
es candidato de sensor, NO chip/revisión física confirmados. Candidatos
436d62e4/436d67ec/436d74bc/436d7e08: diagnósticosmodo/exposición/lectura,
sin vínculo probado aSilent. No etiquetar modo11 como silencioso sin tabla.
Proyecto Ghidra PERSISTENTE analysis/ghidra/silent-liro.gpr; export
silent-liro-functions.json,8funciones decompiladas; scriptExportSilentLiro.java
limpia metadatos del proyecto dedicado y recrea8semillasThumb, sinfullanalysis.
Reabrir con headless-process, ver comando del informe. No usar script sobre
anotaciones manuales que se quieran preservar. Verifica hash original cargado.

Exports REA silent-deep-libObj34reg, silent-deep-avcam61, silent-liro-loader5,
silent-ui3, todos snapshots y sesiones cerradas. REA raw no detectó todos los
handlers Thumb; no procedure ≠ ausencia. No overrideREA_GHIDRA_LANGUAGE_ID enraw.
viewUnified7 importa nodoSilent (relocVA5f7b8), sin prueba de visibilidad.

Nuevo src/liro.py TDD7tests; total26,ruff/mypy correctos. CLI generó tabla220
reports/silent-liro-dispatch.json. No instalar paquetes ni cámara enesta pasada.
No se terminó viabilidad física: siguecategoríaE, sin parche. SinGitutilizable.

## Prioridad vigente: obturación, EFCS y fin electrónico

E014: libObj ELF adaf66..adaf86 configura owner+20 con qid30001 y owner+24
con40193 (setter a1b198); +8=20002. Coincide estructura con accessor de
secuencias pero misma instancia NO demostrada. libosal_uipc nflasha15
0c6b87a... abre /dev/uipc y qid sin bit8000→ioctl80000004. Kernel
osal_uipc.ko82a92b... transforma/encola genéricamente, receptor final pendiente;
dispatcher pseudocódigo con índice dudoso, contrastar instrucciones antes de
asignar casoioctl. Exports analysis/rea/shutter-osal-evidence.json (9) y
shutter-uipc-kernel-evidence.json, snapshots guardados y sesiones cerradas.
No resolver arbitrariamente copias OSAL por nombre; no inferir CMOS de qid.

Leer docs/capture/shutter-investigation.md (E012), docs/capture-pipeline.md
(E013) y docs/capture/research-plan.md. El usuario priorizó EFCS y averiguar
si se puede sustituir la cortina trasera. No afirmar viabilidad ni imposibilidad.
EFCS oficial A6000, On por defecto; comienzo electrónico no acredita fin electrónico.

libObj VA ELF: acción EFCS 0x6896ac (75fa/9776), Silent 0x686d10
(768e/9983); secuencias candidatas 0x95a308 y 0x978e0c envían 9 bytes.
Dispatcher 0x9bbb5c: selectores 4099→99e968,40e3→99b004, TBH y GOT
resueltos con PT_LOAD correcto (GOT file offset = VA-8000). Sender a1b21c
usa osal_snd_msg, cola objeto+4; receptor desconocido. Éxito 9502=f000 se
construye tras envío sin confirmación física en ese tramo. NO son registros
del sensor. Registro reproducible reports/efcs-silent-dispatch.json.
Registro de acciones→secuencias, modelo, receptor, sensor y lectura pendientes.

REA capturó 21/6/115 registros ScalarDaemon/libcamera/libObj; exports
analysis/rea/capture-*-evidence.json y snapshots. Sesiones cerradas. libObj
perfil ARMv7 reducido; snapshots no evitan reimportación. E013 prueba factory
Ghidra118f10 caso1008→TakePicture; captureStart emite modelo3/event7 hacia
11004003/destino2 ModelManager; captureStop emite3/8, NO prueba cortina.
Botón físico aún no mapeado; AutoReview callbacks son metadatos/notificaciones,
no prueba de píxeles de foto final. Pipeline completo sigue abierto.

Nuevo src/thumb_refs.py con TDD, 4 tests; total19, ruff/mypy correctos.
Solo candidatos PC-relative: no control de flujo/clobber. Descartar PDF
helpguide.sony.net/ilc/1410/v1/en/print.pdf: es ILCA-77M2, no A6000.
No cámara, firmware ejecutado ni parche. Sin commit por .git no utilizable.

## Alcance vigente: proyecto general

El usuario amplió el objetivo a **Sony A6000 Hardware & Firmware Reverse
Engineering Project**. El obturador es ahora un subproyecto. Leer primero
README y docs/project-scope.md. No borrar ni mover las evidencias originales.
Dos líneas: docs/architecture/README.md y docs/capture/README.md.

Nuevo atlas: reports/elf-atlas.json, generado con `python3 -m src.atlas`.
679 rutas ARM, 641 hashes únicos, 147 ejecutables, 469 bibliotecas candidatas,
63 módulos; 391 asociaciones funcionales desconocidas. 3890 DT_NEEDED:
3882 resoluciones candidatas y 8 ambiguas. Cache de contenido+productor
comprobada (679 aciertos en segunda pasada). Clasificación heurística y
dependencias declaradas no son responsabilidades ni cargas en ejecución.

Inventario físico: docs/hardware-inventory.md, documental y sin BOM de placa.
Prioridades: identificar chips; resolver libc/ABI/cargadores y ambigüedades
libosal_uipc; seguir libsdcom y la conversión SilentShutter; caracterizar init,
arranque normal y recuperación. No existe recuperación de hardware demostrada.

## Investigación previa conservada

Actualización de la continuación: leer docs/silent-shutter-trace.md (E007–E009).
REA MCP funciona tras reinicio. CautionConfig.so construye nodo SilentShutter
con dos punteros On/Off y propiedades. libsencore.so no aporta prueba de
controlador CMOS. El reintento de libObj.so con ARMv7 y perfil reducido terminó:
xref Ghidra 0x9ab038 a error NON SUPPORTED. Rutina candidata ELF 0x99b004 acepta
mensajes 0x768e/0x75e6, parámetro 0x9983 y valores 0x450/0x451, convirtiendo a
byte 0/1. Falta seguir llamadores y consumidor del buffer; no atribuirlo a un
comando del sensor. Sesiones cerradas, snapshots y evidencias conservados.

El encargo original está en el adjunto del chat: determinar exposición completa
sin cierre mecánico, sin asumir soporte. Continúa vigente dentro del subproyecto.

Fase 1 realizada: descarga oficial DMG, DAT validado contra hash publicado, cabecera 3.21, árbol extraído e inventariado. Fase 2 parcial: símbolos y desensamblado LLVM; REA/Ghidra inicialmente bloqueados; ahora instalados y análisis ARM de libcamera.so ejecutado con éxito. Fases posteriores abiertas. Categoría E.

Pistas prioritarias: `libObj.so` (cadenas SilentShutter y CamUser), `libsencore.so` (S_IMAGER_CURTAINMODE), `libScalarDaemon.so` (captura con símbolos), `libcamera.so` (puente SDComMsg_Basic). No asumir que cadenas comunes son capacidad habilitada en A6000.

El usuario autorizó posteriormente habilitar REA. Instalados REA 6.5.0, Ghidra 12.1.4 y JDK21 portables. Próximo paso: usar ./scripts/rea para resolver xrefs de libObj.so. Importar ELF ARM32 LE, distinguir ARM/Thumb, resolver xrefs de SilentShutter y rutas de rechazo/selección de modelo. Después identificar el receptor y el controlador de lectura; no parchear antes de demostrar finalización electrónica.

WBI1 secciones recuperadas; direcciones declaradas por cabecera no son prueba de un mapeo vivo. `nflasha5` contradice la clasificación TPZL genérica del proyecto base. No hay NAND de una cámara ni firmware comparativo. No existe documentación verificable del modelo/revisión del sensor.

No tocar cámara, bootloader, NAND, calibración o identidad. Instalación de dependencias de REA autorizada por petición posterior; sin push ni producción. Pruebas y calidad pasan. Cambios sin commit por ausencia de repositorio utilizable y .git de solo lectura.


## Sesión 2026-10-16 — manuales y mapa GPIO/IMX210 (leer primero)
- Manuales en `references/manuals/` (MANIFEST.md con SHA-256/URL). Esquemas A6000 hojas 6-11 (IC5700), 6-26, 6-30, 6-33.
- VERIFICADO: P4D→1ST_CURTAIN_MG, P4E→2ND_CURTAIN_MG, P4C→CA_1ST_CURTAIN_START, P4B→CA_RELEASE_LOCK_MSS (A6000 y A6300 idénticos) y son GPIO salida en los 6 perfiles Darwin. Ver docs/capture/fm3-gpio-shutter-mapping.md. Corrige la reserva sobre SIN2_2/SOT2_2.
- VERIFICADO: matriz de 59 registros×13 modos IMX210 en `0x43fe9b74` (analysis/imx210-setmode-register-matrix.json). Modos «vídeo» 05/10/07/18/1a/19 comparten los mismos registros. Ver docs/capture/imx210-video-readout.md.
- Estado de la pregunta principal: ver docs/capture/electronic-still-low-resolution.md (sin evidencia de ruta electrónica aún).
- Scripts nuevos: scripts/{schematic_pin_nets,fm3_gpio_literals,imx210_modes,thumb_callers}.py; tests/test_{fm3_gpio_literals,imx210_modes}.py.
- Próximo: llamadores indirectos de SetMode slot +0x20; `0x43a12c64`; función modo→geometría; registros ADC de SHUTTER_PI; origen del «tipo HW» (0x1B080).

## Sesión 2026-10-16 (parte 2) — pila de parámetros IMX210
- Ruff/Mypy no están instalados (`ruff`, `mypy`, `pyflakes` ausentes; no se instala nada). Sustituto: `py_compile` + comprobación AST de imports; se quitó `import struct` sobrante en `scripts/thumb_callers.py`. Ambos tests pasan.
- Resolución/fps/filas del IMX210 viven en `CSDrvParam/CamcoreDrvParam/ECDrvParam/LCDrvParam` devueltos por GetModeInfo (vtable `+0x24`, `0x436d96b8`), no en la matriz de 59 registros. Detalle y direcciones en `docs/capture/imx210-video-readout.md` (sección «Sesión 2»). Bloqueo: constructor de `ImagerDrvParam_IMX210E` (typeinfo `0x43c94269`).
- P2–P5 no iniciados.

## Sesión 2026-10-16 (parte 3) — constructor y modos IMX210
- Resuelto: ctor `ImagerDrvParam_IMX210E` `0x436d8774` (vtable `0x43fcc150`), llamado desde `0x436d72e8`; las **entradas** por modo están en rodata (`0x43bc16dc` filas 72 B, `0x43bc1c20` 24 B, `0x43bc1d58` 36 B, `0x43bc1ae8/1b84` A/B) y los arrays de salida se calculan en `0x436d9d00`. Volcado: `analysis/imx210-drvparam-inputs.json` (script+test `imx210_param_tables`).
- Hechos clave: 0x0b/0x2f = 6000×4000, periodo 3 608 064 ud = 66,8 ms (54,054 MHz); modos vídeo = 1996×1124 (≈2,2 MP, 59,94/50/48 Hz); 2000×570/800/232, 1024×684 para otros. Detalle en `docs/capture/imx210-video-readout.md` («Sesión 2b»).
- Pendiente: qué mensaje fija `captura+0x4d0` para LV/vídeo (handler `0x4380377c`); decompilar EC/LC (`0x43543dc8/fa0`) para exposición; buffer/JPEG (P2); P3–P5.
- Validación: tests de scripts nuevos OK; Ruff/Mypy siguen sin estar instalados (no se instala).

## Sesión 2026-10-16 (parte 4) — pipeline P2
- Corrección: handler `0x43803780` NO fija el modo IMX210 (guarda byte 0..3 en `DAT_43edfb54`); selector de captura `0x437f7ff0` solo produce 0x0b/0x2f/0x01/0x0c/0x17/0x1b/0x35. Modos 1996×1124: usuario NO identificado.
- Mapa del pipeline en `docs/capture/electronic-still-low-resolution.md` («Sesión 2c»): `ReadExecuteBase 0x438c7800` → SetMode `0x43795a60`/`0x436d62e4` → DFE/CamCore Start; `Stage_SACC 0x43782464` (NFLASH) → Develop → YC → SDF `ApiEncodeJpeg 0x43653d34`. Nuevas herramientas: `scripts/string_xrefs.py`, `scripts/ghidra_dec.sh` (`!addr` entrada exacta en QuerySilentLiro.java), thumb_callers con B.W. JSON: `analysis/ghidra/imaging-cap-exec.json`, `imx210-setmode-callers.json`, etc.
- Siguiente: stage/etapa de Live View y vídeo (quién llama EnterCapturingLv, 0x4372858a); formato RAW/buffers (`0x43ae7d2e` AsyncAllocNew 0x167, `0x4379f618/fb48`); decompilar EC/LC; punto Darwin en la secuencia `0x43b1xxxx`.

## Sesión 2026-10-16 (parte 5) — selector de modos y rutas frame→JPEG
- RESUELTO: selector de modo de vídeo/LV del IMX210 = `0x4380e43c` (`switch(cfg[+0x264]>>15)`; escribe `DAT_43eea2e4`). Vídeo 1080 = 0x1A/0x10, 24p = 0x19/0x07, HFR = 0x12; Live View = 0x01/0x03 (0x0F en AF). Cadena hasta `SetMode`: `0x4380f440` → `0x43e994d0` → `0x43e99320` → `0x4378e334` (`SetSequenceMode_img`) → `0x43795a60`. Ver `imx210-video-readout.md` «Sesión 3».
- Corrección: `AfterViewContRcStart*` es revisión post-captura; `EnterCapturing*` son banderas. Ver «Sesión 3» en `electronic-still-low-resolution.md`.
- Rutas frame→JPEG: SDF `0x43653d34`; SFRA LiveView (consume JPEG, 640×360, `0x439a3b50`); codificador directo `0x4379b180` con anillo `JpegRingBuf` (usado por `Sequence_HSRecGolfshot`; habilitación en A6000 NO VERIFICADA).
- EC/LC = temporizaciones Q8 del receptor, no exposición; `SetExposure` tiene submodos 0..4. Registros sombra sin resolver.
- Nuevo: `scripts/string_xrefs.py` + `tests/test_string_xrefs.py`; exports en `analysis/ghidra/` (mode-*, lv-*, jpeg-*). Ruff/Mypy no instalados (`py_compile` OK).
- Siguiente: productor del JPEG de LV (mensaje `0x61003c`, tarea de buffers); si `Sequence_HSRecGolfshot` está habilitada en A6000; formato YC/estride; submodos de `SetExposure`; origen de `ctx.b[+0xb1]`.

## Sesión 2026-10-16 (parte 6) — ruta C reconstruida
- VERIFICADO: `0x4379b180/b058/aaf4` solo se llaman desde `FUN_4354d740` (Sequence_HSRecGolfshot.cpp). Entrada YC = dos punteros `obj+0x6a8/+0x6ac` de un trabajo RCV (`0x43798ccc`, compartido con película `0x4381592c`); salida = bitstream en `0x43e9f014` (+8 base, +0xc capacidad) y anillo JpegRing. No pasa por Stage_SACC, Develop ni Darwin.
- NO VERIFICADO: alcance en A6000. Gate por modelo `**FUN_4378f9b4()` (`0x43e99208`) vs 0x120/0x127/0x129; código de la A6000 desconocido; despachador de `0x4354c6d0/0x4354d740` (solo puntero en `0x44022478`) sin resolver.
- Test nuevo `tests/test_jpeg_ring_callers.py` (ok). Detalle en «Sesión 4» de `docs/capture/electronic-still-low-resolution.md`.
- Siguiente: despachador de `0x44022478`; inicializador de `0x43e99208[0]` (código de modelo); productor del JPEG de LV (`0x61003c`).

## Sesión 2026-10-16 (parte 7) — despachador, «modelo» y SFRA
- VERIFICADO: la tabla `0x44022300–0x4402251c` es la GOT PIC (base `0x4401eee4`). `0x4354c6d0/0x4354d740` los elige el selector `0x4380e43c` por `(cfg+0x264>>15)` = 10/9, con modos IMX210 0x11/0x08 (no soportados por el IMX210). Tabla: `analysis/seq-dispatch-table.json` (`scripts/seq_dispatch.py`, test ok).
- CORRECCIÓN: `*(short*)*FUN_4378f9b4()` es el código del mensaje en curso, no el modelo. Ya no hay «gate de modelo».
- CORRECCIÓN: `0x61003c` es un pool de mensajes genérico; `0x43b4c4e2` analiza un JPEG, no lo codifica. SFRA tiene comandos `SET_PATH`, `SET_JPEG_PARAM`, `GET_JPEG`, `LiveView SET_JPEG` (`0x439a1864`).
- Siguiente: quién envía los comandos SFRA y el formato de película del host (código fuera de av-cam); productor HW del JPEG de SFRA; `SET_PATH` hasta CAIF/Darwin.

## Sesión 2026-10-16 (parte 8) — productor del JPEG de SFRA y cliente
- VERIFICADO: SFRA (`ScalarInfraAsyncMain`) envía la codificación al **SDF** (`0x56000f`, «Msg to SDF», 0x54 B) y recibe tamaño comprimido para el control de tasa; el motor es el acelerador SA vía `ddl_jpeg`/`tsk_jpeg.c`/`SA_JPEG_ENC` (mismo que `ApiEncodeJpeg`). `GET_JPEG` solo recoge buffers READY. Tamaños hasta 1920×1080 (tope 0x3f000 B/JPEG).
- VERIFICADO: cliente = `libInfraStreamingServer.so` (Linux, nflasha15): Live View Wi-Fi/PTP, acepta anchos 320/640/1024. Corrección: `LiveView SET_JPEG` (`0x439a3b50`) es decode, no productor.
- VERIFICADO: modo `0x11` en `SetMode` `0x436d6b54` = alias que aplica el modo 5 y devuelve error 2; caso 10 sigue sin acceso demostrado.
- VERIFICADO (grafo directo): la región SFRA no llama a captura Darwin/CAIF/SetMode; entrada YC (`pin`) y llamadas indirectas NO VERIFICADO. Script `scripts/sfra_outcalls.py` + test. Detalle en «Sesión 6» de `docs/capture/electronic-still-low-resolution.md`.
- Siguiente: origen del YC en `pin`/`Sa`, estados que abren el path en Linux, `libInfraPtpControl`, exposición independiente.

## Sesión 2026-10-16 (parte 9) — ruta de foto normal y diseño de integración
- VERIFICADO: cadena de grabación normal = LIRO `Stage_Notify` `0x437efe78` (mensaje tipo 4 id `0x1006`, 0x2a8 B, `MPR::StillInfo` 0x28c B en `+0x14`) → `libObj` `SeqStillCap` (ELF `0xa4b650`) → `ObjStillRecorderCore::RecordStill` (ELF `0x908afc`, único llamador `0x90bbdc`) → `MprCtrl::WriteStill` (`0x8fe0a0`) → `libmpr` `FeaCore::WriteStill` (`0x440794`) → `dcf_Lib::WriteDcfMemory`. `StillInfo.jpg_info` = (memHandle,offset,size) de `mainJpg`, `thumJpg`, `screenNail` + `exifSrcInfo`. Los handles son del dominio DMM de SFRA.
- VERIFICADO: gestor de disparo en LIRO = `RelMgr` (`0x4379d83a`, eventos `0xb..0x1f`); S1/S2 exactos NO VERIFICADOS. Cliente SFRA además registra exif/scn por fotograma (HIPÓTESIS: reutilizables).
- Diseño propuesto y bloqueos: `docs/capture/silent-integration-design.md`. Herramientas nuevas: `scripts/libobj_dec.sh`, `analysis/ghidra/DecompAt.java`, `scripts/elf_thumb_callers.py`, `scripts/elf_string_xrefs.py`, `tests/test_elf_xrefs.py`.
- Siguiente: RelMgr→CaptureManager; tabla de etapas de `Stage_RawPlayInit`; contenido mínimo de StillInfo y registro de índice en `DCFStillWriter`; origen YC de `pin`.

## Sesión 2026-10-16 (parte 10) — coordinación Claude + Codex (ronda 1: A, B, C)
- Registro: `docs/capture/RESEARCH_TASKS.md`; contratos en `docs/capture/tasks/`; logs en `analysis/codex-logs/`. Codex CLI 0.162.1 con `codex exec --skip-git-repo-check --sandbox workspace-write` (el alias por defecto es danger-full-access: no usarlo). Sin repo git.
- A (`docs/capture/mpr-dcf-recording.md`, `analysis/stillinfo-layout.json`): tres ABI (payload LIRO 0x28c; StillInfo Linux 0x6b0 con punteros virtuales; WriteStillParam 0x40); JpgInfo = 11 descriptores de 0x10 B; miniatura obligatoria en EXIF nuevo (no se autogenera); evento de reproducción y EXIF mínimo NO VERIFICADOS.
- B (`docs/capture/sfra-mpr-buffer-bridge.md`): handle SFRA = unidad DMM u16 mapeable por Linux; GET_JPEG saca el buffer del ring (propiedad del cliente) y libera los READY restantes; solo da {handle, size>>7} (sin EXIF/thumb/scn: DESCARTADA la hipótesis previa); compatibilidad con mainJpg NO VERIFICADA.
- C (`docs/capture/shutter-trigger-state-machine.md`): RelMgr empieza en 0x4379d838; 1 y 0x10 son índices (no bits S1/S2); RelMgr emite 0x3011 a CamUser 0x40193; selector inicial de secuencia 0x437eabfc (desde 0x437df338) = divergencia candidata; 0x43841070 NO es el selector.
- Claude (`docs/capture/sfra-linux-client.md`): ISS publica directamente en los buzones SFRA 0x1670464 (SET_PATH) y 0x167046a (GET_JPEG); LiveViewStart limita anchos a 320/640/1024; resolución DMM del handle; propiedad confirmada en 0x439a23d0/0x439a235c.
- Ronda 2 lanzada: D (tabla de etapas), E (playback/EXIF), F (productor YC), C2 (cadena 0x3011).

## Sesión 2026-10-16 (parte 11) — límite de Codex y síntesis
- Codex agotó su límite durante la ronda 2 (D, E, F, C2): sin entregables; copia privada de Ghidra borrada. Trabajo continuado solo por Claude.
- NUEVO: `docs/capture/silent-architecture-comparison.md` (A vs B vs C; A provisionalmente la más prometedora); selector de fila `0x437eabfc` decompilado (`analysis/ghidra/liro-seqselect.json`); la tabla 0x43edccf8 está a cero en la imagen (se rellena en tiempo de ejecución; escritor no localizado).
- INCIDENTE: al detener Codex ejecuté un `kill -9` demasiado amplio (patrón "codex") que mató procesos de la app ChatGPT de escritorio (no relacionada). Reiniciarla si no responde.
- (parte 11b) Tabla 0x43edccf8 resuelta: constructor estático 0x437ebed8 inicializa filas de 20 B con delegados a máquinas de estados `Image*→estado` (fila 8 = captura normal = 0x43b1be36; filas 0..16 listadas en `docs/capture/capture-stage-reuse.md`). Punto de sustitución Silent = una fila nueva con el mismo prototipo. Falta etiquetar los estados (CAIF/SACC/Enc/Notify) de la fila 8.
- (parte 12) E/F/C2 por Claude: ver `docs/capture/{sony-dcf-playback,sfra-electronic-frame-source,shutter-trigger-chain-0x3011}.md`. Hallazgo clave: ya existe una ruta Linux para grabar una imagen externa como foto (ScalarDaemon `recordStillImage` → ObjScalar `SequenceRecordStillImageCmd` (msg 0x1027) → libObj `0x930464` → `MprIf::MakeWriteStillImage`(+`WriteStill`)); SFRA recibe el YC por pines EE/Rec (PinSend 0x439abbfe) con modo `shutter mute thru`; 0x3011 se arbitra por tabla (id,estado) en 0x43ffdd30 (receptor de la cola 0x40193 aún no localizado).

- (sesión 9, P1) `0x930464`=GetFileImage construye JPEG completo EN MEMORIA (no SD): ver docs/capture/record-still-image-route.md. Corrige hipótesis de ruta recordStillImage→WriteStill (DESCARTADA). Pendiente: consumidor de msg 0x3a48 y del registro +0x30..0x3c; miniatura/screennail (quién las crea).

- (sesión 10) GetFileImage 0x930464 = ObjConverter (export/subida, TRANSFERENCIA); 0x3a48 = respuesta genérica; escritura cruda a /dev/ms solo en IsNetworkWriteTestMode. 0x1027 lo atiende ObjStillRecorder ELF 0x919ca0 (+0x128=4) y reutiliza RecordStill::Execute. Ver `docs/capture/record-still-image-route.md` y `analysis/record-image-completion-flow.json`.

- (sesión 11) `0x1027` solo arma ObjStillRecorder (+0x128=4); +0xDC = ObjStillRecorderMediaMgr; Execute registra la imagen en el Pool (InfraStillPool::RegisterImage ELF 0x9328b4, msg 0x2008/0x1000, que usa MakeWriteStillImage) y la lee por 0x6108/0x1009 antes de RecordStill→WriteStill. Candidata C′: registrar en el Pool. Ver `docs/capture/objstillrecorder-mode4.md` y `analysis/objstillrecorder-mode4-flow.json`.

- (sesión 12) CORRECCIÓN: `0x100b` (0xB0 B) = 11 descriptores de 16 B {handle,offset,size,maplen} de las ÁREAS DE SALIDA de `MprIf::EncodeStill` (exifSrcArea, model, software, lensModel, publicMakerNote, pimInfo, secretMakerNote, mpfSrcArea, mainJpg, thumJpg, screenNail). `Execute` (ELF 0x90b248, orden 0x10000005) las reserva vacías (0x90a810), MPR las rellena (0x90ad20→0x8fe6f8) y el Pool las registra. La entrada real es un frame YC (mensaje 0x10000006→0x1017/0x1031/0x1041 = PlayData). `MediaMgr+0x2C` = mediaSelectMode (0 Normal,1 Multi,2 Relay,3 Sort,4 None,5 NormalTmp,6 Record). `0x6108/0x1009` = SetImageWrited, no GetStillInfo. Existe 2ª ruta de escritura: `ObjStillRecorderCore::WriteStill` (orden 0x10000003, ELF 0x909a84). Ver analysis/objstillpool-100b-layout.json y docs/capture/objstillpool-image-producers.md, objstillrecorder-mediamgr.md, pool-write-completion.md.

## Sesión 13 — origen de 0x10000005 y contrato YC de EncodeStill (estático)
Detalle: `docs/capture/{encodestill-command-origin,encodestill-yc-contract,liveview-yc-to-encodestill}.md`, `analysis/encodestill-{command-flow,yc-contract}.json`.
- VERIFICADO: `0x10000005` (MSGID_RECORD_IMAGE_CALL) **no tiene remitente externo**: lo crea ObjStillRecorder en `0x919f1a` al recibir por su pin YC un `PlayData` (`0x1003`), envolviéndolo como `0x10000006`. Lo dispara `MSGID_RECORD_IMAGE_CMD` (cat `0x3500` = CATEID_STILL_RECORDER, id `0x3001`, `0x1005` = modo) enviado por `ModelPbCap` (`0x6137b0`, modo 0), `ModelPaint` (`0x611074`, modo 4) y la consola Mcmd (`0x901504`). Modos 0..6 = Pbcap/Trim/RedEye/Focus/Paint/Art/Beauty.
- VERIFICADO: el recorder pide el YC con `YcPinReqDeliver` (`0x90a668`, `ObjMsg(0x2000,0x1011)` por el pin YC `this+0x60`). El productor del `PlayData` en PbCap NO está identificado.
- Consecuencia: `Execute/EncodeStill` es la ruta de PbCap y edición, no la de captura normal. El «modo 4» de `this+0x128` es Paint, no `MediaMgr None`.
- VERIFICADO: `EncodeStill` recibe `RegionInfo` de 0x40 B (buffers dec/yc con unitType, handle u16, phys, offset, size; fondo; lienzo; región; rango Y; colorimetría). Sin formato/stride/submuestreo. Transporte: `MprIf::EncodeStill 0x71cf58 → FeaIf::EncodeStill 0x44f834 → servicio FEA` (codificador fuera de libObj/libmpr).
- NO VERIFICADO: productor del YC para el pin del recorder, topología ObjHandover `0x2a`, compatibilidad del YC del EE, valores de `unitType`, vida útil del buffer.

## Sesión 14 — topología del pin YC, PlayData y puente Live View → EncodeStill (estático)
Detalle: `docs/capture/{objhandover-2a-topology,objscalar-playdata-bridge,yc-unit-types-and-layout,fea-encodestill-buffer-lifetime}.md`, `analysis/{yc-pin-delivery-flow,topology-table-libobj,dmm-unit-types}.json`; scripts `scripts/dump_topology_table.py`, `scripts/dump_dmm_unit_types.py`.
- DESCARTADO: «ObjHandover 0x2a». `ObjHandover` = categoría `0x3a4c` (NFC/Wi-Fi). `0x2a` es la **fila 0x2a de la tabla del TopologyManager** (libObj `.rodata` ELF `0xcc4210`, 211 filas × 0x20 B): enlace YC `ObjId 9 (ObjEffect) salida nº1 → ObjId 11 (ObjStillRecorder) entrada nº0`, StsId 6. ObjId 11 VERIFICADO por el constructor `0x9178f0`; 9 = Effect por firma de pines (INFERENCIA fuerte).
- VERIFICADO: la lista de topologías de ModelPbCap es `{topología CntMgr, 0x2a}` (`0x6135dc`); RedEye/Trimming/FocusRevision usan `{0xa1,7,5,6,0x2a}`; Live View (BootEE) usa `{0xa,7}`. `0x2a` no aparece en ningún modelo de disparo localizado.
- VERIFICADO: quien responde a `YcPinReqDeliver (0x2000/0x1011)` es el parser de pines YC de **ObjEffect** (`0x1e9880`); el PlayData lo construye ObjEffect en `0x15ebfc` tras **reservar unidades DMM nuevas** (`0x50b3f` 1920×1080 y `0xe0b00`) y ejecutar SDF resize/super-resolución: copia dedicada, no el YC original. Clase de tamaño de la petición: 0→640×360, 1→640×480, 2→1920×1080.
- VERIFICADO: `unitType` = clase de unidad DMM (`kmod/dmm.ko ConfigData`, 374 tipos → extents); las «5 reservas en bytes» de Execute son **tipos de unidad**. Cada YC SDS lleva cabecera de 0x800 B con colorimetría/yRange. Canvas = `align64(w) × align16(h)`.
- VERIFICADO: `FeaIf::EncodeStill` encola y devuelve (asíncrono; fin = `CBID_ENCODE_STILL`); el recorder no retiene la entrada (solo Open/Close); DMM tiene refcount `alloc`/`open`/`rdv` por unidad (`DmmShare`/`allocShare` retienen).
- Nuevo: `MprLib::EncodeStillOnMemory` (mcmd) codifica JPEG desde dirección virtual con ancho/alto explícitos (exige unidad DMM); `ObjScalar` construye un PlayData compatible a partir de handles de cliente pero su `0x1027` solo arma y hace eco (E2 sin sustento).
- NO DEMOSTRADO (ni descartado): YC de Live View → EncodeStill. Bloqueo: el modo interno de ObjEffect en el que su salida nº1 atiende `REQ_DELIVER` con entrada de Camera, y qué modelo de disparo crearía la topología `0x2a`.

## Sesión 15 — investigación en paralelo: principal + Rama A (Claude Sonnet 5, razonamiento medio) + Rama B (Codex `gpt-5.6-terra`, razonamiento medio)
Detalle: `docs/capture/liveview-encodestill-parallel-verdict.md` (veredicto integrado), `analysis/liveview-encodestill-crosscheck.json` (cruce completo), `docs/capture/claude-main-bridge-verification.md` (principal), `docs/capture/branch-claude-objeffect.md` + `analysis/branch-claude-effect-states.json` (Rama A), `docs/capture/branch-codex-camera-yc.md` + `analysis/branch-codex-yc-memory.json` + `analysis/dmm-extent-sizes.json` (Rama B).
- Configuración real: Codex `codex-cli 0.162.1`, modelo `gpt-5.6-terra` con `model_reasoning_effort=medium` confirmados por ejecución (no simulados). Subagente Claude: modelo `sonnet`, esfuerzo `medium`.
- INCIDENTE: la Rama A lanzó un segundo subagente (`general-purpose`) en su primera ejecución, violando el límite de un solo agente Claude; se detuvo con `TaskStop` sin que produjera entregables, y se reinstruyó para que ejecutara ella misma. La segunda ejecución cumplió la restricción.
- VERIFICADO (nuevo, principal): identidad del objeto 8 de la tabla del TopologyManager = **ObjCamera**, antes INFERENCIA fuerte. Constructor real en ELF `0x98c380` (wrapper `ObjCamera_Create` en `0x959bdc`); sus 9 pines (6 YC, STILL_DATA, SOUND, CAMERA_STATUS) son **todos de salida** — Camera no tiene ningún pin de entrada y no puede recibir `YcPinReqDeliver`.
- VERIFICADO (nuevo, principal): Camera y Player compiten por el mismo pin de entrada de Effect (`in#0`, filas `0x0a` y `0x4`); no pueden alimentarlo a la vez. No afecta a la coexistencia con `0x2a` (pin de salida distinto de Effect).
- VERIFICADO (nuevo, Rama A): `EffectInternalMode` **no** es `this+0x14+4` directo (aproximación de sesión 14) sino un holder detrás de `GetSubState(block,1)`; getter/setter genéricos en ELF `0x14011c`/`0x140144`. Escritor localizado: ELF `0x173158`, mapea el campo `0x1025` del mensaje `0x1011` a los modos `{2,3,4,5,7,0xe,0xf,0}` (nunca a 1). Modos con acción real sobre `REQ_DELIVER`: **1, 2, 3, 4, 5**; el resto (incluye 7, 0xe, 0xf) solo registra en log. No se encontró ningún escritor de `EffectInternalMode` activado desde `ModelBootEE` (Live View).
- VERIFICADO (nuevo, Rama B): tamaños reales de los extents DMM — `0x50b3f`(`0xed`)=`0x3fc000` B, `0xe0b00`(`0xe4`)=exactamente `0x800` B (confirma que es solo cabecera SDS, nunca el raster de píxeles), `0x220b2e`(`0x13d`)=`0x96000` B.
- Doble verificación independiente (principal + Rama A, sin coordinación previa en el detalle): mismas filas de topología `0x0a/0x07/0x2a`, mismos `StsId` (0/0/6), misma lectura de `TM::createLifeCycles` (ELF `0x4195c0`) sin hallar guard de exclusión mutua entre grupos de `StsId`.
- **Veredicto sin cambios de fondo**: sigue A > E > E2, con E **ni viable ni descartada**. Los tres bloqueos de sesión 14 persisten: ningún modelo de disparo conocido crea `0x2a`; no se encontró relación entre `EffectInternalMode` y Live View; el `unitType`/formato del YC de Camera sigue sin recuperarse. Siguiente bloqueo: localizar el escritor del modo 1 de Effect y cualquier camino que conecte su salida nº1 con el Recorder mientras su entrada recibe de Camera (no de Player).

## Sesión 16 — activación del grabador y compatibilidad del YC: principal + Rama A (Claude Sonnet 5, medio) + Rama B (Codex `gpt-5.6-terra`, medio)
Detalle: `docs/capture/s16-liveview-recorder-verdict.md` (veredicto integrado), `analysis/s16-liveview-recorder-crosscheck.json` (cruce completo), `docs/capture/s16-main-delivery-sequences.md` (principal), `docs/capture/s16-claude-effect-control.md` + `analysis/s16-claude-topology-audit.json` + `analysis/s16-claude-effect-mode1.json` (Rama A), `docs/capture/s16-codex-camera-yc.md` + `analysis/s16-codex-camera-yc.json` + `docs/capture/s16-codex-fea-completion.md` (Rama B).
- Configuración real: Codex `codex-cli 0.162.1`, `gpt-5.6-terra`, `model_reasoning_effort=medium`, confirmado por llamada de prueba previa (respuesta "OK", 831 tokens) antes del trabajo real. Subagente Claude: `sonnet`, esfuerzo `medium`. **Sin incidente de delegación esta vez** (corrige el de sesión 15; ambos agentes confirmaron explícitamente no haber lanzado subagentes).
- VERIFICADO (nuevo, Rama A, corrige bloqueo de sesión 15): existen **dos escritores dinámicos reales** de `EffectInternalMode=1`, identificados por RTTI mangled-name real leído de `.rodata` (no heurística de rango): `OBJEFFECT::ExecCmdAppFaderEfctEndEvt` (ELF `0x154990`, al terminar un fundido de efecto si un contador no alcanza umbral) y `OBJEFFECT::SequencePinDeliverBase` (ELF `0x1e069c`, al recibir submensaje `0x1017` en pin 0 con modo previo 0). Verificado independientemente por el principal (cadenas RTTI + words de vtabla en `0xfe6050`/`0xfeabd4` coinciden byte a byte). Ninguno de los dos se disparó, en la evidencia revisada, desde `ModelBootEE`/Live View.
- VERIFICADO (nuevo, Rama A): recuento reproducible de **213** sitios reales de `createTopology`/`destroyTopology` (93 create + 120 destroy), corrigiendo la cifra de 318 citada en sesión 15 (discrepancia no resuelta). Único creador literal de la fila `0x2a` sigue siendo `ModelPbCap`; el 82%/97% de los sitios construyen el id dinámicamente, sin poder confirmar ni descartar otro creador.
- VERIFICADO (nuevo, Rama A): segunda fila con `StsId=6` en la tabla de topología (`0xb4`: objeto 53 salida#2 → StillRecorder entrada#0, mismo destino que `0x2a`). Abre la HIPÓTESIS (no verificada) de que el arbitraje real entre fuentes hacia ese pin ocurra en el `StsViewer` compartido (`GetStsViewer` ELF `0x4294cc`), no en ObjEffect ni en TopologyManager. Revisión del gestor de pines de ObjEffect y las 7 funciones hermanas de `0x173158`: sin guard de exclusión Camera/Recorder hallado.
- VERIFICADO (nuevo, principal): segundo manejador gemelo (ELF `0x1f25d8`) confirma de forma independiente la regla `EffectInternalMode==1` + submensaje `0x1011` → `ObjMsg(0x3900,0x600d)`; revela una familia de mensajes hermanos no catalogada (`0x6051`, `0x6052`, `0x6053`). La factoría de secuencias (ELF `0x17b004`) muestra que **solo `0x6013` instancia un objeto de secuencia con estado** (`0xd4` B, ctor `0x1861a8`) — `0x600d` se postea como mensaje plano sin objeto de secuencia, lo que es INFERENCIA de que no transporta imagen (ausencia de llamada DMM/SDF en su despacho).
- VERIFICADO (nuevo, Rama B, verificado independientemente por el principal con desensamblado propio de `libmpr.so`, mismo SHA-256): cadena real `MprIf::EncodeStill → FeaIf::EncodeStill` (ELF `0x44f834`): solo reserva un slot y copia un descriptor `RegionInfo` de `0x40` B (handles/tamaños, no el raster); retorna antes de confirmar lectura; error inmediato (código 9) si no hay slot libre; `DmmClose` no libera (solo decrementa contador `open`). `StillConverter` es candidato (INFERENCIA fuerte, por cadenas reales de callback) a receptor de `CBID_ENCODE_STILL`, sin xref directa confirmada.
- **Veredicto sin cambios de fondo**: sigue A > E > E2, con E **ni viable ni descartada**. El bloqueo "sin escritor de modo 1" de sesión 15 queda corregido (sí existe, pero no conectado a EE); el candidato de arbitraje de exclusión se traslada de ObjEffect al `StsViewer` compartido. Siguiente bloqueo: decompilar `GetStsViewer` (ELF `0x4294cc`) y `ConnectPin` (ELF `0x41c25e`); trazar el llamador indirecto de los dos escritores de modo 1.

## Sesión 17 — control E (ConnectPin/StsViewer), SDF/YC (0x6013), FEA/callback y ruta pública P (CameraSequence): principal + Claude A + Claude B (Sonnet 5, medio solicitado) + Codex C + Codex D (`gpt-5.6-terra`, medio)

Detalle: `docs/capture/s17-parallel-research-verdict.md` (veredicto integrado), `analysis/s17-parallel-crosscheck.json` (cruce completo con las 21 respuestas del informe final), `docs/capture/s17-public-camera-api-crosscheck.md`, `docs/capture/s17-a-e-p-architecture-comparison.md`, `docs/capture/s17-main-s2-integration.md` (principal), `docs/capture/s17-claude-a-topology.md` (Claude A), `docs/capture/s17-claude-b-camerasequence.md` + `analysis/s17-claude-b-api-native-flow.json` (Claude B), `docs/capture/s17-codex-c-sdf-yc.md` + `analysis/s17-codex-c-yc-contract.json` (Codex C), `docs/capture/s17-codex-d-fea-lifetime.md` + `analysis/s17-codex-d-fea-callback.json` + `docs/capture/s17-codex-d-dcf-crosscheck.md` (Codex D).

**INCIDENTE DE PROCESO (declarado, no oculto):** Codex C escribió directamente una sección `## Sesión 17` en este archivo (`CONTEXT.md`) durante su ejecución, violando la restricción explícita del encargo de que solo el Claude principal actualiza documentos centrales durante la integración final. El contenido que añadió (contrato de la factoría `0x17b004`/constructor `0x1761a8`) era técnicamente correcto (reverificado independientemente, ver abajo) y se conserva, fundido en esta sección ampliada, en vez de descartarse — pero el acto de editar este archivo no estaba autorizado para esa rama. Ningún agente delegó a un tercero ni lanzó subagentes anidados (confirmado explícitamente por las 4 ramas); el límite de 2 Claude + 2 Codex se respetó.

- Configuración real: Codex C y Codex D = `codex-cli 0.162.1`, `gpt-5.6-terra`, `model_reasoning_effort=medium`, confirmado por llamada de prueba previa. Claude A = `sonnet`, esfuerzo no declarado explícitamente por el propio agente. Claude B = `sonnet`, reportó explícitamente esfuerzo **bajo**, no el `medium` solicitado — discrepancia declarada aquí, no corregida en silencio.
- VERIFICADO (Claude A, re-verificado por el principal con `llvm-objdump` directo): `ConnectPin`/`ObjPin::Connect`/`ObjStatusViewer` **no están en `libObj.so`**, son símbolos importados de `libMWF.so` (`ObjIf::ConnectPin` ELF `0x2450c`, `ObjPin::Connect` ELF `0x29588`, confirmados en la tabla dinámica real). `ObjPin::Connect` **no comprueba si el pin de destino ya está conectado** antes de sobrescribir su puntero — solo rechaza por pin nulo/igual, `kind` incompatible o dirección incompatible; el `ObjStatusViewer` no participa en ninguna rama de esa decisión. `GetStsViewer` (ELF libObj `0x4184cc`, no `0x4294cc` como citaba el encargo — corrección de direccionamiento Ghidra-VA/ELF documentada por Claude A) es un *get-or-create* por `sts_id`: confirma que `0x2a`/`0xb4` comparten el mismo `ObjStatusViewer*`, pero este es un agregador de notificación, no un cerrojo de arbitraje. Cierra el bloqueo técnico de sesión 16; **debilita** la hipótesis de arbitraje activo del `StsViewer` compartido.
- VERIFICADO (principal, nuevo): decompilado completo del selector LIRO `0x437eabfc` (árbol de decisión de 4 niveles sobre campos `+0x4b70/+0x54a5/+0x54a8/+0x70/+0x1d8/+0x1e0` de la petición de captura), sin ninguna marca de modo Silent/EFCS; su tabla de filas (`0x43edccf8`) es BSS/cero en la imagen estática del binario (explica, no solo asume, la no recuperabilidad estática del contenido real de las filas). Localizados por desensamblado directo (Ghidra en modo sin análisis no los veía) dos callers reales de `0x43809ed8` (instalador del callback `CaptureStart`): ninguno referencia literalmente `0x3011` ni `0x40193` — reduce sin cerrar el bloqueo del consumidor de la cola de sesión 16.
- VERIFICADO (Codex C, re-verificado por el principal con desensamblado directo): la factoría ELF `0x17b004` asigna `0xd4` B y llama al constructor en **ELF `0x1761a8`** (no `0x1861a8`, que es la dirección Ghidra VA — corrección de direccionamiento). El constructor instala vptr `0x0db3cc`. El `BeginExecCommand` candidato (`0x15fd50`, INFERENCIA fuerte por layout/cadenas) exige holder `this+0x14`, interfaz `this+0x8` y retorno no-cero del selector virtual 12, **sin comprobar `unitType`** en ninguna de sus tres guardas. Reconstruida la geometría (selector virtual 3, clases 640×360/640×480/1920×1080) y el contrato de `PlayData` (`0x15ebfc`, condicionado a resultado `0x111`). PbCap reserva raster/SDS DMM propios y publica PlayData tras SDF; NO VERIFICADO: `unitType`/descriptores del YC real de Camera o que éste satisfaga el contrato.
- VERIFICADO (Codex D, re-verificado por el principal con `nm -D` directo): API real de registro de callback FEA (`MprIf::SetCallbackFunc` `libmpr.so:0x71f7b8`, `FeaIf::MprIfCallbackPoint` `0x4502e8`) y rango de IDs de callback `0xc0000001..0xc0000091`, con `0xc0000004` como candidato (INFERENCIA fuerte, no confirmado) a `CBID_ENCODE_STILL`. Ningún liberador real de las unidades DMM originales ni de la copia SDF fue localizado tras `EncodeStill`; `DmmClose` sigue sin liberar (solo decrementa contador).
- VERIFICADO (Claude B, nuevo — primera vez que se verifica localmente, no solo se cita GitHub): `CameraSequence`/`CameraEx`/`DeviceBuffer` son reales en el firmware A6000 local (`libcameraex_jni.so`, `libcameraex_client.so`, re-verificados por el principal con `find`/`nm -D`), con backend Binder estándar de Android y enlace concreto a `libScalarDaemon.so` (`SystemEventIssuerCameraSequence`, `CommandProcessorFactoryCameraEx/CameraSequence`, re-verificados). Lectura directa del código real de PMCADemo: `onShutterKeyDown()` usa `takePicture()` convencional, **no** `CameraSequence` — sin enlace al botón físico S2 en ningún código real revisado.
- **Veredicto: A > E > P ≈ E2.** Sin cambio de orden de fondo. El bloqueo de control de E (arbitraje StsViewer) queda debilitado/cerrado (no hay arbitraje activo); se añade arquitectura P (CameraSequence) como referencia pública mejor documentada que E para "¿existe una API accesible de JPEG electrónico?", pero sin ningún enlace a S2 — no reemplaza a E ni a A. Siguiente bloqueo: decompilar `LifeCycle::ctor`/`Activate` (sitio real que invoca `ObjPin::Connect`); resolver el llamador vía vtabla de `0x43809ed8` más allá de los dos callers directos encontrados; productor real del YC de Camera hasta un descriptor concreto; receptor real de `CBID_ENCODE_STILL`.

## Sesión 18 — inventario de fuentes oficiales Sony OSS, inicializador LIRO 0x437EBED8 y ocho ramas (4 Claude Sonnet 5 + 4 Codex `gpt-5.6-terra`, medio solicitado)

Detalle: `docs/capture/s18-parallel-research-verdict.md` (veredicto integrado), `analysis/session18/main/s18-parallel-crosscheck.json` (cruce completo), `analysis/session18/main/sony-oss-inventory.md`/`.json` (inventario de fuentes Sony), `docs/capture/s18-main-init-437ebed8.md` (principal), `docs/capture/s18-claude-a-lifecycle.md` (Claude A), `docs/capture/s18-claude-b-camerasequence.md` (Claude B), `docs/capture/s18-claude-c-relmgr.md` (Claude C), `docs/capture/s18-claude-d-topology.md` (Claude D), `docs/capture/s18-codex-e-yc-buffers.md` (Codex E), `docs/capture/s18-codex-f-sdf-yc.md` (Codex F), `docs/capture/s18-codex-g-fea-dmm.md` + `analysis/session18/codex-g/sony-oss-memory-crosscheck.md` (Codex G), `docs/capture/s18-codex-h-mpr-dcf.md` (Codex H).

**Novedad del encargo**: el usuario añadió a la raíz del proyecto 6 paquetes reales de fuentes OSS de Sony (`linux-kernel.tar.gz` y 5 más), con instrucción expresa de inventariarlos antes de lanzar las 8 ramas. El principal hizo el inventario inicial, calculó SHA-256 de los 6 paquetes, y determinó que el kernel es Linux 3.0.27 con SoCs propios Sony (`arch/arm/mach-cxd90014`, `mach-cxd4132`) arrancando Android — ninguno de los 6 paquetes contiene código propietario de cámara (confirmado independientemente, sin contradicción, por el principal, Codex G y Codex H).

**Incidente de corrección (declarado, no oculto)**: la primera lectura del inventario del principal infirió, por nombre de archivo, que `sdc.c`/`sdc-zqcal*.c` de `mach-cxd4132` eran un controlador de tarjeta SD. **Codex G y Codex H, independientemente, refutaron esto con lectura directa del código**: son calibración de impedancia ZQ de memoria **LPDDR** (RAM del SoC), ajenos tanto a SD como a DCF. Corregido en `sony-oss-inventory.md`/`.json` tras verificación propia del principal sobre `regs-dmc.h` (registros `SDC_COMMAND1/2` documentados explícitamente "for LPDDR1"/"for LPDDR2").

- Configuración real: Claude A, C, D = `sonnet`, esfuerzo `medium` confirmado (C y D explícitamente; A no puede verificar el valor numérico desde dentro de su propio contexto, limitación declarada, no discrepancia). **Claude B repite el patrón de sesión 17**: esfuerzo `bajo` autoinformado en vez de `medium`, con intento fallido de autocorrección (`set_session_effort` bloqueado por la herramienta para una sesión que se autoevalúa). Codex E-H: binario real `/home/nicolas/.local/bin/codex` con `-c model="gpt-5.6-terra" -c model_reasoning_effort="medium"` confirmados en los flags de lanzamiento; los 4 agentes declaran que el nivel de esfuerzo numérico "no está expuesto" desde dentro de su propio proceso (misma limitación de visibilidad que Claude A). Ningún agente lanzó subagentes propios; límite de 2+2+2+2 respetado.
- VERIFICADO (principal, nuevo): base de carga real de LIRO confirmada en `0x43541000` (corrige un desliz de transcripción del resumen de sesión 17 que citaba `0x43540000` — no era un error de los scripts del proyecto, que ya usaban la base correcta). Inicializador maestro `0x437EBED8`: construye objetos de 0x14 B (patrón vptr+estado+payload) sobre al menos 9 tablas globales de LIRO, **incluida la tabla del selector de captura** (`GOT 0x44022934 -> 0x43edccf8`, antes creída BSS irrecuperable en sesión 17) — resuelve sus 15 filas a funciones reales vía punteros GOT estáticos legibles. Técnica reutilizada por Claude A/C/D sobre la misma tabla y sobre `libObj.so` (con resultado DESCARTADO en este último caso, ver abajo). Único hallazgo de cadena "Silent" en LIRO es de sincronización de audio (`ENCAUDSYNC`), no del obturador — DESCARTADO como pista.
- VERIFICADO (Claude A, re-verificado por el principal leyendo `GOT[0x44020894]` directamente del binario): el blocker de sesión 15-17 "¿quién llama a `ObjPin::Connect` desde un LifeCycle construido?" se **reduce** (no se cierra) a exactamente 5 bibliotecas que importan ese símbolo vía `R_ARM_JUMP_SLOT`: `libBizFw.so`, `libBizFw2.so`, `libInfraCacheMgr.so`, `libInfraScalarMpr.so`, `libmprctrl.so` — **`libObj.so` queda descartado** como importador directo (solo importa wrappers). Ningún `bl`/`blx` directo ni relocación `R_ARM_ABS32` localizada hacia esos stubs en ninguna de las 6 bibliotecas examinadas — la llamada real es indirecta vía registro, no resoluble por desensamblado estático simple. Además, confirmado con evidencia dura (vtabla Itanium real de 3 slots en `.rodata 0xcc6698`) que el `LifeCycle` real de `libObj.so` (construido en `0x41b6c0` desde `TM::createLifeCycles`) y el trampolín único de LIRO (`DAT_44020894`→`0x43afb3bb`, sin vtabla) son **mecanismos de clase completamente distintos, sin puente verificado entre ambos**.
- VERIFICADO (Claude A y Claude C, convergencia cruzada independiente): las 4 filas dinámicamente seleccionables del selector LIRO (offsets reales `0xa0,0xc8,0xdc,0x104`, corrigiendo con precisión el cálculo `iVar7*0x14` citado de memoria en el resumen de sesión 17) son variantes casi idénticas entre sí y a la fila `0xb4` ya conocida — mismo manejador genérico de reintento/cancelación/RAW/EXIF, **sin ninguna marca de modo Silent/EFCS**. Nota metodológica de Claude C, reutilizable: los punteros GOT de esta tabla tienen el bit 0 (Thumb) activado; hay que restar 1 antes de pasarlos a Ghidra o se produce `ContextChangeException`.
- VERIFICADO (Claude C, nuevo): `0x43807f4c` es el llamador real de `0x43807d80` (dispatcher denso de dominio local `0x100..0x207`, invocado solo indirectamente — cero `bl` directos en todo el binario). **El puente entre ese dominio y el dominio `0x3011/0x3013/0x3015`/cola `0x40193` sigue sin probarse** — el blocker del consumidor de sesión 16-17 se reduce en alcance (ahora sabemos qué hay un nivel más abajo) pero no se cierra. Kernel Sony (`cxd90014`/`cxd4132`): solo GPIO genérico sin `request_irq`, sin evidencia de IRQ de teclado específico de S2.
- VERIFICADO (Claude D, re-confirmado por método independiente — `llvm-objdump` crudo, no Ghidra): sin llamador común entre `TM::createLifeCycles` y `ObjPin::Connect` (reconfirma sesión 17). Aclarado: la técnica "inicializador GOT→BSS" de LIRO **no tiene equivalente literal en `libObj.so`** — la tabla de topología (`.rodata 0xcc4210`, 211 filas, stride `0x20`) ya es estática y legible sin inicializador; el problema real para identificar "objeto 53" (fila `0xb4`) es un *lookup* dinámico en runtime (`0x41920c`, que solo entrega un proxy genérico si el objeto no está ya registrado), no una tabla de constructores por ObjId. Re-derivadas por segundo método (lectura cruda de `.rodata`) las filas `0x2a`/`0xb4`, coincidentes byte a byte con lo ya documentado arriba (sesión 16, línea 907).
- VERIFICADO (Codex E/F, sobre binarios propietarios): confirmada superficie real de memoria YC en `libObj.so` (`AvbbcPhycMem`, `DmmCh::*`, `DmmAccessPLA::*`, metadatos `C_DataflowInfra_StdData_YC`); contrato YC/SDS más preciso vía `YcSdsAcsr` (raster `0x50b3f` + SDS `0xe0b00`, bloque de control de `0x800` B, no píxeles). El acelerador `cmpr.c` del kernel Sony es LZPART genérico — DESCARTADO como evidencia del formato YC/JPEG real; sin enlace estático entre el kernel OSS y la superficie propietaria YC/DMM.
- VERIFICADO (Codex G, sobre kernel OSS): `ashmem` es el único mecanismo de memoria compartida presente en este Linux 3.0.27 (ION/DMA-BUF no existen en esta versión) — DESCARTADO cualquier `dmm.ko`/interfaz DMM Sony literal (coincide con la búsqueda independiente ya hecha por el principal en el inventario). Hallazgo abierto sin forzar conclusión: dispositivos UDIF `ldec`/`mia` con IRQ/canal DMAC registrados en `mach-cxd4132/udif/platform.c`, sin controlador fuente ni semántica documentada — **NO VERIFICADO** si tienen relación con imagen.
- VERIFICADO (Codex H, sobre kernel OSS + `libmpr.so`): confirma FAT/VFAT real y habilitado en los defconfigs Android CXD90014, con `fsync`/`fdatasync` disponibles en el VFS; `libmpr.so` tiene cadenas DCF/DCIM reales (`RegisterDCFContent`, `GetDCFContentAttribute`, patrón `DSC0%04ld.JPG`) pero la secuencia semántica completa de escritura/catálogo sigue sin reconstruirse por desensamblado — la lógica DCF es propietaria de MPR, no del kernel GPL.
- **Qué aportaron los archivos Sony OSS al proyecto (sección obligatoria del encargo)**: confirmaciones de plataforma (kernel real 3.0.27 con SoCs CXD propios, `ashmem` como mecanismo de memoria compartida, FAT/VFAT real, PL310 específico de CXD4132); **ningún cambio de conclusión sobre S2/el obturador**; una corrección real pero de alcance menor (sdc.c es LPDDR, no SD, un detalle del inventario propio, no de sesión 17); y confirmación por ausencia (tres ramas independientes, sin contradicción) de que DMM/FEA/MPR/RelMgr/CaptureManager/ObjCamera/ObjEffect/ObjStillRecorder/CameraSequence/ScalarDaemon/SDCom y cualquier driver de sensor/ISP/JPEG reconocible **no están en este código GPL/BSD** — es exclusivamente la base de plataforma, nunca la pieza propietaria de cámara.
- **Veredicto: A > E > P ≈ E2, sin cambios respecto a sesión 17.** Los avances de esta sesión son de caracterización (más detalle sobre mecanismos internos) y de corrección (SDCom≠Binder confirmado por Claude B, sdc.c≠SD confirmado por Codex G/H), no de viabilidad. Siguiente bloqueo, ahora mejor delimitado: (1) cerrar el bloqueo de `Connect()` dentro de las 5 bibliotecas identificadas por Claude A vía análisis de flujo de datos; (2) probar o refutar el puente entre el dominio `0x100..0x207` (Claude C) y el dominio `0x3011/0x40193` — es el blocker más concreto de toda la investigación hasta ahora; (3) decompilar las 10 filas restantes de la tabla de 15 de LIRO; (4) identificar la clase real de ObjId 53 por el mecanismo de auto-registro, no por tabla de constructores.

## Sesión 19, ejecución 01 — S19-01 (puente S2 de dominios)

- VERIFICADO: `0x43807f4c` está registrado indirectamente en `0x43fcd5d0` como puntero Thumb `0x43807f4d`; el caso local `0x100` llama `0x43807d80`, que posee rutas a `0x43809ed8` (instalador de CaptureStart). La inscripción en tabla no prueba ejecución.
- NO_VERIFICADO: receptor/registro de la cola CamUser `0x40193` y la conversión de ObjMsg `0x3011/0x3013/0x3015` al dominio local `0x100..0x207`. Tampoco hay prueba de cancelación/liberación cruzada ni de evento físico S1/S2 exacto. No declarar SilentShutter funcional. Detalle: `docs/capture/s19-s2-domain-bridge.md` y `analysis/session19/evidence/s2-domain-bridge.json`.

## Sesion 19, ejecucion 02 — S19-02 (LifeCycle y Connect)

- PARCIAL: `libBizFw2.so:0x2bf1c` prueba que `AVBIZ::UNIVERSE::UObjPin::Connect` delega a `MWF::ObjPin::Connect@plt` con `this+8`, destino y `ObjStatusViewer`; el cuarto argumento sólo controla trazas. Los tres `ConnectPinWrapper` de infraestructura invocan el mismo MWF Connect salvo cuando su flag local difiere la operación. MWF `0x29588` valida nulo/igual, tipo y dirección, pero no rechaza un destino ya conectado.
- VERIFICADO: `TM::createLifeCycles` (`libObj.so:0x4195c0`) construye en `0x41b6c0`, registra el objeto y la vtable Itanium de tres slots tiene address point `0xcc6698`. NO_VERIFICADO: una arista de ejecución desde ese LifeCycle (o su despacho posterior `0x416faa→0x41b728`) hasta Connect. Una vtable o un callback estático no prueba ejecución. Detalle: `docs/capture/s19-lifecycle-connect.md` y `analysis/session19/evidence/lifecycle-connect.json`. SilentShutter sigue sin declararse funcional.

## Sesion 19, ejecucion 03 — S19-03 (ObjId 53)

- PARCIAL: la fila `0xb4` (`[0,6,0x35,1,2,0xb,0,0]`) queda correlacionada con la clase real `ObjStillRecorder`: `ObjStillRecorder_Create` reserva `0x148` y llama al constructor `0x9178f0`, que inicializa `ObjActiveBase(0x2f)` y crea pines/wrappers. La asociación exacta `ObjId 53 → constructor` sigue sin recuperarse.
- Se inspeccionaron los 263 inicializadores de `.init_array` y las secciones de datos asignables: no hay entrada init ni puntero directo a `ObjStillRecorder_*`, ni se localizó inscripción explícita `0x35→ObjStillRecorder_Create`. Eso no descarta un registro indirecto o externo. `0x41920c` sigue siendo sólo lookup/placeholder de `0x30` B, no factoría por ObjId. Ver `s19-objid53-registration.md`; siguiente: S19-04.

## Sesion 19, ejecucion 04 — S19-04 (contrato YC real de ObjCamera)

- PARCIAL: `ObjCamera_Create` (`0x959bdc`) reserva `0x20c` y llama al constructor `0x98c380`; éste inicializa estado/locks/hilo y sus auxiliares construyen nueve pines de salida (`0x987dc6`, `this+0x58..0x78`). No llama a `DmmCh`, `DmmAccessPLA` ni `AvbbcPhycMem`. La topología `0x0a` confirma Camera.out0→Effect.in0, pero no el descriptor del mensaje.
- VERIFICADO: la ruta DMM concreta `ObjEffect`/PbCap (`0x15fa74`) crea `DmmCh(0x35)` y dos `allocNew`; el par conocido es raster `0x50b3f`/extent `0xed`/`0x3fc000` y cabecera SDS `0xe0b00`/extent `0xe4`/`0x800`. La cabecera SDS no es raster.
- NO_VERIFICADO: unitType, handle/offset DMM, memoria física/DMA, geometría, formato, stride, planos, colorimetría, ownership y reciclaje del YC de Camera. Se DESCARTA inferirlos desde registros IMX210; no hay arista estática Camera.out0→descriptor DMM. SilentShutter no se declara funcional. Detalle: `docs/capture/s19-camera-yc-real-contract.md` y `analysis/session19/evidence/camera-yc-contract.json`; siguiente: S19-05.

## Sesion 19, ejecucion 05 — S19-05 (ObjEffect, SDF y Camera)

- PARCIAL: la factory `0x6013` crea la secuencia de `0xd4` B con constructor `0x1761a8`; su `BeginExecCommand` candidato `0x15fd50` exige holder, interfaz y selector virtual 12, conecta infraestructura, reserva el par DMM propio y publica PlayData solo tras `0x111`. La limpieza desconecta/cierra las salidas de la secuencia.
- NO_VERIFICADO: una arista `Camera.out0 → holder/pines Dataflow → operación SDF`, el contrato DMM/geométrico/formato del YC Camera y su ownership extremo a extremo. La ausencia de chequeo `unitType` dentro de `0x15fd50` no prueba compatibilidad. La SDS `0xe0b00` sigue siendo metadato, no raster. Ver `docs/capture/s19-camera-effect-sdf.md`; siguiente: S19-06. SilentShutter no se declara funcional.

## Sesion 19, ejecucion 06 — S19-06 (callback EncodeStill)

- PARCIAL: `MprCtrl::Init` registra el callback global MPR (`libmprctrl.so:0x11b96..0x11ba2`); `FeaIf::MprIfCallbackPoint` invoca ese callback y luego notifica IDs en `0xc0000001..0xc0000091`. `EventSwitcher` distribuye después por `targetId`/`eventId`. Esto verifica el conducto genérico, no el receptor de still.
- INFERENCIA fuerte: `0xc0000004` es `CBID_ENCODE_STILL` y `StillConverter` su consumidor, por literal/cadenas. NO VERIFICADO: la entrada concreta de `AddCallbackFunc`, objeto receptor, última lectura de píxeles, cancelación y liberación de fuente/copia. `EncodeStill` sólo copia `RegionInfo` de `0x40` B y encola; retorno 0 no es JPEG terminado ni lectura completada. Ver `docs/capture/s19-fea-encodestill-completion.md`; siguiente: S19-07. SilentShutter no se declara funcional.

## Sesion 19, ejecucion 07 — S19-07 (tabla LIRO, entradas restantes)

- VERIFICADO: el pendiente real de la tabla del inicializador `0x437ebed8` eran las diez filas no seleccionables (`0x00,0x14,0x28,0x3c,0x50,0x64,0x78,0x8c,0xf0,0x118`); las cuatro dinámicas y `0xb4` ya estaban analizadas. En la vista ELF, sus direcciones Thumb sin bit 0 son funciones completas con selector `FUN_43afdf16`/`tbb`, no stubs vacíos.
- INFERENCIA: forman variantes de la ruta de captura convencional con precondiciones, retries/cancelación y una cola común de metadatos `0x9400`; no se recuperó operación que por sí sola identifique adquisición física, encoder JPEG, finalización ni ownership de buffer. Sin condición Silent/EFCS identificada. Detalle: `docs/capture/s19-liro-remaining-sequences.md`.

## Sesion 19, ejecucion 08 — S19-08 (MPR/DCF y reproduccion)

- PARCIAL: `FeaIf::WriteStill` (`libmpr.so:0x44f784`) admite 1–2 registros y los entrega asincrónicamente; la ruta interna valida estado/writer/identificador de grabación. `MprFileIfCore::WriteAndFlush` (`0x726138`) delega al gestor de medio y existen APIs DCF de pre-registro/lookup (`0x71eafc`/`0x71eb70`) y APIs de reproducción/miniaturas. Esto prueba cuatro capacidades separadas, no una cadena completa.
- NO VERIFICADO: JPEG válido extremo a extremo, escritura en SD de este still, commit/rollback de registro DCF, confirmación durable (`fsync`/`fdatasync`), cancelación/limpieza ni publicación al catálogo/reproducción desde `ObjMsg 0x3500/0x3002`. Un JPEG, retorno de `EncodeStill` o cadena `DSC0%04ld.JPG` no implican las otras tres condiciones. No declarar SilentShutter funcional. Detalle: `docs/capture/s19-dcf-playback-completion.md` y `analysis/session19/evidence/dcf-playback-completion.json`; siguiente: S19-09.

## Sesion 19, ejecucion 09 — S19-09 (CameraSequence / SDCom)

- PARCIAL: se verificó la frontera `CameraSequenceDiadem → CameraSeqUtil → SDCom → CommandProcessorCamseq* → SystemEventIssuerCameraSequence`, no Binder. `getPreviewSequenceFrames` envía SDCom `0x127`; la respuesta crea `DeviceMemoryDiadem` con tickets y `readBuffer` mapea memoria compartida, copia bytes y desmonta. `release()` devuelve el ticket mediante SDCom `0x3`/parámetro 4.
- NO VERIFICADO: que el preview sea JPEG 640×480 (localmente sólo queda el default 640 y opciones configurables), formato/YC, productor físico/JPEG, ownership completo, S2/Silent/EFCS o MPR/DCF. Un DeviceMemory no acredita JPEG ni SilentShutter. Detalle: `docs/capture/s19-camerasequence-sdcom.md` y `analysis/session19/evidence/camerasequence-sdcom.json`; siguiente: S19-10 (entrega del YC de SFRA al cliente Linux).

## Sesion 19, ejecucion 10 — S19-10

- PARCIAL: SFRA es un nombre real de `av-cam.bin` (`ScalarInfraAsyncMain.cpp`, `GET_JPEG`, `SET_PATH`, `SfrJpegBuffer.h`). Su entrada YC usa pines internos EE/Rec, pero la salida Linux demostrada es JPEG READY en DMM: ISS pide `0x2009/0x100`, recibe `{handle:u16, blocks128:u16}`, abre `/dev/mem`, resuelve el extent y aplica `mmap` RW/shared. `MmapLiveViewJpeg` devuelve base+delta y libera la unidad anterior.
- NO VERIFICADO: entrega YC/raw Linux, formato/longitud exacta/validez JPEG, geometría YC, coherencia de caché, relación SFRA↔CameraSequence/SDCom↔ObjCamera, ownership/refcount terminal y enlaces S2/EFCS/MPR/DCF. No aparece `ashmem` en las bibliotecas examinadas: no llamar ashmem a este mapa `/dev/mem`. SilentShutter no se declara funcional. Detalle: `docs/capture/s19-sfra-yc-linux-delivery.md`; siguiente S19-11 (b), modos 2–5 de ObjEffect con entrada Camera.

## Sesion 19, ejecucion 11 — S19-11

- PARCIAL: el valor efectivo de modo de la secuencia ObjEffect se obtiene dinámicamente y el despacho `0x176cc6` acepta exactamente `2..5`. Sólo modo 3 supera su segundo filtro y crea `ObjMsg(0x3900,0x0002)`; 2, 4 y 5 retornan por error **en este dispatcher/recorrido concreto** (`0x176294`); no se verificó que sean inválidos en otras rutas o dispatchers de ObjEffect no examinados (corrección sesión 20, C3). No asigna DMM PbCap ni llama al publicador `0x15ebfc`; `0x3900/0x0002` no es el `0x3900/0x3000` de la ruta SDF PbCap conocida.
- NO VERIFICADO: que Camera.out0 ejecute esta secuencia, el significado nominal del enum, un buffer apto para EncodeStill/PbCap y cualquier condición que evite obturación mecánica. Siguiente S19-12 (h): condiciones que seleccionan u omiten la captura mecánica, separadas de la compatibilidad de buffers. SilentShutter no se declara funcional.

## Sesion 19, ejecucion 12 — S19-12

- PARCIAL: se verificaron puertas reales antes de la captura convencional: admisión de RelMgr `0x4379e6a8`, guardas del dispatcher local `0x43807d80`, clase de captura en `0x437df640` y selección/ejecución de descriptor `0x437eabfc → 0x43b04730`. Ninguna es una condición demostrada de «cortina mecánica frente a electrónica total».
- NO VERIFICADO: el puente `0x3011/0x40193→0x100`, la semántica de las guardas locales y, sobre todo, la fila exacta de `0x43edccf8` que llega a CAIF/Darwin. EFCS (`+0x41c`) sigue siendo selección de exposición, no prueba de omisión de ambas cortinas. Ver `docs/capture/s19-mechanical-shutter-decision-points.md`; siguiente S19-13 (d), cancelaciones y estados posteriores a S2. SilentShutter no se declara funcional.

## Sesion 19, ejecucion 13 — S19-13

- PARCIAL: RelMgr emite `0x3015`; el dispatcher local posee salidas de limpieza/notificación, y las etapas LIRO retornan `0/1/2/5` y limpian condicionalmente `ctx+0x754` mediante `0x437fbad8` antes de ponerla a cero. No se demostró que esos mecanismos estén conectados entre sí.
- NO_VERIFICADO: transición a idle, cancelación de una captura ya comprometida, liberación de buffers DMM y ventana segura antes de CAIF/Darwin. `DmmClose` no es liberación de asignación. Ver `docs/capture/s19-post-s2-cancellation-states.md`; siguiente S19-14 (f), `Stage_RawPlayInit` y reutilización de etapas. SilentShutter no se declara funcional.

## Sesion 20 — investigación directa de Claude (sin Codex, sin subagentes)

- COMPLETADO: tres correcciones documentales de sesión 19. (C1) ObjId 53 es el objeto ORIGEN de la fila de topología `0xb4`; la clase `ObjStillRecorder` corresponde al objeto DESTINO (ObjId 11/0x0b), no a 53. (C2) La tabla `0x43edccf8` SÍ es reconstruible estáticamente vía su inicializador `0x437ebed8` + resolución GOT (ya demostrado en sesión 18); la negación de S19-12 quedó retirada. (C3) Los modos 2/4/5 de ObjEffect inválidos solo en el dispatcher `0x176294`/filtro `0x176cc6` examinado por S19-11, no en todo ObjEffect. Detalle: `docs/capture/s20-s19-corrections.md`.
- PARCIAL, cadena principal CERRADA (S19-14 retomada): `Stage_RawPlayInit`/`ycc_rawplay`/`sds_ycc_handle` (`0x43cad51b`/`0x43cad4dc`/`0x43cad508`) tienen 0 referencias Ghidra registradas — no confirma ni descarta uso. Se decompiló realmente el clúster vecino `Stage_DevLater` (`0x437edaf8`), `Stage_Notify` (`0x437ef8cc`/`0x43b1ad32`/`0x43b1bb4c`), `Stage_Apollo` y `Stage_Orientation` (nombres no documentados antes), que comparte contexto (`ctx+0x4ad0/+0x4ad4/+0x4b54..0x4fe0`) con las filas LIRO ya conocidas. **VERIFICADO (cadena cerrada)**: `0x43afe192 → FUN_437edd44 → FUN_437edd1c → FUN_437edd04 → FUN_43561604 → Stage_DevLater`; `FUN_437edd44` abre y parsea un `.ARW` real desde la tarjeta SD (ruta `DCIM/100MSDCF/DSC%05d.ARW`, tags TIFF `0x111`/`0x117`), no un buffer YC de Live View. **Responde negativamente, para esta ruta, la pregunta central de S19-14**: RawPlay/DevLater revela un `.ARW` ya existente (escrito por una captura previa), no permite generar una foto nueva sin adquisición de sensor. Conexión nueva con la unidad SDS `0xe0b00` (S19-05) vía ruta SPICA/TAP; familia de unit-types raster `0x50b0b`/`0x50b2e` distinta de `0x50b3f`. Detalle: `docs/capture/s20-rawplay-stage-reuse.md`.
- COMPLETADO (S20-ROW78): `FUN_43ae75dc` es un getter trivial (`*param_1`). Los 6 llamadores reales de `FUN_43afe9f4` son las filas LIRO `0x50/0x64/0x78/~0xf0/~0x118`, confirmando y extendiendo el mapa de S19-07. **VERIFICADO**: la fila `0x78` (`FUN_43b1bdb4`), en su caso 0 (rama no-cancelación), llama al selector real de sensor `0x437f7ff0` (ya confirmado en este documento) — esta fila **no** es independiente del sensor. Esa misma rama espera sobre `ctx+0x4b70` con un log nuevo "RawDevInit_WAIT_IMG_PARAM"; `ctx+0x4b70` es el mismo campo que Stage_DevLater escribe desde `ctx2+0x27e4` — enlace real y nuevo entre la cadena RawPlay ya cerrada y la máquina de estados principal de captura. Se confirma (no contradice) que el rango `0x437f22d4..0x437f245c` de S19-13 es una etapa compartida a la que también despacha la fila `0x78`; se documenta por primera vez su rama no-cancelación. Nueva cadena `Stage_Raw.cpp` en filas `0x50/0x64/0x78`. Detalle: `docs/capture/s20-row78-sensor-selector-link.md`. **Extensión (S20-ROW78-EXT)**: `FUN_43afe11a` (hermano de `43afe9f4`) caso 0 rellena `ctx+0x4afa/4ec0/4efa/4efc/4efe/4f00` desde `FUN_4379a320()` — los mismos campos que lee Stage_Apollo, confirmando que es su preparación de dimensiones, no una ruta aparte. Cadena nueva sin clasificar: `GOLFSHOT_FREE_ERR.../SSP_IMAG...`. Se detectó que el mecanismo de guardar/recuperar descriptor tiene **al menos dos instancias paralelas** sobre el mismo objeto `ctx+0x4ad0`: una en `ctx+0x4b54/58/5c` (437ef8cc) y otra en `ctx+0x6e4/8/c` (43afe11a caso 6/7). **Bloqueo de herramienta (S20-P3-ATTEMPT)**: intentar P3 (contrato YC de `ObjCamera.out0`, en `libObj.so`) vía `scripts/libobj_dec.sh`/Ghidra produjo pseudocódigo inconsistente (patrón de handler de excepciones C++, no el constructor real ya verificado por S19-04 con `llvm-objdump`); la decompilación Ghidra de esta clase en el proyecto `a6000-libs` no es fiable con la configuración actual — P3 requiere retomarse con `llvm-objdump` directo, como hizo S19-04/05, no con Ghidra. **S20-P3-RETRY**: reintentado con `llvm-objdump` directo (sin Ghidra). VERIFICADO: `MWF::ObjPin::Send` tiene 464 sitios de llamada en `libObj.so`; ninguno cae dentro del código de construcción ya verificado de `ObjCamera` (ctor `0x98c380` + auxiliares `0x987788/0x987d6c/0x987dc6/0x9880a4`) — hallazgo negativo real, más fuerte que S19-04. Un sitio en `0x98f974` (atribución débil por proximidad de símbolo, NO VERIFICADO que pertenezca a `ObjCamera`) muestra un patrón `GetCategoryId(msg entrante) → SetCateIdMsgId(0x100e/0x100f) → AddParam(0x1011) → GetPin(ctx,6)->Send(0x1003,...)`; si fuera de `ObjCamera` sería el pin 6, no `out0` (pin 0), por lo que no cerraría el contrato aun en el mejor caso. Detalle: `docs/capture/s20-p3-objcamera-pin-attempt.md`. P3 sigue NO_VERIFICADO; bloqueo real es la falta de límites de función/clase recuperados en `libObj.so` (RTTI/vtable pendiente). **S20-P1-MAILBOX (progreso mayor)**: pivotado a P1 en `av-cam.bin`. Búsqueda del literal `0x40193` como palabra de 4 B (57 ocurrencias) + `QuerySilentReferences.java` (55 funciones). **VERIFICADO**: `0x40193` es el buzón de entrada de un **servicio RPC síncrono** (`FUN_43b04cd4`/`FUN_43b04ca2`: asignan mensaje, escriben `reply_to` propio, envían a `0x40193`, esperan respuesta en buzón propio) — no un simple sumidero de mensajes. **VERIFICADO**: identificado el cliente **`CapIdTblMgr`** (`FUN_4381cc7c`), bucle de tarea completo con buzón propio `0x4015e`, que despacha `0xd010 GetTblAddr/0xd011 StartAccess/0xd012 StopAccess/0xd013 Init_End` vía tabla `0x43bf3800` — **la misma región `0x43bf3xxx`** que `shutter-trigger-chain-0x3011.md` ya citaba como destino de los punteros constantes de la tabla de despacho `0x3011` (`0x43ffdd30`), conectando por primera vez ambos hallazgos. **DESCARTADO**: que CapIdTblMgr sea el puente hacia CaptureStart — es cliente del servicio de tabla de IDs, no su receptor. **NO_VERIFICADO**: identidad del servidor real de `0x40193` (no está entre las 55 funciones referenciadas, todas clientes); si algún `reply_to` de otro cliente llega al dominio `0x100`/CaptureStart. **Hallazgo adicional (S20-P1-RELMGR-LINK)**: `FUN_4379d2ec` clasifica `0x1502c7` y `0x40193` en la misma clase; su único llamador registrado, `FUN_43aeaa4a`, **llama directamente a RelMgr** (`FUN_4379d838`) tras generar un id de correlación (`FUN_4379d328`, contador monotónico, no tabla de ruteo). `FUN_43aeaa4a` no tiene llamadores directos registrados (0 refs) — alcanzado solo por despacho indirecto, consistente con ser un callback registrado. **No se decidió** si es (a) retroalimentación desde la respuesta RPC de `0x40193` hacia RelMgr, o (b) la entrada real de un evento externo (S2) hacia RelMgr. Es la pista más fuerte encontrada en 3 sesiones de un camino directo y real hacia RelMgr desde el dominio `0x40193`, pero **no se declara cerrado el puente S2→CaptureStart**. Detalle: `docs/capture/s20-p1-mailbox40193-rpc-pattern.md`. **S20-P1-TABLE-0x4044**: se buscó el registro de `FUN_43aeaa4a` como callback (byte crudo del puntero Thumb `0x43aeaa4b` en todo el blob → 1 única ocurrencia, `0x43ffff88`). **VERIFICADO**: es la fila ID=`0x4044` de una tabla real de 35 filas `{id,fn,pad}` en `0x43ffff84..0x4400012c`, que también contiene el set completo de 23 comandos `0xd0xx` (CapIdTblMgr solo conocía 4). **VERIFICADO**: esta tabla NO es la tabla de 220 filas ya documentada en `silent-shutter-status.md` (`0x43fff30c`) — se decompiló su dispatcher ya conocido `FUN_438052d8` y está cableado (hardcoded) a esa dirección y a 220 iteraciones exactas; no lee la tabla nueva. Son dos tablas de despacho independientes con el mismo formato — el espacio de IDs `0x40xx/0xd0xx` se reutiliza en tablas privadas distintas, no una tabla global. El dispatcher real de la tabla nueva sigue NO_VERIFICADO (0 referencias Ghidra a `0x43ffff84`). **Hallazgo de herramienta**: `analysis/av-cam-analysis-view.elf` está desplazado +0x1F0 respecto a la convención de direcciones del proyecto (generado con `llvm-objcopy -I binary` sin saltar la cabecera del blob) — verificado byte a byte y corregido para el resto de la sesión. **DESCARTADO**: una búsqueda por literal crudo `0x4044` para hallar el remitente del comando resultó ser una coincidencia con un offset GOT no relacionado (función inicializadora distinta) — método abandonado. **S20-P1-CLOSE-AMBIGUITY**: decompilados los 52 sitios restantes de `0x40193` (todos wrappers `{tag=5,id_u16,0}`). **VERIFICADO decisivo**: `0x4379e6a8` (puerta de admisión de RelMgr) envía `0x4045`→`0x40193` condicionalmente y registra diagnóstico nuevo `0x3012`; su handler en la tabla (`0x43aea9f0`) es estructuralmente idéntico al de `0x4044` (clasifica→correla→llama a RelMgr). Los únicos llamadores de `0x4379e6a8` son 5 sitios DENTRO de `FUN_4379d838` (RelMgr) mismo. **Ambigüedad (a)/(b) resuelta a favor de (a)**: es retroalimentación interna de RelMgr, no la entrada de S2. Se precisa `shutter-trigger-chain-0x3011.md`: el mensaje final `{tipo=2,id=0x3011,...}` de `0x4379eba0` y esta familia son formatos distintos al mismo buzón — el receptor real de `0x3011` sigue NO_VERIFICADO, bloqueo original intacto. Siguiente: pivota a P4 (CBID_ENCODE_STILL), línea nueva sin tocar en esta sesión. **S20-P4-STILLCONVERTER**: usando `thumb_pc_strings.py` sobre todo `.text` de `libObj.so` se localizó por primera vez el código real (no solo la cadena) detrás de `"Receive CBID_ENCODE_STILL"` en `0x91ebe0` (bloqueo abierto desde S19-06). **VERIFICADO**: compara un ID interno traducido (`0x4000007c`), no necesariamente `0xc0000004` crudo — límite explícito. Ambas ramas construyen `ObjMsg(0x3a48)+Struct+AddParam` y llaman al mismo slot de vtable `+0xc` sobre un objeto en `ctx+0x4c` (patrón tipo `ObjPin::Send`, no verificado el layout). Atribución a `StillConverter` por densidad de cadenas, no por límites de función — mismo artefacto de etiquetado por proximidad que P3. Siguiente: seguir el pin en `ctx+0x4c` hacia su destino (candidato natural para avanzar P5/DCF). Detalle: `docs/capture/s20-p4-stillconverter-encodestill-dispatch.md`. **S20-PRIORIDAD1 (receptor real de `0x40193`)**: ampliado el alcance a los módulos `.ko` del firmware. **VERIFICADO (resuelve ambigüedad de larga data)**: `liro.ko` ejecuta `av-cam.bin` como hilo real del kernel Linux (`kthread_create_on_node`+`tsk_entry`) — LIRO no es un procesador separado. **VERIFICADO**: el OSAL real vive en `osal_uipc.ko` (`osal_snd_msg`/`osal_rcv_msg_tmo`/`osal_reg_msg_queue_cb`); los wrappers de `av-cam.bin` son tail-calls a un vtable poblado por `liro.ko`. **VERIFICADO, decisivo**: el ID de cola real es de 16 bits (`uxth` confirmado por desensamblado); `0x40193` = cola `0x193` + campo extra `0x4` (`ubfx`) — explica por qué la búsqueda literal de `0x40193` fracasó en 4 sesiones. Búsqueda de `0x193` en 44 receptores reales, 38 creadores reales y las dos tablas de despacho conocidas: 0 coincidencias. Descartado que `osal_subsystem_id/thread_id/dynamic_id` expliquen la composición del ID. **Bloqueo real**: el registro `osal_dir` vive en BSS poblado en runtime, no reconstruible estáticamente sin traza dinámica (prohibida). Línea completamente investigada con herramientas estáticas. Detalle: `docs/capture/s20-mailbox40193-osal-architecture.md`. **S20-P4-CORRECCIÓN**: localizado el constructor real de `StillConverter` (`0x916140`). **CORRIGE** la inferencia de ayer: `ctx+0x4c` es `MWF::EventReceiver` (no `ObjPin`), conectado por *loopback* local a `ctx+0x48` (`EventSender`) del mismo objeto; `ctx+0x44` es un `ObjThread` propio arrancado en construcción. El mecanismo de "Receive CBID_ENCODE_STILL" es auto-notificación hacia el hilo propio, no reenvío a DCF/MPR — este camino no lleva a P5. Detalle: `docs/capture/s20-p4-correction-eventreceiver-not-pin.md`. **S20-P5-WRITEANDFLUSH**: confirmado (sin cambios) que `FeaIf::WriteStill` solo encola. **VERIFICADO**: nuevo (tercer) llamador real de `MprFileIf::WriteAndFlush` localizado en una función no exportada (`0x13df20`) con marcas de estado `0x11/0x1010/0`; **VERIFICADO**: esa función no tiene ningún llamador directo en todo `libmpr.so` — se alcanza solo indirectamente, mismo patrón de despacho asíncrono que `EncodeStill`. Pendiente: decompilar `0x13de98` (post-procesado) y `0x13dbb0` (limpieza compartida). Detalle: `docs/capture/s20-p5-writeandflush-caller.md`. Veredicto sin cambios: A > E > P ≈ E2. SilentShutter no se declara funcional.

- **S20-LOWPRIO (RTTI)**: herramientas propias sin instalar nada (`scripts/rtti_vtables.py`, `func_owner.py`, `pin_signatures.py`). VERIFICADO: Camera.out0 = `PIN_YC#0`; 9 clases `CamUser::PinParser*` = 9 pines de ObjCamera; `0x98f974` no es de ObjCamera. INFERENCIA fuerte: objeto 53 = **ObjScalar**; "Scalar(30)" de S14 probablemente erróneo (obj 30 ≈ ObjDubbing), su conclusión sobre E2 queda en revisión. Detalle: `docs/capture/s20-rtti-tooling-p3-objid53.md`. Veredicto sin cambio de orden; E2 gana evidencia estática. SilentShutter no se declara funcional.

- **S20-CLAUDE-TOPOLOGY (0xae–0xb4/0xcb–0xcd, GetPin(6), SequenceStillCaptureStart)**: VERIFICADO: las filas del obj 53 (ObjScalar) solo las crean variantes `model/SCALAR_*` (PMCA/Scalar, INFERENCIA fuerte): `ModelCamera` SCALAR_CAMERA `0xae/0xaf` (sustituye `0x0a`), `ModelStillRec` SCALAR_STILL_REC `0xb0/0xb1` (STILL_DATA, sustituye `0x08`), `ModelScalar` `0xae–0xb3`, `ModelScalarPb` `0xb2/0xb3`, `ModelMovieRec` SCALAR_MOVIE_REC `0xcb/0xcc/0xcd`. `0xb4` no está en ninguna lista estática; su único creador es dinámico, en `ModelScalarPb` (`0x65a8a4`). GetPin(6) de S14 = PIN_YC out#2 de ObjScalar = origen de `0xb4` (corrige S14: sí existe Scalar→StillRecorder en YC, pero solo en reproducción/edición). `SequenceStillCaptureStart`: 12 Send sobre los pines STILL_DATA#0, CAMERA_STATUS#0 y YC#0 de ObjCamera. Veredicto sin cambios A > E > P ≈ E2 (E2 gana coherencia, no uso en disparo). Detalle: `docs/capture/s20-claude-topology-ae-b4-sequence.md`. SilentShutter no se declara funcional.

## S20 — Codex: cadena MPR/DCF posterior a WriteStill

**VERIFICADO:** libObj llama las APIs DCF en `0x900180/0x93be94`; libmpr
delega por AviMMgrIf `+0x38/+0x34`. `dcf_AVISequence` escribe mediante
`0x38c220` y después llama `RegisterJpegContent` (`0x22c190`) y
`RegisterDcfContent` (`0x22d648`). Callback `0x40000012` identificado hasta
MprAcsr y su EventReceiver local (resultado `0x48` B). **VERIFICADO, corrección
S19-06:** el rango de `0x45030a` es `0x40000001..0x40000091`, no `0xc0000001..91`.
**NO_VERIFICADO:** puentes asíncronos Recorder/filtro/handler FEA, selección
efectiva del secuenciador, rollback, persistencia SD y reproducción. Siguiente:
comando 9 `0x34a92c → 0x2d7d20` y dispatcher `Recorder 0x32d5b2`.
Informe: `docs/capture/s20-codex-mpr-dcf-chain.md`; evidencia `codex-dcf-*`.
Audit PASS; ruff/mypy sin avisos nuevos; originales intactos. Orden sin cambios:
**A > E > P ≈ E2**. SilentShutter no se declara funcional.

## S21 — Claude: pulsación → orden de cortina

**VERIFICADO (corrige S18-S20):** RelMgr `0x4379eba0` envía `{2,0x3011}` a la cola **`0x30001`**
(destino), con `0x40193` como origen. CamMgr `0x437fee08` → `0x43809148` traduce `0x3011`→código
local `0x100` → cola `0x302d9` → `0x43807008` → estado `0x43807f4c` → CaptureStart: **puente S2
cerrado**. El receptor real de `0x40193` es `0x4381d16c`; su tabla de 35 filas está en **`0x44000174`**
(antes `0x43ffff84`, desfase −`0x1F0`). La tabla de estado está en `0x43fcd3c4/3e0`, no en `0x43fcd5b4/5d0`.
Orden de cortina: filas `+0xa0..+0x118` de `0x437eabfc` → `Stage_CaComm 0x438c2538` → CAIF ev1/ev3
→ tarea CA `0x1502c7` → Darwin → P4D (tipos HW 1/2) / P4E (1/2/3). El selector de exposición
`0x437ea8cc` usa la tabla `0x43eddd08` (17 secuencias). Hardware: `XS_1/XS_2`→IC6000 `GPIO_S_11/13`;
`XS_1`→Darwin `INT10`; `MSS_S2_REQ_CA`→Darwin `P29/INT05`. Informe:
`docs/capture/s21-claude-button-to-shutter-order.md`; evidencia `claude-button-to-shutter.*` (PASS).
Orden **A > E > P ≈ E2** sin cambios. SilentShutter no se declara funcional.

## S21 — Codex: exposición → biblioteca (2026-10-17)

**VERIFICADO:** pre-registro DCF condicional desde Execute antes de RecordStill;
comando 9 enlazado por cola Recorder y RecStill al comando 5 de StillWriterFilter.
Selector Linux `StillInfo+0x6ac`: JPEG 0/2/3, RAW 1/2; `0x39746e` llega a
RegisterRawContent aunque su diagnóstico nombre MPO. Cleanup de escritura
incluye close/remove; retorno del filtro 4 B y evento RecStill `0x66/0x84`.
**NO_VERIFICADO:** enlace de ese evento al handler FEA/callback `0x40000012`,
selección de backend SD, compensación DCF completa y publicación en reproducción.
Se cuestiona la equivalencia automática del sobre `0x6108/0x1009` con SetImageWrited.
Informe: `docs/capture/s21-codex-exposure-to-library.md`; evidencia `codex-*`
en `analysis/session21/evidence/`. Auditor: 194 PASS; originales intactos;
ruff/mypy propios PASS, mypy src PASS; ruff src/tests conserva 9 avisos ajenos.
Siguiente: llamador virtual `0x81bb50[0] → 0x34b138`, fn/target/context y evento `0x66`.
Sin git/commit/push ni subagentes. **A > E > P ≈ E2** sin cambios.
SilentShutter no se declara funcional.

## S22 — sensor nuevo → YC para StillRecorder (2026-10-17)

**VERIFICADO:** con SHA-256 de `av-cam.bin` validado, la fila LIRO `0x78`
(`0x43b1bdb4`) llama al selector IMX210 `0x437f7ff0`. La función que contiene
`Stage_Notify` en `0x437efe78` lee `ctx+0x4b54/+0x4b58/+0x4b5c/+0x4b64`, copia
un `StillInfo` de `0x28c` B y envía un mensaje de `0x2a8` B (`0x20002`). Es
metadato/descriptores, no raster. `EncodeStill` exige `ycBufferInfo` DMM,
geometría y colorimetría; formato, pitch, caché, ownership, sincronización y
vida útil siguen abiertos. `WriteStill` es posterior a Pool/Execute y no prueba
que acepte YC crudo. **RECHAZADO:** SFRA (JPEG), RawPlay (ARW existente) y la
mera topología Camera/Scalar como productor de captura nueva. **NO_VERIFICADO:**
terminación DMA/sensor → YC → pin/Recorder y lectura electrónica completa sin
mecánica. Informe `docs/capture/s22-sensor-to-yc.md`; auditor
`analysis/session22/evidence/s22_sensor_yc_audit.py` PASS. Siguiente única:
decompilar `0x436d6118` y sus callbacks. **VEREDICTO: PARCIAL.**
SilentShutter no se declara funcional.

## S23 — Codex: frontera Dataflow de `PIN_YC#0` (2026-10-17)

**VERIFICADO (hallazgo mayor):** `CamUser::PinParserYcOut0` (vtable
`0x1021fb8`, método `0xa279c8`) recibe la rama `0x1000`, exige cuatro
`ParamStd<unsigned int>` (`0x1000..0x1003`), conserva sus valores en
`this+0x34/+0x38/+0x3c/+0x40` y llama `0xa14f88`. Esta función es un puente
Dataflow síncrono: serializa exactamente 20 B, usa `srcId=replyId=0x2015d`,
envía a `this+0x10`, espera una respuesta con timeout `UINT32_MAX` y copia 20
B si el tipo recibido es 1. Es compartido por los parsers `YcOut0/1/2/3/5`.
El request YC0 tiene header `{0x1000,0,0x14,2}` y tres palabras de
`this+0x10/+0x14/+0x18`. La salida `ObjPin::Send(0x1003)` de YC0 usa un sobre
`0x2001/0x1001` con `0x1005` o `0x132e`; no es el `PlayData 0x2001/0x1003` ni
lleva los grupos conocidos del Recorder. **RECHAZADO:** que este parser sea el
productor del raster por sí solo. **NO_VERIFICADO:** identidad del destino,
semántica de los cuatro enteros, handler Dataflow `0x1000`, DMM/YC,
caché/propiedad/vida útil y lectura electrónica sin mecánica. Informe
`docs/capture/s23-yc-pin-dataflow-boundary.md`; auditor
`analysis/session22/evidence/s23_yc_dataflow_audit.py` PASS. Siguiente única:
constructor/registro que asigna `PinParserYcOut0+0x10` y receptor Dataflow de
`0x1000`. **VEREDICTO: PARCIAL.** SilentShutter no se declara funcional.

## S24 — Codex: endpoint de `Camera.YC0` (2026-10-17)

**VERIFICADO:** el constructor ObjCamera crea `PinParserYcOut0` con
`new(0x54)` en `0x987eb6`, lo asocia a `PIN_YC#0` (`ObjCamera+0x58`) y guarda
la instancia en `ObjCamera+0xa0`. Su ctor `0xa281dc` fija
`this+0x10=0x00050004`, `+0x14=0`, `+0x18=2`; por tanto el request Dataflow
S23 usa un destino constante. El código `0x15d6c0..0x15d7a2` crea
`DataflowInfraCh`, recupera dos pines para `0x50004` y los reconecta; por RTTI
queda junto a `OBJEFFECT::State_IntelligentActivePostProcess` (vtable
`0xfee988`). **INFERENCIA FUERTE:** Camera YC0 se configura en el dominio
ObjEffect, acorde a la topología Camera→Effect. **NO_VERIFICADO:** callback
exacto que consume el payload `0x1000`, receptor final, contenido YC/DMM y
ruta de captura electrónica. Informe
`docs/capture/s24-camera-yc0-effect-endpoint.md`; auditor
`analysis/session22/evidence/s24_yc_endpoint_audit.py` PASS. Próxima única:
resolver los dos pines recuperados por `infraGetPin` y su callback de
payload. **VEREDICTO: PARCIAL.** SilentShutter no se declara funcional.

## S25 — Codex: límite del registro Dataflow (2026-10-17)

**VERIFICADO:** `DataflowInfraCh::infraGetPin` en `libBizFw.so:0x35a74` crea
`_MSG_PIN_GET` con opcode `0x1000`, llama `sndRcvAsyncDataflowMsg` y copia el
pin/descriptor desde la respuesta, incluido `reply+0x20 → out+0x1c`. No hay
una tabla local estática endpoint→callback en los constructores Camera/ObjEffect
ya recuperados. **INFERENCIA:** el registro de `0x50004` se llena durante un
ciclo de vida Dataflow; no se ha localizado aún el alta. **NO_VERIFICADO:**
receptor final, YC/DMM y resto de contrato. Informe
`docs/capture/s25-dataflow-pin-registry-limit.md`; auditor
`analysis/session22/evidence/s25_dataflow_registry_audit.py` PASS. Siguiente
única: inicializador que registra `0x50004` / `INFRA_GET_PIN_COMP` en
libObj/libBizFw/dataflowInfraFramework. **VEREDICTO: PARCIAL.** SilentShutter
no se declara funcional.

## S26 — Codex: seis microprocesos estáticos de `Camera.YC0` (2026-10-17)

**CERRADO ESTÁTICAMENTE (alcance acotado):** seis procesos con entrada,
transformación y salida verificables: (1) ObjCamera instancia
`PinParserYcOut0` y lo guarda en `+0xa0`; (2) rama `0x1000` admite cuatro
parámetros y los guarda en `+0x34..+0x40`; (3) helper serializa cabecera
Dataflow de 20 B `{0x1000,0,0x14,2}`; (4) puente `0xa14f88` transmite y espera
la respuesta; (5) `infraGetPin` resuelve un pin desde la respuesta del
registro; (6) parser crea `ObjMsg(0x2001,0x1001)` y lo envía con
`ObjPin::Send(0x1003)`. **RECHAZADO:** tratar esos cierres de transporte como
prueba de un YC de captura o como `PlayData` de Recorder. **NO_VERIFICADO:**
productor sensor/DMA, contrato YC/DMM, callback/alta de `0x50004`,
compatibilidad `WriteStill`, y lectura electrónica sin mecánica. Informe
`docs/capture/s26-five-static-microprocesses.md`; auditor
`analysis/session22/evidence/s26_closed_microprocesses_audit.py` PASS.
**VEREDICTO: PARCIAL.** Próxima única: localizar el alta de `0x50004` y su
callback `0x1000`. SilentShutter no se declara funcional.

## S27 — Codex: recableado ObjEffect PostProcess (2026-10-17)

**VERIFICADO:** `0x15d6c0..0x15d7c4` es el slot virtual 4 de
`OBJEFFECT::State_IntelligentActivePostProcess` (vtable `0xfee988`), y realiza
dos transiciones completas `disconnect → infraGetPin → infraConnectPin` con
control de error. Cada perfil conecta el resultado de `0x005a0048` con el de
`0x50004`; también desconecta `0x01670464`. **NO_VERIFICADO:** significado de
los IDs, registro/callback del opcode, productor YC y compatibilidad Recorder.
Informe `docs/capture/s27-effect-postprocess-rewire.md`. **VEREDICTO:
PARCIAL.** Siguiente única: dispatcher que atiende `_MSG_PIN_GET`/`0x1000`.
SilentShutter no se declara funcional.
