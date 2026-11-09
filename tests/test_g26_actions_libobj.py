"""G26: Copy (0x41) y Reset (0x42) de Picture Profile en el despachador de comandos de `libObj.so` (emulación Unicorn del tramo parcheado)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "tests"))
import patch_libobj_pp as P
from test_g25_gamma_libobj import LIB, needs

uc = pytest.importorskip("unicorn")


def destino(img, ident):
    """Ejecuta desde la comparación 0x4cfcda con r0=id, r5=mensaje, r4=parámetro; devuelve a qué sitio llega primero."""
    from unicorn import UC_HOOK_CODE, Uc, UC_ARCH_ARM, UC_MODE_THUMB
    from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_SP

    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, 0x1100000)
    mu.mem_write(0, img[:0x1100000])
    mu.mem_map(0x20000000, 0x10000)
    stops = {P.DISP_SET: "set", P.DISP_ERR: "error", P.H_COPY: "copy", P.H_RESET: "reset"}
    got = []

    def hook(u, a, s, _):
        if a in stops:
            got.append((stops[a], u.reg_read(UC_ARM_REG_R0), u.reg_read(UC_ARM_REG_R1)))
            u.emu_stop()

    mu.hook_add(UC_HOOK_CODE, hook)
    mu.reg_write(UC_ARM_REG_R0, ident)
    mu.reg_write(UC_ARM_REG_R5, 0x20000100)
    mu.reg_write(UC_ARM_REG_R4, 7)
    mu.reg_write(UC_ARM_REG_SP, 0x2000F000)
    mu.emu_start(P.DISP_SITE | 1, 0x20008000, count=200)
    return got[0] if got else None


@needs
def test_copy_y_reset_llegan_a_sus_acciones_y_lo_demas_sigue_igual():
    old, new = LIB.read_bytes(), P.patch_actions(P.patch_gamma(LIB.read_bytes()))
    assert destino(old, 0x40)[0] == destino(new, 0x40)[0] == "set"
    assert destino(old, 0x41)[0] == "error" and destino(old, 0x42)[0] == "error"          # la A6000 original no las despacha
    assert destino(new, 0x41) == ("copy", 0x20000100, 7) and destino(new, 0x42) == ("reset", 0x20000100, 7)
    for i in (0x43, 0x44):
        assert destino(new, i)[0] == "error"


@needs
def test_actions_exige_el_hueco_de_gamma():
    with pytest.raises(AssertionError):
        P.patch_actions(LIB.read_bytes())
