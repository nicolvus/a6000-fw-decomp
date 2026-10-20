# Veredicto de integración — sesión 17: control E, CameraSequence (P), YC/SDF y FEA/DCF

Alcance: análisis estático exclusivo. **No se afirma que SilentShutter funcione.** No hay cámara conectada ni flasheo. Clasificación: VERIFICADO / INFERENCIA / HIPÓTESIS / NO VERIFICADO / DESCARTADO.

Fuentes íntegras: `docs/capture/s17-main-s2-integration.md` (principal), `docs/capture/s17-claude-a-topology.md` + `analysis/s17-claude-a-topology.json` (Claude A), `docs/capture/s17-claude-b-camerasequence.md` + `analysis/s17-claude-b-api-native-flow.json` (Claude B), `docs/capture/s17-codex-c-sdf-yc.md` + `analysis/s17-codex-c-yc-contract.json` (Codex C), `docs/capture/s17-codex-d-fea-lifetime.md` + `analysis/s17-codex-d-fea-callback.json` + `docs/capture/s17-codex-d-dcf-crosscheck.md` (Codex D).

## 1. Configuración real de esta sesión

Un Claude principal (hilo propio), dos subagentes Claude (vía `Agent`) y dos agentes Codex (`codex-cli 0.162.1`, vía Bash directo al binario, evitando el alias `danger-full-access`). **Discrepancia de esfuerzo detectada y declarada, no ocultada**: se solicitó explícitamente `effort: medium` a ambos subagentes Claude y `model_reasoning_effort=medium` a ambos Codex. Codex C y Codex D confirmaron `gpt-5.6-terra`/medium (verificado con llamada de prueba previa — respuesta "OK"). **Claude A no reportó su esfuerzo explícitamente; Claude B reportó explícitamente "esfuerzo de razonamiento bajo"**, contradiciendo el parámetro solicitado (`medium`). No se sustituyó esto en silencio: se señala aquí como bloqueo de proceso. Máximo de agentes respetado (2 Claude + 2 Codex). **Ningún agente delegó a un tercero** (todas las ramas confirmaron explícitamente no haber usado `Agent` ni lanzado procesos adicionales).

## 2. Verificación cruzada de al menos un hallazgo crítico por rama (por el principal)

- **Claude A** (`MWF::ObjPin::Connect`, ELF `libMWF.so` `0x29588`, no comprueba ocupación previa del pin de destino): verificado por desensamblado directo (`llvm-objdump`) de esa dirección — la secuencia real de comparaciones (`cmp r1,#0`, `cmp r1,r0`, comparación de `+4` "kind", comparación cruzada de `+0xc` "dirección" con patrones 1/2/0) coincide instrucción por instrucción con el pseudocódigo citado. **CONFIRMADO.**
- **Claude B** (`libcameraex_jni.so`/`libcameraex_client.so` reales en el firmware; `libScalarDaemon.so` contiene `SCALARDAEMON::SystemEventIssuerCameraSequence`/`CommandProcessorFactoryCameraEx`): verificado con `find`+`nm -D` directos sobre los binarios del árbol `fw321` — los tres archivos existen y los símbolos exactos citados aparecen en la tabla dinámica real. **CONFIRMADO.**
- **Codex C** (factoría `0x17b004` compara `0x6013` y llama al constructor en **ELF `0x1761a8`**, no `0x1861a8` como citaba el encargo): verificado por desensamblado directo — `movw r3,#0x6013` en `0x17b01e`, `beq 0x17b086`, `movs r0,#0xd4`, `bl 0x1761a8` en `0x17b08e`. **CONFIRMADO**, y la corrección de direccionamiento de Codex C es correcta.
- **Codex D** (`MprIf::SetCallbackFunc` en `libmpr.so` `0x71f7b8`; `FeaIf::MprIfCallbackPoint` en `0x4502e8`): verificado con `nm -D` directo sobre `libmpr.so` — ambos símbolos reales aparecen exactamente en esas direcciones (con bit Thumb +1). **CONFIRMADO.**

No se encontraron contradicciones entre las cinco fuentes (principal + 4 ramas).

## 3. Hallazgos nuevos por rama

**Principal**: decompilado completo del selector `0x437eabfc` (árbol de decisión de 4 niveles sobre campos de la petición de captura, nunca visto completo hasta ahora); confirmación de que la tabla `0x43edccf8` es BSS/cero en la imagen estática (explica, no solo asume, por qué su contenido no es recuperable estáticamente); localización por desensamblado directo (no por referencias de Ghidra, que fallaban) de los dos callers reales de `0x43809ed8` (instalador del callback `CaptureStart`) — ninguno referencia literalmente `0x3011` ni `0x40193`, reduciendo pero no cerrando el bloqueo del consumidor de la cola.

**Claude A**: corrige una confusión de direccionamiento Ghidra-VA-vs-ELF heredada del propio encargo (`GetStsViewer` real es ELF `0x4184cc`, no `0x4294cc`). Hallazgo central: `ConnectPin`/`ObjPin::Connect`/`ObjStatusViewer` **no están en `libObj.so`** sino importados de `libMWF.so`. Lectura completa de `ObjPin::Connect`: **no hay ningún arbitraje de ocupación de pin** — el `ObjStatusViewer` ("StsViewer") es un agregador de notificación, no un cerrojo. `GetStsViewer` es un *get-or-create* por `sts_id` sobre un mapa del `TopologyManager`; confirma que `0x2a` y `0xb4` comparten el mismo objeto pero sin mecanismo de exclusión activa — la única restricción real es estructural (el campo "pin conectado" es un puntero escalar, no una lista).

