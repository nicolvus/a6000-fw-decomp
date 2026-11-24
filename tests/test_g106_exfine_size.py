"""G106 — `exfine_size_patch`: ids EXFINE↔FINE de las tres tablas de `libmprctrl` y el gancho emulado con Unicorn (BackupLib simulado)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmprctrl.so"
pytestmark = pytest.mark.skipif(not LIB.is_file(), reason="fw321 extraído no disponible")
TABLAS = ((0x3B47C, 0x2E300, 60), (0x3A8E8, 0x2DF40, 60), (0x3ADC0, 0x25230, 9))   # (nombre→BKID, índice→entrada, nº) de GetStillDataInfo


def _off(d, va):
    phoff, phentsize, phnum = struct.unpack_from("<I", d, 0x1C)[0], *struct.unpack_from("<HH", d, 0x2A)
    for k in range(phnum):
        t, off, v, _, fs, _ = struct.unpack_from("<6I", d, phoff + k * phentsize)
        if t == 1 and v <= va < v + fs:
            return va - v + off


def test_ids_exfine_relacion_con_fine():
    d = LIB.read_bytes()
    u = lambda va: struct.unpack_from("<I", d, _off(d, va))[0]
    nombre = lambda va: d[_off(d, va):d.index(b"\0", _off(d, va))].decode()
    n = 0
    for t3, t2, cnt in TABLAS:
        for i in range(cnt):
            e = u(t2 + 8 * i + 4)
            if nombre(u(t3 + 16 * e + 4)).endswith("EXFINE_TGT"):
                tgt, mx, ft, fm = u(t3 + 16 * e), u(t3 + 16 * e + 8), u(t3 + 16 * (e - 1)), u(t3 + 16 * (e - 1) + 8)
                assert nombre(u(t3 + 16 * (e - 1) + 4)).endswith("_FINE_TGT") and (ft, fm, mx) == (tgt + 2, tgt + 1, tgt - 1)
                n += 1
    assert n == 43


def _emula(d, tgt_leido, calidad, eep):
    import exfine_size_patch as P
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R2,
        UC_ARM_REG_R4,
        UC_ARM_REG_R6,
        UC_ARM_REG_R7,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, 0x40000)
    mu.mem_write(0, d[:0x32000])
    mu.mem_map(0x100000, 0x10000)
    r7 = 0x108000
    mu.mem_write(r7 + 0x1C, struct.pack("<I", tgt_leido))
    mu.mem_write(r7 + 0x48, struct.pack("<I", calidad))
    for r, v in ((UC_ARM_REG_SP, 0x10C000), (UC_ARM_REG_R7, r7), (UC_ARM_REG_R6, 0x50025), (UC_ARM_REG_R4, 0x1234)):
        mu.reg_write(r, v)
    escritos = {}

    def gancho(uc, addr, size, _):
        if addr in (P.GET, P.SET):
            i, buf = uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R2)
            if addr == P.GET:
                uc.mem_write(buf, struct.pack("<I", eep.get(i, 0)))
            else:
                escritos[i] = struct.unpack("<I", uc.mem_read(buf, 4))[0]
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    mu.hook_add(UC_HOOK_CODE, gancho)
    mu.emu_start(P.HOOK | 1, P.HOOK + 4)
    return mu.reg_read(UC_ARM_REG_R1), mu.reg_read(UC_ARM_REG_R0), escritos


def test_gancho_deriva_exfine_de_fine_y_lo_guarda():
    import exfine_size_patch as P
    d = P.patch(LIB.read_bytes())
    assert P.patch(d) == d                                                   # idempotente
    eep = {0x50027: 4188, 0x50026: 6701}                                     # JPG M 3:2 FINE TGT/MAX (volcado de la cámara)
    r1, r0, esc = _emula(d, 0, 2, eep)
    assert (r1, r0) == (4188 * 3 // 2, 0x1234) and esc == {0x50025: 6282, 0x50024: 13402}
    assert _emula(d, 0, 1, eep)[2] == {} and _emula(d, 777, 2, eep)[:1] == (777,) and _emula(d, 777, 2, eep)[2] == {}


def _emula2(d, id_tgt, tgt_leido, max_leido, eep):
    """Gancho de `CalcStillData_JPG` (G109): r8 = id TGT, sl = id MAX, locales `[r7+0x1c]` (TGT) y `[r7+0x18]` (MAX)."""
    import exfine_size_patch as P
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_R2,
        UC_ARM_REG_R4,
        UC_ARM_REG_R7,
        UC_ARM_REG_R8,
        UC_ARM_REG_R10,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, 0x40000)
    mu.mem_write(0, d[:0x32000])
    mu.mem_map(0x100000, 0x10000)
    r7 = 0x108000
    mu.mem_write(r7 + 0x1C, struct.pack("<I", tgt_leido))
    mu.mem_write(r7 + 0x18, struct.pack("<I", max_leido))
    mu.mem_write(r7 + 0x4C, struct.pack("<I", 0xCAFE))
    for r, v in ((UC_ARM_REG_SP, 0x10C000), (UC_ARM_REG_R7, r7), (UC_ARM_REG_R8, id_tgt), (UC_ARM_REG_R10, id_tgt - 1), (UC_ARM_REG_R4, 0x1234)):
        mu.reg_write(r, v)
    escritos = {}

    def gancho(uc, addr, size, _):
        if addr in (P.GET, P.SET):
            i, buf = uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R2)
            if addr == P.GET:
                uc.mem_write(buf, struct.pack("<I", eep.get(i, 0)))
            else:
                escritos[i] = struct.unpack("<I", uc.mem_read(buf, 4))[0]
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    mu.hook_add(UC_HOOK_CODE, gancho)
    mu.emu_start(P.HOOK2 | 1, P.HOOK2 + 4)
    rd = lambda a: struct.unpack("<I", mu.mem_read(a, 4))[0]
    return rd(r7 + 0x1C), rd(r7 + 0x18), mu.reg_read(UC_ARM_REG_R0), escritos


def test_gancho_calcstilldata_deriva_exfine_al_crear_la_tabla():
    import exfine_size_patch as P
    d = P.patch(LIB.read_bytes())
    eep = {0x50027: 4188, 0x50026: 6701, 0x50005: 111}                       # JPG M 3:2 FINE TGT/MAX; otro id cualquiera
    assert _emula2(d, 0x50025, 0, 0, eep) == (6282, 13402, 0x1234, {0x50025: 6282, 0x50024: 13402})
    assert _emula2(d, 0x50027, 0, 0, eep)[3] == {}                           # un FINE_TGT con valor 0 no es EXFINE: no se toca
    assert _emula2(d, 0x50025, 500, 900, eep)[:2] == (500, 900) and _emula2(d, 0x50025, 500, 900, eep)[3] == {}   # con TGT guardado, nada
    assert _emula2(d, 0x50025, 0, 0, {})[:2] == (0, 0) and _emula2(d, 0x50025, 0, 0, {})[3] == {}          # sin FINE tampoco se inventa
