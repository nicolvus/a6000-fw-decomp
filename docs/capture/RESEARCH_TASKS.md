# RESEARCH_TASKS — registro de coordinación (mantiene solo el coordinador)

## Estado vigente S30 (17-10-2026)

- Captura nueva sin cortinas: pendiente; la ruta fija demostrada usa CAIF/Darwin.
- Sensor/DMA→YC: pendiente; `+4b54` es CaptureId y `436d6118` es getter.
- EncodeStill→Pool: control seguido por InfraAvbbc `55001f`, StillEncoder
  `550123`, SDF `56000f`, retorno bloqueante y continuación a Pool.
  SDF→executor `560010`→driver JPEG→callback SAFIN y espera localizados;
  formato/caché/reciclaje
  del YC de captura todavía no están cerrados.
- [Evidencia y veredicto S30](s30-pipelines-capture-encode.md): 12/12 checks.
  S28/S29 continúan 6/6 cada uno. Las filas históricas siguientes no
  sustituyen estas correcciones.

Definiciones de tarea: docs/capture/tasks/*.md. Logs Codex: analysis/codex-logs/.
| ID | Línea | Tarea | Estado | Depende | Salida | Desbloquea |
|----|-------|-------|--------|---------|--------|------------|
| A | MPR/DCF StillInfo | A-01..04 | COMPLETADO (veredicto CAMBIOS) | — | analysis/stillinfo-layout.json, mpr-dcf-recording.md | B, E, diseño |
| B | SFRA<->MPR | B-01..05 | COMPLETADO (CAMBIOS) | A parcial | sfra-mpr-buffer-bridge.md | arquitectura B/C |
| C | Disparador/CaptureManager | C-01..05 | COMPLETADO (CAMBIOS) | — | shutter-trigger-state-machine.md | arquitectura A/C |
| D | Reutilizar etapas | D-01..04 | NO ENTREGADO (límite de Codex agotado); retomar a mano | A,C | capture-stage-reuse.md | A vs B |
| E | DCF/reproducción | E-01..04 | NO ENTREGADO (límite de Codex); retomar | A | sony-dcf-playback.md | validación |
| F | Productor SFRA/exposición | F-01..05 | NO ENTREGADO (límite de Codex); parcial en sfra-linux-client.md | B | sfra-electronic-frame-source.md | C+F |
| C2 | Cadena 0x3011->CaptureStart | C2-01 parcial: dispatcher 0x43807f4c (msg 0x100→0x438082ce→0x43807d80→0x43809ed8→CaptureStart), referenciado como puntero de función en vtable 0x43fcd3e0; llamador del dispatcher NO localizado estáticamente; receptor de cola 0x40193 NO localizado (sin literal, sin movw/movt, sin BL directo); C2-02 parcial (filas fila8 en capture-stage-reuse.md); C2-03/C2-04 abiertos | NO ENTREGADO | C | shutter-trigger-chain-0x3011.md + analysis/rea-independent/out/C2_CHAIN_ANALYSIS.md | arquitectura A |
## Hallazgos integrados (ronda 1)
- A: tres ABI distintos: payload LIRO 0x28c (mensaje 0x1006), StillInfo Linux 0x6b0 (punteros virtuales), WriteStillParam 0x40. JpgInfo = 11 descriptores de 0x10 B (memHandle,offset,size,arg reuse). Miniatura OBLIGATORIA para EXIF nuevo; no hay autogeneración. Evento de playback y EXIF mínimo NO VERIFICADOS.
- B: handle SFRA = unidad DMM u16 mapeable en Linux; GET_JPEG saca el buffer del ring (propiedad al cliente); GET_JPEG solo da {handle,size>>7} (sin EXIF/thumb/scn; CORRIGE la hipótesis previa de EXIF/SCN por fotograma = DESCARTADO). Tamaño redondeado a 128 B: hay que conocer el tamaño exacto (parser JPEG). Compatibilidad con mainJpg NO VERIFICADA.
- C: RelMgr empieza en 0x4379d838 (no ..3a); 1 y 0x10 son ÍNDICES, no bits S1/S2. Selector inicial de secuencia 0x437eabfc (desde 0x437df338) = divergencia candidata. 0x43841070 NO es el selector de secuencia. 0x3011 (CamUser 0x40193) enlace a CaptureStart NO VERIFICADO.
- Claude (F parcial): ver docs/capture/sfra-linux-client.md (buzones, DMM, propiedad).
- Implicación arquitectónica provisional: un JPEG SFRA no trae miniatura/EXIF => arquitectura B pura (Linux) exige fabricar thumb+EXIF+reserva; arquitectura A/C (LIRO produce main+thumb+scn con etapas existentes desde un YC y Stage_Notify) reutiliza más. Decisión pendiente de D/F.

## Ronda 2
D, E, F y C2 se interrumpieron al agotarse el límite de Codex sin dejar entregables. Síntesis y preguntas abiertas: `silent-architecture-comparison.md`.

## Ronda 3 (Claude en solitario, Codex agotado)
- D: tabla de secuencias RESUELTA (capture-stage-reuse.md).
- C2: parcial (shutter-trigger-chain-0x3011.md): 0x3011 se arbitra por tabla (id,estado) en 0x43ffdd30; receptor de la cola 0x40193 NO localizado.
- F: parcial (sfra-electronic-frame-source.md): YC llega por pines EE/Rec (PinSend 0x439abbfe), existe 'shutter mute thru'.
- E: parcial (sony-dcf-playback.md): HALLAZGO: MprIf::MakeWriteStillImage + ObjScalar::RecordStillImageCmd + ScalarDaemon::recordStillImage = ruta existente para grabar una imagen externa (precedente para arquitectura B/C).

- Sesión 9 P1: completado (0x93677c, 0x930174, 0x930464 reconstruidos; DESCARTADO que grabe en SD). P2–P6 abiertos.

- Sesión 10 P1/P2: completados (0x3a48 = respuesta genérica; GetFileImage = ObjConverter/TRANSFERENCIA; 0x1027 → ObjStillRecorder modo 4). Abierto: fuente de imagen en modo 4, miniatura/screennail, llegada a WriteStill, 0x3011.

- Sesión 11: completado el análisis de Execute/0x1027/MediaMgr. Resultado: 0x1027 = armado; imagen vía Pool/RegisterImage. Abiertos: layout 0x100b, remitente de PreRegisterImage, invocadores de Execute, DCFStillWriter y SetImageWrited. Ver `objstillrecorder-mode4.md`.

- Sesión 12: completado el contrato de `0x100b` (ver analysis/objstillpool-100b-layout.json), `MediaMgr+0x2C` (= mediaSelectMode, None=4), `PreRegisterImage` (orden de Pool 0x1017, reserva sin búferes), retorno (`SetImageWrited` = Pool 0x1009) y la 2ª ruta `ObjStillRecorderCore::WriteStill`. Abiertos: remitente de la orden 0x10000005 y 0x10000003; relación StillInfo.jpg_info LIRO ↔ Execute (¿se usa o solo YC?); formato YC admitido por EncodeStill; origen del modo ≠ None; emisor de SetImageWrited; contenido del bloque 0xBC; capacidades 0x50D17/0x170D0C/0x170D0B; DCFStillWriter/índice de reproducción.

## Sesión 13
- DONE: remitente de la orden: `0x10000005` la genera el propio recorder (`0x919f1a`); disparada por `RECORD_IMAGE_CMD` (`0x3500/0x3001`) de ModelPbCap/ModelPaint/Mcmd (`encodestill-command-origin.md`).
- DONE (parcial): contrato de `RegionInfo`/EncodeStill (`encodestill-yc-contract.md`); formato real del YC implícito en `unitType` (NO verificado).
- OPEN: productor del `PlayData` para el pin YC (topología ObjHandover `0x2a`, captura YUV de ObjRenderer, ObjScalar recordStillImage).
- OPEN: ¿el YC del EE (anchos 320/640/1024) cumple el contrato y sobrevive? (`liveview-yc-to-encodestill.md`).
- OPEN: disparador de `0x6137b0` y precondiciones de UI de PbCap; mapa de ModelPaint/Trimming/Retouch.
- OPEN: valores de `unitType`, disposición de planos, lectura asíncrona de FEA.

## Sesión 14
- DONE: topología `0x2a` y productor del pin YC (ObjEffect salida nº1) — `objhandover-2a-topology.md`; premisa «ObjHandover» descartada.
- DONE: traza `YcPinReqDeliver → ObjEffect → PlayData → Execute` — `analysis/yc-pin-delivery-flow.json`.
- DONE (parcial): `unitType` y capa DMM — `yc-unit-types-and-layout.md` (tamaños de extents sin decodificar).
- DONE (parcial): vida útil/FEA — `fea-encodestill-buffer-lifetime.md` (asíncrono; instante de liberación NO verificado).
- DONE: ObjScalar como puente — `objscalar-playdata-bridge.md` (no demostrado; E2 sin sustento).
- OPEN (bloqueo): modo interno de ObjEffect en EE y entrada de Camera → secuencia WriteStill; quién crearía `0x2a` en disparo; tipos de unidad de los YC de la cámara.
- OPEN: listas de topologías de Paint/Art/Beauty y de modelos de disparo (StillRec, Camera, MovieRec); objetos 0, 46, 53 de la tabla.
- OPEN: destino de `FeaIf this+4` (StillEncoder) y tamaños de los extents `0xed/0x13d/0xe4` en dmm.ko.

## Sesión 15 — investigación en paralelo (principal + Rama A Claude Sonnet 5 + Rama B Codex gpt-5.6-terra)
Detalle: `docs/capture/liveview-encodestill-parallel-verdict.md`, `analysis/liveview-encodestill-crosscheck.json`, `docs/capture/claude-main-bridge-verification.md`, `docs/capture/branch-claude-objeffect.md`, `analysis/branch-claude-effect-states.json`, `docs/capture/branch-codex-camera-yc.md`, `analysis/branch-codex-yc-memory.json`, `analysis/dmm-extent-sizes.json`.
- INCIDENTE: la Rama A lanzó un segundo subagente sin permiso en su primera ejecución; se detuvo con TaskStop sin entregables y se relanzó correctamente (un solo agente, sin delegar).
- DONE: identidad del objeto 8 = ObjCamera, antes INFERENCIA fuerte, ahora VERIFICADO por constructor real (ELF `0x98c380`); sus 9 pines son todos de salida (ningún pin de entrada).
- DONE: estructura real de `EffectInternalMode` (holder indirecto tras `GetSubState(block,1)`, no `this+0x14+4`); escritor localizado (ELF `0x173158`) con tabla `0x1025→modo`; modos con acción real sobre REQ_DELIVER: `{1,2,3,4,5}`.
- DONE: tamaños reales de extents DMM (`0xed`=`0x3fc000` B, `0xe4`=`0x800` B exactos, `0x13d`=`0x96000` B); confirma que `0xe0b00` es solo cabecera SDS, nunca el raster.
- DONE: doble verificación independiente (principal + Rama A) de las filas de topología `0x0a/0x07/0x2a` y sus `StsId` (0/0/6), y de la lectura de `TM::createLifeCycles` (sin guard de exclusión mutua hallado).
- OPEN (bloqueo, sin cambios de fondo): ningún modelo de disparo conocido crea `0x2a` (318 sitios de llamada revisados parcialmente); ningún escritor de `EffectInternalMode` activado desde `ModelBootEE`; `unitType`/formato del YC de Camera/EE; escritor del modo 1 de Effect; receptor y momento de liberación tras `CBID_ENCODE_STILL`.

## Sesión 16 — investigación en paralelo (principal + Rama A Claude Sonnet 5 medio + Rama B Codex gpt-5.6-terra medio)
Detalle: `docs/capture/s16-liveview-recorder-verdict.md`, `analysis/s16-liveview-recorder-crosscheck.json`, `docs/capture/s16-main-delivery-sequences.md`, `docs/capture/s16-claude-effect-control.md`, `analysis/s16-claude-topology-audit.json`, `analysis/s16-claude-effect-mode1.json`, `docs/capture/s16-codex-camera-yc.md`, `analysis/s16-codex-camera-yc.json`, `docs/capture/s16-codex-fea-completion.md`.
- Sin incidente de delegación esta vez (corrige el de sesión 15); modelos/esfuerzos confirmados por ejecución real.
- DONE: dos escritores dinámicos reales de `EffectInternalMode=1` localizados por RTTI (`ExecCmdAppFaderEfctEndEvt` ELF `0x154990`, `SequencePinDeliverBase` ELF `0x1e069c`), corrigiendo el bloqueo "sin escritor" de sesión 15; verificado independientemente por el principal (cadenas RTTI + words de vtabla).
- DONE: segunda fila con `StsId=6` (`0xb4`, objeto 53 → StillRecorder, mismo destino que `0x2a`) — nuevo candidato de arbitraje vía `StsViewer` compartido.
- DONE: recuento reproducible de 213 sitios `createTopology`/`destroyTopology` (corrige la cifra de 318); único creador literal de `0x2a` sigue siendo `ModelPbCap`.
- DONE: segundo handler gemelo (ELF `0x1f25d8`) confirma independientemente la regla modo1+0x1011→0x600d; factoría `0x17b004` muestra que solo `0x6013` instancia una Sequence con estado — `0x600d` es mensaje plano, sin evidencia de transporte de imagen.
- DONE: cadena `FeaIf::EncodeStill` desensamblada (verificada independientemente): solo encola, copia descriptor de 0x40 B, no espera finalización; `StillConverter` candidato (INFERENCIA fuerte) a receptor de `CBID_ENCODE_STILL`.
- OPEN (bloqueo, caracterización más precisa): alcanzabilidad de los dos escritores de modo 1 desde EE/disparo; arbitraje real del `StsViewer` de `StsId=6` (`GetStsViewer` ELF `0x4294cc`, `ConnectPin` ELF `0x41c25e`, no decompilados); otro creador de `0x2a` aparte de PbCap; `unitType`/formato del YC de Camera; consumidor exacto y momento de liberación tras `CBID_ENCODE_STILL`.

## Sesión 17 — investigación en paralelo (principal + Claude A + Claude B Sonnet 5 medio + Codex C + Codex D gpt-5.6-terra medio) — ruta E y ruta pública P (CameraSequence)
Detalle: `docs/capture/s17-parallel-research-verdict.md`, `analysis/s17-parallel-crosscheck.json`, `docs/capture/s17-public-camera-api-crosscheck.md`, `docs/capture/s17-a-e-p-architecture-comparison.md`, `docs/capture/s17-main-s2-integration.md`, `docs/capture/s17-claude-a-topology.md`, `docs/capture/s17-claude-b-camerasequence.md`, `docs/capture/s17-codex-c-sdf-yc.md`, `docs/capture/s17-codex-d-fea-lifetime.md`, `docs/capture/s17-codex-d-dcf-crosscheck.md`.
- Sin incidente de delegación (los 4 agentes confirmaron no usar `Agent` ni lanzar procesos adicionales). Discrepancia de proceso declarada: Claude B reportó esfuerzo "bajo" en vez del "medium" solicitado; Codex C/D confirmados en `medium` por llamada de prueba.
- DONE (cierra el bloqueo "decompilar GetStsViewer/ConnectPin" de sesión 16, VERIFICADO): `ConnectPin`/`ObjPin::Connect`/`ObjStatusViewer` NO están en `libObj.so` sino importados de `libMWF.so`; `ObjPin::Connect` (ELF libMWF `0x29588`, re-verificado por el principal por desensamblado directo) no arbitra por ocupación de pin — solo valida tipo y dirección; `GetStsViewer` (ELF libObj `0x4184cc`, no `0x4294cc` como citaba el encargo — corrección de direccionamiento Ghidra-VA/ELF) es un *get-or-create* por `sts_id` sin lógica de exclusión. Debilita la hipótesis de arbitraje activo; refuerza la de exclusión puramente estructural entre `0x2a`/`0xb4` (puntero escalar de pin conectado, no lista).
- DONE: decompilado completo del selector LIRO `0x437eabfc` (árbol de 4 niveles sobre campos de la petición de captura, sin marca de modo Silent/EFCS); confirmado que su tabla de filas (`0x43edccf8`) es BSS/cero en la imagen estática (explica, no solo asume, la no recuperabilidad).
- DONE: dos callers reales de `0x43809ed8` (instalador de `CaptureStart`) localizados por desensamblado directo (Ghidra en modo sin análisis no los veía); ninguno referencia literalmente `0x3011`/`0x40193` — reduce sin cerrar el bloqueo del consumidor de la cola.
- DONE: corrección de dirección del constructor de la Sequence `0x6013` (ELF `0x1761a8`, no `0x1861a8`); `BeginExecCommand` candidato (`0x15fd50`) sin chequeo de `unitType` en sus 3 guardas; geometría y contrato de `PlayData` (`0x15ebfc`) reconstruidos.
- DONE: API real de registro de callback FEA (`MprIf::SetCallbackFunc` `0x71f7b8`, `FeaIf::MprIfCallbackPoint` `0x4502e8`) y rango de IDs `0xc0000001..0xc0000091`, con `0xc0000004` como candidato no confirmado a `CBID_ENCODE_STILL`; ningún liberador real de buffers localizado tras `EncodeStill`.
- DONE (nueva línea P): `CameraSequence`/`CameraEx`/`DeviceBuffer` verificados como reales en el firmware local (no solo citados de GitHub), con backend Binder/`ScalarDaemon`; `onShutterKeyDown` de PMCADemo usa captura convencional, no `CameraSequence` — sin enlace a S2.
- OPEN (bloqueo, caracterización más precisa): sitio real que invoca `ObjPin::Connect` desde un `LifeCycle` ya construido (`LifeCycle::ctor`/`Activate` no decompilado); llamador vía vtabla de `0x43809ed8` más allá de sus dos callers directos; productor real del YC de Camera hasta un descriptor concreto; receptor real de `CBID_ENCODE_STILL`; enlace S2↔`CameraSequence` (inexistente, requeriría app nueva).

## Sesión 18 — inventario Sony OSS + 8 ramas en paralelo (4 Claude Sonnet 5 + 4 Codex gpt-5.6-terra, medio solicitado)
Detalle: `docs/capture/s18-parallel-research-verdict.md`, `analysis/session18/main/s18-parallel-crosscheck.json`, `analysis/session18/main/sony-oss-inventory.md`/`.json`, `docs/capture/s18-main-init-437ebed8.md`, `docs/capture/s18-claude-{a,b,c,d}-*.md`, `docs/capture/s18-codex-{e,f,g,h}-*.md`, `analysis/session18/codex-g/sony-oss-memory-crosscheck.md`.
- Inventario inicial de 6 paquetes Sony OSS reales añadidos por el usuario (kernel Linux 3.0.27 con SoCs propios `mach-cxd90014`/`mach-cxd4132`, + iproute2/iptables/libpng/webkit/wpa_supplicant genéricos); ninguno contiene código propietario de cámara.
- Incidente de corrección declarado: la hipótesis inicial del principal (sdc.c = controlador SD) fue refutada independientemente por Codex G y Codex H — es calibración LPDDR. Corregido en el inventario tras verificación propia.
- Discrepancia de proceso: Claude B repite el patrón de sesión 17 (esfuerzo "bajo" autoinformado en vez de "medium"), con intento fallido de autocorrección bloqueado por la herramienta. Sin incidente de delegación (los 8 agentes confirman no haber lanzado subagentes).
- DONE: inicializador LIRO `0x437EBED8` resuelve la tabla del selector de captura (antes creída BSS irrecuperable) vía punteros GOT estáticos — cierra metodológicamente ese blocker de sesión 17. Las 15 filas son trampolines hacia implementaciones reales; las 4 dinámicamente seleccionables (`0xa0,0xc8,0xdc,0x104`, offsets reales corregidos) son casi idénticas a la `0xb4`, sin marca Silent (confirmado por duplicado, Claude A + Claude C).
- DONE: blocker de `Connect()` (sesión 15-17) reducido a 5 bibliotecas candidatas concretas (`libBizFw.so`, `libBizFw2.so`, `libInfraCacheMgr.so`, `libInfraScalarMpr.so`, `libmprctrl.so`); `libObj.so` descartado como importador directo. La llamada real sigue sin localizarse (indirecta vía registro).
- DONE: `0x43807f4c` identificado como llamador real de `0x43807d80` (dominio local `0x100..0x207`); el puente con el dominio `0x3011/0x40193` sigue sin probarse — ahora el bloqueo mejor delimitado de toda la investigación.
- DONE: confirmado por método independiente que la técnica "inicializador GOT→BSS" de LIRO no tiene equivalente en `libObj.so` (la tabla de topología ya es `.rodata` estática; el problema de "objeto 53" es de registro dinámico, no de inicialización).
- DONE: contrato YC/SDS más preciso (raster `0x50b3f` + SDS `0xe0b00` de control, vía `YcSdsAcsr`); superficie DMM/`AvbbcPhycMem` confirmada en `libObj.so`, sin enlace estático al kernel OSS.
- DONE: corrección de sesión 17 por Claude B — puente `CameraSequence→ScalarDaemon` usa `libsdcom.so` ("SDCom"), no Binder; Binder solo en el tramo convencional.
- OPEN (bloqueo, mejor delimitado): cerrar `Connect()` dentro de las 5 bibliotecas vía análisis de flujo de datos; probar/refutar el puente `0x100..0x207`↔`0x3011/0x40193`; decompilar las 10 filas restantes de la tabla de 15 de LIRO; identificar clase real de ObjId 53 por auto-registro.

## Sesión 19, ejecución 01 — S19-01

- PARCIAL: ver `s19-s2-domain-bridge.md`. La tabla estática `0x43fcd5b4` contiene el slot Thumb `0x43fcd5d0 = 0x43807f4d`, que registra el dispatcher local; su caso `0x100` llega a `0x43807d80` y a rutas que invocan `0x43809ed8`.
- Sigue abierto: demostrar el receptor/registro de `0x40193` y la traducción `0x3011/0x3013/0x3015` → `0x100..0x207`; el slot registrado no es evidencia de ejecución ni de pertenencia a la cola. Siguiente: S19-02.

## Sesion 19, ejecucion 02 — S19-02

- PARCIAL: se verificó el llamador efectivo `UObjPin::Connect (libBizFw2:0x2bf1c) → MWF::ObjPin::Connect@plt`, más los tres wrappers de infraestructura y las restricciones MWF. `TM::createLifeCycles → ctor 0x41b6c0 → registro` también quedó reconstruido.
- Sigue abierto: la arista de ejecución entre el LifeCycle/despacho activación-candidato (`0x416faa→0x41b728`) y Connect; no equiparar vtable/registro con callback ejecutado. Siguiente: S19-03.

## Sesion 19, ejecucion 03 — S19-03

- PARCIAL: `ObjStillRecorder_Create` (`0x91391c`) reserva `0x148` y usa el constructor `0x9178f0`; la fila `0xb4` mantiene ObjId `0x35` hacia su `in0`. La identidad de clase queda corroborada, pero no la tabla/mapa que registre el entero 53.
- `.init_array` tiene 263 entradas relativas, ninguna para `ObjStillRecorder_*`; no se halló puntero directo de esas APIs en datos asignables ni un auto-registro explícito. Mantener como NO_VERIFICADO (puede ser indirecto/externo). Siguiente: S19-04.

## Sesion 19, ejecucion 04 — S19-04

- PARCIAL: Camera crea nueve pines de salida y `0x0a` enlaza Camera.out0→Effect.in0; no se recuperó llamada DMM/Avbbc ni descriptor YC desde el constructor o esos pines.
- VERIFICADO: el par DMM raster `0x50b3f`/SDS `0xe0b00` es de la ruta Effect/PbCap; `0x800` B SDS no es raster. NO_VERIFICADO: contrato del frame Camera (unitType, handle, offset, física, geometría, formato, stride, planos, colorimetría, ownership y reciclaje). DESCARTADO inferirlo de IMX210. Ver `s19-camera-yc-real-contract.md`; siguiente: S19-05.

## Sesion 19, ejecucion 05 — S19-05

- PARCIAL: `0x6013→0x1761a8→0x15fd50` reconstruye una secuencia PbCap completa: precondiciones holder/interfaz/selectores, conexión `DataflowInfra`, reservas de salida, envío SDF, publicación de PlayData solo con `0x111` y cleanup de sus salidas.
- NO_VERIFICADO: vincular Camera.out0 con ese holder, pines, comando SDF o contrato de entrada; tipos DMM, resolución, formato y vida útil del YC Camera continúan desconocidos. No usar la ausencia de un check de `unitType` como prueba de compatibilidad. Ver `s19-camera-effect-sdf.md`; siguiente: S19-06.

## Sesion 19, ejecucion 06 — S19-06

- PARCIAL: receptor real de `CBID_ENCODE_STILL` sigue abierto. Quedó verificado el puente global `MprCtrl::Init` → `MprIf::SetCallbackFunc` → `FeaIf::MprIfCallbackPoint` → `EventSwitcher`, incluido el filtro por `targetId` y `eventId`.
- Siguiente: S19-07 debe localizar la tabla concreta registrada por `libObj.so:EventSwitcher::AddCallbackFunc` que contenga `0xc0000004`, y enlazarla (o refutarla) con `StillConverter`; no inferir que FEA copia píxeles, termina la lectura, cancela ni libera en el retorno de `EncodeStill`.

## Sesion 19, ejecucion 07 — S19-07

- PARCIAL: se inventariaron las diez filas LIRO que sí seguían sin caracterizar (`0x00,0x14,0x28,0x3c,0x50,0x64,0x78,0x8c,0xf0,0x118`). Son manejadores completos con selector/estados y ramas de retry/cancelación, de la familia convencional; no son prueba de adquisición, codificación, finalización o SilentShutter. Ver `s19-liro-remaining-sequences.md`.
- Siguiente: S19-08 debe localizar la tabla concreta de `EventSwitcher::AddCallbackFunc` para `0xc0000004` y seguir su receptor/ownership sin usar retornos de LIRO como prueba de JPEG terminado.

## Sesion 19, ejecucion 08 — S19-08

- PARCIAL: quedaron verificadas interfaces distintas para admisión de `WriteStill` (`libmpr.so:0x44f784`), construcción EXIF/thumbnail/screennail (`0x38b064`/`0x37af44`), delegación de `WriteAndFlush` (`0x726138`), pre-registro/lookup DCF (`0x71eafc`/`0x71eb70`) y reproducción/miniaturas (símbolos MPR). No hay arista estática que las una para una misma foto.
- Sigue abierto: identificar el receptor de la interfaz virtual de `WriteStill` (paquete 0x90 B), después seguir pre-registro, nombre/numeración, escritura/flush, resultado/error/rollback y la publicación de `EntryId` al consumidor de `0x3500/0x3002`. Mantener separados JPEG válido, escritura SD, registro DCF y visibilidad en reproducción. Siguiente: S19-09.

## Sesion 19, ejecucion 09 — S19-09

- PARCIAL: `CameraSequence` llega localmente a ScalarDaemon por SDCom: `startPreviewSequence` manda `0x124`, `getPreviewSequenceFrames` manda `0x127` y la respuesta se representa como `DeviceMemoryDiadem`; `readBuffer` usa map/copy/unmap de memoria compartida y `release` envía `0x3` con ticket. Binder queda separado en CameraEx convencional.
- Sigue abierto: formato y dimensiones efectivas (640×480/JPEG no demostrados), productor, YC, lifetime/propiedad final, S2 y MPR. Siguiente: S19-10, seguir la entrega del YC de SFRA al cliente Linux para alcanzar el origen de tickets/backing sin atribuirle todavía SilentShutter.

## Sesion 19, ejecucion 10 — S19-10

- PARCIAL: SFRA existe en `av-cam.bin`; su entrada YC es interna por pines EE/Rec. La salida ISS recuperada es JPEG READY en DMM: `pubSfrGetJpeg` pide `0x2009/0x100`, recibe handle u16/tamaño en bloques de 128 B y `pubMmap` abre `/dev/mem` y mapea el extent.
- Siguiente S19-11 (b): caracterizar los modos 2–5 de ObjEffect con entrada Camera; es la prioridad no ejecutada que ataca Camera→Effect, que la ruta JPEG paralela no resuelve. Mantener SilentShutter como NO VERIFICADO.

## Sesion 19, ejecucion 11 — S19-11

- PARCIAL: el rango efectivo visto en el filtro `0x176cc6` de este dispatcher concreto (`0x176294`, secuencia ObjEffect) es 2–5; modo 3 solo construye `0x3900/0x0002`, mientras 2/4/5 toman error EN ESTE RECORRIDO. No se generaliza a otros dispatchers/secuencias de ObjEffect no examinados (corrección sesión 20, C3: ver `s20-s19-corrections.md`). No es la ruta PbCap `0x3900/0x3000`, ni demuestra un buffer de still.
- Siguiente S19-12 (h): localizar condiciones que evitan o seleccionan captura mecánica. No convertir el despacho Effect en evidencia de cortinas, Silent/EFCS o funcionamiento de SilentShutter.

## Sesion 19, ejecucion 12 — S19-12

- PARCIAL: RelMgr, el dispatcher local, `CaptureStart` y `CaptureManager` contienen guardas verificadas que pueden impedir alcanzar la ejecución convencional. El último selector recuperado es `0x437eabfc`, que instala un descriptor de cinco palabras antes de `0x43b04730`.
- NO VERIFICADO: fila `0x43edccf8` → CAIF/Darwin, semántica de sus campos y una alternativa que omita cortinas sin romper exposición/lectura/limpieza. EFCS es un selector de exposición ya existente, no evidencia de obturación totalmente electrónica. Ver `s19-mechanical-shutter-decision-points.md` y `analysis/session19/evidence/mechanical-shutter-decision-points.json`.
- Siguiente S19-13 (d): seguir cancelaciones y estados posteriores a S2 para recuperar las invariantes de cancelación/liberación entre admisión, `CaptureStart` y las filas LIRO.

## Sesion 19, ejecucion 13 — S19-13

- PARCIAL: `0x3015` se emite desde RelMgr; `0x43807d80` tiene salidas de estado/limpieza y la etapa LIRO `0x437f22d4` limpia condicionalmente `ctx+0x754` con `0x437fbad8` y retorno `0/1/2/5`. No hay arista demostrada entre esos tres hechos.
- NO_VERIFICADO: idle, cancelación tras compromiso, liberación de DMM y cualquier ventana segura antes de CAIF/Darwin. `DmmClose` no se puede usar como liberación de asignación. Ver `s19-post-s2-cancellation-states.md` y `analysis/session19/evidence/post-s2-cancellation-states.json`.
- Siguiente S19-14 (f): reconstruir `Stage_RawPlayInit` y reutilización de etapas para recuperar contratos de inicialización/finalización y ownership sin inferir movimiento de cortina.
