# S17 — Claude B: CameraSequence (Android/OpenMemories) vs arquitectura E

Investigación en solitario (sin subagentes). Fuentes: (a) fetch real de 3 URLs públicas vía
`ctx_fetch_and_index` (equivalente a WebFetch, contenido indexado y consultado con `ctx_search`,
no citado de memoria); (b) grep/análisis local de binarios ya extraídos del firmware A6000 en
este proyecto (`analysis/symbols/*`, `firmware/extracted/*`).

## 1. Clases CameraSequence, CameraEx, DeviceBuffer

### Fuente pública (issue #35, ma1co/OpenMemories-Framework) — consultado directamente, NO reproducido localmente
Autor del issue reporta (texto citado, no inventado):
```
CameraEx camEx = CameraEx.open(0, null);
Camera cam = camEx.getNormalCamera();
CameraSequence camSeq = CameraSequence.open(camEx);
CameraSequence.Options seqOpts = new CameraSequence.Options();
camSeq.startPreviewSequence(seqOpts);
DeviceMemory[] memories = cameraSequence.getPreviewSequenceFrames(1);
DeviceBuffer deviceBuffer = (DeviceBuffer) memories[0];
deviceBuffer.read(previewBuffer, deviceBuffer.getSize(), 0);
deviceBuffer.release();
```
Clasificación: **declaración de un usuario de GitHub**, no prueba propia. Sin repro en este
proyecto (no hay entorno Android/hardware disponible en esta sesión).

Firmas derivadas del texto (no de código fuente Java visible en el repo — el repo
OpenMemories-Framework es solo las clases *propias* de ma1co, `CameraSequence`/`CameraEx`/
`DeviceBuffer` son clases internas de Sony `com.sony.scalar.hardware.*`, NO están en ese repo):
- `CameraEx.open(int, Object): CameraEx` (estático)
- `CameraEx.getNormalCamera(): android.hardware.Camera`
- `CameraSequence.open(CameraEx): CameraSequence` (estático)
- `CameraSequence.startPreviewSequence(CameraSequence.Options): void`
- `CameraSequence.getPreviewSequenceFrames(int): DeviceMemory[]`
- `DeviceBuffer extends DeviceMemory`; `DeviceBuffer.read(ByteBuffer,int,int)`, `.getSize()`, `.release()`

### Evidencia local (VERIFICADO — binarios reales del firmware A6000 fw3.21)
Localizados en `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha16_unpacked_unpacked/lib/`:
- `libcameraex_jni.so`
- `libcameraex_client.so`

(también presentes en los árboles de a7s-fw320 y a6300-fw201 extraídos en este proyecto — mismo
par de bibliotecas en varios modelos Sony de la época, consistente con que es infraestructura
compartida, no específica de un modelo).

Símbolos reales extraídos (`analysis/symbols/libcameraex_jni.so.symbols.txt`,
`libcameraex_client.so.symbols.txt`) — VERIFICADO:
```
_Z48register_com_sony_scalar_hardware_CameraSequenceP7_JNIEnv
_Z46register_com_sony_scalar_hardware_DeviceMemoryP7_JNIEnv
_Z42register_com_sony_scalar_hardware_CaemraExP7_JNIEnv   (sic: typo "Caemra" en el símbolo real)
_Z37register_com_sony_scalar_hardware_DSPP7_JNIEnv
_Z49register_com_sony_scalar_hardware_MemoryMapConfigP7_JNIEnv
_Z44register_com_sony_scalar_media_MediaRecorderP7_JNIEnv
_Z43register_com_sony_scalar_media_AudioManagerP7_JNIEnv
_Z57register_com_sony_scalar_graphics_imagefilter_ImageFilterP7_JNIEnv

JNICamSeqContext::postData(int, scalar::DeviceMemoryIF*, int, int)
JNICamSeqContext::notify(int,int,int)
JNICamSeqContext::release()
JNICamSeqContext::requestDelegateEvent(bool,int)
JNICamSeqContext::JNICamSeqContext(JNIEnv*, jobject, jclass, android::sp<scalar::CameraSequenceIF> const&, ...)
android::JNICameraExContext::{create,release,enableExtraEvent,disableExtraEvent,notify,postDataTimestampEx,...}
scalar::CameraSequenceIF_open()      [importado/UND, implementado en otra lib]
scalar::DeviceMemoryIF_createImage(int,int)   [importado/UND]
scalar::DeviceMemoryIF_createBuffer(unsigned int) [importado/UND]
scalar::DSPIF_createProcessor(char const*)    [importado/UND]
```
Esto confirma de forma independiente (sin depender del issue de GitHub) que `CameraSequence`,
`DeviceMemory`/`DeviceBuffer` y `CameraEx` son reales en el firmware A6000, con un backend nativo
C++ (`scalar::CameraSequenceIF`, `scalar::DeviceMemoryIF`) cuya implementación concreta NO está en
`libcameraex_jni.so` (son símbolos `UND`, importados en tiempo de carga de otra biblioteca —
candidatos: `libcamera.so` o `libScalarDaemon.so`, ver §4).

