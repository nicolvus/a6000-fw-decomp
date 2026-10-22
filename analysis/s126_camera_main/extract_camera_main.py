#!/usr/bin/env python3
"""S126 — extracción de las trazas `[CAMERA_MAIN]` (135) del firmware A6000.

- `strings_raw.json`: cadenas con vaddr/offset/texto.
- `func_map.json`: función que referencia cada cadena (regla canónica estricta).
- `summary.json`: sub-bloques, ficheros fuente y diferencial A6000/A7S/A6300.

Convención: vaddr = 0x43541000 + file_offset.
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
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
PREFIX = b"[CAMERA_MAIN]"
HERE = os.path.dirname(os.path.abspath(__file__))
S106 = os.path.join(os.path.dirname(HERE), "s106_imaging_cap")


def extract(data):
    out = []
    start = 0
    while True:
        i = data.find(PREFIX, start)
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
            if struct.unpack_from("<H", data, o + 2)[0] & 0x4000:
                out.append(a)
        a += 2
    return out


def func_map(data, strings, refs):
    starts = prologues(data, 0x43541000, 0x43A00000)
    by_func = defaultdict(list)
    for s in strings:
        for site in refs.get(s["vaddr"], []):
            a = int(site, 16) if isinstance(site, str) else int(site)
            cand = [x for x in starts if x <= a and a - x <= 0x4000]
            if cand:
                by_func[cand[-1]].append(s)
    return [{"func": f"0x{f:x}", "n_strings": len(ss),
             "strings": [{"vaddr": s["vaddr"], "text": s["text"]} for s in ss]}
            for f, ss in sorted(by_func.items())]


def subblock(text):
    m = re.match(r"\[CAMERA_MAIN\]:\s*([A-Za-z][A-Za-z0-9_]{1,19})[:\s]", text)
    return m.group(1) if m else ""


def main():
    data = open(BIN, "rb").read()
    strings = extract(data)
    refs = json.load(open(os.path.join(S106, "pic_refs_strict_global.json")))
    fmap = func_map(data, strings, refs)

    subs = defaultdict(list)
    for s in strings:
        subs[subblock(s["text"]) or "(sin etiqueta)"].append(s)
    sub_rows = [{"submodule": k, "n": len(v),
                 "lo": min(x["vaddr"] for x in v), "hi": max(x["vaddr"] for x in v),
                 "sample": [x["text"][:100] for x in v[:2]]}
                for k, v in sorted(subs.items(), key=lambda kv: -len(kv[1]))]

    # ficheros fuente embebidos en la zona de cadenas
    lo = int(strings[0]["vaddr"], 16) if strings else 0
    hi = int(strings[-1]["vaddr"], 16) if strings else 0
    files = []
    for m in re.finditer(rb"[A-Za-z0-9_]{3,40}\.(?:cpp|h)\x00", data):
        va = BASE + m.start()
        if lo - 0x4000 <= va <= hi + 0x4000:
            files.append({"vaddr": f"0x{va:x}", "name": m.group()[:-1].decode()})

    diffs = {}
    for label, path in (("A7S", A7S), ("A6300", A6300)):
        d = open(path, "rb").read()
        otros = {m.group().decode("latin1") for m in re.finditer(rb"[\x20-\x7e]+", d)}
        comunes = sum(1 for s in strings
                      if s["text"].replace("[CAMERA_MAIN]: ", "") in otros)
        diffs[label] = {
            "prefijo": d.count(PREFIX),
            "comunes_texto_a_texto": comunes,
            "solo_a6000": len(strings) - comunes,
        }

    out = {
        "milestone": "S126",
        "module": "CAMERA_MAIN",
        "counts": {"strings": len(strings), "functions": len(fmap),
                   "submodules": len(sub_rows), "source_files": len(files)},
        "range": [strings[0]["vaddr"], strings[-1]["vaddr"]] if strings else [],
        "submodules": sub_rows,
        "functions": fmap,
        "source_files": files,
        "diff": diffs,
    }
    json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "CAMERA_MAIN", "count": len(strings), "strings": strings},
              open(os.path.join(HERE, "strings_raw.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "CAMERA_MAIN", "functions": fmap},
              open(os.path.join(HERE, "func_map.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out["counts"], indent=1))
    print("rango:", out["range"])
    print("sub-módulos:", [(r["submodule"], r["n"]) for r in sub_rows[:14]])
    print("diferencial:", diffs)


if __name__ == "__main__":
    main()
