"""Lectura del flujo de Live View de la cámara como secuencia de JPEG.

El servidor de la cámara entrega los cuadros como un flujo continuo (multipart o
trozos con cabecera). Delimitar por SOI/EOI de JPEG evita depender del *boundary*
y tolera cabeceras distintas entre modelos. Solo stdlib + numpy/opencv para decodificar.
"""
from __future__ import annotations

import urllib.request
from collections.abc import Iterator
from typing import Self

SOI = b"\xff\xd8"
EOI = b"\xff\xd9"


def iter_jpeg(stream, chunk_size: int = 64 * 1024) -> Iterator[bytes]:
    """Genera los JPEG completos que aparecen en un flujo de bytes."""
    buf = bytearray()
    started = False
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            return
        buf += chunk
        while True:
            if not started:
                i = buf.find(SOI)
                if i < 0:
                    del buf[:-1]  # conserva un byte por si el SOI queda partido
                    break
                del buf[:i]
                started = True
            j = buf.find(EOI, 2)
            if j < 0:
                break
            yield bytes(buf[: j + 2])
            del buf[: j + 2]
            started = False


class LiveviewStream:
    """Flujo de Live View; úsalo como iterador de JPEG o con ``frames()`` para BGR."""

    def __init__(self, url: str, timeout: float = 10.0) -> None:
        self.url = url
        self.timeout = timeout
        self._resp = None

    def __enter__(self) -> Self:
        self._resp = urllib.request.urlopen(self.url, timeout=self.timeout)
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        if self._resp is not None:
            self._resp.close()
            self._resp = None

    def jpegs(self) -> Iterator[bytes]:
        if self._resp is None:
            raise RuntimeError("LiveviewStream usado fuera de contexto")
        yield from iter_jpeg(self._resp)

    def frames(self) -> Iterator:
        """Genera cuadros BGR (requiere OpenCV)."""
        import cv2
        import numpy as np

        for jpg in self.jpegs():
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                yield img
