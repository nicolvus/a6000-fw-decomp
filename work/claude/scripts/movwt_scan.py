#!/usr/bin/env python3
"""Busca pares Thumb-2 MOVW/MOVT (mismo Rd, ventana de 16 B) que cargan un valor dado.
Uso: movwt_scan.py BIN BASE VALOR_HEX [VALOR_HEX...]"""
import sys, struct
def dec(hw1, hw2, op):  # op 0x24=MOVW, 0x2c=MOVT; T3 encoding
    if (hw1 & 0xfbf0) != (0xf240 if op == 'w' else 0xf2c0) or hw2 & 0x8000: return None
    imm = ((hw1 & 0xf) << 12) | (((hw1 >> 10) & 1) << 11) | (((hw2 >> 12) & 7) << 8) | (hw2 & 0xff)
    return (hw2 >> 8) & 0xf, imm
d = open(sys.argv[1], 'rb').read(); base = int(sys.argv[2], 16)
targets = {int(v, 16) for v in sys.argv[3:]}
lo = {t & 0xffff: t for t in targets}
for i in range(0, len(d) - 4, 2):
    hw1, hw2 = struct.unpack_from('<HH', d, i)
    w = dec(hw1, hw2, 'w')
    if not w or w[1] not in lo: continue
    t = lo[w[1]]
    for j in range(i + 4, min(i + 20, len(d) - 4), 2):
        m = dec(*struct.unpack_from('<HH', d, j), 't')
        if m and m[0] == w[0] and m[1] == t >> 16:
            print(f"{t:#x} movw@{base+i:#x} movt@{base+j:#x} r{w[0]}")
