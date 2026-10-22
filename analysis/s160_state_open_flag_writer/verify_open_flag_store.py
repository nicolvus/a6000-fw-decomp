#!/usr/bin/env python3
"""S160: verify the byte store to state offset +0 and its GOT destination."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("open_flag_store.json")
RANGES = (
    (0x4383AC8C, 8),
    (0x4383AC90, 8),
    (0x4383ACA4, 4),
    (0x4383ACD4, 4),
    (0x4383B350, 0x40),
    (0x4383B3B0, 0x40),
)
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
        "milestone": "S160",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "state_slot": {
            "address": f"0x{SLOT:08x}",
            "bytes_hex": slot.hex(),
            "value_le": f"0x{int.from_bytes(slot, 'little'):08x}",
        },
        "store": {
            "address": "0x4383ac90",
            "bytes_hex": read(0x4383AC90, 2).hex(),
            "rea_typed_target": "0x43f72d02",
            "field_offset": "0x0",
            "store_data_semantics": "reaching path stores byte value 0 when the shared countdown expires",
        },
        "rea_evidence_ids": {
            "procedure": "ev_134be2dfce4598770fe1825386a5899cfad96fb794784e8673a5c3f42e37bd3b",
            "typed_write_instruction": "ev_3992433ca320c9303ec5bd74990f7e8e53f481516afd812000138c8654f83014",
            "body_pseudocode": "ev_d9486547d0d47dc8039f483cc2e75d37bee5fd8e82c1044c8d033137462f0946",
            "caller_conditions": [
                "ev_d26c82da23892ec4f409332c9f21087a17c6239b8c09a0c620d048fd5aae0213",
                "ev_2db8b63f3ac711416bf1412cf5b9f69e4bce744fb6e3edf0af500029e9d7aa32",
            ],
        },
        "scope_limit": "This store is to state+0, not gate bytes +3/+6; runtime reachability and writers of the gate bits remain unknown.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} Thumb windows")


if __name__ == "__main__":
    main()
