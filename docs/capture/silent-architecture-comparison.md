# Comparación de arquitecturas SilentShutter (síntesis, 2026-10-16)
Fuentes: A (`mpr-dcf-recording.md`), B (`sfra-mpr-buffer-bridge.md`), C (`shutter-trigger-state-machine.md`), `sfra-linux-client.md` (Claude), `silent-integration-design.md`. Las líneas D, E, F y C2 se lanzaron pero Codex agotó su límite sin entregar: **sus preguntas siguen abiertas** (ver final). Nada aquí está ejecutado ni probado en cámara.

## Hechos que condicionan el diseño
| Hecho | Etiqueta | Fuente |
|---|---|---|
| La foto normal llega a Linux como mensaje 0x1006 con handles DMM ya codificados (main, thumb, screennail, EXIF source) | VERIFICADO | A, Stage_Notify 0x437efe78 |
| EXIF nuevo exige miniatura JPEG válida y área de reserva escribible; MPR no la genera | VERIFICADO | A, libmpr 0x38b064 |
| SFRA/GET_JPEG entrega sólo {handle DMM u16, tamaño redondeado a 128 B}; sin EXIF/thumb/scn | VERIFICADO | B + `0x439a282c` |
| El handle SFRA sale del ring y pasa a propiedad del cliente; los READY sobrantes se liberan en cada GET_JPEG | VERIFICADO | `0x439a23d0`, `0x439a235c` |
| ISS (Linux) publica directamente en las colas SFRA (0x1670464 / 0x167046a) | VERIFICADO | `iss-scalarif.json` |
| Linux no tiene codificador/decodificador JPEG; sólo SdfCh paint/resize/copy | VERIFICADO (imports) | `nm -D -u libObj.so` |
| libObj convierte memHandle→puntero con DmmOpen/DmmReuseAndOpen (+mmap) en el camino 0x1006→StillInfo 0x6b0 | VERIFICADO | A |
| Divergencia candidata de secuencia: `0x437eabfc` (desde `0x437df338`); el índice de fila lo decide una cadena de condiciones (ver abajo) | VERIFICADO | C + decompilado propio |
| Enlace 0x3011 (RelMgr→CamUser 0x40193) → CaptureStart 0x437df640 | NO VERIFICADO | C |
| Productor del YC de SFRA; si el path SFRA se abre en modo foto sin Wi-Fi | NO VERIFICADO | F no entregó |
| Evento que registra la foto en reproducción; EXIF mínimo | NO VERIFICADO | A, E no entregó |

### Selector de fila `0x437eabfc` (decompilado propio, `analysis/ghidra/liro-seqselect.json`)
Tabla base GOT[0x44022934]=0x43edccf8 (filas de 20 B = 5 palabras; **la tabla está a cero en la imagen**: la rellena el constructor estático `0x437ebed8`; cada fila = delegado a una máquina de estados `Image*→estado`, p. ej. fila 8 = 0x43b1be36; ver `capture-stage-reuse.md`). Índice = f(captura): `+0x4b70==0` y `+0x54a5==0`: si `(+0x70)-8<6` y `+0x1d8==0` → fila `+0xb4` (9); si no, según `+0x1e0` (7 → 10, o 0xd si `+0x1d8≠0`; 0x17 → 8; otro → 8, o 0xb si `+0x1d8≠0`). `+0x54a5≠0` (ráfaga en curso): `+0xa0` (8) o `+0xf0` (12) según `+0x54a8`. `+0x4b70==7`: `+300`. Otros `+0x4b70`: `+0x118`. **INFERENCIA**: la fila 8 es la captura JPEG normal de una imagen; 10/0xd/0xb/9 variantes (RAW/ráfaga/intervalo). Nada se sabe de las cinco palabras.

