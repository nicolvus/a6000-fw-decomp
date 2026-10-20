#!/usr/bin/env python3
"""traceid.py: indexa llamadas de traza de captura `mov r1,#ID; bl TRACE` (A7S TRACE=0x43ae826e, A6000 0x43ae769a)
y empareja funciones A7S/A6000 por ID. Uso: traceid.py [ID_HEX...] (sin args: tabla completa en JSON)."""
import json
import re
import sys
from pathlib import Path

D = '/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/work/claude/s52/dis/'
def idx(f, tr):
    res, prev = {}, []
    for l in Path(D + f).read_text().splitlines():
        m = re.match(r'([0-9a-f]{8}):\s+(\S+)\s*(.*)', l)
        if not m: continue
        a, op, arg = int(m.group(1), 16), m.group(2), m.group(3)
        if op == 'bl' and arg.startswith(tr):
            for pa, pop, parg in reversed(prev[-3:]):
                mm = re.match(r'r1, #(0x[0-9a-f]+|\d+)$', parg)
                if pop in ('movs', 'mov.w', 'movw', 'mov') and mm:
                    res.setdefault(int(mm.group(1), 0), []).append(a); break
        prev.append((a, op, arg)); prev = prev[-4:]
    return res
a7, a6 = idx('a7s.dis', '0x43ae826e'), idx('a6000.dis', '0x43ae769a')
ids = [int(x, 16) for x in sys.argv[1:]] or sorted(set(a7) | set(a6))
print(json.dumps({hex(i): {'a7s': [hex(x) for x in a7.get(i, [])], 'a6000': [hex(x) for x in a6.get(i, [])]} for i in ids}))
