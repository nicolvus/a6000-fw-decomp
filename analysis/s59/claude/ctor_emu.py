"""S59-Claude: ejecuta el constructor REAL de C_Imager A7S (0x436f3fc0) y compara el objeto con el sintético S58."""
import sys, json
from pathlib import Path
R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 's58')); sys.path.insert(0, str(R / 's57')); sys.path.insert(0, str(R / 's55'))
from a7s_emu import A7S, O, VT, AMBITO
CTOR, BASECTOR = 0x436f3fc0, 0x436f2d44
def build(idx=0, ambito=None, **k):
    e = A7S(ambito=ambito or AMBITO + [(0x43ad9000, 0x43ae0000)], **k)
    e.u.mem_write(O, bytes(0x500))                 # objeto limpio (el ctor real lo inicializa)
    r = e.call(CTOR, O, idx)
    return e, r
if __name__ == '__main__':
    for idx in (0, 1):
        e, r = build(idx)
        obj = e.rd(O, 0x500)
        out = dict(idx=idx, ret=hex(r), vtable=hex(e.r32(O)), vt_ok=e.r32(O) == VT,
                   stubs={hex(a): n for a, n in sorted(e.stubbed.items())},
                   nz=sum(1 for b in obj if b))
        print(json.dumps(out))
