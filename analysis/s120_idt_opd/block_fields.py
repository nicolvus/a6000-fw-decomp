#!/usr/bin/env python3
"""S120 — extrae (cadena, base, offset) de una función que valida/vuelca un bloque.

Uso:  block_fields.py FUNC_VADDR [FUNC_VADDR ...]

Para cada cadena `[IDT*]: ...` materializada por la función se busca el acceso
`ldr rN, [rB, #off]` inmediatamente anterior (el valor que se imprime) y se anota
la base (parámetro de entrada o global).  De ahí sale la **estructura del bloque**
(nombre del campo → offset dentro del bloque).
"""
import json
import os
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")


def u32(data, a):
    return struct.unpack_from("<I", data, a - BASE)[0]


def cstr(data, a):
    o = a - BASE
    e = data.find(b"\x00", o)
    return data[o:e].decode("latin1")


def walk(data, start, length=0x1400):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    insns = list(md.disasm(data[start - BASE:start - BASE + length], start))
    regs = {"r0": ("param", 0), "r1": ("param", 1), "r2": ("param", 2)}
    pending = {}
    out = []
    for i, ins in enumerate(insns):
        mn, ops = ins.mnemonic, ins.op_str
        if mn.startswith("ldr") and "[pc" in ops:
            r = ops.split(",")[0].strip()
            imm = int(ops.split("#")[1].rstrip("]"), 0)
            lit = ((ins.address + 4) & ~3) + imm
            pending[r] = u32(data, lit)
            continue
        if mn == "add" and ops.endswith("pc"):
            r = ops.split(",")[0].strip()
            if r in pending:
                val = (pending.pop(r) + (ins.address + 4)) & 0xFFFFFFFF
                regs[r] = ("global", val)
                s = cstr(data, val) if BASE <= val < BASE + len(data) else ""
                if s.startswith("[IDT"):
                    # busca hacia atrás el `ldr rN, [rB, #off]` del valor impreso
                    acc = None
                    for j in range(i - 1, max(-1, i - 8), -1):
                        p = insns[j]
                        if p.mnemonic.startswith("ldr") and "[" in p.op_str \
                                and "[pc" not in p.op_str:
                            mm = p.op_str.split("[", 1)[1]
                            breg = mm.split(",")[0].strip()
                            off = 0
                            if "#" in mm:
                                off = int(mm.split("#")[1].rstrip("]"), 0)
                            b = regs.get(breg)
                            if b is not None and b[0] in ("param", "global"):
                                acc = {"base_kind": b[0], "base": b[1], "offset": off,
                                       "width": p.mnemonic, "load_site": f"0x{p.address:x}"}
                            break
                    out.append({"text": s, "site": f"0x{ins.address:x}",
                                "str_addr": f"0x{val:x}", "acc": acc})
            continue
        if mn == "mov" and "," in ops:
            d, s2 = [x.strip() for x in ops.split(",", 1)]
            if s2 in regs:
                regs[d] = regs[s2]
            continue
        if (mn.startswith("ldr") or mn.startswith("ldrh") or mn.startswith("ldrb")) \
                and "[" in ops and "[pc" not in ops:
            dest = ops.split(",")[0].strip()
            mm = ops.split("[", 1)[1]
            breg = mm.split(",")[0].strip()
            off = 0
            if "#" in mm:
                off = int(mm.split("#")[1].rstrip("]"), 0)
            b = regs.get(breg)
            regs[dest] = ("load", (b[0], b[1], off)) if b else None
    return out


def main():
    data = open(BIN, "rb").read()
    out = {}
    for arg in sys.argv[1:]:
        f = int(arg, 0)
        rows = walk(data, f)
        out[f"0x{f:x}"] = rows
        print(f"### función 0x{f:x}")
        for r in rows:
            a = r["acc"]
            if a:
                base = f"arg{a['base']}" if a["base_kind"] == "param" else f"0x{a['base']:x}"
                off = f"+0x{a['offset']:x}"
                w = a["width"]
            else:
                base, off, w = "?", "?", "?"
            print(f"  {off:>8} {w:<5} base={base:<10} {r['text']}")
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "block_fields.json"), "w"),
              indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
