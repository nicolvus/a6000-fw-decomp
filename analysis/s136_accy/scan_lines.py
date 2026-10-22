#!/usr/bin/env python3
"""S136 — numero de linea de fuente embebido en cada traza `[ACCY]`.

En este firmware el primer `%d` de la mayoria de las trazas es el *numero de linea*
del fichero fuente: el codigo hace `movs r3,#<linea>` y lo pasa en la pila como
primer argumento variadico. Este script extrae ese valor para cada sitio de
emision, desensamblando hacia atras desde el `add rX,pc`.

Uso: .venv/bin/python analysis/s136_accy/scan_lines.py
"""
import json
import os
import struct
from collections import defaultdict

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
U16 = struct.Struct("<H").unpack_from


def main():
    data = open(BIN, "rb").read()
    raw = json.load(open(os.path.join(HERE, "accy_raw.json")))
    out = []
    for s in raw["strings"]:
        for site in s["sites"]:
            # hacia atras desde el sitio: el numero de linea se carga con
            # `movs r3,#N` (16 bits) o `movw r3,#N` (32 bits) y se pasa por la
            # pila (`str r3,[sp]` / `stm.w sp,{r3..}`)
            found = None
            addr = site
            for _ in range(40):
                addr -= 2
                if addr < BASE:
                    break
                off = addr - BASE
                h = U16(data, off)[0]
                line = None
                nxt_addr = addr + 2
                if (h & 0xFF00) == 0x2300 and ((h >> 8) & 7) == 3:
                    line = h & 0xFF
                elif (h & 0xFBF0) == 0xF240 and off + 4 <= len(data):
                    h2 = U16(data, off + 2)[0]
                    if ((h2 >> 8) & 0xF) == 3:
                        i = (h >> 10) & 1
                        imm4 = h & 0xF
                        imm3 = (h2 >> 12) & 7
                        imm8 = h2 & 0xFF
                        line = (imm4 << 12) | (i << 11) | (imm3 << 8) | imm8
                        nxt_addr = addr + 4
                if line is None:
                    continue
                # el valor se pasa por la pila: `str r3,[sp]` o `stm.w sp,{r3..}`
                stashed = False
                probe = nxt_addr - BASE
                for _ in range(7):
                    if probe + 2 > len(data):
                        break
                    nxt = U16(data, probe)[0]
                    if nxt == 0x9300 or ((nxt & 0xF800) == 0xE800 and (nxt & 0x0008)):
                        stashed = True
                        break
                    probe += 2
                if stashed:
                    found = {"addr": f"0x{addr:x}", "line": line}
                    break
            out.append({"str": s["vaddr"], "site": f"0x{site:x}",
                        "text": s["text"], "line": found})
    # agrupar por sub-bloque y comprobar monotonía
    bysub = defaultdict(list)
    for e in out:
        sub = e["text"].split("]")[2].lstrip("[")
        bysub[sub].append(e)
    print(f"{'sub':<9} {'n':>3} {'lineas (site:line)'}")
    for sub, lst in bysub.items():
        lst.sort(key=lambda e: int(e["site"], 16))
        ss = ", ".join(f"{e['site'][2:]}:"
                       f"{e['line']['line'] if e['line'] else '-'}" for e in lst)
        print(f"{sub:<9} {len(lst):>3}  {ss}")
    json.dump(out, open(os.path.join(HERE, "accy_lines.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
