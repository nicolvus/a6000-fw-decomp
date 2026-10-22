#!/usr/bin/env python3
"""S307: A7S-only state writes (+0xde, +0xe6/+0xe8/+0xea) sit in A7S-only code.

Signature = 24 bytes around each store (site-8 .. site+16), which contains the
distinctive field immediate. A zero count in the A6000 blob means that exact
store sequence is absent from the A6000 firmware.
"""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A6 = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("writers.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

WRITERS = [
    (0x43865100, "state+0xde", ["0x4386521a"], ["0x438648b0"]),
    (0x438642F0, "state+0xe6/+0xe8/+0xea",
     ["0x438643a6", "0x438643b2", "0x438643bc"], ["0x438647e6", "0x4386484e"]),
    (0x4385352C, "state+0x02", ["0x438536a0", "0x438536d0"],
     ["0x43854d1c", "0x43854f0c"]),
    (0x4385A290, "state+0x00", ["0x4385a334"], ["0x4385aa1c", "0x4385aaa6"]),
    (0x4385A384, "state+0x02", ["0x4385a67c"], ["0x437cb34a"]),
    (0x4385A98C, "state+0x02", ["0x4385a9c6"], ["0x43854e20", "0x4385514a"]),
]
RELAXED = [  # reading +0xae (x1000) and +0xe6 in the A7S timing path
    (0x438642F0, "lectura state+0xae/+0xe6", ["0x43864732"]),
]


def sig(blob, site, before=8, after=16):
    s = site - before
    return blob[s - BASE:s - BASE + before + after]


def _site(a7, a6, s):
    addr = int(s, 16)
    ins = next(MD.disasm(a7[addr - BASE:addr - BASE + 4], addr), None)
    return {"site": s,
            "insn": f"{ins.mnemonic} {ins.op_str}" if ins else None,
            "signature_hex": sig(a7, addr).hex(),
            "a6000_signature_hits": a6.count(sig(a7, addr))}


def main():
    a7 = A7.read_bytes()
    a6 = A6.read_bytes()
    rows = []
    for func, field, sites, callers in WRITERS:
        rows.append({
            "function": f"0x{func:08x}", "field": field, "callers": callers,
            "write_sites": [_site(a7, a6, s) for s in sites],
        })
    relaxed = [{
        "function": f"0x{f:08x}", "field": field,
        "sites": [{"site": s, "signature_hex": sig(a7, int(s, 16)).hex(),
                   "a6000_signature_hits": a6.count(sig(a7, int(s, 16)))} for s in sites],
    } for f, field, sites in RELAXED]

    sel = 0x43826D58
    sel_ins = next(MD.disasm(a7[sel - BASE:sel - BASE + 4], sel), None)
    win = 0x438645BE
    data = {
        "milestone": "S307",
        "title": "escrituras A7S exclusivas del estado (+0xde, +0xe6..+0xea) en código ausente en la A6000",
        "base": f"0x{BASE:08x}",
        "firmware": {"a6000": hashlib.sha256(a6).hexdigest(),
                     "a7s": hashlib.sha256(a7).hexdigest()},
        "writers": rows,
        "reads_only": relaxed,
        "selector": {
            "entry": f"0x{sel:08x}",
            "bytes_hex": a7[sel - BASE:sel - BASE + 4].hex(),
            "insn": f"{sel_ins.mnemonic} {sel_ins.op_str}" if sel_ins else None,
            "callers_direct": ["0x4354908c", "0x43826df2"],
        },
        "timing_function": {
            "entry": f"0x{win:08x}",
            "prologue_insn": "push {r4, r5, r6, r7, lr}",
            "direct_callers": [], "literal_pointer_hits": 0,
        },
        "scope_limit": "Ausencia por firma exacta de 24 B alrededor del store; no prueba que no "
                       "exista código equivalente reescrito. Alcanzabilidad runtime NO_VERIFICADA.",
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    for r in rows:
        print(r["function"], r["field"], [(w["site"], w["a6000_signature_hits"])
                                          for w in r["write_sites"]])


if __name__ == "__main__":
    main()
