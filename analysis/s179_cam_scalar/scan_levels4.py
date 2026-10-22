#!/usr/bin/env python3
"""S179 - nivel/flag por traza: busqueda hacia atras de la definicion mas cercana de r1 y r2."""
import json
from capstone import *
from capstone.arm import *
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail=True
REG={ARM_REG_R0:0,ARM_REG_R1:1,ARM_REG_R2:2,ARM_REG_R3:3}
def win(site):
    for off in range(140,0,-2):
        ins=list(md.disasm(B[site-off-BASE:site+4-BASE],site-off))
        for i in ins:
            if i.address==site and i.mnemonic=="add" and len(i.operands)==2 and i.operands[1].type==ARM_OP_REG and i.operands[1].reg==ARM_REG_PC:
                return ins,i
    return None,None
rows=json.load(open("analysis/s179_cam_scalar/pic_full.json"))
res=[]; from collections import Counter
cnt=Counter(); unknown=[]
for r in rows:
    for s in r["sitios_nuevo"]:
        site=int(s,16); ins,add=win(site)
        idx=[i for i in ins if i.address<site]
        bl=None
        for i in reversed(idx):
            if i.mnemonic in ("bl","blx") and "0x4380a5d0" in i.op_str: bl=i; break
        seq=[i for i in ins if bl and bl.address<i.address<site]
        vals={}
        for i in seq:
            ops=i.operands
            if not ops or ops[0].type!=ARM_OP_REG or ops[0].reg not in REG: continue
            r0=REG[ops[0].reg]
            if i.mnemonic in ("movs","mov","mov.w") and len(ops)==2:
                vals[r0]= ops[1].imm if ops[1].type==ARM_OP_IMM else None
            elif i.mnemonic in ("adds","add") and len(ops)==2 and ops[1].type==ARM_OP_IMM:
                vals[r0]=None
        key=(vals.get(0),vals.get(1),vals.get(2))
        cnt[key]+=1
        res.append({"site":s,"vaddr":r["vaddr"],"modulo":key[0],"nivel":key[1],"flag":key[2],"texto":r["texto"]})
        if key[1] is None or key[2] is None:
            unknown.append((s,[f"{hex(i.address)} {i.mnemonic} {i.op_str}" for i in seq]))
print(cnt)
for s,seq in unknown[:12]:
    print(s, seq)
json.dump(res,open("analysis/s179_cam_scalar/levels.json","w"),indent=1)
