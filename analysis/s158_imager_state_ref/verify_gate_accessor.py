#!/usr/bin/env python3
"""S158: verify the GOT-pointer spill and accessor reads in FUN_4385b234."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("state_accessor.json")
RANGES = (
    (0x4385B244, 0x20),
    (0x4385B25E, 0x10),
    (0x4385B27C, 0x36),
    (0x4385BA46, 0x20),
    (0x4385BEAE, 8),
)
GOT_SLOT = 0x4401F990


def main():
    blob = BIN.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

    def read(address, size):
        off = address - BASE
        raw = blob[off:off + size]
        if len(raw) != size:
            raise ValueError(f"short read at {address:#x}")
        return raw

    regions = []
    for address, size in RANGES:
        raw = read(address, size)
        regions.append({
            "address": f"0x{address:08x}",
            "length": size,
            "file_offset": f"0x{address - BASE:x}",
            "bytes_hex": raw.hex(),
            "instructions": [
                {"address": f"0x{i.address:08x}", "text": f"{i.mnemonic} {i.op_str}".strip()}
                for i in md.disasm(raw, address)
            ],
        })
    slot = read(GOT_SLOT, 4)
    result = {
        "milestone": "S158",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "got_slot": {
            "address": f"0x{GOT_SLOT:08x}",
            "bytes_hex": slot.hex(),
            "value_le": f"0x{int.from_bytes(slot, 'little'):08x}",
        },
        "procedure_ranges": regions,
        "rea_evidence_ids": {
            "procedure": "ev_633b2499c1f64a98ef9dd1dee3a8785a4eb185e877a01886c8f80b10ecfb5551",
            "instruction_xref": "ev_a1843181423095ac768e124db07db27e4259ffb8776b681caea4238fdb06414e",
            "typed_references": "ev_34d9295f6218a4ff16b071ff3c48aabd51ee2f8280c09aeb46d5ca2e438bfc4d",
            "complete_function_instructions": "ev_6dc087d973990a3aeaf9d67b413d3bff80620de2a4a88e4b9cb9350c82ab0bbb",
        },
        "scope_limit": "Only FUN_4385b234; the xref is a stack spill of the pointer. No conclusion about other writers or runtime state.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} instruction windows")


if __name__ == "__main__":
    main()
