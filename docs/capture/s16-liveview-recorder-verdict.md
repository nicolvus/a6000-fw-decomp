# Veredicto de integración — sesión 16: activación del grabador y compatibilidad del YC

Alcance: análisis estático exclusivo de `libObj.so`/`libmpr.so`/`dmm.ko` fw 3.21 (Sony A6000). **No se afirma que SilentShutter funcione.** No hay cámara conectada ni flasheo. Clasificación: VERIFICADO / INFERENCIA / HIPÓTESIS / NO VERIFICADO / DESCARTADO.

Fuentes íntegras: `docs/capture/s16-main-delivery-sequences.md` (principal), `docs/capture/s16-claude-effect-control.md` + `analysis/s16-claude-topology-audit.json` + `analysis/s16-claude-effect-mode1.json` (Rama A, Sonnet 5 medio), `docs/capture/s16-codex-camera-yc.md` + `analysis/s16-codex-camera-yc.json` + `docs/capture/s16-codex-fea-completion.md` (Rama B, Codex gpt-5.6-terra medio). Cruce completo en `analysis/s16-liveview-recorder-crosscheck.json`.

## 1. Configuración real de esta sesión

Un Claude principal (hilo propio, Sonnet 5, sin cambio de modelo/esfuerzo), un subagente Claude (Sonnet 5, esfuerzo medio, vía `Agent`) y un agente Codex (`codex-cli 0.162.1`, `gpt-5.6-terra`, `model_reasoning_effort=medium`, confirmado por llamada de prueba previa — respuesta "OK", 831 tokens — antes del trabajo real). **Ningún agente delegó a un tercero** en esta sesión (a diferencia del incidente de sesión 15, que sí se produjo y fue corregido entonces). Máximo de agentes respetado.

## 2. Verificación cruzada de al menos un hallazgo crítico por rama

- **Rama A** (dos escritores de `EffectInternalMode=1` por RTTI): verificado de forma independiente por el principal leyendo bytes crudos del binario — las cadenas mangled `N9OBJEFFECT25ExecCmdAppFaderEfctEndEvtE` (file-offset `0xbd69fa`) y `N9OBJEFFECT22SequencePinDeliverBaseE` (file-offset `0xc0c1e8`), y los words de vtabla en `0xfe6050`=`0x154991` y `0xfeabd4`=`0x1e069d`, coinciden exactamente. **CONFIRMADO.**
- **Rama B** (`FeaIf::EncodeStill` solo encola, no espera finalización): verificado de forma independiente por el principal desensamblando `libmpr.so` (mismo SHA-256) en `0x44f834-0x44f8e8` — símbolo real `FeaIf::EncodeStill(MprIf::EncodeStillParam*)`, estructura de reserva de slot, rama de error (`AsyncApiDone`, código `9`) y rama de éxito (copia de `RegionInfo` + llamada a `vtable+0x20`) coinciden instrucción por instrucción. **CONFIRMADO.**

No se encontraron contradicciones entre las tres fuentes. La única discrepancia (213 vs 318 sitios de `createTopology`/`destroyTopology`) es una corrección de cifra declarada explícitamente como no resuelta por la propia Rama A, no una contradicción de hallazgos.

## 3. Hallazgos nuevos por rama

**Principal**: un segundo manejador gemelo (ELF `0x1f25d8`) confirma, de forma independiente a `0x1e9880`, que `EffectInternalMode==1` + submensaje `0x1011` → `ObjMsg(0x3900,0x600d)`; revela una familia de mensajes hermanos no catalogada (`0x6051`, `0x6052`, `0x6053`); y el decompilado de la factoría de secuencias (`0x17b004`) muestra que **solo `0x6013` instancia un objeto de secuencia con estado** (`0xd4` B, constructor `0x1861a8`) — `0x600d` nunca aparece en esa factoría, se postea como mensaje plano sin objeto de estado.

**Rama A (Sonnet 5)**: corrige el bloqueo de sesión 15 "sin escritor de modo 1 localizado" — existen **dos escritores dinámicos reales** (`ExecCmdAppFaderEfctEndEvt`, `SequencePinDeliverBase`), identificados por RTTI real, no por heurística. Recuento reproducible de **213** sitios de `createTopology`/`destroyTopology` (no 318). Descubrimiento de una **segunda fila con `StsId=6`** (`0xb4`: objeto 53 → StillRecorder, mismo destino que `0x2a`), abriendo la hipótesis de arbitraje vía `StsViewer` compartido. Revisión del gestor de pines de ObjEffect: sin guard de exclusión Camera/Recorder.

