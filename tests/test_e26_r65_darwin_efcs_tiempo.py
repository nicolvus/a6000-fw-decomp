"""E26-R65: con EFCS activado Darwin resta u16[G+0x42] al tiempo de exposición (0x18a2e); unidades en µs (0x19a12); t arranca a 0."""
from __future__ import annotations

import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
needs = pytest.mark.skipif(not DARWIN.is_file(), reason="darwin_core.bin original ausente")
unicorn = pytest.importorskip("unicorn")
BASE, S, G, RET = 0x4200, 0x200036D8, 0x20000480, 0x4000


def _call(addr: int, r0: int, ram: dict[int, bytes]) -> int:
    from unicorn import UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, Uc
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    mu.mem_map(0x0, 0x40000)
    mu.mem_map(0x20000000, 0x10000)
    mu.mem_write(BASE, DARWIN.read_bytes())
    for a, b in ram.items():
        mu.mem_write(a, b)
    mu.reg_write(UC_ARM_REG_LR, RET | 1)
    mu.reg_write(UC_ARM_REG_SP, 0x20008000)
    mu.reg_write(UC_ARM_REG_R0, r0 & 0xFFFFFFFF)
    mu.emu_start(addr | 1, RET, count=200)
    return struct.unpack("<i", struct.pack("<I", mu.reg_read(UC_ARM_REG_R0)))[0]


def _s48(t_us: int, s31: int, s60: int = 0, g40: int = -435, g42: int = 3407) -> int:
    return _call(0x18A2E, t_us, {S + 0x31: bytes([s31]), S + 0x60: bytes([s60]),
                                 G + 0x40: struct.pack("<hH", g40, g42)})


@needs
def test_tv_a_microsegundos():
    assert _call(0x19A12, 0x1000, {}) == 1_000_000      # Tv 0x1000 = 1 s
    assert _call(0x19A12, 0x1A00, {}) == 976            # 1/1024 s


@needs
def test_efcs_on_resta_g42_y_off_suma_g40():
    assert _s48(1000, 0x02) == 1000 - 3407              # EFCS on (t = 0): T − u16[G+0x42]
    assert _s48(1000, 0x40) == 1000 - 435                # EFCS off: T + s16[G+0x40]
    assert _s48(1000, 0x02, s60=0x02) == 1000           # S+0x60 bit 1 anula la resta
    assert _s48(1000, 0x40, s60=0x01) == 1000           # S+0x60 bit 0 anula la suma


@needs
def test_tipo_t_en_bss_a_cero():
    d = DARWIN.read_bytes()
    # tabla de carga dispersa: 0x20002ed0 + 0xf8c se pone a cero (0x4494); t = [0x20003cd8+0x20]
    _, ram, size, fn = struct.unpack_from("<4I", d, 0x2A754 - BASE)
    assert (ram, size, fn) == (0x20002ED0, 0xF8C, 0x4494)
    assert ram <= 0x20003CF8 < ram + size
