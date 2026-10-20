#!/usr/bin/env python3
"""nearid.py DIS TRACE OFF: para cada ld/st [rX,#OFF] (no pc) da el ID de traza previo más cercano (mov r1,#ID; bl TRACE)."""
import re
import sys
from pathlib import Path

dis, tr, off = sys.argv[1], sys.argv[2], sys.argv[3]
last, prev = None, []
for l in Path(dis).read_text().splitlines():
    m = re.match(r'([0-9a-f]{8}):\s+(\S+)\s*(.*)', l)
    if not m: continue
    a, op, arg = int(m.group(1), 16), m.group(2), m.group(3)
    if op == 'bl' and arg.startswith(tr):
        for pa, pop, parg in reversed(prev[-3:]):
            mm = re.match(r'r1, #(0x[0-9a-f]+|\d+)$', parg)
            if mm: last = (int(mm.group(1), 0), a); break
    if re.search(rf'\[r\d+, #{off}\]', arg) and 'pc' not in arg and op.startswith(('ldr', 'str')):
        print(f'{a:#x} {op} {arg.split(",")[0]} id={hex(last[0]) if last else None} d={a-last[1] if last else -1:#x}')
    prev = (prev + [(a, op, arg)])[-4:]
