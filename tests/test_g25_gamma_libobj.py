"""G25: parche de Gamma de `libObj.so` (ITU709(800%) y S-Log2): emulación Unicorn de App2Obj/Obj2App antes y después (offline)."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import patch_libobj_pp as P

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
uc = pytest.importorskip("unicorn")
needs = pytest.mark.skipif(not LIB.is_file(), reason="libObj.so de Sony ausente")
APP2OBJ_FN, OBJ2APP_FN = 0x4B46B8, 0x4B4290


def call(img: bytes, fn: int, case: int, val: int):
    """Ejecuta fn(this=0, case, val, &out) con los `bl` anulados; devuelve (r0, out)."""
    from unicorn import UC_HOOK_CODE, Uc, UC_ARCH_ARM, UC_MODE_THUMB, UcError
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, 0x1100000)
    mu.mem_write(0, img[:0x1100000])
    mu.mem_map(0x20000000, 0x10000)
    END, OUT = 0x20008000, 0x20004000
    mu.mem_write(END, b"\x00\xbf" * 4)
    mu.mem_write(OUT, struct.pack("<I", 0xDEAD))

    def hook(u, addr, size, _):
        h1, h2 = struct.unpack("<HH", bytes(u.mem_read(addr, 4)))
        if (h1 & 0xF800) == 0xF000 and (h2 & 0xC000) == 0xC000 and (h2 & 0x1000 or True) and (h2 & 0xD000) in (0xD000, 0xC000):
            u.reg_write(UC_ARM_REG_R0, 0)
            u.reg_write(UC_ARM_REG_PC, (addr + 4) | 1)

    mu.hook_add(UC_HOOK_CODE, hook, begin=fn, end=fn + 0x800)
    mu.reg_write(UC_ARM_REG_SP, 0x2000F000)
    mu.reg_write(UC_ARM_REG_R0, 0)
    mu.reg_write(UC_ARM_REG_R1, case)
    mu.reg_write(UC_ARM_REG_R2, val)
    mu.reg_write(UC_ARM_REG_R3, OUT)
    mu.reg_write(UC_ARM_REG_LR, END | 1)
    try:
        mu.emu_start(fn | 1, END, count=20000)
    except UcError as e:
        raise RuntimeError(f"{e} pc={mu.reg_read(UC_ARM_REG_PC):#x}")
    return mu.reg_read(UC_ARM_REG_R0) & 0xFF, struct.unpack("<I", bytes(mu.mem_read(OUT, 4)))[0]


@needs
def test_app2obj_acepta_12_valores_y_rechaza_el_13():
    old, new = LIB.read_bytes(), P.patch_gamma(LIB.read_bytes())
    for v in range(10):
        assert call(old, APP2OBJ_FN, 7, v) == (1, P.VALUEID[v]) == call(new, APP2OBJ_FN, 7, v)   # comportamiento anterior intacto
    assert call(old, APP2OBJ_FN, 7, 10)[0] == 0 and call(old, APP2OBJ_FN, 7, 11)[0] == 0
    assert call(new, APP2OBJ_FN, 7, 10) == (1, 0x481) and call(new, APP2OBJ_FN, 7, 11) == (1, 0x480)
    assert call(new, APP2OBJ_FN, 7, 12)[0] == 0


@needs
def test_obj2app_es_la_inversa():
    old, new = LIB.read_bytes(), P.patch_gamma(LIB.read_bytes())
    for app, vid in enumerate(P.VALUEID):
        assert call(new, OBJ2APP_FN, 7, vid) == (1, app)
        if app < 10:
            assert call(old, OBJ2APP_FN, 7, vid) == (1, app)
    assert call(new, OBJ2APP_FN, 7, 0x482)[0] == 0 and call(new, OBJ2APP_FN, 7, 0x1B6)[0] == 0


@needs
def test_otros_casos_no_cambian():
    old, new = LIB.read_bytes(), P.patch_gamma(LIB.read_bytes())
    for case, vals in ((8, range(4)), (10, (-15, 0, 15, 16)), (9, (-7, 7, 8)), (30, (-7, 8))):
        for v in vals:
            assert call(old, APP2OBJ_FN, case, v & 0xFFFFFFFF) == call(new, APP2OBJ_FN, case, v & 0xFFFFFFFF)
