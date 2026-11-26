
import sys, collections, bisect
sys.path.insert(0,'/tmp')
from ifotool import Binary
from ifocfg import dec, bl_targets, push_entries, cfg
b=Binary(); ACQ,REL=0x5bad00,0x5bacb0
LO,HI=0x6e807c,0x6ec200
ent=sorted(set(s for s in b.fmap if LO<=s<HI)|bl_targets(LO,HI)|push_entries(LO,HI))
acq=[s for s in b.calls_to(ACQ) if LO<=s<HI]; rel=[s for s in b.calls_to(REL) if LO<=s<HI]
def unit_of(site):
    idx=bisect.bisect_right(ent,site)-1
    for j in range(idx,-1,-1):
        e=ent[j]; lim=ent[j+1] if j+1<len(ent) else HI
        ins,_,_,_=cfg(e,lim)
        if site in ins: return e,lim
    return None,None
tgt=collections.Counter()
for s in acq:
    u,lim=unit_of(s)
    if not u: continue
    r=[x for x in rel if u<=x<lim][0]
    a=s+4
    while a<r:
        i=dec(a)
        if i is None: break
        if i.mnemonic=='bl': tgt[i.op_str.lstrip('#')]+=1
        a+=i.size
for t,c in tgt.most_common(): print('  %s x%d' % (t,c))

