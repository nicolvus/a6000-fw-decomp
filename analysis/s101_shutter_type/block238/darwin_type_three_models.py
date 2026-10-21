import re
import struct
from pathlib import Path

from capstone import *

P={'a6000':'firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin',
'a7s':'firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0640_darwin/darwin_core.bin',
'a6300':'firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0640_darwin/darwin_core.bin'}
for n,f in P.items():
    b=Path(f).read_bytes(); base=0x4200
    md=Cs(CS_ARCH_ARM,CS_MODE_THUMB); md.skipdata=True
    ins=list(md.disasm(b,base))
    pool={base+o:struct.unpack_from('<I',b,o)[0] for o in range(0,len(b)-3,4)}
    # lectores del tipo: ldrb.w ...,[r,#0x50] precedido por literal 0x20000000
    rd=[];wr=[]
    for k,i in enumerate(ins):
        if re.search(r'\[\w+, #0x50\]$',i.op_str) and i.mnemonic.startswith(('ldrb','strb')):
            w=ins[max(0,k-6):k]
            if any(x.mnemonic.startswith('ldr') and 'pc' in x.op_str and pool.get(((x.address+4)&~3)+int(re.search(r'#(0x[0-9a-f]+)',x.op_str).group(1),16))==0x20000000 for x in w):
                (wr if i.mnemonic.startswith('strb') else rd).append(hex(i.address))
    lit=[hex(v) for v in set(pool.values()) if 0x20000050<=v<=0x20000058]
    print(n,len(b),'lectores',rd,'escritores',wr,'literales',lit)
