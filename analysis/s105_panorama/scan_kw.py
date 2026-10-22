#!/usr/bin/env python3
"""S105 — búsqueda de una lista arbitraria de palabras clave en los blobs A6000/A7S."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
BLOBS = {
    "A6000": ROOT / "analysis/rea-independent/input/av-cam.bin",
    "A7S": ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
PAT = re.compile(rb"[\x20-\x7e]{4,}")
def scan(which, keys, minlen=4):
    data = BLOBS[which].read_bytes()
    out = []
    for m in PAT.finditer(data):
        t = m.group(0).decode("latin-1")
        if any(k in t for k in keys):
            out.append((m.start()+BASE, m.start(), t))
    return out
if __name__ == "__main__":
    which = sys.argv[1]
    keys = sys.argv[2].split(",")
    for v,o,t in scan(which, keys):
        print(f"0x{v:08x} off=0x{o:08x} {t}")
