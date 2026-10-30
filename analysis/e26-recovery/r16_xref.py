"""R16: referencias a direcciones dentro del prefijo de Loader3 (literales de 32 bits y adr/ldr pc-relativo)."""

from __future__ import annotations

import re
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from r16_callgraph import BASE_VA, DATA, END_VA, FILE_OFF

MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def xrefs(targets: set[int]) -> list[str]:
    """Instrucciones que cargan (literal o adr) o saltan a alguno de `targets` (rango ±0)."""
    lit = {}
    for va in range(BASE_VA, END_VA, 4):
        v = struct.unpack_from("<I", DATA, FILE_OFF + va - BASE_VA)[0]
        if v in targets:
            lit[va] = v
    out = []
    for va in range(BASE_VA, END_VA - 4, 2):
        i = next(
            MD.disasm(
                DATA[FILE_OFF + va - BASE_VA : FILE_OFF + va - BASE_VA + 4], va, 1
            ),
            None,
        )
        if not i or i.size == 0:
            continue
        m = re.search(r"\[pc, #(0x[0-9a-f]+|\d+)\]$|^\w+, #(0x[0-9a-f]+)$", i.op_str)
        if i.mnemonic.startswith(("ldr", "adr")) and m:
            if i.mnemonic.startswith("adr"):
                t = ((va + 4) & ~3) + int(m[2], 0)
                if any(t <= x < t + 1 for x in targets):
                    out.append(f"{va:08x}: {i.mnemonic} {i.op_str} -> {t:08x}")
                continue
            addr = ((va + 4) & ~3) + int(m[1], 0)
            if addr in lit:
                out.append(
                    f"{va:08x}: {i.mnemonic} {i.op_str} -> lit@{addr:08x}={lit[addr]:08x}"
                )
        if i.mnemonic in ("bl", "blx", "b", "b.w"):
            mm = re.match(r"#(0x[0-9a-f]+)$", i.op_str)
            if mm and int(mm[1], 16) in targets:
                out.append(f"{va:08x}: {i.mnemonic} {i.op_str}")
    return out


if __name__ == "__main__":
    for line in xrefs({int(x, 16) for x in sys.argv[1:]}):
        print(line)
