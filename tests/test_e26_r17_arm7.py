"""E26-R17 — pruebas offline del BossFirm ARM7 (bootloader.bin histórico). Se omiten si falta el binario.

Comprueban instrucciones/literales del desensamblado; no demuestran comportamiento del LDEC físico.
"""

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "e26-recovery"))

A = importlib.import_module("r16_arm7")
pytestmark = pytest.mark.skipif(
    not A.BL.is_file(), reason="bootloader.bin histórico ausente"
)
F = importlib.import_module("r17_arm7_full")


def _text(a: int) -> str:
    i = F.ins_at(a)
    return f"{i.mnemonic} {i.op_str}"


def test_dispatch_table_and_ldec_op0():
    assert [F.word(0x379C + 4 * k) for k in range(2)] == [0x1338, 0x15AC]
    assert _text(0xF14) == "ldr r1, [sb, r0, lsl #2]" and _text(0xF1C) == "bx r1"


def test_coverage_and_ldec_base_sites():
    r = F.explore()
    assert 4 * len(r["seen"]) / F.N > 0.9
    assert sorted(a for a, v in F.literal_loads().items() if v == F.LDEC) == [
        0x3F8,
        0x440,
        0x4D8,
    ]


def test_ldec_0c_written_once_from_job_0c():
    assert _text(0x424) == "ldr r3, [r0, #0xc]" and _text(0x428) == "str r3, [r1, #0xc]"
    assert _text(0x42C) == "ldr r0, [r0, #0x10]"
    # la rutina de configuración no lee trabajo+8
    assert not any("[r0, #8]" in _text(a) for a in range(0x3F4, 0x43C, 4))


def test_op0_never_reads_job_plus8():
    # 0x1338..0x1414: r7 = trabajo; solo [r7] y [r7,#4]
    uses = [_text(a) for a in range(0x1338, 0x1414, 4) if "[r7" in _text(a)]
    assert uses and all(u.endswith(("[r7]", "[r7, #4]")) for u in uses)


def test_ldec_isr_error_map():
    assert (
        _text(0x450) == "ldr r0, [r2, #0x34]" and _text(0x454) == "str r0, [r2, #0x30]"
    )
    codes = {0x10: 0x29, 0x2: 0x2C, 0x4: 0x2B, 0x8: 0x2A, 0x20: 0x28, 0x40: 0x2D}
    for a, (bit, code) in zip(
        (0x458, 0x468, 0x474, 0x480, 0x490, 0x49C), codes.items()
    ):
        assert (
            _text(a).startswith("cmp r0, #") and int(_text(a).split("#")[1], 0) == bit
        )
        assert _text(a + 4) == f"moveq r0, #{code:#x}"
