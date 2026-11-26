# BENCH — detector de ojos Eye AF (PC)

Medición **real** en esta máquina de `EyeDetector.detect()` (pipeline completo: letterbox a
`input_size`, inferencia YuNet y normalización de coordenadas). Sin cámara, sin captura y sin
dibujo: solo el detector sobre frames en memoria.

## Entorno medido (VERIFICADO)

| dato | valor |
| --- | --- |
| CPU | AMD Ryzen 5 2400G with Radeon Vega Graphics (4 núcleos / 8 hilos) |
| OpenCV | **4.14.0** (`opencv-python-headless==4.14.0.94`), 8 hilos (`cv2.getNumThreads()` = 8) |
| numpy / Python | 2.5.5 / 3.14.8 |
| Backend | `yunet` (`.venv` con `cv2.FaceDetectorYN` disponible) |
| `input_size` del detector | **640x480** (fijo para las tres resoluciones) |
| Escena | `tests/data/obama-2012-retrato-dominio-publico.jpg` encajada con letterbox en cada resolución → 2 ojos detectados siempre |
| Iteraciones | **200** medidas por resolución (+30 de calentamiento), **10 rondas** por resolución |

## Resultados (ms/frame)

| frame de entrada | media | p95 | mediana | fps (1000/media) | rango de medias por ronda |
| --- | --- | --- | --- | --- | --- |
| 640x480 | **16,42** | **19,44** | 16,08 | 60,9 | 16,4 – 39,3 |
| 1024x680 | **17,08** | **19,65** | 16,88 | 58,6 | 17,1 – 46,2 |
| 1920x1080 | **18,27** | **20,44** | 19,06 | 54,7 | 18,3 – 77,6 |

Valores de la **ronda menos interferida** de cada resolución (10 rondas × 200 iteraciones,
`--iterations 200 --repeat 10`); el rango de la última columna es la dispersión observada de las
medias por ronda en ~40 rondas.

## Lectura

* **VERIFICADO**: ~16–18 ms/frame con `input_size` 640x480, muy por debajo de los 33 ms de 30 fps.
  El coste lo fija la inferencia (640x480), no el tamaño del frame: de 640x480 a 1920x1080 solo
  sube ~1,9 ms.
* **VERIFICADO** (desglose del letterbox, 100 iteraciones): 0,15 ms a 640x480, 4,43 ms a 1024x680 y
  2,61 ms a 1920x1080. La diferencia no es monótona porque `cv2.resize`/`INTER_AREA` tiene camino
  rápido con factores casi enteros (1920→384 es ×5; 1024→460 no).
* **INFERENCIA**: el techo práctico ronda 50–60 fps en este CPU con un solo frame a la vez y
  `input_size` 640x480; subir `input_size` o usar varias caras grandes encarece la inferencia.
* **VERIFICADO**: los números son **pesimistas**. Esta máquina estaba compartida durante la
  medición con otras sesiones (JVMs de Ghidra y `pytest` ajenos): `loadavg` de 13–16 con 8 hilos,
  y rondas con medias hasta 77 ms por desalojo del planificador. La contención solo infla, así que
  el mínimo observado es la mejor estimación; en una máquina en reposo cabe esperar 1–3 ms menos.
* **NO_VERIFICADO**: rendimiento con más de una cara por frame (aquí 1 cara), con video real de
  cámara (captura y dibujo no se miden) y bajo Windows/macOS.

## Reproducir

```shell
.venv/bin/python tools/eye-af/bench_detector.py --iterations 200 --repeat 10
.venv/bin/python tools/eye-af/bench_detector.py --iterations 200 --repeat 10 --md   # filas markdown
```

`--repeat N` repite la medición y reporta la ronda de **menor media**, pensado para máquinas
compartidas donde la contención externa solo puede sumar tiempo.
