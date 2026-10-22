#!/usr/bin/env python3
"""S123 — atribución de ficheros fuente a las funciones que emiten `[CAMERA_MAIN_CC]`.

Método: el mapa PIC estricto da, para cada cadena, los sitios `add` que la
referencian. Para cada **nombre de fichero `.cpp`/`.h`** se localizan sus sitios de
referencia y se asigna a la función que los contiene (prólogo + epílogo, con
capstone). Se marcan los ficheros referenciaados por funciones **dentro de la
región de código del módulo CC** y los de fuera.

Uso:  attr_sources.py [REFS_GLOBAL_JSON] [SALIDA]
"""
import json
import os
import re
import struct
import sys
import bisect
from collections import defaultdict

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
MAX_FUNC = 0x6000
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

# regiones de código donde viven las funciones que emiten trazas [CAMERA_MAIN_CC]
CC_REGIONS = [(0x4379ec84, 0x4379fc02, "capture-control"),
              (0x437a1a7e, 0x437a27b2, "lut"),
              (0x437a6890, 0x437a80a6, "ie"),
              (0x437a8fac, 0x437a9552, "miniraw"),
              (0x437ada6e, 0x437adb74, "makernote-playraw"),
              (0x4381d296, 0x4381d386, "camcore-3dlut")]


def prologues(data):
    out = []
    a = 0
    while a + 2 <= len(data):
        h = struct.unpack_from("<H", data, a)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D and a + 4 <= len(data):
            h2 = struct.unpack_from("<H", data, a + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def func_end(code, start_rel, base_vaddr, limit=0x6000):
    for ins in md.disasm(code[start_rel:start_rel + limit], base_vaddr + start_rel):
        if ins.mnemonic.startswith("pop") and "pc" in ins.op_str:
            return ins.address
        if ins.mnemonic == "bx" and ins.op_str == "lr":
            return ins.address
    return None


def main():
    refs_path = (sys.argv[1] if len(sys.argv) > 1
                 else "/tmp/opencode/pic_strict_global.json")
    dest = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "source_files.json")
    refs = json.load(open(refs_path))
    data = open(BIN, "rb").read()

    srcpat = re.compile(r"^[A-Za-z0-9_./]{3,60}\.(?:cpp|h)$")
    inv = defaultdict(list)
    for tgt, sites in refs.items():
        for s in sites:
            inv[s].append(int(tgt, 16))

    src_sites = []
    for tgt, sites in refs.items():
        t = int(tgt, 16)
        off = t - BASE
        if off < 0 or off >= len(data):
            continue
        e = off
        while e < len(data) and e < off + 80 and 32 <= data[e] < 127:
            e += 1
        txt = data[off:e].decode("latin1")
        if srcpat.match(txt):
            src_sites.append((t, txt, sites))
    src_sites.sort()

    lo_c = max(BASE, min(min(s[2]) for s in src_sites) - 0x8000)
    hi_c = min(BASE + len(data), max(max(s[2]) for s in src_sites) + 0x8000)
    code = data[lo_c - BASE:hi_c - BASE]
    prols = prologues(code)

    def owner(site):
        """Prólogo más cercano por detrás cuyo intervalo contenga el sitio."""
        rel = site - lo_c
        i = bisect.bisect_right(prols, rel) - 1
        while i >= 0:
            p = prols[i]
            if rel - p > MAX_FUNC:
                break
            end = func_end(code, p, lo_c)
            if end is not None and lo_c + p <= site <= end:
                return (lo_c + p, end)
            i -= 1
        return None

    def region_of(a, b):
        for lo, hi, name in CC_REGIONS:
            if lo <= a <= hi:
                return name
        return None

    rows = []
    for t, txt, sites in src_sites:
        owners = {}
        for s in sites:
            o = owner(s)
            if o:
                owners.setdefault(o, []).append(s)
        in_cc = []
        out_cc = []
        for (a, b), ss in sorted(owners.items()):
            rec = {"func": f"0x{a:x}", "func_end": f"0x{b:x}",
                   "sites": [f"0x{x:x}" for x in sorted(ss)]}
            reg = region_of(a, b)
            if reg:
                rec["region"] = reg
                in_cc.append(rec)
            else:
                out_cc.append(rec)
        rows.append({"vaddr": f"0x{t:x}", "name": txt,
                     "n_refs": len(sites),
                     "in_cc_regions": in_cc, "elsewhere": out_cc})

    json.dump({"module": "CAMERA_MAIN_CC", "cc_regions": CC_REGIONS,
               "files": rows}, open(dest, "w"), indent=1, ensure_ascii=False)
    print(f"ficheros fuente referenciados: {len(rows)}")
    for r in rows:
        if r["in_cc_regions"]:
            regs = sorted({x.get("region") for x in r["in_cc_regions"]})
            print(f"  {r['vaddr']} {r['name']:40s} refs={r['n_refs']:2d} CC={regs}")


if __name__ == "__main__":
    main()
