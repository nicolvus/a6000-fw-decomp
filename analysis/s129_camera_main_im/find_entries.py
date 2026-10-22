#!/usr/bin/env python3
"""S129 — atribución de sitios a funciones: prólogo vs. destino de salto.

Compara dos criterios de "inicio de función" sobre los sitios PIC de
`[CAMERA_MAIN_IM]`:

  A) prólogo Thumb (`push {...,lr}` / `push.w {...,lr}`) más cercano hacia atrás;
  B) destino de salto (`bl`/`blx`/`b`/`b.w`) más cercano hacia atrás, es decir,
     una dirección a la que el propio firmware salta (criterio más fiable).

Salida: analysis/s129_camera_main_im/entries_cmp.json

Uso: .venv/bin/python analysis/s129_camera_main_im/find_entries.py
"""
import json
import os
import struct

BASE = 0x43541000
HERE = os.path.dirname(os.path.abspath(__file__))
BIN = "analysis/rea-independent/input/av-cam.bin"
GLOBAL = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
PREFIX = b"[CAMERA_MAIN_IM]"


def prologues(data):
    """Inicios Thumb: push {...,lr} (B5xx con lr) o push.w {...,lr}."""
    out = []
    for a in range(BASE, BASE + len(data) - 4, 2):
        o = a - BASE
        h = struct.unpack_from("<H", data, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
        elif h == 0xE92D and (struct.unpack_from("<H", data, o + 2)[0] & 0x4000):
            out.append(a)
    return out


def branch_targets(data):
    """Destinos de bl/blx/b/b.w (F000 xxxx con bits de tipo 9/C/D/E)."""
    out = set()
    for a in range(BASE, BASE + len(data) - 4, 2):
        o = a - BASE
        h1 = data[o] | (data[o + 1] << 8)
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = data[o + 2] | (data[o + 3] << 8)
        if (h2 & 0xD000) not in (0x9000, 0xC000, 0xD000, 0xE000):
            continue
        s = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
        if s & 0x400000:
            s -= 0x800000
        out.add((a + 4 + s) & 0xFFFFFFFF)
    return out


def enclosing(sorted_list, addr, maxback=0x4000):
    lo, hi = 0, len(sorted_list)
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_list[mid] <= addr:
            lo = mid + 1
        else:
            hi = mid
    if lo == 0:
        return None
    cand = sorted_list[lo - 1]
    return cand if addr - cand <= maxback else None


def main():
    data = open(BIN, "rb").read()
    starts = prologues(data)
    tgts = sorted(t for t in branch_targets(data) if BASE <= t < BASE + len(data))
    g = json.load(open(GLOBAL))

    strings = []
    i = data.find(PREFIX)
    while i >= 0:
        e = i
        while e < len(data) and data[e] != 0:
            e += 1
        strings.append({"vaddr": BASE + i, "text": data[i:e].decode("latin1")})
        i = data.find(PREFIX, i + 1)

    rows, by_a, by_b = [], {}, {}
    for s in strings:
        for site in g.get(f"0x{s['vaddr']:x}", []):
            site = int(site)
            a = enclosing(starts, site)
            b = enclosing(tgts, site)
            rows.append({"string": f"0x{s['vaddr']:x}", "site": f"0x{site:x}",
                         "func_prologue": f"0x{a:x}" if a else None,
                         "func_target": f"0x{b:x}" if b else None})
            by_a.setdefault(a, []).append((site, s))
            by_b.setdefault(b, []).append((site, s))

    json.dump({"sites": rows,
               "n_sites": len(rows),
               "n_funcs_prologue": len(by_a),
               "n_funcs_target": len(by_b),
               "funcs_target": sorted(f"0x{x:x}" for x in by_b if x)},
              open(os.path.join(HERE, "entries_cmp.json"), "w"), indent=1)
    diff = [r for r in rows if r["func_prologue"] != r["func_target"]]
    print(f"cadenas={len(strings)} sitios={len(rows)} "
          f"funcs(prologo)={len(by_a)} funcs(destino)={len(by_b)} "
          f"discrepancias={len(diff)}")
    for r in diff:
        print(r["site"], r["func_prologue"], "->", r["func_target"], r["string"])


if __name__ == "__main__":
    main()
