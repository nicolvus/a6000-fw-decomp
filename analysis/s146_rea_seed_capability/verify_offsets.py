#!/usr/bin/env python3
"""S146: independently verify the file-offset coordinates used in REA tests."""
import hashlib
import json
import struct
from pathlib import Path

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("rea_seed_capability.json")
ADDRESSES = (0x437B617E, 0x43843A44, 0x437B717E)


def main():
    blob = BIN.read_bytes()
    mappings = []
    for address in ADDRESSES:
        offset = address - BASE
        if offset < 0 or offset >= len(blob):
            raise ValueError(f"address outside image: {address:#x}")
        mappings.append({
            "address": f"0x{address:08x}",
            "file_offset": f"0x{offset:x}",
            "first_4_bytes_hex": blob[offset:offset + 4].hex(),
        })
    result = {
        "milestone": "S146",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "address_mappings": mappings,
        "rea_tool_result": {
            "procedure_pseudo_code_selector": "file-offset:<offset> resolves file mapping then requires an already observed containing/starting procedure; it does not create or seed one.",
            "procedures_rejected_selector": ["procedure_info", "procedure_assembly", "analyze_function"],
            "candidate_offsets": {
                "0x43843a44": "0x302a44",
                "0x437b617e": "0x27517e",
                "mistyped_offset_0x27617e_maps_to": "0x437b717e (unrelated analyzed procedure extent)",
            },
            "coverage_error": "File offset 0x302a44 maps to analysis address 0x43843a44, but no procedure starts at or contains that address in the current Ghidra analysis.",
        },
        "evidence_ids": [
            "ev_adf4d88907eb3ff81fba796af3f1ddac9680ffe4aded30e67aa18febd79e3417",
            "ev_26bca5083b40a7c16bcf21eec1635a774c20532c95739f7acd57aa3649d06ad7",
            "ev_ea22a2182a4e3d23312394b402b358789ae6a158f2c91f4dd012453fd50de7ed",
            "ev_b0d6874334a9baa4823bb7b150b77290a5434ef146c37fcd58858065b1babd63",
            "ev_b0f83d8206f65a014ebfad1dd74c5428aa1aa66ff8fe6cb7067cfa007f94e20b",
        ],
        "conclusion": "REA current tool surface cannot seed these unrecognized entries; this is an analysis coverage limit, not evidence of absent code or non-execution.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(mappings)} virtual/file mappings")


if __name__ == "__main__":
    main()
