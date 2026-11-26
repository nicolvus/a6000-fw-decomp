import sys, struct, json, re
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from elfhelper import Elf
from capstone import *
P='firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so'
e=Elf(P); d=e.d
starts=json.load(open('/tmp/fstarts.json'))
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB)
def rd32(a): return struct.unpack_from('<I',d,a)[0]
def cstr(va):
    o=e.va2off(va)
    if o is None: return None
    j=d.find(b'\0',o,o+90)
    if j<0: return None
    s=d[o:j]
    if len(s)<3 or not all(32<=c<127 for c in s): return None
    return s.decode()
def disas(va,end):
    out=[];pos=va
    while pos<end:
        off=e.va2off(pos); ins=None
        for i in md.disasm(d[off:min(off+4,len(d))],pos):
            if i.address==pos: ins=i
            break
        if ins is None:
            out.append((pos,'.hword','',  '')); pos+=2; continue
        out.append((pos,ins.mnemonic,ins.op_str,ins.bytes.hex())); pos+=ins.size
    return out
def fstart(va):
    c=[s for s in starts if s<=va]
    return c[-1] if c else None
def fname(va):
    st=fstart(va); nxt=[s for s in starts if s>st]
    nxt=nxt[0] if nxt else st+0x400
    last=None
    for pos,mn,ops,hx in disas(st,min(st+0x80,nxt)):
        if mn=='ldr' and '[pc' in ops:
            m=re.search(r'#(0x[0-9a-f]+)',ops)
            if m:
                v=rd32(((pos+4)&~3)+int(m.group(1),16)); s=cstr(v)
                if s: last=s
        if mn=='bl' and ops.startswith('#') and int(ops[1:],16)==0x2b1e68:
            return last
    return last
for arg in sys.argv[1:]:
    va=int(arg,16)
    print('%08x  inicio=%08x  nombre=%r' % (va, fstart(va), fname(va)))
