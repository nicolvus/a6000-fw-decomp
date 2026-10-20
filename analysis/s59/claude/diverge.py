import sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
for p in ('s58', 's57', 's55', 's59/claude'): sys.path.insert(0, str(R / p))
from real_scen import A7S, AMB, AMBITO, O, CTOR
from unicorn import UC_HOOK_CODE
def trace(real, mode=0x0b, shut=0):
    e = A7S(ambito=AMB if real else AMBITO, stubfn={0x438f6864: lambda e: 1})
    if real: e.u.mem_write(O, bytes(0x500)); e.call(CTOR, O, 0)
    e.setmode(mode); e.setexposure(shd=0x123, svd=0x456, spl=0x78, shut=shut); e.setread(agc=0x100)
    pcs = []
    e.u.hook_add(UC_HOOK_CODE, lambda uc, a, sz, _: pcs.append(a))
    try: e.execute()
    except Exception as ex: pcs.append(('ERR', str(ex)))
    return pcs, e
if __name__ == '__main__':
    mode = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x0b
    a, ea = trace(True, mode); b, eb = trace(False, mode)
    n = min(len(a), len(b))
    k = next((i for i in range(n) if a[i] != b[i]), None)
    print(len(a), len(b), 'primera divergencia', k, [hex(x) if isinstance(x, int) else x for x in a[max(0, (k or 0) - 6):(k or 0) + 6]], [hex(x) if isinstance(x, int) else x for x in b[max(0, (k or 0) - 6):(k or 0) + 6]])
