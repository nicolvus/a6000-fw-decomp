import re
from capstone import *
b=open('analysis/rea-independent/input/av-cam.bin','rb').read(); base=0x43541000
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB); md.skipdata=True
ins=list(md.disasm(b[:0x9c0000],base))
OFF=set(range(0x230,0x244))|set(range(0x278,0x28c))
callees=set(); res=[]
for k,i in enumerate(ins):
    if i.mnemonic=='bl' and i.op_str in('#0x43804de8','#0x43804c38'):
        regs={'r0'}
        for j in ins[k+1:k+80]:
            o=j.op_str
            if j.mnemonic in('pop','pop.w') and 'pc' in o: break
            m=re.match(r'(r\d+|sb|sl|fp|ip), (r\d+)$',o)
            if j.mnemonic.startswith('mov') and m and m.group(2) in regs: regs.add(m.group(1))
            elif j.mnemonic.startswith('mov') and m and m.group(1) in regs: regs.discard(m.group(1))
            mm=re.search(r'\[(\w+), #(0x[0-9a-f]+)\]',o)
            if mm and mm.group(1) in regs and int(mm.group(2),16) in OFF: res.append((hex(i.address),hex(j.address),j.mnemonic,o))
            if j.mnemonic.startswith('add') and re.match(r'(\w+), (\w+), #(0x[0-9a-f]+)$',o):
                a=re.match(r'(\w+), (\w+), #(0x[0-9a-f]+)$',o)
                if a.group(2) in regs and int(a.group(3),16) in OFF: res.append((hex(i.address),hex(j.address),j.mnemonic,o))
            if j.mnemonic=='bl' and 'r0' in regs and j is not None and j.op_str.startswith('#'): callees.add(j.op_str)
            if j.mnemonic=='bl': regs.discard('r0')
print(res); print(len(callees))
for c in sorted(callees):
    a=int(c[1:],16)
    if not(base<=a<base+len(b)): continue
    for j in md.disasm(b[a-base:a-base+400],a):
        mm=re.search(r'#(0x[0-9a-f]+)\]?$',j.op_str)
        if mm and int(mm.group(1),16) in OFF and j.mnemonic.startswith(('ldr','str','add')): print('callee',c,hex(j.address),j.mnemonic,j.op_str)
