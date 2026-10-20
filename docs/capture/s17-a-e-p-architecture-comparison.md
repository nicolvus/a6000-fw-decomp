# Comparación de arquitecturas A / E / P (sesión 17)

No se afirma que SilentShutter funcione. Clasificación: VERIFICADO / INFERENCIA / HIPÓTESIS / NO VERIFICADO / DESCARTADO. Separación obligatoria: comportamiento observado en código / alcanzabilidad estática / comportamiento reportado en fuente externa / hipótesis de integración / validación física (inexistente en este proyecto).

## Arquitectura A — LIRO estándar (RelMgr → CaptureManager → Darwin)

- **Comportamiento observado en código:** completo y real, es el camino de disparo mecánico de fábrica (`docs/capture/shutter-trigger-state-machine.md`, `shutter-trigger-chain-0x3011.md`).
- **Alcanzabilidad estática:** total — es el camino que el firmware ejecuta por defecto.
- **Validación física:** es, por definición, la que ya usa la cámara (precedente operativo real).
- **Veredicto:** única arquitectura con precedente operativo demostrado. Sigue siendo la referencia.

## Arquitectura E — ObjCamera → ObjEffect → ObjStillRecorder → EncodeStill (Live View continuo)

- **Comportamiento observado en código (sesión 17, nuevo):**
  - `ObjPin::Connect` (libMWF.so) no arbitra por ocupación de pin; `ObjStatusViewer`/`StsViewer` es un agregador de notificación, no un cerrojo (Claude A, VERIFICADO).
  - `Effect.in0` (Camera) y `Effect.out1` (Recorder) son pines distintos sin colisión estructural entre sí (VERIFICADO); la única colisión real es entre las filas `0x2a`/`0xb4` que comparten el mismo pin de destino escalar en StillRecorder (INFERENCIA fuerte).
  - La Sequence `0x6013` (`BeginExecCommand` candidato `0x15fd50`) no compara `unitType` en sus guardas visibles (Codex C, VERIFICADO para esa función; NO VERIFICADO en capas internas del holder/SDF).
  - El selector de captura `0x437eabfc` (LIRO, lado principal) no tiene ninguna marca de modo Silent/EFCS en su árbol de decisión (VERIFICADO); su tabla de filas es BSS/no recuperable estáticamente (VERIFICADO).
  - `FeaIf::EncodeStill` solo encola (no espera fin de lectura); ningún liberador real de buffers DMM fue localizado tras el callback (Codex D, VERIFICADO/NO VERIFICADO).
- **Alcanzabilidad estática:** el camino de control Camera→Effect→Recorder **no está bloqueado por `ObjPin::Connect`/`GetStsViewer`** (bloqueo de sesión 16 debilitado); sigue **sin disparador fotográfico conocido** que lleve a los modos 2–5 de `EffectInternalMode`, y sin consumidor confirmado de la cola `0x40193`/`0x3011` que conecte con este subsistema.
- **Hipótesis de integración:** si existiera tal disparador, la ruta de datos (YC→SDF→PlayData→EncodeStill) tiene un contrato parcialmente reconstruido para PbCap, sin prueba de que acepte el YC real de Camera.
- **Validación física:** inexistente (no hay hardware en este proyecto).
- **Veredicto:** ni viable ni descartada. El bloqueo de control se debilitó (no hay arbitraje activo); el bloqueo de datos y el de disparo persisten.

## Arquitectura P — CameraSequence (API Android pública de Sony)

- **Comportamiento observado en código (sesión 17, nuevo):**
  - `CameraSequence`/`CameraEx`/`DeviceBuffer` son reales en el firmware A6000 local (`libcameraex_jni.so`, `libcameraex_client.so`), con backend Binder estándar y enlace verificado a `libScalarDaemon.so` (Claude B + verificación cruzada del principal, VERIFICADO).
  - El único código real que intercepta el botón físico S2 (PMCADemo, `CameraActivity.java`) usa `takePicture()` convencional, **no** `CameraSequence` (VERIFICADO por lectura directa de fuente).
- **Comportamiento reportado en fuente externa (no reproducido):** un usuario de GitHub reporta JPEG de preview funcional a 640×480/30fps vía `getPreviewSequenceFrames(1)` en una A6000 real — declaración de terceros, no prueba de este proyecto.
- **Alcanzabilidad estática:** la API existe y está respaldada por binarios reales; **no hay ningún enlace, público ni local, entre S2 y esta API**.
- **Hipótesis de integración:** conectar S2 a `CameraSequence` requeriría escribir una aplicación Android nueva que intercepte `onShutterKeyDown`, mantenga una `CameraSequence` en preview activo, y llame `getPreviewSequenceFrames(1)` en el instante del evento, guardando el JPEG manualmente (sin EXIF/miniatura/registro DCF automático).
- **Validación física:** inexistente; además la declaración externa que sustenta el formato/resolución tampoco fue reproducida.
- **Veredicto:** mejor sustento documental y binario para "¿existe una API accesible de JPEG electrónico?" que E; peor sustento para la misión real ("¿S2 dispara eso?") — cero evidencia de conexión al botón físico. No es un camino operativo ya existente, es trabajo de integración por construir.

## Orden final de esta sesión

**A > E > P ≈ E2.**

- A: único precedente operativo real.
- E: bloqueo de control debilitado (sin arbitraje activo de StsViewer), bloqueos de datos y de disparo sin cambios.
- P: mejor API pública verificada, peor conexión a S2 (ninguna).
- E2 (variante de E discutida en sesiones previas): sin cambios, sigue en el mismo nivel aproximado que P por ausencia de evidencia de disparo.

Ninguna de las tres rutas (E, P, E2) demuestra estáticamente una cadena completa hasta escritura DCF y confirmación de catálogo de reproducción (criterio CIPA DC-009 citado por Codex D). No se afirma que SilentShutter funcione.
