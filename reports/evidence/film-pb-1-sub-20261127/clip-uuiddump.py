#!/usr/bin/env python3
"""Volcado hex de las cajas uuid de Sony y del esds de audio."""
import sys

d = open(sys.argv[1], 'rb').read()


def hx(o, n, tag):
    b = d[o:o + n]
    print("--- %s off=%d len=%d" % (tag, o, n))
    for i in range(0, n, 16):
        ch = b[i:i + 16]
        asc = ''.join(chr(c) if 32 <= c < 127 else '.' for c in ch)
        print("  %9d %-48s %s" % (o + i, ch.hex(' '), asc))


for off, ln, tag in [
    (28, 148, 'uuid PROF top-level'),
    (14543023, 52, 'uuid USMT en trak video'),
    (14545598, 52, 'uuid USMT en trak audio'),
    (14545650, 46, 'uuid USMT en moov (cola)'),
    (14543423, 39, 'esds mp4a'),
    (14543462, 24, 'stts audio'),
]:
    hx(off, ln, tag)
