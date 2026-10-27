"""E25-04 — comprobaciones estáticas del fin de L0 y de los temporizadores (sin cámara).

Verifica dos hechos nuevos que sostienen el veredicto F = NO del informe:
  * el estado exterior 9 libera el bit 24 de la máscara de ocupación y el 10 es el id terminal;
  * la espera acotada de 1000 unidades (0x1ff2a) pertenece a la API de carga (0x1984e),
    no al camino de captura, que espera a 0x199d0 sin ese límite.

Solo lee `darwin_core.bin` oficial (no versionado); se omite si falta.
Informe: docs/capture/e25-04-recuperabilidad-y-decision.md
"""
from __future__ import annotations

import struct
from pathlib import Path

import pytest

capstone = pytest.importorskip("capstone")

ROOT = Path(__file__).resolve().parents[1]
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
BASE = 0x4200


@pytest.fixture(scope="module")
def core() -> bytes:
    if not DARWIN.exists():
        pytest.skip(f"falta {DARWIN.relative_to(ROOT)}")
    return DARWIN.read_bytes()


def _u32(core: bytes, addr: int) -> int:
    return struct.unpack_from("<I", core, addr - BASE)[0]


def _insns(core: bytes, addr: int, size: int):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    md.detail = True
    return list(md.disasm(core[addr - BASE:addr - BASE + size], addr))


def _text(core: bytes, addr: int, size: int = 4) -> str:
    ins = _insns(core, addr, size)
    return f"{ins[0].mnemonic} {ins[0].op_str}" if ins else ""


def test_l0_state9_releases_bit24_and_state10_is_terminal(core):
    # L0 = [0,7,8,9,10] (bytes 0x29cd8..0x29cdc)
    assert core[0x29CD8 - BASE:0x29CD8 - BASE + 5] == bytes([0x00, 0x07, 0x08, 0x09, 0x0A])

    # Tabla exterior 0x29d0c: pares (id, manejador|1); el id terminal es 0xa.
    assert _u32(core, 0x29CF4) == 0xA              # id máximo/terminal del descriptor 0x29cf0
    assert _u32(core, 0x29D54) == 9 and _u32(core, 0x29D58) == 0x200E6 | 1
    assert _u32(core, 0x29D5C) == 0xA and _u32(core, 0x29D60) == 0x200FC | 1

    # Estado 9: mov.w r0,#0x1000000; bl 0xd18e; 0xd18e hace bics en [0x20002bd0+8] y +4.
    assert "mov.w r0, #0x1000000" in _text(core, 0x200EA)
    assert "bl #0xd18e" in _text(core, 0x200EE)
    assert "ldr r5, [pc" in _text(core, 0xD198)
    assert "ldr r1, [r5, #8]" in _text(core, 0xD19A)
    assert "bics r1, r0" in _text(core, 0xD19C)
    assert "str r1, [r5, #8]" in _text(core, 0xD19E)
    assert "ldr r1, [r5, #4]" in _text(core, 0xD1A0)
    assert "bics r1, r0" in _text(core, 0xD1A2)
    assert "str r1, [r5, #4]" in _text(core, 0xD1A6)


def test_bounded_1000_wait_belongs_to_load_api_not_capture(core):
    # 0x1ff2a: presupuesto de 1000 unidades y sondeo de 0x201a0; solo lo llama 0x19884.
    assert "mov.w r5, #0x3e8" in _text(core, 0x1FF32)
    assert "bl #0x1e512" in _text(core, 0x1FF40)
    assert "bl #0x1ff2a" in _text(core, 0x19884)

    callers = set()
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    md.detail = True
    for addr in range(BASE, BASE + len(core) - 4, 2):
        for ins in md.disasm(core[addr - BASE:addr - BASE + 4], addr, 1):
            if ins.mnemonic in ("bl", "b.w") and ins.operands and ins.operands[0].imm == 0x1FF2A:
                callers.add(addr)
    assert callers == {0x19884}

    # El camino de captura espera a 0x199d0 mientras devuelve 0, sin el presupuesto de 1000.
    assert "bl #0x199d0" in _text(core, 0x17DBA)
    assert "beq #0x17dba" in _text(core, 0x17DC0)
    assert "b.w #0x20018" in _text(core, 0x199D0)
    assert "ldr.w r0, [r0, #0x12c]" in _text(core, 0x2001A)
    assert "movs r0, #0" in _text(core, 0x20020)
    assert "bx lr" in _text(core, 0x20022)
