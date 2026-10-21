"""S71-19: copias grandes (memcpy 0x439c5320 con tamaño 0x800..0x2000) cuyo destino es una base PIC dentro de G."""
import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

b = Path("analysis/rea-independent/input/av-cam.bin").read_bytes()
base = 0x43541000
G = 0x43E9B548
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.skipdata = True
ins = list(md.disasm(b[:0x9C0000], base))
pend = {}
for k, i in enumerate(ins):
    m = re.match(r"(r\d+), \[pc, #(0x[0-9a-f]+)\]$", i.op_str) if i.mnemonic.startswith("ldr") else None
    if m:
        la = ((i.address + 4) & ~3) + int(m.group(2), 16)
        pend[m.group(1)] = (struct.unpack_from("<I", b, la - base)[0], k, None)
        continue
    if i.mnemonic == "add" and i.op_str.endswith(", pc"):
        r = i.op_str.split(",")[0]
        if r in pend and pend[r][0] is not None:
            pend[r] = (None, k, (pend[r][0] + i.address + 4) & 0xFFFFFFFF)
    if i.mnemonic in ("blx", "bl") and i.op_str in ("#0x439c5320", "#0x439c5324"):
        size = dest = None
        for x in reversed(ins[max(0, k - 14):k]):
            mm = re.match(r"r2, #(0x[0-9a-f]+)$", x.op_str)
            if mm and size is None and x.mnemonic.startswith(("mov", "movw")):
                size = int(mm.group(1), 16)
        for r, (_, kk, t) in pend.items():
            if t and G <= t < G + 0x2000 and k - kk < 14:
                dest = hex(t)
        if size and 0x800 <= size <= 0x2000 and dest:
            print(hex(i.address), hex(size), dest)
