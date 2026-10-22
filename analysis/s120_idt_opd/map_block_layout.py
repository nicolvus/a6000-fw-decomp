#!/usr/bin/env python3
"""S120 — reconstruye la tabla de punteros que vuelca la función de mapas.

Función `dump` (0x439f85d4 en la A6000 fw3.21): para cada campo del bloque imprime
`nombre:%X` con el valor leído de `[base+offset]`.  De aquí sale la **estructura del
bloque de mapas** (direcciones globales y offsets) verificable contra los bytes.
"""
import json
import os
import struct

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
DUMP = 0x439F85D4
END = 0x439F8930


def u32(data, a):
    return struct.unpack_from("<I", data, a - BASE)[0]


def cstr(data, a):
    o = a - BASE
    e = data.find(b"\x00", o)
    return data[o:e].decode("latin1")


def main():
    data = open(BIN, "rb").read()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    regs = {}        # registro -> valor conocido (dirección)
    pending = {}     # registro -> literal pendiente de `add pc`
    out = []
    for ins in md.disasm(data[DUMP - BASE:END - BASE], DUMP):
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
                regs[r] = val
                s = cstr(data, val) if BASE <= val < BASE + len(data) else ""
                if s.startswith("[IDT"):
                    out.append({"kind": "str", "site": f"0x{ins.address:x}",
                                "reg": r, "addr": f"0x{val:x}", "text": s})
                else:
                    out.append({"kind": "global", "site": f"0x{ins.address:x}",
                                "reg": r, "addr": f"0x{val:x}"})
            continue
        if mn.startswith("ldr") and "[" in ops and "[pc" not in ops:
            dest = ops.split(",")[0].strip()
            mm = ops.split("[", 1)[1]
            basereg = mm.split(",")[0].strip()
            off = 0
            if "#" in mm:
                off = int(mm.split("#")[1].rstrip("]"), 0)
            if basereg in regs:
                out.append({"kind": "load", "site": f"0x{ins.address:x}",
                            "reg": dest, "base": f"0x{regs[basereg]:x}",
                            "offset": off,
                            "expr": f"[0x{regs[basereg]:x} + 0x{off:x}]"})
                regs[dest] = None
    for r in out:
        print(r)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "map_block_table.json"), "w"),
              indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
