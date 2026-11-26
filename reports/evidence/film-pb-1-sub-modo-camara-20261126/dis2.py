import struct, sys, re
from capstone import *
P='/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so'
d=open(P,'rb').read()
SEGS=[(0x000000,0x000000,0x9bb1c8),(0x9bb1c8,0x009c31c8,0x1c640)]
def va2off(va):
    for po,base,fsz in SEGS:
        if base<=va<base+fsz: return po+va-base
    return None
def rd(va,n):
    o=va2off(va); return d[o:o+n] if o is not None else b''
def word(va):
    b=rd(va,4); return struct.unpack('<I',b)[0] if len(b)==4 else None
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB)
def note(i, size=32):
    ops=i.op_str.replace(' ','')
    if i.mnemonic.startswith('ldr') and '[pc' in i.op_str:
        m=re.search(r'#(0x[0-9a-f]+)', i.op_str)
        if m:
            tgt=((i.address+4)&~3)+int(m.group(1),16)
            val=word(tgt)
            if val is not None:
                s=rd(val,48); t=''
                if s: 
                    seg=s.split(b'\0')[0]
                    if len(seg)>3 and all(32<=c<127 or c in (9,10) for c in seg):
                        t=' "%s"'%seg.decode('latin1')[:48]
                return '  ; [%08x]=%08x%s'%(tgt,val,t)
    return ''
def run(va,end,skipbad=True):
    a=va
    while a<end:
        got=False
        for i in md.disasm(rd(a,4),a):
            print('%08x: %-10s %-8s %-30s%s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str,note(i)))
            a=i.address+i.size; got=True
        if not got:
            if skipbad:
                print('%08x: %s   <bad/skip>'%(a,rd(a,2).hex())); a+=2
            else: break
if __name__=='__main__':
    run(int(sys.argv[1],16), int(sys.argv[2],16))
