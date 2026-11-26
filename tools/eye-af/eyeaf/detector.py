"""Detector de ojos para el proyecto "Eye AF en tiempo real" (PC, sin cámara).

Ruta principal: YuNet (``cv2.FaceDetectorYN``), que devuelve caja de cara, 5
landmarks (ojo derecho, ojo izquierdo, nariz, comisura derecha, comisura
izquierda) y una puntuación de cara. De los 5 landmarks solo se usan los dos
primeros: YuNet no entrena ojos como clase propia, así que "detectar el ojo" es
aquí "localizar el landmark de ojo".

Degradación: si la versión de OpenCV instalada no expone ``FaceDetectorYN``
(por ejemplo OpenCV 5.x sin el módulo, o un build sin ``objdetect``), se usan
cascadas Haar de OpenCV (``haarcascade_frontalface_default.xml`` +
``haarcascade_eye.xml``). Ver el bloque ``shortcut:`` en ``_detect_haar``.

Coordenadas: ``Eye.x``/``Eye.y`` y ``Eye.face_box`` van NORMALIZADAS 0..1
respecto al frame de entrada (``frame_bgr.shape``), nunca en píxeles.

``side`` se expresa desde el punto de vista del SUJETO: en una foto frontal sin
espejar el ojo del sujeto que aparece a la izquierda de la imagen es su ojo
derecho. Marcado como convención (INFERENCE): un frame espejado o una cara de
perfil invierten o anulan esta lectura, y con un solo ojo visible se devuelve
``'unknown'``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = HERE.parent / "models" / "face_detection_yunet_2023mar.onnx"

# YuNet exige que la entrada sea múltiplo de 32 (modelo de forma estática).
_YUNET_SIZE_MULTIPLE = 32

# Las cascadas Haar no dan probabilidad: se usa una constante fija y documentada.
# shortcut: no es una confianza calibrada, solo "hay detección".
HAAR_CONFIDENCE = 0.5

SIDES = ("left", "right", "unknown")


@dataclass(frozen=True)
class Eye:
    """Ojo detectado, con coordenadas normalizadas 0..1 respecto al frame."""

    x: float
    y: float
    confidence: float
    side: str
    face_box: tuple[float, float, float, float]
    face_score: float

    def __post_init__(self) -> None:
        if self.side not in SIDES:
            raise ValueError(f"side inválido: {self.side!r} (esperado {SIDES})")


class EyeDetector:
    """Detector de ojos sobre frames BGR en memoria.

    Parameters
    ----------
    model_path:
        Ruta al ONNX de YuNet. ``None`` usa ``tools/eye-af/models/face_detection_yunet_2023mar.onnx``.
    score_threshold, nms_threshold:
        Umbrales de cara de YuNet (se aplican al crear el detector).
    input_size:
        Tamaño de inferencia ``(ancho, alto)``. El frame se reescala con
        letterbox conservando la relación de aspecto y se redondea a múltiplo de 32.
    max_faces:
        Máximo de caras por frame (``top_k`` de YuNet).
    """

    def __init__(
        self,
        model_path: str | Path | None = None,
        score_threshold: float = 0.7,
        nms_threshold: float = 0.3,
        input_size: tuple[int, int] = (640, 480),
        max_faces: int = 5,
    ) -> None:
        if max_faces < 1:
            raise ValueError("max_faces debe ser >= 1")
        width, height = (int(input_size[0]), int(input_size[1]))
        if width <= 0 or height <= 0:
            raise ValueError(f"input_size inválido: {input_size!r}")

        self.model_path = Path(model_path) if model_path is not None else DEFAULT_MODEL_PATH
        self.score_threshold = float(score_threshold)
        self.nms_threshold = float(nms_threshold)
        self.input_size = (width, height)
        self.max_faces = int(max_faces)

        self.backend = "yunet" if hasattr(cv2, "FaceDetectorYN") else "haar"
        self._detector = None
        self._face_cascade = None
        self._eye_cascade = None

    # ------------------------------------------------------------------ API

    def detect(self, frame_bgr) -> list[Eye]:
        """Devuelve los ojos detectados (coordenadas normalizadas 0..1)."""
        frame = self._as_bgr(frame_bgr)
        if self.backend == "yunet":
            return self._detect_yunet(frame)
        return self._detect_haar(frame)

    # -------------------------------------------------------------- helpers

    @staticmethod
    def _as_bgr(frame_bgr) -> np.ndarray:
        frame = np.asarray(frame_bgr)
        if frame.ndim == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        if frame.ndim != 3 or frame.shape[2] != 3:
            raise ValueError(f"frame debe ser HxWx3 BGR, recibido shape={frame.shape}")
        if frame.shape[0] < 1 or frame.shape[1] < 1:
            raise ValueError(f"frame vacío: shape={frame.shape}")
        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)
        return frame

    def _yunet_input(self, frame: np.ndarray) -> tuple[np.ndarray, float]:
        """Letterbox a ``input_size`` (múltiplo de 32) y factor de escala aplicado."""
        target_w = max(_YUNET_SIZE_MULTIPLE, (self.input_size[0] // _YUNET_SIZE_MULTIPLE) * _YUNET_SIZE_MULTIPLE)
        target_h = max(_YUNET_SIZE_MULTIPLE, (self.input_size[1] // _YUNET_SIZE_MULTIPLE) * _YUNET_SIZE_MULTIPLE)
        height, width = frame.shape[:2]
        scale = min(target_w / width, target_h / height)
        new_w = max(1, round(width * scale))
        new_h = max(1, round(height * scale))
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
        canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        canvas[:new_h, :new_w] = resized
        return canvas, scale

    def _ensure_yunet(self):
        if self._detector is not None:
            return self._detector
        if not self.model_path.is_file():
            raise FileNotFoundError(
                f"modelo YuNet ausente: {self.model_path}. Ejecuta `python tools/eye-af/fetch_models.py`."
            )
        self._detector = cv2.FaceDetectorYN.create(
            str(self.model_path),
            "",
            self.input_size,
            self.score_threshold,
            self.nms_threshold,
            self.max_faces,
        )
        return self._detector

    @staticmethod
    def _clamp01(value: float) -> float:
        return 0.0 if value < 0.0 else 1.0 if value > 1.0 else float(value)

    # --------------------------------------------------------------- YuNet

    def _detect_yunet(self, frame: np.ndarray) -> list[Eye]:
        detector = self._ensure_yunet()
        canvas, scale = self._yunet_input(frame)
        detector.setInputSize((canvas.shape[1], canvas.shape[0]))
        _, faces = detector.detect(canvas)
        if faces is None:
            return []

        height, width = frame.shape[:2]
        eyes: list[Eye] = []
        rows = sorted((row for row in faces if float(row[-1]) >= self.score_threshold), key=lambda r: -float(r[-1]))
        for row in rows[: self.max_faces]:
            score = float(row[-1])
            fx = self._clamp01(float(row[0]) / scale / width)
            fy = self._clamp01(float(row[1]) / scale / height)
            fw = self._clamp01(float(row[2]) / scale / width)
            fh = self._clamp01(float(row[3]) / scale / height)
            face_box = (fx, fy, fw, fh)
            # Fila de YuNet (15 floats): x, y, w, h, ojo_derecho(x,y), ojo_izquierdo(x,y),
            # nariz(x,y), comisura_der(x,y), comisura_izq(x,y), score.
            # El primer ojo (índices 4-5) es el del SUJETO a la izquierda de la imagen.
            for offset, side in ((4, "right"), (6, "left")):
                ex = self._clamp01(float(row[offset]) / scale / width)
                ey = self._clamp01(float(row[offset + 1]) / scale / height)
                eyes.append(
                    Eye(
                        x=ex,
                        y=ey,
                        confidence=score,
                        side=side,
                        face_box=face_box,
                        face_score=score,
                    )
                )
        return eyes

    # ---------------------------------------------------------------- Haar

    def _ensure_haar(self):
        if self._face_cascade is not None:
            return self._face_cascade, self._eye_cascade
        base = Path(cv2.data.haarcascades)
        self._face_cascade = cv2.CascadeClassifier(str(base / "haarcascade_frontalface_default.xml"))
        self._eye_cascade = cv2.CascadeClassifier(str(base / "haarcascade_eye.xml"))
        if self._face_cascade.empty() or self._eye_cascade.empty():
            raise RuntimeError(f"cascadas Haar no encontradas en {base}")
        return self._face_cascade, self._eye_cascade

    def _detect_haar(self, frame: np.ndarray) -> list[Eye]:
        """Degradación con cascadas Haar (sin landmarks).

        shortcut: esta ruta es un apaño de compatibilidad, no un detector de ojos
        equivalente. Limitaciones explícitas:
          * no hay landmarks ni probabilidad calibrada (``HAAR_CONFIDENCE`` fijo);
          * ``haarcascade_eye.xml`` busca ojos abiertos y frontales: parpadeos,
            gafas, perfil y ojos pequeños fallan;
          * el lado solo se deduce si aparecen DOS ojos (se ordenan por x);
            con uno solo se devuelve ``'unknown'``;
          * ``haarcascade_frontalface_default`` no cubre caras giradas ni tapadas.
        """
        face_cascade, eye_cascade = self._ensure_haar()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        height, width = gray.shape[:2]
        min_side = max(24, round(min(height, width) * 0.08))
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(min_side, min_side)
        )
        if len(faces) == 0:
            return []

        boxes = sorted((tuple(int(v) for v in box) for box in faces), key=lambda b: -b[2] * b[3])
        eyes: list[Eye] = []
        for x, y, w, h in boxes[: self.max_faces]:
            face_box = (
                self._clamp01(x / width),
                self._clamp01(y / height),
                self._clamp01(w / width),
                self._clamp01(h / height),
            )
            # Los ojos viven en la mitad superior de la cara; recortar evita que la
            # cascada de ojos dispare sobre boca/nariz.
            roi = gray[y : y + int(h * 0.6), x : x + w]
            found = eye_cascade.detectMultiScale(roi, scaleFactor=1.1, minNeighbors=4)
            if len(found) == 0:
                continue
            candidates = sorted((tuple(int(v) for v in e) for e in found), key=lambda e: -e[2] * e[3])
            # Con dos ojos en la misma cara se puede deducir el lado: el de menor x
            # es el ojo derecho del sujeto (convención de imagen sin espejar).
            pair = sorted(candidates[:2], key=lambda e: e[0])
            for index, (ex, ey, ew, eh) in enumerate(pair):
                side = "unknown"
                if len(pair) == 2:
                    side = "right" if index == 0 else "left"
                eyes.append(
                    Eye(
                        x=self._clamp01((x + ex + ew / 2) / width),
                        y=self._clamp01((y + ey + eh / 2) / height),
                        confidence=HAAR_CONFIDENCE,
                        side=side,
                        face_box=face_box,
                        face_score=HAAR_CONFIDENCE,
                    )
                )
        return eyes