`libcameraex_client.so` (VERIFICADO, símbolos reales) implementa el lado Binder de `CameraEx`:
```
android::CameraEx::{init,create,connect,disconnect,reopen,sendCommand,sendCommandR,
  getInitialParameters,getSupportedParameters,getLensInfo,getFocusAreaInfos,
  getChannelColorSelect,setColorSelectedToChannel,getPreviewDisplayColor,
  getPictureReviewSupportedTimes,settingChangeTypesControl,setListener,dataCallback,
  notifyCallback,getCameraExService,remote}
android::ICameraExClient (BnInterface<ICameraExClient>, descriptor real en .data)
android::ICameraExService::asInterface(sp<IBinder> const&)
android::BnCameraExClient::onTransact(...)
```
`CameraEx::getCameraExService()` usa `android::defaultServiceManager()` — es decir, `CameraEx` se
conecta a un **servicio Binder del sistema** llamado por su descriptor (`ICameraExService`), no a
un socket propio ni a un RPC ad-hoc.

## 2. Bibliotecas JNI y símbolos nativos

| Biblioteca | Rol | Estado |
|---|---|---|
| `libcameraex_jni.so` | Puente JNI Java↔nativo para `com.sony.scalar.hardware.{CameraSequence,CameraEx,DeviceMemory,DSP,MemoryMapConfig}` y `com.sony.scalar.media.{MediaRecorder,AudioManager}` | VERIFICADO (binario real, fw3.21) |
| `libcameraex_client.so` | Cliente Binder de `CameraEx` (`ICameraExClient`/`ICameraExService`, clase C++ `android::CameraEx`) | VERIFICADO |
| `libcamera.so` | HAL de cámara Android (`android::CameraHardwareDiadem` — nombre interno "Diadem"); contiene `KEY_BURST_DRIVE_BUTTON_RELEASE_BEHAVE` y métodos de parámetros Camera2-style | VERIFICADO (símbolos demangled reales, `analysis/symbols/libcamera.so.demangled.txt`) |
| `libScalarDaemon.so` | Contiene clases `SCALARDAEMON::SystemEventIssuerCameraSequence` y `SCALARDAEMON::CommandProcessorFactoryCameraEx/CameraSequence` | VERIFICADO — ver §4 |

No se encontró el cuerpo de `scalar::CameraSequenceIF_open`/`DeviceMemoryIF_create*` en
`libcameraex_jni.so` ni en `libcameraex_client.so` (ambos los referencian como `UND`). No se
localizó explícitamente en qué `.so` residen estos símbolos esta sesión (requeriría resolver la
tabla de símbolos dinámicos de `libcamera.so`/`libScalarDaemon.so` buscando el nombre exacto
`CameraSequenceIF_open`, lo cual quedó fuera del tiempo de esta tarea). **NO VERIFICADO** en qué
biblioteca concreta vive la implementación de `CameraSequenceIF`.

## 3. Rutas Binder/sockets/RPC

