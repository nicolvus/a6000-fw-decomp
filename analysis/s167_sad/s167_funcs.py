#!/usr/bin/env python3
"""S167 —EWICE: mapa función→cadenas del módulo [SAD] con la regla PIC estricta."""
import bisect, json
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
U16=__import__("struct").Struct("<H").unpack_from
GM={int(k,16):sorted(set(v)) for k,v in json.load(open("analysis/s167_sad/pic_a6000.json")).items()}
def cstr(a):
    o=a-BASE
    if o<0 or o>=len(B): return None
    e=B.find(b"\x00",o); return B[o:e].decode("latin1")
def prologues(lo,hi):
    out=[];a=lo
    while a<hi:
        o=a-BASE
        h=U16(B,o)[0]
        if (h & 0xFE00)==0xB400 and (h & 0x0100): out.append(a); a+=2; continue
        if h==0xE92D:
            h2=U16(B,o+2)[0]
            if h2 & 0x4000: out.append(a)
        a+=2
    return out
P=prologues(0x43990000,0x439a2000)
def fstart(site):
    i=bisect.bisect_right(P,site)-1
    return P[i] if i>=0 else None
def fend(f):
    i=bisect.bisect_right(P,f)
    return P[i] if i<len(P) else None
EM=[0x43998578,0x4399d464,0x4399d528,0x4399d618,0x439a119c]
#_strings_ de cada función (todas las cadenas referenciadas por PIC dentro de su rango)
for f in EM:
    end=fend(f) or 0x439a2000
    ss=[]
    for dest,sites in GM.items():
        for s in sites:
            if f<=s<end:
                ss.append((s,dest,cstr(dest)))
    ss.sort()
    print(f"=== func {f:#x} .. {end:#x}  ({len(ss)} sitios)")
    for s,d,t in ss:
        print(f"   {s:#x} -> {d:#x} {t!r}")
