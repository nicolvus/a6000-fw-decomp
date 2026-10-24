"""Regresiones de identidad, ABI, límites y punteros; solo lectura del firmware."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recordimage_audit import LIBRARIES, Elf32


@pytest.fixture(scope="module", params=LIBRARIES)
def image(request):
    return request.param, Elf32(LIBRARIES[request.param])


def test_unwind_intervals_and_real_entries(image):
    model, elf = image
    if model == "A7S":
        assert elf.unwind_span(0x84803A) == (0x847E1C, 0x84814C)
        assert elf.read(0x847E1C, 8).hex() == "2de9f047adf5567d"
        assert elf.read(0x848100, 4).hex() == "bde8f087"
        assert elf.read(0x84814C, 4).hex() == "2de9f041"
    else:
        assert elf.unwind_span(0x90B248) == (0x90B248, 0x90C088)
        assert elf.unwind_span(0x90DE2E) == (0x90D7E8, 0x90E148)
        assert elf.unwind_span(0x91634E) == (0x9162D0, 0x91647C)
        assert elf.read(0x91631A, 13).hex() == "076d121d6d27326d6d3d6d4f61"
        assert elf.instruction(0x916316).mnemonic == "tbb"


def test_identity_from_resolved_pc_relative_strings(image):
    model, elf = image
    if model == "A7S":
        assert elf.pc_string(0x847E26, 0x847E30) == (0xCB6F2B, " RecordStill :")
        for load, add in [(0x847F4E, 0x847F52), (0x847F60, 0x847F64),
                          (0x847FD6, 0x847FDA), (0x847FE8, 0x847FEC),
                          (0x848018, 0x84801C), (0x84803A, 0x84803E)]:
            assert elf.pc_string(load, add) == (0xCB7BBB, "RecordStill")
    else:
        assert elf.pc_string(0x90B254, 0x90B25C) == (0xDDF3FC, " RecordImage :")
        assert elf.pc_string(0x90B310, 0x90B316) == (0xDDFD72, "RecordImage")


def test_different_argument_contracts(image):
    model, elf = image
    if model == "A7S":
        assert elf.instruction(0x847E32).op_str == "sl, r2"
        assert elf.instruction(0x847E34).op_str == "r8, r3"
        # 0x20 saved + 0x358 locals; r7 = sp + 8 => incoming sp = r7 + 0x370.
        assert elf.instruction(0x847E36).op_str == "sb, [r7, #0x370]"
        assert elf.instruction(0x847E4C).op_str == "r1, #0x1001"
        assert elf.instruction(0x847E84).op_str == "r1, #0x1002"
        assert elf.instruction(0x847EBC).op_str == "r1, #0x100e"
        assert elf.instruction(0x8480BC).op_str == "#0x83c9a0"
        assert elf.instruction(0x8480F8).op_str == "r0, r5"
    else:
        assert elf.instruction(0x90B252).op_str == "r8, r1"
        assert elf.instruction(0x90B2A4).op_str == "r1, #0x100f"
        assert elf.instruction(0x90B2AA).op_str == "#0xe01a8"
        assert elf.instruction(0x90BEAA).op_str == "r0, r5"
        assert elf.read(0x90BEB6, 4).hex() == "bde8f08f"


def test_indirect_dispatch_evidence_is_positive_and_scoped():
    elf = Elf32(LIBRARIES["A6000"])
    hits = elf.word_hits(0x90D7E9)
    assert hits == list(range(0x101EF18, 0x101F159, 0x18))
    assert elf.u32(0x101EF10) == 0x10000003
    assert elf.u32(0x101EF18) == 0x90D7E9  # Thumb bit preserved.
    assert elf.offset(0x101EF18) == 0x1016F18  # VA != file offset in data.
    # These negatives describe only exact words in file-backed PT_LOAD segments.
    assert elf.word_hits(0x90B248) == []
    assert elf.word_hits(0x90B249) == []
    assert elf.word_hits(0x9162D0) == []
    assert elf.word_hits(0x9162D1) == []
    section = elf.sections[".rel.dyn"]
    relocations = {
        elf.u32(section[3] + delta): elf.u32(section[3] + delta + 4)
        for delta in range(0, section[5], 8)
    }
    assert all(relocations[va] == 23 for va in hits)  # R_ARM_RELATIVE.


def test_statemgr_consumes_recordimage_callback_table():
    obj = Elf32(LIBRARIES["A6000"])
    mgr = Elf32(LIBRARIES["A6000"].with_name("libmprctrl.so"))
    start = 0x101EF0C
    rows = [[obj.u32(start + i * 0x18 + j * 4) for j in range(6)] for i in range(25)]
    assert len(rows) * 0x18 == 0x258
    assert all(row[3] == 0x90D7E9 for row in rows)
    assert rows[0] == [0, 0x10000003, 0x907BA1, 0x90D7E9, 0x907C95, 1]
    assert rows[22][:2] == [2, 0x10000005]
    assert obj.instruction(0x91776E).op_str == "r1, [pc, #0x178]"
    assert (obj.u32(0x9178E8) + 0x91777E) & 0xFFFFFFFF == start
    assert obj.instruction(0x917770).op_str == "r2, #0x258"
    assert obj.instruction(0x91777C).op_str == "#0xe0964"  # memcpy
    assert obj.instruction(0x917782).op_str == "r1, #0x19"
    assert obj.instruction(0x917786).op_str == "#0xdc4ec"  # AddEntry
    assert obj.instruction(0x916676).op_str == "#0x919908"
    assert obj.instruction(0x919BD4).op_str == "r0, [r4, #0x8c]"
    assert obj.instruction(0x919BDC).op_str == "#0xe027c"  # ChangeState
    assert mgr.instruction(0x1CF74).op_str == "r3, [r6, #0xc]"
    assert mgr.instruction(0x1CF7E).op_str == "#0xea24"  # CallFunc
    assert mgr.instruction(0x1CEEA).op_str == "r3, [r1, #0xc]"
    assert mgr.instruction(0x1CEF2).mnemonic == "blx"
    assert mgr.instruction(0x1CEF2).op_str == "r3"


def test_actual_counterparts_and_nested_call():
    a, b = (Elf32(LIBRARIES[model]) for model in ["A6000", "A7S"])
    assert a.unwind_span(0x908AFC) == (0x908AFC, 0x908E2C)
    assert b.unwind_span(0x84A568) == (0x84A568, 0x84B3A8)
    assert a.pc_string(0x908B06, 0x908B10)[1] == " RecordStill :"
    assert b.pc_string(0x84A574, 0x84A57C)[1] == " RecordImage :"
    assert b.instruction(0x84A5C4).op_str == "r1, #0x100f"
    assert b.instruction(0x84A5CA).op_str == "#0xe3604"
    assert a.instruction(0x90BBDC).op_str == "#0x908afc"
    assert b.instruction(0x84AEFC).op_str == "#0x847e1c"
    assert a.read(0x90BBCC, 16) == b.read(0x84AEEC, 16)  # Five-argument setup.


def test_recordstill_whole_code_layout_with_explicit_exceptions():
    """260 instructions; callee semantics are NOT proven by masking call targets."""
    a, b = (Elf32(LIBRARIES[model]) for model in ["A6000", "A7S"])
    left = list(a.decoder.disasm(a.read(0x908AFC, 0x2E8), 0x908AFC))
    right = list(b.decoder.disasm(b.read(0x847E1C, 0x2E8), 0x847E1C))
    assert len(left) == len(right) == 260
    line_offsets = {0x128, 0x13A, 0x1B0, 0x1C2, 0x1F2, 0x214}
    calls = 0
    for x, y in zip(left, right, strict=True):
        assert x.address - 0x908AFC == y.address - 0x847E1C
        assert x.size == y.size and x.mnemonic == y.mnemonic
        if x.mnemonic in {"bl", "blx"}:
            calls += 1
        elif x.address - 0x908AFC in line_offsets:
            assert x.op_str.startswith("r3,") and y.op_str.startswith("r3,")
            assert y.operands[1].imm == x.operands[1].imm + 9
        else:
            assert x.bytes == y.bytes
    assert calls == 43
