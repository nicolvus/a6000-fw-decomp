"""R16: grafo de llamadas directas de Loader3 desde las raíces TPZL + constantes MMIO (0xf0..).

Heurística: una función termina en el siguiente `push` con lr (límite aproximado, sin REA).
Salida: r16-loader3-callgraph.json. Solo lectura.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

sys.path.insert(0, str(Path(__file__).parent))
from r16_dis import BASE_VA, BL, END_VA, FILE_OFF

DATA = BL.read_bytes()
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False


def u32(va: int) -> int:
    o = FILE_OFF + va - BASE_VA
    return struct.unpack_from("<I", DATA, o)[0]


def insns(va: int, limit: int = 0x600):
    """Instrucciones Thumb consecutivas desde `va` (sin seguir el flujo de control)."""
    out, pos = [], va
    while pos < min(va + limit, END_VA):
        chunk = DATA[FILE_OFF + pos - BASE_VA : FILE_OFF + pos - BASE_VA + 4]
        got = list(MD.disasm(chunk, pos, 1))
        if not got:
            pos += 2
            continue
        out.append(got[0])
        pos += got[0].size
    return out


def func_body(va: int):
    body: list = []
    started = False
    for i in insns(va, 0x800):
        if started and i.mnemonic.startswith("push") and "lr" in i.op_str and body:
            break
        started = True
        body.append(i)
    return body


def analyze(va: int):
    calls, consts = set(), set()
    for i in func_body(va):
        m = re.match(r"#(0x[0-9a-f]+)$", i.op_str)
        if i.mnemonic in ("bl", "blx", "b", "b.w") and m:
            t = int(m[1], 16)
            if i.mnemonic in ("bl", "blx"):
                calls.add(t & ~1)
        mm = re.match(r"(\w+), \[pc, #(0x[0-9a-f]+|\d+)\]$", f"{i.op_str}")
        if i.mnemonic.startswith("ldr") and mm:
            addr = ((i.address + 4) & ~3) + int(mm[2], 0)
            if BASE_VA <= addr < END_VA:
                consts.add(u32(addr))
    return calls, consts


def walk(roots, depth):
    seen: dict = {}
    frontier = [(r, 0) for r in roots]
    while frontier:
        va, d = frontier.pop(0)
        if va in seen or not BASE_VA <= va < END_VA:
            continue
        calls, consts = analyze(va)
        seen[va] = {
            "depth": d,
            "calls": sorted(calls),
            "mmio_consts": sorted(
                c for c in consts if 0xF0000000 <= c < 0xF3000000 or 0xFFF00000 <= c
            ),
        }
        if d < depth:
            frontier += [(c, d + 1) for c in sorted(calls)]
    return seen


if __name__ == "__main__":
    roots = [int(x, 16) for x in sys.argv[2:]] or [0xC01FE006, 0xC01FDD8E, 0xC01F2C2A]
    g = walk(roots, int(sys.argv[1]))
    for va, v in sorted(g.items()):
        print(
            f"{va:08x} d{v['depth']} calls={[f'{c:x}' for c in v['calls']]} mmio={[f'{c:x}' for c in v['mmio_consts']]}"
        )
