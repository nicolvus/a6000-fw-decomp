#!/usr/bin/env python3
"""ctx.py DIS ADDR[,ADDR...] [antes] [despues] -> contexto del desensamblado lineal LLVM (s52/dis/*.dis)."""
import bisect
import re
import sys
from pathlib import Path

dis, addrs = sys.argv[1], [int(a, 16) for a in sys.argv[2].split(',')]
b, a = (int(sys.argv[3]) if len(sys.argv) > 3 else 8), (int(sys.argv[4]) if len(sys.argv) > 4 else 8)
lines = Path(dis).read_text().splitlines()
keys = [int(m.group(1), 16) if (m := re.match(r'\s*([0-9a-f]{4,8}):', l)) else -1 for l in lines]
idx = [i for i, k in enumerate(keys) if k >= 0]; ks = [keys[i] for i in idx]
for ad in addrs:
    j = idx[bisect.bisect_left(ks, ad)]
    print(f'== {ad:#x}')
    for l in lines[max(0, j - b):j + a + 1]:
        print(re.sub(r'\s*<_binary[^>]*>', '', l).replace('\t', ' ').replace('      ', ' '))
