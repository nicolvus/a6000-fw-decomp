#!/usr/bin/env python3
"""S312: every consumer of the A7S cluster +0xae/+0xde..+0xea belongs to A7S-only code."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A6 = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("consumers.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

# (sitio, función, campos) — de S301
SITES = [
    ("0x438477d4", 0x438477A0, ["+0xe0", "+0xe2"]),
    ("0x438478ee", 0x438477A0, ["+0xe4"]),
    ("0x43861a8a", 0x43861A58, ["+0xdf"]),
    ("0x4386271a", 0x438625A0, ["+0xdf"]),
    ("0x4386430e", 0x438642F0, ["+0xe6"]),
    ("0x43864730", 0x438645BC, ["+0xae", "+0xe6"]),
    ("0x43864e3e", 0x43864CB0, ["+0xde"]),
]


def callers(blob, target):
    out = []
    for a in range(0x43541000, 0x43D00000, 2):
        off = a - BASE
        if off + 4 > len(blob):
            break
        hw = blob[off] | (blob[off + 1] << 8)
        if (hw & 0xF800) != 0xF000:
            continue
        i = next(MD.disasm(blob[off:off + 4], a), None)
        if i and i.mnemonic in ("bl", "blx", "b", "b.w") and i.op_str == f"#0x{target:x}":
            out.append(f"0x{a:08x}")
    return out


def main():
    a6, a7 = A6.read_bytes(), A7.read_bytes()
    funcs = {}
    for site, f, fields in SITES:
        head = a7[f - BASE:f - BASE + 24]
        funcs.setdefault(f, {"function": f"0x{f:08x}", "head_hex": head.hex(),
                             "a6000_hits": a6.count(head),
                             "callers": callers(a7, f)})
    rows = [{"site": s, "function": f"0x{f:08x}", "fields": fields,
             "a6000_hits": funcs[f]["a6000_hits"]} for s, f, fields in SITES]
    data = {
        "milestone": "S312",
        "title": "todos los consumidores del cluster A7S +0xae/+0xde..+0xea son código A7S",
        "firmware": {"a6000": hashlib.sha256(a6).hexdigest(),
                     "a7s": hashlib.sha256(a7).hexdigest()},
        "base": f"0x{BASE:08x}",
        "site_rows": rows,
        "functions": list(funcs.values()),
        "scope_limit": "Presencia por 24 B de prólogo; no prueba ausencia de funcionalidad "
                       "equivalente reescrita.",
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print("funcs", len(funcs), "all absent:", all(v["a6000_hits"] == 0 for v in funcs.values()))


if __name__ == "__main__":
    main()
