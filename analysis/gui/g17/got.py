"""Resuelve r5 (GOT) del conversor y la entrada GOT del caso; muestra reubicación y símbolo."""
import struct,subprocess,sys,re
L=sys.argv[1]; d=open(L,'rb').read()
def u32(a): return struct.unpack_from('<I',d,a)[0]
conv,case=int(sys.argv[2],16),int(sys.argv[3],16)
# ldr.w r5,[pc,#imm] at conv+6 ; add r5,pc at conv+0x12
from capstone import *
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
ins=list(md.disasm(d[conv:conv+0x20],conv))
ld=[i for i in ins if i.mnemonic.startswith('ldr') and i.op_str.startswith('r5, [pc')][0]
ad=[i for i in ins if i.mnemonic=='add' and i.op_str=='r5, pc'][0]
r5=(u32(((ld.address+4)&~3)+int(ld.op_str.split('#')[1].rstrip(']'),16))+ad.address+4)&0xffffffff
c=next(md.disasm(d[case:case+4],case))
lit=u32(((c.address+4)&~3)+int(c.op_str.split('#')[1].rstrip(']'),16))
got=(r5+lit)&0xffffffff
# vaddr->offset (segmento RW desplazado)
segs=[]
for l in subprocess.run(['readelf','-lW',L],capture_output=True,text=True).stdout.splitlines():
    f=l.split()
    if f and f[0]=='LOAD': segs.append((int(f[1],16),int(f[2],16),int(f[4],16)))
off=next(o+(got-v) for o,v,s in segs if v<=got<v+s)
rel=subprocess.run(['readelf','-rW',L],capture_output=True,text=True).stdout
m=[l for l in rel.splitlines() if l.startswith(f'{got:08x}')]
print('GOT',hex(got),'valor',hex(u32(off)),'reloc',m[:1])
