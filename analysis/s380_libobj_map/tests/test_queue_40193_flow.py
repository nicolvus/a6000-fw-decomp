"""Regresiones de S384: un literal en .text no es un falso positivo."""

import hashlib
import struct
import sys
from pathlib import Path

import pytest
from capstone import CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB, Cs

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from queue_40193_flow import literal_loads, mov_halves
from recordimage_audit import LIBRARIES, Elf32

AV_BASE = 0x43541000


@pytest.fixture(scope="module")
def avcam():
    root = Path(__file__).resolve().parents[3]
    data = (root / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
            "nflasha3_unpacked_unpacked/av-cam.bin").read_bytes()
    assert hashlib.sha256(data).hexdigest() == (
        "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
    )
    return data


def av_instruction(data, address):
    return next(Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(
        data[address - AV_BASE:address - AV_BASE + 4], address, count=1,
    ))


def av_word(data, address):
    return struct.unpack_from("<I", data, address - AV_BASE)[0]


def test_receiver_initializer_in_contiguous_thumb_pointer_table(avcam):
    start, end = 0x43B7F8A8, 0x43B7FE78
    pointers = [av_word(avcam, address) for address in range(start, end, 4)]
    assert len(pointers) == 372
    assert pointers[189] == 0x4379E93D
    assert all(pointer & 1 and AV_BASE <= pointer - 1 < end for pointer in pointers)
    assert av_word(avcam, end) == 0


