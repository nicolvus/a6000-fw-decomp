#!/usr/bin/env python3
"""S167 — escáner PIC estricto genérico para cualquier av-cam.bin.
Uso: s167_picscan.py <bin> <lo_vaddr> <hi_vaddr> <out.json>
Genera {destino: [sitios]} para todo inicio de cadena."""
import bisect, json, struct, sys
BASE = 0x43541000
path, lo, hi, dest = sys.argv[1], int(sys.argv[2],0), int(sys.argv[3],0), sys.argv[4]
B = open(path,"rb").read(); N=len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
def string_starts():
    out=set(); prev=False
    for i in range(N):
        cur = 32<=B[i]<127
        if cur and not prev: out.add(BASE+i)
        prev=cur
    return out
def ldr_sites(lo,hi):
    out=[]; a=lo
    while a<hi:
        o=a-BASE
        if o<0 or o>N-8: a+=2; continue
        h=U16(B,o)[0]; reg=lit=None
        if (h & 0xF800)==0x4800:
            reg=(h>>8)&7; lit=((a+4)&~3)+((h&0xFF)*4)
        elif (h & 0xFF7F)==0xF85F:
            h2=U16(B,o+2)[0]; reg=(h2>>12)&0xF
            lit=((a+4)&~3)+((((h2>>8)&0xF)<<8)|(h2&0xFF))
        if reg is not None and 0<=lit-BASE<=N-4:
            out.append((a,reg,U32(B,lit-BASE)[0]))
        a+=2
    return out
def add_sites(lo,hi):
    out=[]; a=lo
    while a<hi:
        o=a-BASE
        if o<0 or o>N-4: a+=2; continue
        h=U16(B,o)[0]
        if (h & 0xFF00)==0x4400 and ((h>>3)&0xF)==15:
            out.append((a, (((h>>7)&1)<<3)|(h&7)))
        a+=2
    return out
starts=string_starts()
ldrs=ldr_sites(lo,hi); adds=add_sites(lo,hi)
by_reg={}
for a,reg,w in ldrs: by_reg.setdefault(reg,[]).append((a,w))
for v in by_reg.values(): v.sort()
keys={r:[x[0] for x in v] for r,v in by_reg.items()}
res={}
for a,reg in adds:
    v=by_reg.get(reg)
    if not v: continue
    ks=keys[reg]; i=bisect.bisect_left(ks,a)-1
    if i<0: continue
    la,w=v[i]
    if a-la>4096: continue
    t=(w+(a+4))&0xFFFFFFFF
    if t in starts: res.setdefault(t,[]).append(a)
json.dump({f"0x{k:x}":sorted(set(v)) for k,v in sorted(res.items())}, open(dest,"w"), indent=0)
print("destinos:", len(res))
