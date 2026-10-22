#!/usr/bin/env python3
"""S147: verify byte ranges for the REA-observed G-row producer/consumer."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("g_rows.json")
RANGES = (
    (0x437B57EC, 4),
    (0x437B5F00, 0x20),
    (0x437B60E6, 4),
    (0x4383BF2C, 0x20),
    (0x4383C9DC, 0x60),
    (0x43836A00, 0x34),
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
        "milestone": "S147",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "row_layout_observed": {
            "first_row_offset_from_G_plus_0x224": "0x2c",
            "row_count": 4,
            "row_stride": "0x10",
            "writer_function": "0x4383c9dc",
            "relative_store_offsets_in_writer": ["0x0", "0x4", "0x6", "0xa", "0xc", "0xe"],
            "not_written_by_this_loop": ["0x8", "0x9"],
            "meaning": "unassigned; no physical sensor semantics inferred",
        },
        "rea_evidence_ids": {
            "G_xrefs": "ev_7375812f6a63afe1d0db14b91c6cec50187e7d53a2f6bd7a4436500fb2ec9df0",
            "builder_4383bf2c": "ev_5305a4dbabf37e02baec4bd8b258137d9e733c0817ce4b373defe5a8ecc12203",
            "row_writer_4383c9dc": "ev_cd6567d4fb0af5c12b4d8d21ee30a574ca5bd289cfba828745757f185d89ecb2",
            "row_writer_page_1": "ev_d4653d3615add43984db5b04eb31c812b23d2a5865e6038908736caf291fd05a",
            "row_writer_page_2": "ev_9caa8366dd8aa3149c26482110e5523aa6132b3fd299d39fb05de95a2003380e",
            "row_reader_context_43836a": "ev_afc6e27db62a908c1a0a4efc787ccfa5608e0adaff61d037fea073abdebaa48c",
        },
        "coverage_limit": "Only the direct xrefs and listed routines are characterized. The mode meanings, unlisted aliases, and physical sensor semantics remain unknown.",
        "regions": regions,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} Thumb ranges")


if __name__ == "__main__":
    main()
