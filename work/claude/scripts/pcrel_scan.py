#!/usr/bin/env python3
"""Busca referencias PIC Thumb: LDR Rd,[PC,#imm] (16 bit) ... ADD Rd,PC con Rd+PC+4 == objetivo.
Uso: pcrel_scan.py BIN BASE VALOR_HEX [VALOR_HEX...]  -> dirección del ADD (la referencia)."""
import sys, struct
d = open(sys.argv[1], 'rb').read(); base = int(sys.argv[2], 16)
targets = {int(v, 16) for v in sys.argv[3:]}
for a in range(0, len(d) - 2, 2):
    hw = struct.unpack_from('<H', d, a)[0]
    if hw & 0xff78 != 0x4478: continue  # ADD Rdn, PC (T2, Rm=PC)
    rd = (hw & 7) | ((hw >> 4) & 8)
    for b in range(a - 2, max(a - 64, 0), -2):
        h = struct.unpack_from('<H', d, b)[0]
        if h >> 11 == 0b01001 and (h >> 8) & 7 == rd:
            lit = ((base + b + 4) & ~3) + (h & 0xff) * 4 - base
            if 0 <= lit < len(d) - 4:
                v = (struct.unpack_from('<I', d, lit)[0] + base + a + 4) & 0xffffffff
                if v in targets: print(f"{v:#x} ref add@{base+a:#x} ldr@{base+b:#x} r{rd}")
            break
