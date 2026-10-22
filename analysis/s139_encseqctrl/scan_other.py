#!/usr/bin/env python3
"""S139 — aplicación de la regla PIC **estricta** a la A7S fw3.20 y al A6300 fw2.01
para el token `[ENCSEQCTRL]` (y opcionalmente otros), y comparación con la A6000.

Reutiliza las funciones del escáner canónico `analysis/s106_imaging_cap/scan_pic_refs_strict.py`.

Uso: .venv/bin/python analysis/s139_encseqctrl/scan_other.py a7s [token]
"""
import importlib.util
import json
import os
import re
import struct
import sys

BASE = 0x43541000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BINS = {
    "a6000": "analysis/rea-independent/input/av-cam.bin",
    "a7s": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}

spec = importlib.util.spec_from_file_location(
    "strict", os.path.join(ROOT, "analysis/s106_imaging_cap/scan_pic_refs_strict.py"))
strict = importlib.util.module_from_spec(spec)
spec.loader.exec_module(strict)


def strings_with(b, token):
    out = []
    for m in re.finditer(re.escape(token.encode()), b):
        s = m.start()
        while s > 0 and b[s - 1] != 0 and 32 <= b[s - 1] < 127:
            s -= 1
        e = b.find(b"\0", m.start())
        out.append((BASE + s, b[s:e].decode("latin1")))
    return out


def prologues(b, lo, hi):
    out = []
    a = lo
    while a < hi:
        h = struct.unpack_from("<H", b, a - BASE)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = struct.unpack_from("<H", b, a - BASE + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def run(name, token):
    path = os.path.join(ROOT, BINS[name])
    b = open(path, "rb").read()
    strict.B = b
    strict.N = len(b)
    starts = {s for s, _ in strings_with(b, token)}
    res = strict.scan(BASE, BASE + len(b))
    sites = 0
    ref = 0
    for s in starts:
        v = res.get(s)
        if v:
            ref += 1
            sites += len(v)
    P = prologues(b, BASE, BASE + len(b))
    funcs = set()
    for s in starts:
        for x in res.get(s, []):
            i = 0
            # búsqueda binaria
            lo, hi = 0, len(P)
            while lo < hi:
                mid = (lo + hi) // 2
                if P[mid] <= x:
                    lo = mid + 1
                else:
                    hi = mid
            if lo:
                funcs.add(P[lo - 1])
    return {"cadenas": len(starts), "referenciadas": ref, "sitios": sites,
            "funciones": len(funcs),
            "rango_funciones": [hex(min(funcs)) if funcs else None,
                                 hex(max(funcs)) if funcs else None]}


if __name__ == "__main__":
    token = sys.argv[2] if len(sys.argv) > 2 else "[ENCSEQCTRL]"
    for name in sys.argv[1].split(","):
        print(name, token, json.dumps(run(name, token)))
