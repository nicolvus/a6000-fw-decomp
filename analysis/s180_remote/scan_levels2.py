#!/usr/bin/env python3
"""S180 - id de modulo (r0) y nivel (r2) en CADA traza [ACCY], usando el logger
de su propio sub-bloque (el primer `bl` tras el sitio)."""
import json, re
from collections import Counter, defaultdict
from capstone import *
from capstone.arm import *

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True
REGNUM = {ARM_REG_R0: 0, ARM_REG_R1: 1, ARM_REG_R2: 2, ARM_REG_R3: 3, ARM_REG_R4: 4,
          ARM_REG_R5: 5, ARM_REG_R6: 6, ARM_REG_R7: 7, ARM_REG_R8: 8, ARM_REG_R9: 9,
          ARM_REG_R10: 10, ARM_REG_R11: 11, ARM_REG_R12: 12, ARM_REG_SP: 13,
          ARM_REG_LR: 14, ARM_REG_PC: 15}
LEVEL = {"ERR": 1, "WARN": 2, "DEBUG": 3, "INFO": 4}
accy = json.load(open("analysis/s136_accy/accy.json"))
allstr = json.load(open("analysis/s180_remote/pic_sites.json"))["strings"]
rem = {r["vaddr"] for r in allstr}


def dis(lo, hi):
    return list(md.disasm(B[lo - BASE:hi - BASE], lo))


rows = []
for s in accy["strings"]:
    vaddr = int(s["vaddr"], 16)
    m = re.match(r"^\[ACCY\]\[([A-Z]+)\]\[?([A-Za-z0-9]*)\]?", s["text"])
    lvl_txt = m.group(1) if m else None
    sub = m.group(2) if m else ""
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
        bl = None
        for p in ins:
            if p.address < site:
                continue
            if p.mnemonic == "bl":
                try:
                    bl = (p.address, p.operands[0].imm)
                except Exception:
                    bl = (p.address, None)
                break
        regs = {}
        if bl:
            for p in ins:
                if p.address >= bl[0]:
                    break
                if p.mnemonic in ("movs", "mov", "movw", "mov.w") and len(p.operands) == 2 \
                   and p.operands[0].type == ARM_OP_REG and p.operands[1].type == ARM_OP_IMM:
                    n = REGNUM.get(p.operands[0].reg)
                    if n is not None:
                        regs[n] = p.operands[1].imm
        rows.append({"vaddr": hex(vaddr), "site": sit, "sub": sub, "nivel_txt": lvl_txt,
                     "logger": (hex(bl[1]) if bl and bl[1] else None),
                     "r0_id_modulo": regs.get(0), "r2_nivel": regs.get(2),
                     "es_remoto": vaddr in rem, "text": s["text"]})

json.dump(rows, open("analysis/s180_remote/levels_accy.json", "w"), indent=1)
per = defaultdict(Counter)
for r in rows:
    per[r["sub"]][r["r0_id_modulo"]] += 1
print("id de modulo (r0) por sub-bloque [ACCY]:")
for sub in sorted(per):
    print(f"  {sub or '(sin sub-bloque)':10s} {dict(per[sub])}")
print()
remrows = [r for r in rows if r["es_remoto"]]
ok = sum(1 for r in remrows if r["r0_id_modulo"] == 93 and r["r2_nivel"] == LEVEL.get(r["nivel_txt"]))
print(f"[REMOTE]: r0==93 y r2==nivel en {ok}/{len(remrows)} sitios")
bad = [r for r in remrows if not (r["r0_id_modulo"] == 93 and r["r2_nivel"] == LEVEL.get(r["nivel_txt"]))]
for r in bad:
    print("  ", r)
