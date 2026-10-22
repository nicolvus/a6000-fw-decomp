#!/usr/bin/env python3
"""S122 — utilidades de desensamblado sobre bytes (Capstone) para verificación a mano.

Uso:
  disasm.py func <vaddr> [n_inst]      desensambla desde el prólogo que contiene <vaddr>
  disasm.py window <lo> <hi>           desensambla un rango
  disasm.py callees <lo> <hi>          lista los destinos de `bl` del rango
  disasm.py strings <lo> <hi>          cadenas referenciadas por PIC dentro del rango
"""
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
U16 = struct.Struct("<H").unpack_from
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = True


def prologues(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
        elif h == 0xE92D and (U16(B, o + 2)[0] & 0x4000):
            out.append(a)
        a += 2
    return out


def func_of(a, lo=0x43541000, hi=0x43C90000):
    cand = [x for x in prologues(lo, hi) if x <= a]
    return cand[-1] if cand else None


def disasm(lo, n=200):
    code = B[lo - BASE: lo - BASE + n * 4]
    return list(MD.disasm(code, lo))


def cstr(v):
    o = v - BASE
    if not (0 <= o < len(B)):
        return None
    e = o
    while e < len(B) and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1") if e > o else None


def show(ins):
    for i in ins:
        print(f"0x{i.address:08x}  {i.bytes.hex():<10} {i.mnemonic:<8} {i.op_str}")


def callees(lo, hi):
    out = []
    for i in disasm(lo, (hi - lo) // 4 + 1):
        if i.mnemonic.startswith("bl"):
            t = i.operands[0]
            out.append((i.address, t.imm))
    return out


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "func":
        a = int(sys.argv[2], 16)
        f = func_of(a)
        print(f"# función 0x{f:x} (sitio 0x{a:x})")
        show(disasm(f, int(sys.argv[3]) if len(sys.argv) > 3 else 400))
    elif cmd == "window":
        lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
        show(disasm(lo, (hi - lo) // 4 + 1))
    elif cmd == "callees":
        lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
        for a, t in callees(lo, hi):
            print(f"0x{a:x} -> 0x{t:x}")
    elif cmd == "strings":
        lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
        last = {}
        for i in disasm(lo, (hi - lo) // 4 + 1):
            if i.mnemonic.startswith("ldr") and "[pc," in i.op_str:
                reg = i.op_str.split(",")[0]
                pool = ((i.address + 4) & ~3) + i.operands[1].mem.disp
                last[reg] = (i.address, struct.unpack_from("<I", B, pool - BASE)[0])
            elif i.mnemonic == "add" and i.op_str.endswith(", pc"):
                reg = i.op_str.split(",")[0]
                if reg in last:
                    d = last[reg][1] + i.address + 4
                    s = cstr(d)
                    if s:
                        print(f"0x{i.address:x} {reg} -> 0x{d:x} {s!r}")
