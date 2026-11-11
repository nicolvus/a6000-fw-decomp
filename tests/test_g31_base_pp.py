"""G31: el parche PP del núcleo va en la imagen (nflasha3): mismo núcleo que dejaba pp_ram.sh, TPZL sin violaciones de hardware y sumas válidas."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "scripts"))
BASE = ROOT / "analysis/gui/g22/base-357.tar"
pytestmark = pytest.mark.skipif(not BASE.is_file(), reason="base-357.tar ausente")


def test_imagen_con_pp_equivale_al_nucleo_de_pp_ram(tmp_path):
    import build_base_pp
    import pp_curves_patch
    from e25_27 import build, fatimg, sums, tarball, tpzl
    res = build_base_pp.main(BASE, tmp_path / "b.tar")
    m = {e.name: e.data for e in tarball.parse((tmp_path / "b.tar").read_bytes())[0]}
    img = tpzl.TpzlImage.parse(m[build.NFLASHA3])
    assert tpzl.hardware_violations(img) == [] and sums.verify(m[build.PART_SUM].decode(), build.PART_ENTRY, m[build.NFLASHA3])
    base = {e.name: e.data for e in tarball.parse(BASE.read_bytes())[0]}
    b0 = fatimg.Fat16.parse(tpzl.TpzlImage.parse(base[build.NFLASHA3]).decompressed()).read(build.AVCAM_NAME)
    b1 = fatimg.Fat16.parse(img.decompressed()).read(build.AVCAM_NAME)
    pp_curves_patch.main(_escribe(tmp_path, b0), tmp_path / "pp", None, color=True)
    assert b1 == (tmp_path / "pp/av-cam.pp.bin").read_bytes() and b1 != b0 and res["bytes_cambiados"] > 30000


def _escribe(d, data):
    (d / "x.bin").write_bytes(data)
    return d / "x.bin"
