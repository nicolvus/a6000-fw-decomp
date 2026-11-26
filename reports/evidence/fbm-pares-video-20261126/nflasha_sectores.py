#!/usr/bin/env python3
"""Censo de los 30 sectores FBM (lista 0x9D2380) en la particion nflasha4.
Sector FBS = 1 KiB; +0x00 u32 estado, +0x04 firma 0x004A004A, +0x08 registros de 8 B
{u32 longitud, u8,u8,u8,0xFF}, trailer "draCNV4'" en +0x3AB.
"""
import struct, re
D = 'analysis/camera-dumps/nand-20261020/dev_nflasha4.bin'
SECT = 1024
LISTA = [0x10,0x11,0x12,0x20,0x21,0x28,0x29,0x2c,0x2d,0x30,0x31,0x38,0x39,0x40,0x60,
         0x61,0x68,0x6c,0x62,0x63,0x90,0x91,0x92,0xa0,0xb1,0xb2,0xb3,0xb8,0xbc,0xbd]
HANDLE = {0x30:4, 0x62:3, 0xa0:1, 0xb2:5}

d = open(D, 'rb').read()
tot = len(d) // SECT
blank = sum(1 for i in range(tot) if d[i*SECT:(i+1)*SECT] == b'\xff'*SECT)
print('%s: %d sectores de %d B; totalmente 0xFF = %d; no blancos = %d'
      % (D, tot, SECT, blank, tot-blank))
print('sector  offset   estado      firma       registros (u32 longitud + 4 flags)            handle')
for s in LISTA:
    sec = d[s*SECT:(s+1)*SECT]
    st, sig = struct.unpack_from('<I', sec, 0)[0], struct.unpack_from('<I', sec, 4)[0]
    recs = []
    for i in range(120):
        r = sec[8+i*8:16+i*8]
        if r == b'\xff'*8:
            break
        recs.append('%08x' % struct.unpack_from('<I', r, 0)[0] + '/' + r[4:].hex())
    print('0x%02X    0x%06X  0x%08X  0x%08X  %-46s %s'
          % (s, s*SECT, st, sig, ' '.join(recs[:6]), HANDLE.get(s, '-')))

print()
print("rutas legibles ('ms:/') en la particion:")
i = 0
while True:
    j = d.find(b'ms:/', i)
    if j < 0:
        break
    print('  0x%07X sector 0x%04X: %r' % (j, j//SECT, d[j:j+40].split(b'\0')[0].decode('latin1')))
    i = j + 1