**Rama B (Codex)**: cadena completa `MprIf::EncodeStill → FeaIf::EncodeStill` con desensamblado real y hashes de binario declarados; identificación de `StillConverter` como candidato (INFERENCIA fuerte) a receptor de `CBID_ENCODE_STILL`; confirmación de que `DmmClose` no libera (solo decrementa el contador `open`); descarte explícito de atribuir a Camera el formato/dimensiones del YC por ausencia de evidencia directa.

## 4. Respuestas a los criterios de éxito (sesión 16, §5 del encargo)

1. **¿Un modelo/comando conecta `Effect.out1` con Recorder?** Solo `ModelPbCap` confirmado (re-verificado); el 82%/97% de los sitios restantes construyen el id dinámicamente — no se puede confirmar ni descartar otro. **NO VERIFICADO.**
2. **¿`Effect.in0` recibe YC de Camera?** Sí, a nivel de topología estática (fila `0x0a`, Camera.out0→Effect.in0). **VERIFICADO** (estructura); el contenido real del YC sigue sin recuperarse.
3. **¿Existe una secuencia alcanzable que responda a REQ_DELIVER?** Sí: modos 2–5 (vía `0x6013`, instancia Sequence real) y modo 1 (vía `0x600d`, mensaje plano, probablemente sin imagen). **VERIFICADO** la existencia; **NO VERIFICADO** que sean alcanzables desde Live View/disparo.
4. **¿SDF produce buffers compatibles con PlayData?** Demostrado solo para el par ya construido por ObjEffect en PbCap (`0x50b3f`/`0xe0b00`); no para el tipo del YC de Camera. **NO DEMOSTRADO** para Camera.
5. **¿El buffer permanece válido durante EncodeStill?** `FeaIf::EncodeStill` solo encola (copia descriptor, no raster) y retorna antes de confirmar lectura; no se encontró ruta de liberación posterior. **NO VERIFICADO**, riesgo documentado desde sesión 13 sin resolver.
6. **¿El grabador puede continuar hacia Pool y MPR?** Sin cambios respecto a sesiones previas (ya verificado en sesiones 11-12 para el flujo estándar). No evaluado de nuevo esta sesión por no ser el foco.

## 5. Veredicto A frente a E

**Sin cambio de orden: A > E > E2.** Esta sesión no demuestra ni descarta la arquitectura E. Aporta:
- Una pieza que antes faltaba (escritor real de `EffectInternalMode=1`), pero sin conexión a Live View.
- Un candidato nuevo y más prometedor para la pregunta de exclusión (el `StsViewer` compartido por `StsId=6`, no ObjEffect ni TopologyManager).
- Evidencia que debilita (no descarta) al modo 1 como portador de imagen, por ausencia de instanciación de Sequence/DMM/SDF en su despacho — si se confirmara, el modo 1 dejaría de ser relevante y el foco seguiría en los modos 2–5, que siguen sin escritor conocido desde EE.

No hay evidencia estática que demuestre ni descarte que un frame de `Live View` pueda atravesar `ObjEffect` y llegar a `EncodeStill` sin iniciar la captura mecánica. El bloqueo de fondo (ningún modelo de disparo fotográfico conocido activa la ruta) persiste.

## 6. Siguiente bloqueo técnico específico y comprobable

Decompilar `GetStsViewer` (ELF `0x4294cc`) y `ObjIf::ConnectPin` (ELF `0x41c25e`) para determinar si el `StsViewer` compartido por `StsId=6` arbitra entre las filas `0x2a` y `0xb4`; y trazar el llamador indirecto (vía vtabla) de `ExecCmdAppFaderEfctEndEvt` y `SequencePinDeliverBase` para establecer si son alcanzables fuera de fundidos de efecto/edición de UI.

## NO VERIFICADO (pendiente, declarado explícitamente)

Alcanzabilidad de los dos escritores de modo 1 desde EE/disparo; otro creador de la fila `0x2a` aparte de `ModelPbCap`; combinación `0x0a+0x07+0x2a` en una misma secuencia; semántica de `0x6051/0x6052/0x6053`; `Execute()`/`BeginExecCommand` real de la Sequence `0xd4`B; consumidor exacto y momento de liberación tras `CBID_ENCODE_STILL`; `unitType`/formato/geometría real del YC de Camera.
