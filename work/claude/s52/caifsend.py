#!/usr/bin/env python3
"""caifsend.py DIS OFF: lista `movs r0,#EV ... ldr.w r1,[rX,#OFF] ... bl F` (envío CAIF: OFF=0xd8 A6000, 0xe8 A7S
sobre captura+0x4a00) con la función contenedora aproximada (último push)."""
import re
import sys
from pathlib import Path

dis, off = sys.argv[1], sys.argv[2]
win, lastpush = [], 0
for l in Path(dis).read_text().splitlines():
    m = re.match(r'([0-9a-f]{8}):\s+(\S+)\s*(.*)', l)
    if not m: continue
    a, op, arg = int(m.group(1), 16), m.group(2), re.sub(r'\s*<_binary[^>]*>', '', m.group(3))
    if op.startswith('push'): lastpush = a
    win = (win + [(a, op, arg)])[-5:]
    if op == 'bl' and any(o.startswith('ldr') and re.search(rf'r1, \[r\d+, #{off}\]', x) for _, o, x in win[:-1]):
        ev = [x for _, o, x in win[:-1] if o in ('movs', 'mov.w') and x.startswith('r0, #')]
        print(f'{a:#x} fn~{lastpush:#x} ev={ev[-1][4:] if ev else "?"} -> {arg.split()[0]}')
