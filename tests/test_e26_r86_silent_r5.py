"""E26-R86: Silent calibrado en la imagen BIONZ (ShutMode 0 + r5 desde Tv), emulado con Unicorn sobre el av-cam del CFW."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/g22")]
TAR = ROOT / "analysis/gui/g22/pkg-375w/base-pp.tar"
pytest.importorskip("unicorn")
pytest.importorskip("keystone")


@pytest.fixture(scope="module")
def avcam():
    if not TAR.exists():
        pytest.skip("sin base-pp.tar del 3.75 (no versionado)")
    from e25_27 import build, fatimg, tarball, tpzl
    m = {e.name: e.data for e in tarball.parse(TAR.read_bytes())[0]}
    return fatimg.Fat16.parse(tpzl.TpzlImage.parse(m[build.NFLASHA3]).decompressed()).read(build.AVCAM_NAME)


def test_r5_como_r56(avcam):
    import patch_silent_r5 as R
    img = R.apply_bytes(avcam)
    assert R.emular(img, 0x1600) == (0x1234, 3341, 0)      # 1/60 con el ajuste R87
    assert R.emular(img, 0x1800) == (0x1234, 4025, 0)      # 1/250
    assert R.emular(img, 0x1C00)[1:] == (4218, 0)          # 1/4000: acotado a 1 línea
    assert R.emular(img, 0x1300)[1:] == (1, 3)             # 1/8: no cabe en un cuadro, no se toca
    assert R.emular(img, 0x1A00, silent=0)[1:] == (1, 3)   # Silent desactivado: no se toca


def test_no_reaplica(avcam):
    import patch_silent_r5 as R
    from e25_24.patch_bionz import ImageError
    with pytest.raises(ImageError):
        R.apply_bytes(R.apply_bytes(avcam))
