#!/usr/bin/env python3
"""S310: 0x43ad9704 is a C++ virtual-call thunk (vtable slot 0x64), not a message builder."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("thunk.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

WINDOW = (0x43AD96FA, 0x43AD9712, 0x43AD9720, 0x43AD972C, 0x43AD9744, 0x43AD9750)


def main():
    blob = A7.read_bytes()
    rows = []
    for a in WINDOW:
        raw = blob[a - BASE:a - BASE + 12]
        ins = [f"{i.mnemonic} {i.op_str}" for i in MD.disasm(raw, a)]
        slots = [i for i in ins if "[" in i and "#0x" in i]
        rows.append({"entry": f"0x{a:08x}", "bytes_hex": raw.hex(),
                     "insn": ins[:4],
                     "vtable_slot": slots[0].split("#")[1].rstrip("]") if slots else None})
    data = {
        "milestone": "S310",
        "title": "0x43ad9704 es un thunk de llamada virtual (vtable+0x64)",
        "firmware": {"name": "av-cam.bin (A7S fw3.20)",
                     "sha256": hashlib.sha256(blob).hexdigest()},
        "base": f"0x{BASE:08x}",
        "thunks": rows,
        "selector_result_path": {
            "stored": "0x43549098 str r0,[sp,#0x2c]",
            "passed_to": "0x435490c4 bl 0x43ad9704",
            "semantics": "llamada virtual obj->vtable[0x64](...)", 
        },
        "scope_limit": "La identidad del objeto/vtable no se resuelve aquí; el consumidor "
                       "del modo 0x4e/0x4f queda NO_VERIFICADO.",
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    for r in rows:
        print(r["entry"], "slot", r["vtable_slot"], r["insn"][:3])


if __name__ == "__main__":
    main()
