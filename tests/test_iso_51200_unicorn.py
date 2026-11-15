"""G48 — ISO 51200 (0x26) sobre bytes reales en Unicorn: MAX de libObj (variante --51200), getValue de processDataMgr y lista de CautionConfig parcheada."""
import re
import struct
import subprocess
import sys
from pathlib import Path

import pytest
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R7, UC_ARM_REG_SP, UC_ARM_REG_PC

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import iso_list_patch as lp  # noqa: E402
import iso_max_patch as mp  # noqa: E402

LIB = ROOT / "analysis/camera-extract/usr/lib"
LIBOBJ = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
pytestmark = pytest.mark.skipif(not (LIB / "CautionConfig.so").exists() or not LIBOBJ.exists(), reason="extracciones no disponibles")


def _load(path: Path, data: bytes, size=0x300000):
    """Mapea los PT_LOAD y aplica ABS32/GLOB_DAT/RELATIVE (suficiente para leer GOT y listas)."""
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, size)
    e_phoff, = struct.unpack_from("<I", data, 0x1C)
    phentsize, phnum = struct.unpack_from("<HH", data, 0x2A)
    for i in range(phnum):
        t, off, va, _, fs, ms, *_ = struct.unpack_from("<8I", data, e_phoff + i * phentsize)
        if t == 1:
            mu.mem_write(va, data[off:off + fs])
    for ln in subprocess.run(["readelf", "-r", "-W", str(path)], capture_output=True, text=True).stdout.splitlines():
        p = ln.split()
        if len(p) < 4 or not re.fullmatch(r"[0-9a-f]{8}", p[0]):
            continue
        off, typ = int(p[0], 16), p[2]
        if typ in ("R_ARM_GLOB_DAT", "R_ARM_ABS32", "R_ARM_RELATIVE"):
            add = struct.unpack("<I", mu.mem_read(off, 4))[0] if typ != "R_ARM_GLOB_DAT" else 0
            sym = int(p[3], 16) if typ != "R_ARM_RELATIVE" else 0
            mu.mem_write(off, struct.pack("<I", (sym + add) & 0xFFFFFFFF))
    return mu


# 1. libObj: con MAX 0x23 (25600) el conversor fuerza 0x26 (51200)
def test_libobj_forza_0x26():
    d = LIBOBJ.read_bytes()
    out = mp.patch(d, mp.NEW51)
    assert sum(a != b for a, b in zip(d, out)) <= 14 and mp.patch(out, mp.NEW51) == out
    assert out[mp.SITE:mp.SITE + 14] == mp.NEW51
    for k in range(0x4B):
        mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        mu.mem_map(0x1000, 0x1000); mu.mem_map(0x8000, 0x1000)
        mu.mem_write(0x1000, mp.NEW51); mu.mem_write(0x8038, k.to_bytes(4, "little"))
        mu.reg_write(UC_ARM_REG_R7, 0x8000)
        mu.emu_start(0x1001, 0x1000 + 14)
        assert int.from_bytes(mu.mem_read(0x8038, 4), "little") == (0x26 if 0x23 <= k <= 0x28 else k), hex(k)


# 2. processDataMgr::getValue: cadena código -> id desde 0x6839c hasta el epílogo 0x6850e (bytes reales)
def _getvalue_chain(code: int):
    so = LIB / "cmn_view_processDataMgr.so"
    mu = _load(so, so.read_bytes())
    mu.mem_map(0x400000, 0x1000)
    mu.reg_write(UC_ARM_REG_R0, code)
    mu.reg_write(UC_ARM_REG_R4, 0x400000)
    mu.reg_write(UC_ARM_REG_R5, 0xDEAD)
    mu.emu_start(0x6839C | 1, 0x6850E)
    return mu.reg_read(UC_ARM_REG_R5), struct.unpack("<I", mu.mem_read(0x400000, 4))[0]


@pytest.mark.parametrize("code,ident", [(0x23, 0x1D), (0x24, 0x1E), (0x25, 0x1F), (0x26, 0x20)])
def test_getvalue_hasta_51200(code, ident):
    assert _getvalue_chain(code) == (1, ident)


def test_getvalue_mas_alla_de_51200_sin_valor():  # límite documentado: 0x27.. sigue sin id (ISO-B)
    assert _getvalue_chain(0x27)[0] == 0


# 3. CautionConfig::ISOSensitivity::_getSubNode (caso tipo 29) con el parche de lista: 35 filas hasta 51200
def test_getsubnode_lista_hasta_51200():
    so = LIB / "CautionConfig.so"
    d = lp.patch(so.read_bytes())
    mu = _load(so, d)
    syms = {}
    for ln in subprocess.run(["nm", "-D", str(so)], capture_output=True, text=True).stdout.splitlines():
        p = ln.split()
        if len(p) == 3:
            syms[int(p[0], 16)] = p[2]
    mu.mem_map(0x400000, 0x2000)
    node, sp = 0x400000, 0x401000

    def hook(uc, addr, size, _):
        if addr == 0x107D94:  # blx 0x101c20: tipo de modelo = 29
            uc.mem_write(uc.reg_read(UC_ARM_REG_R1), bytes([29]))
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, 0x107D98 | 1)

    mu.hook_add(UC_HOOK_CODE, hook, begin=0x107D94, end=0x107D96)
    mu.reg_write(UC_ARM_REG_R0, node)
    mu.reg_write(UC_ARM_REG_SP, sp)
    mu.emu_start(0x107D7C | 1, 0x107E2E + 6)
    lst, n = struct.unpack("<II", mu.mem_read(node + 4, 8))
    assert n == 35
    names = [syms.get(struct.unpack("<I", mu.mem_read(lst + 4 * i, 4))[0], "?").replace("cmnViewSettingNodeISOSensitivity", "") for i in range(n)]
    assert names[:2] == ["MultiFrameNoiseReduct", "AUTO"] and names[30:] == ["32000", "40000", "51200", "ISOAUTOMAX_MR", "ISOAUTOMIN_MR"]
