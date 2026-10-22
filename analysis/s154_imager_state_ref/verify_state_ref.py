#!/usr/bin/env python3
"""S154: reproduce the candidate state-reference instruction and field reads."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("state_ref.json")
RANGES = ((0x438363CC, 0xC0), (0x43836490, 0x64))
SLOT = 0x4401F990


def main():
    blob = BIN.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    regions = []
    for address, size in RANGES:
        offset = address - BASE
        raw = blob[offset:offset + size]
        if len(raw) != size:
            raise ValueError(f"short read at {address:#x}")
        ins = list(md.disasm(raw, address))
        regions.append({
            "address": f"0x{address:08x}",
            "length": size,
            "file_offset": f"0x{offset:x}",
            "bytes_hex": raw.hex(),
            "instructions": [
                {"address": f"0x{i.address:08x}", "text": f"{i.mnemonic} {i.op_str}".strip()}
                for i in ins
            ],
        })
    slot = blob[SLOT - BASE:SLOT - BASE + 4]
    result = {
        "milestone": "S154",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "slot": {
            "address": f"0x{SLOT:08x}",
            "file_offset": f"0x{SLOT - BASE:x}",
            "bytes_hex": slot.hex(),
            "value_le": f"0x{int.from_bytes(slot, 'little'):08x}",
        },
        "procedure_ranges": regions,
        "rea_evidence_ids": {
            "procedure_instructions": "ev_98aa775d3c95df94438bb40d89c729bddd5b0493c30968d146bfee6243fb3c63",
            "typed_outgoing_references": "ev_e8a264c61f10ca8c40c32e8171a4b743ec4bfa571f23898386dd5ab4a8ec7efa",
            "state_byte_reads": {
                "object_plus_0x3a": "ev_cb1224e3e94ea1cd0f793b0da5a902997b57288cb68465451b407ea40079a234",
                "object_plus_0x39": "ev_7dcaca9f5ba1f6d3e2b1e2e6b47d5d206f7b52d186be1c5460b54a55286f6b23",
                "object_plus_0x38": "ev_517ca4e7ee3bcfebfaaaec5ac71bd393297b2cc541486b636d6e90b014c97f24",
            },
            "slot_bytes": "ev_ef0ae04fe4e640945736ea7bd40211f7cbdc4dbc7865e58ec0051c994f67bc7f",
        },
        "scope_limit": "Only FUN_438363cc is classified. Its base xref is a GOT pointer load, not a store to the gate bytes; no global writer conclusion.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(regions)} procedure ranges")


if __name__ == "__main__":
    main()
