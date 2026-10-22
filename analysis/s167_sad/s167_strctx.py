#!/usr/bin/env python3
"""S167 — cadenas vecinas de las trazas [SAD] (contexto de .rodata)."""
import re, sys
BASE = 0x43541000
B = open("analysis/rea-independent/input/av-cam.bin", "rb").read()
lo = int(sys.argv[1], 0); hi = int(sys.argv[2], 0)
o0, o1 = lo - BASE, hi - BASE
for m in re.finditer(rb"[\x20-\x7e]{2,}", B[o0:o1]):
    s = o0 + m.start()
    e = B.find(b"\x00", s)
    print(f"{BASE + s:#x}  {B[s:e].decode('latin1')!r}")
