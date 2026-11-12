"""G33-B: rama nativa de Hi-Light Detail / B/W Balance del APC con la tabla propia — Unicorn sobre los sitios de `av-cam.bin` (A6000 fw3.21)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
pytest.importorskip("unicorn")
pytestmark = pytest.mark.skipif(not AVCAM.is_file(), reason="av-cam.bin ausente")
import pp_bwhl_patch as P
from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_R0,
    UC_ARM_REG_R6,
    UC_ARM_REG_R7,
    UC_ARM_REG_SB,
    UC_ARM_REG_SP,
)

CAVE, CTX, SP = 0x43FAF290, 0x46000000, 0x47000800   # CAVE: solo para la prueba (hueco de G18), no es una asignación


def run(img: bytes, start: int, end: int, gotreg: int, mode: int, idx: int, slot: int) -> int:
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(P.BASE, (len(img) + 0xFFF) & ~0xFFF)
    mu.mem_write(P.BASE, img)
    mu.mem_map(CTX, 0x1000)
    mu.mem_write(CTX + 0x139, bytes([mode]))
    mu.mem_write(CTX + slot, bytes([idx]))
    mu.mem_map(SP - 0x800, 0x1000)
    mu.mem_write(SP, b"\x77\x00" * 0x60)             # centinela 0x77 en las medias palabras de la pila
    mu.reg_write(UC_ARM_REG_SP, SP)
    mu.reg_write(UC_ARM_REG_R6, CTX)
    mu.reg_write(gotreg, P.GOT)
    if gotreg != UC_ARM_REG_R7:
        mu.reg_write(UC_ARM_REG_R7, 100)             # sitio Hi-Light: r7 → sp+0x7a, r0 → sp+0x7c (dos umbrales interpolados)
        mu.reg_write(UC_ARM_REG_R0, 200)
    mu.emu_start(start | 1, end)
    return int.from_bytes(mu.mem_read(SP + 0x34, 4), "little") if gotreg == UC_ARM_REG_R7 else int.from_bytes(mu.mem_read(SP + 0x7C, 2), "little")


def imagen(**kw) -> bytes:
    img = bytearray(AVCAM.read_bytes())
    for a, b, _ in P.patches(bytes(img), CAVE, **kw):
        img[a - P.BASE:a - P.BASE + len(b)] = b
    return bytes(img)


def hl(img, mode, idx):
    return run(img, 0x438B154A, 0x438B15A0, UC_ARM_REG_SB, mode, idx, 0x13F)


def test_original_bandera_cerrada():
    base = AVCAM.read_bytes()
    assert hl(base, 1, 4) == 200                       # bandera 0 en el archivo: sp+0x7c = r0


def test_hilight_manual_suma_tabla():
    img = imagen()
    assert [hl(img, 1, i) for i in range(5)] == [100 + v for v in P.HL]
    assert hl(img, 0, 4) == 200                        # Detail Mode Auto: sin cambio
    assert hl(img, 1, 9) == 100 + P.HL[0]              # índice fuera de rango → T[0x1b]


def test_bw_solo_si_se_pide():
    bw = (0x21, 0x32, 0x43, 0x54, 0x65)
    assert run(imagen(), 0x438B18EE, 0x438B1932, UC_ARM_REG_R7, 1, 2, 0x13C) == 0x00770077   # sin `bw` no se toca
    assert run(imagen(bw=bw), 0x438B18EE, 0x438B1932, UC_ARM_REG_R7, 1, 2, 0x13C) == 0x00040003  # 0x43: bajo → sp+0x34, alto → sp+0x36


def test_comprobaciones():
    base = AVCAM.read_bytes()
    with pytest.raises(AssertionError):
        P.patches(base, P.FLAG_SLOT)                   # cueva no vacía
    with pytest.raises(AssertionError):
        P.patches(base, CAVE, bw=(1, 2))               # B/W necesita 5 valores
