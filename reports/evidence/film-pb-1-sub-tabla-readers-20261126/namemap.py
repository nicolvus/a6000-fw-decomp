import sys, struct, json, re
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from elfhelper import Elf
from capstone import *
P='firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so'
e=Elf(P); d=e.d
starts=json.load(open('/tmp/fstarts.json'))
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB)
def u16(a): return struct.unpack_from('<H',d,a)[0]
def rd32(a): return struct.unpack_from('<I',d,a)[0]
def cstr(va):
    try: o=e.va2off(va)
    except: return None
    if o is None: return None
    j=d.find(b'\0',o,o+80)
    if j<0: return None
    s=d[o:j]
    if len(s)<3: return None
    if all(32<=c<127 for c in s): return s.decode()
    return None
def disas(va,end):
    out=[]
    pos=va
    while pos<end:
        off=e.va2off(pos)
        ins=None
        for i in md.disasm(d[off:min(off+4,len(d))],pos):
            if i.address==pos: ins=i
            break
        if ins is None:
            out.append((pos,'.hword',None,'')); pos+=2; continue
        out.append((pos,ins.mnemonic,ins.op_str,ins.bytes.hex()))
        pos+=ins.size
    return out
def fname(va):
    nxt=None
    for s in starts:
        if s>va: nxt=s; break
    if nxt is None: nxt=va+0x400
    ins=disas(va,min(va+0x60,nxt))
    laststr=None
    for pos,mn,ops,hx in ins:
        if mn=='ldr' and ops and '[pc' in ops:
            m=re.search(r'#(0x[0-9a-f]+)',ops)
            if m:
                lit=((pos+4)&~3)+int(m.group(1),16)
                v=rd32(lit)
                s=cstr(v)
                if s: laststr=s
        if mn=='bl' and ops and ops.startswith('#'):
            t=int(ops[1:],16)
            if t==0x2b1e68:
                return laststr
    return laststr
lo,hi=int(sys.argv[1],16),int(sys.argv[2],16)
for s in starts:
    if lo<=s<hi:
        print('%08x  %s' % (s, fname(s)))
