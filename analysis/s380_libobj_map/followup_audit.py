"""Contrasta la API instalada por liro.ko y los 43 callees de RecordStill."""

import hashlib
import json
import struct
from typing import Any

from capstone import CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB, Cs
from elf_plt import resolve_plt
from recordimage_audit import LIBRARIES, ROOT, Elf32

LIRO = LIBRARIES["A6000"].parent.parent / "kmod/liro.ko"
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"


def section_bytes(elf: Elf32, name: str) -> bytes:
    section = elf.sections[name]
    return elf.data[section[4]:section[4] + section[5]]


def symbols(elf: Elf32, table: str, strings: str) -> list[tuple[str, int, int, int]]:
    names = section_bytes(elf, strings)
    rows = []
    for name, value, size, _, _, section in struct.iter_unpack("<IIIBBH", section_bytes(elf, table)):
        rows.append((names[name:].split(b"\0", 1)[0].decode(), value, size, section))
    return rows


def liro_api_map() -> dict[str, Any]:
    """El offset del servicio se mide desde la metadata, no desde la cabecera."""
    elf = Elf32(LIRO)
    sym = symbols(elf, ".symtab", ".strtab")
    api = {
        offset: sym[info >> 8][0]
        for offset, info in struct.iter_unpack("<II", section_bytes(elf, ".rel.init.data"))
        if info & 255 == 2  # R_ARM_ABS32, aplicado por el cargador de módulos.
    }
    init = section_bytes(elf, ".init.text")
    # LLVM: r0 = [blob+0x14] + 0x24; r1 = .init.data; r2 = 0x344.
    assert struct.unpack_from("<III", init, 0x42C) == (0xE59F1090, 0xE5960014, 0xE2800024)
    assert struct.unpack_from("<I", init, 0x438)[0] == 0xEBFFFFFE
    rels = dict(struct.iter_unpack("<II", section_bytes(elf, ".rel.init.text")))
    assert sym[rels[0x438] >> 8][0] == "memcpy"
    assert sym[rels[0x4C4] >> 8][3] == list(elf.sections).index(".init.data")
    assert rels[0x4C4] & 255 == 2
    assert struct.unpack_from("<I", init, 0x4C4)[0] == 0
    assert len(section_bytes(elf, ".init.data")) == 0x344
    assert api[0x3C - 0x24] == "sta_tsk"
    assert api[0x1D4 - 0x24] == "osal_snd_msg"
    assert api[0x298 - 0x24] == "Backup_read"
    assert api[0x2C8 - 0x24] == "Backup_reg_cb"
    image = AVCAM.read_bytes()
    assert struct.unpack_from("<I", image, 0x14)[0] == 0x435410B4
    return {
        "liro_sha256": hashlib.sha256(elf.data).hexdigest(),
        "copy_destination": "*(blob + 0x14) + 0x24", "api_entries": 0x344 // 4,
        "service_0x3c": api[0x3C - 0x24], "send_0x1d4": api[0x1D4 - 0x24],
        "backup_read_0x298": api[0x298 - 0x24],
        "backup_reg_cb_0x2c8": api[0x2C8 - 0x24],
        "task_id": "0x46", "task_argument": "0x43ea048c",
        "limits": "Static loader contract; no observed task activation or kernel addresses.",
    }


