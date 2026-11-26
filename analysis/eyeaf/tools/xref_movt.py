#!/usr/bin/env python3
"""Busca referencias a una dirección formadas por parejas movw/movt (o movw+ldr) en .text."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from armdis import Bin
from capstone.arm import ARM_OP_REG, ARM_OP_IMM

def build_index(b):
    text = [s for n, s in b.SEC.items() if n == '.text'][0]
    tva, toff, tsize = text
    movw, movt = [], []
    for ins in b.cs.disasm(b.data[toff:toff + tsize], tva):
        if ins.mnemonic in ('movw', 'movt') and len(ins.operands) == 2:
            o0, o1 = ins.operands
            if o0.type == ARM_OP_REG and o1.type == ARM_OP_IMM:
                (movw if ins.mnemonic == 'movw' else movt).append((ins.address, ins.address, ins.reg_name(o0.reg), o1.imm & 0xffff))
    return movw, movt

def xrefs(b, target):
    movw, movt = build_index(b)
    hi = (target >> 16) & 0xffff
    lo = target & 0xffff
    res = []
    mw = {a: (r, v) for a, _, r, v in movw}
    mwl = sorted((a, r, v) for a, _, r, v in movw)
    for a, _, r, v in movt:
        if v != hi:
            continue
        # buscar movw con mismo registro en las 8 instrucciones previas
        for a2, r2, v2 in mwl:
            if a2 >= a or a - a2 > 32:
                continue
            if r2 == r and v2 == lo:
                res.append((a2, a, r))
    return res

if __name__ == '__main__':
    b = Bin(sys.argv[1])
    for t in sys.argv[2:]:
        t = int(t, 16)
        print(f'== 0x{t:x}')
        for a2, a, r in xrefs(b, t):
            owner = None; best = -1
            for sa, nm in b.sym.items():
                if sa <= a2 and sa > best and b.sym_size.get(sa, 0) > (a2 - sa):
                    best = sa; owner = nm
            print(f'   movw@0x{a2:08x} movt@0x{a:08x} reg={r} owner={owner}')
