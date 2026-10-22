#!/usr/bin/env python3
"""S155: verify three reader/accessor xrefs to the diagnostic state object."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("state_readers.json")
RANGES = ((0x43857F88, 0x18), (0x43857FA8, 0x12), (0x4385812C, 0x50))
SLOTS = (0x4401F990, 0x44022FCC, 0x440220A0)


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
    slots = [{
        "address": f"0x{address:08x}",
        "bytes_hex": read(address, 4).hex(),
        "value_le": f"0x{int.from_bytes(read(address, 4), 'little'):08x}",
    } for address in SLOTS]
    result = {
        "milestone": "S155",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "slot_values": slots,
        "procedure_ranges": regions,
        "rea_evidence_ids": {
            "state_byte_zero_image": "ev_9e94446227412bad60faa35ecd2d1a97dcf54563b75970c9958846857001ca3b",
            "function_43857f88": "ev_50ec9a795fdeee1871d4df7045a9bc37b0e30b6187a21faef21c2d7d3fd3734a",
            "function_43857fa8": "ev_671901b96f062bf27c18b5a5db2b60b04f8131fde5cb02090e128ff818624502",
            "function_4385812c": "ev_b38e559657d05b6ab4a57389988c5f11f0adae407c47ecaa4e30cd3bfccd740c",
            "references_43857f88": "ev_9975507315e3e9ae8b0b12ed371553fbde517212c7deab61373a08b5fdd07e0c",
            "references_43857fa8": "ev_8af01bde84b54dc562aa3f33aacbc80ffbc8e7e2ca7f89e26e51b8143ca3dd92",
            "references_4385812c": "ev_8e30d1b8e05356a533217a31f3da3ec92df520c6aa1e9eb79cca3dbd31c18132",
        },
        "scope_limit": "These three procedures only; no global writer conclusion or runtime state claim.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} reader procedures")


if __name__ == "__main__":
    main()
