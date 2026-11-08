"""Conversor 0x4066 de libObj: por cada clave de ParamList (movw r1,#K ; blx get) el byte del buffer (strb rX,[r4,#B]) que rellena."""
import sys,re
from capstone import *
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
def fields(d,start,end):
    out=[]; key=None
    for i in md.disasm(d[start:end],start):
        m=re.match(r'r1, #(0x[0-9a-f]+)$',i.op_str)
        if i.mnemonic in('movw','movs','mov.w') and m and int(m.group(1),16)>=0x9000: key=int(m.group(1),16)
        m=re.match(r'r\d+, \[r4, #(0x[0-9a-f]+)\]',i.op_str)
        if i.mnemonic.startswith('strb') and m and key is not None: out.append((key,int(m.group(1),16)))
    seen={}
    for k,b in out: seen.setdefault(k,set()).add(b)
    return seen
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read(); s=int(sys.argv[2],16); e=int(sys.argv[3],16)
    for k,v in sorted(fields(d,s,e).items()): print(hex(k),sorted(hex(x) for x in v))
