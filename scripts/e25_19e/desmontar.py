#!/usr/bin/env python3
"""Desensamblador Thumb-2 de av-cam.bin: dis.py START END [mapa de etiquetas ignorado]."""
from __future__ import annotations

import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000


def dis(start: int, end: int, data: bytes | None = None) -> list[str]:
    data = data or BIN.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    out, pos = [], start - BASE
    while BASE + pos < end:
        got = False
        for i in md.disasm(data[pos:pos + 4], BASE + pos, 1):
            out.append(f"{i.address:#x}: {i.mnemonic} {i.op_str}")
            pos += i.size
            got = True
        if not got:
            out.append(f"{BASE + pos:#x}: .short {int.from_bytes(data[pos:pos + 2], 'little'):#06x}")
            pos += 2
    return out


if __name__ == "__main__":
    print("\n".join(dis(int(sys.argv[1], 0), int(sys.argv[2], 0))))
