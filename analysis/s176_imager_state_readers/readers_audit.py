"""Reproduce S176 desde bytes originales; no ejecuta ni modifica el firmware."""

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BINARY = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000


def audit(data: bytes) -> dict[str, Any]:
    """Resuelve ambos accesos PIC y verifica cada rama antes de interpretar ceros."""
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    decoder.detail = True

    def instruction(address: int):
        return next(decoder.disasm(data[address - BASE:address - BASE + 4], address, count=1))

    def word(address: int) -> int:
        return struct.unpack_from("<I", data, address - BASE)[0]

    def literal(address: int) -> int:
        ins = instruction(address)
        assert ins.mnemonic == "ldr" and ins.reg_name(ins.operands[1].mem.base) == "pc"
        return word(((address + 4) & ~3) + ins.operands[1].mem.disp)

    got = (literal(0x43861400) + 0x43861406 + 4) & 0xFFFFFFFF
    other_got = (literal(0x438690EA) + 0x438690F0 + 4) & 0xFFFFFFFF
    assert got == other_got == 0x4401EEE4
    assert instruction(0x43861406).op_str == "r2, pc"
    assert instruction(0x438690F0).op_str == "r5, pc"
    slot = got + literal(0x43861404)
    assert slot == got + literal(0x438693EA) == 0x4401F990
    assert word(slot) == 0x43F72D02
    assert instruction(0x4386140A).op_str == "r3, [r2, r3]"
    assert instruction(0x438693EC).op_str == "r3, [r5, r3]"
    assert instruction(0x43861410).mnemonic == "ldrb.w"
    assert instruction(0x43861410).op_str == "r2, [r3, #0xac]"
    assert instruction(0x43861414).op_str == "#0x438fec38"
    for address, text in {
        0x438FEC44: "r8, r2", 0x438FEC6C: "r8, #0", 0x438FEC70: "ne",
        0x438FEC72: "r2, r8", 0x438FEC74: "r2, #6", 0x438FEC7C: "r2, [r3]",
    }.items():
        assert instruction(address).op_str == text
    default_destination = (literal(0x438FEC68) + 0x438FEC76 + 4) & 0xFFFFFFFF

    rows = []
    destinations = [0x664, 0x66C, 0x674, 0x67C, 0x684, 0x68C, 0x690, 0x694]
    for index, destination in enumerate(destinations):
        address = 0x438693EE + index * 10
        load, branch, store = (instruction(address + delta) for delta in (0, 4, 6))
        reg = "r3" if index == 7 else "r2"
        assert load.mnemonic == "ldrb.w"
        assert load.op_str == f"{reg}, [r3, #{0x30 + index:#x}]"
        assert branch.mnemonic == "cbnz" and branch.op_str == f"{reg}, #{address + 10:#x}"
        assert store.mnemonic == "str.w"
        assert store.op_str == f"{reg}, [r6, #{destination:#x}]"
        rows.append({
            "load": hex(address), "branch": hex(address + 4), "store": hex(address + 6),
            "state_offset": hex(0x30 + index), "destination_offset": hex(destination),
            "value": 0, "condition": "state_byte == 0",
        })
    return {
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "method": "PIC pools + decoded Thumb loads/branches/stores; static only",
        "got_base": hex(got), "got_slot": hex(slot), "state": hex(word(slot)),
        "single_read": {"site": "0x43861410", "offset": "0xac"},
        "first_reader_default": {
            "input_offset": "0xac", "zero_replacement": 6, "instruction": "0x438fec74",
            "destination": hex(default_destination),
            "condition": "first-reader initialization path and state[0xac] == 0",
        },
        "zero_overrides": rows, "physical_semantics": "NO_VERIFICADO",
    }


if __name__ == "__main__":
    print(json.dumps(audit(BINARY.read_bytes()), indent=2))
