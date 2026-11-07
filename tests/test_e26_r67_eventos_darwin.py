"""E26-R67: evento A de Darwin baja P4C (CA_1ST_CURTAIN_START, 0x230); evento B sube P4E (2ND_CURTAIN_MG, 0x238)."""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
capstone = pytest.importorskip("capstone")
BASE = 0x4200


def _dis(addr: int, n: int) -> list[str]:
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    d = DARWIN.read_bytes()
    return [f"{i.mnemonic} {i.op_str}" for i in md.disasm(d[addr - BASE:addr - BASE + 4 * n], addr)][:n]


@pytest.mark.skipif(not DARWIN.is_file(), reason="darwin_core.bin original ausente")
def test_eventos_a_y_b():
    assert _dis(0x1ECEC, 1) == ["mov.w r2, #0x230"]                      # P4C
    assert _dis(0x16E68, 3)[1:] == ["movs r0, #0", "bl #0x1ecec"]         # A: P4C <- 0
    assert "bl #0x16e68" in _dis(0x202FC, 4)                             # 0x202f2(0) llama a 0x16e68
    assert _dis(0x20D0E, 3) == ["movs r1, #1", "mov.w r0, #0x238", "bl #0x51c0"]  # B: P4E <- 1
    assert "bl #0x20d00" in _dis(0x2042E, 12)                            # 0x2041e(0) llama a 0x20d00