def backup_state_source(data: bytes) -> dict[str, Any]:
    """Vincula tablas, registro y copia; no inventa el tamaño persistido."""
    base = 0x43541000
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    decoder.detail = True

    def word(address: int) -> int:
        return struct.unpack_from("<I", data, address - base)[0]

    def ins(address: int):
        return next(decoder.disasm(data[address - base:address - base + 4], address, count=1))

    def literal(address: int) -> int:
        instruction = ins(address)
        assert instruction.mnemonic == "ldr" and "[pc," in instruction.op_str
        return word(((address + 4) & ~3) + instruction.operands[1].mem.disp)

    got = (literal(0x4378BFB0) + 0x4378BFBA + 4) & 0xFFFFFFFF
    assert got == 0x4401EEE4
    slot = got + literal(0x4378BFE2)
    assert slot == 0x4401F080 and word(slot) == 0x43FF3200
    state = word(word(slot) + 18 * 4)
    assert state == 0x43F72D02
    assert word(0x43FF2FAC + 18 * 4) == word(0x43FF345C + 18 * 4) == 0x3000B
    callback = word(got + literal(0x4378BFDC))
    assert callback == 0x43AE8B7B
    expected = {
        0x4378BFD8: ("add", "r1, sp, #4"),
        0x4378BFDA: ("str", "r3, [sp, #4]"),
        0x4378BFE0: ("str", "r3, [sp, #8]"),
        0x4378BFE4: ("ldr", "r3, [r4, r3]"),
        0x4378BFE6: ("ldr", "r3, [r5, r3]"),
        0x4378BFE8: ("adds", "r5, #4"),
        0x4378BFEA: ("str", "r3, [sp, #0xc]"),
        0x4378BFF6: ("bl", "#0x435614d0"),
        0x4378BFFA: ("cmp", "r7, #0x94"),
        0x4378C292: ("ldr", "r3, [r6, r3]"),
        0x4378C29A: ("ldr.w", "r1, [r3, r5, lsl #2]"),
        0x4378C2A4: ("bl", "#0x435613b0"),
        0x435613BC: ("ldr.w", "r3, [r3, #0x298]"),
        0x435614DC: ("ldr.w", "r3, [r3, #0x2c8]"),
        0x43AE8B7C: ("mov", "r4, r1"), 0x43AE8B80: ("mov", "r1, r2"),
        0x43AE8B82: ("mov", "r0, r3"), 0x43AE8B84: ("mov", "r2, r4"),
        0x43AE8B86: ("blx", "#0x439c5320"),
    }
    for address, pair in expected.items():
        instruction = ins(address)
        assert (instruction.mnemonic, instruction.op_str) == pair
    return {
        "source_sha256": hashlib.sha256(data).hexdigest(), "index": 18,
        "table": hex(word(slot)), "state": hex(state), "key_both_variants": "0x3000b",
        "callback": hex(callback & ~1), "callback_operation": "memcpy(arg4, arg3, arg2)",
        "registration_count": 148, "read_path": "0x4378c29a -> 0x435613b0 -> Backup_read",
        "effective_size_and_values": "NO_VERIFICADO",
    }


def plt_names(elf: Elf32) -> dict[int, str]:
    sym = symbols(elf, ".dynsym", ".dynstr")
    got = {
        offset: sym[info >> 8][0]
        for offset, info in struct.iter_unpack("<II", section_bytes(elf, ".rel.plt"))
    }
    section = elf.sections[".plt"]
    return resolve_plt(elf.data, section[3], section[4], section[5], got)


def uipc_route() -> dict[str, Any]:
    """Comprueba ioctl, relocaciones del dispatcher y el mismo índice de cola."""
    user = Elf32(LIBRARIES["A6000"].with_name("libosal_uipc.so"))
    kernel = Elf32(LIRO.with_name("osal_uipc.ko"))
    names = plt_names(user)
    assert names[0x15E0] == "u_osal_snd_msg" and names[0x1740] == "ioctl"
    for address, pair in {
        0x4220: ("tst.w", "r0, #0x8000"), 0x4232: ("bne", "#0x4242"),
        0x423E: ("b.w", "#0x15e0"), 0x2440: ("stm.w", "r7, {r0, r1}"),
        0x2446: ("movs", "r1, #4"), 0x244A: ("movt", "r1, #0x8000"),
        0x2450: ("blx", "#0x1740"),
    }.items():
        ins = user.instruction(address)
        assert (ins.mnemonic, ins.op_str) == pair
    sym = symbols(kernel, ".symtab", ".strtab")
    table = {
        address: sym[info >> 8][0]
        for address, info in struct.iter_unpack("<II", section_bytes(kernel, ".rel.rodata"))
        if info & 255 == 2
    }
    assert table[0x28] == "__k_4u_stat_sem"
    assert table[0x28 + 4 * 4] == "__k_4u_snd_msg"
    text_relocations = dict(struct.iter_unpack("<II", section_bytes(kernel, ".rel.text")))
    for address, name in {0x1B90: "osal_snd_msg", 0x1A6C: "osal_rcv_msg_tmo"}.items():
        assert text_relocations[address] & 255 == 28  # R_ARM_CALL.
        assert sym[text_relocations[address] >> 8][0] == name
    arm = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    text = section_bytes(kernel, ".text")
    for address, register in ((0x3BF4, "r8"), (0x3260, "r7")):
        ins = next(arm.disasm(text[address:address + 4], address, count=1))
        assert (ins.mnemonic, ins.op_str) == ("uxth", f"{register}, r0")
    return {
        "user_sha256": hashlib.sha256(user.data).hexdigest(),
        "kernel_sha256": hashlib.sha256(kernel.data).hexdigest(),
        "send_ioctl": "0x80000004", "kernel_dispatch_slot": 4,
        "kernel_helper": table[0x38], "queue_low16": hex(0x40193 & 0xFFFF),
        "liro_consumer": "blocking osal_rcv_msg_tmo",
        "specific_linux_callback_required": False,
        "limits": "Static path for the supplied factory libraries/modules; runtime load, "
                  "queue state and physical activation were not observed.",
    }


