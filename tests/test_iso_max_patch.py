"""G42 — parche MAX de ISO en libObj (scripts/gui/iso_max_patch.py): bytes, idempotencia y ejecución Unicorn del fragmento."""
import sys
from pathlib import Path

import capstone
import pytest
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R7, UC_ARM_REG_R0, UC_ARM_REG_R1

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import iso_max_patch as p  # noqa: E402

SO = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
pytestmark = pytest.mark.skipif(not SO.exists(), reason="fw321 extraído no disponible")


def test_bytes_e_idempotencia():
    d = SO.read_bytes()
    out = p.patch(d)
    assert sum(a != b for a, b in zip(d, out)) <= 14 and len(out) == len(d)
    assert p.patch(out) == out
    with pytest.raises(AssertionError):
        p.patch(d[:p.SITE] + b"\0" * 14 + d[p.SITE + 14:])


def test_desensamblado():
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    txt = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(p.NEW, p.SITE)]
    assert txt == ["ldr r1, [r7, #0x38]", "sub.w r2, r1, #0x26", "cmp r2, #3", "it lo", "movlo r1, #0x29", "str r1, [r7, #0x38]"]


def _run(code: bytes, k: int) -> int:
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0x1000, 0x1000)
    mu.mem_map(0x8000, 0x1000)
    mu.mem_write(0x1000, code)
    mu.mem_write(0x8038, k.to_bytes(4, "little"))
    mu.reg_write(UC_ARM_REG_R7, 0x8000)
    mu.emu_start(0x1000 | 1, 0x1000 + len(code))
    return int.from_bytes(mu.mem_read(0x8038, 4), "little")


def test_clamp_unicorn():
    for k in range(0x4B):
        exp = 0x29 if 0x26 <= k <= 0x28 else k
        assert _run(p.NEW, k) == exp, hex(k)
