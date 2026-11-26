"""Llamadores verificados con capstone: decodifica la función contenedora y comprueba el BL."""
import sys, bisect
sys.path.insert(0, '/tmp/avc')
from atlas import BASE, D, MD, STARTS, IDX, owner
from capstone.arm import ARM_OP_IMM


def bl_in(start, end, want):
    d = D['321']
    o = start - BASE
    out = []
    for i in MD.disasm(d[o:o + (end - start)], start):
        if i.mnemonic in ('bl', 'blx') and i.operands and i.operands[0].type == ARM_OP_IMM:
            if (i.operands[0].imm & ~1) == (want & ~1):
                out.append(i.address)
    return out


def next_start(a):
    i = bisect.bisect_right(STARTS, a)
    return STARTS[i] if i < len(STARTS) else a + 0x400


def verified_callers(target, maxlen=0x2000):
    res = []
    for c in IDX.get(target & ~1, []):
        ow = owner(c)
        if ow is None: continue
        end = min(next_start(ow), ow + maxlen)
        if ow > c: continue
        if c in bl_in(ow, end, target):
            res.append((c, ow))
    return res


if __name__ == '__main__':
    for x in sys.argv[1:]:
        a = int(x, 0)
        ow = owner(a)
        r = verified_callers(ow)
        print(f'\n### función {ow:08x} (sitio {a:08x}): {len(r)} llamadores verificados')
        for c, o in r:
            print(f'   {c:08x} en {o:08x}')
