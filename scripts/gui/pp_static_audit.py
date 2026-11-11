#!/usr/bin/env python3
"""G34 — auditoría estática de las conexiones del Picture Profile en el núcleo `av-cam.bin` (A6000 fw3.21). Solo lee.

Para cada base de `cfg` (0x43EDF684 y copias) busca, con un seguimiento lineal de registros, los accesos `[reg+off]` a los campos PP (0x138…0x173)
y los agrupa por campo y por función. Uso: pp_static_audit.py [av-cam.bin] → JSON a stdout."""
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from capstone.arm_const import *

BASE = 0x43541000
BASES = {0x43EDF684: "cfg", 0x43ED4D70: "cfgW", 0xC0FFEE: "cfg**(g+4)"}
LO, HI = 0x134, 0x174
DEF = Path(__file__).resolve().parents[2] / "analysis/rea-independent/input/av-cam.bin"


def barrer(b: bytes, code_end: int):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    md.skipdata = True
    ins = list(md.disasm(b[:code_end], BASE))
    return ins


def u32(b, a):
    o = a - BASE
    return struct.unpack_from("<I", b, o)[0] if 0 <= o <= len(b) - 4 else None


def main(path=DEF, code_end=0x0774000):
    b = Path(path).read_bytes()
    ins = barrer(b, min(code_end, len(b)))
    acc = defaultdict(lambda: defaultdict(list))   # campo → función → [(addr, instr)]
    regs: dict[int, int] = {}                      # registro → base cfg (valor)
    since = 0
    func = 0
    for i in ins:
        mn, op = i.mnemonic, i.op_str
        if i.id == 0:                              # bytes sin decodificar (SKIPDATA)
            continue
        if mn.startswith("push") and "lr" in op:
            regs, func = {}, i.address
        if mn == "ldr" and "[pc," in op and i.id == ARM_INS_LDR:
            r = i.operands[0].reg
            pc = (i.address + 4) & ~3
            v = u32(b, pc + i.operands[1].mem.disp)
            regs[r] = ("lit", v)
            continue
        if mn == "add" and "pc" in op and len(i.operands) == 2 and i.operands[1].type == ARM_OP_REG and i.operands[1].reg == ARM_REG_PC:
            r = i.operands[0].reg
            if r in regs and regs[r][0] == "lit":
                v = (regs[r][1] + i.address + 4) & 0xFFFFFFFF
                regs[r] = ("base", v) if v in BASES else ("x",)
            continue
        if mn == "mov" and len(i.operands) == 2 and i.operands[1].type == ARM_OP_REG:
            d, s = i.operands[0].reg, i.operands[1].reg
            if s in regs and regs[s][0] == "base":
                regs[d] = regs[s]
            else:
                regs.pop(d, None)
            continue
        mem = [o.mem for o in i.operands if o.type == ARM_OP_MEM]
        if mn.startswith("ldr") and mem and mem[0].base != ARM_REG_PC and mem[0].index == 0 and i.operands[0].type == ARM_OP_REG:
            d = i.operands[0].reg
            if mem[0].disp == 4 and mem[0].base not in (ARM_REG_SP,):
                regs[d] = ("p4",)
                continue
            if mem[0].disp == 0 and mem[0].base in regs and regs[mem[0].base][0] == "p4":      # cfg = **(g + 4)
                regs[d] = ("base", 0xC0FFEE)
                continue
        if mem and mem[0].base in regs and regs[mem[0].base][0] == "base" and LO <= mem[0].disp < HI:
            m = mem[0]
            acc[m.disp][func].append((i.address, f"{mn} {op}", BASES[regs[m.base][1]]))
        # el registro destino deja de ser base si se sobreescribe
        if i.operands and i.operands[0].type == ARM_OP_REG and mn[:3] in ("ldr", "mov", "add", "sub", "and", "orr", "lsl", "lsr"):
            r = i.operands[0].reg
            if r in regs and not (mn == "ldr" and "[pc," in op):
                if regs[r][0] == "base" and mn.startswith("add") is False:
                    regs.pop(r, None)
    return {f"{k:#x}": {f"{f:#x}": v for f, v in sorted(d.items())} for k, d in sorted(acc.items())}


if __name__ == "__main__":
    r = main(*sys.argv[1:2])
    print(json.dumps({k: {f: [(hex(a), s, c) for a, s, c in v] for f, v in d.items()} for k, d in r.items()}, indent=0)[:200000])
