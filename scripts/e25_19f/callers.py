#!/usr/bin/env python3
"""Llamadores directos (BL/B.W) a una o varias direcciones de av-cam.bin: callers.py ADDR [ADDR...]"""
from __future__ import annotations

import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from capstone.arm_const import ARM_OP_IMM

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"


def callers(targets: set[int]) -> dict[int, list[int]]:
    data = open(BIN, "rb").read()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    out: dict[int, list[int]] = {t: [] for t in targets}
    pos = 0
    while pos < len(data) - 4:
        got = False
        for i in md.disasm(data[pos:pos + 4], BASE + pos, 1):
            if i.mnemonic in ("bl", "blx", "b.w") and i.operands and i.operands[0].type == ARM_OP_IMM and i.operands[0].imm in targets:
                out[i.operands[0].imm].append(i.address)
            pos += i.size
            got = True
        if not got:
            pos += 2
    return out


if __name__ == "__main__":
    for t, v in callers({int(a, 0) for a in sys.argv[1:]}).items():
        print(hex(t), [hex(x) for x in v])
