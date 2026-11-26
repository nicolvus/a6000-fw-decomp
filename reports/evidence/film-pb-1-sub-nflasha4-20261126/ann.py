"""Annotated Thumb-2 disassembly of libmpr.so: resolves ldr [pc,#] literals, follows bl."""
import struct, importlib.util
from capstone import *
import os
spec=importlib.util.spec_from_file_location("rd", os.path.join(os.path.dirname(os.path.abspath(__file__)),"recdesc.py"))
rd=importlib.util.module_from_spec(spec); spec.loader.exec_module(rd)
D=rd._data
def cstr(va, maxlen=90):
    if not (0<va<len(D)): return None
    e=D.find(b'\x00',va,va+maxlen)
    if e<=va: return None
    s=D[va:e]
    if all(32<=c<127 for c in s): return s.decode()
    return None
def litval(ins,addr):
    # ldr rX,[pc,#imm] : target = align4(addr+4)+imm
    try: off=int(ins.op_str.split('#')[-1].rstrip(']'),0)
    except Exception: return None
    return ((addr+4)&~3)+off
def dump(entry,maxins=6000,show=('bl','b') ):
    ins=rd.funcs_from(entry,maxins)
    print("=== %#x : %d instrs, %#x..%#x"%(entry,len(ins),ins[0].address,ins[-1].address))
    for i in ins:
        extra=''
        if i.mnemonic.startswith('ldr') and '[pc' in i.op_str:
            t=litval(i,i.address)
            if t is not None and t+4<=len(D):
                v=struct.unpack('<I',D[t:t+4])[0]
                s=cstr(v)
                extra='   ; [%#x]=%#x'%(t,v)+((' "'+s[:70]+'"') if s else '')
                if 0x700000<=v<0x9bb1c8 and not s:
                    s2=cstr(v-8); extra+= (' /*near: '+s2[:60]+' */') if s2 else ''
        print("%08x  %-8s %-34s%s"%(i.address,i.mnemonic,i.op_str,extra))
    return ins
