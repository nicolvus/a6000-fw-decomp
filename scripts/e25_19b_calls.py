#!/usr/bin/env python3
"""Llamadas (bl/blx/b.w) de una función Thumb de av-cam.bin hasta su último retorno alcanzable. Uso: ADDR [MAXLEN]."""
from __future__ import annotations

import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from e25_19b_dis import BASE, BIN


def calls(data: bytes, start: int, maxlen: int = 0x800) -> tuple[list[tuple[int, str, int]], int]:
    """Barrido lineal; termina al pasar el mayor destino de salto interno tras un `pop {..pc}`/`bx lr`/`b.w` incondicional."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    out, far, end = [], start, start
    for i in md.disasm(data[start - BASE : start - BASE + maxlen], start):
        end = i.address + i.size
        if i.mnemonic.startswith(("bl", "blx", "b.w")) and i.op_str.startswith("#"):
            out.append((i.address, i.mnemonic, int(i.op_str[1:], 0)))
        elif i.mnemonic[0] == "b" and i.op_str.startswith("#"):
            far = max(far, int(i.op_str[1:], 0))
        elif i.mnemonic.startswith("cb"):
            far = max(far, int(i.op_str.split("#")[1], 0))
        if (i.mnemonic.startswith("pop") and "pc" in i.op_str or i.mnemonic == "bx" and i.op_str == "lr"
                or i.mnemonic == "b.w") and i.address >= far:
            break
    return out, end


if __name__ == "__main__":
    a = int(sys.argv[1], 16)
    c, end = calls(BIN.read_bytes(), a, int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x800)
    print(f"{a:#x}..{end:#x} ({end - a:#x} B)")
    for site, m, t in c:
        print(f"  {site:#x} {m} {t:#x}")
