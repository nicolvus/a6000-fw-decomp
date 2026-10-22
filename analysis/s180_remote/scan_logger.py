#!/usr/bin/env python3
"""S180 - (a) firma del logger [REMOTE]  (b) targets de llamada de las 16 funciones."""
import json, re, struct
from capstone import *
from capstone.arm import *

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
LOGGER = 0x435661e4
GLOBAL_LOGGER = 0x43902718
B = open(BIN, "rb").read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True

fm = json.load(open("analysis/s180_remote/func_map.json"))
remote = json.load(open("analysis/s180_remote/pic_sites.json"))["strings"]
rem = {r["vaddr"]: r for r in remote}


def dis(lo, hi):
    return list(md.disasm(B[lo - BASE:hi - BASE], lo))


def cstr(a):
    o = a - BASE
    e = o
    while e < len(B) and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1")


starts = sorted(int(k, 16) for k in fm["funcs"])
lim = {s: (starts[i + 1] if i + 1 < len(starts) else s + 0x400) for i, s in enumerate(starts)}

rows = []
calls = {}
for f, items in sorted(fm["funcs"].items(), key=lambda kv: int(kv[0], 16)):
    fa = int(f, 16)
    rem_items = [i for i in items if int(i["dest"], 16) in rem]
    if not rem_items:
        continue
    ins = dis(fa, min(lim[fa], fa + 0x800))
    tgts = []
    for i in ins:
        if i.mnemonic in ("bl", "blx"):
            try:
                tgts.append(i.operands[0].imm)
            except Exception:
                pass
    calls[f] = sorted(set(f"0x{t:08x}" for t in tgts))
    for idx, i in enumerate(ins):
        if i.mnemonic != "bl":
            continue
        try:
            tgt = i.operands[0].imm
        except Exception:
            continue
        if tgt != LOGGER:
            continue
        dest = site = None
        for j in range(idx - 1, max(-1, idx - 30), -1):
            p = ins[j]
            if p.mnemonic == "add" and len(p.operands) == 2 and p.operands[1].type == ARM_OP_REG \
               and p.operands[1].reg == ARM_REG_PC:
                rd = p.operands[0].reg
                for k in range(j - 1, max(-1, j - 30), -1):
                    q = ins[k]
                    if q.mnemonic.startswith("ldr") and len(q.operands) == 2 \
                       and q.operands[1].type == ARM_OP_MEM and q.operands[1].mem.base == ARM_REG_PC \
                       and q.operands[0].reg == rd:
                        lit = ((q.address + 4) & ~3) + q.operands[1].mem.disp
                        W = struct.unpack_from("<I", B, lit - BASE)[0]
                        dest = (W + (p.address + 4)) & 0xFFFFFFFF
                        site = p.address
                        break
                if dest is not None:
                    break
        regs = {}
        for j in range(max(0, idx - 40), idx):
            p = ins[j]
            if p.mnemonic in ("movs", "mov", "movw", "mov.w", "movt") and len(p.operands) == 2 \
               and p.operands[0].type == ARM_OP_REG and p.operands[1].type == ARM_OP_IMM:
                regs[p.operands[0].reg] = p.operands[1].imm
        line = None
        for j in range(max(0, idx - 40), idx):
            p = ins[j]
            if p.mnemonic in ("str", "str.w") and len(p.operands) == 2 \
               and p.operands[1].type == ARM_OP_MEM and p.operands[1].mem.base == ARM_REG_SP \
               and p.operands[1].mem.disp == 0 and p.operands[0].type == ARM_OP_REG:
                rr = p.operands[0].reg
                if rr in regs:
                    line = regs[rr]
                    break
        rows.append({
            "func": f, "bl": hex(i.address), "site": (hex(site) if site else None),
            "dest": (hex(dest) if dest else None),
            "text": cstr(dest) if dest else None,
            "is_remote": dest in rem,
            "r0": regs.get(ARM_REG_R0), "r1": regs.get(ARM_REG_R1), "r2": regs.get(ARM_REG_R2),
            "line": line,
        })

json.dump(rows, open("analysis/s180_remote/log_calls.json", "w"), indent=1)
json.dump(calls, open("analysis/s180_remote/calls.json", "w"), indent=1)
print(f"{'func':>10} {'bl':>10} {'site':>10}  r0  r1  r2  linea  texto")
for r in rows:
    mark = "REMOTE" if r["is_remote"] else "      "
    print(f"{mark} {r['func']} {r['bl']} {r['site']}  {r['r0']} {r['r1']} {r['r2']} {r['line']}  {str(r['text'])[:60]!r}")
print()
print("--- el logger global 0x43902718 aparece en alguna funcion REMOTE? ---")
for f, tg in calls.items():
    if "0x43902718" in tg:
        print("  SI:", f)
print("  (vacio = no)")
print()
print("--- targets de llamada por funcion REMOTE ---")
for f, tg in calls.items():
    print(f"{f}: {tg}")
