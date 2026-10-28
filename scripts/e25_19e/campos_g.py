#!/usr/bin/env python3
"""E25-19e P3 — accesos a G+0x60/+0x7e/+0x7f (G=[0x4402546c]=0x43e95950, desplazamiento GOT 0x6588).

Busca `ldr rX,[pc,#]` cuyo literal vale 0x6588, el `ldr rY,[rPIC,rX]` siguiente (puntero G) y, en una ventana de instrucciones,
accesos [rY,#off] con off en CAMPOS. Salida: analysis/e25-19e/campos-g.json
"""
from __future__ import annotations

import json
import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000
GOT_OFF = 0x6588
CAMPOS = {0x60, 0x7E, 0x7F}
VENT = 260


def desensamblar(data: bytes) -> list:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    ins, pos = [], 0
    while pos < len(data) - 4:
        got = False
        for i in md.disasm(data[pos:pos + 4], BASE + pos, 1):
            ins.append(i)
            pos += i.size
            got = True
        if not got:
            pos += 2
    return ins


def accesos(data: bytes) -> list[dict]:
    ins = desensamblar(data)
    out = []
    for k, i in enumerate(ins):
        m = re.match(r"(\w+), \[pc, #(0x[0-9a-f]+)\]", i.op_str)
        if i.mnemonic not in ("ldr", "ldr.w") or not m:
            continue
        lit = (((i.address + 4) & ~3) + int(m.group(2), 0)) - BASE
        if lit + 4 > len(data) or struct.unpack_from("<I", data, lit)[0] != GOT_OFF:
            continue
        rx, rg = m.group(1), None
        for j in ins[k + 1:k + 8]:
            m2 = re.match(rf"(\w+), \[(\w+), {rx}\]", j.op_str)
            if j.mnemonic.startswith("ldr") and m2:
                rg = m2.group(1)
                inicio = j
                break
        if not rg:
            continue
        for j in ins[ins.index(inicio) + 1:ins.index(inicio) + VENT]:
            if j.mnemonic.startswith("push") and "lr" in j.op_str:
                break
            m3 = re.search(rf"\[{rg}, #(0x[0-9a-f]+)\]", j.op_str)
            if m3 and int(m3.group(1), 0) in CAMPOS:
                out.append({"ldr_got": hex(i.address), "addr": hex(j.address), "campo": hex(int(m3.group(1), 0)),
                            "tipo": "W" if j.mnemonic.startswith("str") else "R", "ins": f"{j.mnemonic} {j.op_str}"})
    return out


if __name__ == "__main__":
    r = accesos(BIN.read_bytes())
    (ROOT / "analysis/e25-19e/campos-g.json").write_text(json.dumps(r, indent=1) + "\n")
    for x in r:
        print(x["addr"], x["tipo"], x["campo"], x["ins"])
