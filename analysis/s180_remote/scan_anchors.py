#!/usr/bin/env python3
"""S180 - buscar el bloque REMOTE equivalente en A7S/A6300 (sin token [REMOTE])."""
import os, re, sys

BASE = 0x43541000
BINS = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}

# anclas textuales: nucleo de la primera y ultima cadena [REMOTE]
ANCHORS = [
    b"NotifyUartCommand...UART CMD",
    b"NotifyAttached",
    b"NotifyUartTimedOut",
    b"RecvCmd Unknown Category",
]


def extract_strings(data, minlen=6):
    """Extrae cadenas C (printables) con su offset."""
    out = []
    n = len(data)
    i = 0
    cur = None
    while i < n:
        c = data[i]
        if 32 <= c < 127:
            if cur is None:
                cur = i
            i += 1
        else:
            if cur is not None and i - cur >= minlen:
                out.append((cur, data[cur:i]))
            cur = None
            i += 1
    if cur is not None and n - cur >= minlen:
        out.append((cur, data[cur:n]))
    return out


for k, p in BINS.items():
    d = open(p, "rb").read()
    print("=" * 70)
    print(k, len(d), "B")
    for a in ANCHORS:
        idx = d.find(a)
        if idx < 0:
            print(f"  {a!r}: NO ENCONTRADO")
            continue
        # retroceder hasta el inicio de la cadena
        s = idx
        while s > 0 and 32 <= d[s - 1] < 127:
            s -= 1
        e = idx
        while e < len(d) and 32 <= d[e] < 127:
            e += 1
        print(f"  {a!r} @ off 0x{s:x} vaddr 0x{s+BASE:x}: {d[s:e].decode('latin1')!r}")
