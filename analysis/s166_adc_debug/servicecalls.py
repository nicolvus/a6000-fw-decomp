#!/usr/bin/env python3
"""S166 — resuelve el "handle" (r0) de las llamadas al servicio generico 0x43561228
(vtable slot 0x1d8) dentro de una region, y el id de mensaje (msg[0]) si se puede.

Uso: servicecalls.py 0xLO 0xHI [0xSERVICE_HELPER]
"""
import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
DATA = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False


def u32(a):
    o = a - BASE
    if 0 <= o and o + 4 <= len(DATA):
        return struct.unpack_from("<I", DATA, o)[0]
    return None


def main():
    lo, hi = int(sys.argv[1], 0), int(sys.argv[2], 0)
    helper = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x43561228
    insns = list(MD.disasm(DATA[lo - BASE:hi - BASE], lo))
    last = {}
    for i in insns:
        m = re.match(r"^r(\d+), \[pc, #(0x[0-9a-f]+)\]$", i.op_str)
        if m:
            reg = int(m.group(1))
            imm = int(m.group(2), 16)
            lit = ((i.address + 4) & ~3) + imm
            last[reg] = (lit, u32(lit))
            continue
        if i.mnemonic == "bl" and i.op_str.startswith("#0x"):
            tgt = int(i.op_str[1:], 16)
            if tgt == helper:
                # r0 se carga con el literal mas reciente del registro r0
                lit, v = last.get(0, (None, None))
                extra = ""
                if lit is not None:
                    # si el literal se usa con 'add rX,pc' -> puntero a cadena/dato
                    extra = " lit %08x=0x%08x" % (lit, v)
                print("bl %08x -> %08x%s" % (i.address, tgt, extra))
                last.clear()


if __name__ == "__main__":
    main()