def compare_recordstill_callees() -> dict[str, Any]:
    """Import homology is exact; unresolved local bodies remain candidates."""
    a, b = (Elf32(LIBRARIES[model]) for model in ("A6000", "A7S"))
    plt_a, plt_b = plt_names(a), plt_names(b)
    bodies = [list(e.decoder.disasm(e.read(start, 0x2E8), start))
              for e, start in ((a, 0x908AFC), (b, 0x847E1C))]
    assert len(bodies[0]) == len(bodies[1]) == 260
    calls, local = [], {}
    for left, right in zip(*bodies, strict=True):
        assert left.address - 0x908AFC == right.address - 0x847E1C
        assert left.mnemonic == right.mnemonic
        if left.mnemonic not in {"bl", "blx"}:
            continue
        dest_a, dest_b = left.operands[0].imm, right.operands[0].imm
        name_a, name_b = plt_a.get(dest_a), plt_b.get(dest_b)
        if name_a or name_b:
            assert name_a == name_b
        else:
            local[(dest_a, dest_b)] = {
                "A6000": hex(dest_a), "A7S": hex(dest_b),
                "A6000_unwind": [hex(v) for v in a.unwind_span(dest_a)],
                "A7S_unwind": [hex(v) for v in b.unwind_span(dest_b)],
                "classification": "LOCAL_CANDIDATE",
            }
        calls.append({
            "A6000_site": hex(left.address), "A7S_site": hex(right.address),
            "A6000_target": hex(dest_a), "A7S_target": hex(dest_b),
            "A6000_symbol": name_a, "A7S_symbol": name_b,
            "classification": "SAME_IMPORT" if name_a else "LOCAL_CANDIDATE",
        })
    row = [a.u32(0x101EF0C + 22 * 24 + field * 4) for field in range(6)]
    assert row == [2, 0x10000005, 0x907BA1, 0x90D7E9, 0x907C95, 1]
    return {
        "source_sha256": {"A6000": hashlib.sha256(a.data).hexdigest(),
                          "A7S": hashlib.sha256(b.data).hexdigest()},
        "calls": calls, "local_pairs": list(local.values()),
        "capture_entry": {
            "state": row[0], "message": hex(row[1]), "check": hex(row[2] & ~1),
            "call": hex(row[3] & ~1), "next_state_function": hex(row[4] & ~1),
            "next_state": row[5],
        },
        "whole_function_equivalence": "NO_VERIFICADO",
        "physical_activation": "NO_VERIFICADO",
    }


if __name__ == "__main__":
    print(json.dumps({"liro_api": liro_api_map(), "recordstill": compare_recordstill_callees(),
                      "backup_state": backup_state_source(AVCAM.read_bytes()),
                      "uipc_route": uipc_route()}, indent=2))
