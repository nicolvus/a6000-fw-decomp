#!/usr/bin/env python3
"""S129 — módulo `[CAMERA_MAIN_IM]` del firmware A6000 fw3.21.

Extrae las cadenas con el prefijo, toma los sitios de referencia PIC del mapa global
(regla canónica estricta, `analysis/s106_imaging_cap/pic_refs_strict_global.json`) y
atribuye cada sitio a su función por el prólogo Thumb más cercano hacia atrás.
Compara con A7S fw3.20 y A6300 fw2.01.

Convención: vaddr = 0x43541000 + file_offset.

Uso: .venv/bin/python analysis/s129_camera_main_im/scan_s129.py
"""
import json
import os
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
PREFIX = b"[CAMERA_MAIN_IM]"


def extract(data, prefix=PREFIX):
    out = []
    start = 0
    while True:
        i = data.find(prefix, start)
        if i < 0:
            break
        e = i
        while e < len(data) and data[e] != 0:
            e += 1
        out.append({"vaddr": f"0x{BASE + i:x}", "off": i,
                    "text": data[i:e].decode("latin1")})
        start = i + 1
    return out


def prologues(data, lo, hi):
    """Inicios de función Thumb: push {...,lr} (B5xx con lr) o push.w {...,lr}."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
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


def bl_targets(data, func_start, size=0x600):
    """Destinos de `bl` (F000/F800) dentro de [func_start, func_start+size)."""
    out = []
    for a in range(func_start, min(func_start + size, len(data) + BASE), 2):
        o = a - BASE
        h1, h2 = struct.unpack_from("<HH", data, o)
        if (h1 & 0xF800) == 0xF000 and (h2 & 0xD000) == 0xD000:
            s = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
            if s & 0x400000:
                s -= 0x800000
            out.append((a, (a + 4 + s) & 0xFFFFFFFF))
    return out


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
            by_func[enclosing(starts, site)].append((site, s))

    lines = [f"cadenas\t{len(strings)}",
             f"sitios\t{sum(len(s['sites']) for s in strings)}",
             f"funciones\t{len(by_func)}",
             "sin_referencia\t" + ",".join(s["vaddr"] for s in strings if not s["sites"])]
    for f in sorted(by_func):
        ss = by_func[f]
        lines.append(f"FUNC 0x{f:x}\t{len(ss)}\tsites=" +
                     ",".join(f"0x{a:x}" for a, _ in ss))
        for a, s in ss:
            lines.append(f"   0x{a:x}\t{s['vaddr']}\t{s['text']}")
    open(os.path.join(HERE, "func_map.txt"), "w").write("\n".join(lines) + "\n")

    funcs = []
    for f in sorted(by_func):
        ss = by_func[f]
        funcs.append({
            "func": f"0x{f:x}",
            "n_sites": len(ss),
            "strings": [s["vaddr"] for _, s in ss],
            "sites": [f"0x{a:x}" for a, _ in ss],
            "bl": [f"0x{t:x}" for _, t in bl_targets(data, f)][:40],
        })

    # diferencial
    def texts(d):
        return set(s["text"] for s in extract(d))

    a7s = open(A7S, "rb").read()
    a6300 = open(A6300, "rb").read()
    mine = set(s["text"] for s in strings)
    inner = set(s["text"].replace("[CAMERA_MAIN_IM]: ", "") for s in strings)
    a7s_all = set(x.decode("latin1") for x in a7s.split(b"\x00") if len(x) > 8)
    a6_all = set(x.decode("latin1") for x in a6300.split(b"\x00") if len(x) > 8)

    dif = {
        "a6000_strings": len(mine),
        "a7s_with_prefix": len(texts(a7s)),
        "a6300_with_prefix": len(texts(a6300)),
        "a7s_interior_exact": len(inner & a7s_all),
        "a6300_interior_exact": len(inner & a6_all),
        "a7s_interior_missing": sorted(x for x in inner if x not in a7s_all),
        "a6300_interior_missing": sorted(x for x in inner if x not in a6_all),
    }
    json.dump(dif, open(os.path.join(HERE, "diff.json"), "w"), indent=1,
              ensure_ascii=False)
    json.dump(strings, open(os.path.join(HERE, "strings_raw.json"), "w"),
              indent=1, ensure_ascii=False)
    json.dump(funcs, open(os.path.join(HERE, "func_map.json"), "w"), indent=1,
              ensure_ascii=False)
    print("\n".join(lines[:4]))
    print(json.dumps(dif, indent=1, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    main()
