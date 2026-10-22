#!/usr/bin/env python3
"""S179 - id de modulo / nivel / flag de cada traza [CAM_SCALAR] (evaluacion simbolica simple)."""
import json
from capstone import *
from capstone.arm import *
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail=True
def dis(lo,hi): return list(md.disasm(B[lo-BASE:lo-BASE+(hi-lo)],lo))
def win(site):
    for off in range(140,0,-2):
        ins=dis(site-off,site+4)
        for i in ins:
            if i.address==site and i.mnemonic=="add" and len(i.operands)==2 and i.operands[1].type==ARM_OP_REG and i.operands[1].reg==ARM_REG_PC:
                return ins,i
    return None,None
REG={ARM_REG_R0:0,ARM_REG_R1:1,ARM_REG_R2:2,ARM_REG_R3:3,ARM_REG_R4:4,ARM_REG_R5:5,ARM_REG_R6:6,ARM_REG_R7:7}
rows=json.load(open("analysis/s179_cam_scalar/pic_full.json"))
res=[];bad=0
for r in rows:
    for s in r["sitios_nuevo"]:
        site=int(s,16); ins,add=win(site)
        # retroceder hasta el bl al logger 0x4380a5d0
        idx=[i for i in ins if i.address<site]
        bl=None
        for i in reversed(idx):
            if i.mnemonic in ("bl","blx") and i.op_str.startswith("#0x4380a5d0"):
                bl=i; break
        vals={0:None,1:None,2:None}
        if bl:
            for i in ins:
                if i.address<=bl.address or i.address>=site: continue
                if i.mnemonic in ("movs","mov") and len(i.operands)==2 and i.operands[0].type==ARM_OP_REG and i.operands[0].reg in REG \
                   and i.operands[1].type==ARM_OP_IMM:
                    vals[REG[i.operands[0].reg]]=i.operands[1].imm
                elif i.mnemonic in ("adds","add") and len(i.operands)==2 and i.operands[0].type==ARM_OP_REG and i.operands[0].reg in REG \
                   and i.operands[1].type==ARM_OP_IMM:
                    v=vals[REG[i.operands[0].reg]]
                    vals[REG[i.operands[0].reg]] = (v + i.operands[1].imm) if (v is not None and i.operands[1].imm<0) else None
                elif i.mnemonic in ("movs","mov") and len(i.operands)==2 and i.operands[0].type==ARM_OP_REG and i.operands[0].reg in REG:
                    vals[REG[i.operands[0].reg]]=None
        res.append({"site":s,"vaddr":r["vaddr"],"bl":hex(bl.address) if bl else None,
                    "modulo":vals[0],"nivel":vals[1],"flag":vals[2],"texto":r["texto"]})
        if not (vals[0]==5 and vals[1]==6 and vals[2]==1): bad+=1
json.dump(res,open("analysis/s179_cam_scalar/levels.json","w"),indent=1)
from collections import Counter
print(Counter((x["modulo"],x["nivel"],x["flag"]) for x in res))
print("sitios no (5,6,1):",bad,"de",len(res))
