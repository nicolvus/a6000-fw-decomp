#!/usr/bin/env python3
"""Busca llamadas/ramas directas (BL, BLX, B.W) a direcciones dadas decodificando
TODAS las ventanas de 4 bytes alineadas a 2 en la imagen (independiente del sincronismo
del barrido lineal). Solo análisis estático.

Uso: blfind.py 0x437b6670 0x43a06428 ...
"""
import sys

BASE = 0x43541000
BIN = ('/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter'
       '/analysis/rea-independent/input/av-cam.bin')
D = open(BIN, 'rb').read()


def sx(v, bits):
    m = 1 << (bits - 1)
    return (v & (m - 1)) - (v & m)


def decode(hw0, hw1, addr):
    """Devuelve (kind, target) si la ventana es BL/BLX/B.W, si no None."""
    if (hw0 & 0xF800) == 0xF000 and (hw1 & 0x8000) == 0x8000:
        s = (hw0 >> 10) & 1
        imm10 = hw0 & 0x3FF
        j1 = (hw1 >> 13) & 1
        j2 = (hw1 >> 11) & 1
        imm11 = hw1 & 0x7FF
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
        imm = sx(imm, 25)
        if (hw1 & 0xD000) == 0xD000:      # BLX (imm10H/imm10L)
            return ('blx', addr + 4 + imm)
        if (hw1 & 0xD000) == 0x9000:      # B.W T4
            return ('b.w', addr + 4 + imm)
        if (hw1 & 0xD000) == 0x8000:      # BL T1
            return ('bl', addr + 4 + imm)
    if (hw0 & 0xF800) == 0xE000:          # B T2 (16-bit)
        imm = sx((hw0 & 0x7FF) << 1, 12)
        return ('b', addr + 4 + imm)
    return None


def main(targets):
    want = set(targets)
    hits = {t: [] for t in targets}
    n = len(D)
    for off in range(0, n - 4, 2):
        addr = BASE + off
        hw0 = int.from_bytes(D[off:off + 2], 'little')
        hw1 = int.from_bytes(D[off + 2:off + 4], 'little')
        r = decode(hw0, hw1, addr)
        if r is None:
            continue
        kind, tgt = r
        if tgt in want:
            hits[tgt].append((addr, kind))
    for t in targets:
        print(f'== {t:#010x}: {len(hits[t])}')
        for a, k in hits[t][:12]:
            print(f'   {a:#010x} {k}')


if __name__ == '__main__':
    main([int(a, 16) for a in sys.argv[1:]])
