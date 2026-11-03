"""CAM-01: referencias a callbacks y ausencias medidas en av-cam A6000 fw3.21."""
import sys
sys.path.insert(0, "analysis/camera_closure")
import closure2 as K


def test_callbacks_registrados_por_puntero():
    for f, site in [(0x437b8774, "0x437b92f6"), (0x437b7778, "0x437b74fc"), (0x436ea2d0, "0x436ea36a"), (0x43705d64, "0x43705dfa")]:
        assert K.refs(f)["pic"] == [site]


def test_sin_referencias_estaticas():
    for f in (0x436fecbe, 0x436fee80, 0x438786c4, 0x43879204, 0x438792dc, 0x4387938e):
        assert not any(K.refs(f).values())
