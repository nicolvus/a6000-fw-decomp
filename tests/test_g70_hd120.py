"""G70-HD120 — 100p/120p en Ajuste grabación: parche de lista (bytes originales, idempotencia) y cadena del valor 0x15 sobre bytes reales en Unicorn."""
import re
import struct
import subprocess
import sys
from pathlib import Path

import capstone
import pytest
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_SP,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import hd120_list_patch as hp

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib"
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
pytestmark = pytest.mark.skipif(not (LIB / "CautionConfig.so").exists(), reason="extracción no disponible")
RET = 0x7F001


def _load(path: Path, data: bytes, size=0x300000):
    """Mapea los PT_LOAD y aplica las relocalizaciones de DT_REL (`--use-dynamic`, vale con tablas movidas)."""
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, size)
    e_phoff, = struct.unpack_from("<I", data, 0x1C)
    phentsize, phnum = struct.unpack_from("<HH", data, 0x2A)
    for i in range(phnum):
        t, off, va, _, fs, _ms, *_ = struct.unpack_from("<8I", data, e_phoff + i * phentsize)
        if t == 1:
            mu.mem_write(va, data[off:off + fs])
    for ln in subprocess.run(["readelf", "-r", "-W", "--use-dynamic", str(path)], capture_output=True, text=True, check=True).stdout.splitlines():
        p = ln.split()
        if len(p) < 4 or not re.fullmatch(r"[0-9a-f]{8}", p[0]):
            continue
        off, typ = int(p[0], 16), p[2]
        if typ in ("R_ARM_GLOB_DAT", "R_ARM_ABS32", "R_ARM_RELATIVE"):
            add = struct.unpack("<I", mu.mem_read(off, 4))[0] if typ != "R_ARM_GLOB_DAT" else 0
            sym = int(p[3], 16) if typ != "R_ARM_RELATIVE" else 0
            mu.mem_write(off, struct.pack("<I", (sym + add) & 0xFFFFFFFF))
    return mu


def _call(mu, entry, args=(), stubs=None, stack=()):
    """Ejecuta una función Thumb; `stubs` = {dir_PLT: f(mu)} (cada stub vuelve a LR)."""
    sp = 0x2F0000
    for i, v in enumerate(stack):
        mu.mem_write(sp + 4 * i, struct.pack("<I", v & 0xFFFFFFFF))
    for r, v in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), args):
        mu.reg_write(r, v)
    mu.reg_write(UC_ARM_REG_SP, sp)
    mu.reg_write(UC_ARM_REG_LR, RET)

    def hook(uc, addr, size, _):
        if addr in stubs:
            stubs[addr](uc)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    h = mu.hook_add(UC_HOOK_CODE, hook, begin=0x100000, end=0x110000) if stubs else None
    mu.emu_start(entry | 1, RET & ~1)
    if h:
        mu.hook_del(h)
    return mu.reg_read(UC_ARM_REG_R0)


@pytest.fixture(scope="module")
def so_patched(tmp_path_factory):
    src = (LIB / "CautionConfig.so").read_bytes()
    out = hp.patch(src)
    p = tmp_path_factory.mktemp("hd120") / "CautionConfig.so"
    p.write_bytes(out)
    return src, out, p


def _syms(path):
    r = {}
    for ln in subprocess.run(["nm", "-D", "-S", str(path)], capture_output=True, text=True, check=True).stdout.splitlines():
        f = ln.split()
        if len(f) == 4:
            r[f[3]] = (int(f[0], 16), int(f[1], 16))
    return r


def test_bytes_originales_e_idempotencia(so_patched):
    src, out, _ = so_patched
    s = _syms(LIB / "CautionConfig.so")
    assert s["cmnViewSettingNodesMovieRecordingSettingType04"] == (0x1A358C, 0x44)
    assert struct.unpack_from("<I", src, s["cmnViewSettingNodesNumOfMovieRecordingSettingType04"][0] - 0x8000)[0] == 17
    assert hp.patch(out) == out
    with pytest.raises(AssertionError):
        hp.patch(src[:0x19B58C] + b"\1" + src[0x19B58D:])  # addendum en sitio distinto de 0


