"""Cliente del Camera Remote API y parser de Live View (sin cámara: servidor falso)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "eye-af"))

from eyeaf.api import CameraError, CameraRemoteAPI
from eyeaf.liveview import iter_jpeg
from fake_camera import FakeCamera

JPG_A = b"\xff\xd8" + b"AAA" + b"\xff\xd9"
JPG_B = b"\xff\xd8" + b"BBB" + b"\xff\xd9"


def test_iter_jpeg_tolera_basura_y_cabeceras():
    stream = b"\r\n--boundary\r\nContent-Type: image/jpeg\r\n\r\n" + JPG_A
    stream += b"\r\n--boundary\r\n\r\n" + JPG_B + b"\r\n--boundary--\r\n"

    import io

    got = list(iter_jpeg(io.BytesIO(stream)))
    assert got == [JPG_A, JPG_B]


def test_api_descubre_y_registra_el_punto_de_af():
    with FakeCamera([JPG_A]) as cam:
        api = CameraRemoteAPI("127.0.0.1", cam.port, timeout=5)
        assert api.versions() == ["1.0"]
        assert "setTouchAFPosition" in api.method_types()
        assert "setTouchAFPosition" in api.available_api_list()
        assert api.start_liveview() == f"{cam.url}/liveviewstream"
        api.set_touch_af(0.25, 0.75)
        assert cam.af_calls == [(0.25, 0.75)]
        assert api.get_touch_af() == [[0.25, 0.75]]
        api.cancel_touch_af()
        assert cam.cancels == 1
        api.set_focus_mode("AF-C")
        assert cam.focus_modes == ["AF-C"]
        ev = api.get_event()
        assert ev["cameraStatus"] == "IDLE" and ev["touchAFPosition"] == [0.25, 0.75]


def test_respuesta_de_af_se_interpreta():
    from eyeaf.api import parse_af_result

    assert parse_af_result([0, {"AFResult": True, "AFType": "Touch"}]) is True
    assert parse_af_result([0, {"AFResult": False, "AFType": "Touch"}]) is False
    assert parse_af_result([]) is None
    assert parse_af_result([0]) is None


def test_api_propaga_el_error_de_la_camara():
    with FakeCamera([JPG_A]) as cam:
        api = CameraRemoteAPI("127.0.0.1", cam.port, timeout=5)
        with pytest.raises(CameraError) as e:
            api.call("metodoInexistente")
        assert "No Such Method" in str(e.value)


def test_wait_for_method_encuentra_la_api():
    from eyeaf.api import wait_for_method

    with FakeCamera([JPG_A]) as cam:
        api = CameraRemoteAPI("127.0.0.1", cam.port, timeout=5)
        assert wait_for_method(api, "setTouchAFPosition", timeout=1.0, period=0.05) is True
        assert wait_for_method(api, "noExiste", timeout=0.2, period=0.05) is False
