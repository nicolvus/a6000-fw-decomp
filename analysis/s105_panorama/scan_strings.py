#!/usr/bin/env python3
"""S105 — extracción de cadenas de panorámica / barrido / bracketing / intervalo.

Convención: vaddr = 0x43541000 + file_offset (verificada empíricamente en ambos blobs).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000

BLOBS = {
    "A6000": ROOT / "analysis/rea-independent/input/av-cam.bin",
    "A7S": ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}

# Prefijos / palabras clave searched as ASCII inside the blob.
KEYS = [
    b"panorama", b"Panorama", b"PANORAMA",
    b"sweep", b"Sweep", b"SWEEP",
    b"bracket", b"Bracket", b"BRACKET", b"BRKT",
    b"interval", b"Interval", b"INTERVAL",
    b"stitch", b"Stitch",
    b"bkt", b"BKT",
]


def strings(data, minlen=4):
    """Yield (offset, text) for printable ASCII runs."""
    pat = re.compile(rb"[\x20-\x7e]{%d,}" % minlen)
    for m in pat.finditer(data):
        yield m.start(), m.group(0).decode("latin-1")


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "A6000"
    needle = sys.argv[2].encode() if len(sys.argv) > 2 else None
    data = BLOBS[which].read_bytes()
    hits = []
    for off, text in strings(data):
        if needle and needle not in text.encode("latin-1"):
            continue
        if needle is None and not any(k in text.encode("latin-1") for k in KEYS):
            continue
        hits.append((off + BASE, off, text))
    for v, o, t in hits:
        print(f"0x{v:08x} off=0x{o:08x} {t}")


if __name__ == "__main__":
    main()
