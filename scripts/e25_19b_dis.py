#!/usr/bin/env python3
"""Desensamblado Thumb-2 de av-cam.bin con literales PC resueltos. Uso: e25_19b_dis.py ADDR [LEN_BYTES]."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BIN = Path(__file__).resolve().parents[1] / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000


def dis(data: bytes, addr: int, length: int = 0x200) -> list[str]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    out = []
    for i in md.disasm(data[addr - BASE : addr - BASE + length], addr & ~1):
        note = ""
        if i.mnemonic.startswith("ldr") and "[pc," in i.op_str:
            d = int(i.op_str.split("#")[1].rstrip("]"), 0)
            lit = ((i.address + 4) & ~3) + d
            if 0 <= lit - BASE < len(data) - 4:
                note = f"   ; [{lit:#x}]={struct.unpack_from('<I', data, lit - BASE)[0]:#x}"
        out.append(f"{i.address:#x}: {i.mnemonic} {i.op_str}{note}")
    return out


if __name__ == "__main__":
    a = int(sys.argv[1], 16)
    print("\n".join(dis(BIN.read_bytes(), a, int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x200)))
