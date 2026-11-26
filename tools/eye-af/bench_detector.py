#!/usr/bin/env python3
"""Bench del detector de ojos Eye AF: ms/frame (media y p95) por resolución de frame.

Mide el pipeline COMPLETO por frame: ``EyeDetector.detect()`` incluye el letterbox
a ``input_size``, la inferencia YuNet y la conversión a coordenadas normalizadas.
La resolución listada es la del frame de ENTRADA; la inferencia se hace siempre al
``input_size`` del detector (por defecto 640x480), que es lo que fija el coste.

Uso:
    .venv/bin/python tools/eye-af/bench_detector.py                 # tabla de texto
    .venv/bin/python tools/eye-af/bench_detector.py --md            # filas markdown
    .venv/bin/python tools/eye-af/bench_detector.py --iterations 200 --sizes 640x480,1280x720
"""

from __future__ import annotations

import argparse
import platform
import statistics
import sys
import time
from pathlib import Path

import cv2
import numpy as np

TOOL = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL))

from eyeaf import EyeDetector

FACE = TOOL / "tests" / "data" / "obama-2012-retrato-dominio-publico.jpg"
SIZES = [(640, 480), (1024, 680), (1920, 1080)]


def parse_sizes(text: str) -> list[tuple[int, int]]:
    sizes = []
    for item in text.split(","):
        width, height = item.lower().split("x")
        sizes.append((int(width), int(height)))
    return sizes


def make_frame(width: int, height: int) -> np.ndarray:
    """Frame de prueba: la foto real encajada (contain) con barras negras.

    Se usa la misma escena a todas las resoluciones para que los tiempos sean
    comparables; una imagen sintética de ruido daría un coste distinto.
    """
    photo = cv2.imread(str(FACE))
    if photo is None:  # fallback sin red ni datos: degradado suave, sin caras
        return cv2.GaussianBlur(np.full((height, width, 3), 96, np.uint8), (0, 0), 12)
    scale = min(width / photo.shape[1], height / photo.shape[0])
    resized = cv2.resize(
        photo,
        (max(1, round(photo.shape[1] * scale)), max(1, round(photo.shape[0] * scale))),
        interpolation=cv2.INTER_AREA,
    )
    canvas = np.zeros((height, width, 3), np.uint8)
    canvas[: resized.shape[0], : resized.shape[1]] = resized
    return canvas


def cpu_name() -> str:
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "desconocida"


def bench_one(detector: EyeDetector, frame: np.ndarray, iterations: int, warmup: int) -> dict:
    for _ in range(warmup):
        detector.detect(frame)
    times = np.empty(iterations, dtype=np.float64)
    eyes = 0
    for index in range(iterations):
        start = time.perf_counter()
        eyes = len(detector.detect(frame))
        times[index] = (time.perf_counter() - start) * 1000.0
    return {
        "mean": float(times.mean()),
        "median": float(statistics.median(times.tolist())),
        "p95": float(np.percentile(times, 95)),
        "p99": float(np.percentile(times, 99)),
        "min": float(times.min()),
        "max": float(times.max()),
        "eyes": eyes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bench de EyeDetector (ms/frame, media y p95).")
    parser.add_argument("--iterations", type=int, default=200, help="iteraciones medidas por resolución (200)")
    parser.add_argument("--warmup", type=int, default=20, help="iteraciones de calentamiento (20)")
    parser.add_argument("--sizes", default=",".join(f"{w}x{h}" for w, h in SIZES), help="resoluciones WxH separadas por comas")
    parser.add_argument("--input-size", default="640x480", help="input_size del detector, WxH (640x480)")
    parser.add_argument("--model", type=Path, default=None, help="ruta alternativa al ONNX de YuNet")
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="rondas por resolución; se reporta la de menor media (máquina compartida, la contención infla)",
    )
    parser.add_argument("--md", action="store_true", help="imprimir la tabla en markdown")
    args = parser.parse_args(argv)

    input_size = parse_sizes(args.input_size)[0]
    detector = EyeDetector(model_path=args.model, input_size=input_size)
    sizes = parse_sizes(args.sizes)

    print(f"CPU: {cpu_name()}")
    print(f"OpenCV {cv2.__version__} | numpy {np.__version__} | Python {platform.python_version()} | "
          f"hilos cv2 {cv2.getNumThreads()} | backend {detector.backend} | input_size {input_size[0]}x{input_size[1]}")
    print(f"iteraciones medidas: {args.iterations} (calentamiento {args.warmup}), rondas por resolución: {args.repeat}")
    print(f"carga del sistema al empezar: {Path('/proc/loadavg').read_text().split()[0]}")
    print()

    rows = []
    for width, height in sizes:
        frame = make_frame(width, height)
        runs = [bench_one(detector, frame, args.iterations, args.warmup) for _ in range(max(1, args.repeat))]
        result = min(runs, key=lambda r: r["mean"])
        if args.repeat > 1:
            medias = ", ".join(f"{r['mean']:.2f}" for r in runs)
            print(f"  {width}x{height}: medias por ronda [{medias}] ms -> se reporta la menor ({result['mean']:.2f} ms)")
        rows.append((width, height, result))

    if args.md:
        print("| Frame | ms/frame media | ms/frame p95 | ms/frame mediana | fps (media) | ojos detectados |")
        print("| --- | --- | --- | --- | --- | --- |")
        for width, height, r in rows:
            print(f"| {width}x{height} | {r['mean']:.2f} | {r['p95']:.2f} | {r['median']:.2f} | "
                  f"{1000.0 / r['mean']:.1f} | {r['eyes']} |")
        return 0

    header = f"{'frame':>11} | {'media':>8} | {'p95':>8} | {'mediana':>8} | {'p99':>8} | {'max':>8} | {'fps':>6} | ojos"
    print(header)
    print("-" * len(header))
    for width, height, r in rows:
        print(f"{f'{width}x{height}':>11} | {r['mean']:>7.2f} | {r['p95']:>7.2f} | {r['median']:>7.2f} | "
              f"{r['p99']:>7.2f} | {r['max']:>7.2f} | {1000.0 / r['mean']:>6.1f} | {r['eyes']:>4}")
    print("\nms/frame; fps = 1000/media (un solo hilo de proceso, sin captura ni dibujo).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
