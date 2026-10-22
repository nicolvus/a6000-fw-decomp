#!/usr/bin/env python3
"""S141: independently disassemble the two REA-observed row-copy sites."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("row_trace.json")
RANGES = ((0x43B0893C, 0x16), (0x43849FB8, 0xA0))


def main():
    blob = BIN.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    regions = []
    for address, length in RANGES:
        off = address - BASE
        raw = blob[off:off + length]
        if len(raw) != length:
            raise ValueError(f"short read at {address:#x}")
        regions.append({
            "address": f"0x{address:08x}",
            "length": length,
            "file_offset": f"0x{off:x}",
            "bytes_hex": raw.hex(),
            "thumb_instructions": [
                {"address": f"0x{i.address:08x}", "text": f"{i.mnemonic} {i.op_str}".strip()}
                for i in md.disasm(raw, address)
            ],
        })
    result = {
        "milestone": "S141",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "regions": regions,
        "scope_limit": "Static instruction verification only; does not establish runtime stores to S[0] or row population conditions.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} instruction ranges")


if __name__ == "__main__":
    main()