## Arquitecturas
| Criterio | A — LIRO | B — Linux/MPR | C — Híbrida |
|---|---|---|---|
| Idea | Fila/descriptor Silent tras 0x437eabfc: YC del flujo continuo → etapas de codificación existentes (main+thumb+scn+EXIF) → Stage_Notify | Disparo → Linux pide GET_JPEG → adapta buffer + fabrica thumb/EXIF → MprIf::WriteStill | LIRO detecta/coordina el disparo Silent y entrega el YC/JPEG; Linux usa MPR |
| Miniatura/EXIF | Reutiliza etapas Stage_THMEnc/SCNEnc/EXIF existentes (INFERENCIA, falta D) | **Bloqueante**: Linux no tiene codificador; habría que codificar thumb en LIRO igualmente | Igual que A para thumb |
| Handles/propiedad | Los crea LIRO como en una foto normal (contrato conocido) | Hay que transferir/copiar handle SFRA a StillInfo 0x6b0 y retener | Mixto |
| Ciclo mecánico | Se evita decidiendo en 0x437eabfc (HIPÓTESIS); riesgo de estados (S2Handler, contadores) | Lo evita porque no entra en CaptureManager, pero el disparador seguiría arrancando la captura normal salvo que se intercepte | Depende de interceptar 0x3011 |
| Estado del botón / vuelta a normal | Conserva RelMgr; requiere cancelación/finalización propias | El flujo normal del botón seguiría corriendo en paralelo (conflicto) | Intermedio |
| Evidencia que falta | Contenido de la tabla, qué etapas aceptan YC de LV, EXIF | Todo el tramo thumb/EXIF/reserva, evento de reproducción | Ambos |
| Veredicto provisional | **Más prometedora (INFERENCIA)** | Menos viable por thumb/EXIF y por el conflicto con la captura normal | Alternativa si A no admite YC de LV |

## Mínimo de cambios hipotéticos (arquitectura A)
1. Ajuste Silent leído y congelado en la petición (cfg+0x264/0x265, ya existente en el selector de captura de `silent-capture-config-folded.json`).
2. Rama en `0x437eabfc`: si Silent → devolver una fila nueva (5 palabras) en lugar de las de la tabla.
3. Fila nueva = lista de etapas: (a) capturar un frame YC coherente del flujo de LV (retener el SDS/buffer; **NO VERIFICADO** de dónde sale), (b) codificar main (EncodeJpeg_MainYC), thumb (THMEnc), screennail (SCNEnc), EXIF, (c) Stage_Notify con StillInfo válido.
4. Cancelación/finalización propias; no emitir CAIF ni SetMode de captura; no tocar GPIO.
5. Vuelta a LV sin residuos (S2Handler, contadores 0x43ed4cf8/f0).

## Preguntas abiertas (prioridad)
1. (D) Tabla RESUELTA a nivel de filas (ver `capture-stage-reuse.md`); falta etiquetar los estados de la fila 8 (0x43b1be36) y ver cuáles aceptan un YC de LV.
2. (F) Origen del YC en SFRA `pin` y si puede retenerse un frame sin cambiar de modo.
3. (C2) Camino 0x3011 → CaptureStart.
4. (E) Evento de catálogo/reproducción y EXIF mínimo.

## Actualización (ronda 3)
- CORREGIDO (sesión 10, revisado en 11 por `objstillrecorder-mode4.md`): la cadena `recordStillImage → 0x930464 → MakeWriteStillImage + WriteStill` era errónea. `0x930464` es ObjConverter (export/subida); el mensaje 0x1027 lo recibe ObjStillRecorder (`0x929ca0`, modo `+0x128=4`). Ver apéndice sesión 10.
- Cambio de recomendación provisional: **C (híbrida) pasa a ser la candidata principal** si se confirma que el registro de imagen acepta un JPEG de SFRA + miniatura generada aparte (p. ej. un segundo `GET_JPEG` a 320 de ancho no vale: SFRA solo da JPEG a la resolución del path; la miniatura 160×120 requiere codificación adicional). A sigue siendo viable pero con más cambios en LIRO.
- Cuestión abierta crítica: quién produce la miniatura 160×120 y el screennail (¿otro path SFRA de 320×240, o SDF desde LIRO?).

- Sesión 9 P1: recordStillImage/GetFileImage NO escribe en SD (genera archivo en memoria + msg 0x3a48). C híbrida pierde la ventaja "escritura incluida"; A (0x1006→RecordStill→WriteStill) sigue siendo la única ruta a DCF demostrada. Ver record-still-image-route.md.

## Apéndice sesión 10
- B (MakeWriteStillImage como constructor) queda rebajada: GetFileImage es TRANSFERENCIA (ObjConverter), sin interfaz de persistencia.
- Mejor candidata (INFERENCIA): inyectar vía `0x1027` modo 4 en ObjStillRecorder, que reutiliza `RecordStill::Execute` nativo. Falta verificar la fuente de imagen en modo 4 y su llegada a WriteStill.

