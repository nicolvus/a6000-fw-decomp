# Veredicto continuo Codex — Sesión 19, ejecución 01

**S19-01: PARCIAL.** `0x43807f4c` está inscrito indirectamente mediante el slot Thumb `0x43fcd5d0 = 0x43807f4d`; su caso local `0x100` alcanza la familia que instala `CaptureStart`. Esto no identifica el receptor de `0x40193` ni demuestra traducción de `0x3011/0x3013/0x3015` a aquel dominio. La liberación/cancelación cruzada y la relación exacta con S1/S2 continúan **NO_VERIFICADAS**. SilentShutter no se declara funcional.

Fuentes directas: `analysis/av-cam-analysis-view.elf`, `docs/capture/shutter-trigger-chain-0x3011.md`. Detalle y clasificación: `s19-s2-domain-bridge.md` y `analysis/session19/evidence/s2-domain-bridge.json`.

## Sesion 19, ejecucion 02 — S19-02

**S19-02: PARCIAL.** El camino efectivo queda demostrado: `libBizFw2.so:0x2bf1c` llama el PLT de `MWF::ObjPin::Connect`; `UObjPin` delega con su pin base en `this+8` y no añade una regla de compatibilidad. Los wrappers de CacheMgr, ScalarMpr y MprCtrl pueden diferir su llamada con una bandera local. `TM::createLifeCycles` construye y registra el LifeCycle con vtable en `0xcc6698`, pero no se encontró un flujo de datos/ejecución desde esa instancia o su despacho observado hasta Connect. Por ello no se declara LifeCycle→Activate→Connect ni SilentShutter funcional. Detalle: `s19-lifecycle-connect.md` y `analysis/session19/evidence/lifecycle-connect.json`.

## Sesion 19, ejecucion 03 — S19-03

**S19-03: PARCIAL.** La fila `0xb4` conserva ObjId `0x35` hacia `ObjStillRecorder.in0`; `ObjStillRecorder_Create` reserva `0x148` y alcanza el constructor real `0x9178f0`, que construye `ObjActiveBase(0x2f)`, pines MWF y wrappers. Esto corrobora la clase del extremo, no una asociación recuperada de `53→constructor`. No surgió un auto-registro explícito: los 263 inicializadores de `.init_array` no apuntan a `ObjStillRecorder_*`, y no hay puntero directo de esa API en datos asignables. El registro indirecto/externo queda **NO_VERIFICADO**; `0x41920c` sólo fabrica el placeholder genérico ante lookup fallido. SilentShutter no se declara funcional. Detalle: `s19-objid53-registration.md` y `analysis/session19/evidence/objid53-registration.json`.

## Sesion 19, ejecucion 04 — S19-04

**S19-04: PARCIAL.** `ObjCamera_Create` alcanza el constructor `0x98c380`; éste y su auxiliar de pines `0x987dc6` construyen nueve salidas y no invocan `DmmCh`, `DmmAccessPLA` ni `AvbbcPhycMem`. La topología `0x0a` prueba `Camera.out0 → Effect.in0`, no un descriptor de memoria. Las asignaciones DMM verificadas (`0x15fa74`) pertenecen a la ruta Effect/PbCap y producen el par conocido raster `0x50b3f` / SDS `0xe0b00`; la SDS de `0x800` B no es píxel. Sin arista estática Camera→descriptor, unitType, handle, offset, memoria física, geometría, formato, stride, planos, colorimetría, ownership y reciclaje del YC real siguen **NO_VERIFICADOS**. Se descarta derivarlos de IMX210. SilentShutter no se declara funcional. Detalle: `s19-camera-yc-real-contract.md` y `analysis/session19/evidence/camera-yc-contract.json`.

## Sesion 19, ejecucion 05 — S19-05

**S19-05: PARCIAL.** La cadena PbCap `0x6013 → 0x1761a8 → 0x15fd50 → 0x15fa74 → 0x15ebfc` es positiva para una conversión SDF: exige holder/interfaz/selectores, conecta DataflowInfra, reserva raster/SDS nuevos y solo publica PlayData tras `0x111`; su cleanup cierra los recursos de salida. No hay evidencia positiva de que Camera.out0 suministre ese holder, los pines SDF o un descriptor compatible. Por eso los tipos DMM, geometría/formato y ownership del YC Camera, y la compatibilidad Camera→SDF→PbCap, permanecen **NO_VERIFICADOS**. La falta de una comparación de `unitType` en `0x15fd50` no acredita compatibilidad. SilentShutter no se declara funcional. Detalle: `s19-camera-effect-sdf.md` y `analysis/session19/evidence/camera-effect-sdf.json`.

## Sesion 19, ejecucion 06 — S19-06

**S19-06: PARCIAL.** `libmprctrl.so` registra el callback MPR en `0x11ba2`; FEA lo invoca en `0x450308` y luego notifica el intervalo `0xc0000001..0xc0000091`. El `EventSwitcher` posterior filtra por `targetId`/`eventId`. Aún no existe una arista estática desde `0xc0000004` a la tabla/objeto de `StillConverter`: el ID y receptor siguen siendo **INFERENCIA fuerte/NO_VERIFICADO**. `EncodeStill` sólo copia el descriptor de 0x40 B y encola; no prueba copia de píxeles, lectura final, éxito JPEG, cancelación ni liberación. SilentShutter no se declara funcional. Detalle: `s19-fea-encodestill-completion.md` y `analysis/session19/evidence/fea-callback-completion.json`.

## Sesion 19, ejecucion 07 — S19-07

