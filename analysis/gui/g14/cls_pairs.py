import sys,json,struct,re
S=sys.argv[1]; sys.path.insert(0,S)
import pairs, vt
from capstone import *
P='firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/viewUnified2.so'
d=open(P,'rb').read(); md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
TEXT_END=[s for s in vt.segs(d) if s[0]==1][0][4]
def rd(v):
    o=vt.v2o(d,v); return None if o is None else struct.unpack_from('<I',d,o)[0]
def slots(v):
    out=[]
    for i in range(2,80):
        w=rd(v+4*i)
        if w is None or not (0x1000<w<TEXT_END) or not (w&1): break
        out.append(w&~1)
    return out
def extent(a):
    o=vt.v2o(d,a); end=a+0x40
    for i in md.disasm(d[o:o+0x1000],a):
        if i.address>a and i.mnemonic in('push','push.w','stmdb'): break
        end=i.address+i.size
    return end
j=json.load(open(S+'/f6300.json'))
base=set(slots(j['vt']['CustomBase']))|set(slots(j['vt']['Normal']))
rng={}
for cls,v in j['vt'].items():
    for f in set(slots(v))-base: rng[(f,extent(f))]=cls
hits=pairs.pairs_in(P,list(rng))
A={tuple(x[:2]) for x in json.load(open(S+'/a6000_pairs.json'))}
res={}
for m,imm,cal,B in hits:
    cls=next(c for (a,b),c in rng.items() if a<=B<b)
    res.setdefault(cls,set()).add((m,imm,(m,imm) in A))
json.dump({k:sorted(map(list,v),key=str) for k,v in res.items()},open(S+'/cls_pairs.json','w'),indent=0)
for k in sorted(res): print(k, sorted(res[k],key=str))
