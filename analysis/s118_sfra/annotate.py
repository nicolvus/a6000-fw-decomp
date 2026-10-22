#!/usr/bin/env python3
"""S118 — desensamblador anotado del módulo `[SFRA]`.

Resuelve el esquema PIC Thumb del firmware (ldr rX,[pc,#imm] + add rX,pc) y
anota cada `add rX, pc` con la cadena a la que apunta (usando la resolución con
flujo de datos `pic_refs_dataflow.json`, que descarta los falsos positivos de
la regla canónica).

Uso:  python3 annotate.py 0x439a1864 [n_insns]
"""
import json
import os
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))


def load():
    return open(BIN, "rb").read()


def cstr(data, va, maxlen=120):
    off = va - BASE
    if off < 0 or off >= len(data):
        return None
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    if end == off:
        return None
    return data[off:end].decode("latin1")


def site_map():
    """sitio `add` -> cadena [SFRA] resuelta."""
    m = {}
    p = os.path.join(HERE, "pic_refs_dataflow.json")
    if not os.path.exists(p):
        return m
    for dest, sites in json.load(open(p)).items():
        va = int(dest, 16)
        for s in sites:
            m[s] = va
    return m


def main():
    start = int(sys.argv[1], 0)
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    data = load()
    smap = site_map()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    off = start - BASE
    for ins in md.disasm(data[off:off + count * 4], start):
        ann = []
        h = struct.unpack_from("<H", data, ins.address - BASE)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            tgt = smap.get(ins.address)
            if tgt:
                s = cstr(data, tgt)
                ann.append(f"-> {tgt:#x} {s!r}")
        elif (h & 0xF800) == 0x4800:
            lit = ((ins.address + 4) & ~3) + (h & 0xFF) * 4
            w = struct.unpack_from("<I", data, lit - BASE)[0]
            ann.append(f"pool@{lit:#x}=0x{w:08x}")
        extra = ("   ; " + " | ".join(ann)) if ann else ""
        print(f"{ins.address:08x}  {ins.mnemonic + ' ' + ins.op_str:<34}{extra}")


if __name__ == "__main__":
    main()
