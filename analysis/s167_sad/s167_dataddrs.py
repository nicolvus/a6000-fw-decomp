#!/usr/bin/env python3
"""S167 — direcciones de DATOS (no-cadena) referenciadas por los emisores [SAD],
con el emparejamiento estricto (ldr más cercano del mismo registro -> add rX,pc)."""
import bisect, struct, sys
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
U16=struct.Struct("<H").unpack_from; U32=struct.Struct("<I").unpack_from
def cstr(a):
    o=a-BASE
    if o<0 or o>=len(B): return None
    e=B.find(b"\x00",o)
    t=B[o:e]
    try: return t.decode("latin1")
    except Exception: return None
def ldrs(lo,hi):
    out=[];a=lo
    while a<hi:
        o=a-BASE; h=U16(B,o)[0]; reg=lit=None
        if (h & 0xF800)==0x4800: reg=(h>>8)&7; lit=((a+4)&~3)+((h&0xFF)*4)
        elif (h & 0xFF7F)==0xF85F:
            h2=U16(B,o+2)[0]; reg=(h2>>12)&0xF; lit=((a+4)&~3)+((((h2>>8)&0xF)<<8)|(h2&0xFF))
        if reg is not None and 0<=lit-BASE<=len(B)-4: out.append((a,reg,U32(B,lit-BASE)[0],lit))
        a+=2
    return out
def adds(lo,hi):
    out=[];a=lo
    while a<hi:
        o=a-BASE; h=U16(B,o)[0]
        if (h & 0xFF00)==0x4400 and ((h>>3)&0xF)==15: out.append((a,(((h>>7)&1)<<3)|(h&7)))
        a+=2
    return out
def run(name, lo, hi):
    L=ldrs(lo,hi); by={}
    for a,r,w,p in L: by.setdefault(r,[]).append((a,w,p))
    for v in by.values(): v.sort()
    keys={r:[x[0] for x in v] for r,v in by.items()}
    seen=set()
    print("===",name)
    for s,reg in adds(lo,hi):
        v=by.get(reg)
        if not v: continue
        ks=keys[reg]; i=bisect.bisect_left(ks,s)-1
        if i<0: continue
        la,w,p=v[i]
        if s-la>4096: continue
        d=(w+(s+4))&0xFFFFFFFF
        if d in seen: continue
        seen.add(d)
        t=cstr(d)
        isstr = t is not None and all(32<=ord(c)<127 for c in t) and len(t)>0
        print(f"   add@{s:#x} r{reg} ldr@{la:#x} pool={p:#x} W={w:#x} -> {d:#x} "
              f"{'CADENA ' + repr(t[:60]) if isstr else '<datos>'}")
for a in sys.argv[1:]:
    lo=int(a,0)
    hi=int(sys.argv[2],0)
    run(a, lo, hi)
