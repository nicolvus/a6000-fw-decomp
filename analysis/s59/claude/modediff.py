"""S59-Claude: diferencia de funciones ejecutadas por SetMode+SetExposure+SetRead+Execute entre modo foto (0x0b) y Silent (0x4e/0x4f) con ctor real."""
import sys, json, bisect
from pathlib import Path
R = Path(__file__).resolve().parents[2]
for p in ('s58', 's57', 's55', 's59/claude'): sys.path.insert(0, str(R / p))
from real_scen import A7S, AMB, O, CTOR
from unicorn import UC_HOOK_CODE
from strrefs import scan
_, STARTS = scan('A7S')
def fn(a): k = bisect.bisect_right(STARTS, a) - 1; return STARTS[k] if k >= 0 else 0
def run(mode, shut=0):
    e = A7S(ambito=AMB, stubfn={0x438f6864: lambda e: 1})
    try: e.u.mem_map(0, 0x1000)
    except Exception: pass
    e.u.mem_write(O, bytes(0x500)); e.call(CTOR, O, 0)
    stages = {}
    for name, f in (('setmode', lambda: e.setmode(mode)), ('setexp', lambda: e.setexposure(shd=0x123, svd=0x456, spl=0x78, shut=shut)), ('setread', lambda: e.setread(agc=0x100)), ('exec', e.execute)):
        pcs = []; h = e.u.hook_add(UC_HOOK_CODE, lambda uc, a, sz, _: pcs.append(a)); f(); e.u.hook_del(h)
        stages[name] = pcs
    return stages
if __name__ == '__main__':
    a, b = int(sys.argv[1], 0), int(sys.argv[2], 0)
    A, B2 = run(a), run(b)
    res = {}
    for st in A:
        fa = {fn(x) for x in A[st]}; fb = {fn(x) for x in B2[st]}
        res[st] = dict(only_a=sorted(map(hex, fa - fb)), only_b=sorted(map(hex, fb - fa)), na=len(A[st]), nb=len(B2[st]))
        print(st, hex(a), len(A[st]), hex(b), len(B2[st]), 'solo', hex(a), res[st]['only_a'], 'solo', hex(b), res[st]['only_b'])
    json.dump(res, open(Path(__file__).parent / f'modediff_{a:x}_{b:x}.json', 'w'))