def test_get_subnode_tipo29_devuelve_19_nodos(so_patched):
    """`_getSubNode` (bytes reales, tipo de modelo 29): antes 17 nodos; después los mismos 17 más 100p y 120p al final (valores 0x14, 0x15)."""
    src, out, p = so_patched
    res = {}
    for nombre, data, path in (("antes", src, LIB / "CautionConfig.so"), ("despues", out, p)):
        mu = _load(path, data)
        mu.mem_map(0x300000, 0x1000)
        mu.mem_write(0x300000, bytes(0x100))
        tipo = lambda uc: uc.mem_write(uc.reg_read(UC_ARM_REG_R1), bytes([29])) or uc.reg_write(UC_ARM_REG_R0, 0)
        _call(mu, 0x108E71, (0x300000,), {0x101C20: tipo})
        arr, cnt = struct.unpack("<I", mu.mem_read(0x300004, 4))[0], struct.unpack("<I", mu.mem_read(0x300008, 4))[0]
        res[nombre] = (cnt, [struct.unpack("<I", mu.mem_read(arr + 4 * i, 4))[0] for i in range(cnt)])
    assert res["antes"][0] == 17 and res["despues"][0] == 19
    assert res["despues"][1][:17] == res["antes"][1]
    s = _syms(p)
    assert res["despues"][1][17:] == [s[n.decode()][0] for n in hp.NEW_NODES]
    # los dos nodos nuevos llevan el valor interno 0x14 / 0x15 (propiedad 0x0f, ya existían en el firmware)
    sys.path.insert(0, str(ROOT / "scripts/gui"))
    import setting_nodes as sn
    vals = {n: {a: c for a, _, c in pr}[0xF] for n, pr in sn.property_lists(LIB / "CautionConfig.so", r"^MovieRecordingSetting1[02]0_p_50M$")}
    assert vals == {"MovieRecordingSetting100_p_50M": 0x14, "MovieRecordingSetting120_p_50M": 0x15}


# --- cadena del valor en processDataMgr (bytes reales) -------------------------------------------------------------------------------
PDM = LIB / "cmn_view_processDataMgr.so"
PLT = {0x4C6E8: "ctor", 0x4D328: "dtor", 0x4EC7C: "isMR", 0x4D374: "read", 0x4D4DC: "wr_attr", 0x4E1C8: "write", 0x4E59C: "ui"}


def _pdm(entry, args, stack=(), ids=None, log=None):
    mu = _load(PDM, PDM.read_bytes(), 0x200000)
    mu.mem_map(0x400000, 0x10000)
    mu.mem_map(0x500000, 0x10000)
    mu.mem_write(0x500004, struct.pack("<I", 0x500100))
    ids = ids or {}

    def mk(name):
        def f(uc):
            r0, r1 = uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)
            if name == "read":
                uc.mem_write(r1, bytes([ids.get(r0, 0)]))
            if name == "write" and log is not None:
                log[r0] = uc.mem_read(r1, 1)[0]
            if name == "ui" and log is not None:
                log[("ui", r1)] = uc.reg_read(UC_ARM_REG_R2)
            uc.reg_write(UC_ARM_REG_R0, 0)
        return f

    stubs = {a: mk(n) for a, n in PLT.items()}
    stubs = {a: (lambda uc, f=f: f(uc)) for a, f in stubs.items()}

    def hook(uc, addr, size, _):
        if addr in PLT:
            stubs[addr](uc)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    sp = 0x40F000
    for i, v in enumerate(stack):
        mu.mem_write(sp + 4 * i, struct.pack("<I", v & 0xFFFFFFFF))
    for r, v in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), args):
        mu.reg_write(r, v)
    mu.reg_write(UC_ARM_REG_SP, sp)
    mu.reg_write(UC_ARM_REG_LR, RET)
    mu.hook_add(UC_HOOK_CODE, hook, begin=0x4C000, end=0x4F000)
    mu.emu_start(entry | 1, RET & ~1)
    return mu


