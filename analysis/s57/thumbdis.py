"""S57 util: desensamblado Thumb con resolución de literales GOT -> registro sombra IMX210. uso: thumbdis.py 0xINI 0xFIN"""
import sys,struct,re
from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent / 's56')); sys.path.insert(0, str(Path(__file__).parent.parent / 's55'))
import rec_users as R
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
B=0x43541000
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
s2r={o:p for p,offs in R.slots.items() for o in offs}
def dis(a,b,out=print):
    for i in md.disasm(R.d[a-B:b-B],a):
        note=''
        m=re.match(r'(r\d+), \[pc, #(0x[0-9a-f]+|\d+)\]$',i.op_str)
        if i.mnemonic.startswith('ldr') and m:
            la=((i.address+4)&~3)+int(m.group(2),0)
            try: v=struct.unpack_from('<I',R.d,la-B)[0]
            except Exception: v=0
            note=' ; lit=%#x'%v
            if v in s2r: note+=' REG id=%#x'%R.recs[s2r[v]]
        out('%x %s %s%s'%(i.address,i.mnemonic,i.op_str,note))
if __name__=='__main__': dis(int(sys.argv[1],0),int(sys.argv[2],0))
