import re
import struct
import sys

from capstone import *

f=sys.argv[1]; b=open(f,'rb').read(); base=0x4200
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB); md.skipdata=True
ins=list(md.disasm(b,base))
pool={base+o:struct.unpack_from('<I',b,o)[0] for o in range(0,len(b)-3,4)}
for k,i in enumerate(ins):
    m=re.match(r'(r\d+), \[pc, #(0x[0-9a-f]+)\]$',i.op_str) if i.mnemonic.startswith('ldr') else None
    if not m: continue
    V=pool.get(((i.address+4)&~3)+int(m.group(2),16))
    if V is None or not(0x20000000<=V<0x20000100): continue
    r=m.group(1)
    for x in ins[k+1:k+40]:
        if x.mnemonic in('pop','bx') or x.mnemonic.startswith('b') and x.op_str.startswith('#') and False: break
        mm=re.match(rf'(\w+), \[{r}, #(0x[0-9a-f]+)\]!?$',x.op_str)
        if mm and x.mnemonic.startswith(('str','ldr')):
            e=V+int(mm.group(2),16)
            if 0x20000050<=e<0x20000068: print(x.mnemonic[:3],hex(i.address),hex(x.address),x.mnemonic,x.op_str,hex(e))
