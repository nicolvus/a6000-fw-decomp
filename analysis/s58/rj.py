"""S58: llamada REA con JSON. uso: rj.py TOOL '{"procedure":"0x..","max_depth":4}' [fichero_salida]"""
import sys, json
from rq import run
r = run([{'tool': sys.argv[1], 'args': json.loads(sys.argv[2])}])[0]
s = json.dumps(r, indent=1) if not isinstance(r, str) else r
if len(sys.argv) > 3: open(sys.argv[3], 'w').write(s); print('->', sys.argv[3], len(s))
else: print(s[:6000])
