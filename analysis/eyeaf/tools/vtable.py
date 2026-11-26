#!/usr/bin/env python3
"""Vuelca una vtable y resuelve sus entradas contra .dynsym."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from armdis import Bin

if __name__ == '__main__':
    b = Bin(sys.argv[1])
    va = int(sys.argv[2], 16)
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    for i in range(n):
        w = b.read(va + 4 * i, 4)
        if not w:
            break
        v = struct.unpack('<I', w)[0]
        owner = ''
        best = -1
        for sa, nm in b.sym.items():
            if sa <= v and sa > best and b.sym_size.get(sa, 0) > (v - sa):
                best = sa
                owner = nm
        if v == 0:
            owner = '<0>'
        print(f'[{i:3d}] slot 0x{i*4:03x}  0x{v:08x}  {owner}')
