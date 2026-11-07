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


@pytest.mark.skipif(not DARWIN.is_file(), reason="darwin_core.bin original ausente")
def test_retardo_de_a_se_satura_a_1():
    """R68: en la rama S+0x48 < −150, si S+0x48 + B86 >= 0 el retardo de A vale 1 µs (limita E26-R66-B86)."""
    seq = _dis(0x18E6A, 7)
    assert seq[0] == "adds r0, r1, r0"
    assert seq[4:7] == ["bmi #0x18e7c", "mov.w r0, #-1", "rsbs r0, r0, #0"]


@pytest.mark.skipif(not DARWIN.is_file(), reason="darwin_core.bin original ausente")
def test_patron_de_imanes():
    """R69: P4D (delantera) se retiene antes y se suelta al bajar en A; P4E (trasera) solo sube en B y baja después (pulso)."""
    assert _dis(0x20CA6, 2) == ["movs r1, #1", "mov.w r0, #0x234"]      # 0x20c90: P4D <- 1 (preparación)
    assert _dis(0x20CC8, 2) == ["movs r1, #0", "mov.w r0, #0x234"]      # 0x20cb2 (A): P4D <- 0
    assert _dis(0x20CE2, 2) == ["movs r1, #0", "mov.w r0, #0x238"]      # 0x20cd4: P4E <- 0 (fin del pulso)
    assert "bl #0x20cd4" in _dis(0x207BE, 3)                            # paso temporizado de la lista
