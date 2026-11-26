import sys,struct
sys.path.insert(0,'/tmp')
from elfhelper import Elf
e=Elf('analysis/camera-extract/usr/lib/libmpr.so')
text_va,text_off,text_sz=e.sec['.text']; d=e.d
callers={}
for off in range(text_off,text_off+text_sz-3,2):
    hw1,hw2=struct.unpack_from('<HH',d,off)
    if (hw1&0xF800)!=0xF000 or (hw2&0xC000)!=0xC000: continue
    s=(hw1>>10)&1; imm10=hw1&0x3FF
    j1=(hw2>>13)&1; j2=(hw2>>11)&1; imm11=hw2&0x7FF
    i1=(~(j1^s))&1; i2=(~(j2^s))&1
    imm=(s<<24)|(i1<<23)|(i2<<22)|(imm10<<12)|(imm11<<1)
    if s: imm-=1<<25
    pc=text_va+(off-text_off)
    base=pc+4 if (hw2&0x1000) else ((pc+4)&~3)
    tgt=base+imm
    callers.setdefault(tgt,[]).append(pc)
def name(a):
    return e.name_at(a) or ''
def show(target,maxdepth=4):
    print('CALLERS of %08x %s'%(target,name(target)))
    seen=set()
    def rec(t,depth):
        for c in sorted(set(callers.get(t,[]))):
            if (c,depth) in seen: continue
            seen.add((c,depth))
            print('  '*depth+'<- %08x %s'%(c,name(c)))
            if depth<maxdepth: rec(c,depth+1)
    rec(target,1)
if __name__=='__main__':
    for a in sys.argv[1:]:
        show(int(a,16),3)
