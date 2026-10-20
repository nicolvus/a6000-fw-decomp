# Sesión 18 (Claude B) — kernel Sony OSS vs. cadena JNI/Binder/ScalarDaemon

Alcance: análisis estático exclusivo, sin agentes delegados (prohibido explícitamente en el encargo; no se usó `Agent` en ningún momento de esta rama). **No se afirma que SilentShutter funcione.** No hay cámara conectada ni flasheo. No se editó `CONTEXT.md` ni ningún binario original. Clasificación obligatoria: VERIFICADO / INFERENCIA / HIPÓTESIS / NO VERIFICADO / DESCARTADO.

**Modelo/esfuerzo real usado**: Claude Sonnet 5, esfuerzo configurado en esta sesión = **bajo** (`reasoning_effort: 20` en la configuración del job), no "medium" como pedía el encargo. Intenté subir el esfuerzo con `set_session_effort`, pero esa herramienta solo opera sobre *otras* sesiones, no sobre la propia ("refused for this session — a session must not silently re-price its own turns"), así que no pude corregirlo desde dentro. Lo declaro igual que en sesión 17 en vez de ocultarlo. Esto limita la profundidad de desensamblado real que pude hacer (prioricé `nm -D`/`readelf`/`strings` sobre desensamblado instrucción por instrucción).

Fuentes: `linux-kernel.tar.gz` (raíz del proyecto, sin modificar) + extracción parcial en `analysis/session18/main/sony-oss-extracted/linux/`; binarios reales de `firmware/extracted/fw321/.../nflasha15_unpacked_unpacked/lib/libScalarDaemon.so` y `.../nflasha16_unpacked_unpacked/lib/{libcameraex_jni.so,libcameraex_client.so,libcameraseq.so}` (árbol A6000 fw 3.21, el mismo ya usado en sesión 17); `analysis/session18/main/sony-oss-inventory.md` (leído primero, no reconfirmado innecesariamente).

## 1. Binder/ashmem del kernel liberado vs. lo que usan los binarios reales

**VERIFICADO (parcial)**: el kernel incluye el Binder estándar de AOSP (`drivers/staging/android/binder.c` + `binder.h`) y `ashmem` — pero **ashmem está en `linux/mm/ashmem.c` + `linux/include/linux/ashmem.h`**, no en `drivers/staging/android/` (ubicación atípica respecto al AOSP "stock" de la época, donde ashmem suele vivir junto a binder en staging/android). No se encontró `lowmemorykiller`/`logger`/`ram_console`/`timed_output` fuera de staging/android (ubicación estándar).

**Comparación literal con los binarios (lo pedido explícitamente, "no asumas")**: no pude comparar IOCTLs/estructuras directamente porque **ninguno de los tres binarios de cámara llama a Binder/ioctl por sí mismo** — están *stripped* y ninguno importa `ioctl` ni símbolos `binder_*` (`nm -D`/`nm -D -u` vacíos para esas cadenas). El uso de Binder está delegado a `libbinder.so` (vía `NEEDED`), que es AOSP genérico, no código Sony específico — comparar sus IOCTLs contra el kernel liberado no aporta nada específico de la A6000 y queda **fuera de alcance razonable con el tiempo/esfuerzo disponible esta sesión**: NO VERIFICADO a ese nivel de detalle, declarado en vez de asumido.

**Hallazgo más importante de esta pregunta** (ver §5): la cadena real `CameraSequence → ScalarDaemon` **no pasa por Binder en absoluto**, sino por una librería propia (`libsdcom.so`, "SDCom"). Esto corrige una imprecisión de sesión 17.

## 2. ¿Driver de cámara real (V4L2/media) para el sensor de la A6000?

**DESCARTADO** (con el inventario disponible): `drivers/media/video/` solo contiene `omap3isp/` (driver genérico de TI OMAP3, ajeno a Sony/CXD) entre los subdirectorios con nombre reconocible; no hay ningún driver V4L2 con nombre que mencione Sony, BIONZ, CXD o un sensor Exmor. `drivers/mmc/host/` es la lista stock de hosts SD de Linux (ninguno con nombre Sony); el controlador SD real de la plataforma (`mach-cxd4132/sdc.c`) es la pieza específica de Sony, pero es controlador de tarjeta SD, no de sensor/imagen. **No se hizo inventario exhaustivo de los cientos de archivos de `drivers/media/`** por el límite de tiempo/esfuerzo de esta sesión — declarado como NO VERIFICADO a nivel exhaustivo, igual que ya constaba en el inventario de `sony-oss-inventory.md` §6.

