#!/usr/bin/env python3
"""guards.py DIS F1,F2,...: para cada `bl F` lista el llamador y si en las 8 instrucciones previas hay acceso a +0x748/+0x78c (A7S)
o +0x740 (A6000)."""
import re
import sys
from pathlib import Path

dis, fs = sys.argv[1], sys.argv[2].split(',')
win = []
for l in Path(dis).read_text().splitlines():
    m = re.match(r'\s*([0-9a-f]{8}):\s+(\S+)\s*(.*)', l)
    if not m: continue
    a, op, arg = m.group(1), m.group(2), re.sub(r'\s*<_binary[^>]*>', '', m.group(3))
    if op in ('bl', 'b.w') and arg.split()[0] in fs:
        g = [f'{x[0]}:{x[1]} {x[2]}' for x in win if re.search(r'#0x(748|78c|740)\]', x[2])]
        print(f'{a} {op} {arg.split()[0]}  guard={g}')
    win = (win + [(a, op, arg)])[-8:]
