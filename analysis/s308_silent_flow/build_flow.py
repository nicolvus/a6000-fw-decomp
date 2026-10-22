#!/usr/bin/env python3
"""S308: where the A7S silent selector result goes, and why the timing writer has no entry."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("flow.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

CLAIMS = [
    ("selector_args_mode", 0x43549084),
    ("selector_args_sub", 0x43549088),
    ("selector_call", 0x4354908C),
    ("selector_result_saved", 0x43549098),
    ("selector_result_used", 0x435490C4),
    ("timing_prev_return", 0x4386458C),
    ("timing_entry", 0x438645BC),
]


def main():
    a7 = A7.read_bytes()

    def read(a, n=4):
        return a7[a - BASE:a - BASE + n]

    def dis(a):
        i = next(MD.disasm(read(a), a), None)
        return f"{i.mnemonic} {i.op_str}" if i else None

    # every 4-byte value in the blob that points into 0x43864xxx
    ptrs = []
    for i in range(len(a7) - 4):
        v = int.from_bytes(a7[i:i + 4], "little")
        if 0x43864000 <= v < 0x43865000:
            ptrs.append({"at": f"0x{BASE + i:08x}", "value": f"0x{v:08x}"})

    # direct callers of the timing entry
    callers = []
    for a in range(0x43541000, 0x43D00000, 2):
        off = a - BASE
        if off + 4 > len(a7):
            break
        hw = a7[off] | (a7[off + 1] << 8)
        if (hw & 0xF800) != 0xF000:
            continue
        i = next(MD.disasm(a7[off:off + 4], a), None)
        if i and i.mnemonic in ("bl", "blx", "b", "b.w") and i.op_str == "#0x438645bc":
            callers.append(f"0x{a:08x}")

    data = {
        "milestone": "S308",
        "title": "flujo del selector silent y entrada del escritor de tiempos",
        "firmware": {"name": "av-cam.bin (A7S fw3.20)",
                     "sha256": hashlib.sha256(a7).hexdigest()},
        "base": f"0x{BASE:08x}",
        "selector_site": [
            {"label": lab, "address": f"0x{a:08x}",
             "bytes_hex": read(a).hex(), "insn": dis(a)} for lab, a in CLAIMS
        ],
        "pointers_into_0x43864xxx": ptrs,
        "timing_entry_direct_callers": callers,
        "scope_limit": "Solo transferencias directas y punteros absolutos de 32 bits; "
                       "no cubre saltos calculados ni tablas relativas.",
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print(f"ptrs={len(ptrs)} callers={len(callers)}")


if __name__ == "__main__":
    main()