**S19-07: PARCIAL.** Se resolvieron las diez filas LIRO restantes a sus entradas reales y se comprobó que son máquinas de estados con `FUN_43afdf16`/`tbb`, no trampolines vacíos. Comparten contexto, retries/cancelación y la cola de metadatos `0x9400` con la captura convencional. Adquisición física, encoder JPEG, publicación/finalización y ownership/liberación continúan **NO_VERIFICADOS**; ninguna fila recuperada aporta una marca Silent/EFCS. SilentShutter no se declara funcional. Detalle: `s19-liro-remaining-sequences.md`; siguiente: S19-08.

## Sesion 19, ejecucion 08 — S19-08

**S19-08: PARCIAL.** `FeaIf::WriteStill` (`libmpr.so:0x44f784`) empaqueta y entrega 1–2 stills asincrónicamente; `MprFileIfCore::WriteAndFlush` (`0x726138`) delega una escritura+flush al gestor de medio. MPR también expone pre-registro/lookup DCF (`0x71eafc`/`0x71eb70`) y consultas/miniaturas de reproducción. Ninguna arista estática recuperada une esas capacidades en una transacción de esta foto. JPEG válido, bytes escritos a SD, contenido DCF registrado y fotografía visible en reproducción son cuatro estados distintos y todos salvo las interfaces siguen **NO_VERIFICADOS** extremo a extremo. También siguen abiertos flush durable, error/rollback, cancelación/liberación y el consumidor de `0x3500/0x3002`. SilentShutter no se declara funcional. Detalle: `s19-dcf-playback-completion.md`; siguiente: S19-09.

## Sesion 19, ejecucion 09 — S19-09

**S19-09: PARCIAL.** Se verificó el tramo local `CameraSequenceDiadem → CameraSeqUtil → SDCom → ScalarDaemon`: StartPreview envía `0x124`; `getPreviewSequenceFrames` envía `0x127`, recibe vectores y fabrica `DeviceMemoryDiadem`; `readBuffer` mapea/copia/desmonta memoria compartida; `release` devuelve el ticket por SDCom `0x3`/parámetro 4. Eso demuestra un préstamo de bytes opacos y su devolución, no JPEG, 640×480, YC, productor físico, ownership terminal, S2, MPR ni Silent/EFCS. SilentShutter no se declara funcional. Detalle: `s19-camerasequence-sdcom.md`; siguiente: S19-10 (entrega del YC de SFRA al cliente Linux).

## Sesion 19, ejecucion 10 — S19-10

**S19-10: PARCIAL.** SFRA se verificó directamente en `av-cam.bin`: su YC entra por pines EE/Rec. La entrega Linux demostrada no es YC: ISS pide `GET_JPEG` (`0x2009/0x100`), recibe handle DMM u16 más tamaño redondeado a 128 B y lo expone mediante `pubDmmOpenUnit → /dev/mem → mmap` RW/shared; `MmapLiveViewJpeg` libera la unidad anterior. No aparece `ashmem` en las bibliotecas examinadas. No se prueban YC/raw Linux, JPEG exacto/válido, cache coherency, CameraSequence/ObjCamera, ownership final, S2/EFCS/MPR/DCF. SilentShutter no se declara funcional. Detalle: `s19-sfra-yc-linux-delivery.md`; siguiente: S19-11 (b), modos 2–5 de ObjEffect con Camera.

## Sesion 19, ejecucion 11 — S19-11

**S19-11: PARCIAL.** El byte de modo de la secuencia ObjEffect se calcula por interfaz virtual y `0x176cc6` verifica el intervalo real 2–5. Sólo 3 entra a `0x1765cc` y transmite `ObjMsg(0x3900,0x0002)`; 2, 4 y 5 retornan por error. No hay llamada a `0x15ebfc`, ni reservas DMM PbCap, ni el command-id `0x3000` de la ruta SDF conocida, por lo que no se verifica ningún buffer apto para EncodeStill/PbCap. La topología Camera→Effect no prueba que Camera ejecute este tramo. Tampoco existe arista a control físico de obturador; ningún modo evita mecánica de forma demostrada. SilentShutter no se declara funcional. Detalle: `s19-objeffect-modes-2-5.md`; siguiente: S19-12 (h).

## Sesion 19, ejecucion 12 — S19-12

**S19-12: PARCIAL.** Se aislaron las decisiones reales que preceden a la ejecución convencional: RelMgr admite o rechaza la petición en `0x4379e6a8`; el dispatcher local sólo instala CaptureStart tras guardas de retorno/estado (`0x43807d80`); `0x437df640` separa clases mediante `cfg+0x265`; y `0x437eabfc` selecciona el descriptor que `0x43b04730` ejecuta. No se recuperó un flag «mecánico/no mecánico» ni la fila `0x43edccf8` que correlacione un descriptor con CAIF/Darwin. EFCS sigue siendo selección de exposición, no obturación totalmente electrónica. SilentShutter no se declara funcional. Detalle: `s19-mechanical-shutter-decision-points.md`; siguiente: S19-13 (d).

## Sesion 19, ejecucion 13 — S19-13

**S19-13: PARCIAL.** RelMgr construye `0x3015`; el dispatcher local tiene rutas que llaman helpers de estado antes de retornar; y LIRO `0x437f22d4` limpia condicionalmente `ctx+0x754` con `0x437fbad8`, además de devolver `0/1/2/5`. No existe una arista estática que conecte esos hechos con liberación de S2, retorno idle, cancelación tras compromiso o CAIF/Darwin. Tampoco hay liberación DMM demostrada; `DmmClose` no equivale a liberar una asignación. No se verifica una ventana segura de cancelación antes de cortinas. SilentShutter no se declara funcional. Detalle: `s19-post-s2-cancellation-states.md`; siguiente: S19-14 (f).
