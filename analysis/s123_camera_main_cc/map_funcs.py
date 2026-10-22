#!/usr/bin/env python3
"""S123 — mapa función → traza de `[CAMERA_MAIN_CC]`.

Regla canónica de referencias: `analysis/s106_imaging_cap/scan_pic_refs_strict.py`
(regla **estricta**: cada `add rX,pc` se empareja con el `ldr rX,[pc,#imm]` más cercano
del mismo registro, ventana 4 KB). Ver `analysis/s106_imaging_cap/pic_xref_methodology.md`.

Los límites de función se calculan con **capstone**:
  * inicio = prólogo Thumb (`push {..,lr}` / `push.w {..,lr}`) más cercano por detrás;
  * fin    = primer `pop {..,pc}` / `bx lr` alcanzado al desensamblar hacia delante.
Para cada sitio de referencia se busca el prólogo **más cercano** cuyo intervalo
[ini, fin) contenga el sitio.

Además se calcula el conjunto completo de cadenas referenciadas por cada función
(emisor de trazas) para poder atribuirle ficheros fuente `.cpp`/`.h`.

Uso:  map_funcs.py [REFS_GLOBAL_JSON] [SALIDA]
"""
import json
import os
import struct
import sys

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
MAX_FUNC = 0x6000

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = False


def read_range(lo, hi):
    fh = open(BIN, "rb")
    fh.seek(lo - BASE)
    d = fh.read(hi - lo)
    fh.close()
    return d


def prologues(data, lo):
    """Direcciones de prólogo (relativas a lo) en los 16 bits alineados."""
    out = []
    a = 0
    while a + 2 <= len(data):
        h = struct.unpack_from("<H", data, a)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):          # push {..,lr}
            out.append(a)
            a += 2
            continue
        if h == 0xE92D and a + 4 <= len(data):                # push.w {..,lr}
            h2 = struct.unpack_from("<H", data, a + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def func_end(code, start_rel, base_vaddr):
    """Primera dirección (vaddr) del `pop {..,pc}` / `bx lr` tras el prólogo."""
    for ins in md.disasm(code[start_rel:], base_vaddr + start_rel):
        m = ins.mnemonic
        if m.startswith("pop") and "pc" in ins.op_str:
            return ins.address
        if m == "bx" and ins.op_str == "lr":
            return ins.address
    return None


def site_to_func(site, prols, data, base_vaddr):
    """(ini, fin) de la función que contiene el sitio, o (None, None)."""
    rel = site - base_vaddr
    best = None
    for p in prols:
        if p > rel:
            break
        if rel - p > MAX_FUNC:
            continue
        end = func_end(data, p, base_vaddr)
        if end is None:
            continue
        if base_vaddr + p <= site <= end:
            best = (base_vaddr + p, end)
    return best if best else (None, None)


def main():
    refs_path = (sys.argv[1] if len(sys.argv) > 1
                 else "/tmp/opencode/pic_strict_global.json")
    dest = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "func_map.json")
    refs = json.load(open(refs_path))
    strings = json.load(open(os.path.join(HERE, "cc_strings.json")))["strings"]

    lo_v = min(int(s["vaddr"], 16) for s in strings)
    hi_v = max(int(s["vaddr"], 16) for s in strings)
    sites = []
    for s in strings:
        for site in refs.get(s["vaddr"], []):
            sites.append((site, s))
    lo_c = min(site for site, _ in sites) - 0x8000
    hi_c = max(site for site, _ in sites) + 0x8000
    data = read_range(lo_c, hi_c)
    prols = prologues(data, lo_c)

    by_func = {}
    rows = []
    for site, s in sorted(sites, key=lambda x: x[0]):
        f, e = site_to_func(site, prols, data, lo_c)
        rows.append({"string": s["vaddr"], "text": s["text"], "site": f"0x{site:x}",
                     "func": f"0x{f:x}" if f else None,
                     "func_end": f"0x{e:x}" if e else None})
        if f:
            by_func.setdefault(f, []).append((e, s, site))

    funcs = []
    for f, items in sorted(by_func.items()):
        ss = [{"vaddr": s["vaddr"], "text": s["text"], "site": f"0x{site:x}"}
              for _, s, site in items]
        funcs.append({"func": f"0x{f:x}", "func_end": f"0x{items[0][0]:x}",
                      "n_strings": len(ss), "strings": ss})

    out = {"module": "CAMERA_MAIN_CC",
           "rule": "estricta (scan_pic_refs_strict.py)",
           "n_sites": len(rows), "n_functions": len(funcs),
           "functions": funcs, "xrefs": rows}
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print(f"sitios: {len(rows)}  funciones: {len(funcs)} -> {dest}")
    for fn in funcs:
        print(f"  {fn['func']}-{fn['func_end']}  n={fn['n_strings']}  "
              f"{fn['strings'][0]['text'][:66]}")


if __name__ == "__main__":
    main()
