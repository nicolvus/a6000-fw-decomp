#!/usr/bin/env python3
"""Lista LDR/STR(.W/B/H) Thumb-2 T3 con offset inmediato imm12 dado. Uso: ldst_imm_scan.py BIN BASE OFF_HEX..."""
import sys, struct
d = open(sys.argv[1], 'rb').read(); base = int(sys.argv[2], 16); offs = {int(x, 16) for x in sys.argv[3:]}
ops = {0xf8d0: 'ldr', 0xf8c0: 'str', 0xf890: 'ldrb', 0xf880: 'strb', 0xf8b0: 'ldrh', 0xf8a0: 'strh'}
for i in range(0, len(d) - 4, 2):
    h1, h2 = struct.unpack_from('<HH', d, i)
    op = ops.get(h1 & 0xfff0)
    if op and (h2 & 0xfff) in offs:
        print(f"{base+i:#x} {op} r{h2>>12}, [r{h1&15}, #{h2&0xfff:#x}]")
