#!/usr/bin/env python3
"""Barrido lineal de .text de orb-server: recoge (a) direcciones de instrucción que
materializan un puntero a cadena (movw/movt o ldr/add pc) y (b) los valores constantes
de 32 bits (movw/movt) usados junto a llamadas de interés.

Uso: sweep.py BIN [--strings out.json]
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from armdis import Bin
from capstone.arm import ARM_OP_REG, ARM_OP_IMM, ARM_OP_MEM


def sweep(b):
    regs = {}
    out = []
    text = [s for n, s in b.SEC.items() if n == '.text'][0]
    tva, toff, tsize = text
    code = b.data[toff:toff + tsize]
    for ins in b.cs.disasm(code, tva):
        m = ins.mnemonic
        ops = ins.operands
        txt = None
        if m == 'movw' and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_IMM:
            regs[ins.reg_name(ops[0].reg)] = ops[1].imm & 0xffff
        elif m == 'movt' and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_IMM:
            r = ins.reg_name(ops[0].reg)
            val = ((ops[1].imm & 0xffff) << 16) | (regs.get(r) or 0)
            regs[r] = val
            txt = b.cstr(val)
            if txt:
                out.append({'at': ins.address, 'kind': 'movt_str', 'value': hex(val), 'text': txt})
        elif m.startswith('ldr') and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_MEM and ins.reg_name(ops[1].mem.base) == 'pc':
            lit = ((ins.address + 4) & ~3) + ops[1].mem.disp
            v = b.read(lit, 4)
            if v:
                regs[ins.reg_name(ops[0].reg)] = int.from_bytes(v, 'little')
        elif m.startswith('bl') and len(ops) == 1 and ops[0].type == ARM_OP_IMM:
            regs = {}
        elif m in ('add', 'add.w') and len(ops) == 2 and ops[1].type == ARM_OP_REG and ins.reg_name(ops[1].reg) == 'pc':
            r = ins.reg_name(ops[0].reg)
            base = regs.get(r)
            if base is not None:
                val = ((ins.address + 4) & ~3) + base
                txt = b.cstr(val)
                if txt:
                    out.append({'at': ins.address, 'kind': 'addpc_str', 'value': hex(val), 'text': txt})
        elif m.startswith('b') and len(ops) == 1:
            regs = {}
    return out


if __name__ == '__main__':
    b = Bin(sys.argv[1])
    res = sweep(b)
    print('hits', len(res))
    outp = sys.argv[sys.argv.index('--strings') + 1] if '--strings' in sys.argv else None
    if outp:
        json.dump(res, open(outp, 'w'), ensure_ascii=False)
    pats = sys.argv[sys.argv.index('--grep') + 1].split('|') if '--grep' in sys.argv else []
    for r in res:
        if not pats or any(p in r['text'] for p in pats):
            print(f"{r['at']:08x} {r['kind']:9s} {r['value']:>10s} {r['text'][:110]!r}")
