"""G104 — parche av-cam del ISO 409600 sobre el av-cam real del CFW Film + PP (Unicorn): topes, tabla de EXIF e idempotencia."""
import struct
import sys
from pathlib import Path

import pytest
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R6,
    UC_ARM_REG_SP,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts/gui"), str(ROOT / "scripts"), str(ROOT / "scripts/lut"), str(ROOT / "scripts/g22")]
import iso_avcam_patch as P

AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
pytestmark = pytest.mark.skipif(not AVCAM.is_file(), reason="av-cam no disponible")
ISO = [10, 10, 12, 16, 20, 25, 32, 40, 50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000,
       6400, 8000, 10000, 12800, 16000, 20000, 25600, 32000, 40000, 51200, 64000, 80000, 102400, 128000, 160000, 204800, 256000, 320000, 409600]


@pytest.fixture(scope="module")
def img():
    d = AVCAM.read_bytes()
    return d, P.apply_bytes(d)


def _run(data: bytes, ini: int, fin: int, **regs) -> Uc:
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(P.BASE, (len(data) + 0xFFFFF) // 0x100000 * 0x100000 + 0x100000)
    mu.mem_write(P.BASE, data)
    mu.mem_map(0x10000000, 0x10000)
    mu.reg_write(UC_ARM_REG_SP, 0x10008000)
    mu.reg_write(UC_ARM_REG_LR, 0x10000001)
    for k, v in regs.items():
        mu.reg_write({"r0": UC_ARM_REG_R0, "r1": UC_ARM_REG_R1, "r6": UC_ARM_REG_R6}[k], v)
    mu.hook_add(UC_HOOK_CODE, lambda m, a, s, u: m.emu_stop() if a == fin else None)
    mu.emu_start(ini | 1, fin, count=2000)
    return mu


def test_tabla_exif_48_entradas(img):
    orig, nuevo = img
    for cod, esperado in enumerate(ISO):
        mu = _run(nuevo, 0x437B403E, 0x437B404C, r0=cod)
        assert mu.reg_read(UC_ARM_REG_R6) == esperado, cod
    mu = _run(nuevo, 0x437B403E, 0x437B404C, r0=0x80)       # fuera de rango: tope 0x2f
    assert mu.reg_read(UC_ARM_REG_R6) == 409600
    mu = _run(orig, 0x437B403E, 0x437B404C, r0=0x2f)         # original: tope 0x2c (204800)
    assert mu.reg_read(UC_ARM_REG_R6) == 204800


def test_codigo_a_sv(img):
    orig, nuevo = img
    sv = lambda d, c: _run(d, 0x43B074E4, 0x10000000, r0=c).reg_read(UC_ARM_REG_R0)
    assert sv(nuevo, 0x2f) == 0x400 and sv(nuevo, 0x2c) == 0x500      # (0x3b - código)·0x100 / 3
    assert sv(orig, 0x2f) == sv(orig, 0x2c) == 0x500          # el original topaba en 0x2c
    assert all(sv(nuevo, c) == sv(orig, c) for c in range(0x2d) if c)   # sin cambios hasta 204800
    assert sv(nuevo, 0x30) == sv(nuevo, 0x2f) == 0x400


def test_sv_a_codigo_y_idempotencia(img):
    orig, nuevo = img
    cod = lambda sv: _run(nuevo, 0x43B074BA, 0x10000000, r0=sv).reg_read(UC_ARM_REG_R0) & 0xFF
    assert cod(0x400) == 0x2f and cod(0x500) == 0x2c
    assert P.apply_bytes(nuevo) == nuevo
    cambios = [i for i in range(len(orig)) if orig[i] != nuevo[i]]
    assert len(cambios) <= 3 + 3 + 192 + 4 and all(c < 0x44000000 - P.BASE for c in cambios)


def test_cadena_cfw_film():
    """El parche entra al final de las dos cadenas del CFW Film (3.38 base): sin solapes con película/PP y con la tabla en ZONA_B."""
    import build_cfw_completo as C
    import build_cfw_film as F
    from e25_27 import build, fatimg, tarball, tpzl
    if not C.BASE_TAR.is_file():
        pytest.skip("base-380.tar no disponible")
    entries, _ = tarball.parse(C.BASE_TAR.read_bytes())
    part = tpzl.TpzlImage.parse({e.name: e.data for e in entries}[build.NFLASHA3])
    orig = fatimg.Fat16.parse(part.decompressed()).read(build.AVCAM_NAME)
    for fn in (F.bionz, F.bionz_pp):
        nuevo = fn(orig)
        assert struct.unpack_from("<4I", nuevo, P.TABLA_NUEVA - P.BASE)[:4] == (10, 10, 12, 16)
        assert struct.unpack_from("<3I", nuevo, P.TABLA_NUEVA - P.BASE + 4 * 45) == P.EXTRA
        assert P.apply_bytes(nuevo) == nuevo
