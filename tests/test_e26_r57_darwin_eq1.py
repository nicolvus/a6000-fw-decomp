"""E26-R57: la compuerta de Darwin del 3.36 solo cierra con pkt[0x0e] == 1 (el 3.35 cerraba con cualquier valor != 0)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from e25_24 import patch_darwin as PD

capstone = pytest.importorskip("capstone")
unicorn = pytest.importorskip("unicorn")
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
needs = pytest.mark.skipif(not DARWIN.is_file(), reason="darwin_core.bin original ausente")
FLAG, ORIG, RET = 0x20003716, 0x1B080, 0x20c7d


def _run(cave: bytes, flag: int) -> tuple[int, int]:
    """Ejecuta la compuerta en 0x4318 con el flag dado; devuelve (r0, pc final) — el pc es ORIG si salta a Sony."""
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0x0, 0x40000)
    mu.mem_map(0x20000000, 0x10000)
    mu.mem_write(PD.CAVE, cave)
    mu.mem_write(PD.LITERAL, FLAG.to_bytes(4, "little"))
    mu.mem_write(FLAG, bytes([flag]))
    mu.reg_write(UC_ARM_REG_LR, RET | 1)
    mu.reg_write(UC_ARM_REG_SP, 0x20008000)
    mu.reg_write(UC_ARM_REG_R0, 0)
    hit = []
    mu.hook_add(UC_HOOK_CODE, lambda m, a, s, u: (hit.append(a), m.emu_stop()) if a == ORIG else None)
    mu.emu_start(PD.CAVE | 1, RET & ~1, count=20)
    return mu.reg_read(UC_ARM_REG_R0), (ORIG if hit else mu.reg_read(UC_ARM_REG_PC))


@needs
@pytest.mark.parametrize("flag,cierra", [(0, False), (1, True), (2, False), (0xFF, False), (0x80, False)])
def test_eq1_solo_cierra_con_uno(flag, cierra):
    r0, pc = _run(PD.cave_bytes_eq1(), flag)
    assert (pc != ORIG) == cierra
    if cierra:
        assert r0 == 0


@needs
def test_cave_35_cierra_con_cualquier_valor():
    old = _run(PD.cave_bytes(), 0xFF)
    assert old[1] != ORIG, "el 3.35 cerraba con 0xff"


@needs
def test_eq1_parche_reversible_y_solo_toca_sus_sitios():
    PD.use_eq1()
    try:
        orig = DARWIN.read_bytes()
        new, diff = PD.apply_bytes(orig)
        assert PD.restore_bytes(new) == orig
        assert {d["address"] for d in diff} <= PD.allowed_addresses()
        assert new[PD.CAVE - PD.BASE:PD.CAVE - PD.BASE + 16] == PD.cave_bytes_eq1()
    finally:
        import importlib
        importlib.reload(PD)
