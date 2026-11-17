"""G79 — restricción de tarjeta de XAVC S en ObjMedia (libObj 3.21, Unicorn sobre bytes reales) y su parche."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import xavcs_card_patch as P

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
pytestmark = pytest.mark.skipif(not LIB.exists(), reason="libObj.so no disponible")
SET_INH, SALIDA = 0x94A8A4, 0x942202


def _factor(d, fs, clase, f25e=1):
    """Ejecuta 0x942156…0x942202 con el objeto ObjMedia simulado; devuelve el factor pasado a SetInhStatus (o None)."""
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import UC_ARM_REG_R1, UC_ARM_REG_R4, UC_ARM_REG_SP
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, 0x1100000)
    mu.mem_write(0, d)
    obj = 0x10F0000
    mu.mem_write(obj + 0x2C8, fs.to_bytes(2, "little"))
    mu.mem_write(obj + 0x25E, f25e.to_bytes(2, "little"))
    mu.mem_write(obj + 0x2A2, clase.to_bytes(2, "little"))
    out = {}

    def h(uc, addr, size, _):
        if addr == SET_INH:
            out["f"] = uc.reg_read(UC_ARM_REG_R1)
            uc.emu_stop()
        elif addr == SALIDA:
            uc.emu_stop()

    mu.hook_add(UC_HOOK_CODE, h)
    mu.reg_write(UC_ARM_REG_R4, obj)
    mu.reg_write(UC_ARM_REG_SP, 0x10F8000)
    mu.emu_start(0x942156 | 1, 0x942300, count=200)
    return out.get("f")


def test_restriccion_de_fabrica_y_parche():
    d = LIB.read_bytes()
    p = P.patch(d)
    assert P.patch(p) == p and sum(a != b for a, b in zip(d, p, strict=True)) == 2
    # FAT32 de una SDHC (fs ≠ 4, clase 0x8401): de fábrica pone 0x20000 (aviso XAVC S); con el parche, nada
    assert _factor(d, 2, 0x8401) == 0x20000
    assert _factor(p, 2, 0x8401) is None
    # exFAT en SDXC (0x8402): nunca se pone (lo de fábrica no cambia)
    assert _factor(d, 4, 0x8402) is None and _factor(p, 4, 0x8402) is None
    # exFAT con clase no SDXC (0x8400, lo que mide el arnés con una imagen exFAT): de fábrica 0x20000; con el parche, nada
    assert _factor(d, 4, 0x8400) == 0x20000 and _factor(p, 4, 0x8400) is None
