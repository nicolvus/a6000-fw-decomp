#!/usr/bin/env python3
"""S118 — ids numéricos asociados a cada comando de `[SFRA]`.

Para cada traza de comando (`***...***`) localiza los sitios PIC que la
referencian, delimita la función que los contiene y busca la constante
inmediata movida a r1/r2 justo antes del `add rX, pc` (el id que acompaña al
nombre del comando en la llamada de registro).
"""
import json
import os
import re
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_sfra import (BASE, BIN, CODE_HI, CODE_LO, CMD_RE, extract,  # noqa: E402
                          function_ranges, site_to_func)

HERE = os.path.dirname(os.path.abspath(__file__))


def prev_consts(data, addr, back=48):
    """Inmediatos movidos a r1/r2/r3 en las ~`back` bytes anteriores a addr."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    start = addr - back
    out = []
    off = start - BASE
    for ins in md.disasm(data[off:off + back], start):
        if ins.address >= addr:
            break
        if ins.mnemonic in ("movs", "mov", "movw"):
            m = re.match(r"r([0-9]+), #(-?0x[0-9a-fA-F]+|-?\d+)", ins.op_str)
            if m:
                reg = int(m.group(1))
                val = int(m.group(2), 0)
                out.append((ins.address, reg, val))
    return out


def main():
    data = open(BIN, "rb").read()
    strings = extract(data)
    refs = json.load(open(os.path.join(HERE, "pic_refs.json")))
    ranges = function_ranges(data, CODE_LO, CODE_HI)
    rows = []
    for s in strings:
        m = CMD_RE.search(s["text"])
        if not m:
            continue
        sites = refs.get(s["vaddr"], [])
        for site in sites:
            f = site_to_func(site, ranges)
            consts = prev_consts(data, site)
            imm = None
            reg = None
            for a, r, v in reversed(consts):
                if r in (1, 2, 3):
                    imm, reg = v, r
                    break
            rows.append({"name": m.group(1), "text": s["text"], "vaddr": s["vaddr"],
                         "site": f"0x{site:x}", "func": f"0x{f:x}",
                         "imm": imm, "reg": reg,
                         "consts": [f"r{c[1]}=0x{c[2]:x}@{c[0]:#x}" for c in consts[-4:]]})
    json.dump(rows, open(os.path.join(HERE, "cmd_ids.json"), "w"), indent=1, ensure_ascii=False)
    for r in rows:
        print(f"{r['name']:<28} {r['vaddr']} site={r['site']} func={r['func']} "
              f"r{r['reg']}=0x{r['imm']:x}" if r["imm"] is not None else
              f"{r['name']:<28} {r['vaddr']} site={r['site']} func={r['func']} (sin const)")


if __name__ == "__main__":
    main()