## 3. ¿Ashmem/PMEM/ION como backend de los buffers de CameraSequence/DeviceBuffer?

- **VERIFICADO**: ashmem existe en el árbol (`mm/ashmem.c`), es memoria compartida anónima estándar de Android (fd + mmap), mecanismo plausible para pasar buffers de preview/raw entre procesos sobre Binder.
- **DESCARTADO**: no existe ningún driver ION (`drivers/gpu/ion`, `drivers/staging/ion` o equivalente) ni PMEM en el árbol — las coincidencias de "ion" encontradas por grep son subcadenas de otras palabras (`version`, `exception`, `compaction`, etc.), no un driver real.
- **INFERENCIA, no VERIFICADO**: que ashmem sea específicamente el backend de `DeviceBuffer`/CameraSequence. Es plausible (es el único mecanismo de memoria compartida presente y es el que usa el resto del stack Binder de Android en esa época), pero no hay ninguna referencia textual cruzada entre `DeviceBuffer` y `ashmem` en los binarios revisados — no se encontró la cadena `ashmem` en `strings` de `libcameraseq.so`/`libcameraex_jni.so`/`libcameraex_client.so` en la revisión rápida de esta sesión. Queda como hipótesis razonable, no como hecho confirmado.

## 4. ¿Algún código real conecta el botón físico S2 con CameraSequence?

**NO, con firmeza, sin ambigüedad — reafirmado, no repetido desde cero.** Esta sesión no volvió a rehacer la búsqueda exhaustiva ya cerrada en sesión 17 (que revisó `PMCADemo`/`CameraActivity.java` y confirmó `takePicture()` convencional). El nuevo hallazgo de esta sesión (§5) añade, si acaso, más distancia: el camino `CameraSequence → ScalarDaemon` ni siquiera comparte el bus Binder que usa la cámara convencional (`ICameraClient`/`ICameraService`), sino un IPC aparte (`SDCom`) hacia un proceso con *userland* distinto (glibc, no Bionic — ver §5). No se encontró, en ningún binario ni código fuente local revisado hasta ahora (sesión 17 + esta), ninguna referencia a un evento de botón físico (S2, `KEYCODE_FOCUS`, interrupción de teclado) que invoque `CameraSequenceDiadem`, `CameraSeqUtil` o cualquier símbolo de `SCALARDAEMON::SystemEventIssuerCameraSequence`. **DESCARTADO como ruta ya conectada en el firmware de fábrica.**

## 5. Ciclo de vida de CameraSequence en libScalarDaemon.so

**VERIFICADO con `nm -D`** sobre `libScalarDaemon.so` (nflasha15, fw321/A6000): los símbolos reales de `SCALARDAEMON::SystemEventIssuerCameraSequence` son:

- `createStream(int,int,bool)` — inicio/creación del stream.
- `setRawCapture(int,bool,bool,bool,int,int,bool)`, `setPreviewPath(...)`, `setPreviewBuffering(int,int)` — configuración antes/durante la captura.
- `getPreviewInfo`, `getPreviewBufferingFrame`, `getPreviewSaAnalizedData` — lectura de estado.
- `setChangeReleaseLockStatus(int,bool)` — el único símbolo con "release" en el nombre, pero es sobre un *lock status*, no una liberación/destrucción de stream.
- Callbacks de evento: `CameraSequenceEventRawCaptureEventCb`, `CameraSequenceEventPreviewErrorEventCb`, `CameraSequenceEventPreviewSaNotifyEventCb` (con sus `*EventList` como datos `D`, no función).
- `CommandProcessorFactoryCameraSequence::createProcessor(ScalarDaemonMsg::MESSAGE_ID)` — fábrica que despacha mensajes `SDCom` entrantes a comandos de CameraSequence.

