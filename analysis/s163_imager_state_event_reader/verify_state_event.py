#!/usr/bin/env python3
"""S163: verify the third reader of state+0x1c and its nearby read-only fields."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("state_event_reader.json")
RANGES = ((0x438D939C, 0xD0), (0x43F72D02, 0x20))
SLOTS = (0x4401F990,)


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
    slots = []
    for address in SLOTS:
        raw = read(address, 4)
        slots.append({"address": f"0x{address:08x}", "bytes_hex": raw.hex(),
                      "value_le": f"0x{int.from_bytes(raw, 'little'):08x}"})
    result = {
        "milestone": "S163",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "state_pointer_slots": slots,
        "regions": regions,
        "fields_read": ["state+0x1c (u16)", "state+0x1e (u8)"],
        "defaults_observed_in_decompilation": {"zero_at_plus_0x1c": 3, "zero_at_plus_0x1e": 4},
        "write_destinations_not_state": ["0x43f7c708", "0x43f7c70a", "0x43eff43c", "message_buffer"],
        "rea_evidence_ids": {
            "procedure": "ev_102b271ac6592a0bafc828c3d02e3a2d717b827f29445c7c46fc53a24e2942d9",
            "read_state_plus_1c": "ev_3d73989ad3bf9bf698d74295d05425993f61317c5abb3c491511a3a71c5f800e",
            "read_state_plus_1e": "ev_acf64d0ce0966ca85e468761ddb57b8dd267b30031d509fc210fabec25001053",
            "outgoing_references": "ev_0a887b1bd052d8b3d5b4d678910ef9808acc4c0ec7648dab3c13fc020e0fc190",
        },
        "scope_limit": "This message/event helper only; no runtime reachability or global writer conclusion.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} byte ranges")


if __name__ == "__main__":
    main()
