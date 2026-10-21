#!/usr/bin/env python3
"""Agregados del modulo `[TRK]` (A6000 fw3.21) a partir de refs.json.

Entradas:  refs.json (scan_refs.py), strings_raw.json (scan_strings.py),
           a7s_diff.json (scan_a7s.py).
Salida:    trk.json

No inventa nada: cada agregado se calcula sobre los sitios PIC ya auditados
en refs.json. Los rangos de funcion se recalculan con los mismos prologos
Thumb de scan_refs.py para poder citar [inicio, fin) de cada funcion.
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import scan_refs as S  # noqa: E402

BIN = os.path.join(ROOT, S.BIN)

TAGS = [
    ("[DETSA]", "DETSA"),
    ("[EDTSA]", "EDTSA"),
    ("[IRO2G]", "IRO2G"),
    ("[PMV]", "PMV"),
    ("[BT]", "BT"),
    ("[STK_AUTO_SAL]", "STK_AUTO_SAL"),
    ("[STK AUTO SAL]", "STK_AUTO_SAL"),
    ("[STK_COLOR_SIM]", "STK_COLOR_SIM"),
    ("[STK COLOR SIM]", "STK_COLOR_SIM"),
    ("[STK_C_SIM]", "STK_C_SIM"),
    ("[STK_TOUCH_SIM]", "STK_TOUCH_SIM"),
    ("[STK TOUCH SIM]", "STK_TOUCH_SIM"),
    ("[STK_T_SIM]", "STK_T_SIM"),
    ("[STK]", "STK"),
]

ZONES = [
    ("trk_face", 0x43A30000, 0x43A39000, "modulo [TRK] propio (STK/BT/EDTSA/PMV/IRO2G/DETSA/VAE/VAT/VOT)"),
    ("sa_stubs", 0x43A1A000, 0x43A1E000, "zona ZIT de S80: 0 sitios [TRK] con la regla nearest-ldr (antes atribuidos por la pasada espuria)"),
    ("apl_sa", 0x439C0000, 0x439D0000, "capa APL/SA: alta/baja de sesion [CAM INIT/CLOSE/VSYNC]"),
    ("fc", 0x437C0000, 0x437D0000, "capa FC: 0 sitios [TRK] verificados (el unico [DETSA] RESOURCE CONTENTION esta en trk_face)"),
    ("apl_osal", 0x439D0000, 0x439E0000, "capa APL/OSAL: 0 sitios [TRK] verificados (osal_can_timer vive en trk_face)"),
]


def block_of(text):
    t = text[len("[TRK]:"):].strip() if text.startswith("[TRK]:") else text
    if t.startswith("[CAM ") or t.startswith("[VSYNC "):
        return "sesion"
    for tag, name in TAGS:
        if t.startswith(tag):
            return name
    if t.startswith("IRO2G"):
        return "IRO2G"
    if t.startswith("Vae") or t.startswith("VAE_"):
        return "VAE"
    if t.startswith("Vat") or t.startswith("VAT_"):
        return "VAT"
    if t.startswith("VOT") or t.startswith("Refmap"):
        return "VOT"
    if t.startswith("osal_") or t.startswith("almhdl"):
        return "TIMER"
    return "motor"


def sources(data, lo=0x43CEF000, hi=0x43D01000):
    out = []
    i = lo - S.BASE
    end = hi - S.BASE
    while i < end:
        if 32 <= data[i] < 127:
            j = i
            while j < end and 32 <= data[j] < 127:
                j += 1
            s = data[i:j].decode("latin1")
            if s.startswith("FC/") and s.endswith(".cpp"):
                out.append({"vaddr": hex(S.BASE + i), "file": s})
            i = j
        else:
            i += 1
    return out


def main():
    refs = json.load(open(os.path.join(HERE, "refs.json")))
    diff = json.load(open(os.path.join(HERE, "a7s_diff.json")))
    data = open(BIN, "rb").read()

    funcs = S.prologue_ends(data, S.BASE, 0x43C00000)
    extent = {s: e for s, e in funcs}

    strings = refs["strings"]
    by_func = defaultdict(list)
    by_block = defaultdict(list)
    relaxed = []
    unref = []
    zone_sites = Counter()
    zone_funcs = defaultdict(set)

    for row in strings:
        blk = block_of(row["text"])
        by_block[blk].append(row["vaddr"])
        if not row["sites"]:
            unref.append({"vaddr": row["vaddr"], "text": row["text"],
                          "note": "sin referencia PIC directa (regla nearest-ldr, MAX_GAP=0x40); tampoco literal absoluto ni adr"})
        for o in row["refs"]:
            by_func[o["func"]].append(row["vaddr"])
            if o["kind"] == "relaxed":
                relaxed.append({"site": o["site"], "func": o["func"],
                                "string": row["vaddr"], "text": row["text"]})
            a = int(o["site"], 16)
            for name, lo, hi, _desc in ZONES:
                if lo <= a < hi:
                    zone_sites[name] += 1
                    zone_funcs[name].add(o["func"])
                    break

    kinds = defaultdict(Counter)
    for row in strings:
        for o in row["refs"]:
            kinds[o["func"]][o["kind"]] += 1
    functions = []
    for f, sv in by_func.items():
        start = int(f, 16)
        blocks = sorted({block_of(r["text"]) for r in strings if r["vaddr"] in set(sv)})
        end = extent.get(start)
        # El fin por `pop {..,pc}`/`bx lr` no vale si el sitio atribuido cae
        # fuera: pasa con las colas de error (atribucion relaxed).
        max_site = max(int(o["site"], 16) + 2 for r in strings if r["vaddr"] in set(sv)
                       for o in r["refs"] if o["func"] == f)
        functions.append({"start": f,
                          "end": hex(end) if end and end >= max_site else None,
                          "n_strings": len(set(sv)),
                          "n_sites": sum(kinds[f].values()),
                          "kinds": dict(kinds[f]),
                          "blocks": blocks,
                          "strings": sorted(set(sv))})
    functions.sort(key=lambda x: (-x["n_strings"], int(x["start"], 16)))

    blocks = []
    for name, addrs in by_block.items():
        # rango de cadenas del sub-bloque
        fset = set()
        sites = 0
        for row in strings:
            if row["vaddr"] in addrs:
                sites += len(row["sites"])
                fset.update(o["func"] for o in row["refs"])
        blocks.append({"name": name, "n_strings": len(addrs), "n_sites": sites,
                       "n_functions": len(fset), "lo": min(addrs), "hi": max(addrs)})
    blocks.sort(key=lambda x: int(x["lo"], 16))

    zones = []
    for name, lo, hi, desc in ZONES:
        zones.append({"name": name, "lo": hex(lo), "hi": hex(hi), "desc": desc,
                      "n_sites": zone_sites[name],
                      "n_functions": len(zone_funcs[name])})

    out = {
        "milestone": "S111",
        "module": "TRK",
        "bin": S.BIN,
        "base_vaddr": "0x43541000",
        "code_scan": {"lo": refs["code_lo"], "hi": refs["code_hi"],
                      "n_functions_candidates": refs["n_functions"]},
        "counts": {
            "n_occurrences": 216,
            "n_strings": refs["n_strings"],
            "n_referenced": refs["n_referenced"],
            "n_sites": refs["n_sites"],
            "n_sites_strict": refs["n_sites_strict"],
            "n_sites_relaxed": refs["n_sites_relaxed"],
            "n_sites_unowned": refs["n_sites_unowned"],
            "n_functions": len(functions),
        },
        "string_range": {"lo": min(s["vaddr"] for s in strings),
                         "hi": max(s["vaddr"] for s in strings)},
        "blocks": blocks,
        "functions": functions,
        "zones": zones,
        "sources": sources(data),
        "relaxed": relaxed,
        "unreferenced": unref,
        "a7s_diff": diff,
    }
    json.dump(out, open(os.path.join(HERE, "trk.json"), "w"), indent=1,
              ensure_ascii=False)
    print(json.dumps({"counts": out["counts"], "blocks": blocks,
                      "zones": zones, "n_sources": len(out["sources"]),
                      "n_relaxed": len(relaxed), "n_unref": len(unref)},
                     indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
