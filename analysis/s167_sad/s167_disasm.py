#!/usr/bin/env python3
"""S167 — desensamblado de un rango (Thumb). Uso: s167_disasm.py LO HI [n]"""
import sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

BASE = 0x43541000
B = open("analysis/rea-independent/input/av-cam.bin", "rb").read()

def cstr(a):
    o = a - BASE
    if o < 0 or o >= len(B):
        return None
    e = B.find(b"\x00", o)
    return B[o:e].decode("latin1")

def main():
    lo = int(sys.argv[1], 0); hi = int(sys.argv[2], 0)
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    for ins in md.disasm(B[lo-BASE:hi-BASE], lo):
        s = ins.mnemonic + " " + ins.op_str
        extra = ""
        #注解: si hay ldr literal, mostrar el literal
        if ins.mnemonic.startswith("ldr") and "[pc" in ins.op_str:
            try:
                imm = int(ins.op_str.split("#")[1].rstrip("]"), 0)
                pool = ((ins.address + 4) & ~3) + imm
                val = int.from_bytes(B[pool-BASE:pool-BASE+4], "little")
                extra = f"   ; pool={pool:#x} W={val:#x} -> {val + ins.address + 4:#x} {cstr(val + ins.address + 4)!r}"
            except Exception as e:
                extra = f"  ; ldr? {e}"
        print(f"{ins.address:#010x}  {ins.bytes.hex():<10s} {s:<40s}{extra}")

main()
