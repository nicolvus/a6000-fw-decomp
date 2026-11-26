"""Indexa parejas movw/movt (Thumb-2) para resolver xrefs a datos en binarios ARM PIC."""
import struct
from collections import defaultdict

def scan(data, base):
    movw = defaultdict(list)   # imm16 -> [(va, reg)]
    movt = defaultdict(list)
    n = len(data)
    for off in range(0, n - 4, 2):
        hw1 = data[off] | (data[off+1] << 8)
        t = hw1 & 0xFFF0
        if t not in (0xF240, 0xF640, 0xF2C0, 0xF6C0):
            continue
        hw2 = data[off+2] | (data[off+3] << 8)
        imm4 = hw1 & 0xF
        i = 1 if (hw1 & 0x0400) else 0
        imm3 = (hw2 >> 12) & 0x7
        rd = (hw2 >> 8) & 0xF
        imm8 = hw2 & 0xFF
        imm16 = (imm4 << 12) | (i << 11) | (imm3 << 8) | imm8
        va = base + off
        if t in (0xF240, 0xF640):
            movw[imm16].append((va, rd))
        else:
            movt[imm16].append((va, rd))
    return movw, movt

def xrefs(movw, movt, target, window=24):
    lo = target & 0xffff
    hi = (target >> 16) & 0xffff
    out = []
    for a_t, r_t in movt.get(hi, ()):
        for a_w, r_w in movw.get(lo, ()):
            if r_w == r_t and a_w < a_t and a_t - a_w <= window:
                out.append((a_w, a_t, r_t))
    return sorted(set(out))
