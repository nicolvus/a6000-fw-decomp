#!/usr/bin/env python3
"""pic.py BIN LDR_ADDR ADD_ADDR [GOT_LIT_ADDR...]: valor PIC = u32(literal de LDR Rd,[pc,#imm] T1) + ADD_ADDR + 4;
con GOT_LIT_ADDR (literal de un `ldr rX,[rBASE,rY]`) da también *(base+lit). Base de carga 0x43541000."""
import struct
import sys
from pathlib import Path

B = 0x43541000; d = Path(sys.argv[1]).read_bytes()
u32 = lambda a: struct.unpack_from('<I', d, a - B)[0]
ldr, add = int(sys.argv[2], 16), int(sys.argv[3], 16)
h = struct.unpack_from('<H', d, ldr - B)[0]
lit = ((ldr + 4) & ~3) + (h & 0xff) * 4 if h >> 11 == 0b01001 else None
if lit is None:  # ldr.w rt,[pc,#imm] T2
    h2 = struct.unpack_from('<H', d, ldr + 2 - B)[0]; lit = ((ldr + 4) & ~3) + (h2 & 0xfff)
base = (u32(lit) + add + 4) & 0xffffffff
print(f'base={base:#x} (lit@{lit:#x})')
for g in sys.argv[4:]:
    gl = int(g, 16); off = u32(gl); slot = (base + off) & 0xffffffff
    print(f'  GOT lit@{gl:#x} off={off:#x} slot={slot:#x} -> *slot={u32(slot) if B <= slot < B + len(d) else "RAM?"!s}' if not (B <= slot < B+len(d)) else f'  GOT lit@{gl:#x} slot={slot:#x} *slot={u32(slot):#x}')
