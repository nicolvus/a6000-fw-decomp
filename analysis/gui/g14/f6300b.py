import struct,re,json,sys,subprocess
from capstone import *
sys.path.insert(0,'/tmp/claude-1000/-home-nicolas-Documents-a6000/a2e085c4-fb55-411a-9856-65c9ed210332/scratchpad')
import vt
P=sys.argv[1]
d=open(P,'rb').read()
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
REL={}
for l in subprocess.run(['readelf','-rW',P],capture_output=True,text=True).stdout.splitlines():
    f=l.split()
    if len(f)>=3 and re.fullmatch(r'[0-9a-f]{8}',f[0]): REL[int(f[0],16)]=(f[2],f[4] if len(f)>4 else None)
def rd(v):
    o=vt.v2o(d,v); return None if o is None else struct.unpack_from('<I',d,o)[0]
def cstr(v):
    o=vt.v2o(d,v); return None if o is None else d[o:o+90].split(b'\0')[0].decode('latin1')
VT={}
def cls_from_slot(slot):
    t,s=REL.get(slot,(None,None))
    if s and 'ProcessDataElement' in s: return s
    v=rd(slot)
    if v:
        ti=rd(v+4); nm=rd(ti+4) if ti else None
        if nm:
            n=cstr(nm)
            if n and 'ProcessDataElement' in n: VT[n]=v; return n
        t2,s2=REL.get(v+4,(None,None))
        if s2 and 'ProcessDataElement' in s2: return s2
    return None
def scan(fn,depth):
    if depth==0 or vt.v2o(d,fn) is None: return None
    regs={}; direct=None; sub=None
    o=vt.v2o(d,fn)
    for i in md.disasm(d[o:o+200],fn):
        ops=[x.strip() for x in i.op_str.split(',')]
        if i.mnemonic=='ldr' and len(ops)==3 and ops[1]=='[pc' :
            regs[ops[0]]=('lit',rd(((i.address+4)&~3)+int(ops[2].strip('#]'),16)))
        elif i.mnemonic=='add' and len(ops)==2 and ops[1]=='pc' and regs.get(ops[0],(0,))[0]=='lit':
            regs[ops[0]]=('abs',(regs[ops[0]][1]+i.address+4)&0xffffffff)
        elif i.mnemonic=='ldr' and len(ops)==3 and ops[1].startswith('[r') and ops[2].endswith(']') and ops[2].startswith('r'):
            a=regs.get(ops[1][1:]); b=regs.get(ops[2][:-1])
            if a and b and {a[0],b[0]}=={'abs','lit'}:
                c=cls_from_slot((a[1]+b[1])&0xffffffff)
                if c: direct=c
        elif i.mnemonic in('bl','blx') and ops[0].startswith('#'):
            c=scan(int(ops[0][1:],16),depth-1)
            if c and not sub: sub=c
        elif i.mnemonic in('b.w','b') and ops[0].startswith('#'):
            return direct or scan(int(ops[0][1:],16),depth-1)
        if (i.mnemonic.startswith('pop') and 'pc' in i.op_str) or i.op_str=='lr' and i.mnemonic=='bx': break
    return direct or sub
base,ncase,ge_lit,ge_add,npid=[int(x,16) for x in sys.argv[2:7]]
cases={}
for c in range(ncase):
    t=(base+rd(base+4*c))&~1 if sys.argv[7]=='rel' else None
    n=scan(t,4)
    cases[c]=re.sub(r'.*CmnViewProcessDataElement','',n) if n else hex(t)
tab=(rd(ge_lit)+ge_add+4)&0xffffffff
E=[rd(tab+4*p) for p in range(npid)]
print(sum(not v.startswith('0x') for v in cases.values()),'de',len(cases))
json.dump({'cases':{str(k):v for k,v in cases.items()},'pid2case':E,'vt':{re.sub(r'.*CmnViewProcessDataElement','',k):v for k,v in VT.items()}},open(sys.argv[8],'w'))
