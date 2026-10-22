#!/usr/bin/env python3
"""S153: reproduce the byte reads and conditional gates for gap diagnostics."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("dump_gates.json")
RANGES = ((0x438583B0, 8), (0x438584F0, 8), (0x43F72D02, 8))


def main():
    blob = BIN.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    items = []
    for address, size in RANGES:
        offset = address - BASE
        raw = blob[offset:offset + size]
        if len(raw) != size:
            raise ValueError(f"short read at {address:#x}")
        items.append({
            "address": f"0x{address:08x}",
            "file_offset": f"0x{offset:x}",
            "bytes_hex": raw.hex(),
            "thumb_instructions": [
                {"address": f"0x{i.address:08x}", "text": f"{i.mnemonic} {i.op_str}".strip()}
                for i in md.disasm(raw, address)
            ],
        })
    result = {
        "milestone": "S153",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "gate_bytes": {
            "offset_3_mask_0x02": items[0],
            "offset_6_mask_0x20": items[1],
            "state_object_initial_image": items[2],
        },
        "rea_xrefs": {
            "state_base_0x43f72d02": {
                "evidence_id": "ev_6da432586526f5e685ab773333ad5329a099d92f9018cb8078383eff72d6a2c1",
                "addresses": [
                    "0x438363e6", "0x4383ac90", "0x4384cb06", "0x4384cb0a",
                    "0x43857f90", "0x43857fb0", "0x43858134", "0x43859954",
                    "0x4385b268", "0x4386001c", "0x43860112", "0x43860506",
                    "0x438d933e", "0x438d9378", "0x43ff3248",
                ],
            },
            "flag_3": {
                "evidence_id": "ev_2988fcffcf7768198b5e5d25f616294bfa4ee489710012b6f85b06434aabfde4",
                "read_sites": [
                    "0x43858396", "0x438583b0", "0x438583ca", "0x438583ec",
                    "0x43858406", "0x43858420", "0x4385843a", "0x43858454",
                ],
            },
            "flag_6": {
                "evidence_id": "ev_7a31d71d07dc687daced9c48fe2a917ae8a24bf330dd09d4cb5d966c77a1669a",
                "read_sites": [
                    "0x4385846e", "0x43858488", "0x438584a2", "0x438584bc",
                    "0x438584d6", "0x438584f0", "0x4385850a", "0x43858524",
                ],
            },
        },
        "scope_limit": "Direct flag xrefs are readers in a diagnostic dumper. No writer is proven by this bounded evidence; zero initial bytes and empty writer candidates do not establish runtime state or global absence.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(items)} byte regions")


if __name__ == "__main__":
    main()
