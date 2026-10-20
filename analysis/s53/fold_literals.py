"""Sustituye _DAT_<dir ROM> del volcado Ghidra por el valor literal de la ROM original (solo lectura)."""
import re
import sys
from pathlib import Path

from dz import BASE, rom, u32

name = sys.argv[1]
d = rom(name)
src = Path(f'ghidra/{name}-decomp.c').read_text(encoding='utf-8')


def rep(m):
    a = int(m.group(1), 16)
    if BASE <= a < BASE + len(d) - 3:
        return f'L_{u32(d, a):x}'
    return m.group(0)


Path(f'ghidra/{name}-decomp-folded.c').write_text(encoding='utf-8', data=re.sub(r'_?DAT_([0-9a-f]{8})', rep, src))
