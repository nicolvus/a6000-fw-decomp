#!/usr/bin/env python3
"""Llamadores directos (bl/blx/b.w a destino fijo) de av-cam.bin por barrido Thumb-2. Uso: ADDR [ADDR...]."""
from __future__ import annotations

import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BIN = Path(__file__).resolve().parents[1] / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000


def callers(data: bytes, targets: set[int]) -> dict[int, list[int]]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    res: dict[int, list[int]] = {t: [] for t in targets}
    pos = 0
    while pos < len(data) - 4:
        n = 0
        for i in md.disasm(data[pos:pos + 0x4000], BASE + pos):
            n = i.address + i.size - BASE
            if i.mnemonic in ("bl", "blx", "b.w", "b") and i.op_str.startswith("#"):
                t = int(i.op_str[1:], 0)
                if t in res:
                    res[t].append(i.address)
        pos = max(n, pos + 2) if n else pos + 2
    return res


if __name__ == "__main__":
    tg = {int(a, 16) & ~1 for a in sys.argv[1:]}
    for t, v in callers(BIN.read_bytes(), tg).items():
        print(f"{t:#x}: " + " ".join(f"{x:#x}" for x in v))
