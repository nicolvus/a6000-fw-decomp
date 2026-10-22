#!/usr/bin/env python3
"""S179 - id de modulo / nivel / flag por traza, con propagacion de constantes desde el inicio de funcion."""
import bisect, json
from capstone import *
from capstone.arm import *
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail=True
REG={ARM_REG_R0:0,ARM_REG_R1:1,ARM_REG_R2:2,ARM_REG_R3:3,ARM_REG_R4:4,ARM_REG_R5:5,ARM_REG_R6:6,ARM_REG_R7:7,
     ARM_REG_R8:8,ARM_REG_R9:9,ARM_REG_R10:10,ARM_REG_R11:11}
fm=json.load(open("analysis/s179_cam_scalar/func_map.json"))
starts=sorted(int(f["func"],16) for f in fm["funciones"])
def func_of(a):
    i=bisect.bisect_right(starts,a)-1
    return starts[i] if i>=0 else None
def dis(lo,hi): return list(md.disasm(B[lo-BASE:lo-BASE+(hi-lo)],lo))

def consts_before(site, fstart):
    ins=dis(fstart, site+4)
    v={}
    for i in ins:
        if i.address>=site: break
        ops=i.operands
        if not ops: continue
        d=ops[0]
        if d.type!=ARM_OP_REG or d.reg not in REG: continue
        r=REG[d.reg]
        if i.mnemonic in ("movs","mov","mov.w") and len(ops)==2:
            if ops[1].type==ARM_OP_IMM: v[r]=ops[1].imm
            elif ops[1].type==ARM_OP_REG and REG.get(ops[1].reg) in v: v[r]=v[REG[ops[1].reg]]
            else: v[r]=None
        elif i.mnemonic in ("adds","add","add.w","subs","sub","sub.w") and len(ops)==2 and ops[1].type==ARM_OP_IMM:
            b=v.get(r)
            v[r] = (b+ops[1].imm) if (b is not None and i.mnemonic.startswith("add")) else None
        elif i.mnemonic in ("movw","movt"):
            v[r]=None
        elif i.mnemonic.startswith("ldr") or i.mnemonic.startswith("str") or i.mnemonic in ("bl","blx","pop","pop.w","ldm","ldmia","ldmia.w","ldmdb","stm","stmdb","stm.w","cmp","cmn","tst","cbz","cbnz","uxtb","uxth","sxtb","sxth","and","orr","eor","bic","mvn","mul","lsl","lsr","asr","rsb","teq","tst"):
            if i.mnemonic.startswith("ldr"): v[r]=None
    return v

rows=json.load(open("analysis/s179_cam_scalar/pic_full.json"))
res=[]; from collections import Counter
cnt=Counter()
for r in rows:
    for s in r["sitios_nuevo"]:
        site=int(s,16); fs=func_of(site)
        v=consts_before(site, fs)
        key=(v.get(0),v.get(1),v.get(2))
        cnt[key]+=1
        res.append({"site":s,"vaddr":r["vaddr"],"func":hex(fs),"modulo":key[0],"nivel":key[1],"flag":key[2],"texto":r["texto"]})
print(cnt)
json.dump(res,open("analysis/s179_cam_scalar/levels.json","w"),indent=1)
