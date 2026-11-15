"""G63 Flicker Scan: la exposición Silent se redondea al periodo del parpadeo (584 líneas = 100 Hz, 486 = 120 Hz). Unicorn sobre el av-cam del CFW."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/g22"), str(ROOT / "scripts/g38"), str(ROOT / "scripts/g63")]
TAR = ROOT / "analysis/gui/g22/base-pp.tar"
pytest.importorskip("unicorn")
pytest.importorskip("keystone")


@pytest.fixture(scope="module")
def avcam():
    if not TAR.exists():
        pytest.skip("sin base-pp.tar (no versionado)")
    from e25_27 import build, fatimg, tarball, tpzl
    m = {e.name: e.data for e in tarball.parse(TAR.read_bytes())[0]}
    return fatimg.Fat16.parse(tpzl.TpzlImage.parse(m[build.NFLASHA3]).decompressed()).read(build.AVCAM_NAME)


def test_flicker(avcam):
    import flicker_scan_patch as F
    import patch_silent_r5_sublinea as S
    img = F.apply_bytes(avcam)
    n = lambda tv, o, s=1: 4252 - F.emular(img, tv, o, s)[1]
    base = lambda tv: 4252 - S.emular(S.apply_bytes(avcam), tv)[1]
    for tv in (0x1600, 0x1800, 0x1A00, 0x1C00):          # 1/60, 1/250, 1/1000, 1/4000
        assert n(tv, 0) == base(tv)                       # Off = comportamiento de Silent sin tocar
    assert base(0x1600) == 911 and n(0x1600, 1) == 1168    # 1/60 = 15 625 µs -> 2 periodos de 100 Hz
    assert n(0x1600, 2) == 972                             # 120 Hz: 2 × 486
    assert n(0x1800, 1) == base(0x1800) and n(0x1800, 2) == base(0x1800)   # 1/250 < periodo: sin tocar
    assert n(0x1600, 1, 0) == 4252 - 1 or F.emular(img, 0x1600, 1, 0)[1:] == (1, 3)   # Silent off: no se toca
    assert n(0x1400, 1) % 584 == 0 and n(0x1400, 2) % 486 == 0   # 1/16 s
    assert n(0x1600, 9) == base(0x1600)                    # byte fuera de la tabla = Off