def _convert_xavc(v):
    o = [0x400100 + 4 * i for i in range(7)]
    mu = _pdm(0x6C37A, [0x500000, v, o[0], o[1]], stack=o[2:])
    return mu.reg_read(UC_ARM_REG_R0), [struct.unpack("<i", mu.mem_read(a, 4))[0] for a in o]


def test_valor_0x15_convierte_a_formato_4_en_backup():
    """Menú 0x14/0x15 -> ramas XAVC de `setValue`: 0x1070c9a (clase de formato) = 4; 50p/60p (0x12/0x13) = 0; 24p (0xf) = 3."""
    for v, esperado in ((0x0F, 3), (0x12, 0), (0x13, 0), (0x14, 4), (0x15, 4)):
        ok, out = _convert_xavc(v)
        assert ok == 1
        log = {}
        _pdm(0x6C064, [0x500000, out[0], out[1], out[2]], stack=out[3:], log=log)
        assert log[0x1070C9A] == esperado, hex(v)
    _, hfr = _convert_xavc(0x15)
    assert hfr == _convert_xavc(0x14)[1] == [10, 4, 3, 1, 1, 1, 8]
    assert _convert_xavc(0x16)[0] == 0   # sin caso: no hay conversión (0x16 no existe en el menú)


def test_inhibicion_solo_xavcs_segun_sistema():
    """`isValueDisable` (0 = habilitado): 100p solo con XAVC S (0x1070087==9) y PAL (0x10704fd==0); 120p con XAVC S y NTSC (1)."""
    for v, sistema in ((0x14, 0), (0x15, 1)):
        for fmt in range(12):
            for sis in range(4):
                mu = _pdm(0x6B92C, [0x500000, v], ids={0x1070087: fmt, 0x10704FD: sis})
                assert (mu.reg_read(UC_ARM_REG_R0) == 0) == (fmt == 9 and sis == sistema), (hex(v), fmt, sis)


@pytest.mark.skipif(not AVCAM.exists(), reason="av-cam.bin no disponible")
def test_avcam_conserva_la_clase_4():
    """av-cam 0x4381acac (conversión de 0x1070c9a al campo de formato del mensaje): identidad 0..5, así la clase 4 llega intacta (selector 0x4380e43c: formato 4 -> sensor 0x12)."""
    d = AVCAM.read_bytes()
    base = 0x43541000
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0x43000000, 0x1100000)
    mu.mem_map(0x7F000, 0x1000)
    mu.mem_map(0x2E0000, 0x20000)
    mu.mem_write(base, d)
    for k in range(7):
        assert _call(mu, 0x4381ACAC, (k,)) == (k if k <= 5 else 1)


def _norm(data, addr, n):
    """Instrucciones Thumb con los saltos y literales relativos anulados (la copia de viewUnified2 llama por `bl` donde processDataMgr usa PLT)."""
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    out = []
    for i in md.disasm(data[addr:addr + 0x200], addr):
        rel = i.mnemonic.startswith(("b", "cb")) or "pc" in i.op_str
        out.append("b*" if i.mnemonic.startswith(("bl", "blx")) else i.mnemonic + " " + ("REL" if rel else i.op_str))
        if len(out) == n:
            return out
    return out


def test_la_copia_que_corre_en_la_camara_es_la_probada():
    """G75 T20 (medido): `cmn_view_processDataMgr.so` no se carga en im.elf; la UI usa la copia estática de la clase en `viewUnified2.so`.
    Las funciones emuladas arriba (isValueDisable, conversión XAVC, escritura al Backup) y la regla de gris HFR son las mismas instrucciones."""
    v = (LIB / "viewUnified2.so").read_bytes()
    m = PDM.read_bytes()
    pares = {0x6B92C: 0x2541C0, 0x6C688: 0x254F1C, 0x6C736: 0x254FCA, 0x6C37A: 0x254C0E, 0x6C064: 0x2548F8}  # pdm -> viewUnified2
    for a, b in pares.items():
        assert _norm(m, a, 50) == _norm(v, b, 50), hex(a)
