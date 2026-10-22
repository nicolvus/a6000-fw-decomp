#!/usr/bin/env python3
"""S118 — protocolo de control de `[SFRA]`: tabla comando → predicado de mensaje.

En `ScalarInfraAsyncMain` (`0x439a1864`) el bucle principal consulta, para cada
comando, una función-predicado de la familia `0x43b63xxx` (¿es este mensaje de
tipo X?); si la respuesta es positiva imprime la traza `[SFRA][CMD] ***...***` o
`[SFRA][CMP] ***...***` con su número de línea.

Este script empareja cada predicado con la traza que protege y saca la lista
ordenada de predicados (que es la enumeración de tipos de mensaje).
"""
import json
import os
import re
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_sfra import BASE, BIN  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = 0x439A1864
END = 0x439A1E00


def main():
    data = open(BIN, "rb").read()
    smap = {}
    p = os.path.join(HERE, "site_best.json")
    for s, lst in json.load(open(p)).items():
        smap[int(s, 16)] = int(lst[0], 16)

    def cstr(va):
        off = va - BASE
        end = off
        while end < len(data) and 32 <= data[end] < 127:
            end += 1
        return data[off:end].decode("latin1")

    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    rows = []
    pred = None
    line = None
    fname = None
    for ins in md.disasm(data[MAIN - BASE:END - BASE], MAIN):
        if ins.mnemonic == "bl":
            t = int(ins.op_str.lstrip("#"), 16)
            if 0x43B63000 <= t < 0x43B64000:
                pred = t
        if ins.mnemonic == "movs" and re.match(r"r1, #0x[0-9a-f]+$", ins.op_str):
            v = int(ins.op_str.split("#")[1], 16)
            if 0x40 <= v <= 0x200:
                line = v
        tgt = smap.get(ins.address)
        if tgt is None:
            continue
        txt = cstr(tgt)
        if "***" in txt:
            rows.append({"pred": f"0x{pred:x}" if pred else None,
                         "line": line, "vaddr": f"0x{tgt:x}", "text": txt})
            pred = None
    for r in rows:
        print(f"pred={r['pred']}  linea={r['line']}  {r['vaddr']}  {r['text']}")
    json.dump(rows, open(os.path.join(HERE, "protocol_main.json"), "w"), indent=1,
              ensure_ascii=False)


if __name__ == "__main__":
    main()
