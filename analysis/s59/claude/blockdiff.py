"""S59-Claude: diferencia a nivel de instrucción (rangos contiguos de PC) en Execute entre modos, ctor real, depuración sin sustitución (0xff)."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from modediff import run
def ranges(pcs):
    out = []
    for x in sorted(pcs):
        if out and x - out[-1][1] <= 4: out[-1][1] = x
        else: out.append([x, x])
    return out
def diff(a, b):
    A, B2 = run(a), run(b); sa, sb = set(A['exec']), set(B2['exec'])
    return dict(n_a=len(A['exec']), n_b=len(B2['exec']), only_a=[(hex(x), hex(y)) for x, y in ranges(sa - sb)], only_b=[(hex(x), hex(y)) for x, y in ranges(sb - sa)])
if __name__ == '__main__':
    res = {f'{a:#x}_{b:#x}': diff(a, b) for a, b in ((0x0b, 0x4e), (0x4c, 0x4e), (0x0b, 0x4c))}
    json.dump(res, open(Path(__file__).parent / 'blockdiff.json', 'w'), indent=1)
    for k, v in res.items(): print(k, v['n_a'], v['n_b'], 'solo A', v['only_a'], 'solo B', v['only_b'])
