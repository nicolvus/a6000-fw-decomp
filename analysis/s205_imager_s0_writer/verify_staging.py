"""Verificación por instrucciones del origen de S y de su selector de fila."""

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BINARY = Path(__file__).resolve().parents[1] / "rea-independent/input/av-cam.bin"


def audit(data: bytes) -> dict[str, Any]:
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    decoder.detail = True

    def word(address: int) -> int:
        return struct.unpack_from("<I", data, address - BASE)[0]

    def ins(address: int):
        return next(decoder.disasm(data[address - BASE:address - BASE + 4], address, count=1))

    def literal(address: int) -> int:
        instruction = ins(address)
        assert instruction.mnemonic == "ldr" and "[pc," in instruction.op_str
        return word(((address + 4) & ~3) + instruction.operands[1].mem.disp)

    got = (literal(0x437B6184) + 0x437B618A + 4) & 0xFFFFFFFF
    slot = got + literal(0x437B61AC)
    assert got == 0x4401EEE4 and slot == 0x44020C9C
    assert word(slot) == 0x43EB35D0
    assert word(got + literal(0x437B61BE)) == 0x43EB05D8
    expected = {
        0x437B617C: ("ldr", "r3, [r0, #0x20]"),
        0x437B6182: ("mov", "r5, r0"), 0x437B618A: ("add", "r4, pc"),
        0x437B61AE: ("mov", "r0, r5"), 0x437B61B0: ("ldr", "r7, [r4, r3]"),
        0x437B61B4: ("str", "r7, [sp]"),
        0x437B61C4: ("ldr", "r2, [r4, r3]"),
        0x437B61C8: ("add.w", "r2, r2, #0x224"),
        0x437B61D2: ("bl", "#0x43843a44"),
        0x43843A44: ("push.w", "{r4, r5, r6, r7, r8, sb, sl, fp, lr}"),
        0x43843A4A: ("ldr", "r3, [r0, #0x20]"),
        0x43843A4C: ("sub", "sp, #0x1c"),
        0x43843A54: ("ldrb", "r3, [r3, #1]"),
        0x43843A5A: ("ldr", "r4, [sp, #0x40]"),
        0x43843A5E: ("strb", "r3, [r4]"),
        0x43843AD8: ("cmp", "r3, #3"), 0x43843ADA: ("bne", "#0x43843b3c"),
        0x43843AEE: ("movs", "r2, #4"),
        0x43843AF2: ("add.w", "r3, r7, #0x2c"),
        0x43843AF6: ("add.w", "lr, r8, #0x64"),
        0x43843AFA: ("adds", "r7, #0x10"),
        0x43843AFC: ("add.w", "r8, r8, #0x10"),
        0x43843B00: ("ldm", "r3, {r0, r1, r2, r3}"),
        0x43843B02: ("stm.w", "lr, {r0, r1, r2, r3}"),
        0x43843B28: ("subs", "r3, r1, #1"),
        0x43843B34: ("bne", "#0x43843af2"),
    }
    for address, pair in expected.items():
        instruction = ins(address)
        assert (instruction.mnemonic, instruction.op_str) == pair
    return {
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "caller": "0x437b617c", "staging": "0x43843a44",
        "state": hex(word(slot)), "state_slot": hex(slot),
        "selector_store": "0x43843a5e", "source": "u8(*(ctx + 0x20) + 1)",
        "rows": {"source": "0x43eb07fc", "count": 4, "size": 16,
                 "source_offset": "0x2c", "destination_offset": "0x64",
                 "condition": "selector == 3"},
        "electronic_end_of_integration": "NO_VERIFICADO",
    }


if __name__ == "__main__":
    print(json.dumps(audit(BINARY.read_bytes()), indent=2))
