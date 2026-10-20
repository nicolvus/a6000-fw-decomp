"""S61: referencias al global cfg (0x43e964a4, GOT+0x21a0) y accesos a +0xd/+0x168/+0x16a/+0x3a."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s58"))
from tdis import B, data, ins_list, u32

L = ins_list("A6000")
users = []
for k, (a, m, o) in enumerate(L):
    mm = re.match(r"(r\d+), \[pc, #(0x[0-9a-f]+|\d+)\]$", o)
    if m.startswith("ldr") and mm:
        la = ((a + 4) & ~3) + int(mm.group(2), 0)
        if B <= la < B + len(data("A6000")) - 4 and u32("A6000", la) == 0x21A0:
            users.append(a)
print(len(users))
Path(__file__).with_name("cfg_users.json").write_text(json.dumps([hex(x) for x in users]))
