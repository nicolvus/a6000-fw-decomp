#!/usr/bin/env python3
"""S180 - que logger usa cada traza [ACCY] (destino del primer `bl` tras el sitio)."""
import json, re
from collections import Counter
from capstone import *

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True
accy = json.load(open("analysis/s136_accy/accy.json"))
allstr = json.load(open("analysis/s180_remote/pic_sites.json"))["strings"]
rem = {r["vaddr"] for r in allstr}


def dis(lo, hi):
    return list(md.disasm(B[lo - BASE:hi - BASE], lo))


rows = []
for s in accy["strings"]:
    vaddr = int(s["vaddr"], 16)
    sub = re.match(r"^\[ACCY\]\[[A-Z]+\]\[([A-Z]+)\]", s["text"])
    sub = sub.group(1) if sub else "?"
    for sit in s["sites"]:
        site = int(sit, 16)
        f = None
        for cand in s["functions"]:
            fa = int(cand, 16)
            if fa <= site:
                f = fa
        if f is None:
            continue
        ins = dis(f, f + 0x900)
        tgt = None
        for p in ins:
            if p.address < site:
                continue
            if p.mnemonic == "bl":
                try:
                    tgt = p.operands[0].imm
                except Exception:
                    tgt = None
                break
        rows.append({"vaddr": hex(vaddr), "site": sit, "sub": sub,
                     "bl_target": (hex(tgt) if tgt else None),
                     "es_remoto": vaddr in rem, "text": s["text"]})

json.dump(rows, open("analysis/s180_remote/logger_targets.json", "w"), indent=1)
c = Counter(r["bl_target"] for r in rows)
print("destinos del primer bl tras cada traza [ACCY]:")
for k, v in c.most_common():
    print(f"  {k}: {v}")
print()
print("por sub-bloque:")
for sub in sorted({r["sub"] for r in rows}):
    cc = Counter(r["bl_target"] for r in rows if r["sub"] == sub)
    print(f"  {sub:8s} {dict(cc)}")
