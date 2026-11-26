"""Tests del detector de ojos Eye AF (PC, sin cámara).

Usa una imagen real de dominio público (retrato oficial de la Casa Blanca, ver
``tools/eye-af/tests/data/README.md``). Si falta OpenCV, el módulo ``eyeaf`` o el
ONNX de YuNet, los tests se OMITEN con motivo explícito: nunca fallan por entorno.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "eye-af"
MODEL = TOOL / "models" / "face_detection_yunet_2023mar.onnx"
FACE = TOOL / "tests" / "data" / "obama-2012-retrato-dominio-publico.jpg"

cv2 = pytest.importorskip("cv2", reason="OpenCV ausente: .venv/bin/pip install opencv-python-headless")
np = pytest.importorskip("numpy")
sys.path.insert(0, str(TOOL))
eyeaf = pytest.importorskip("eyeaf", reason=f"módulo eyeaf no importable desde {TOOL}")


def _make_detector(**kwargs):
    """EyeDetector con el modelo por defecto; omite el test si YuNet lo necesita y falta."""
    if hasattr(cv2, "FaceDetectorYN") and not MODEL.is_file():
        pytest.skip(f"falta el modelo YuNet ({MODEL.name}): ejecuta `.venv/bin/python tools/eye-af/fetch_models.py`")
    return eyeaf.EyeDetector(model_path=MODEL, **kwargs)


@pytest.fixture(scope="module")
def detector():
    return _make_detector()


@pytest.fixture(scope="module")
def frame():
    if not FACE.is_file():
        pytest.skip(f"falta la imagen de prueba {FACE}")
    img = cv2.imread(str(FACE))
    assert img is not None, f"no se pudo leer {FACE}"
    return img


def test_detecta_al_menos_un_ojo(detector, frame):
    eyes = detector.detect(frame)
    assert eyes, "no se detectó ningún ojo en un retrato frontal"


def test_coordenadas_normalizadas(detector, frame):
    eyes = detector.detect(frame)
    assert eyes
    for eye in eyes:
        assert 0.0 <= eye.x <= 1.0, f"x fuera de 0..1: {eye.x}"
        assert 0.0 <= eye.y <= 1.0, f"y fuera de 0..1: {eye.y}"
        assert 0.0 <= eye.confidence <= 1.0, f"confidence fuera de 0..1: {eye.confidence}"
        fx, fy, fw, fh = eye.face_box
        assert 0.0 <= fx and 0.0 <= fy and 0.0 <= fw <= 1.0 and 0.0 <= fh <= 1.0
        # el ojo debe caer dentro de la caja de cara detectada
        assert fx <= eye.x <= min(1.0, fx + fw), f"ojo fuera de la caja en x: {eye}"
        assert fy <= eye.y <= min(1.0, fy + fh), f"ojo fuera de la caja en y: {eye}"


def test_dos_ojos_frontales_con_separacion_razonable(detector, frame):
    eyes = detector.detect(frame)
    assert len(eyes) >= 2, f"se esperaban dos ojos en un retrato frontal, hay {len(eyes)}"
    sides = {eye.side for eye in eyes[:2]}
    assert sides == {"left", "right"}, f"lados esperados left/right, obtenidos {sides}"
    right = next(e for e in eyes if e.side == "right")
    left = next(e for e in eyes if e.side == "left")
    # Convención: imagen sin espejar -> el ojo derecho del sujeto está a la izquierda de la imagen.
    assert right.x < left.x, f"ojo derecho del sujeto debería tener menor x ({right.x} vs {left.x})"
    separation = left.x - right.x
    assert 0.02 <= separation <= 0.60, f"separación horizontal anómala: {separation:.3f}"
    assert abs(left.y - right.y) <= 0.05, f"los dos ojos deberían estar a la misma altura ({left.y} vs {right.y})"


def test_dos_caras_y_limite_max_faces(frame):
    # Dos copias del mismo retrato en un solo frame: comprueba NMS por cara y el top_k.
    small = cv2.resize(frame, (320, 400), interpolation=cv2.INTER_AREA)
    pareja = np.hstack([small, small])
    ojos = _make_detector(max_faces=2).detect(pareja)
    assert len(ojos) == 4, f"se esperaban 4 ojos (2 caras), hay {len(ojos)}"
    assert len({eye.face_box for eye in ojos}) == 2, "las dos caras deberían ser cajas distintas"
    assert len(_make_detector(max_faces=1).detect(pareja)) == 2, "max_faces=1 debe limitar a una cara"


def test_imagen_negra_no_devuelve_nada(detector):
    assert detector.detect(np.zeros((480, 640, 3), dtype=np.uint8)) == []


def test_umbral_alto_descarta_caras(frame):
    estricto = _make_detector(score_threshold=0.999)
    assert estricto.detect(frame) == []


def test_admite_gris_y_rechaza_formas_invalidas(detector, frame):
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    assert detector.detect(gris), "un frame en gris debería convertirse a BGR y detectarse"
    with pytest.raises(ValueError):
        detector.detect(np.zeros((16,), dtype=np.uint8))


def test_dataclass_eye_valida_el_lado():
    eye = eyeaf.Eye(x=0.5, y=0.5, confidence=0.9, side="left", face_box=(0.1, 0.1, 0.4, 0.4), face_score=0.9)
    assert eye.side == "left"
    with pytest.raises(ValueError):
        eyeaf.Eye(x=0.5, y=0.5, confidence=0.9, side="centro", face_box=(0.1, 0.1, 0.4, 0.4), face_score=0.9)
