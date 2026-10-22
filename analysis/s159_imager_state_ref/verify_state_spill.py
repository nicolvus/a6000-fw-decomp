#!/usr/bin/env python3
"""S159: byte-level check that xref 0x4386001c is a state-pointer stack spill."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("state_spill.json")
RANGES = (
    (0x43860008, 0x20),
    (0x43860110, 0x0c),
    (0x43860148, 0x18),
    (0x43860410, 0x20),
)
SLOT = 0x4401F990


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
    slot = read(SLOT, 4)
    result = {
        "milestone": "S159",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "state_got_slot": {
            "address": f"0x{SLOT:08x}",
            "bytes_hex": slot.hex(),
            "value_le": f"0x{int.from_bytes(slot, 'little'):08x}",
        },
        "regions": regions,
        "rea_evidence_ids": {
            "procedure": "ev_5b0f148005650c3e22de895825765d726859466967149bcff370c3d43ddd1f73",
            "xref_instruction": "ev_3c2f0fbe550810719bf22e531025709d7c0ca323e91ab8635e60f9afca166181",
            "typed_references": "ev_eb099b43bb1c2559ab27672e7a60d390533927b72af8b8a486614aaee8090843",
            "full_instructions": "ev_6dc087d973990a3aeaf9d67b413d3bff80620de2a4a88e4b9cb9350c82ab0bbb",
            "caller": "ev_834e1efc6cdb2d2fc89e38963b8bea30d8c8fc2958eb176451469ce09f63fa3f",
        },
        "scope_limit": "This function xref is a stack spill; body-level no-write conclusion is local and does not exclude other writers/aliases.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} Thumb ranges")


if __name__ == "__main__":
    main()
