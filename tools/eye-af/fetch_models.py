#!/usr/bin/env python3
"""Descarga y verifica el modelo de detección de caras YuNet (ONNX).

Origen y licencia
-----------------
* Modelo: YuNet, ``face_detection_yunet_2023mar.onnx``.
* Distribución: OpenCV Zoo, ruta ``models/face_detection_yunet/`` del repo
  https://github.com/opencv/opencv_zoo (repositorio bajo licencia Apache-2.0).
* Autoría/pesos originales: Shiqi Yu et al., repo ``ShiqiYu/libfacedetection.train``
  (licencia BSD-3-Clause), paper "YuNet: A Tiny Millisecond-level Face Detector".
* El fichero se sirve vía Git LFS, por eso se usa ``media.githubusercontent.com``
  (``raw.githubusercontent.com`` devuelve el puntero LFS de 131 bytes, no el modelo).

El SHA-256 y el tamaño están fijados aquí y se comprueban antes de dar el modelo
por bueno; el puntero LFS del propio repositorio declara el mismo ``oid sha256``.
El modelo pesa 232 589 B (< 1 MB), así que se versiona sin entrada de .gitignore.

Uso:
    python tools/eye-af/fetch_models.py [--dest tools/eye-af/models] [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

MODEL_NAME = "face_detection_yunet_2023mar.onnx"
MODEL_URL = (
    "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/"
    "models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
MODEL_SHA256 = "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"
MODEL_SIZE = 232_589
MODEL_LICENSE = "Apache-2.0 (OpenCV Zoo) sobre pesos BSD-3-Clause (ShiqiYu/libfacedetection.train)"

DEFAULT_DEST = Path(__file__).resolve().parent / "models"


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(path: Path) -> None:
    """Lanza RuntimeError si el fichero no coincide con el SHA-256/tamaño fijados."""
    size = path.stat().st_size
    if size != MODEL_SIZE:
        raise RuntimeError(f"tamaño inesperado en {path}: {size} != {MODEL_SIZE}")
    got = sha256_of(path)
    if got != MODEL_SHA256:
        raise RuntimeError(f"SHA-256 no coincide en {path}: {got} != {MODEL_SHA256}")


def fetch(dest_dir: Path, force: bool = False) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / MODEL_NAME
    if target.exists() and not force:
        verify(target)
        print(f"[ok] ya presente y verificado: {target}")
        return target

    tmp = target.with_suffix(target.suffix + ".part")
    print(f"[..] descargando {MODEL_URL}")
    print(f"[..] licencia: {MODEL_LICENSE}")
    with urllib.request.urlopen(MODEL_URL, timeout=120) as response, tmp.open("wb") as out:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} al descargar {MODEL_URL}")
        while True:
            chunk = response.read(1 << 16)
            if not chunk:
                break
            out.write(chunk)
    try:
        verify(tmp)
    except RuntimeError:
        tmp.unlink(missing_ok=True)
        raise
    tmp.replace(target)
    print(f"[ok] {target} ({MODEL_SIZE} B, sha256 {MODEL_SHA256})")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Descarga el ONNX de YuNet y verifica su SHA-256 fijado.")
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST, help=f"directorio destino (por defecto {DEFAULT_DEST})")
    parser.add_argument("--force", action="store_true", help="redescargar aunque ya exista")
    args = parser.parse_args(argv)
    try:
        fetch(args.dest, force=args.force)
    except (RuntimeError, OSError) as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
