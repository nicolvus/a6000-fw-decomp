import struct,sys,json,re
sys.path.insert(0,sys.argv[1]); import vt
from capstone import *
S=sys.argv[1]
P='firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/viewUnified2.so'
sys.path.insert(0,'scripts/gui'); import elf_scan
x=elf_scan.Elf(P); plt=x.plt_map()
d=open(P,'rb').read(); md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
TEXT_END=[s for s in vt.segs(d) if s[0]==1][0][4]
def rd(v):
    o=vt.v2o(d,v); return None if o is None else struct.unpack_from('<I',d,o)[0]
def cstr(v):
    o=vt.v2o(d,v)
    if o is None: return None
    s=d[o:o+60].split(b'\0')[0]
    return s.decode('latin1') if len(s)>=3 and all(32<=c<127 for c in s) else None
def slots(v):
    out=[]
    for i in range(2,80):
        w=rd(v+4*i)
        if w is None or not (0x1000<w<TEXT_END) or not (w&1): break
        out.append(w&~1)
    return out
def body(a,depth=2,seen=None):
    seen=seen or set()
    if a in seen or depth<0: return [],[]
    seen.add(a); strs=[];ext=[]
    o=vt.v2o(d,a); lits={}
    for i in md.disasm(d[o:o+0x600],a):
        ops=[s.strip() for s in i.op_str.split(',')]
        if i.mnemonic=='ldr' and len(ops)==3 and ops[1]=='[pc': lits[ops[0]]=rd(((i.address+4)&~3)+int(ops[2].strip('#]'),16))
        if i.mnemonic=='add' and len(ops)==2 and ops[1]=='pc' and lits.get(ops[0]) is not None:
            s=cstr((lits[ops[0]]+i.address+4)&0xffffffff)
            if s: strs.append(s)
        if i.mnemonic in('bl','blx') and ops[0].startswith('#'):
            t=int(ops[0][1:],16)
            n=plt.get(t) or plt.get(t+4)
            if n: ext.append(n)
            elif depth>0:
                s2,e2=body(t,depth-1,seen); strs+=s2; ext+=e2
        if (i.mnemonic.startswith('pop') and 'pc' in i.op_str) : break
    return strs,ext
j=json.load(open(S+'/f6300.json'))
base=set(slots(j['vt']['CustomBase']))|set(slots(j['vt']['Normal']))
res={}
for cls,v in j['vt'].items():
    S1=[];E1=[]
    for f in sorted(set(slots(v))-base):
        s,e=body(f); S1+=s; E1+=e
    res[cls]={'strings':sorted(set(S1)),'ext':sorted(set(E1))}
json.dump(res,open(S+'/calls.json','w'),indent=0)
for k in ('CustomReleaseWOCard','CustomIsoAutoMinShutterSpeed','CustomStillShutterType','CustomSelfTimerOnBracket'): print(k,res[k]['strings'][:12],[re.sub(r'^_ZN?\d*','',e)[:50] for e in res[k]['ext']][:15])