def test_liro_header_reaches_initializer_table_consumer(avcam):
    assert av_word(avcam, 0x4354101C) == 0x43541078
    arm_call = next(Cs(CS_ARCH_ARM, CS_MODE_ARM).disasm(
        avcam[0x7C:0x80], 0x4354107C, count=1,
    ))
    assert (arm_call.mnemonic, arm_call.op_str) == ("blx", "#0x43a3a98c")
    assert (av_instruction(avcam, 0x43A3A998).mnemonic,
            av_instruction(avcam, 0x43A3A998).op_str) == (
                "bl", "#0x4356082c",
            )

    got_base = (av_word(avcam, 0x435608A4) + 0x4356083E) & 0xFFFFFFFF
    assert got_base == 0x4401EEE4
    start_slot = got_base + av_word(avcam, 0x435608B8)
    end_slot = got_base + av_word(avcam, 0x435608B4)
    start, end = av_word(avcam, start_slot), av_word(avcam, end_slot)
    assert (start_slot, end_slot) == (0x440206D8, 0x440200B4)
    assert (start, end, (end - start) // 4) == (0x43B7F8A8, 0x43B7FE78, 372)
    assert [av_instruction(avcam, address).mnemonic for address in (
        0x4356086C, 0x43560870, 0x43560872, 0x43560874,
        0x43560878, 0x43560882, 0x43560888,
    )] == ["ldr", "ldr", "subs", "asrs", "ldr", "blx", "blo"]
    assert av_instruction(avcam, 0x43560882).op_str == "r3"
    assert av_instruction(avcam, 0x43560888).op_str == "#0x43560878"
    assert av_word(avcam, start + 189 * 4) == 0x4379E93D


def test_literal_load_pc_alignment_and_negative_displacement():
    # Thumb T1, T2 positivo y negativo; PC se alinea a cuatro bytes.
    data = bytes.fromhex("00 49 df f8 04 20 5f f8 04 30")
    assert list(literal_loads(data, 0x1000)) == [
        (0x1000, 1, 0x1004), (0x1002, 2, 0x1008), (0x1006, 3, 0x1004),
    ]


def test_halves_do_not_confuse_movw_with_movt_or_branch():
    data = bytes.fromhex("40 f2 93 13 c0 f2 04 03 40 f2 93 f9")
    assert list(mov_halves(data, 0x1000)) == [
        (0x1000, "movw", 3, 0x193), (0x1004, "movt", 3, 4),
    ]


def test_all_nine_a6000_words_have_literal_load_candidates():
    elf = Elf32(LIBRARIES["A6000"])
    section = elf.sections[".text"]
    hits = set(elf.word_hits(0x40193))
    refs = [(a, reg, pool) for a, reg, pool in literal_loads(
        elf.read(section[3], section[5]), section[3],
    ) if pool in hits]
    assert refs == [
        (0xADAF84, 1, 0xADB084), (0xAF929E, 1, 0xAF92D0),
        (0xAF9312, 1, 0xAF9344), (0xAF9382, 1, 0xAF93B4),
        (0xAF93F2, 1, 0xAF9424), (0xAF9CAA, 1, 0xAF9CE0),
        (0xAF9D0A, 1, 0xAF9D40), (0xAF9D6A, 1, 0xAF9DA0),
        (0xAF9DCA, 1, 0xAF9E00),
    ]
    for address, _, pool in refs:
        ins = elf.instruction(address)
        assert ins.mnemonic == "ldr" and ins.op_str.startswith("r1, [pc,")
        assert ((address + 4) & ~3) + ins.operands[1].mem.disp == pool


@pytest.mark.parametrize("entry", [0xAF503C, 0xAF5110, 0xAF51E4, 0xAF52B8])
def test_sender_preserves_destination_through_allocation_and_copy(entry):
    elf = Elf32(LIBRARIES["A6000"])
    wrappers = {0xAF503C: 0xAF5104, 0xAF5110: 0xAF51D8,
                0xAF51E4: 0xAF52AC, 0xAF52B8: 0xAF5380}
    assert elf.instruction(wrappers[entry] + 8).op_str == f"#{entry:#x}"
    expected = {
        0xAF5046: "r5, r1", 0xAF5048: "r0, r1",
        0xAF504A: "r8, r2", 0xAF5050: "r2, #0x10", 0xAF5054: "#0xe13d8",
        0xAF508E: "r2, #0x10",
        0xAF5090: "r1, r8", 0xAF5092: "#0xe0964",
        0xAF5098: "r1, r6", 0xAF509A: "#0xaf4d5c",
        0xAF509E: "r0, r5", 0xAF50A0: "r1, [r7, #0xc]",
        0xAF50A2: "#0xe2a28",
    }
    delta = entry - 0xAF503C
    assert {a: elf.instruction(a + delta).op_str for a in expected} == expected
    assert elf.read(0xAF4D60, 4).hex() == "40f8041c"  # reply-to at payload-4.


def test_rpc_copies_twelve_bytes_and_receives_on_reply_queue(avcam):
    # Este cliente NO llama al helper de 8 bytes 43b04cd4 de S20.
    expected = {
        0x4372A3EE: "r2, [pc, #0x24]", 0x4372A3FA: "#0x43ae12c4",
        0x43AE12D0: "r7, r2", 0x43AE12E4: "r0, r7",
        0x43AE12E8: "r2, #0xc", 0x43AE12EC: "#0x435612d0",
        0x43AE12FC: "r6, {r0, r1, r2}",
        0x43AE1302: "r3, {r0, r1, r2}",
        0x43AE1306: "r0, r7", 0x43AE130A: "#0x4356120c",
        0x43AE1312: "r0, [sp, #0xc]", 0x43AE131A: "#0x43561260",
    }
    assert {a: av_instruction(avcam, a).op_str for a in expected} == expected
    assert av_word(avcam, 0x4372A414) == 0x40193


def test_destination_field_does_not_identify_callback_queue():
    elf = Elf32(LIBRARIES["A6000"])
    expected = {
        0xA1B19C: "r1, [r0, #4]", 0xA1B1A4: "r1, [r0, #8]",
        0xADAF7A: "r1, #0x20002", 0xADAF7E: "#0xa1b1a0",
        0xADAF84: "r1, [pc, #0xfc]", 0xADAF86: "#0xa1b198",
        0xA1B238: "r0, [r0, #4]", 0xA1B292: "r0, [r4, #4]",
        0xA1B294: "#0xe2a28", 0xA1B31A: "r6, r1",
        0xA1B32E: "r0, r6", 0xA1B334: "#0xdd068",
        0xA1B342: "r6, [r4, #8]", 0xA1B120: "r6, [r5, #0xc]",
        0xA1B126: "r6", 0xA1B12A: "r0, [r5, #8]",
        0xA1B12C: "#0xe20dc",
    }
    assert {a: elf.instruction(a).op_str for a in expected} == expected
    assert elf.u32(0xADB084) == 0x40193
    got = (elf.u32(0xA1B350) + 0xA1B322) & 0xFFFFFFFF
    assert got == 0x102CBD0
    assert got + elf.u32(0xA1B354) == 0x103267C
    assert elf.u32(0x103267C) == 0xA1B109  # Generic callback, Thumb bit.
    reloc = elf.sections[".rel.dyn"]
    assert any(elf.u32(reloc[3] + off) == 0x103267C
               and elf.u32(reloc[3] + off + 4) == 23  # R_ARM_RELATIVE.
               for off in range(0, reloc[5], 8))


def test_receiver_consumes_message_id_not_queue_id_and_dispatches_table(avcam):
    expected = {
        0x4381D176: "#0x43561260", 0x4381D182: "r5, [r1, #3]",
        0x4381D184: "r3, [r1, #2]", 0x4381D186: "r2, [r1, #-0x4]",
        0x4381D18A: "r5, r3, r5, lsl #8", 0x4381D198: "r0, #0xc",
        0x4381D1C2: "r3", 0x4381D1CA: "r4, #0x23",
        0x4381D1D2: "#0x435612ec",
    }
    assert {a: av_instruction(avcam, a).op_str for a in expected} == expected
    assert av_word(avcam, 0x4381D1D8) == 0x40193
    assert (av_word(avcam, 0x4381D1DC) + 0x4381D194) & 0xFFFFFFFF == 0x44000174
    rows = [struct.unpack_from("<3I", avcam, 0x44000174 - AV_BASE + 12 * k)
            for k in range(35)]
    assert rows[0] == (0x4044, 0x43AEAA4B, 0)
    assert rows[18] == (0xD008, 0x43AEA99B, 0)
    assert all(adjustment == 0 and function & 1 for _, function, adjustment in rows)


def test_initializer_copies_worker_pointer_into_descriptor(avcam):
    # GOT y bases PC reales: no confundir 0x46 (índice de tarea) con 0x40193.
    got = (av_word(avcam, 0x4379E988) + 0x4379E950) & 0xFFFFFFFF
    assert got == 0x4401EEE4
    assert av_word(avcam, got + av_word(avcam, 0x4379E990)) == 0x4381D16D
    descriptor = (av_word(avcam, 0x4379E994) + 0x4379E968) & 0xFFFFFFFF
    assert descriptor == 0x43EA048C
    expected = {
        0x4379E958: "r1, [r4, r3]", 0x4379E95A: "#0x43acac1a",
        0x43ACAC1E: "#0x436ba1e4", 0x436BA1EA: "r6, r1",
        0x436BA1F6: "r6, [r5, #8]", 0x4379E962: "r1, #0x46",
        0x4379E966: "#0x43acac02", 0x43ACAC0A: "r6!, {r0, r1, r2, r3}",
        0x43ACAC0E: "r7!, {r0, r1, r2, r3}", 0x43ACAC16: "r2, [r7]",
        0x43ACABEE: "r3, [r0, #8]", 0x43ACABF0: "r3",
    }
    assert {a: av_instruction(avcam, a).op_str for a in expected} == expected


def test_descriptor_is_passed_to_indirect_service_dispatch(avcam):
    # Una segunda función consume el descriptor ya instalado, sin probar que
    # el servicio invoque después el callback ni que Linux registre 0x40193.
    load, add = 0x4379E912, 0x4379E914
    assert av_instruction(avcam, load).op_str == "r0, [pc, #0x20]"
    assert av_instruction(avcam, add).op_str == "r0, pc"
    pool = ((load + 4) & ~3) + 0x20
    assert (av_word(avcam, pool) + add + 4) & 0xFFFFFFFF == 0x43EA048C
    expected = {
        0x437880CA: "#0x4379e8f4",
        0x4379E916: "#0x43b2a162",
        0x43B2A162: "r1, r0",
        0x43B2A164: "r0, [r0, #0x14]",
        0x43B2A168: "#0x43560bb0",
        0x43560BB8: "r3, [r3, r2]",
        0x43560BBA: "r3, [r3, #0x14]",
        0x43560BBC: "r3, [r3, #0x3c]",
        0x43560BBE: "r3",
    }
    assert {address: av_instruction(avcam, address).op_str
            for address in expected} == expected
