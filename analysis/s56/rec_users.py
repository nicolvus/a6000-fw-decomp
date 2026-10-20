"""S56: usuarios (por literal GOT) de registros sombra del IMX210 (id u16 + dato u8) del modelo A6000."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from xr import index, B
G = 0x4401eee4
d, idx = index('A6000'); u = lambda a: struct.unpack_from('<I', d, a - B)[0]
tab = [u(0x43fe995c + 4 * i) for i in range(119)]
recs = {p: struct.unpack_from('<H', d, p - B)[0] for p in tab}
slots = {}   # offset GOT -> registro
for off in range(0, 0x8000, 4):
    try: v = u(G + off)
    except Exception: break
    if v in recs: slots.setdefault(v, []).append(off)
def users(rec):
    offs = set(slots.get(rec, [])); return sorted({a for a, v, r in idx['lits'] if v in offs and r is None})
if __name__ == '__main__':
    for a in sys.argv[1:]:
        r = int(a, 0); print(hex(r), 'id', hex(recs[r]), 'slots', [hex(o) for o in slots.get(r, [])], [hex(x) for x in users(r)])