## Apéndice sesión 11
- `0x1027` NO inyecta imagen (solo arma el grabador). La opción "C híbrida por 0x1027" queda DESCARTADA tal como estaba planteada.
- Nueva candidata C′: registrar la imagen en el Pool mediante `InfraStillPool::RegisterImage` (mensaje `0x2008/0x1000`, ELF `0x9328b4`) y dejar que `Execute`/`RecordStill`/`WriteStill` la graben. Evidencia: parser `0x940c34`/`0x940508` (tabla de handles DMM `u16`, `StillInfo` por `MakeStillInfo`, `MakeWriteStillImage` interno). Pendiente: layout `0x100b`, quién genera miniatura/EXIF, y cómo disparar `Execute` sin captura mecánica.
- A (LIRO nativa) sigue siendo la referencia de extremo a extremo; C′ es la única variante híbrida con evidencia de código.

## Apéndice sesión 12
- La entrada nativa de imagen al grabador es un **frame YC** (orden `0x10000005`, `PlayData`), no un JPEG: `MprIf::EncodeStill` produce JPEG principal, miniatura, screennail y maker note. Un JPEG de SFRA no es entrada válida de `Execute`.
- C′ (registrar JPEG en el Pool) queda debilitada: exigiría fabricar miniatura, screennail, maker note y fuente EXIF (entradas 0,1,4,9,10 del `0x100b`), que hoy produce MPR.
- Nueva candidata **E**: alimentar `Execute` con un YC de Live View (handle+unitType+phys+canvas) y dejar que MPR/Pool/`RecordStill`/`WriteStill` hagan el resto. Evidencia: contrato de entrada y salida leídos en código. Sin demostrar: remitente de la orden, formato YC aceptado, `mediaSelectMode != None`, resolución del YC de Live View, estado de MPR.
- A (LIRO nativa) sigue siendo la única demostrada de extremo a extremo. Recomendación: seguir con A como referencia y estudiar E como sustituto de la fase JPEG, no de la adquisición.

## Sesión 13 — E reevaluada
- E existe como **mecanismo nativo** (PbCap): `RECORD_IMAGE_CMD modo 0` → pin YC → `Execute` → `EncodeStill` → Pool → `WriteStill` → DCF. Entrega fotos de reproducción de vídeo (cadenas 1920×1080/640×360/640×480). Es la única ruta «fotograma electrónico → JPEG → tarjeta» demostrada sin LIRO, pero **parte de reproducción**.
- Falta para disparo: (1) productor de YC del EE en el pin YC del recorder; (2) disparar `RECORD_IMAGE_CMD` desde la secuencia de disparo en lugar de la captura mecánica; (3) mantener el buffer vivo. Todo NO VERIFICADO.
- Criterios: compatibilidad YC = plausible/no probada; subsistemas = Linux (libObj) sin LIRO; miniatura/EXIF = los genera EncodeStill; reproducción = no verificada (sí en PbCap nativo); botón = requiere interceptar la captura normal, sin localizar el punto.
- Recomendación: A sigue siendo la única demostrada de extremo a extremo; E es la candidata a investigar si se acepta resolución reducida. C′ queda descartada como prioridad.

## Sesión 14 — comparación A / E / E2
| Criterio | A (LIRO nativa) | E (reutilizar PbCap/EncodeStill) | E2 (puente ObjScalar) |
|---|---|---|---|
| Conexiones nuevas | ninguna | topología `0x2a` en disparo (`TopologyManager`, modelo nuevo/parcheado) + modo de ObjEffect + ruta de entrada Camera→Effect o1 | ObjScalar↔recorder sin topología existente |
| Productor YC disponible | LIRO | ObjEffect (solo con entrada de Player demostrada) | cliente externo (ScalarDaemon, Wi-Fi) |
| Formatos y handles | nativos | unidades `0x50b3f/0xe0b00` fabricadas por ObjEffect (VERIFICADO) | handles del cliente (`allocShare`) |
| Estabilidad del buffer | LIRO (`ycc_freeze`) | copia dedicada del productor; `EncodeStill` asíncrono | `allocShare` retiene |
| Estados de cámara/reproductor | captura | modo interno de ObjEffect y estado de ObjRenderer en disparo: NO VERIFICADO | Paint (edición) |
| Metadatos | LIRO + MPR | EncodeStill/Effect (`0x1041` desde el mensaje de entrada) | del cliente |
| Selección del medio | nativa | `MediaMgr` ≠ None, CntMgr por topología | idem |
| Calidad/resolución | completa | ≤1920×1080 (destino de PbCap) | la del cliente |
| Independencia mecánica | no (secuencia mecánica) | **no demostrada** (dependencias de Effect/Camera) | no |
| Complejidad y riesgo | ya existe | alta (varios subsistemas Linux) | alta y requiere Wi-Fi |

