import sys,json
S=sys.argv[1]; sys.path.insert(0,S)
import params, cls_pairs_rng
P=cls_pairs_rng.P; rng=cls_pairs_rng.rng
A=set(json.load(open(S+'/a6000_params.json')))
hits=params.scan(P,sorted(rng))
res={}
for v,f,addr in hits:
    cls=next(c for (a,b),c in rng.items() if a<=addr<b)
    res.setdefault(cls,{'nuevos':set(),'existentes':set()})['existentes' if v in A else 'nuevos'].add(v)
out={k:{kk:sorted(vv) for kk,vv in v.items()} for k,v in res.items()}
json.dump(out,open(S+'/cls_params.json','w'),indent=0)
for k in ('CustomStillShutterType','CustomReleaseWOCard','CustomIsoAutoMinShutterSpeed','CustomSelfTimerOnBracket','CustomFocusMagnifAF','CustomRawFileType','CustomPictureProfileGamma','CustomLensRingSetup','CustomZoomRingRotate','CustomFrontCurtainShutter','CustomDriveMode'):
    print(k,{kk:[hex(x) for x in vv] for kk,vv in out.get(k,{}).items()})
