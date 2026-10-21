import re
from pathlib import Path

from capstone import *

b=Path('analysis/rea-independent/input/av-cam.bin').read_bytes(); base=0x43541000
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB); md.skipdata=True
ins=list(md.disasm(b[:0x9c0000],base))
G={0x43804de8,0x43804c50}
for k,i in enumerate(ins):
    if i.mnemonic=='bl' and i.op_str.startswith('#') and int(i.op_str[1:],16)==0x43804de8:
        seen=[]
        for j in ins[k+1:k+14]:
            m=re.search(r'\[(r\d+), #(0x[0-9a-f]+)\]',j.op_str)
            if m and j.mnemonic.startswith(('ldr','str')): seen.append((j.address,j.mnemonic,int(m.group(2),16)))
            if j.mnemonic in('bl','pop','bx'): break
        for j in ins[k+1:k+16]:
            mm=re.search(r"#(0x[0-9a-f]+)$|#(0x[0-9a-f]+)\]",j.op_str)
            if mm:
                v=int(mm.group(1) or mm.group(2),16)
                if v in(0x234,0x238,0x23c,0x280): print(hex(i.address),hex(j.address),j.mnemonic,j.op_str)
            if j.mnemonic in("bl","pop","bx"): break
        for a,mn,o in []:
            if o in range(0x230,0x244) or o in range(0x278,0x28c): print(hex(i.address),hex(a),mn,hex(o))
