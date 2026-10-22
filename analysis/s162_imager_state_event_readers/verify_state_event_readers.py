#!/usr/bin/env python3
"""S162: verify two state-derived event readers and their distinct destinations."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("event_readers.json")
RANGES = (
    (0x438D932A, 0x18),
    (0x438D9376, 0x1A),
    (0x438D9340, 2),
    (0x438D937A, 2),
    (0x43F72D1E, 2),
)
SLOTS = (0x4401F990, 0x4401F7B0, 0x440220A0)


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
        "milestone": "S162",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "state_pointer_slot": slots[0],
        "other_destination_slots": slots[1:],
        "rea_evidence_ids": {
            "xref_base": "ev_4db80d5468d11118561f766f8d8699b7d85f44889d368fd8c5eacd01aae0454d",
            "first_reader": "ev_02d7e5d7893000bd111b30f25f386665394b5759bfb5ae161c19b78576267719",
            "second_reader": "ev_59bc79c25846b1f1541a2e92f6dc4702c4546864117f903afa9c76c5a9ee6dfd",
            "first_state_field_load": "ev_6a42bc996de46b8fcf43744545e137c4fdb396d441dcaff4fc2927f5d04ba023",
            "second_state_field_load": "ev_99cc8a35a1ce639df757c861113ec77dbfaccfdcee754a4f307ee10210a02d83",
            "write_first_other_object": "ev_b854d8070081b91afd67f83ed553f32981e05ad26dd437820c559fa0a609b9ca",
            "write_second_other_object": "ev_142578032f626c121d666087158687149c10c3b7c262d075f72e2423cd0cf7bc",
        },
        "conclusion_scope": "Two reader functions only; a separate reader at 0x438d93aa and global writer/runtime reachability are outside this result.",
        "regions": regions,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} instruction/data windows")


if __name__ == "__main__":
    main()
