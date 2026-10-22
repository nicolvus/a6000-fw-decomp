#!/usr/bin/env python3
"""S161: verify the pointer load and stack spill at 0x4384cb06/0a."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("state_spill.json")
RANGES = ((0x4384CB02, 0x10), (0x4384CFA0, 4))
SLOT = 0x4401F990


def main():
    blob = BIN.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

    def read(address, size):
        offset = address - BASE
        raw = blob[offset:offset + size]
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
        "milestone": "S161",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "state_got_slot": {
            "address": f"0x{SLOT:08x}",
            "bytes_hex": slot.hex(),
            "value_le": f"0x{int.from_bytes(slot, 'little'):08x}",
        },
        "regions": regions,
        "rea_evidence_ids": {
            "procedure": "ev_1e8e048eb0f0141cf4d85e3688d89fe80dba6b0653e5ad1a7171f615be7c3de4",
            "got_load_instruction": "ev_d4025f0b945b5cb7b78c5d9cc83524a9b740a27a939c671a69cd8d903f897061",
            "spill_instruction": "ev_92b61d8fa023614fa3a5d727782551016292e79dbeeec8e093567b03cf125a06",
            "body_references": "ev_3303b18d85c46c4e2f17bbd020bc6d05f0c6ea1dcb7fee814e779e672f12ab01",
        },
        "scope_limit": "The DATA/PARAM edge at the xref carries the state pointer; the actual instruction writes stack. This body-local result does not exclude other writers.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} byte ranges")


if __name__ == "__main__":
    main()
