"""S61: escritores del global G (0x43e964a4, GOT+0x21a0) con taint simple de registro dentro de cada función."""
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xr import *

N = len(data("A6000"))
U = [int(x, 16) for x in json.loads(Path(__file__).with_name("cfg_users.json").read_text())]
res = collections.defaultdict(list)
for u in U:
    f = func_start(u)
    ins = instrs(f, f + 0x3000)
    # primer push lr siguiente = fin
    end = len(ins)
    for k in range(1, len(ins)):
        if ins[k][1].startswith("push") and "lr" in ins[k][2]:
            end = k; break
    ins = ins[:end]
    idx = next(k for k, x in enumerate(ins) if x[0] == u)
    m0 = re.match(r"(r\d+),", ins[idx][2]); rz = m0.group(1)
    tainted = set()
    for a, m, o in ins[idx:]:
        mm = re.match(r"(r\d+), \[(r\d+), (r\d+)\]$", o)
        if m.startswith("ldr") and mm and mm.group(3) == rz:
            tainted.add(mm.group(1)); continue
        if m.startswith("mov") and re.match(r"(r\d+), (r\d+)$", o):
            d, s = o.split(", ")
            if s in tainted: tainted.add(d)
            elif d in tainted: tainted.discard(d)
            continue
        st = re.match(r"(r\d+), \[(r\d+)(?:, #(0x[0-9a-f]+|\d+))?\]$", o)
        if m.startswith("str") and st and st.group(2) in tainted:
            res[f].append((hex(a), m, int(st.group(3) or "0", 0)))
            continue
        d = re.match(r"(r\d+),", o)
        if d and d.group(1) in tainted and not m.startswith(("str", "cmp", "tst")):
            tainted.discard(d.group(1))
out = {hex(f): sorted({x[2] for x in v}) for f, v in res.items()}
Path(__file__).with_name("g_writers.json").write_text(json.dumps({hex(f): v for f, v in res.items()}))
for f, offs in sorted(out.items(), key=lambda kv: -len(kv[1]))[:25]:
    print(f, len(offs), [hex(o) for o in offs][:14])
print("total funciones con escrituras:", len(out))
