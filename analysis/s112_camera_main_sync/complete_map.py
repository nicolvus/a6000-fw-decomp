#!/usr/bin/env python3
"""S112 — completa el entregable: mapa función→traza y diferencial exacto con la A7S.

Añade a `camera_main_sync.json`:
  * `functions`: función que referencia cada una de las 429 trazas (esquema PIC + prólogos);
  * `a7s`: recuento exacto de mensajes comunes texto a texto (ignorando los
    especificadores de formato) y los exclusivos de la A6000.
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
    """Normaliza un mensaje para compararlo entre firmwares (sin especificadores)."""
    t = t.split("%")[0].replace("0x", "").replace(" ", "").rstrip(":!.,")
    return t


def main():
    data = open(BIN, "rb").read()
    d = json.load(open(os.path.join(HERE, "camera_main_sync.json"), encoding="utf-8"))
    refs = json.load(open(os.path.join(S106, "pic_refs.json")))
    starts = prologues(data, 0x43541000, 0x43A00000)

    by_func = defaultdict(list)
    for s in d["strings"]:
        for site in refs.get(s["vaddr"], []):
            a = int(site, 16) if isinstance(site, str) else int(site)
            cand = [x for x in starts if x <= a and a - x <= 0x4000]
            if cand:
                by_func[cand[-1]].append(s)
    funcs = [{"func": f"0x{f:x}", "n_strings": len(ss),
              "strings": [{"vaddr": s["vaddr"], "text": s["text"]} for s in ss]}
             for f, ss in sorted(by_func.items())]

    a7s = open(os.path.join(os.path.dirname(HERE), "..", A7S), "rb").read()
    a7s_norm = {norm(m.group().decode("latin1"))
                for m in re.finditer(rb"[\x20-\x7e]{6,}", a7s)}
    comunes, solo = [], []
    for s in d["strings"]:
        core = s["text"][len("[CAMERA_MAIN_SYNC]: "):] if s["text"].startswith("[CAMERA_MAIN_SYNC]: ") \
            else s["text"]
        (comunes if norm(core) in a7s_norm else solo).append(s["vaddr"])

    d["functions"] = funcs
    d["n_functions"] = len(funcs)
    d["a7s"] = {
        "prefijo": a7s.count(b"[CAMERA_MAIN_SYNC]"),
        "comunes_texto_a_texto": len(comunes),
        "solo_a6000": len(solo),
        "vaddrs_solo_a6000": solo,
    }
    json.dump(d, open(os.path.join(HERE, "camera_main_sync.json"), "w"), indent=1,
              ensure_ascii=False)
    print(f"funciones: {len(funcs)}  |  pares: {sum(f['n_strings'] for f in funcs)}")
    print(f"A7S: prefijo={d['a7s']['prefijo']} comunes={len(comunes)} solo_a6000={len(solo)}")


if __name__ == "__main__":
    main()
