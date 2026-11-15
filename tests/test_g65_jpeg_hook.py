"""G65 (MULTIEXP-ACC F1): gancho contador en Stage_EncodeJpeg_MainYC, Unicorn sobre el av-cam original."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts/g65")]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
pytest.importorskip("unicorn")
pytest.importorskip("keystone")


def test_gancho():
    if not BIN.exists():
        pytest.skip("sin av-cam.bin")
    import jpeg_hook_patch as J
    img = BIN.read_bytes()
    assert img[J.HOOK - J.BASE:J.HOOK - J.BASE + 4] == J.HOOK_OLD
    new = J.apply_bytes(img)
    assert J.emular(img)[1] == 0
    assert J.emular(new, 3) == (1, 3, J.RET_OK)
    with pytest.raises(ValueError):
        J.apply_bytes(new)
