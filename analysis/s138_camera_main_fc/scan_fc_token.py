#!/usr/bin/env python3
"""S138 — busca en el binario candidatos textuales al significado de la sigla "FC".

Busca: nombres mangled/RTTI que contengan "FC", y cadenas con "Face"/"Touch" cerca.
No interpreta: solo lista candidatos con su vaddr.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()

STR_RE = re.compile(rb"[ -~]{4,120}\x00")


def main():
    pat = sys.argv[1] if len(sys.argv) > 1 else "FC"
    seen = set()
    out = []
    for m in STR_RE.finditer(B):
        s = m.group()[:-1].decode("latin1")
        if pat in s and s not in seen:
            seen.add(s)
            out.append((BASE + m.start(), s))
    print(f"cadenas con {pat!r}: {len(out)}")
    for a, s in out:
        print(f"  0x{a:08x}  {s!r}")


if __name__ == "__main__":
    main()
