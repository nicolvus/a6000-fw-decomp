"""S71-16: usos de un campo base+off de una variable global accedida por PIC (ldr rX,[pc,#k]; add rX,pc).
Uso: pic_field_users.py BASE OFF [OFF...] (hex). Imprime lecturas/escrituras con el desensamblado de contexto."""
import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

b = Path("analysis/rea-independent/input/av-cam.bin").read_bytes()
base = 0x43541000
G = int(sys.argv[1], 16)
offs = {int(x, 16) for x in sys.argv[2:]}
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.skipdata = True
ins = list(md.disasm(b[:0x9c0000], base))
pend = {}
for k, i in enumerate(ins):
    m = re.match(r"(r\d+), \[pc, #(0x[0-9a-f]+)\]$", i.op_str) if i.mnemonic.startswith("ldr") else None
    if m:
        la = ((i.address + 4) & ~3) + int(m.group(2), 16)
        if la - base + 4 <= len(b):
            pend[m.group(1)] = (struct.unpack_from("<I", b, la - base)[0], k)
        continue
    if i.mnemonic == "add" and i.op_str.endswith(", pc"):
        r = i.op_str.split(",")[0]
        if r in pend and k - pend[r][1] < 14:
            t = (pend[r][0] + i.address + 4) & 0xFFFFFFFF
            if G <= t < G + 0x2000:
                for j in ins[k + 1:k + 40]:
                    mm = re.match(rf"(\w+), \[{r}, #(0x[0-9a-f]+)\]$", j.op_str)
                    if mm and j.mnemonic.startswith(("ldr", "str")) and t + int(mm.group(2), 16) - G in offs:
                        print(hex(j.address), j.mnemonic, j.op_str, "base", hex(t))
                    if j.mnemonic in ("pop", "bx"):
                        break
