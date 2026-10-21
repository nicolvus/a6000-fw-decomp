import re
import struct

from capstone import *

b=open('firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin','rb').read(); base=0x4200
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB); md.skipdata=True
ins=list(md.disasm(b,base))
pool={base+o:struct.unpack_from('<I',b,o)[0] for o in range(0,len(b)-3,4)}
for k,i in enumerate(ins):
    m=re.match(r'(r\d+), \[pc, #(0x[0-9a-f]+)\]$',i.op_str) if i.mnemonic.startswith('ldr') else None
    if m and pool.get(((i.address+4)&~3)+int(m.group(2),16))==0x20000000:
        r=m.group(1)
        for x in ins[k+1:k+40]:
            if x.mnemonic in('pop','bx') : break
            mm=re.match(rf'(\w+), \[{r}, #(0x[0-9a-f]+)\]$',x.op_str)
            if mm and x.mnemonic.startswith('str') and 0x50<=int(mm.group(2),16)<=0x6f: print('STORE',hex(i.address),hex(x.address),x.mnemonic,x.op_str)
            if re.match(rf'{r}, {r}, #0x(5\d|6\d)$',x.op_str) or re.match(rf'\w+, {r}, #0x(5\d|6\d)$',x.op_str): print('ADD',hex(i.address),hex(x.address),x.mnemonic,x.op_str)
print('--global')
for k,i in enumerate(ins):
    if i.mnemonic.startswith('strb') and re.search(r'\[\w+, #0x(5\d|6[0-7])\]$',i.op_str): print(hex(i.address),i.mnemonic,i.op_str, '|', ' ; '.join(f"{x.mnemonic} {x.op_str}" for x in ins[max(0,k-4):k]))
