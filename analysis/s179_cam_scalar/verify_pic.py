#!/usr/bin/env python3
"""S179 - verificacion a mano de los pares PIC (regla estricta) con capstone detail=True.

Para cada sitio (direccion del 'add rX,pc') se comprueba:
  (a) el 'ldr rX,[pc,#imm]' MAS CERCANO por detras del mismo registro,
  (b) el valor W del pool de literales,
  (c) destino = W + (add + 4) == direccion esperada,
  (d) el registro NO se reescribe entre el ldr y el add.
"""
import json, struct, sys
from capstone import *
from capstone.arm import *
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail=True

def dis(lo,hi):
    return list(md.disasm(B[lo-BASE:lo-BASE+(hi-lo)], lo))

def cstr(a):
    o=a-BASE; e=o
    while e<len(B) and 32<=B[e]<127: e+=1
    return B[o:e].decode("latin1")

WRITES={"mov","movs","mov.w","movt","movw","mvn","ldr","ldr.w","str","str.w","strb","strh","add","adds","add.w",
 "sub","subs","sub.w","orr","orrs","and","ands","eor","bic","mul","muls","rsb","lsl","lsr","asr","uxtb","uxth",
 "sxtb","sxth","pop","pop.w","ldm","ldmia","ldmia.w","ldmdb","ldm.w","stm","stmdb","stm.w","ldrex","rev","rrx"}

def window(addsite):
    """devuelve la lista de instrucciones de una ventana que decodifica bien en 'addsite'"""
    for off in range(120,0,-2):
        ins=dis(addsite-off, addsite+4)
        for i in ins:
            if i.address==addsite and i.mnemonic=="add" and len(i.operands)==2 \
               and i.operands[1].type==ARM_OP_REG and i.operands[1].reg==ARM_REG_PC:
                return ins,i
    return None,None

def verify(addsite, expected):
    ins,add=window(addsite)
    if add is None: return False,"no add rX,pc decodificable",None,None
    rd=add.operands[0].reg
    ldrs=[]
    for i in ins:
        if i.address>=addsite: break
        if i.mnemonic.startswith("ldr") and len(i.operands)==2 and i.operands[1].type==ARM_OP_MEM \
           and i.operands[1].mem.base==ARM_REG_PC and i.operands[0].reg==rd:
            ldrs.append(i)
    if not ldrs: return False,"sin ldr del mismo registro",None,None
    ldr=ldrs[-1]
    lit=((ldr.address+4)&~3)+ldr.operands[1].mem.disp
    W=struct.unpack_from("<I",B,lit-BASE)[0]
    tgt=(W+(addsite+4))&0xFFFFFFFF
    kill=None
    for i in ins:
        if i.address<=ldr.address or i.address>=addsite: continue
        if i.mnemonic in WRITES and i.operands and i.operands[0].type==ARM_OP_REG and i.operands[0].reg==rd:
            kill=i; break
    info=f"ldr=0x{ldr.address:08x} pool=0x{lit:08x} W=0x{W:08x} tgt=0x{tgt:08x} r={rd}"
    return (tgt==expected), info, kill, ldr

rows=json.load(open("analysis/s179_cam_scalar/pic_full.json"))
allp=[]
for r in rows:
    for s in r["sitios_nuevo"]: allp.append((int(s,16), int(r["vaddr"],16), r["texto"], "nuevo"))
    for s in r["sitios_gemelo"]: allp.append((int(s,16), int(r["gemelo"],16), r["gemelo_texto"], "gemelo"))
allp.sort()
res=[]; fails=0; kills=0
for site,exp,txt,kind in allp:
    ok,info,kill,ldr=verify(site,exp)
    if not ok: fails+=1
    if kill is not None: kills+=1
    res.append({"site":hex(site),"target":hex(exp),"kind":kind,"ok":ok,"info":info,
                "kill":(hex(kill.address) if kill else None),
                "ldr":(hex(ldr.address) if ldr else None),"texto":txt})
    if not ok or kill is not None:
        print(f"  {'OK ' if ok else 'FAIL'} {hex(site)} -> {hex(exp)}  {info}  kill={kill.address if kill else None}")
json.dump(res,open("analysis/s179_cam_scalar/pic_verified.json","w"),indent=1)
print(f"pares verificados: {len(res)}  fallos: {fails}  reuso de registro: {kills}")
