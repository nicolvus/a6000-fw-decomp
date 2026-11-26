import sys, struct, json, re
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from elfhelper import Elf
from capstone import *
P='firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so'
e=Elf(P); d=e.d
starts=json.load(open('/tmp/fstarts.json'))
tv,to,ts=e.sec['.text']
def u16(a): return struct.unpack_from('<H',d,a)[0]
def rd32(a): return struct.unpack_from('<I',d,a)[0]
def cstr(va):
    o=e.va2off(va)
    if o is None: return None
    j=d.find(b'\0',o,o+90)
    if j<0: return None
    s=d[o:o+(j-o)]
    if len(s)<3 or not all(32<=c<127 for c in s): return None
    return s.decode()
pool=set(a for a in e.xrefs(0xA3699C) if a)
hits=[]
off=to
while off<to+ts-4:
    hw=u16(off); va=tv+(off-to)
    if (hw & 0xF800)==0x4800:
        lit=((va+4)&~3)+(hw&0xFF)*4
        if lit in pool: hits.append((va,(hw>>8)&7,'r%d'%((hw>>8)&7)))
    elif hw==0xF8DF:
        hw2=u16(off+2); lit=((va+4)&~3)+(hw2&0xFFF)
        if lit in pool: hits.append((va,hw2>>12,'r%d'%(hw2>>12)))
    off+=2
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB)
def dis(va,n=16):
    out=[];pos=va
    while pos<va+n:
        o=e.va2off(pos); ins=None
        for i in md.disasm(d[o:o+4],pos):
            if i.address==pos: ins=i
            break
        if ins is None: out.append((pos,'.hword','')); pos+=2; continue
        out.append((pos,ins.mnemonic,ins.op_str)); pos+=ins.size
    return out
def fstart(va):
    c=[s for s in starts if s<=va]
    return c[-1] if c else None
print('%-10s %-4s %-10s %-28s %s' % ('VA','reg','funcion','nombre','6 instrucciones desde la carga'))
for va,rt,rname in sorted(hits):
    st=fstart(va)
    print('---')
    print('%08x  %-4s func=%08x' % (va,rname,st))
    for p,mn,ops in dis(va,14):
        print('      %08x  %-7s %s' % (p,mn,ops))
