"""G27: S-Gamut3 / S-Gamut3.Cine en el núcleo de la A6000 (pp_color_patch): emulación Unicorn de las funciones tocadas, imagen original frente a parcheada."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import pp_color_patch as C

uc = pytest.importorskip("unicorn")
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_SP

AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
FW = ROOT / "firmware/extracted"
P6300 = FW / "a6300-fw201/payload/firmware.tar_unpacked/0110_backup/SYSMUSASHI-DSLR/DX/CX79100_E38.bin"
P6000 = FW / "fw321/firmware.tar_unpacked/0110_backup/SYSMUSASHI-DSLR/DM_UUD3/CX77500_E38.bin"
needs = pytest.mark.skipif(not (AVCAM.is_file() and P6300.is_file() and P6000.is_file()), reason="faltan av-cam o presets")
T = 0x43F78DD2                                  # bloque de ajuste de color (propiedad 0x30001) en RAM
CTX, STACK, SENT = 0x50000000, 0x50100000, 0x50200000


def props(path):
    sys.path.insert(0, str(ROOT / "references/pmca"))
    import io

    from pmca.backup import BackupFile
    return {i: bytes(p.data) for i, p in BackupFile(io.BytesIO(path.read_bytes())).listProperties()}


def nuevo(base):
    img = bytearray(base)
    for a, d, _ in C.patches(base, P6300.read_bytes()):
        img[a - C.BASE:a - C.BASE + len(d)] = d
    return bytes(img)


def maquina(img, bloque=None):
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(C.BASE, (len(img) + 0xFFFFF) // 0x100000 * 0x100000)
    mu.mem_write(C.BASE, img)
    if bloque is not None:
        mu.mem_write(T, bloque)
    for a in (CTX, STACK, SENT):
        mu.mem_map(a, 0x10000)
    mu.mem_write(CTX, b"".join(struct.pack("<I", CTX + 0x400 + 0x80 * k) for k in range(8)))   # contexto: punteros a estructuras a cero
    mu.reg_write(UC_ARM_REG_SP, STACK + 0x8000)
    mu.reg_write(UC_ARM_REG_LR, SENT | 1)
    return mu


def llama(img, bloque, f, r0=0, r1=0, r2=0, r3=0, pre=None):
    mu = maquina(img, bloque)
    if pre:
        pre(mu)
    from unicorn.arm_const import (
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R2,
        UC_ARM_REG_R3,
    )
    for r, v in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), (r0, r1, r2, r3)):
        mu.reg_write(r, v)
    mu.emu_start(f | 1, SENT, count=20000)
    return mu


@needs
def test_cabecera_y_ganchos_originales_y_cueva_dentro_del_hueco():
    base = AVCAM.read_bytes()
    ps = C.patches(base, P6300.read_bytes())
    assert all(a >= C.CAVE and a + len(d) <= 0x43FB8EE0 for a, d, w in ps if w.startswith("dato"))
    assert all(a % 2 == 0 and len(d) % 2 == 0 for a, d, _ in ps) and len({a for a, _, _ in ps}) == len(ps)
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    txt = {a: [f"{i.mnemonic} {i.op_str}" for i in md.disasm(d, a)] for a, d, w in ps if "código" in w}
    assert txt[C.CODE_SW][:3] == [f"bhi.w #{C.CODE_SW + 8:#x}", "b.w #0x437a4db6", "cmp.w r8, #0x17"]
    assert any("movs r5, #0x10" in x for x in txt[C.CODE_SW]) and any("movs r5, #0x11" in x for x in txt[C.CODE_SW])


@needs
def test_tipo_a_id():
    base = AVCAM.read_bytes()
    old, new = base, nuevo(base)

    def idt(img, tipo):
        mu = maquina(img)
        mu.mem_write(CTX + 0x138, struct.pack("<I", tipo))
        from unicorn.arm_const import UC_ARM_REG_R2, UC_ARM_REG_R3
        mu.reg_write(UC_ARM_REG_R3, CTX)
        mu.hook_add(UC_HOOK_CODE, lambda u, a, s, _: u.emu_stop() if a == 0x437AA840 else None)
        mu.emu_start(0x437AA800 | 1, SENT, count=200)
        return mu.reg_read(UC_ARM_REG_R2)

    assert [idt(old, t) for t in range(13)] == [0, 0xF, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0, 0, 0, 0, 0]
    assert [idt(new, t) for t in range(13)] == [0, 0xF, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0, 0, 0x18, 0x19, 0]


@needs
def test_switch_ids_nuevos_y_resto_intacto():
    from unicorn.arm_const import (
        UC_ARM_REG_R1,
        UC_ARM_REG_R2,
        UC_ARM_REG_R3,
        UC_ARM_REG_R5,
        UC_ARM_REG_R8,
        UC_ARM_REG_R9,
    )
    base = AVCAM.read_bytes()
    old, new = base, nuevo(base)
    cave = range(C.CODE_SW, C.CODE_SW + 0x40)

    def corre(img, r8):
        mu = maquina(img)
        mu.reg_write(UC_ARM_REG_R8, r8)
        res = {}

        def hook(u, a, s, _):
            if a in (C.SW_EPILOGO, C.SW_DEFECTO):
                res["fin"], res["r"] = a, [u.reg_read(r) for r in (UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R5, UC_ARM_REG_R9)]
                u.emu_stop()
            elif a not in cave and not 0x437A4DAE <= a < 0x437A4DBA and "tbh" not in res:
                res["tbh"] = a                                   # primera instrucción tras el tbh
                u.emu_stop()
        mu.hook_add(UC_HOOK_CODE, hook)
        mu.emu_start(0x437A4DAE | 1, SENT, count=100)
        return res

    for r8 in range(0x15):                                       # ids 1…0x15: mismo destino que antes
        assert corre(new, r8) == corre(old, r8), r8
    for r8 in (0x15, 0x16, 0x19, 0x1A, 0xFF):                    # ids 0x16, 0x17, 0x1a…: rama por defecto
        assert corre(new, r8)["fin"] == C.SW_DEFECTO == corre(old, r8)["fin"]
    assert corre(new, 0x17) == {"fin": C.SW_EPILOGO, "r": [0, C.IDX_SET, 0xFF, C.IDX_S3, 0xFF]}
    assert corre(new, 0x18) == {"fin": C.SW_EPILOGO, "r": [0, C.IDX_SET, 0xFF, C.IDX_CINE, 0xFF]}


@needs
def test_matrices_y_deltas():
    base = AVCAM.read_bytes()
    old, new = base, nuevo(base)
    t = props(P6000)[0x30001]
    m_s3, m_cine, delta = C.datos_a6300(P6300.read_bytes())

    def matriz(img, idx):
        mu = llama(img, t, 0x437A4B40, CTX + 0x100, idx, CTX)
        return bytes(mu.mem_read(CTX + 0x100, 18))

    esperada = {i: t[0x48 + 0x12 * i:][:18] for i in range(8)} | {i: t[0x400 + 0x12 * (i - 8):][:18] for i in range(8, 15)} | {0xF: t[0x310:][:18]}
    for i in (0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 0xF):
        assert matriz(old, i) == matriz(new, i) == esperada[i], i
    assert matriz(new, C.IDX_S3) == m_s3 and matriz(new, C.IDX_CINE) == m_cine
    assert matriz(old, C.IDX_S3) != m_s3

    def deltas(img, idx, blq):
        mu = llama(img, blq, 0x437A44D0, CTX + 0x200, idx, CTX)
        return bytes(mu.mem_read(CTX + 0x200, 0x30))

    for i in range(0x19):
        assert deltas(old, i, t) == deltas(new, i, t), i
    ref = bytearray(t)                                           # el mismo conjunto copiado a un hueco de la tabla original (conjunto 0xd)
    ref[0x100 + 0x18 * 0xD:0x100 + 0x18 * 0xD + 24] = delta
    assert deltas(new, C.IDX_SET, t) == deltas(old, 0xD, bytes(ref)) != deltas(new, 0xD, t)
    assert deltas(new, 0x1A, t) == deltas(new, C.IDX_SET, t)     # en la A6000 el gate permite hasta 0x1a (mismo conjunto)
    assert struct.unpack_from("<8b", delta) == (-28, 8, -28, 8, -64, -64, -64, -64)
