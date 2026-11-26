#!/usr/bin/env python3
"""Consulta: para cada patrón de texto, lista copias en .rodata y sitios de código que las
materializan (según libobj_strxref.json), con el símbolo .dynsym que los contiene.
Solo estático."""
import json, subprocess, sys, re, os

PATH = os.environ.get('LIBOBJ', 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so')
XREF = 'analysis/eyeaf/data/libobj_strxref.json'
data = open(PATH, 'rb').read()
xr = json.load(open(XREF))

def syms():
    out = subprocess.run(['readelf', '-sW', PATH], capture_output=True, text=True).stdout
    S = []
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 8 and f[3] in ('FUNC', 'OBJECT', 'IFUNC') and f[1] != '00000000':
            try: a = int(f[1], 16)
            except ValueError: continue
            try: n = int(f[2])
            except ValueError: n = 0
            S.append((a & ~1, n, f[7]))
    S.sort()
    return S
SYM = syms()

def owner(va):
    lo, hi = 0, len(SYM) - 1
    best = None
    for a, n, nm in SYM:
        if a <= va and (n == 0 or va < a + n):
            if best is None or a >= best[0]: best = (a, n, nm)
    return best

def copies(text):
    b = text.encode()
    i = data.find(b); out = []
    while i != -1:
        out.append(i)
        i = data.find(b, i + 1)
    return out

for pat in sys.argv[1:]:
    ptr = pat.replace('\\n', '\n')
    print(f'### {pat}')
    for off in copies(ptr):
        key = hex(off)
        sites = xr.get(key, [])
        ow = owner(next(iter(sites))) if sites else None
        print(f'  copy 0x{off:x} refs={[hex(s) for s in sites]} fn={("0x%x %s" % (ow[0], ow[2])) if ow else None}')
