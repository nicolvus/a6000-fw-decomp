#!/usr/bin/env python3
"""S157: verify the state-pointer xref and field reads in FUN_43859944."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("snapshot_ref.json")
RANGES = ((0x43859944, 0x8A),)
SLOTS = (0x4401F990,)


def main():
    blob = BIN.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    regions = []
    for address, size in RANGES:
        offset = address - BASE
        raw = blob[offset:offset + size]
        if len(raw) != size:
            raise ValueError(f"short read at {address:#x}")
        regions.append({
            "address": f"0x{address:08x}",
            "length": size,
            "file_offset": f"0x{offset:x}",
            "bytes_hex": raw.hex(),
            "instructions": [
                {"address": f"0x{i.address:08x}", "text": f"{i.mnemonic} {i.op_str}".strip()}
                for i in md.disasm(raw, address)
            ],
        })
    slots = []
    for address in SLOTS:
        offset = address - BASE
        raw = blob[offset:offset + 4]
        slots.append({"address": f"0x{address:08x}", "bytes_hex": raw.hex(),
                      "value_le": f"0x{int.from_bytes(raw, 'little'):08x}"})
    result = {
        "milestone": "S157",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "got_slots": slots,
        "procedures": regions,
        "rea_evidence_ids": {
            "procedure": "ev_ec6f97762141815f395c4f95495973ab27f5327ae5c1aab1c33e5f7593780ece",
            "instruction_xref": "ev_a1843181423095ac768e124db07db27e4259ffb8776b681caea4238fdb06414e",
            "typed_references": "ev_34d9295f6218a4ff16b071ff3c48aabd51ee2f8280c09aeb46d5ca2e438bfc4d",
            "field_plus_5": "ev_7881d9e7228dfb57cfc851cb6d4882c6825f2ef1e8a9b2f54a0fcc10d8e5b7cf",
            "field_plus_0x0f": "ev_26139718bebfe0c0ce0c3fb0e15c67f4f50a01ee534688889d39b746b96c0ca7",
        },
        "scope_limit": "Only FUN_43859944 is classified; the DATA/PARAM edge is a loaded pointer, not a memory write to the state object.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} procedure ranges")


if __name__ == "__main__":
    main()
