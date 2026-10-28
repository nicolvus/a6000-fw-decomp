#!/usr/bin/env python3
"""Inicio probable de la función Thumb-2 que contiene ADDR: último `push {..lr}` previo alineado en 2 con desensamblado limpio."""
from __future__ import annotations

import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from desmontar import BASE, BIN


def inicio(addr: int, data: bytes | None = None, tope: int = 0x6000) -> int | None:
    data = data or BIN.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    for a in range(addr & ~1, addr - tope, -2):
        for i in md.disasm(data[a - BASE:a - BASE + 4], a, 1):
            if i.mnemonic.startswith("push") and "lr" in i.op_str:
                return a
    return None


if __name__ == "__main__":
    for s in sys.argv[1:]:
        r = inicio(int(s, 0))
        print(s, hex(r) if r else None)