VERIFICADO: `CameraEx` usa **Binder estándar de Android** (`android::defaultServiceManager()`,
`BnInterface<ICameraExClient>`, `ICameraExService::asInterface`), NO un socket propio. Esto es
coherente con el patrón normal de servicios de cámara de Android (como `android.hardware.Camera`
usa `ICameraService`), extendido aquí con un servicio paralelo `ICameraExService` específico de
Sony para las extensiones (`CameraEx`). `CameraSequence` en el lado Java (`JNICamSeqContext`) no
muestra en sus símbolos un segundo canal Binder propio — recibe datos vía el callback
`postData`/`notify` invocado desde el nativo, probablemente sobre el mismo canal `CameraEx`
(`dataCallback`, `notifyCallback`). **INFERENCIA** (no verificado con trace en vivo): `CameraSequence`
viaja dentro del mismo Binder de `CameraEx`, no abre una conexión Binder independiente.

## 4. Relación con ScalarDaemon, SFRA/streaming, DMM

**VERIFICADO** (grep directo sobre `analysis/symbols/libScalarDaemon.so.symbols.txt`, símbolos
reales demangled):
```
SCALARDAEMON::SystemEventIssuerCameraSequence::setPreviewPath(...)
SCALARDAEMON::SystemEventIssuerCameraSequence::getPreviewInfo(int,int)
SCALARDAEMON::SystemEventIssuerCameraSequence::setPreviewBuffering(int,int)
SCALARDAEMON::SystemEventIssuerCameraSequence::getPreviewBufferingFrame(int,int)
SCALARDAEMON::SystemEventIssuerCameraSequence::setRawCapture(int,bool,bool,bool,int,int,bool)
SCALARDAEMON::SystemEventIssuerCameraSequence::createStream(int,int,bool)
SCALARDAEMON::SystemEventIssuerCameraSequence::setChangeReleaseLockStatus(int,bool)
SCALARDAEMON::SystemEventIssuerCameraSequence::{setPreviewSaAnalizedNotify,getPreviewSaAnalizedData}
SCALARDAEMON::CommandProcessorFactoryCameraEx::createProcessor(ScalarDaemonMsg::MESSAGE_ID)
SCALARDAEMON::CommandProcessorFactoryCameraSequence::createProcessor(ScalarDaemonMsg::MESSAGE_ID)
SCALARDAEMON::CameraSequenceEventRawCaptureEventCb(...)
SCALARDAEMON::CameraSequenceEventPreviewSaNotifyEventCb(...)
SCALARDAEMON::CameraSequenceEventPreviewErrorEventCb(...)
```
Esto **confirma con enlace concreto** (no solo coincidencia de nombres) que la API Android
`CameraSequence` está respaldada en el lado nativo por `ScalarDaemon` — el mismo daemon central
que las ramas B/F investigan para SFRA/DMM. `ScalarDaemon` tiene una fábrica de "command
processors" dedicada a `CameraEx` y otra a `CameraSequence`, y emite eventos propios
(`CameraSequenceEventRawCaptureEvent`, `...PreviewSaNotifyEvent`, `...PreviewErrorEvent`).

`createStream(int,int,bool)` y `setRawCapture(...)` sugieren fuertemente que `CameraSequence`
puede pedir no solo JPEG de preview sino también **flujos raw** — coherente con que sea un
front-end más del mismo motor de streaming de ScalarDaemon que `SFRA` usa (`capture-scalar*.json`
en este proyecto), aunque **NO VERIFICADO** que compartan el mismo buffer `DMM`/ring que `SFRA`
(ningún call-graph trazado esta sesión conecta `SystemEventIssuerCameraSequence::createStream` con
las rutinas DMM/SFRA documentadas en `sfra-mpr-buffer-bridge.md`/`sfra-electronic-frame-source.md`).
**INFERENCIA fuerte** (mismo daemon, nomenclatura paralela a `SystemEventIssuer*` de otros
subsistemas de ScalarDaemon ya mapeados en el proyecto) de que comparten la misma capa de memoria
DMM; **no se declara como arquitectura E/SFRA confirmada**, solo como daemon compartido.

## 5. Propiedad de DeviceBuffer y qué hace `.release()`

