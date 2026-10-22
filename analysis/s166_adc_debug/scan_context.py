#!/usr/bin/env python3
"""S166 — lista las cadenas referenciadas (PIC, regla estricta) desde una region de codigo,
con su funcion contenedora, y las funciones de la region.

Uso: scan_context.py 0xLO 0xHI
"""
import bisect
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
DATA = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
REFS = json.loads((ROOT / "analysis/s106_imaging_cap/pic_refs_strict_global.json").read_text())
PROL = json.loads((ROOT / "analysis/s166_adc_debug/prologues.json").read_text())
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False

STR = {}
for m in re.finditer(rb"[\x20-\x7e]{4,}", DATA):
    STR[BASE + m.start()] = m.group().decode("latin1")


def container(site):
    k = bisect.bisect_left(PROL, site) - 1
    for p in reversed(PROL[max(0, k - 80):k + 1]):
        if site - p > 0x3000:
            break
        last = None
        ok = True
        for ins in MD.disasm(DATA[p - BASE:site - BASE], p):
            if ins.address >= site:
                break
            m, o = ins.mnemonic, ins.op_str
            if (m.startswith("pop") and "pc" in o) or (m == "bx" and o == "lr"):
                ok = False
                break
            last = ins
        if ok and last is not None and last.address + last.size == site:
            return p
    for p in reversed(PROL[max(0, k - 80):k + 1]):
        if site - p > 0x3000:
            break
        return p
    return None


def main():
    lo, hi = int(sys.argv[1], 0), int(sys.argv[2], 0)
    rev = defaultdict(list)
    for k, v in REFS.items():
        d = int(k, 16)
        for s in v:
            rev[s].append(d)
    rows = []
    for site in sorted(rev):
        if not (lo <= site < hi):
            continue
        for d in rev[site]:
            rows.append((site, d, STR.get(d, "?"), container(site)))
    print("== cadenas referenciadas en la region ==")
    for site, d, txt, f in rows:
        print("  site %08x -> %08x %-70r func %s" % (site, d, txt[:70],
                                                      ("%08x" % f) if f else "?"))
    print("== funciones (prologos) en la region ==")
    for p in PROL:
        if lo <= p < hi:
            print("  %08x" % p)


if __name__ == "__main__":
    main()
