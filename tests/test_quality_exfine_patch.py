"""G39 — parche «Extra fine» (scripts/gui/quality_exfine_patch.py): 8 bytes, idempotente, rechaza ficheros ajenos."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import quality_exfine_patch as q  # noqa: E402

SO = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/CautionConfig.so"


@pytest.mark.skipif(not SO.exists(), reason="fw321 extraído no disponible")
def test_patch_solo_dos_literales():
    d = SO.read_bytes()
    out = q.patch(d)
    assert [i for i in range(len(d)) if d[i] != out[i]].__len__() <= 8
    assert struct.unpack_from("<II", out, q.LIT_T) == q.NEW
    assert q.patch(out) == out
    with pytest.raises(AssertionError):
        q.patch(d[:q.MASK[0]] + b"\0" * 8 + d[q.MASK[0] + 8:])
