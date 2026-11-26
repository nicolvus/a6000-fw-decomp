# tools/eye-af — detector de ojos para "Eye AF en tiempo real" (PC)

Módulo de detección de ojos sobre imágenes/frames en memoria. **No habla con la cámara**:
recibe un `numpy.ndarray` BGR y devuelve ojos con coordenadas normalizadas.

## API

```python
from eyeaf import EyeDetector, Eye

detector = EyeDetector(model_path=None, score_threshold=0.7, nms_threshold=0.3,
                       input_size=(640, 480), max_faces=5)
eyes: list[Eye] = detector.detect(frame_bgr)
```

`Eye` es un `dataclass(frozen=True)` con:

| campo | significado |
| --- | --- |
| `x`, `y` | centro del ojo, **normalizado 0..1** respecto al frame |
| `confidence` | confianza de la **cara** (YuNet no puntúa cada landmark por separado) |
| `side` | `'right'`/`'left'` **desde el punto de vista del sujeto**, `'unknown'` si no se puede deducir |
| `face_box` | `(x, y, w, h)` normalizado de la cara que lo contiene |
| `face_score` | puntuación de la cara (igual que `confidence` en la ruta YuNet) |

Convención de `side`: en una imagen frontal sin espejar, el ojo que aparece a la izquierda
de la imagen es el ojo **derecho del sujeto**. Un frame espejado o un perfil invierten esa
lectura; la ruta Haar devuelve `'unknown'` cuando solo ve un ojo.

## Backends

1. **YuNet** (`cv2.FaceDetectorYN`, preferido): caja de cara + 5 landmarks + score. Los dos
   primeros landmarks son los ojos, que es lo único que se usa aquí (YuNet no tiene clase
   "ojo": se localiza el landmark).
2. **Cascadas Haar** (degradación si `cv2.FaceDetectorYN` no existe en la versión instalada):
   `haarcascade_frontalface_default.xml` + `haarcascade_eye.xml`. Limitaciones documentadas
   en el bloque `shortcut:` de `eyeaf/detector.py` (sin landmarks, score fijo 0.5, exige
   ambos ojos para deducir el lado, falla con perfil/parpadeo/gafas).

Notas de implementación (VERIFICADO ejecutando en esta máquina):

* La fila que devuelve `FaceDetectorYN.detect()` tiene 15 valores:
  `x, y, w, h, ojo_der(x,y), ojo_izq(x,y), nariz(x,y), comisura_der(x,y), comisura_izq(x,y), score`.
  Los landmarks empiezan en el índice **4**, no en el 5.
* El modelo `2023mar` tiene forma de entrada estática y **exige múltiplos de 32**: la entrada
  se redondea hacia abajo al múltiplo de 32 más cercano (640x480 ya lo es).
* El frame se encaja con letterbox conservando la relación de aspecto; las coordenadas se
  deshacen del factor de escala antes de normalizar.
* En el retrato de prueba el landmark cae sobre el ojo pero ligeramente **por debajo** del
  centro de la pupila (característica del modelo, no del código).

## Modelo

`models/face_detection_yunet_2023mar.onnx` (232 589 B, SHA-256
`8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4`), descargado con:

```shell
.venv/bin/python tools/eye-af/fetch_models.py            # verifica SHA-256 fijado
.venv/bin/python tools/eye-af/fetch_models.py --force    # redescarga
```

Origen: OpenCV Zoo (`models/face_detection_yunet/`, repo **Apache-2.0**), pesos originales de
ShiqiYu/libfacedetection.train (**BSD-3-Clause**) y artículo *YuNet: A Tiny Millisecond-level
Face Detector*. El fichero se sirve por Git LFS: `raw.githubusercontent.com` devuelve el
puntero de 131 B, por eso el script usa `media.githubusercontent.com`. Pesa < 1 MB, así que
se versiona sin entrada en `.gitignore`.

## Entorno

```shell
.venv/bin/pip install "opencv-python-headless==4.14.0.94" numpy
```

OpenCV **5.x no sirve para la ruta de degradación**: en 5.1.0.95 no existen
`cv2.CascadeClassifier` ni los XML de `cv2.data.haarcascades` (VERIFICADO en esta máquina).
Por eso el entorno fija la 4.14, que tiene YuNet *y* cascadas.

## Tests y bench

```shell
.venv/bin/python -m pytest tests/test_eye_af_detector.py -q
.venv/bin/python tools/eye-af/bench_detector.py            # ms/frame por resolución
.venv/bin/python tools/eye-af/bench_detector.py --md       # filas markdown para BENCH.md
```

Resultados de esta máquina en [`BENCH.md`](BENCH.md).

## Eye AF en tiempo real (bucle completo)

El detector de arriba es una pieza. El bucle que mueve el punto de enfoque de la cámara usa
la API remota que la propia A6000 ya trae (app **Smart Remote Control**, `orb-server`):
`startLiveview` → JPEG por HTTP → ojos → `setTouchAFPosition`.

```shell
# 1) cámara: app Smart Remote Control abierta y el PC en la misma red
.venv/bin/python scripts/eye_af.py --host 192.168.1.29 --check      # diagnóstico de la API
# 2) seguimiento con ventana (ESC sale, ESPACIO dispara)
.venv/bin/python scripts/eye_af.py --host 192.168.1.29 --preview --focus-mode AF-C
# 3) sólo visión, sin tocar la cámara
.venv/bin/python scripts/eye_af.py --host 192.168.1.29 --dry-run --preview
```

| pieza | archivo | papel |
| --- | --- | --- |
| cliente de la API | `eyeaf/api.py` | JSON-RPC a `/sony/camera`, autodetecta puerto 8080/10000 |
| Live View | `eyeaf/liveview.py` | JPEGs del flujo `chunked` (delimitados por SOI/EOI) |
| decisión del punto | `eyeaf/tracker.py` | elige ojo, suaviza, banda muerta y límite de frecuencia |
| bucle | `eyeaf/loop.py` | cuadro → ojo → `setTouchAFPosition`, estadísticas, grabación |
| cámara falsa | `fake_camera.py` | mismo contrato en local para probar sin hardware |

Datos de la API que condicionan el diseño (**VERIFICADO** en `orb-server` fw3.21, ver
[`analysis/eyeaf/orb_touchaf.md`](../../analysis/eyeaf/orb_touchaf.md)): coordenadas
**0..100** en porcentaje del encuadre, respuesta `[0, {"AFResult": bool, "AFType": "Touch"}]`,
y disponibilidad dependiente de que la cámara anuncie el método (id 45).

Prueba del bucle sin cámara:

```shell
.venv/bin/python -m pytest tests/test_eye_af_*.py -q
.venv/bin/python tools/eye-af/fake_camera.py --image tools/eye-af/tests/data/obama-2012-retrato-dominio-publico.jpg --port 8080 &
.venv/bin/python scripts/eye_af.py --host 127.0.0.1 --dry-run --max-seconds 3
```
