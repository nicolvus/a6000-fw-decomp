"""G38-A: el tope de r5 de Silent pasa de 4218 a 4251; 1/8000 → r5 = 4245 (7 líneas ≈ 120 µs en la ley R87). Emulado sobre el av-cam 3.75."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/g22"), str(ROOT / "scripts/g38")]
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


def test_sublinea(avcam):
    import patch_silent_r5 as R0
    import patch_silent_r5_sublinea as S
    img = S.apply_bytes(avcam)
    assert R0.R5_FULL == 4219 and R0.R5_LAG == 33          # el módulo original queda intacto
    assert S.emular(img, 0x1CF7)[1:] == (4245, 0)          # 1/8000
    assert S.emular(img, 0x1BF7)[1:] == (4238, 0)          # 1/4000
    assert S.emular(img, 0x1800)[1:] == (4025, 0)          # 1/250 igual que R87
    assert S.emular(img, 0x1CF7, silent=0)[1:] == (1, 3)   # Silent off: no se toca
    assert 115 < S.exposicion_us(4245) < 125