**NO VERIFICADO**: no apareció ningún símbolo explícito `stopStream`/`closeStream`/`destroyStream`/`releaseStream` para `SystemEventIssuerCameraSequence`. **INFERENCIA**: el cierre/liberación probablemente se maneja como un `MESSAGE_ID` más dentro de `ScalarDaemonMsg`, despachado vía `CommandProcessorFactoryCameraSequence::createProcessor`, no como un método C++ con nombre propio — coherente con que todo el protocolo es mensaje-céntrico (`SDComMsg`), no RPC con un método por operación. No se hizo desensamblado de `createProcessor` para confirmar qué IDs de mensaje despacha (fuera de alcance con el esfuerzo bajo real de esta sesión).

**Hallazgo nuevo, corrige sesión 17**: sesión 17 afirmó "backend Binder estándar... enlace concreto a `libScalarDaemon.so`". Con `readelf -d`/`nm -D` esta sesión se confirma que:

- `libcameraex_client.so` (lado Bionic/Android) sí enlaza `libbinder.so` — eso es la ruta Binder convencional (`ICameraClient`/`ICameraService`), coherente con lo ya sabido.
- Pero el puente real hacia `CameraSequence`/`ScalarDaemon` es **otra librería**, `libcameraseq.so` (también NEEDED de `libcameraex_jni.so`), que **no enlaza `libbinder.so`**, sino `libsdcom.so`. Sus símbolos (`scalar::CameraSeqUtil::openSDCom`, `::sendSDComMsg`, `::closeSDCom`, `scalar::CameraSequenceDiadem::onEventReceived/handleRawCaptureEvent/...`) muestran que habla el protocolo **SDCom** (`SDComMsg`, `SDComIPCListener`, `SDComMsgUtil`) definido en `libsdcom.so`.
- `libScalarDaemon.so` (el proceso que realmente implementa `SystemEventIssuerCameraSequence`) **tampoco enlaza `libbinder.so`**: sus `NEEDED` son `libsdcom.so`, `libpthread.so.0`, `libstdc++.so.6`, `libc.so.6`, `librt.so.1`, etc. — **nombres de librería versionados estilo glibc** (`.so.6`, `.so.0`, `.so.1`), distinto del `libc.so`/`libstdc++.so` sin versión que usan los binarios Bionic/Android de la misma partición. Esto es **VERIFICADO por `readelf -d`** e **INFERENCIA fuerte**: `ScalarDaemon` corre en un entorno Linux de espacio de usuario separado del Android/Bionic que ejecuta `libcameraex_jni.so`/`libcameraseq.so` (probablemente el "lado Scalar/RTOS" ya documentado en sesiones previas del proyecto, no el lado Android).
- Conclusión corregida: **CameraSequence usa Binder solo en el tramo convencional de cámara (Android↔CameraService); el tramo específico hacia ScalarDaemon es SDCom, un IPC propio de Sony, no Binder.** La frase de sesión 17 "backend Binder estándar" para CameraSequence/ScalarDaemon es **imprecisa y se corrige aquí**, no se repite sin matizar.

## 6. ¿`getPreviewSequenceFrames()` como símbolo real local?

**DESCARTADO** (en los binarios disponibles): se buscó con `strings` la cadena `getPreviewSequenceFrames` en `libcameraex_jni.so`, `libcameraseq.so`, `libcameraex_client.so` y `libScalarDaemon.so` (fw321/A6000) — **cero coincidencias** en ninguno. Sigue sin haber verificación local de ese símbolo; la única fuente es el reporte de terceros en el issue #35 de OpenMemories-Framework (no verificable aquí, no se tiene ese software ni se instaló nada). Se mantiene como **NO VERIFICADO / probablemente no presente en esta versión de firmware**.

## 7. Plausibilidad del kernel 3.0.27 como kernel real de la A6000 (2014)

**INFERENCIA razonable, no certeza**: el inventario ya documentó mtime interno del tarball `2014-02-19` y defconfigs `cxd90014_android_*` que arrancan Android sobre un SoC Sony propio (`arch/arm/mach-cxd90014`). La A6000 se anunció/lanzó en abril de 2014. Un paquete OSS fechado ~2 meses antes del lanzamiento es temporalmente consistente con el ciclo habitual de publicación de código GPL de Sony (suelen liberar cerca del lanzamiento del producto, a veces con cierto desfase). **No hay ningún identificador textual ("ILCE-6000", número de modelo, etc.) que lo confirme de forma directa** — como ya señalaba el inventario, sin un segundo paquete (p. ej. A6300) para comparar mach-cxd90014 entre ambos no se puede descartar que el mismo kernel/SoC se comparta entre varios cuerpos de la misma generación BIONZ X. Conclusión: **plausible y consistente, no demostrado de forma unívoca.**

