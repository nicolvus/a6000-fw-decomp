#!/usr/bin/env python3
"""S180 - firma del logger del modulo [ACCY]: (id de modulo r0, nivel r2) por traza.

Se recorre cada sitio PIC de las 106 trazas [ACCY] hacia adelante hasta la llamada
al logger 0x435661e4 y se leen r0 y r2 (inmediatos cargados antes de la llamada).
"""
import json, re, struct
from capstone import *
from capstone.arm import *

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
LOGGER = 0x435661e4
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

# funcion -> traza, desde el mapa de S136
site2 = {}
for s in accy["strings"]:
    for sit in s["sites"]:
        site2[int(sit, 16)] = s


def dis(lo, hi):
    return list(md.disasm(B[lo - BASE:hi - BASE], lo))


rows = []
for s in accy["strings"]:
    vaddr = int(s["vaddr"], 16)
    lvl_txt = re.match(r"^\[ACCY\]\[([A-Z]+)\]", s["text"])
    lvl_txt = lvl_txt.group(1) if lvl_txt else None
    for sit in s["sites"]:
        site = int(sit, 16)
        # función: la primera de la lista de S136 que contiene el sitio
        f = None
        for cand in s["functions"]:
            fa = int(cand, 16)
            if fa <= site:
                f = fa
        if f is None:
            continue
        ins = dis(f, f + 0x900)
        bl_addr = None
        for p in ins:
            if p.address < site:
                continue
            if p.mnemonic == "bl":
                try:
                    if p.operands[0].imm == LOGGER:
                        bl_addr = p.address
                except Exception:
                    pass
                break
        if bl_addr is None:
            rows.append({"vaddr": hex(vaddr), "site": sit, "text": s["text"],
                         "nivel_txt": lvl_txt, "r0": None, "r2": None,
                         "es_remoto": vaddr in rem, "nota": "sin llamada al logger de modulo"})
            continue
        regs = {}
        for p in ins:
            if p.address >= bl_addr:
                break
            if p.mnemonic in ("movs", "mov", "movw", "mov.w") and len(p.operands) == 2 \
               and p.operands[0].type == ARM_OP_REG and p.operands[1].type == ARM_OP_IMM:
                n = REGNUM.get(p.operands[0].reg)
                if n is not None:
                    regs[n] = p.operands[1].imm
        rows.append({"vaddr": hex(vaddr), "site": sit, "text": s["text"],
                     "nivel_txt": lvl_txt, "r0": regs.get(0), "r2": regs.get(2),
                     "es_remoto": vaddr in rem, "bl": hex(bl_addr)})

json.dump(rows, open("analysis/s180_remote/levels_accy.json", "w"), indent=1)

remrows = [r for r in rows if r["es_remoto"]]
print(f"=== trazas [REMOTE]: {len(remrows)} sitios ===")
ok = 0
for r in remrows:
    exp = LEVEL.get(r["nivel_txt"])
    good = (r["r2"] == exp) and r["r0"] == 93
    ok += good
    if not good:
        print("  ", r)
print(f"  r0==93 (id de modulo) y r2==nivel del prefijo en {ok}/{len(remrows)} sitios")
print("  ids de modulo r0 distintos de 93:",
      sorted({r["r0"] for r in remrows}))
print("  niveles r2 distintos:", sorted({r["r2"] for r in remrows}))
print()
allr = [r for r in rows if r["r0"] is not None]
print("=== todo el bloque [ACCY] (%d sitios con logger de modulo) ===" % len(allr))
from collections import Counter
print("  ids de modulo r0:", Counter(r["r0"] for r in allr))
print("  niveles r2:", Counter(r["r2"] for r in allr))
mismatch = [r for r in allr if LEVEL.get(r["nivel_txt"]) != r["r2"]]
print("  discrepancias nivel texto vs r2:", len(mismatch))
for r in mismatch[:10]:
    print("   ", r["vaddr"], r["nivel_txt"], r["r2"], r["text"][:60])
