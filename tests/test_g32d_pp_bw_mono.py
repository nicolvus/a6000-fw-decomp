"""G32-D: indicador monocromo por tipo B&W — Unicorn sobre el sitio real 0x437a2728 de `av-cam.bin` (A6000 fw3.21)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
pytest.importorskip("unicorn")
pytest.importorskip("keystone")
pytestmark = pytest.mark.skipif(not AVCAM.is_file(), reason="av-cam.bin ausente")
import pp_bw_mono_patch as P
from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_SP

D = 0x46000000
CTX, SUM, OUT, CAPS = D, D + 0x100, D + 0x200, D + 0x300


def mono(img: bytes, tipo: int, sat: int, caps3: int) -> int:
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(P.BASE, (len(img) + 0xFFF) & ~0xFFF)
    mu.mem_write(P.BASE, img)
    mu.mem_map(D, 0x2000)
    mu.mem_write(CTX, SUM.to_bytes(4, "little") + bytes(4) + OUT.to_bytes(4, "little"))
    mu.mem_write(SUM + 0x24, bytes([sat & 0xFF]))
    mu.mem_write(SUM + 0x31, bytes([tipo]))
    mu.mem_write(OUT + 0x88, b"\x77")
    mu.mem_write(CAPS + 3, bytes([caps3]))
    for r, v in ((UC_ARM_REG_R4, CTX), (UC_ARM_REG_R5, CAPS), (UC_ARM_REG_SP, D + 0x1F00), (UC_ARM_REG_LR, 0)):
        mu.reg_write(r, v)
    mu.emu_start(P.SITE | 1, 0x437A2748)                # ambos caminos (strb 1 en 0x437a2744 o 0 en 0x437a279e) llegan aquí
    return mu.mem_read(OUT + 0x88, 1)[0]


def parcheada() -> bytes:
    img = bytearray(AVCAM.read_bytes())
    for a, b, _ in P.patches(bytes(img)):
        img[a - P.BASE:a - P.BASE + len(b)] = b
    return bytes(img)


def test_original_depende_de_caps():
    base = AVCAM.read_bytes()
    assert mono(base, 8, 0, 0x40) == 0                  # NVRAM real (caps[3] = 0x40): B&W sin monocromo
    assert mono(base, 5, -8, 0x42) == 1                 # con el bit 1, la saturación −8 lo dispara
    assert mono(base, 5, -8, 0x40) == 0


def test_parche_solo_tipo_bw():
    img = parcheada()
    assert mono(img, 8, 0, 0x40) == 1                   # B&W activa el monocromo aunque caps[3] bit 1 = 0
    assert mono(img, 5, -8, 0x42) == 0                  # Saturación ≤ −8 ya no lo dispara
    assert mono(img, 5, -32, 0x40) == 0
    assert all(mono(img, t, 0, 0x42) == 0 for t in (0, 1, 7, 9))


def test_sitio_comprobado():
    with pytest.raises(AssertionError):
        P.patches(parcheada())
