"""S71-17: ¿qué llamadores de una función reciben la raíz G (0x43e9b548..+0x1000) por argumento? (literal PIC en las 40 instrucciones previas)."""
import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

b = Path("analysis/rea-independent/input/av-cam.bin").read_bytes()
base = 0x43541000
F = int(sys.argv[1], 16)
G = int(sys.argv[2], 16)
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.skipdata = True
ins = list(md.disasm(b[:0x9c0000], base))
for k, i in enumerate(ins):
    if i.mnemonic in ("bl", "b.w") and i.op_str == f"#{hex(F)}":
        pend = {}
        res = []
        for x in ins[max(0, k - 40):k]:
            m = re.match(r"(r\d+), \[pc, #(0x[0-9a-f]+)\]$", x.op_str) if x.mnemonic.startswith("ldr") else None
            if m:
                la = ((x.address + 4) & ~3) + int(m.group(2), 16)
                pend[m.group(1)] = struct.unpack_from("<I", b, la - base)[0]
            elif x.mnemonic == "add" and x.op_str.endswith(", pc"):
                r = x.op_str.split(",")[0]
                if r in pend:
                    t = (pend[r] + x.address + 4) & 0xFFFFFFFF
                    if G <= t < G + 0x1000:
                        res.append((hex(x.address), hex(t)))
        print(hex(i.address), res)