Según el issue (declaración de usuario, NO reproducido): `getPreviewSequenceFrames()` devuelve un
array de `DeviceMemory`, de los cuales `DeviceBuffer` es un subtipo; el buffer es de "solo
lectura directa" (`ByteBuffer.allocateDirect`), se lee con `.read(dest, size, offset)` y luego se
debe llamar `.release()` — el usuario advierte que `.read()` no actualiza `position()/limit()` del
`ByteBuffer` destino (hay que ajustarlos manualmente).

Evidencia local VERIFICADA: `scalar::DeviceMemoryIF_createBuffer(unsigned int)` existe como función
nativa importada por `libcameraex_jni.so` — confirma que la asignación es nativa (lado C++,
backend `scalar::DeviceMemoryIF`), y el objeto Java `DeviceMemory`/`DeviceBuffer` es un wrapper JNI
sobre un puntero nativo. **Propiedad**: el buffer pertenece al runtime nativo (ScalarDaemon o la
biblioteca que implemente `DeviceMemoryIF`); `.release()` casi con certeza decrementa un refcount
o libera el buffer de vuelta al pool nativo (consistente con el patrón `android::RefBase`/`sp<>`
visible en todos los símbolos C++ de este firmware — `incStrong`/`decStrong` aparecen en
`libcameraex_client.so.symbols.txt`). Esto es **INFERENCIA fuerte por patrón de diseño Android
estándar**, no una lectura de la implementación real de `.release()` (no decompilado esta sesión).

## 6. Formatos aceptados; `PREVIEW_FRAME_FORMAT=256`

