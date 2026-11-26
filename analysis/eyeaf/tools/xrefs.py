#!/usr/bin/env python3
"""Buscador de referencias (LE32) a una dirección en las secciones de datos/.text de un ELF ARM32.

Uso: xrefs.py BIN 0xADDR [0xADDR...]
Salida: dirección del literal, sección, símbolo que lo contiene (si lo hay).
"""
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from armdis import Bin


def main():
    b = Bin(sys.argv[1])
    targets = [int(x, 16) for x in sys.argv[2:]]
    for t in targets:
        pat = struct.pack('<I', t)
        print(f'== 0x{t:x} ({pat.hex()})')
        hits = 0
        data = b.data
        i = data.find(pat)
        while i != -1:
            va = None
            sec = None
            for name, (sva, soff, ssize) in b.SEC.items():
                if soff is None:
                    continue
                if soff <= i < soff + ssize:
                    va = sva + (i - soff)
                    sec = name
                    break
            if va is not None:
                owner = None
                best = -1
                for sa, nm in b.sym.items():
                    if sa <= va and sa > best and b.sym_size.get(sa, 0) > (va - sa):
                        best = sa
                        owner = nm
                print(f'   0x{va:08x} {sec:9s} owner={owner}')
                hits += 1
            i = data.find(pat, i + 1)
        if not hits:
            print('   (sin referencias literales)')


if __name__ == '__main__':
    main()
