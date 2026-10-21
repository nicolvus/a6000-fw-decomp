"""S56-A: mapa registro sombra (ID) -> funciones que lo escriben/leen (por literal GOT). Salida: rec_map.json"""
import sys, json, bisect, pickle, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).parent.parent / 's55'))
import rec_users as R
from gpio_calls_diff import B, disasm
CACHE_DIR = Path(tempfile.gettempdir()) / 'a6000_re_cache'   # portable: /tmp/claude-1000 no existe en otras maquinas
CACHE_DIR.mkdir(parents=True, exist_ok=True)
cache = CACHE_DIR / 'fstarts.pkl'
if cache.exists(): starts = pickle.load(open(cache, 'rb'))
else:
    starts = sorted(i.address for i in disasm(R.d) if (i.mnemonic == 'push' or i.mnemonic == 'push.w') and 'lr' in i.op_str); pickle.dump(starts, open(cache, 'wb'))
NAMES = {0x436d6f6c: 'SetExposure', 0x436d7e08: 'SetRead', 0x436d62e4: 'SetMode', 0x436d79c4: 'drvmode_fill', 0x436d7c08: 'trigger_bit'}
def fn(a): return starts[bisect.bisect_right(starts, a) - 1]
out = []
for p in sorted(R.recs, key=lambda x: (R.recs[x], x)):
    us = sorted({fn(u) for u in R.users(p)})
    out.append(dict(rec=hex(p), id=R.recs[p], data=R.d[p - B + 2], funcs=[hex(x) for x in us]))
json.dump(out, open(Path(__file__).parent / 'rec_map.json', 'w'), indent=0)
import collections
c = collections.Counter(f for o in out for f in o['funcs']); print(c.most_common(25))
