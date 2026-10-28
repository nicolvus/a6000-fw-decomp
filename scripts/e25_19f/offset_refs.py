#!/usr/bin/env python3
"""Instrucciones de av-cam.bin con operando de memoria [rX, #OFF]: offset_refs.py OFF [lector|escritor] (todo el binario)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"


def refs(off: int, modo: str = "") -> list[str]:
    data = Path(BIN).read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    pat = re.compile(rf"\[(?:r\d+|sb|sl|fp|ip), #{off:#x}\]|\[(?:r\d+|sb|sl|fp|ip), #{off:#x}\]!")
    out, pos = [], 0
    while pos < len(data) - 4:
        got = False
        for i in md.disasm(data[pos:pos + 4], BASE + pos, 1):
            if pat.search(i.op_str):
                es = i.mnemonic.startswith("st")
                if modo == "" or (modo == "escritor") == es:
                    out.append(f"{i.address:#x}: {i.mnemonic} {i.op_str}")
            pos += i.size
            got = True
        if not got:
            pos += 2
    return out


if __name__ == "__main__":
    print("\n".join(refs(int(sys.argv[1], 0), sys.argv[2] if len(sys.argv) > 2 else "")))
