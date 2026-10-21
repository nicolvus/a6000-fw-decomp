#!/usr/bin/env python3
"""S109 — ¿alguna de las 28 cadenas [CDIAG] sin referencia PIC está referenciada
de otra forma?  Para cada objetivo se calcula, para cada `ldr rX,[pc,#imm]`
de la imagen, la dirección de `add` que haría falta y se comprueba si existe
un `add rX,pc` (16 bits) en esa posición exacta, con el mismo registro.

Salida: texto por pantalla (no escribe ficheros).
"""
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
data = open(BIN, "rb").read()
N = len(data)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from

targets = [int(x, 16) for x in sys.argv[1:]] or [
    0x43C3CF60, 0x43C3CF87, 0x43C3D083, 0x43C3C29C, 0x43C3DA06, 0x43C3DB1E,
]

# 1) todos los ldr [pc,#imm] con su valor de pool
ldrs = []
for a in range(BASE, BASE + N - 8, 2):
    o = a - BASE
    h = U16(data, o)[0]
    if (h & 0xF800) == 0x4800:
        reg = (h >> 8) & 7
        lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
    elif (h & 0xFF7F) == 0xF85F:
        h2 = U16(data, o + 2)[0]
        reg = (h2 >> 12) & 0xF
        imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
        lit = ((a + 4) & ~3) + imm12
    else:
        continue
    o2 = lit - BASE
    if 0 <= o2 <= N - 4:
        ldrs.append((a, reg, U32(data, o2)[0]))

print(f"ldr [pc,#imm] encontrados: {len(ldrs)}")

for t in targets:
    hits = []
    for la, reg, w in ldrs:
        add_addr = (t - w - 4) & 0xFFFFFFFF
        if add_addr < BASE or add_addr >= BASE + N - 2:
            continue
        if (add_addr - BASE) % 2:
            continue
        h = U16(data, add_addr - BASE)[0]
        if (h & 0xFF00) != 0x4400 or ((h >> 3) & 0xF) != 15:
            continue
        rd = (((h >> 7) & 1) << 3) | (h & 7)
        if rd != reg:
            continue
        hits.append((hex(la), hex(add_addr), reg))
    print(f"{hex(t)} -> referencias exactas: {hits[:8]}  (n={len(hits)})")