**Claude B**: verificación local (no solo del issue público) de que `CameraSequence`/`CameraEx`/`DeviceBuffer` son reales en el firmware A6000 (`libcameraex_jni.so`, `libcameraex_client.so`), con backend Binder estándar de Android y enlace concreto a `libScalarDaemon.so`. Lectura directa del código real de PMCADemo: `onShutterKeyDown` usa `takePicture()` convencional, **no** `CameraSequence`. No existe bytecode Java/DEX en el proyecto para verificar `PREVIEW_FRAME_FORMAT=256` contra `ImageFormat.JPEG`.

**Codex C**: corrige la dirección del constructor de la Sequence `0x6013` (ELF `0x1761a8`, no `0x1861a8`); identifica el candidato a `BeginExecCommand` (`0x15fd50`, `SequencePinDeliverExecWriteStillCmd`) con sus tres guardas de entrada reales (ninguna de ellas compara `unitType`); reconstruye la geometría real (selector virtual 3 del holder, clases de tamaño 640×360/640×480/1920×1080) y el contrato completo de `PlayData` (`0x15ebfc`, condicionado a resultado `0x111`).

**Codex D**: localiza la API real de registro de callback FEA (`MprIf::SetCallbackFunc`, `FeaIf::MprIfCallbackPoint`) y el rango de IDs de callback (`0xc0000001..0xc0000091`), con el literal `0xc0000004` como candidato (no confirmado) a `CBID_ENCODE_STILL`; confirma que ningún liberador de las unidades DMM originales ni de la copia SDF fue localizado tras `EncodeStill`.

## 4. Respuesta a los cuatro criterios de éxito (sesión 17, §10 del encargo)

1. **Control: ¿Camera → Effect → Recorder alcanzable?** `Effect.in0` (Camera) y `Effect.out1` (Recorder) son pines distintos sin colisión estructural entre sí (Claude A). La única colisión estructural real es entre `0x2a` y `0xb4` (mismo pin de destino escalar en StillRecorder). **VERIFICADO que no hay bloqueo de `ObjPin::Connect`**; **NO VERIFICADO** que el modo interno de `ObjEffect` permita servir `out0` (Renderer/LV) y `out1` (Recorder) a la vez — bloqueo de fondo sin cambios.
2. **Datos: ¿YC de Camera convertible a formato válido para EncodeStill?** Codex C demuestra la ruta completa para PbCap (SDF → raster `0x50b3f` + SDS `0xe0b00` → PlayData), sin ninguna comparación de `unitType` visible en el `BeginExecCommand` de la Sequence `0x6013` — es decir, **no hay guard explícito que lo impida**, pero tampoco evidencia de que el holder/contrato de Camera produzca lo que esa Sequence espera. **NO VERIFICADO** en ningún sentido.
3. **Alternativa pública: ¿CameraSequence es un camino más corto?** Mejor sustento documental/binario para "JPEG electrónico 640×480 vía API pública" (VERIFICADO que la API es real); **peor sustento para la misión real** — cero evidencia de que S2 esté conectado a esa API; el único código real que intercepta S2 (PMCADemo) usa captura convencional.
4. **Seguridad/grabación: ¿cuándo es seguro liberar el buffer?** Codex D confirma que el retorno `0` de `FeaIf::EncodeStill` certifica solo "encolado", no lectura completa, y que ningún liberador real fue localizado. **NO VERIFICADO**, sin cambios de fondo respecto a sesión 16.

## 5. Veredicto A frente a E frente a P

**Sin cambio de orden de fondo: A > E > P ≈ E2.** Esta sesión no demuestra ni descarta E. Debilita la hipótesis de que el `StsViewer` compartido sea un mecanismo de arbitraje activo (es agregador, no cerrojo) y fortalece la hipótesis de exclusión puramente estructural entre `0x2a`/`0xb4` (no entre Camera y Recorder). Aporta una arquitectura P mejor documentada que E para la pregunta estrecha de "JPEG electrónico accesible", pero sin ningún enlace al botón físico — P requiere escribir una aplicación Android nueva, no es un camino ya operativo en el firmware de Sony. Ver comparación completa en `docs/capture/s17-a-e-p-architecture-comparison.md`.

## 6. Siguiente bloqueo técnico específico y comprobable

Decompilar `LifeCycle::ctor`/`LifeCycle::Activate` (ELF `libObj.so` ≈`0x42b6c0`) para encontrar el sitio real donde se invoca `ObjPin::Connect` para una fila ya construida (createLifeCycles solo construye la lista, no conecta); y resolver el llamador indirecto (vía vtabla) de `0x43809ed8` localizando la tabla de function-pointers que lo contiene (los dos callers directos encontrados esta sesión —`0x43807d80`, `0x438089d4`— no referencian literalmente `0x3011`/`0x40193`, por lo que el enlace sigue abierto en una capa más).

## NO VERIFICADO (pendiente, declarado explícitamente)

Coexistencia real de modos de `ObjEffect` (`0x0a`+`0x07`+`0x2a` simultáneos a nivel de modo interno); identidad del "objeto 53"; otro creador de `0x2a` aparte de `ModelPbCap`; invocador vía vtabla de los dos escritores de modo 1; contenido real de las filas BSS de `0x43edccf8`; consumidor real de la cola `0x40193`; valor numérico confirmado de `CBID_ENCODE_STILL`; liberador real de los buffers DMM tras `EncodeStill`; enlace de bytecode Java para `PREVIEW_FRAME_FORMAT=256`; relación de origen físico común (o no) entre el evento Android y RelMgr/LIRO.