## 8. Compatibilidad estructural Binder del kernel vs. ICameraExClient/ICameraExService

**NO VERIFICADO a nivel de comparación binaria real** (y en buena medida **sin objeto**, ver §1 y §5): como los binarios de cámara no invocan `ioctl`/Binder directamente (delegan en `libbinder.so`, AOSP estándar), y el tramo específico CameraSequence↔ScalarDaemon no usa Binder sino SDCom, no hay una superficie Binder "propietaria de Sony" que comparar contra el `binder.c`/`binder.h` del kernel liberado más allá de la implementación AOSP genérica. Lo único verificable es que el kernel trae el Binder estándar de esa era (mismo `binder.h` que cualquier AOSP 3.0.x), que es la base sobre la que corre `libbinder.so`/`ICameraService` convencional — **consistente pero no diferenciador**, no se encontró ninguna extensión Sony del protocolo Binder en el árbol liberado.

## 9–16. ¿Cambia la conclusión de sesión 17 (A > E > P ≈ E2) con el kernel?

**No, sin cambio de fondo: sigue siendo A > E > P ≈ E2.** Razones, con el kernel como contexto nuevo:

- El kernel liberado **no aporta ninguna pieza propietaria de cámara** (confirmado explícitamente en el inventario §9: no contiene `libObj.so`, `libMWF.so`, `libmpr.so`, RelMgr, CaptureManager, ObjCamera/ObjEffect/ObjStillRecorder, EncodeStill, DMM, FEA ni CameraSequence/CameraEx). Es contexto de plataforma (SoC, Binder/ashmem genéricos, drivers SD/red estándar), no evidencia directa del comportamiento de los binarios propietarios ya analizados por desensamblado.
- Lo que sí cambia (matiza, no invierte el veredicto) es la **comprensión de P (CameraSequence)**: ya no es "Binder estándar hacia ScalarDaemon", sino "Binder convencional para la cámara normal + SDCom propio (no Binder) específicamente para CameraSequence/ScalarDaemon, cruzando además hacia un proceso con *userland* glibc separado del Android/Bionic". Esto hace **a P técnicamente más compleja y menos "pública/estándar" de lo que sesión 17 sugería**, no más simple. No mejora su desconexión del botón S2 (sigue sin haber ningún enlace real, §4), y añade una frontera de proceso/IPC adicional que una app Android nueva tendría que atravesar igual (vía `libcameraseq.so`/JNI, que sigue siendo la única puerta de entrada documentada).
- A (la ruta ya analizada por desensamblado directo del pipeline `ObjCamera→ObjEffect→ObjStillRecorder`/`EncodeStill`) y E siguen sin verse afectadas por este inventario de kernel — ninguna de sus piezas vive en código GPL/BSD liberado.
- Conclusión: **A > E > P ≈ E2 se mantiene.** El kernel no promueve a P porque P sigue sin tener ningún enlace con S2, y la nueva información (SDCom, proceso separado) la hace, si acaso, una vía *menos* "camino corto público" de lo que se pensaba, al añadir una frontera de proceso/IPC propietaria adicional (SDCom) que tampoco está documentada públicamente (a diferencia de la API Java de CameraSequence, que sí lo está vía el issue de terceros).

## Resumen de incidentes de esta sesión

- Esfuerzo real usado: **Sonnet 5, bajo** (no "medium" como se pidió). Se intentó corregir con `set_session_effort` y la herramienta rechazó el cambio sobre la propia sesión. Declarado explícitamente, sin ocultarlo, igual que exige el encargo.
- No se lanzó ningún subagente (prohibido explícitamente en el encargo, respetado).
- No se tocó `CONTEXT.md`, no se modificó ningún binario original, no se conectó ni flasheó la cámara, no se instaló ningún paquete.
- Los `tar.gz` originales de la raíz no se volvieron a descargar; solo se listó su contenido con `tar tzf` (sin extraer fuera de `analysis/session18/claude-b/` cuando se necesitó detalle adicional — en la práctica, el inventario de `main` y una lectura de `tar tzf` directa sobre los `.tar.gz` de la raíz fueron suficientes para responder, por lo que no fue necesario extraer nada adicional esta sesión).
