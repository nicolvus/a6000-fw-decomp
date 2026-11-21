#!/usr/bin/env python3
"""Réplica fuera de línea de una sesión del arnés (G75 T62): arranca la LIRO VM, reinyecta las `entra` de un avcam.jsonl en su tiempo virtual y vuelca (≈15 s) los valores que toma 0x43796954 en su gancho 0x43796c9a. Uso: replica.py avcam.jsonl t_fin_ms."""
sys.path.insert(0,'scripts/gui/avcam')
import puente, liro_vm as L
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
src=sys.argv[1]; tfin=float(sys.argv[2])
vm,t0=puente.arranca(None)
rd=lambda a,n=4: int.from_bytes(bytes(vm.uc.mem_read(a,n)),'little')
seen=collections.OrderedDict()
def h(uc,addr,size,_):
    r4=uc.reg_read(UC_ARM_REG_R4)
    try:
        p=rd(r4); a=rd(r4+4); b=rd(r4+8)
        k=(rd(p,2), rd(b+0x1ed,1), rd(b+0x1d4), rd(rd(a)+0x10) if False else rd(a+0x10), rd(b+0x26c,2), uc.reg_read(UC_ARM_REG_R11), uc.reg_read(UC_ARM_REG_R10)!=0)
    except Exception as e:
        k=('err',str(e))
    if k not in seen: seen[k]=[round(vm.t,2),0]
    seen[k][1]+=1
vm.uc.hook_add(UC_HOOK_CODE,h,None,0x43796c9a,0x43796c9b)
recs=[json.loads(l) for l in open(src)]
ent=[r for r in recs if 'entra' in r]
for r in ent:
    if r['t']>tfin: break
    vm.limite=r['t']; L.planifica(vm,20_000_000)
    q=int(r['entra'],16); tam=len(r['datos'])//2
    m=vm.malloc(max(tam,0x40)+12+0x20)+12
    vm.uc.mem_write(m-12,bytes.fromhex(r['cab'])); vm.uc.mem_write(m,bytes.fromhex(r['datos'])[:tam]); vm.msz[m]=tam
    L.entrega(vm,q,m)
vm.limite=tfin; L.planifica(vm,50_000_000)
print('t final',vm.t,'seq',hex(rd(0x43ede338)),'dest',hex(rd(0x43ede320)),'mod0',hex(rd(0x43e9bd58,2)))
for k,v in seen.items(): print(k,v)
