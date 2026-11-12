"""G22: tres estados (Mecánico / EFCS / Electrónico) en BIONZ, en línea y sin cuevas (offline, emulado)."""
from __future__ import annotations

import hashlib
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

unicorn = pytest.importorskip("unicorn")
capstone = pytest.importorskip("capstone")
from g22 import patch_tristate as P
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_R0,
    UC_ARM_REG_R4,
    UC_ARM_REG_R5,
    UC_ARM_REG_R6,
    UC_ARM_REG_R9,
    UC_ARM_REG_SP,
)

BASE = P.BASE
AVCAM = ROOT / "analysis/e25-27/artifacts-338/av-cam.integrated.bin"
needs = pytest.mark.skipif(not AVCAM.is_file(), reason="av-cam del 3.38 ausente")


@pytest.fixture(scope="module")
def pair() -> tuple[bytes, bytes]:
    orig = AVCAM.read_bytes()
    assert hashlib.sha256(orig).hexdigest() == P.SHA256_3_38
    return orig, P.apply_bytes(orig)[0]


def _uc(code: bytes) -> Uc:
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(BASE, (len(code) + 0xFFF) & ~0xFFF)
    uc.mem_write(BASE, code)
    uc.mem_map(0x50000000, 0x20000)
    return uc


def _run(uc: Uc, start: int, stop: int) -> None:
    uc.hook_add(UC_HOOK_CODE, lambda u, a, s, d: u.emu_stop() if a == stop else None)
    uc.emu_start(start | 1, 0)


@needs
def test_solo_cambia_lo_previsto_y_revierte(pair):
    orig, out = pair
    diff = {BASE + i for i, (a, b) in enumerate(zip(orig, out)) if a != b}
    assert diff and diff <= P.allowed_addresses()
    assert out[:0x1000] == orig[:0x1000]                       # bloque TPZL 0 intacto (R55)
    assert P.restore_bytes(out) == orig


@needs
@pytest.mark.parametrize("efcs,silent", [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_copiador_igual_que_sony_salvo_el_byte_nuevo(pair, efcs, silent):
    """0x43845f2e..0x43845fa4: misma memoria de `cap` y mismo `sb`; se añade cap+0x41d = silent y, con Silent, cap+0x41c = 1 (EFCS de Sony
    desactivado, como el A6300: Silent manda sobre EFCS; G22-A, el estado EFCS On + Silent On equivale al (1,1) medido en R87)."""
    orig, out = pair
    rng = random.Random(7)
    blk_bytes = bytes(rng.randrange(256) for _ in range(0x600))

    def run(code):
        uc = _uc(code)
        blk, ptr, cap = 0x50000000, 0x50001000, 0x50004000
        uc.mem_write(blk, blk_bytes)
        uc.mem_write(blk + 0x210, efcs.to_bytes(4, "little"))
        uc.mem_write(blk + 0x238, silent.to_bytes(4, "little"))
        uc.mem_write(ptr, blk.to_bytes(4, "little"))
        uc.mem_write(cap, bytes(0x1000))
        for r, v in ((UC_ARM_REG_R5, ptr), (UC_ARM_REG_R4, cap), (UC_ARM_REG_SP, 0x5001F000)):
            uc.reg_write(r, v)
        _run(uc, 0x43845F2E, 0x43845FA4)
        return bytes(uc.mem_read(cap, 0x1000)), uc.reg_read(unicorn.arm_const.UC_ARM_REG_SB)

    mem_o, sb_o = run(orig)
    mem_n, sb_n = run(out)
    assert sb_o == sb_n
    diff = [i for i in range(0x1000) if mem_o[i] != mem_n[i]]
    assert diff == ([0x41C] if silent and not efcs else []) + ([0x41D] if silent else [])
    assert mem_n[0x41C] == efcs | silent and mem_n[0x41D] == silent


@needs
@pytest.mark.parametrize("r6", [0, 1])
@pytest.mark.parametrize("efcs,silent", [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_envio_pkt0e_es_electronico(pair, r6, efcs, silent):
    """0x438d01a2 -> strb de 0x438d01fa, en las dos ramas (r6 == 0 y r6 != 0); Sony original = EFCS en vivo no."""
    _, out = pair
    uc = _uc(out)
    obj, carga = 0x50000000, 0x50008000
    uc.mem_write(obj + 0x4AD8, carga.to_bytes(4, "little"))
    uc.mem_write(carga + 0x20, (carga + 0x100).to_bytes(4, "little"))
    uc.mem_write(P.LIVE_BASE + 0x210, efcs.to_bytes(4, "little"))
    uc.mem_write(P.LIVE_BASE + 0x238, silent.to_bytes(4, "little"))
    uc.reg_write(UC_ARM_REG_R4, obj)
    uc.reg_write(UC_ARM_REG_R6, r6)
    uc.reg_write(UC_ARM_REG_SP, 0x5001F000)
    _run(uc, 0x438D01A2, 0x438D01FE)
    assert uc.mem_read(carga + 0x4E, 1)[0] == silent
    # r6 == 0 deja obj+0x768 = 1 (como Sony: no ejecuta 0x438d01c2); r6 != 0 lo pone a 0
    assert uc.mem_read(obj + 0x768, 1)[0] == (1 if r6 == 0 else 0)


@needs
@pytest.mark.parametrize("efcs,silent", [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_ctor_pkt0e_lee_el_byte_nuevo_y_pkt0d_igual(pair, efcs, silent):
    orig, out = pair
    for r0, r1, r2 in ((0, 0, 0), (3, 1, 2), (255, 255, 3), (7, 2, 1)):
        res = []
        for code in (orig, out):
            uc = _uc(code)
            pkt, cap = 0x50000000, 0x50001000
            uc.mem_write(cap + 0x41C, efcs.to_bytes(4, "little"))
            uc.mem_write(cap + 0x41D, bytes([silent]))
            for r, v in ((UC_ARM_REG_R0, r0), (unicorn.arm_const.UC_ARM_REG_R1, r1), (unicorn.arm_const.UC_ARM_REG_R2, r2),
                         (UC_ARM_REG_R4, pkt), (UC_ARM_REG_R9, cap), (UC_ARM_REG_SP, 0x50001F00)):
                uc.reg_write(r, v)
            _run(uc, 0x43841472, 0x4384148C)
            res.append(bytes(uc.mem_read(pkt, 0x10)))
        so, nw = res
        assert nw[0x0D] == so[0x0D] and nw[0x0E] == silent


@needs
def test_lectores_de_sony_siguen_viendo_solo_el_efcs(pair):
    """La palabra cap+0x41c = efcs | electronic << 8: los dos `cmp #1` de Sony deben leer el byte bajo."""
    _, out = pair
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    for addr, reg in ((0x4384219E, "r1"), (0x43842270, "r2")):
        ins = next(md.disasm(out[addr - BASE:addr - BASE + 4], addr))
        assert (ins.mnemonic, ins.op_str) == ("ldrb.w", f"{reg}, [r7, #0x41c]")
        uc = _uc(out)
        uc.mem_write(0x50001000 + 0x41C, (0x101).to_bytes(4, "little"))
        uc.reg_write(UC_ARM_REG_R4, 0)
        uc.reg_write(unicorn.arm_const.UC_ARM_REG_R7, 0x50001000)
        _run(uc, addr, addr + 4)
        assert uc.reg_read(unicorn.arm_const.UC_ARM_REG_R1 if reg == "r1" else unicorn.arm_const.UC_ARM_REG_R2) == 1
