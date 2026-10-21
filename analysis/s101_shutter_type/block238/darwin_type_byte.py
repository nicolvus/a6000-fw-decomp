import collections
import re
import struct
from pathlib import Path

from capstone import *

b=Path('firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin').read_bytes(); base=0x4200
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB); md.skipdata=True
ins=list(md.disasm(b,base))
pool={base+o:struct.unpack_from('<I',b,o)[0] for o in range(0,len(b)-3,4)}
c=collections.Counter(v for v in pool.values() if 0x20000000<=v<0x20000400)
print(sorted((hex(k),n) for k,n in c.items() if 0x20000040<=k<=0x20000060 or 0x200002b0<=k<=0x200002d0 or k==0x20000000))
for k,i in enumerate(ins):
    m=re.match(r'(r\d+), \[pc, #(0x[0-9a-f]+)\]$',i.op_str) if i.mnemonic.startswith('ldr') else None
    if not m: continue
    la=((i.address+4)&~3)+int(m.group(2),16); v=pool.get(la)
    if v in(0x20000000,0x200002c0):
        r=m.group(1); w=ins[k+1:k+16]
        hit=[x for x in w if re.search(r'#0x(5[0-7]|2c[0-7])\b',x.op_str) and re.search(rf'\b{r}\b',x.op_str)]
        if hit: print(hex(i.address),hex(v),[f"{x.address:x} {x.mnemonic} {x.op_str}" for x in hit][:4])
