"""G107 — `PreTypeCheck`/`EnumValueCheck` de `libObj` (0xa3a21c): las listas de VALUEID admitidos de Color Mode y Gamma deben incluir los del CFW.

Se ejecuta con Unicorn la función real que da la definición de tipo de un PARAMID (`0x95aca8`) sobre la `libObj` parcheada y se leen clase, cuenta y lista.
"""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "tests"))
import add_menu_entry as A
import patch_libobj_pp as P
from test_g25_gamma_libobj import LIB, needs

uc = pytest.importorskip("unicorn")
COLOR_IDS, GAMMA_IDS = (0x9673, 0x9692), (0x9685, 0x96A4)


def definicion(d: bytes, pid: int) -> tuple[int, list[int]]:
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP
    segs = A._segments(d)
    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, (top + 0xFFFFF) & ~0xFFFFF)
    for t, off, va, _, fs, _, _, _ in segs:
        if t == 1:
            mu.mem_write(va, d[off:off + fs])
    mu.mem_map(0x20000000, 0x100000)
    mu.reg_write(UC_ARM_REG_SP, 0x20080000)
    mu.reg_write(UC_ARM_REG_R0, pid)
    mu.reg_write(UC_ARM_REG_LR, 0x30001)
    mu.emu_start(0x95ACA8 | 1, 0x30000, count=100000)
    r = mu.reg_read(UC_ARM_REG_R0)
    _, b, p = struct.unpack("<3I", bytes(mu.mem_read(r, 12)))
    assert b & 0xFF == 4, "no es una comprobación de enumerado"
    return b >> 16, list(struct.unpack(f"<{b >> 16}I", bytes(mu.mem_read(p, 4 * (b >> 16)))))


@needs
def test_fabrica_rechaza_los_valores_del_cfw():
    d = LIB.read_bytes()
    assert not set(P.COLOR[8:]) & set(definicion(d, 0x9673)[1])
    assert 0x585 not in definicion(d, 0x9685)[1]


@needs
def test_listas_ampliadas_con_color_y_gamma_del_cfw():
    import pp_valuecheck_patch as V
    d = V.patch(P.patch_color(P.patch_gamma(LIB.read_bytes(), hlg=True)), hlg=True)
    for pid in COLOR_IDS:
        n, lista = definicion(d, pid)
        assert lista == list(P.COLOR) and n == 12
    for pid in GAMMA_IDS:
        assert set(P.VALUEID_HLG) <= set(definicion(d, pid)[1])
    assert V.patch(d, hlg=True) == d                                          # idempotente


def test_bw_y_sgamut_no_son_centinelas_de_la_a6000():
    assert not {0x504, 0x505} & set(P.COLOR)                                  # VALUEID_NO_SET / VALUEID_COMP_RESULT_OK en la A6000
    assert len(set(P.COLOR) | set(P.VALUEID_HLG)) == len(P.COLOR) + len(P.VALUEID_HLG)
