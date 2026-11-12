"""G32-C: con pp_slog3_core_patch, la gamma 0x17 (S-Log3) toma las ramas de 0x14 (S-Log2). Emula con Unicorn solo los tramos de decisión."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import pp_slog3_core_patch as P

pytest.importorskip("unicorn")
from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_R5,
    UC_ARM_REG_R7,
)

AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
pytestmark = pytest.mark.skipif(not AVCAM.is_file(), reason="falta av-cam.bin")
ORIG = AVCAM.read_bytes() if AVCAM.is_file() else b""
PATCHED = P.apply(ORIG) if ORIG else b""


def run(img: bytes, start: int, stops: set[int], regs: dict[int, int]) -> tuple[int, int]:
    """Ejecuta desde start hasta una dirección de stops; devuelve (pc, r7)."""
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    lo = (start - 0x1000) & ~0xFFF
    uc.mem_map(lo, 0x2000)
    uc.mem_write(lo, img[lo - P.BASE:lo - P.BASE + 0x2000])
    tab = 0x43BC8000
    uc.mem_map(tab, 0x1000)
    uc.mem_write(tab, img[tab - P.BASE:tab - P.BASE + 0x1000])
    for r, v in regs.items():
        uc.reg_write(r, v)
    pc = start
    for _ in range(40):
        uc.emu_start(pc | 1, 0, count=1)
        pc = uc.reg_read(UC_ARM_REG_PC)
        if pc in stops:
            return pc, uc.reg_read(UC_ARM_REG_R7)
    raise AssertionError("sin salida")


A_STOPS = {0x4386783E, 0x4386784C}
B_END = {0x4386797E}


def a(img, g):  # 0x438677e0, modo 2 con bandera
    return run(img, 0x43867836, A_STOPS, {UC_ARM_REG_R5: g})[0]


def b(img, g, r3=0, mode1=False):  # 0x438678ac: clase r7
    regs = {UC_ARM_REG_R2: g, UC_ARM_REG_R3: r3, UC_ARM_REG_R0: 0, UC_ARM_REG_R7: 1}
    return run(img, 0x43867902 if mode1 else 0x4386790C, B_END, regs)[1]


def test_original_excluye_0x17():
    assert a(ORIG, 0x17) != a(ORIG, 0x14)
    assert b(ORIG, 0x17) != b(ORIG, 0x14)
    assert b(ORIG, 0x17, mode1=True) == 0


@pytest.mark.parametrize("r3", [0, 0x20, 0x29])
def test_parche_0x17_como_0x14(r3):
    assert a(PATCHED, 0x17) == a(PATCHED, 0x14) == 0x4386783E
    assert b(PATCHED, 0x17, r3) == b(PATCHED, 0x14, r3) in (8, 9)
    assert b(PATCHED, 0x17, mode1=True) == b(PATCHED, 0x14, mode1=True) == 8


@pytest.mark.parametrize("g", [0, 1, 0x0A, 0x13, 0x14, 0x15, 0x16, 0x18, 0x1B, 0x1E])
def test_resto_de_gammas_igual(g):
    assert a(PATCHED, g) == a(ORIG, g)
    assert b(PATCHED, g) == b(ORIG, g)
    if g <= 0x1B:
        assert b(PATCHED, g, mode1=True) == b(ORIG, g, mode1=True)
