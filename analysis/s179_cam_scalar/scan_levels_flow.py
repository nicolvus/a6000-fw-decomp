import json
from capstone import *
from capstone.arm import *
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail=True
REG={ARM_REG_R0:0,ARM_REG_R1:1,ARM_REG_R2:2}
rows=json.load(open("analysis/s179_cam_scalar/pic_full.json"))
ok=0; bad=[]
for r in rows:
    for s in r["sitios_nuevo"]:
        site=int(s,16)
        win=None
        for off in range(200,0,-2):
            ins=list(md.disasm(B[site-off-BASE:site+40-BASE],site-off))
            if any(i.address==site and i.mnemonic=="add" and len(i.operands)==2 and i.operands[1].type==ARM_OP_REG and i.operands[1].reg==ARM_REG_PC for i in ins):
                win=ins; break
        seq=[i for i in win if i.address<site]
        vals={}
        for i in seq:
            ops=i.operands
            if not ops or ops[0].type!=ARM_OP_REG or ops[0].reg not in REG: continue
            rr=REG[ops[0].reg]
            if i.mnemonic in ("movs","mov","mov.w") and len(ops)==2:
                vals[rr]= ops[1].imm if ops[1].type==ARM_OP_IMM else None
            elif i.mnemonic in ("adds","add") and len(ops)==2 and ops[1].type==ARM_OP_IMM:
                v=vals.get(rr)
                vals[rr]= (v+ops[1].imm) if (v is not None and i.mnemonic=="adds" and ops[1].imm>0) else None
            elif i.mnemonic.startswith("ldr"): vals[rr]=None
        bl=None
        for i in win:
            if i.address<=site: continue
            if i.mnemonic in ("bl","blx") and i.op_str.startswith("#0x"):
                bl=i; break
        if vals.get(0)==5 and vals.get(1)==6 and vals.get(2)==1: ok+=1
        else: bad.append((hex(site), hex(bl.address) if bl else None, vals))
print("confirmados (5,6,1):",ok,"de 47")
for b in bad: print("  ",b)
