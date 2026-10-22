#!/usr/bin/env python3
"""S166 — desensamblado anotado con resolucion de literales:
   - `ldr rX,[pc,#imm]`  -> muestra la palabra del pool
   - `add rX,pc`         -> muestra el destino calculado (si hay un ldr reciente)
   - `bl/blx`            -> muestra el destino
Uso: disasm2.py 0xADDR [N_INSTR]
"""
import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
DATA = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
REFS = json_refs = None
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False

STR = {}
for m in re.finditer(rb"[\x20-\x7e]{4,}", DATA):
    STR[BASE + m.start()] = m.group().decode("latin1")


def u32(a):
    o = a - BASE
    if 0 <= o and o + 4 <= len(DATA):
        return struct.unpack_from("<I", DATA, o)[0]
    return None


def cstr(a):
    o = a - BASE
    if o < 0 or o >= len(DATA):
        return "<OOR>"
    e = o
    while e < len(DATA) and DATA[e] != 0:
        e += 1
    return DATA[o:e].decode("latin1")


def main():
    a = int(sys.argv[1], 0)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    last_ldr = {}
    for i in MD.disasm(DATA[a - BASE:a - BASE + n * 4], a):
        note = ""
        m = re.match(r"^r(\d+), \[pc, #(0x[0-9a-f]+)\]$", i.op_str)
        if m:
            reg = int(m.group(1))
            imm = int(m.group(2), 16)
            lit = ((i.address + 4) & ~3) + imm
            v = u32(lit)
            last_ldr[reg] = (lit, v)
            note = "  ; pool %08x = 0x%08x" % (lit, v if v is not None else 0)
        elif re.match(r"^r\d+, pc$", i.op_str):
            reg = int(i.op_str[1:-4].strip())
            if reg in last_ldr:
                lit, v = last_ldr[reg]
                if v is not None:
                    dst = i.address + 4 + v
                    note = "  ; -> %08x %r" % (dst, cstr(dst))
        elif i.mnemonic in ("bl", "blx") and i.op_str.startswith("#0x"):
            note = ""
        print("%08x  %-9s %-28s%s" % (i.address, i.mnemonic, i.op_str, note))


if __name__ == "__main__":
    main()
