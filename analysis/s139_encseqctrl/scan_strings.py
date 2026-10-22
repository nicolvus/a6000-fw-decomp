#!/usr/bin/env python3
"""Localiza el token [ENCSEQCTRL] en una imagen y lista sus cadenas."""
import sys

BINS = {
    "a6000": "analysis/rea-independent/input/av-cam.bin",
    "a7s": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "a6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
BASE = 0x43541000

def load(name):
    p = BINS[name]
    return open(p, "rb").read()

def strings_with_token(b, token):
    """Devuelve [(addr, texto_corto)] de todas las cadenas que contienen el token."""
    res = []
    start = None
    cur = bytearray()
    for i, c in enumerate(b):
        if 32 <= c < 127:
            if start is None:
                start = i
            cur.append(c)
        else:
            if start is not None and token.encode() in cur:
                res.append((BASE + start, bytes(cur).decode("ascii", "replace")))
            start = None
            cur = bytearray()
    if start is not None and token.encode() in cur:
        res.append((BASE + start, bytes(cur).decode("ascii", "replace")))
    return res

if __name__ == "__main__":
    for name in sys.argv[1:] or ["a6000"]:
        b = load(name)
        r = strings_with_token(b, "[ENCSEQCTRL]")
        print(f"== {name}: {len(r)} cadenas con el token; {len(set(t for _,t in r))} textos distintos")
        for a, t in r:
            print(f"  0x{a:x}  {t[:110]}")
