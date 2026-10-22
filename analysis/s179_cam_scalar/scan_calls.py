#!/usr/bin/env python3
"""S179 - llamadas (bl) desde las 14 funciones emisoras + clasificacion de destinos."""
import json, bisect
from capstone import *
from capstone.arm import *
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail=True
fm=json.load(open("analysis/s179_cam_scalar/func_map.json"))
funcs=[(int(f["func"],16), f["n_sitios"], f["sitios"]) for f in fm["funciones"]]
def dis(lo,hi): return list(md.disasm(B[lo-BASE:lo-BASE+(hi-lo)],lo))
# limites: usar el siguiente inicio de funcion del mapa global de bl? approximacion: 0x400 bytes
starts=sorted(set([f[0] for f in funcs]) | set(
    [0x4380a688]))
# 확장: obtener todos los inicios de funcion globales como en scan_funcmap
import importlib.util
spec=importlib.util.spec_from_file_location("sfm","analysis/s179_cam_scalar/scan_funcmap.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
starts=sorted(set(m.func_starts(0x43541000,0x44017000)) | m.all_bl_targets())
cl=[]
for x in starts:
    if cl and x-cl[-1][-1]<=8: cl[-1].append(x)
    else: cl.append([x])
starts=sorted(c[0] for c in cl)
def fstart(a):
    i=bisect.bisect_right(starts,a)-1
    return starts[i] if i>=0 else None
allcalls={}
for f,n,ss in funcs:
    nxt=[s for s in starts if s>f]
    end=nxt[0] if nxt else f+0x1000
    if end-f>0x4000: end=f+0x4000
    ins=dis(f,end)
    calls=sorted(set(i.operands[0].imm for i in ins if i.mnemonic in ("bl","blx") and i.operands and i.operands[0].type==ARM_OP_IMM))
    allcalls[hex(f)]={"n":n,"calls":[hex(c) for c in calls],"fin":hex(f),"fin_end":hex(end)}
    print(f"0x{f:08x} n={n} end=0x{end:08x} -> {len(calls)} llamadas")
# clasificacion por zona
ZONES=[(0x43541000,0x435a0000,"libc/osal/otro"),(0x435a0000,0x43600000,"lib"),
       (0x43800000,0x43810000,"cam-core(HAPI/Fn)"),(0x43810000,0x43900000,"cam-core2"),
       (0x43900000,0x43a00000,"SA/infra"),(0x43a00000,0x43b00000,"otro"),
       (0x43b00000,0x43c00000,"util"),(0x43c00000,0x44017000,"datos/rodata")]
def zone(a):
    for lo,hi,n in ZONES:
        if lo<=a<hi: return n
    return "?"
from collections import Counter
cnt=Counter()
for f,info in allcalls.items():
    for c in info["calls"]:
        cnt[zone(int(c,16))]+=1
print(cnt)
json.dump(allcalls,open("analysis/s179_cam_scalar/calls.json","w"),indent=1)
