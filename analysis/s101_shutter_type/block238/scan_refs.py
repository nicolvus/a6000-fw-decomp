# S70: referencias PC-relativas al bloque 0x43edf684 (lento: ~3 min). Resultado: 62 sitios, todos en 0x43802000-0x43805000.
import struct,re,sys
from capstone import *
b=open('analysis/rea-independent/input/av-cam.bin','rb').read(); base=0x43541000
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB); md.skipdata=True; md.detail=True
T0,T1=0x43edf684,0x43edf684+0x700
ins=list(md.disasm(b[:0x9c0000],base))
hits=[]
pend={}
for k,i in enumerate(ins):
    if i.mnemonic.startswith('ldr') and 'pc' in i.op_str and '#' in i.op_str and i.op_str.startswith('r'):
        m=re.match(r'(r\d+), \[pc, #(0x[0-9a-f]+|\d+)\]',i.op_str)
        if m:
            la=((i.address+4)&~3)+int(m.group(2),0)
            if la-base+4<=len(b):
                pend[m.group(1)]=(struct.unpack('<I',b[la-base:la-base+4])[0],k)
    elif i.mnemonic=='add' and i.op_str.endswith(', pc'):
        r=i.op_str.split(',')[0]
        if r in pend and k-pend[r][1]<12:
            t=(pend[r][0]+i.address+4)&0xffffffff
            if T0<=t<T1: hits.append((i.address,t,r))
for a,t,r in hits: print(hex(a),hex(t),r)
