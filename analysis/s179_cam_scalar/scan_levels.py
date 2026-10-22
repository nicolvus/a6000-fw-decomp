#!/usr/bin/env python3
"""S179 - constantes (id de modulo, nivel, flag) en cada sitio de traza [CAM_SCALAR]."""
import json, struct
from capstone import *
from capstone.arm import *
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail=True
def dis(lo,hi): return list(md.disasm(B[lo-BASE:lo-BASE+(hi-lo)],lo))
def win(site):
    for off in range(120,0,-2):
        ins=dis(site-off,site+4)
        for i in ins:
            if i.address==site and i.mnemonic=="add" and len(i.operands)==2 and i.operands[1].type==ARM_OP_REG and i.operands[1].reg==ARM_REG_PC:
                return ins,i
    return None,None
rows=json.load(open("analysis/s179_cam_scalar/pic_full.json"))
out=[]
for r in rows:
    for s in r["sitios_nuevo"]:
        site=int(s,16); ins,add=win(site)
        ctx=[]
        for i in ins:
            if site-40<=i.address<site:
                ctx.append(f"0x{i.address:x} {i.mnemonic} {i.op_str}")
        out.append({"site":s,"vaddr":r["vaddr"],"texto":r["texto"],"ctx":ctx})
        print(f"--- {s} -> {r['vaddr']}  {r['texto'][:60]}")
        for c in ctx: print("     ",c)
json.dump(out,open("analysis/s179_cam_scalar/levels.json","w"),indent=1)
