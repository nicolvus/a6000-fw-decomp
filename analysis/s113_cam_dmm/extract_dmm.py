#!/usr/bin/env python3
"""S113 — extracción de las trazas `[CAM_DMM]` (gestor de memoria dinámico).

- `strings_raw.json`: las 54 cadenas con vaddr/offset/texto.
- `func_map.json`: función que referencia cada cadena (esquema PIC + prólogos Thumb).
- `summary.json`: operaciones, clases de error y diferencial con la A7S fw3.20.

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
PREFIX = b"[CAM_DMM]"
HERE = os.path.dirname(os.path.abspath(__file__))


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
    """Prólogos de función: push {..,lr} (16 bits) y push.w {..,lr} (32 bits)."""
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
    out = [{"func": f"0x{f:x}", "n_strings": len(ss),
            "strings": [{"vaddr": s["vaddr"], "text": s["text"]} for s in ss]}
           for f, ss in sorted(by_func.items())]
    return out


def main():
    data = open(BIN, "rb").read()
    strings = extract(data)
    refs_path = os.path.join(os.path.dirname(HERE), "s106_imaging_cap", "pic_refs.json")
    refs = json.load(open(refs_path))
    fmap = func_map(data, strings, refs)

    ops, errs = defaultdict(list), defaultdict(list)
    for s in strings:
        m = re.match(r"\[CAM_DMM\]:\s*([A-Za-z0-9_]+):\s*(.*)$", s["text"])
        if not m:
            continue
        op, rest = m.group(1), m.group(2)
        ops[op].append(s["vaddr"])
        e = re.search(r"(ERR_DMM_[A-Z_]+)", rest)
        if e:
            errs[e.group(1)].append(s["vaddr"])

    a7s = open(os.path.join(os.path.dirname(HERE), "..", A7S), "rb").read()
    comunes = 0
    solo = []
    for s in strings:
        core = s["text"][len("[CAM_DMM]: "):]
        if core.encode() in a7s:
            comunes += 1
        else:
            solo.append(s)

    out = {
        "milestone": "S113",
        "module": "CAM_DMM",
        "counts": {"strings": len(strings), "functions": len(fmap),
                   "operations": len(ops), "error_classes": len(errs),
                   "a7s_comunes": comunes, "a7s_solo_a6000": len(solo)},
        "operations": {k: {"n": len(v), "vaddrs": v} for k, v in sorted(ops.items())},
        "error_classes": {k: {"n": len(v), "vaddrs": v} for k, v in sorted(errs.items())},
        "functions": fmap,
        "a7s_only_a6000": [{"vaddr": s["vaddr"], "text": s["text"]} for s in solo],
    }
    json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "CAM_DMM", "count": len(strings), "strings": strings},
              open(os.path.join(HERE, "strings_raw.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "CAM_DMM", "functions": fmap},
              open(os.path.join(HERE, "func_map.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out["counts"], indent=1))
    print("operaciones:", {k: v["n"] for k, v in out["operations"].items()})
    print("errores:", {k: v["n"] for k, v in out["error_classes"].items()})
    print("funciones:", [(f["func"], f["n_strings"]) for f in fmap])
    print("solo A6000:", [s["vaddr"] for s in solo])


if __name__ == "__main__":
    main()