Issue (declaración de usuario, NO verificado): opciones conocidas que "funcionan":
```
PREVIEW_FRAME_RATE=30000 (30fps)
PREVIEW_FRAME_WIDTH=640
PREVIEW_FRAME_HEIGHT=480  (0 = auto)
PREVIEW_FRAME_FORMAT=256  ("no estoy seguro de la unidad, no he probado otros valores")
PREVIEW_FRAME_MAX_NUM (típicamente 1)
JPEG_COMPRESS_MAX_SIZE
JPEG_COMPRESS_RATE_DENOM
```
El propio autor del issue dice explícitamente que NO sabe qué significa `256` ni ha probado otros
valores. **NO VERIFICADO** que sea JPEG. Comparación solicitada con `android.graphics.ImageFormat`
(https://developer.android.com/reference/android/graphics/ImageFormat): en esa API,
`ImageFormat.JPEG = 256` es una constante real de Android. PERO: `CameraSequence.Options` es una
clase interna de Sony bajo el paquete `com.sony.scalar.hardware`, no hay evidencia (ni en el
issue, ni en los símbolos JNI locales, que no exponen nombres de constantes Java/enteros) de que
el código de Sony importe o redefina `android.graphics.ImageFormat`. Los símbolos nativos
disponibles (`register_com_sony_scalar_hardware_CameraSequence`, etc.) no permiten ver el valor
numérico interno usado para "JPEG" dentro de `CameraSequence.Options` — eso está en bytecode Java
(.dex de una app Sony) que no se localizó en este proyecto (ver §7, cruce local). **Conclusión: la
coincidencia numérica 256 con `ImageFormat.JPEG` es, con la evidencia disponible, HIPÓTESIS NO
VERIFICADA de que sea deliberada; también es plausible que sea casualidad de un enum interno de
Sony.** No se declara que son la misma constante.

## 7. ¿Un solo frame? Condiciones de modo; ¿funciona sin app visible?

Issue: `getPreviewSequenceFrames(1)` pide un solo frame explícitamente — es una llamada
**síncrona/pull**, no basada en callback (el propio issue dice "Unlike Android API, this is not
event driven so timing must be handled separately"). Requiere haber llamado antes
`startPreviewSequence(seqOpts)`, que a su vez requiere un `CameraEx` abierto y (según el ejemplo
oficial de uso) una `Camera` normal de Android vinculada a un `SurfaceHolder` con preview ya
iniciado (patrón visto en PMCADemo, ver §8). El issue no prueba ni menciona funcionamiento sin
superficie visible/app en foreground — **NO VERIFICADO** si funciona en segundo plano o sin
`Activity` visible. Dado el patrón estándar del HAL de cámara de Android
(`CameraHardwareDiadem::release()` VERIFICADO en `libcamera.so`, ligado al ciclo de vida de la
superficie de preview), es **HIPÓTESIS razonable pero NO VERIFICADA** que CameraSequence exige una
sesión de cámara activa con preview corriendo — es decir, una app Android en ejecución, con la
cámara abierta y mostrando preview, no una captura "headless" instantánea.

## 8. CameraSequence preview JPEG vs `takePicture()` convencional — separación S2/onShutterKeyDown

Leído directamente el código real de `PMCADemo/CameraActivity.java` (fetch real, citado, no de
memoria):
```java
import com.sony.scalar.hardware.CameraEx;
...
camera = CameraEx.open(0, null);
...
protected boolean onFocusKeyDown() { camera.getNormalCamera().autoFocus(null); return true; }
protected boolean onFocusKeyUp()   { camera.getNormalCamera().cancelAutoFocus(); return true; }
protected boolean onShutterKeyDown() { camera.getNormalCamera().takePicture(null, null, null); return true; }
protected boolean onShutterKeyUp()   { camera.cancelTakePicture(); return true; }
```
Hallazgo clave (VERIFICADO por lectura directa del código fuente real): el demo oficial de
ma1co que sí intercepta las teclas físicas de disparo (`onShutterKeyDown`/`onFocusKeyDown`, que
son **callbacks de `BaseActivity`**, es decir, del framework Android de eventos de teclado —
`KeyEvent`/`onKeyDown` de Activity, no un canal nativo propio) usa, al pulsar, el
`android.hardware.Camera.takePicture()` **convencional** (obtenido vía
`camEx.getNormalCamera()`), NO la ruta `CameraSequence.getPreviewSequenceFrames()`. Es decir:

- La ruta "S2 físico → captura" que **sí existe y funciona** en el ejemplo real es: tecla física
  → evento de teclado Android (`onShutterKeyDown`) → `Camera.takePicture()` convencional (obturador
  mecánico/HAL estándar, probablemente NO silencioso).
- La ruta `CameraSequence`/`DeviceBuffer` (JPEG de preview a 640×480) es un mecanismo
  **completamente aparte**, pensado para streaming continuo de baja resolución (vista en vivo,
  análisis), no demostrado ni en el issue ni en el demo como disparado por una tecla física.

**No hay evidencia pública ni local de que alguien haya conectado `onShutterKeyDown` a
`CameraSequence.getPreviewSequenceFrames()`** en vez de a `takePicture()`. Sería una integración
nueva por construir (código de aplicación Android), no un camino ya recorrido por Sony ni por la
comunidad OpenMemories.

## Cruce local — DEX/ODEX/JAR del firmware

Búsqueda realizada (`find . -iname "*.dex" -o -iname "*.odex" -o -iname "*.jar" -o -iname "*.apk"`
sobre todo el árbol del proyecto, excluyendo cachés de herramientas): **no se encontró ningún
DEX/ODEX/JAR/APK extraído del firmware en este proyecto.** Solo existen los `.so` nativos ya
mencionados (`libcameraex_jni.so`, `libcameraex_client.so`, `libcamera.so`, `libScalarDaemon.so`)
en `firmware/extracted/{fw321,a7s-fw320,a6300-fw201}/.../lib/`. No hay bytecode Java/Android
(que contendría las clases `CameraSequence.java`, `CameraEx.java`, `DeviceBuffer.java` reales con
sus constantes numéricas) extraído ni analizado en este proyecto. Esto es la explicación de por
qué §6 no puede verificarse más allá de HIPÓTESIS: falta la parte Java/Dalvik del sistema, que
probablemente reside en `/system/framework/*.jar` o similar dentro de una imagen de sistema
Android completa, no presente en este árbol de firmware extraído (el firmware aquí extraído
parece ser la partición `nflasha16` con bibliotecas nativas, no la imagen de sistema Android
completa). **DESCARTADO por ahora seguir esta vía localmente — no hay material; no se inventan
rutas.**

## Arquitectura P: evaluación

**Definición de P**: S2 → solicitud de JPEG electrónico vía `CameraSequence.getPreviewSequenceFrames()`
→ `DeviceBuffer` → integración fotográfica pendiente (guardar como foto real, no solo preview).

**Sustento de P vs arquitectura E (ObjCamera/ObjEffect/PbCap)**:
- P tiene **mejor sustento documental externo y de verificación binaria local** para la pregunta
  estrecha "¿existe una API accesible que entregue JPEG electrónico a 640×480?": sí, de forma
  VERIFICADA (símbolos reales en el firmware A6000 + reporte funcional independiente de un
  tercero). E se apoya en cadenas de inferencia internas mucho más largas y con más bloqueos
  abiertos (ver `RESEARCH_TASKS.md` sesiones 13–16: creador de topología `0x2a`, formato YC,
  liberación tras `CBID_ENCODE_STILL`, etc., todos parcialmente o no verificados).
- P tiene **peor sustento para la pregunta real de la misión** ("S2 dispara captura electrónica"):
  no hay NINGUNA evidencia, pública ni local, de que el botón físico S2 esté conectado a
  `CameraSequence` en el firmware de Sony. La única conexión demostrada entre tecla física y
  cámara en código real (PMCADemo) usa el obturador convencional, no `CameraSequence`. Conectar S2
  a `CameraSequence` requeriría escribir una app Android nueva que (a) intercepte
  `onShutterKeyDown`, (b) tenga una `CameraSequence` ya corriendo en preview, y (c) llame
  `getPreviewSequenceFrames(1)` en ese instante, guardando el JPEG manualmente (sin EXIF/miniatura,
  igual que el problema ya documentado para la ruta SFRA/DMM pura en `RESEARCH_TASKS.md` línea 14).
  Esto es trabajo de integración por hacer, no un camino ya operativo.
- Relación con arquitectura E: **no se encontró enlace** entre `CameraSequence`/`ScalarDaemon` y
  `ObjCamera`/`ObjEffect`/`PbCap` (esos símbolos pertenecen a otra familia de binarios LIRO, no
  tocados por `libcameraex_*`). Si comparten algo, sería más plausible que comparta backend con la
  arquitectura B/F (SFRA/DMM, también servida por `ScalarDaemon`) que con E — pero esto es
  **INFERENCIA**, no un call-graph verificado.

**Conclusión explícita: NO se afirma que CameraSequence funcione para disparo por S2.** Es una API
real, verificada, pensada para preview/streaming, sin conexión demostrada al botón físico ni a la
arquitectura E, con una conexión nominal verificada a `ScalarDaemon` (relevante para contrastar con
B/F) y sin bytecode Java local disponible para profundizar más en esta sesión.

## Confirmaciones de proceso requeridas

(a) No se delegó ningún trabajo a subagentes ni a Codex ni a ningún otro proceso; todas las
fetches, greps y lecturas de este informe se ejecutaron directamente por este agente (Claude B),
usando `ctx_fetch_and_index`/`ctx_search` como sustituto equivalente de WebFetch (fetch real de
red, contenido indexado) y `Bash`/`Read` para el árbol local.

(b) Modelo/esfuerzo real usado: Claude Sonnet 5 (`claude-sonnet-5`), esfuerzo de razonamiento bajo
(reasoning effort = low), tal como indica la configuración de la sesión.

(c) Hallazgo concreto para el Claude principal (contraste con `RelMgr`/LIRO): en el lado Android,
el evento de disparo físico llega a la aplicación como un **callback de alto nivel del framework
Android** (`onShutterKeyDown`/`onFocusKeyDown` de `BaseActivity`, basado en el despacho estándar de
`KeyEvent` de Android), completamente separado y sin enlace demostrado con la cola nativa LIRO
`0x40193`/`RelMgr` (`0x4379d838`) que la investigación principal rastrea para S1/S2. No se halló
evidencia de que el mismo evento de hardware llegue también a RelMgr desde el lado Android, ni de
que Android y LIRO compartan el mismo origen de interrupción — son dos rutas de software
documentadas de forma independiente en este proyecto, cuya relación de origen común (mismo GPIO,
despachado dos veces) queda como pregunta abierta para la rama LIRO.
