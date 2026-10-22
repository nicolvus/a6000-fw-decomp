#!/usr/bin/env python3
"""S177 — calcula el destino de TODOS los `add rX,pc` (esquema PIC) y busca
destinos concretos (no sólo inicios de cadena).

Uso: find_pic_targets.py <dest1> [dest2 ...] [fw]
"""
import bisect
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
FILES = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
args = sys.argv[1:]
fw = "A6000"
if args and args[-1] in FILES:
    fw = args.pop()
targets = {int(a, 0) for a in args}
B = open(os.path.join(ROOT, FILES[fw]), "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from

ldr = []
adds = []
a = BASE
while a < BASE + N:
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
        ldr.append((a, reg, U32(B, lit - BASE)[0], lit))
    if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
        adds.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
    a += 2

by_reg = {}
for a_, reg, w, lit in ldr:
    by_reg.setdefault(reg, []).append((a_, w, lit))
for v in by_reg.values():
    v.sort()
keys = {r: [x[0] for x in v] for r, v in by_reg.items()}

found = {t: [] for t in targets}
for a_, reg in adds:
    v = by_reg.get(reg)
    if not v:
        continue
    ks = keys[reg]
    i = bisect.bisect_left(ks, a_) - 1
    if i < 0:
        continue
    la, w, lit = v[i]
    if a_ - la > 4096:
        continue
    dest = (w + (a_ + 4)) & 0xFFFFFFFF
    if dest in found:
        found[dest].append((a_, la, lit, w))
for t in sorted(targets):
    print(f"{t:#x}: {len(found[t])} referencias PIC")
    for a_, la, lit, w in found[t]:
        print(f"    add@{a_:#x} ldr@{la:#x} pool@{lit:#x} W={w:#x}")
