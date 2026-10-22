#!/usr/bin/env python3
"""S120 — extracción de las trazas `[IDT_OPD]` (módulo de mapas del imager).

Salidas:
  - `strings_raw.json`: las cadenas `[IDT_OPD]` con vaddr/offset/texto.
  - `func_map.json`   : mapa función → traza (esquema PIC + prólogos Thumb).
  - `summary.json`    : sub-bloques, contadores y diferencial A7S/A6300.

Convención: vaddr = 0x43541000 + file_offset.
Método de referencias: `analysis/s106_imaging_cap/scan_pic_refs_v2.py` (kill analysis).
"""
import json
import os
import struct
import sys
from collections import defaultdict

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
PREFIX = b"[IDT_OPD]"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PIC = "/tmp/opencode/pic_refs_v2.json"        # kill analysis global (S118)


def extract(data, prefix=PREFIX):
    """Cadenas que empiezan por `prefix`, terminadas en NUL (pueden contener \\n)."""
    out = []
    idx = 0
    while True:
        i = data.find(prefix, idx)
        if i < 0:
            break
        idx = i + 1
        e = data.find(b"\x00", i)
        if e < 0:
            e = len(data)
        out.append({"vaddr": f"0x{BASE + i:x}", "off": i,
                    "text": data[i:e].decode("latin1")})
    return out


def prologues(data, lo, hi):
    """Direcciones de prólogos de función Thumb (push {..,lr} / stmdb sp!...)."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > len(data) - 4:
            a += 2
            continue
        h = struct.unpack_from("<H", data, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = struct.unpack_from("<H", data, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def func_map(data, strings, refs, starts):
    by_func = defaultdict(list)
    sites = []
    for s in strings:
        for site in refs.get(s["vaddr"], []):
            a = int(site, 16) if isinstance(site, str) else int(site)
            cand = [x for x in starts if x <= a and a - x <= 0x4000]
            if cand:
                f = cand[-1]
                by_func[f].append(s)
                sites.append({"site": f"0x{a:x}", "func": f"0x{f:x}",
                              "vaddr": s["vaddr"], "text": s["text"]})
    return ([{"func": f"0x{f:x}", "n_strings": len(ss),
              "strings": [{"vaddr": s["vaddr"], "text": s["text"]} for s in ss]}
             for f, ss in sorted(by_func.items())], sites)


# --- sub-bloques: rangos contiguos de la tabla de cadenas (definidos en el módulo canónico) ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_idt_opd_json import SUBBLOCKS  # noqa: E402


def classify(trace):
    """Sub-bloque = rango contiguo de la tabla de cadenas que contiene la traza."""
    a = int(trace["vaddr"], 16)
    for lo, hi, name, desc in SUBBLOCKS:
        if int(lo, 16) <= a < int(hi, 16):
            return name, desc
    return "(fuera)", "(fuera de los rangos)"


def main():
    data = open(os.path.join(ROOT, BIN), "rb").read()
    strings = extract(data)
    refs = json.load(open(PIC))
    starts = prologues(data, 0x43541000, 0x43A00000)
    fmap, sites = func_map(data, strings, refs, starts)

    # sub-bloques
    subs = defaultdict(list)
    for s in strings:
        k, _desc = classify(s)
        subs[k].append(s)
    sub_rows = []
    for k, ss in sorted(subs.items(), key=lambda kv: -len(kv[1])):
        sub_rows.append({"submodule": k,
                         "desc": next((d for _, _, n, d in SUBBLOCKS if n == k),
                                      "(sin encabezado reconocible)"),
                         "n": len(ss), "lo": min(x["vaddr"] for x in ss),
                         "hi": max(x["vaddr"] for x in ss),
                         "sample": [x["text"] for x in ss[:2]]})

    # diferencial A7S / A6300 (texto a texto, sin el prefijo)
    a7s = open(os.path.join(ROOT, A7S), "rb").read()
    a63 = open(os.path.join(ROOT, A6300), "rb").read()
    a7s_idt = extract(a7s, b"[IDT]")
    a63_idt = extract(a63, b"[IDT]")
    core6 = {s["text"][len("[IDT_OPD]"):] for s in strings}
    core7 = {s["text"][len("[IDT]"):] for s in a7s_idt}
    core63 = {s["text"][len("[IDT]"):] for s in a63_idt}
    a7s_opd = extract(a7s, PREFIX)
    a63_opd = extract(a63, PREFIX)

    out = {
        "milestone": "S120",
        "module": "IDT_OPD",
        "base": "0x43541000",
        "bin": BIN,
        "counts": {
            "trazas_idt_opd": len(strings),
            "tokens_idt_opd": data.count(PREFIX),
            "funciones": len(fmap),
            "sitios_pic_kill": len(sites),
            "cadenas_con_referencia": len({s['vaddr'] for s in sites}),
            "sub_bloques": len(sub_rows),
            "a7s_traces_idt_opd": len(a7s_opd),
            "a7s_traces_idt": len(a7s_idt),
            "a7s_comunes": len(core6 & core7),
            "a7s_solo_a6000": len(core6 - core7),
            "a7s_solo_a7s": len(core7 - core6),
            "a6300_traces_idt_opd": len(a63_opd),
            "a6300_traces_idt": len(a63_idt),
            "a6300_comunes": len(core6 & core63),
            "a6300_solo_a6000": len(core6 - core63),
        },
        "range": [min(s["vaddr"] for s in strings), max(s["vaddr"] for s in strings)],
        "submodules": sub_rows,
        "functions": fmap,
        "sites": sites,
        "a7s_only": sorted(core7 - core6),
        "a6000_only": sorted(core6 - core7),
        "a6300_only": sorted(core63 - core6),
    }
    json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "IDT_OPD", "count": len(strings), "strings": strings},
              open(os.path.join(HERE, "strings_raw.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "IDT_OPD", "functions": fmap},
              open(os.path.join(HERE, "func_map.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out["counts"], indent=1))
    print("sub-bloques:", [(r["submodule"], r["n"]) for r in sub_rows])
    print("rango:", out["range"])


if __name__ == "__main__":
    main()
