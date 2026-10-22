#!/usr/bin/env python3
"""S145: verify the Thumb bytes in the REA procedure-coverage gap."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("code_gap.json")
RANGES = (
    (0x437B617E, 0x58),  # candidate entry through BL at +0x54
    (0x43843A38, 0x10),  # observed 8-byte setter, literal, candidate prologue
    (0x43843A44, 0x20),  # candidate staging body bytes
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
        "milestone": "S145",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "regions": regions,
        "rea_findings": {
            "observed_setter": "FUN_43843a38 has body 0x43843a38-0x43843a3f; 0x43843a44 is not in an analyzed procedure.",
            "candidate_caller": "Bytes at 0x437b617e contain a prologue and a direct BL at 0x437b61d2 to 0x43843a44; that callsite is not in an analyzed procedure.",
            "coverage_warning": "Procedure-boundary gaps and xref emptiness do not prove code absence or runtime execution.",
        },
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} byte-verified regions")


if __name__ == "__main__":
    main()
