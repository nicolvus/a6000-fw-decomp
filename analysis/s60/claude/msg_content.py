"""S60-Claude: contenido de los mensajes 0x1000/0x1001 en modo foto 0x0b: dependencia de (shd, svd, spl, agc) con el ctor real."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 's59' / 'claude'))
import real_scen as rs
base = dict(shd=0x123, svd=0x456, spl=0x78, agc=0x100)
res = {}
def msgs(**o):
    k = dict(base); k.update(o)
    return [[hex(x) for x in m] for m in rs.scenario(0x0b, 0, **k)['msgs']]
res['base'] = msgs()
for f, v in (('shd', 0x321), ('svd', 0x654), ('spl', 0x87), ('agc', 0x200)):
    res[f] = msgs(**{f: v})
res['changed_vs_base'] = {f: res[f] != res['base'] for f in ('shd', 'svd', 'spl', 'agc')}
json.dump(res, open('analysis/s60/claude/msg_content.json', 'w'), indent=1); print(json.dumps(res))
