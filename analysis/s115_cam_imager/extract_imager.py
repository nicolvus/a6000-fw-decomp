#!/usr/bin/env python3
"""S115 — extracción de las trazas `[CAM_IMAGER]` (driver del imager en la cámara).

- `strings_raw.json`: las cadenas con vaddr/offset/texto.
- `func_map.json`: función que referencia cada cadena (esquema PIC + prólogos Thumb).
- `summary.json`: sub-bloques, vocabulario P2S/ID y diferencial con la A7S fw3.20.

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
PREFIX = b"[CAM_IMAGER]"
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
        while e < len(data) and 32 <= data[e] < 127:
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
            h2 = struct.unpack_from("<H", data, o + 2)[0]
            if h2 & 0x4000:
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
    m = re.match(r"\[CAM_IMAGER\]:\s*([A-Za-z][A-Za-z0-9_]{1,19})[:\s]", text)
    return m.group(1) if m else None


def main():
    data = open(BIN, "rb").read()
    strings = extract(data)
    refs = json.load(open(os.path.join(S106, "pic_refs.json")))
    fmap = func_map(data, strings, refs)

    subs = defaultdict(list)
    for s in strings:
        t = subblock(s["text"])
        if t:
            subs[t].append(s)
    sub_rows = []
    for t, ss in sorted(subs.items(), key=lambda kv: -len(kv[1])):
        sub_rows.append({"submodule": t, "n": len(ss),
                         "lo": min(x["vaddr"] for x in ss),
                         "hi": max(x["vaddr"] for x in ss),
                         "sample": [x["text"][:100] for x in ss[:2]]})

    # vocabulario P2S / IDs de canal
    p2s = Counter()
    for s in strings:
        for m in re.finditer(r"P2S\(?([A-Za-z0-9_]*)", s["text"]):
            p2s[m.group(1) or "(generico)"] += 1
    handlers = sorted({m.group(0) for s in strings
                       for m in re.finditer(r"int_[a-z0-9_]+_handler", s["text"])})

    a7s = open(os.path.join(os.path.dirname(HERE), "..", A7S), "rb").read()
    comunes = 0
    solo = []
    for s in strings:
        core = s["text"][len("[CAM_IMAGER]: "):]
        if core.encode() in a7s:
            comunes += 1
        else:
            solo.append(s)

    out = {
        "milestone": "S115",
        "module": "CAM_IMAGER",
        "counts": {"strings": len(strings), "functions": len(fmap),
                   "submodules": len(sub_rows), "a7s_comunes": comunes,
                   "a7s_solo_a6000": len(solo)},
        "submodules": sub_rows,
        "p2s_channels": dict(p2s),
        "interrupt_handlers": handlers,
        "functions": fmap,
        "a7s_only_a6000": [{"vaddr": s["vaddr"], "text": s["text"]} for s in solo],
    }
    json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "CAM_IMAGER", "count": len(strings), "strings": strings},
              open(os.path.join(HERE, "strings_raw.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "CAM_IMAGER", "functions": fmap},
              open(os.path.join(HERE, "func_map.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out["counts"], indent=1))
    print("sub-módulos:", [(r["submodule"], r["n"]) for r in sub_rows])
    print("P2S:", dict(p2s))
    print("handlers:", handlers)
    print("solo A6000:", [s["vaddr"] for s in solo][:12])


if __name__ == "__main__":
    main()
