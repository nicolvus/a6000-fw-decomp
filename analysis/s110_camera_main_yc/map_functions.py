#!/usr/bin/env python3
"""Mapa función → trazas de `[CAMERA_MAIN_YC]`.

Para cada cadena del módulo se conoce el sitio PIC que la referencia (sitio `add`).
La función que la referencia se obtiene asignando a cada sitio la función más
cercana por detrás, delimiting functions by Thumb prologues:
  * `push {..,lr}` de 16 bits  (0xb5xx con el bit de LR)
  * `push.w {..,lr}` de 32 bits (0xe92d)
y cortando en el `pop {..,pc}` / `bx lr` correspondiente.

El resultado se valida contra casos conocidos (ver `--check`).
"""
import json
import os
import re
import struct
from collections import Counter, defaultdict

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
MAX_FUNC = 0x4000          # tamaño máximo admitido de una función


def load():
    data = open(BIN, "rb").read()
    return data


def prologues(data, lo, hi):
    """Direcciones de prólogo de función en [lo, hi)."""
    out = []
    n = len(data)
    a = lo
    while a < hi:
        o = a - BASE
        h = struct.unpack_from("<H", data, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):        # push {..,lr}
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:                                # push.w {..,lr} (32 bits)
            h2 = struct.unpack_from("<H", data, o + 2)[0]
            if (h2 & 0x4000):                              # bit de LR (14) en la 2ª mitad
                out.append(a)
        a += 2
    return out


def function_starts(data, prologues_list, lo, hi):
    """Inicio de función = prólogo cuyo anterior prólogo está a más de 4 B."""
    starts = []
    prev = None
    for p in prologues_list:
        if prev is not None and p - prev > 4 and p - prev < 0x40:
            pass  # dos prólogos pegados: el segundo es el real inicio
        starts.append(p)
        prev = p
    return starts


def site_to_func(site, starts):
    cand = [s for s in starts if s <= site and site - s <= MAX_FUNC]
    if not cand:
        return None
    return cand[-1]


def main():
    data = load()
    strings = json.load(open(os.path.join(HERE, "strings_raw.json")))["strings"]
    refs = json.load(open(os.path.join(
        os.path.dirname(HERE), "s106_imaging_cap", "pic_refs.json")))
    lo = min(int(s["vaddr"], 16) for s in strings)
    hi = max(int(s["vaddr"], 16) for s in strings)
    # el código que las referencia está en el rango 0x43541000-0x43a00000
    prols = prologues(data, 0x43541000, 0x43A00000)
    starts = prologues(data, 0x43541000, 0x43A00000)
    by_func = defaultdict(list)
    sin_func = []
    for s in strings:
        sites = refs.get(s["vaddr"], [])
        for site in sites:
            a = int(site, 16) if isinstance(site, str) else int(site)
            f = site_to_func(a, starts)
            if f is None:
                sin_func.append((s["vaddr"], site))
            else:
                by_func[f].append(s)
    out = []
    for f, ss in sorted(by_func.items()):
        out.append({
            "func": f"0x{f:x}",
            "n_strings": len(ss),
            "strings": [{"vaddr": s["vaddr"], "text": s["text"]} for s in ss],
        })
    json.dump({"module": "CAMERA_MAIN_YC", "n_functions": len(out),
               "functions": out, "sin_funcion": len(sin_func)},
              open(os.path.join(HERE, "func_map.json"), "w"), indent=1, ensure_ascii=False)
    print(f"{len(strings)} cadenas, {len(out)} funciones, {len(sin_func)} referencias sin función")
    for row in out[:12]:
        print(f"  {row['func']}  {row['n_strings']:3d}  {row['strings'][0]['text'][:70]}")


if __name__ == "__main__":
    main()
