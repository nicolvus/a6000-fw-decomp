#!/usr/bin/env python3
"""Referencias a cadenas/datos desde codigo Thumb de libmpr.so.

1. busca en .text las palabras (pool de literales) iguales al valor pedido;
2. para cada una, retrocede hasta 0xFFF B buscando el `ldr rX,[pc,#imm]` que la carga.
Uso: strref.py 0x81c742 0x81c85e ...
"""
import sys

sys.path.insert(0, "reports/evidence/fbm-sector31-consola-20261126/evidencia")
import mprdis as M
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

TEXT = M.sec(".text")
code = M.rd(TEXT[0], TEXT[1] - TEXT[0])
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def find_loader(match_va):
    out = []
    # todos los offsets 4-alineados del .text que contienen el valor
    for off in range(0, len(code) - 4, 2):
        if int.from_bytes(code[off:off + 4], "little") != match_va:
            continue
        pool = TEXT[0] + off
        for back in range(2, 0x1000, 2):
            a = pool - back
            if a < TEXT[0]:
                break
            ins = next(md.disasm(M.rd(a, 4), a), None)
            if not ins or ins.mnemonic != "ldr" or "[pc," not in ins.op_str:
                continue
            try:
                imm = int(ins.op_str.split("#")[-1].rstrip("]"), 0)
            except ValueError:
                continue
            if ((ins.address + 4) & ~3) + imm == pool:
                out.append((a, ins.op_str))
    return out


for arg in sys.argv[1:]:
    va = int(arg, 0)
    if va < TEXT[0] or va >= TEXT[0] + len(code):
        print(f"{va:#x}: fuera de .text")
        continue
    refs = find_loader(va)
    s = M.cstr(va) or ""
    print(f"{va:#x} \"{s}\": {len(refs)} refs -> " +
          ", ".join(f"{a:#x}({op})" for a, op in refs[:8]))
