#!/usr/bin/env python3
"""Índice de referencias a datos en av-cam (Thumb): resuelve `ldr rN,[pc,#i]; add rN,pc` y GOT `ldr rB,[pc];add rB,pc; ldr rN,[pc]; ldr rD,[rB,rN]`.
Salida xidx.pkl: {dirección_destino: [direcciones de instrucción]}. Heurística de ventana (<=14 instr), sin flujo: puede perder casos."""
import re,struct,pickle,collections
B=0x43541000; d=open('../../rea-independent/input/av-cam.bin','rb').read()
def w(a): return struct.unpack_from('<I',d,a-B)[0] if B<=a<B+len(d)-4 else None
ins=[]
for l in open('av.dis'):
    m=re.match(r'([0-9a-f]+): (?:[0-9a-f]{4} )+(\S+)\s*(.*)',l.strip())
    if m: ins.append((int(m.group(1),16),m.group(2),m.group(3)))
idx=collections.defaultdict(list); n=len(ins)
rl=re.compile(r'(r\d+), \[pc, #(0x[0-9a-f]+)\]'); ra=re.compile(r'(r\d+), pc$'); rg=re.compile(r'(r\d+), \[(r\d+), (r\d+)\]')
for i,(a,op,args) in enumerate(ins):
    m=rl.match(args)
    if not (m and op.startswith('ldr')): continue
    reg=m.group(1); lit=w(((a+4)&~3)+int(m.group(2),16))
    if lit is None: continue
    for j in range(i+1,min(i+14,n)):
        a2,op2,ar2=ins[j]
        if op2=='add' and ra.match(ar2) and ra.match(ar2).group(1)==reg: idx[(a2+4+lit)&0xffffffff].append(a2); base=(reg,(a2+4+lit)&0xffffffff); break
        mm=rg.match(ar2)
        if op2.startswith('ldr') and mm and mm.group(3)==reg: pass  # GOT: base reg desconocido aquí; se resuelve abajo
    # GOT: ldr rN,[rB,rN] con rB conocido por add previo
pickle.dump(dict(idx),open('xidx_pc.pkl','wb'))
# segunda pasada GOT: seguimiento de registros base
regs={}; got=collections.defaultdict(list)
for i,(a,op,args) in enumerate(ins):
    if op.startswith('push') or op.startswith('bl'): regs={} if op.startswith('push') else regs
    m=rl.match(args)
    if m and op.startswith('ldr'): regs[m.group(1)]=('lit',w(((a+4)&~3)+int(m.group(2),16)))
    elif op=='add' and ra.match(args):
        r=ra.match(args).group(1)
        if r in regs and regs[r][0]=='lit' and regs[r][1] is not None: regs[r]=('base',(a+4+regs[r][1])&0xffffffff)
    else:
        mm=rg.match(args)
        if mm and op.startswith('ldr'):
            rd,rb,ro=mm.groups()
            for x,y in ((rb,ro),(ro,rb)):
                if regs.get(x,('',))[0]=='base' and regs.get(y,('',))[0]=='lit' and regs[y][1] is not None:
                    ga=(regs[x][1]+regs[y][1])&0xffffffff; p=w(ga)
                    if p: got[p].append(a); regs[rd]=('ptr',p); break
pickle.dump(dict(got),open('xidx_got.pkl','wb'))
print(len(idx),len(got))
