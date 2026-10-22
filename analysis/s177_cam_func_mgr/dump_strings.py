#!/usr/bin/env python3
"""S177 — volcado de las cadenas ASCII en un rango de vaddr (para inspección manual)."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
B = open(os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"), "rb").read()

lo = int(sys.argv[1], 0)
hi = int(sys.argv[2], 0)
o0, o1 = lo - BASE, hi - BASE
for m in re.finditer(rb"[\x20-\x7e]{3,}", B[o0:o1]):
    s = m.group().decode("ascii")
    print(f"{o0 + m.start() + BASE:#x}  {s}")
