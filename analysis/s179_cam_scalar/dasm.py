#!/usr/bin/env python3
"""Desensamblador Thumb simple (capstone)."""
import sys
from capstone import *
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
md=Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail=True
def dis(lo,hi):
    o=lo-BASE
    code=B[o:o+(hi-lo)]
    for i in md.disasm(code, lo):
        print(f"0x{i.address:08x}  {i.mnemonic:8s} {i.op_str}")
if __name__=="__main__":
    lo=int(sys.argv[1],0); hi=int(sys.argv[2],0)
    dis(lo,hi)
