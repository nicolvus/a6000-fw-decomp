#!/usr/bin/env python3
"""S127 — módulo `[CAMERA_MAIN_LC]` (calibración de lente) del firmware A6000 fw3.21.

Extrae las cadenas con el prefijo, toma los sitios de referencia PIC del mapa global
(regla canónica estricta, `analysis/s106_imaging_cap/pic_refs_strict_global.json`) y
atribuye cada sitio a su función por el prólogo Thumb más cercano hacia atrás.
Compara con A7S fw3.20 y A6300 fw2.01.

Convención: vaddr = 0x43541000 + file_offset.

Uso: .venv/bin/python analysis/s127_camera_main_lc/scan_s127.py
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
PREFIX = b"[CAMERA_MAIN_LC]"


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


def main():
    data = open(BIN, "rb").read()
    strings = extract(data)
    g = json.load(open(GLOBAL))
    for s in strings:
        s["sites"] = [int(x) for x in g.get(s["vaddr"], [])]
    starts = prologues(data, BASE, 0x43A00000)
    by_func = defaultdict(list)
    for s in strings:
        for site in s["sites"]:
            f = enclosing(starts, site)
            by_func[f].append((site, s))

    lines = []
    lines.append(f"cadenas\t{len(strings)}")
    lines.append(f"sitios\t{sum(len(s['sites']) for s in strings)}")
    lines.append(f"funciones\t{len(by_func)}")
    dead = [s["vaddr"] for s in strings if not s["sites"]]
    lines.append("sin_referencia\t" + ",".join(dead))
    for f in sorted(by_func):
        ss = by_func[f]
        lines.append(f"FUNC 0x{f:x}\t{len(ss)}\tsites=" +
                     ",".join(f"0x{a:x}" for a, _ in ss))
        for a, s in ss:
            lines.append(f"   0x{a:x}\t{s['vaddr']}\t{s['text']}")
    open(os.path.join(HERE, "func_map.txt"), "w").write("\n".join(lines) + "\n")

    # diferencial
    a7s = open(A7S, "rb").read()
    a6300 = open(A6300, "rb").read()
    def texts(d):
        return set(s["text"] for s in extract(d))
    mine = set(s["text"] for s in strings)
    ta, tb = texts(a7s), texts(a6300)
    inner = set(s["text"].replace("[CAMERA_MAIN_LC]: ", "") for s in strings)
    # ¿el texto interior existe en A7S/A6300 con o sin otra etiqueta?
    a7s_all = set(x.decode("latin1") for x in a7s.split(b"\x00") if len(x) > 8)
    a6_all = set(x.decode("latin1") for x in a6300.split(b"\x00") if len(x) > 8)
    dif = {
        "a6000_strings": len(mine),
        "a7s_with_prefix": len(ta),
        "a6300_with_prefix": len(tb),
        "a7s_interior_exact": len(inner & a7s_all),
        "a6300_interior_exact": len(inner & a6_all),
        "a7s_interior_missing": sorted(x for x in inner if x not in a7s_all),
        "a6300_interior_missing": sorted(x for x in inner if x not in a6_all),
    }
    json.dump(dif, open(os.path.join(HERE, "diff.json"), "w"), indent=1,
              ensure_ascii=False)
    json.dump([{"vaddr": s["vaddr"], "text": s["text"],
                "sites": [f"0x{x:x}" for x in s["sites"]],
                "func": f"0x{enclosing(starts, s['sites'][0]):x}"
                        if s["sites"] else None} for s in strings],
              open(os.path.join(HERE, "strings_sites.json"), "w"), indent=1,
              ensure_ascii=False)
    print("\n".join(lines[:4]))
    print(json.dumps(dif, indent=1, ensure_ascii=False)[:2000])


if __name__ == "__main__":
    main()
