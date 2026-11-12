"""G22-A: el control BIONZ de la auditoría acepta 3.38 + tres estados, o + PP + Silent calibrado (exacto), y rechaza cualquier byte de más."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/fwtool"))
AVCAM = ROOT / "analysis/e25-27/artifacts-338/av-cam.integrated.bin"
pytestmark = pytest.mark.skipif(not AVCAM.is_file(), reason="av-cam del 3.38 ausente")


def test_control_bionz_g22():
    pytest.importorskip("keystone")
    import audit_package_nflasha15 as AU
    import build_base_pp
    from g22 import patch_tristate as P

    base = AVCAM.read_bytes()
    tri = P.apply_bytes(base)[0]
    cfw = build_base_pp.bionz_cfw(tri)
    assert all(AU.bionz_g22_checks(base, tri).values())
    assert all(AU.bionz_g22_checks(base, cfw).values())
    import pp_bw_mono_patch
    import pp_bwhl_patch
    import pp_slog3_core_patch
    for a, _, new, _ in pp_slog3_core_patch.PATCHES:                  # G33-B §10 (3.81): S-Log3, B&W y Hi-Light en el núcleo
        assert cfw[a - P.BASE:a - P.BASE + len(new)] == new
    assert cfw[pp_bw_mono_patch.SITE - P.BASE:pp_bw_mono_patch.END - P.BASE] != tri[pp_bw_mono_patch.SITE - P.BASE:pp_bw_mono_patch.END - P.BASE]
    assert any(cfw[pp_bwhl_patch.CAVE - P.BASE:pp_bwhl_patch.CAVE - P.BASE + 0x24])
    malo = bytearray(cfw)
    malo[0x2000] ^= 1                                   # un byte fuera de los parches documentados
    assert not any(AU.bionz_g22_checks(base, bytes(malo)).values())