**Orden de sustento: A > E > E2.** A es la única demostrada. E tiene mecanismo nativo y cadena identificada pero faltan tres piezas: (1) crear `0x2a` en disparo, (2) que ObjEffect sirva `REQ_DELIVER` con Camera, (3) el tipo/geometría del YC del visor. E2 queda sin sustento (el `0x1027` solo arma y hace eco; no hay topología Scalar→recorder).

## Sesión 15 — investigación en paralelo, orden sin cambios

Detalle: `docs/capture/liveview-encodestill-parallel-verdict.md`, `analysis/liveview-encodestill-crosscheck.json`. Investigación en tres fuentes independientes (investigador principal, subagente Claude Sonnet 5, Codex `gpt-5.6-terra`) que no se contradijeron.

Piezas nuevas que refuerzan (sin resolver) a E: identidad VERIFICADA de ObjCamera (productor puro, 9 pines de salida, ninguno de entrada); estructura real de `EffectInternalMode` (holder indirecto, escritor `0x173158` localizado, modos `{1,2,3,4,5}` con acción real); tamaños exactos de los extents DMM (`0xe0b00`=`0x800` B confirma que es solo cabecera, nunca el raster).

Los tres bloqueos de sesión 14 **persisten intactos**: (1) ningún modelo de disparo conocido crea `0x2a` (búsqueda de 318 sitios de llamada, no exhaustiva); (2) no se encontró ningún escritor de `EffectInternalMode` activado desde `ModelBootEE`, es decir, Effect no parece entrar en un modo relevante durante Live View en absoluto; (3) el `unitType`/formato del YC de Camera sigue sin recuperarse.

**Orden de sustento sin cambios: A > E > E2.** E no se declara viable ni se descarta.

## Sesión 16 — escritor real de modo 1, segunda fila StsId=6, orden sin cambios

Detalle: `docs/capture/s16-liveview-recorder-verdict.md`, `analysis/s16-liveview-recorder-crosscheck.json`. Misma configuración de tres fuentes (principal + Sonnet 5 + Codex `gpt-5.6-terra`), sin incidentes de delegación esta vez.

Piezas nuevas: (1) corrección del bloqueo de sesión 15 "sin escritor de `EffectInternalMode=1`" — existen dos escritores dinámicos reales (`ExecCmdAppFaderEfctEndEvt`, `SequencePinDeliverBase`, identificados por RTTI), pero ninguno conectado a Live View en la evidencia revisada; (2) segunda fila con `StsId=6` (`0xb4`, objeto 53 → StillRecorder, mismo destino que `0x2a`) — nuevo candidato de arbitraje vía `StsViewer` compartido, en vez de ObjEffect/TopologyManager; (3) la factoría de secuencias (`0x17b004`) muestra que solo `0x6013` instancia una Sequence con estado — `0x600d` (modo 1) se postea como mensaje plano, sin evidencia de transporte de imagen; (4) recuento reproducible de 213 sitios de `createTopology`/`destroyTopology` (corrige la cifra de 318 citada en sesión 15, único creador literal de `0x2a` sigue siendo `ModelPbCap`).

Los bloqueos de fondo **persisten**: ningún modelo de disparo fotográfico conocido crea `0x2a`; sin conexión entre los nuevos escritores de modo 1 y `ModelBootEE`; `unitType`/formato del YC de Camera sigue sin recuperarse.

**Orden de sustento sin cambios: A > E > E2.** E no se declara viable ni se descarta.

## Sesión 17 — se debilita el bloqueo de control de E; se añade arquitectura P (CameraSequence pública), orden sin cambios de fondo

Detalle: `docs/capture/s17-parallel-research-verdict.md`, `analysis/s17-parallel-crosscheck.json`, `docs/capture/s17-a-e-p-architecture-comparison.md`. Configuración: principal + 2 Claude Sonnet 5 (medio solicitado) + 2 Codex `gpt-5.6-terra` (medio, confirmado). Sin incidentes de delegación.

