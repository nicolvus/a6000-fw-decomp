#!/usr/bin/env python3
"""Vuelca la tabla de pares (userID,mediaID)->sector de libmpr (VA 0x9D23FC, filas de 0x18)
y la cruza con la lista de sectores 0x9D2380 (30 u32) y la Sector Manager Info Table
0xA3699C (30 entradas de 0x14) leida del RAM dump real.

VA -> fisico: el volcado es RAM fisica; las paginas file-backed de libmpr aparecen
sueltas, pero el offset dentro de pagina se conserva (va & 0xFFF == fisico & 0xFFF).
"""
import struct, sys

SO  = 'analysis/camera-extract/usr/lib/libmpr.so'
RAM = 'analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin'
DATA_VA, DATA_OFF = 0x9C42E8, 0x9BC2E8      # seccion .data en el ELF

so = open(SO, 'rb').read()
ram = open(RAM, 'rb')

def va2off(va):                     # VA de .data -> offset en el .so
    return DATA_OFF + (va - DATA_VA)

def rd(va, n):                      # fisico -> bytes del volcado
    ram.seek(va - 0x80000000)
    return ram.read(n)

# ---- paginas fisicas que contienen cada estructura (buscadas por contenido) ----
def image_of(va, n):
    return so[va2off(va):va2off(va) + n]

def find_pages(va, n):
    pat = image_of(va, n)
    hits, CH, prev, off = [], 1 << 24, b'', 0
    ram.seek(0)
    while True:
        b = ram.read(CH)
        if not b:
            break
        buf = prev + b
        i = 0
        while True:
            j = buf.find(pat, i)
            if j < 0:
                break
            hits.append(off - len(prev) + j + 0x80000000)
            i = j + 1
        prev, off = buf[-64:], off + len(b)
    return hits

PAIRS_VA, PAIRS_N   = 0x9D23FC, 37 * 0x18     # filas de 0x18, terminador +0==0
LIST_VA,  LIST_N    = 0x9D2380, 30 * 4        # 30 sectores + -1
SMT_VA,   SMT_N     = 0xA3699C, 30 * 0x14     # .bss: solo en RAM

# 1) tabla de pares: contenido del .so + copias en RAM (deben coincidir)
pairs_img = image_of(PAIRS_VA, PAIRS_N)
copies = find_pages(PAIRS_VA, 0x30)
print('copias fisicas de la tabla de pares (VA 0x%08X):' % PAIRS_VA,
      ['0x%08X' % c for c in copies])
for c in copies:
    print('  0x%08X == .so: %s' % (c, rd(c, PAIRS_N) == pairs_img))

pairs = [struct.unpack('<6I', pairs_img[i * 0x18:(i + 1) * 0x18]) for i in range(37)]

# 2) lista de 30 sectores (0x9D2380) y su copia en RAM
list_img = [struct.unpack('<I', so[va2off(LIST_VA) + 4 * i:va2off(LIST_VA) + 4 * i + 4])[0]
            for i in range(30)]
lcopies = find_pages(LIST_VA, 120)
print('copias fisicas de la lista 0x9D2380:', ['0x%08X' % c for c in lcopies])

# 3) Sector Manager Info Table desde RAM (pagina .bss localizada por contenido)
def find_smt():
    # la pagina .bss no esta en el .so; se busca la rejilla 0x14 con los 30 sectores
    CH, prev, off = 1 << 24, b'', 0
    pat = struct.pack('<I', list_img[0]) + bytes(0x10) + struct.pack('<I', list_img[1])
    out = []
    ram.seek(0)
    while True:
        b = ram.read(CH)
        if not b:
            break
        buf = prev + b
        i = 0
        while True:
            j = buf.find(pat, i)
            if j < 0:
                break
            out.append(off - len(prev) + j + 0x80000000)
            i = j + 1
        prev, off = buf[-64:], off + len(b)
    return out

smt_hits = find_smt()
print('copias fisicas de la SMT 0xA3699C (paso 0x14):', ['0x%08X' % c for c in smt_hits])
SMT = smt_hits[0]
print('SMT usada: 0x%08X  (VA=0x%08X, base implicita 0x%08X)' % (SMT, SMT_VA, SMT - SMT_VA))

smt = []
for i in range(30):
    e = rd(SMT + i * 0x14, 0x14)
    smt.append(struct.unpack('<5I', e))

# 4) tabla cruzada: 30 filas por indice
sector2idx = {s: i for i, s in enumerate(list_img)}
print()
hdr = 'idx  sector  pares(userID,mediaID)                 handle  valido  +0xC  +0x10'
print(hdr)
print('-' * len(hdr))
for i in range(30):
    s, h, v, c0, c1 = smt[i]
    users = ['(0x%02X,%d)' % (p[0], p[1]) for p in pairs if p[2] == s]
    print('%2d   0x%02X    %-38s  %-6d  %-6d  0x%02X  %s'
          % (i, s, ' '.join(users) if users else '-', h, v, c0,
             ('0x%02X' % c1) if c1 else '-'))
print()
print('entradas con handle != 0:', sum(1 for e in smt if e[1]))
print()
print('--- las 37 filas de 0x9D23FC (VA 0x%08X, paso 0x18) ---' % PAIRS_VA)
print('fila  userID mediaID sector  idx  handle valido')
for n, p in enumerate(pairs):
    print('%3d   0x%02X    %d      0x%02X    %2d   %-6d %d'
          % (n, p[0], p[1], p[2], sector2idx.get(p[2], -1),
             smt[sector2idx[p[2]]][1], smt[sector2idx[p[2]]][2]))
