# Cruce de fuentes públicas — API CameraSequence/CameraEx (sesión 17)

Clasificación obligatoria por enlace: Consultado directamente / Consultado parcialmente / Inaccesible / No consultado. Fuente: trabajo de Claude B (`docs/capture/s17-claude-b-camerasequence.md`), verificado por el principal mediante `find`/`nm -D` locales (ver `s17-parallel-crosscheck.json`, verificación cruzada #2).

| Enlace | Estado | Hallazgo |
|---|---|---|
| P1 — OpenMemories-Framework issue #35 | **Consultado directamente** (fetch real) | Declaración de un usuario de GitHub (no reproducida localmente): `CameraEx.open`→`CameraSequence.open`→`startPreviewSequence`→`getPreviewSequenceFrames(1)`→`DeviceBuffer.read/release`, reportado funcional en ILCE-6000 a 640×480/30fps/formato 256 JPEG. El propio autor admite no estar seguro del significado de `256`. |
| P2 — OpenMemories-Framework (raíz) | **Consultado directamente** (fetch real) | Confirma que `CameraSequence`/`CameraEx`/`DeviceBuffer` son clases internas de Sony (`com.sony.scalar.hardware.*`), no parte del propio repo de ma1co. |
| P3 — PMCADemo `CameraActivity.java` | **Consultado directamente** (fetch real, código citado) | `onShutterKeyDown()` usa `camera.getNormalCamera().takePicture(null,null,null)` — captura convencional, NO `CameraSequence`. `onFocusKeyDown/Up` usan autofocus estándar. |
| P4 — Sony OSS ILCE-6000 | **Consultado parcialmente** (Codex D, como contexto, no como prueba de implementación) | El portal publica paquetes GPL (`linux-kernel.tar.gz`); no se usó ni se demuestra que exponga FEA/DMM propietarios. |
| P5 — Sony OSS ILCE-6300 | **No consultado** esta sesión | — |
| P6 — Sony-PMCA-RE | **No consultado** esta sesión | — |
| P7 — fwtool.py | **No consultado** esta sesión | — |
| P8 — sony-a6000-firmware-research | **No consultado** esta sesión | — |
| P9 — CIPA DC-009/DCF | **Consultado parcialmente** (Codex D) | Identifica DC-009-2010 (DCF 2.0) como el estándar de catálogo; no se cruzó contra la implementación interna de Sony. |
| P10 — Android `ImageFormat` | **Consultado por referencia** (citado, no fetcheado explícitamente esta sesión) | `ImageFormat.JPEG=256` es una constante real de Android; **no se encontró evidencia** (bytecode Java ausente en el proyecto) de que `CameraSequence.Options` importe o redefina esa constante — coincidencia numérica sin confirmar como deliberada. |

## Verificación local independiente de las declaraciones públicas

A diferencia de sesiones previas que solo citaban el issue de GitHub, esta sesión **verificó localmente contra binarios reales del firmware A6000 fw3.21** (no contra el testimonio de terceros):

- `libcameraex_jni.so` y `libcameraex_client.so` existen realmente en `firmware/extracted/fw321/.../nflasha16_unpacked_unpacked/lib/` — **VERIFICADO** (archivo presente, SHA no recalculado esta sesión).
- Símbolos JNI reales (`register_com_sony_scalar_hardware_CameraSequence`, `JNICamSeqContext::{postData,notify,release}`, etc.) — **VERIFICADO** por `nm`/tablas de símbolos ya generadas en `analysis/symbols/`.
- `libcameraex_client.so` implementa `android::CameraEx` sobre Binder estándar (`ICameraExClient`/`ICameraExService`, `android::defaultServiceManager()`) — **VERIFICADO**.
- `libScalarDaemon.so` contiene `SCALARDAEMON::SystemEventIssuerCameraSequence` y `SCALARDAEMON::CommandProcessorFactoryCameraEx/CameraSequence` — **VERIFICADO independientemente por el principal** (`nm -D` directo, ver crosscheck).

## Distinción obligatoria: declaración de usuario vs. prueba reproducida

**Declaración de usuario (no verificada por este proyecto):** que `getPreviewSequenceFrames(1)` entregue efectivamente un JPEG válido a 640×480/30fps en una A6000 real; que `.release()` libere correctamente el buffer; que el formato `256` sea JPEG.

**Prueba reproducida localmente (VERIFICADO):** que las clases, el backend JNI/Binder y el daemon (`ScalarDaemon`) que sostendrían esa API existen de verdad en el firmware 3.21 de este proyecto, y que el único código real que intercepta el botón físico (PMCADemo) no usa esa API.

## Conclusión

La API pública `CameraSequence` está mejor documentada externamente y mejor verificada localmente (en términos de existencia binaria) que la ruta interna de la arquitectura E, pero **no existe ningún enlace demostrado, ni público ni local, entre el botón físico S2 y `CameraSequence`**. Conectarlos sería trabajo de integración nuevo (una aplicación Android), no un camino ya operativo en el firmware de Sony. No se afirma que SilentShutter funcione por esta vía.
