#!/usr/bin/env python3
"""S179 - escaner PIC estricto LOCAL que acepta destinos en cadenas prefijadas y en sus gemelos +14."""
import bisect, json, os, struct
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE=0x43541000
B=open(os.path.join(ROOT,"analysis/rea-independent/input/av-cam.bin"),"rb").read()
N=len(B); U16=struct.Struct("<H").unpack_from; U32=struct.Struct("<I").unpack_from
LO,HI=0x43541000,0x44017000
MAXGAP=4096

def string_starts(lo,hi):
    out=set(); prev=False
    for i in range(max(0,lo-BASE),min(N,hi-BASE)):
        c=B[i]; cur=32<=c<127
        if cur and not prev: out.add(BASE+i)
        prev=cur
    return out

def ldr_sites(lo,hi):
    out=[]; a=lo
    while a<hi:
        o=a-BASE
        if o<0 or o>N-8: a+=2; continue
        h=U16(B,o)[0]; reg=lit=None
        if (h&0xF800)==0x4800:
            reg=(h>>8)&7; lit=((a+4)&~3)+((h&0xFF)*4)
        elif (h&0xFF7F)==0xF85F:
            h2=U16(B,o+2)[0]; reg=(h2>>12)&0xF; lit=((a+4)&~3)+((((h2>>8)&0xF)<<8)|(h2&0xFF))
        if reg is not None:
            o2=lit-BASE
            if 0<=o2<=N-4: out.append((a,reg,U32(B,o2)[0]))
        a+=2
    return out

def add_sites(lo,hi):
    out=[]; a=lo
    while a<hi:
        o=a-BASE
        if o<0 or o>N-4: a+=2; continue
        h=U16(B,o)[0]
        if (h&0xFF00)==0x4400 and ((h>>3)&0xF)==15:
            out.append((a,(((h>>7)&1)<<3)|(h&7)))
        a+=2
    return out

def scan(lo,hi):
    starts=string_starts(0,0xFFFFFFFF)
    ldrs=ldr_sites(lo,hi); adds=add_sites(lo,hi)
    by={}
    for a,reg,w in ldrs: by.setdefault(reg,[]).append((a,w))
    for v in by.values(): v.sort()
    keys={r:[x[0] for x in v] for r,v in by.items()}
    out={}
    for a,reg in adds:
        v=by.get(reg)
        if not v: continue
        ks=keys[reg]; i=bisect.bisect_left(ks,a)-1
        if i<0: continue
        la,w=v[i]
        if a-la>MAXGAP: continue
        tgt=(w+(a+4))&0xFFFFFFFF
        out.setdefault(tgt,[]).append(a)
    return out,starts

if __name__=="__main__":
    S=json.load(open(os.path.join(ROOT,"analysis/s179_cam_scalar/strings_raw.json")))["A6000"]
    dests={}
    for s in S:
        a=s["vaddr"]; dests[a]=[a]; dests[a+14]=[a+14]
    res,starts=scan(LO,HI)
    G=json.load(open(os.path.join(ROOT,"analysis/s106_imaging_cap/pic_refs_strict_global.json")))
    Gm={int(k,16):v for k,v in G.items()}
    out=[]
    for s in S:
        a=s["vaddr"]; t=a+14
        sn=sorted(set(res.get(a,[]))); st=sorted(set(res.get(t,[])))
        # comparacion con el mapa global (solo valido para inicios de cadena)
        gm=[x for x in Gm.get(a,[])]
        ok = (sn==sorted(set(gm)))
        print(f"0x{a:08x} nuevos={len(sn)} {[hex(x) for x in sn]}  gemelo_sitios={len(st)} {[hex(x) for x in st]}  global_ok={ok}")
        out.append({"vaddr":hex(a),"texto":s["text"],"gemelo":hex(t),
                    "sitios_nuevo":[hex(x) for x in sn],"sitios_gemelo":[hex(x) for x in st],
                    "global_ok":ok,"n_sitios_nuevo":len(sn),"n_sitios_gemelo":len(st)})
    json.dump(out,open(os.path.join(ROOT,"analysis/s179_cam_scalar/pic_full.json"),"w"),indent=1)
    print("TOTAL nuevos:",sum(r['n_sitios_nuevo'] for r in out)," gemelos:",sum(r['n_sitios_gemelo'] for r in out))
    print("cadenas con >=1 sitio (nuevo):",sum(1 for r in out if r['n_sitios_nuevo']))
    print("discrepancias vs global:",sum(1 for r in out if not r['global_ok']))
