"""G43 — parche de lista ISO (scripts/gui/iso_list_patch.py): 8 bytes, idempotente, rechaza ficheros ajenos."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import iso_list_patch as p  # noqa: E402

SO = ROOT / "analysis/camera-extract/usr/lib/CautionConfig.so"


@pytest.mark.skipif(not SO.exists(), reason="camera-extract no disponible")
def test_patch_solo_dos_literales():
    d = SO.read_bytes()
    out = p.patch(d)
    assert sum(a != b for a, b in zip(d, out)) <= 8
    assert struct.unpack_from("<II", out, p.LIT[0]) == p.NEW
    assert p.patch(out) == out
    with pytest.raises(AssertionError):
        p.patch(d[:p.LIT[0]] + b"\0" * 8 + d[p.LIT[0] + 8:])
