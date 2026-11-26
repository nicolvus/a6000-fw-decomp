"""Bucle completo sin cámara: Live View (servidor falso) -> ojo -> punto de AF."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "eye-af"))

from eyeaf.api import CameraRemoteAPI
from eyeaf.liveview import LiveviewStream
from eyeaf.loop import EyeAF, to_camera
from eyeaf.tracker import EyeTracker
from fake_camera import FakeCamera

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")


@dataclass
class Eye:
    x: float
    y: float
    confidence: float = 0.9
    side: str = "right"
    face_box: tuple = (0.2, 0.2, 0.3, 0.3)


class StubDetector:
    def __init__(self, eyes):
        self.eyes = eyes
        self.frames = 0

    def detect(self, frame):
        self.frames += 1
        assert frame.shape[:2] == (48, 64)
        return list(self.eyes)


def jpeg(w=64, h=48):
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :, 1] = 80
    ok, buf = cv2.imencode(".jpg", img)
    assert ok
    return buf.tobytes()


@pytest.mark.parametrize("mode,esperado", [
    ("percent", (25.0, 50.0)),
    ("normalized", (0.25, 0.5)),
    ("centered", (-0.5, 0.0)),
    ("pixels", (16.0, 24.0)),
])
def test_conversion_de_coordenadas(mode, esperado):
    assert to_camera(0.25, 0.5, mode, 64, 48) == esperado


@pytest.mark.parametrize("mode,esperado", [
    ("percent", (25.0, 50.0)),
    ("normalized", (0.25, 0.5)),
])
def test_bucle_completo_mueve_el_punto_de_af(mode, esperado):
    with FakeCamera([jpeg()], fps=200.0) as cam:
        api = CameraRemoteAPI("127.0.0.1", cam.port, timeout=5)
        url = api.start_liveview()
        detector = StubDetector([Eye(0.25, 0.5)])
        app = EyeAF(api, detector, EyeTracker(min_move=0.0, max_hz=1000.0, smooth=1.0), coord=mode)
        with LiveviewStream(url, timeout=5) as stream:
            stats = app.run_frames(stream.frames(), max_frames=3, verbose=False)
        assert stats.frames == 3
        assert detector.frames == 3
        assert cam.af_calls, "no se envió ninguna orden de AF"
        assert cam.af_calls[-1] == pytest.approx(esperado, abs=1e-6)


def test_dry_run_no_toca_la_camara():
    with FakeCamera([jpeg()], fps=200.0) as cam:
        api = CameraRemoteAPI("127.0.0.1", cam.port, timeout=5)
        url = api.start_liveview()
        app = EyeAF(api, StubDetector([Eye(0.5, 0.5)]), EyeTracker(min_move=0.0), dry_run=True)
        with LiveviewStream(url, timeout=5) as stream:
            app.run_frames(stream.frames(), max_frames=2, verbose=False)
        assert cam.af_calls == []


def test_cancela_cuando_desaparece_el_ojo():
    class Sequencer:
        def __init__(self):
            self.n = 0

        def detect(self, frame):
            self.n += 1
            return [Eye(0.4, 0.4)] if self.n <= 1 else []

    with FakeCamera([jpeg()], fps=200.0) as cam:
        api = CameraRemoteAPI("127.0.0.1", cam.port, timeout=5)
        url = api.start_liveview()
        app = EyeAF(api, Sequencer(), EyeTracker(min_move=0.0, max_hz=1000.0, lost_after=0.0))
        with LiveviewStream(url, timeout=5) as stream:
            app.run_frames(stream.frames(), max_frames=3, verbose=False)
        assert cam.cancels >= 1


def test_pipeline_real_detector_pone_el_punto_en_el_ojo():
    """Visión real -> coordenadas -> orden de AF, con el retrato de prueba."""
    img_path = ROOT / "tools" / "eye-af" / "tests" / "data" / "obama-2012-retrato-dominio-publico.jpg"
    model = ROOT / "tools" / "eye-af" / "models" / "face_detection_yunet_2023mar.onnx"
    if not img_path.exists() or not model.exists():
        pytest.skip("falta la imagen o el modelo del detector")
    frame = cv2.imread(str(img_path))
    ok, buf = cv2.imencode(".jpg", frame)
    assert ok
    from eyeaf import EyeDetector

    detector = EyeDetector(model_path=model)
    with FakeCamera([buf.tobytes()], fps=200.0) as cam:
        api = CameraRemoteAPI("127.0.0.1", cam.port, timeout=5)
        url = api.start_liveview()
        app = EyeAF(api, detector, EyeTracker(min_move=0.0, max_hz=1000.0, smooth=1.0))
        with LiveviewStream(url, timeout=5) as stream:
            app.run_frames(stream.frames(), max_frames=2, verbose=False)
    assert cam.af_calls, "no se envió ninguna orden de AF"
    x, y, *_ = cam.af_calls[-1]
    # la API de la A6000 espera porcentaje 0..100 (orb-server, fw3.21)
    assert 35.0 < x < 65.0, f"x fuera de la zona de los ojos: {x}"
    assert 10.0 < y < 28.0, f"y fuera de la zona de los ojos: {y}"
