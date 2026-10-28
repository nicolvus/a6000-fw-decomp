#!/usr/bin/env python3
"""E25-19d P0 — barrido Thumb-2 de av-cam.bin: accesos a offsets que cubren cap+0x74f (0x74c..0x74f) y construcciones de la constante.

Salida: analysis/e25-19d/barrido-74f.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000
OFFS = {0x74C, 0x74D, 0x74E, 0x74F}
RE_MEM = re.compile(r"\[(\w+), #(-?0x[0-9a-f]+|-?\d+)\]")


def barrido(data: bytes) -> list[dict]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    res = []
    pos = 0
    while pos < len(data) - 4:
        got = False
        for i in md.disasm(data[pos:pos + 4], BASE + pos, 1):
            got = True
            m = RE_MEM.search(i.op_str)
            if i.mnemonic.startswith(("str", "ldr")) and m and int(m.group(2), 0) in OFFS:
                res.append({"addr": i.address, "tipo": "mem", "ins": f"{i.mnemonic} {i.op_str}"})
            elif i.mnemonic in ("movw", "mov.w", "add.w", "addw", "adds.w", "orr.w") and re.search(r"#(0x74[cdef]|18[67]\d)\b", i.op_str):
                res.append({"addr": i.address, "tipo": "const", "ins": f"{i.mnemonic} {i.op_str}"})
            pos += i.size
        if not got:
            pos += 2
    return res


if __name__ == "__main__":
    r = barrido(BIN.read_bytes())
    out = ROOT / "analysis/e25-19d/barrido-74f.json"
    out.write_text(json.dumps([{**x, "addr": hex(x["addr"])} for x in r], indent=1) + "\n")
    for x in r:
        print(hex(x["addr"]), x["tipo"], x["ins"])
