#!/usr/bin/env python3
"""Compara las dos copias fisicas de la tabla de pares (VA 0x9D23FC) con el .so."""
import struct
so = open('analysis/camera-extract/usr/lib/libmpr.so', 'rb').read()
ram = open('analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin', 'rb')
DATA_VA, DATA_OFF = 0x9C42E8, 0x9BC2E8
img = so[DATA_OFF+(0x9D23FC-DATA_VA):DATA_OFF+(0x9D23FC-DATA_VA)+37*0x18]
for base in (0x88F3A3FC, 0x8BB3E3FC):
    ram.seek(base-0x80000000); d = ram.read(37*0x18)
    print('copia 0x%08X (va&0xFFF=0x%03X)' % (base, base & 0xFFF))
    n = 0
    for i in range(37):
        a, b = img[i*0x18:(i+1)*0x18], d[i*0x18:(i+1)*0x18]
        if a != b:
            n += 1
            pa, pb = struct.unpack('<6I', a), struct.unpack('<6I', b)
            print('  fila %2d (userID=0x%02X mediaID=%d sector=0x%02X): .so +0x10=0x%08X +0x14=0x%08X | RAM +0x10=0x%08X +0x14=0x%08X'
                  % (i, pa[0], pa[1], pa[2], pa[4], pa[5], pb[4], pb[5]))
    print('  filas distintas del .so: %d' % n)
