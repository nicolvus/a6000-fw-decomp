# tools/eye-af/camera — Eye AF dentro de la cámara (`ar.eyeaf`)

App Android mínima (API 10, la que corre la A6000) que **no necesita PC**: pide la detección de
caras al propio firmware, toma los ojos que ya calcula (`Camera.Face.leftEye`/`rightEye`, que en la
A6000 provienen de `Camera::FC::Drv::ProcessEdt` — ver
[`docs/capture/eye-af-nativo-a6000.md`](../../../docs/capture/eye-af-nativo-a6000.md)) y manda el
punto de AF con el mensaje nativo de la cámara.

| Fichero | Qué es | Android |
|---|---|---|
| `src/eyeaf/AfPoint.java` | normalizado 0..1 → porcentaje 0..100 y empaquetado `(x·100)<<16 \| (y·100)` | no |
| `src/eyeaf/AfTracker.java` | banda muerta, límite de Hz, suavizado, salto de sujeto, cancelación | no |
| `src/eyeaf/WebApiMsg.java` | mensaje `WebApiIntMsg` de 1568 B (`msgid 0x192`, `paramid 0x8d`, payload `+0x10`) | no |
| `src/eyeaf/SelfTest.java` | 32 comprobaciones con las constantes verificadas en el binario | no |
| `src/eyeaf/EyeAfActivity.java` | preview + `setFaceDetectionListener` + envío | sí |

## Compilar y probar (sin cámara)

```shell
./build.sh core     # sólo el núcleo Java puro + sus 32 comprobaciones
./build.sh          # app completa + APK firmado en out/EyeAf.apk
```

Necesita `javac` (JDK 17) y, para la app, `android.jar` + `build-tools`:

```shell
JAVA_HOME=~/.local/jdk17 ANDROID_SDK=/tmp/sdk ./build.sh
```

## Cómo decide

Igual que el bucle del PC (`eyeaf/tracker.py`): elige la cara más grande, se queda con su ojo,
suaviza, y **sólo manda orden** si el ojo se movió más del 1 % del encuadre y como mucho 3 veces por
segundo. Si desaparece el ojo 1,5 s, manda la cancelación una vez.

## Canales de envío

- Por defecto **sólo registro** (`LogSender`): no toca la cámara.
- `UipcSender` escribe el mensaje de 1568 B en un socket local cuyo nombre se pasa por extra:
  `adb shell am start -n ar.eyeaf/.EyeAfActivity --es socket <nombre>`.
  El nombre del socket que atiende la orden **no está verificado** (ver
  [`analysis/eyeaf/rc_touchaf.md`](../../../analysis/eyeaf/rc_touchaf.md)): el canal demostrado es la
  API remota por HTTP, no el socket interno.

## Límites

- No se ha instalado en ninguna cámara.
- Que el firmware rellene `leftEye`/`rightEye` en `Camera.Face` es **NO_VERIFICADO**; si vienen
  vacíos se usa el tercio superior de la cara (`shortcut` marcado en el código).
- El sistema de coordenadas de `Camera.Face` es el del sensor (−1000..1000); la app lo remapea a
  0..1 y no aplica rotación ni espejo: se verificará en la primera prueba física.
