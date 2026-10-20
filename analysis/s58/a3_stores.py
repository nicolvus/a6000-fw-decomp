"""S58-A.3: almacenes con desplazamiento inmediato en [lo,hi) dentro de un rango de código. uso: a3_stores.py CODE_LO CODE_HI OFF_LO OFF_HI"""
import sys, re, bisect
sys.path.insert(0, '.')
from tdis import ins_list
ins = ins_list('A6000')
starts = [a for a, m, o in ins if m in ('push', 'push.w') and 'lr' in o]
fn = lambda a: starts[bisect.bisect_right(starts, a) - 1]
clo, chi, olo, ohi = [int(x, 0) for x in sys.argv[1:5]]
for a, m, o in ins:
    if clo <= a < chi and m.startswith('str'):
        mm = re.search(r'\[(\w+), #(0x[0-9a-f]+|\d+)\]', o)
        if mm and olo <= int(mm.group(2), 0) < ohi: print(hex(fn(a)), hex(a), m, o)
