#!/usr/bin/env python3
"""Busca punteros (Thumb, +1) a una VA en los segmentos cargados de libmpr.so
(vtables, callbacks, tablas) y devuelve las VA donde aparecen."""
import sys

from elftools.elf.elffile import ELFFile

LIB = "analysis/camera-extract/usr/lib/libmpr.so"
e = ELFFile(open(LIB, "rb"))
segs = [(s["p_vaddr"], s["p_vaddr"] + s["p_filesz"], s["p_offset"])
        for s in e.iter_segments() if s["p_type"] == "PT_LOAD"]

secs = []
for nm in (".rodata", ".data", ".init_array", ".got"):
    s = e.get_section_by_name(nm)
    if s:
        secs.append((nm, s["sh_addr"], s["sh_addr"] + s["sh_size"], s["sh_offset"]))

for a in sys.argv[1:]:
    va = int(a, 0) & ~1
    for pat, tag in ((va | 1, "thumb+1"), (va, "raw")):
        b = pat.to_bytes(4, "little")
        hits = []
        with open(LIB, "rb") as f:
            for nm, lo, hi, off in secs:
                f.seek(off)
                blob = f.read(hi - lo)
                i = blob.find(b)
                while i >= 0:
                    if i % 4 == 0:
                        hits.append(f"{nm}+{lo + i:#x}")
                    i = blob.find(b, i + 1)
        if hits:
            print(f"{va:#x} ({tag}): {', '.join(hits[:12])}")
