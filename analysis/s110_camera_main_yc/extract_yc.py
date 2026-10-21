#!/usr/bin/env python3
"""Extracción de las trazas `[CAMERA_MAIN_YC]` (motor de imagen YC) de la A6000.

- `strings_raw.json`: las 970 cadenas con vaddr/offset/texto.
- `blocks.json`: bloques contiguos con su rango y sus tokens dominante.
- `functions.json`: función que referencia cada cadena (mapa PIC de la imagen).

Convención: vaddr = 0x43541000 + file_offset.
"""
import json
import os
import re
import struct
from collections import Counter

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
PREFIX = b"[CAMERA_MAIN_YC]"
HERE = os.path.dirname(os.path.abspath(__file__))


def extract():
    data = open(BIN, "rb").read()
    out = []
    start = 0
    while True:
        i = data.find(PREFIX, start)
        if i < 0:
            break
        e = i
        while e < len(data) and 32 <= data[e] < 127:
            e += 1
        out.append({"vaddr": f"0x{BASE + i:x}", "off": i, "text": data[i:e].decode("latin1")})
        start = i + 1
    return data, out


def blocks(strings, gap=0x400):
    rows = sorted(strings, key=lambda r: r["off"])
    out = []
    cur = [rows[0]]
    for a, b in zip(rows, rows[1:]):
        if b["off"] - a["off"] > gap:
            out.append(cur)
            cur = [b]
        else:
            cur.append(b)
    out.append(cur)
    res = []
    for blk in out:
        tok = Counter()
        for r in blk:
            for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", r["text"]):
                tok[t] += 1
        res.append({
            "lo": blk[0]["vaddr"], "hi": blk[-1]["vaddr"], "n": len(blk),
            "tokens": tok.most_common(12),
            "strings": blk,
        })
    return res


def source_files(data, lo, hi):
    out = []
    for m in re.finditer(rb"[A-Za-z0-9_]{3,40}\.(?:cpp|h)\x00", data):
        va = BASE + m.start()
        if lo <= va < hi:
            out.append({"vaddr": f"0x{va:x}", "name": m.group()[:-1].decode()})
    return out


def func_map(strings):
    """Cadena -> función que la referencia, según el mapa PIC de la imagen."""
    path = os.path.join(os.path.dirname(HERE), "s106_imaging_cap", "pic_refs.json")
    refs = json.load(open(path))
    out = []
    for r in strings:
        va = int(r["vaddr"], 16)
        sites = refs.get(r["vaddr"], [])
        out.append({**r, "xref_sites": [s if isinstance(s, str) else f"0x{int(s):x}" for s in sites],
                    "n_xrefs": len(sites)})
    return out


def main():
    data, strings = extract()
    bl = blocks(strings)
    fmap = func_map(strings)
    files = source_files(data, BASE + strings[0]["off"], BASE + strings[-1]["off"])
    json.dump({"module": "CAMERA_MAIN_YC", "base": f"0x{BASE:x}", "count": len(strings),
               "strings": strings},
              open(os.path.join(HERE, "strings_raw.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "CAMERA_MAIN_YC", "blocks": bl},
              open(os.path.join(HERE, "blocks.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "CAMERA_MAIN_YC", "strings": fmap},
              open(os.path.join(HERE, "functions.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "CAMERA_MAIN_YC", "files": files},
              open(os.path.join(HERE, "source_files.json"), "w"), indent=1, ensure_ascii=False)
    print(f"{len(strings)} cadenas, {len(bl)} bloques, {len(files)} ficheros fuente")
    for b in bl:
        print(f"  {b['lo']}-{b['hi']} n={b['n']:4d}  {[t[0] for t in b['tokens'][:6]]}")


if __name__ == "__main__":
    main()
