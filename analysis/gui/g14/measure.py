import struct,sys,json
sys.path.insert(0,sys.argv[1]); import vt
from capstone import *
S=sys.argv[1]
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
def fsize(a):
    n=0;calls=0
    o=vt.v2o(d,a)
    for i in md.disasm(d[o:o+0x2000],a):
        n=i.address+i.size-a
        if i.mnemonic in('bl','blx'): calls+=1
        if (i.mnemonic.startswith('pop') and 'pc' in i.op_str) or (i.mnemonic=='bx' and i.op_str=='lr'): break
    return n,calls
j=json.load(open(S+'/f6300.json'))
base=set(slots(j['vt']['CustomBase']))|set(slots(j['vt']['Normal']))
res={}
for cls,v in j['vt'].items():
    own=[f for f in slots(v) if f not in base]
    own=sorted(set(own))
    sz=[fsize(f) for f in own]
    res[cls]={'metodos_propios':len(own),'bytes':sum(s for s,_ in sz),'llamadas':sum(c for _,c in sz)}
json.dump(res,open(S+'/measure.json','w'),indent=0)
for k in ('CustomStillShutterType','CustomFrontCurtainShutter','CustomIsoAutoMinShutterSpeed','CustomReleaseWOCard','CustomPictureProfile','CustomZebra'): print(k,res.get(k))
