"""Recursive-descent disassembler for the Thumb-2 code of libmpr.so (no symbols)."""
import re
from capstone import *
LIB='analysis/camera-extract/usr/lib/libmpr.so'
_f=open(LIB,'rb'); _data=_f.read()
def read(va,n):
    return _data[va:va+n] if 0<=va<len(_data) else b''
_MD=Cs(CS_ARCH_ARM,CS_MODE_THUMB+CS_MODE_LITTLE_ENDIAN)
# first segment: VA == file offset, ends at 0x9bb1c8
CODE_LO, CODE_HI = 0x0, 0x9bb1c8

def funcs_from(entry, maxins=4000):
    seen={}; work=[entry]
    order=[]
    while work:
        a=work.pop()
        while a not in seen and len(seen)<maxins:
            code=read(a,4)
            if not code: break
            ins=next(_MD.disasm(code,a),None)
            if ins is None or ins.address!=a: break
            seen[a]=ins; order.append(a)
            m=ins.mnemonic
            if m.startswith('pop') and 'pc' in ins.op_str: break
            if m=='bx' and ins.op_str=='lr': break
            if m in ('b','b.w') and ins.op_str.startswith('#'):
                t=int(ins.op_str[1:],16)
                if CODE_LO<=t<CODE_HI and t!=a: work.append(t)
                break
            COND=('beq','bne','bcs','bhs','bcc','blo','bmi','bpl','bvs','bvc','bhi','bls','bge','blt','bgt','ble','beq.w','bne.w','bmi.w','bpl.w','bge.w','blt.w','bgt.w','ble.w','bhi.w','bls.w','cbz','cbnz','tbz','tbnz')
            mm=re.search(r'#(0x[0-9a-f]+)$', ins.op_str)
            if m in COND and mm:
                t=int(mm.group(1),16)
                if CODE_LO<=t<CODE_HI: work.append(t)
            if m in ('bl','blx') and ins.op_str.startswith('#'):
                t=int(ins.op_str[1:],16)
                if CODE_LO<=t<CODE_HI: _CALLS.append((a,t))
            a=ins.address+ins.size
    order.sort()
    return [seen[x] for x in order]

_CALLS=[]
def dump(entry, maxins=4000, show_calls=True):
    global _CALLS
    _CALLS=[]
    ins=funcs_from(entry,maxins)
    print("=== func %#x: %d instrs, %#x..%#x ==="%(entry,len(ins),ins[0].address,ins[-1].address))
    for i in ins: print("%08x  %-8s %s"%(i.address,i.mnemonic,i.op_str))
    if show_calls: print("calls:", [hex(t) for _,t in _CALLS])
    return ins
if __name__=='__main__':
    import sys
    dump(int(sys.argv[1],0), int(sys.argv[2]) if len(sys.argv)>2 else 4000)
