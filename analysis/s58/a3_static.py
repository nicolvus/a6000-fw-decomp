"""S58-A.3 estático: funciones que cargan el slot GOT 0xcb0 (P=0x43eaee84, estado AE) y almacenan en offsets de interés."""
import sys, re, bisect
sys.path.insert(0, '.')
from tdis import data, B, u32
d = data('A6000')
from tdis import ins_list
ins = ins_list('A6000')
starts = [a for a, m, o in ins if m in ('push', 'push.w') and 'lr' in o]
fn = lambda a: starts[bisect.bisect_right(starts, a) - 1]
LIT = int(sys.argv[1], 0); OFFS = set(range(int(sys.argv[2], 0), int(sys.argv[3], 0)))
users = set()
for a, m, o in ins:
    mm = re.match(r'(r\d+), \[pc, #(0x[0-9a-f]+|\d+)\]$', o)
    if m.startswith('ldr') and mm:
        la = ((a + 4) & ~3) + int(mm.group(2), 0)
        if la - B + 4 <= len(d) and u32('A6000', la) == LIT: users.add(fn(a))
print('funciones con literal', hex(LIT), [hex(x) for x in sorted(users)])
for a, m, o in ins:
    if m.startswith('str') and fn(a) in users:
        mm = re.search(r'\[(\w+), #(0x[0-9a-f]+|\d+)\]', o)
        if mm and int(mm.group(2), 0) in OFFS: print(hex(fn(a)), hex(a), m, o)
