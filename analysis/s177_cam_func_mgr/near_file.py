#!/usr/bin/env python3
"""S177 — para direcciones de código dadas, encuentra la referencia PIC más
cercana (hacia atrás, en un radio) a un nombre de fichero `.cpp` o a un nombre
de clase RTTI `N6Camera...`.

Uso: near_file.py <addr> [radio] ...
"""
import bisect
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
B = open(os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"), "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def cstr(a):
    o = a - BASE
    if o < 0 or o >= N:
        return None
    e = B.find(b"\x00", o)
    if e < 0 or e - o > 160:
        return None
    try:
        s = B[o:e].decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if all(32 <= ord(c) < 127 for c in s) else None


def pic_all(lo, hi):
    ldrs = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None and 0 <= lit - BASE <= N - 4:
            ldrs.append((a, reg, U32(B, lit - BASE)[0], lit))
        a += 2
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            reg = (((h >> 7) & 1) << 3) | (h & 7)
            v = by_reg.get(reg)
            if v:
                ks = keys[reg]
                i = bisect.bisect_left(ks, a) - 1
                if i >= 0:
                    la, w, lit = v[i]
                    if a - la <= 4096:
                        out.append((a, (w + a + 4) & 0xFFFFFFFF, reg))
        a += 2
    return out


LO, HI = 0x43780000, 0x43810000
allp = pic_all(LO, HI)
interesting = []
for a, dest, reg in allp:
    s = cstr(dest)
    if s and (s.endswith(".cpp") or s.endswith(".h") or s.startswith("N6Camera")
              or "Function/" in s or "wrapper/" in s or "tsk/" in s or "api/" in s):
        interesting.append((a, dest, s))

for arg in sys.argv[1:]:
    a = int(arg, 0)
    prev = [x for x in interesting if x[0] <= a]
    prev.sort()
    print(f"--- {a:#x}")
    for (pa, pd, ps) in prev[-3:]:
        print(f"     ref@{pa:#x} -> {pd:#x} {ps!r}   (delta {a - pa:+#x})")
