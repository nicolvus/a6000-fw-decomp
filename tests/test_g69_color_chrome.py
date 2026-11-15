"""G69 Color Chrome / Film: suma a Saturación y Color Depth del paquete de colorimetría del av-cam. Unicorn sobre los bytes reales."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/g22"), str(ROOT / "scripts/g38"), str(ROOT / "scripts/g69")]
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
pytest.importorskip("unicorn")
pytest.importorskip("keystone")
pytest.importorskip("capstone")


@pytest.fixture(scope="module")
def img():
    return AVCAM.read_bytes()


def test_bytes_originales_y_diff_acotado(img):
    import color_chrome_patch as C
    assert img[C.HOOK - C.BASE:C.HOOK - C.BASE + 4] == C.HOOK_OLD
    assert not any(img[C.CAVE - C.BASE:C.CAVE_END - C.BASE])
    p = C.apply_bytes(img)
    dif = [i for i in range(len(img)) if img[i] != p[i]]
    assert all(C.HOOK - C.BASE <= i < C.HOOK - C.BASE + 4 or C.CAVE - C.BASE <= i < C.CAVE_END - C.BASE for i in dif)
    with pytest.raises(ValueError):
        C.apply_bytes(p)                       # idempotencia: sobre la imagen ya parcheada se rechaza


def test_off_y_fuera_de_tabla_igual_a_fabrica(img):
    import color_chrome_patch as C
    p = C.apply_bytes(img)
    for depth, sat in (((0,) * 6, 0), ((3, -2, 7, -7, 1, 0), 5)):
        base = C.emular(img, None, depth, sat)         # av-cam de fábrica
        assert C.emular(p, 0, depth, sat) == base
        assert C.emular(p, 9, depth, sat) == base          # byte fuera de la tabla = Off


def test_filas_suman_al_usuario_y_recortan(img):
    import color_chrome_patch as C
    p = C.apply_bytes(img)
    # cfg 0x148…0x14d = R, G, B, C, M, Y; el paquete 0x2a…0x2f = R, Y, G, C, B, M
    usuario = (1, -3, 6, -7, 0, 2)
    pk = [usuario[0], usuario[5], usuario[1], usuario[3], usuario[2], usuario[4]]
    for k in range(1, len(C.FILAS)):
        s, d, flag = C.emular(p, k, usuario, 2)
        f = C.FILAS[k]
        assert flag == 1
        assert s == max(-7, min(7, 2 + f[0]))
        assert d == [max(-7, min(7, a + b)) for a, b in zip(pk, f[1:])]


def test_saturacion_menos_8_bw_no_se_toca(img):
    import color_chrome_patch as C
    p = C.apply_bytes(img)
    assert C.emular(p, 4, (0,) * 6, -8)[0] == -8


def test_convive_con_silent_y_pp(img):
    """Las cuevas de Silent (0x43FB7E00) y de pp_tone (0x43FB7500…) no se pisan con la de Color Chrome."""
    import color_chrome_patch as C
    import patch_silent_r5 as R
    assert C.CAVE_END <= R.CAVE
    import pp_tone_patch as T
    assert C.CAVE >= T.CODE + 970