Piezas nuevas sobre E: (1) cierra el bloqueo "decompilar `GetStsViewer`/`ConnectPin`" de sesión 16 — ambos viven en `libMWF.so`, no en `libObj.so`; `ObjPin::Connect` **no arbitra** por ocupación de pin (solo valida tipo/dirección), y el `ObjStatusViewer`/`StsViewer` es un agregador de notificación, no un cerrojo — esto **debilita** la hipótesis de arbitraje activo entre `0x2a`/`0xb4` y, a la vez, **confirma que no hay colisión estructural entre `Effect.in0` (Camera) y `Effect.out1` (Recorder)**, que son pines distintos; (2) la única colisión real sigue siendo `0x2a` vs `0xb4` (mismo pin de destino escalar en StillRecorder); (3) el selector de captura LIRO `0x437eabfc` no tiene marca de modo Silent/EFCS, y su tabla de filas es BSS/no recuperable estáticamente (explica el bloqueo, no lo resuelve); (4) la Sequence `0x6013` no compara `unitType` en sus guardas de entrada visibles.

**Nueva arquitectura P (CameraSequence, API Android pública de Sony)**: verificada como real en el firmware local (no solo citada de fuentes externas), con mejor sustento documental/binario que E para la pregunta estrecha "¿existe una API accesible de JPEG electrónico a 640×480?", pero **sin ningún enlace al botón físico S2** — el único código real que intercepta S2 (PMCADemo) usa captura convencional. Ver comparación completa en `s17-a-e-p-architecture-comparison.md`.

Los bloqueos de fondo de E **persisten**: ningún modelo de disparo fotográfico conocido crea `0x2a` ni activa los modos 2-5 de `EffectInternalMode`; consumidor real de la cola `0x40193`/`0x3011` no localizado; `unitType`/formato del YC de Camera sigue sin recuperarse; receptor real de `CBID_ENCODE_STILL` sin confirmar.

## Sesión 18 — inventario Sony OSS sin aporte directo; blockers de E/control caracterizados con más precisión, orden sin cambios

Detalle: `docs/capture/s18-parallel-research-verdict.md`, `analysis/session18/main/s18-parallel-crosscheck.json`, `analysis/session18/main/sony-oss-inventory.md`. Configuración: principal + 4 Claude Sonnet 5 (medio solicitado, 2/4 confirmados, 1/4 "bajo" autoinformado — repite patrón de sesión 17) + 4 Codex `gpt-5.6-terra` (medio en los flags de lanzamiento). Sin incidentes de delegación (8/8 agentes lo confirman).

**Fuentes oficiales Sony OSS (kernel Linux 3.0.27 + utilidades genéricas) no aportan evidencia directa sobre FEA/DMM/el pipeline fotográfico** — confirmado por ausencia, de forma independiente y sin contradicción, por el principal, Codex G y Codex H. Sirven solo como contexto de plataforma (SoCs CXD propios, `ashmem` como mecanismo de memoria compartida real en esta versión de kernel, FAT/VFAT real para el medio extraíble).

Piezas nuevas sobre el control de E: (1) el inicializador LIRO `0x437EBED8` cierra metodológicamente el bloqueo "tabla BSS irrecuperable" de sesión 17 (se resuelve leyendo el inicializador, no la tabla en reposo) — aplicado a la tabla del selector de captura, **no** a la tabla de topología de `libObj.so` (que ya era `.rodata` estática; Claude D confirma que la técnica no tiene equivalente ahí); (2) confirmado con evidencia dura que `LifeCycle` real (`libObj.so`) y el trampolín único de LIRO son clases/mecanismos distintos, sin puente verificado; (3) el blocker "¿quién llama a `Connect()`?" se reduce de "todo el stack" a 5 bibliotecas concretas (Claude A), sin cerrarse.

**Corrección de sesión 17 (Claude B)**: el puente `CameraSequence→ScalarDaemon` usa una librería propia `libsdcom.so` ("SDCom"), no Binder como se documentó entonces — Binder solo aparece en el tramo de cámara convencional. No cambia el veredicto sobre P (sigue sin enlace a S2).

Los bloqueos de fondo **persisten, ahora mejor delimitados**: el consumidor real de la cola `0x40193`/`0x3011` se acerca un nivel (dominio local `0x100..0x207` identificado por Claude C, con llamador real `0x43807f4c`), pero el puente entre ambos dominios sigue sin probarse — es el bloqueo más concreto de toda la investigación hasta ahora; `unitType`/formato del YC de Camera caracterizado con más detalle (contrato raster+SDS) pero sin resolver; receptor real de `CBID_ENCODE_STILL` sin confirmar.

**Orden de sustento sin cambios: A > E > P ≈ E2.**

**Orden de sustento: A > E > P ≈ E2.** E no se declara viable ni se descarta; su bloqueo de control se debilitó, sus bloqueos de datos y disparo persisten. P se añade como referencia pública mejor documentada que E, sin reemplazarla por falta de enlace al botón físico.
