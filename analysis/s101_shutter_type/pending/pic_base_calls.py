"""S71-18: instrucciones donde una base PIC resuelve exactamente a BASE y se usa como argumento (mov r0,rX / bl cercano)."""
import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

b = Path("analysis/rea-independent/input/av-cam.bin").read_bytes()
base = 0x43541000
T = int(sys.argv[1], 16)
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.skipdata = True
ins = list(md.disasm(b[:0x9c0000], base))
pend = {}
for k, i in enumerate(ins):
    m = re.match(r"(r\d+), \[pc, #(0x[0-9a-f]+)\]$", i.op_str) if i.mnemonic.startswith("ldr") else None
    if m:
        la = ((i.address + 4) & ~3) + int(m.group(2), 16)
        pend[m.group(1)] = (struct.unpack_from("<I", b, la - base)[0], k)
        continue
    if i.mnemonic == "add" and i.op_str.endswith(", pc"):
        r = i.op_str.split(",")[0]
        if r in pend and k - pend[r][1] < 14 and ((pend[r][0] + i.address + 4) & 0xFFFFFFFF) == T:
            ctx = " ; ".join(f"{x.mnemonic} {x.op_str}" for x in ins[k + 1:k + 7])
            print(hex(i.address), r, "|", ctx[:200])
