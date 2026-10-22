#!/usr/bin/env python3
"""S142: byte-level check of known direct references to the imager S object."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("s_accesses.json")
RANGES = (
    (0x437B56B2, 12),
    (0x437B59CE, 2),
    (0x43B08748, 8),
    (0x4383C66E, 4),
    (0x4383C6AA, 4),
)


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
            "file_offset": f"0x{offset:x}",
            "bytes_hex": raw.hex(),
            "instructions": [
                {"address": f"0x{i.address:08x}", "text": f"{i.mnemonic} {i.op_str}".strip()}
                for i in md.disasm(raw, address)
            ],
        })
    result = {
        "milestone": "S142",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "direct_xref_semantics": [
            "0x437b56b4 loads S and the following code clears 0x148 bytes.",
            "0x437b59ce loads S, then its caller passes the u16 at S+0xda to 0x4383c638.",
        ],
        "regions": regions,
        "scope_limit": "Only the listed direct references and parameter flow are covered; aliases and pointer-parameter writers remain open.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} verified instruction ranges")


if __name__ == "__main__":
    main()
