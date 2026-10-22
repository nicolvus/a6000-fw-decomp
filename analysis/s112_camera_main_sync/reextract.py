#!/usr/bin/env python3
"""S112 — corrección y completado del entregable de `[CAMERA_MAIN_SYNC]`.

El borrador del subagente tenía dos defectos de extracción:
  1. las direcciones apuntaban **un byte después** del inicio real (se saltaba el `[`);
  2. el texto de cada cadena incluía las cadenas siguientes (no se cortaba en el NUL).

Este script reextrae las 429 cadenas correctamente, recalcula los sub-bloques, añade el
**mapa función→traza** (esquema PIC + prólogos Thumb) y el **diferencial exacto con la
A7S fw3.20**, y reescribe `camera_main_sync.json`.
"""
import json
import os
import re
import struct
from collections import Counter, defaultdict

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
PREFIX = b"[CAMERA_MAIN_SYNC]"
HERE = os.path.dirname(os.path.abspath(__file__))
S106 = os.path.join(os.path.dirname(HERE), "s106_imaging_cap")


def prologues(data, lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
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


def norm(t):
    t = t.split("%")[0].replace("0x", "").replace(" ", "").rstrip(":!.,")
    return t


def tag_of(text):
    m = re.match(r"\[CAMERA_MAIN_SYNC\]:\s*([A-Za-z][A-Za-z0-9_]{1,19})[:\s]", text)
    return m.group(1) if m else ""


def main():
    data = open(BIN, "rb").read()
    strings = []
    start = 0
    while True:
        i = data.find(PREFIX, start)
        if i < 0:
            break
        e = i
        while e < len(data) and data[e] != 0:
            e += 1
        strings.append({"vaddr": f"0x{BASE + i:x}", "offset": i,
                        "text": data[i:e].decode("latin1")})
        start = i + 1

    refs = json.load(open(os.path.join(S106, "pic_refs.json")))
    starts = prologues(data, 0x43541000, 0x43A00000)
    by_func = defaultdict(list)
    for s in strings:
        s["tag"] = tag_of(s["text"])
        for site in refs.get(s["vaddr"], []):
            a = int(site, 16) if isinstance(site, str) else int(site)
            cand = [x for x in starts if x <= a and a - x <= 0x4000]
            if cand:
                by_func[cand[-1]].append(s)
    funcs = [{"func": f"0x{f:x}", "n_strings": len(ss),
              "strings": [{"vaddr": s["vaddr"], "text": s["text"]} for s in ss]}
             for f, ss in sorted(by_func.items())]

    subs = defaultdict(list)
    for s in strings:
        subs[s["tag"] or "(sin etiqueta)"].append(s)
    subblocks = {}
    for t, ss in subs.items():
        subblocks[t] = {
            "count": len(ss),
            "lo": min(x["vaddr"] for x in ss),
            "hi": max(x["vaddr"] for x in ss),
            "sample_texts": [x["text"][:110] for x in ss[:3]],
        }

    a7s = open(os.path.join(os.path.dirname(HERE), "..", A7S), "rb").read()
    a7s_norm = {norm(m.group().decode("latin1"))
                for m in re.finditer(rb"[\x20-\x7e]{6,}", a7s)}
    comunes, solo = [], []
    for s in strings:
        core = s["text"][len(PREFIX) + 1:] if s["text"].startswith(PREFIX.decode() + ":") \
            else s["text"]
        (comunes if norm(core) in a7s_norm else solo).append(s["vaddr"])

    d = json.load(open(os.path.join(HERE, "camera_main_sync.json"), encoding="utf-8"))
    d["strings"] = strings
    d["string_count"] = len(strings)
    d["total_strings"] = len(strings)
    d["vaddr_range"] = f"{strings[0]['vaddr']} - {strings[-1]['vaddr']}"
    d["subblocks"] = subblocks
    d["functions"] = funcs
    d["n_functions"] = len(funcs)
    d["a7s"] = {
        "prefijo": a7s.count(PREFIX),
        "comunes_texto_a_texto": len(comunes),
        "solo_a6000": len(solo),
        "vaddrs_solo_a6000": solo,
    }
    json.dump(d, open(os.path.join(HERE, "camera_main_sync.json"), "w"), indent=1,
              ensure_ascii=False)
    print(f"cadenas: {len(strings)}  rango {d['vaddr_range']}")
    print(f"sub-bloques: {len(subblocks)}  funciones: {len(funcs)}  "
          f"pares: {sum(f['n_strings'] for f in funcs)}")
    print(f"A7S: prefijo={d['a7s']['prefijo']} comunes={len(comunes)} solo_a6000={len(solo)}")
    print("top sub-bloques:", Counter(s["tag"] or "(sin etiqueta)" for s in strings).most_common(12))


if __name__ == "__main__":
    main()
