"""E24-04: el watchdog hardware de Darwin se arma con un tiempo por estado y se desactiva con 0.

Lee `darwin_core.bin` oficial (no versionado); se omite si falta. Informe: docs/capture/e24-04-dictamen-seguridad.md.
"""
import struct
from pathlib import Path

import pytest

capstone = pytest.importorskip("capstone")

ROOT = Path(__file__).resolve().parents[1]
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
BASE = 0x4200
ARM, FEED = 0xA4C4, 0xA524


@pytest.fixture(scope="module")
def core() -> bytes:
    if not DARWIN.exists():
        pytest.skip(f"falta {DARWIN.relative_to(ROOT)}")
    return DARWIN.read_bytes()


def _insns(core: bytes, addr: int, n: int):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.detail = True
    return list(md.disasm(core[addr - BASE:addr - BASE + n], addr))


def _lit(core: bytes, insn_addr: int, off: int) -> int:
    return struct.unpack_from("<I", core, (((insn_addr + 4) & ~3) + off) - BASE)[0]


def test_arm_function_reload_is_arg_times_0x1869f_and_zero_disarms(core):
    ins = {i.address: f"{i.mnemonic} {i.op_str}" for i in _insns(core, ARM, 0x60)}
    assert ins[0xA4C6] == "cbnz r0, #0xa4cc"                 # arg 0 → rama que desarma (0xa4ac: control = 0)
    assert _lit(core, 0xA4CC, 0x70) == 0x1869F               # r1
    assert _lit(core, 0xA4CE, 0x68) == 0x1ACCE551            # clave de desbloqueo
    assert ins[0xA4D0] == "muls r0, r1, r0"                  # recarga = arg × 0x1869f
    assert ins[0xA4D8] == "str r0, [r1]"                     # WDG_LDR = recarga
    assert _lit(core, 0xA4D2, 0x68) == 0x40011000            # base del HWWDT


def test_arm_function_callers_pass_a_configured_byte_per_state(core):
    # llamadores de 0xa4c4 y el byte de configuración `+0x40..+0x43` que pasan como argumento
    callers = {0x73D4: 0x40, 0x7956: 0x41, 0x804E: 0x42, 0x823C: 0x43, 0x8460: 0x43}  # 0x1bfae lo recarga antes de un `pop.w`
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.detail = True
    found = {}
    for a in range(BASE, BASE + 0x23000, 2):
        for i in md.disasm(core[a - BASE:a - BASE + 4], a, 1):
            if i.mnemonic in ("bl", "b.w") and i.operands and i.operands[0].imm in (ARM, FEED):
                prev = next(md.disasm(core[a - 4 - BASE:a - BASE], a - 4), None)
                found[a] = (i.operands[0].imm, prev)
    arm = {a: p for a, (t, p) in found.items() if t == ARM}
    assert set(arm) == set(callers) | {0x1BFAE}
    for a, off in callers.items():
        p = arm[a]
        assert p.mnemonic == "ldrb.w" and p.op_str.endswith(f"#{off:#x}]"), hex(a)
    assert {a for a, (t, _) in found.items() if t == FEED} == {0x79A6, 0x8A3E}
