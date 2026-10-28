#!/usr/bin/env python3
"""Referencias a una dirección construida con `ldr rX,[pc,#]` + `add rX,pc` en av-cam.bin (y la instrucción de memoria que sigue).

Uso: xref_pc.py ADDR [ventana_bytes]
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BIN = Path(__file__).resolve().parents[2] / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000


def xrefs(data: bytes, target: int, ventana: int = 0) -> list[str]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    ins = []
    pos = 0
    while pos < len(data) - 4:
        got = False
        for i in md.disasm(data[pos:pos + 4], BASE + pos, 1):
            ins.append(i)
            pos += i.size
            got = True
        if not got:
            pos += 2
    out = []
    for n, i in enumerate(ins):
        if i.mnemonic == "add" and i.op_str.endswith(", pc") and "#" not in i.op_str:
            rx = i.op_str.split(",")[0]
            for p in ins[max(0, n - 4):n]:
                if p.mnemonic.startswith("ldr") and p.op_str.startswith(rx + ", [pc, #"):
                    d = int(p.op_str.split("#")[1].rstrip("]"), 0)
                    lit = ((p.address + 4) & ~3) + d
                    if 0 <= lit - BASE < len(data) - 4:
                        v = (struct.unpack_from("<I", data, lit - BASE)[0] + i.address + 4) & 0xFFFFFFFF
                        if abs(v - target) <= ventana:
                            nxt = "; ".join(f"{q.mnemonic} {q.op_str}" for q in ins[n + 1:n + 5])
                            out.append(f"{i.address:#x}: {rx}={v:#x} -> {nxt}")
    return out


if __name__ == "__main__":
    print("\n".join(xrefs(BIN.read_bytes(), int(sys.argv[1], 16), int(sys.argv[2], 0) if len(sys.argv) > 2 else 0)))
