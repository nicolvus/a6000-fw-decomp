#!/usr/bin/env python3
"""adjscan.py DIS TARGET_HEX: accesos indirectos a base+TARGET vía `add rX, rY, #K` seguido (≤8 instr) de ld/st [rX, #o]
con K+o==TARGET (K≠TARGET o o≠0 incluido), y strd/ldrd que cubren TARGET. Heurístico (no sigue movs ni llamadas)."""
import re
import sys
from pathlib import Path

dis, T = sys.argv[1], int(sys.argv[2], 16)
adj = {}
for l in Path(dis).read_text().splitlines():
    m = re.match(r'([0-9a-f]{8}):\s+(\S+)\s*(.*)', l)
    if not m: continue
    a, op, arg = int(m.group(1), 16), m.group(2), re.sub(r'\s*<_binary[^>]*>|@.*', '', m.group(3)).strip()
    mm = re.match(r'(r\d+|r1[0-2]|lr), (r\d+), #(0x[0-9a-f]+)$', arg)
    if op.startswith('add') and mm:
        k = int(mm.group(3), 16)
        if 0 < k <= T: adj[mm.group(1)] = (a, k, 8)
        else: adj.pop(mm.group(1), None)
        continue
    m2 = re.match(r'(\S+), (?:(\S+), )?\[(r\d+|r1[0-2]), #(0x[0-9a-f]+)\]', arg)
    if m2 and (op.startswith(('ldr', 'str'))):
        base, o = m2.group(3), int(m2.group(4), 16)
        if base in adj:
            ad, k, _ = adj[base]
            span = 8 if op.endswith('d') or m2.group(2) else (4 if 'b' not in op[3:] and 'h' not in op[3:] else 2)
            if k + o <= T < k + o + span and k != 0: print(f'{a:#x} {op} {arg}  (base {base}=+{k:#x} @ {ad:#x})')
    for r in list(adj):
        ad, k, n = adj[r]
        if n <= 1 or re.match(rf'{r},', arg): adj.pop(r)
        else: adj[r] = (ad, k, n - 1)
