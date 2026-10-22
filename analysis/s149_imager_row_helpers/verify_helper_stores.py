#!/usr/bin/env python3
"""S149: byte-level verification of the four-row loop and adjacent helper stores."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("row_helper_stores.json")
RANGES = (
    (0x4383C9EC, 0x24),
    (0x4383CBFA, 0x14),
    (0x4383CBBE, 8),
    (0x4383BA4C, 0x26),
    (0x4383C88C, 0x48),
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
            "length": size,
            "file_offset": f"0x{offset:x}",
            "bytes_hex": raw.hex(),
            "thumb_instructions": [
                {"address": f"0x{i.address:08x}", "text": f"{i.mnemonic} {i.op_str}".strip()}
                for i in md.disasm(raw, address)
            ],
        })
    result = {
        "milestone": "S149",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "loop": {
            "count_initial": 4,
            "destination_stride": "0x10",
            "row_bases_relative_to_G_plus_0x224": ["0x2c", "0x3c", "0x4c", "0x5c"],
            "writer_relative_offsets": ["0", "4", "6", "0xa", "0xc", "0xe"],
            "unwritten_by_row_writer": ["0x8", "0x9"],
        },
        "rea_evidence_ids": {
            "writer_dossier": "ev_cd6567d4fb0af5c12b4d8d21ee30a574ca5bd289cfba828745757f185d89ecb2",
            "complete_function_instructions": "ev_05541f7fa796e9902a584d283765f42028aa618772a3ece2a2b2e519b172211b",
            "four_helper_dossiers": {
                "0x4383b790": "ev_f4e7ee8c49c2a05c87830ae4432cb9f89b76b505c258c1a4187a700113bf407c",
                "0x4383bfd4": "ev_2840e01dbc3ca082d7dfffe4aad87e8760f3f806f2c0d323a950d1f800ce6355",
                "0x43b08786": "ev_76117d450acd81c363f9fa8b4c4f5284f47263d347df63e76c6e2dec1348c88e",
                "0x4383c818": "ev_c681e6e23a4263909564de62cee2a44c081686f7a2f295bec17542c813f643c3",
            },
            "selected_helper_evidence": {
                "0x43b0d16e": "ev_754e831f6b38c1ac43d38480668cd9f8e06ea03645226d749cb771bfcd7deb23",
            },
        },
        "scope_limit": "Static stores in these exact callees and gates only; other writers and caller behavior are not excluded.",
        "regions": regions,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} byte ranges")


if __name__ == "__main__":
    main()
