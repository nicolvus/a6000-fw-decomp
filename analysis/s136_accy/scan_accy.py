#!/usr/bin/env python3
"""S136 — módulo `[ACCY]` (accesorios) del firmware A6000 fw3.21.

Extrae las cadenas con el prefijo `[ACCY]`, toma los sitios de referencia PIC del mapa
global (regla canónica estricta, `analysis/s106_imaging_cap/pic_refs_strict_global.json`),
atribuye cada sitio a su función por el prólogo Thumb más cercano hacia atrás, y compara
con A7S fw3.20 y A6300 fw2.01.

Convención: vaddr = 0x43541000 + file_offset.

Uso: .venv/bin/python analysis/s136_accy/scan_accy.py
"""
import json
import os
import re
import struct
from collections import defaultdict

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
GLOBAL = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
HERE = os.path.dirname(os.path.abspath(__file__))
PREFIX = b"[ACCY]"


def extract(data, prefix=PREFIX):
    """Cadenas que empiezan por el prefijo (fin = byte NUL)."""
    out = []
    for m in re.finditer(re.escape(prefix), data):
        i = m.start()
        e = data.find(b"\x00", i)
        if e < 0:
            e = len(data)
        out.append({"vaddr": f"0x{BASE + i:x}", "off": i,
                    "text": data[i:e].decode("latin1")})
    return out


def prologues(data, lo, hi):
    """Inicios de función Thumb: push {...,lr} (B5xx con lr) o push.w {...,lr}."""
    out = []
    a = lo
    n = len(data)
    while a < hi:
        o = a - BASE
        if o < 0 or o + 4 > n:
            a += 2
            continue
        h = struct.unpack_from("<H", data, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D and (struct.unpack_from("<H", data, o + 2)[0] & 0x4000):
            out.append(a)
        a += 2
    return out


def enclosing(starts, addr, maxback=0x4000):
    cand = [x for x in starts if x <= addr and addr - x <= maxback]
    return cand[-1] if cand else None


def token_count(path, tok=b"ACCY"):
    data = open(path, "rb").read()
    return len(re.findall(re.escape(b"[" + tok + b"]"), data)), len(data)


def main():
    data = open(BIN, "rb").read()
    strings = extract(data)
    g = json.load(open(GLOBAL))
    for s in strings:
        s["sites"] = sorted(int(x) for x in g.get(s["vaddr"], []))
    starts = prologues(data, BASE, 0x43A00000)
    by_func = defaultdict(list)
    for s in strings:
        for site in s["sites"]:
            f = enclosing(starts, site)
            by_func[f].append((site, s))

    n_ref = sum(1 for s in strings if s["sites"])
    n_sites = sum(len(s["sites"]) for s in strings)
    n_funcs = len([f for f in by_func if f is not None])
    print(f"cadenas: {len(strings)}  referenciadas: {n_ref}  sitios: {n_sites}  "
          f"funciones: {n_funcs}")
    print(f"rango: {strings[0]['vaddr']} - {strings[-1]['vaddr']}")

    # diferencial de token
    for name, path in (("A7S fw3.20", A7S), ("A6300 fw2.01", A6300)):
        if os.path.exists(path):
            c, _ = token_count(path)
            print(f"token [ACCY] en {name}: {c}")
        else:
            print(f"NO EXISTE {path}")

    out = {
        "prefix": "[ACCY]",
        "n_strings": len(strings),
        "n_referenced": n_ref,
        "n_sites": n_sites,
        "n_functions": n_funcs,
        "range": [strings[0]["vaddr"], strings[-1]["vaddr"]],
        "strings": strings,
        "by_func": {f"0x{f:x}" if f else "None": [
            {"site": f"0x{site:x}", "str": s["vaddr"], "text": s["text"]}
            for site, s in sorted(v)] for f, v in by_func.items()},
    }
    with open(os.path.join(HERE, "accy_raw.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
