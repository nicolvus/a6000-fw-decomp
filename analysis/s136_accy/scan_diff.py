#!/usr/bin/env python3
"""S136 — diferencial del contenido de `[ACCY]`: ¿existe el texto en otros firmwares?

Para cada una de las 106 cadenas de la A6000 fw3.21 se busca, en la A7S fw3.20 y en la
A6300 fw2.01, (a) la cadena completa, (b) el "núcleo" (el texto tras el prefijo) y
(c) fragmentos distintivos.

Uso: .venv/bin/python analysis/s136_accy/scan_diff.py
"""
import json
import os
import re

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
HERE = os.path.dirname(os.path.abspath(__file__))


def cores(strings):
    """Núcleo de cada traza: el texto tras ']' inicial, sin el prefijo de módulo."""
    out = []
    for s in strings:
        t = s["text"]
        assert t.startswith("[ACCY]")
        rest = t[len("[ACCY]"):]
        # quita el nivel [INFO]/[DEBUG]/...
        m = re.match(r"\[[A-Z]+\]", rest)
        if m:
            rest = rest[m.end():]
        # quita el sub-módulo [XXX]
        m = re.match(r"\[[A-Za-z0-9_]+\]", rest)
        if m:
            rest = rest[m.end():]
        out.append((s["vaddr"], rest))
    return out


def main():
    raw = json.load(open(os.path.join(HERE, "accy_raw.json")))
    strings = raw["strings"]
    data7 = open(A7S, "rb").read()
    data6300 = open(A6300, "rb").read()
    res = []
    nfull7 = ncore7 = nfrag7 = 0
    nfull6 = ncore6 = nfrag6 = 0
    for vaddr, core in cores(strings):
        full = [s["text"] for s in strings if s["vaddr"] == vaddr][0]
        f7 = full.encode("latin1") in data7
        c7 = core.encode("latin1") in data7
        # fragmento distintivo: la parte alfanumérica más larga
        frags = [w for w in re.split(r"[^A-Za-z0-9_%]+", core) if len(w) >= 6]
        g7 = any(w.encode("latin1") in data7 for w in frags)
        f6 = full.encode("latin1") in data6300
        c6 = core.encode("latin1") in data6300
        g6 = any(w.encode("latin1") in data6300 for w in frags)
        nfull7 += f7; ncore7 += c7; nfrag7 += g7
        nfull6 += f6; ncore6 += c6; nfrag6 += g6
        res.append({"vaddr": vaddr, "full": full, "core": core,
                    "a7s_full": f7, "a7s_core": c7, "a7s_frag": g7,
                    "a6300_full": f6, "a6300_core": c6, "a6300_frag": g6})
    print(f"A7S  fw3.20: texto completo {nfull7}/106, núcleo {ncore7}/106, "
          f"algún fragmento {nfrag7}/106")
    print(f"A6300 fw2.01: texto completo {nfull6}/106, núcleo {ncore6}/106, "
          f"algún fragmento {nfrag6}/106")
    json.dump(res, open(os.path.join(HERE, "accy_diff.json"), "w"), indent=1)
    print("\n--- cores presentes en A7S (texto) ---")
    for r in res:
        if r["a7s_core"]:
            print(f"  {r['vaddr']} {r['core'][:80]!r}")
    print("\n--- fragmentos coincidentes en A7S pero núcleo ausente ---")
    for r in res:
        if r["a7s_frag"] and not r["a7s_core"]:
            print(f"  {r['vaddr']} {r['core'][:80]!r}")


if __name__ == "__main__":
    main()
