#!/usr/bin/env python3
"""S125 — diferencial A6000 fw3.21 vs A7S fw3.20 y A6300 fw2.01.

Compara, texto a texto, las cadenas de los módulos `[IMAGING_REL]` y `[IMAGING]` de la
A6000 con las cadenas **sin etiqueta** de la A7S y del A6300.

Reglas:
  * `core` = texto de la cadena de la A6000 **sin** el prefijo de módulo
    (`[IMAGING_REL]: ` / `[IMAGING]: `).
  * `común`   = el `core` aparece literally en el blob ajeno.
  * `solo A6000` = el `core` no aparece en el blob ajeno.
  * `solo A7S/A6300` = cadenas del blob ajeno que contienen una *marca* distintiva del
    módulo (la etiqueta entre corchetes que sigue al prefijo, p. ej. `[PanoramaStitch]`,
    `[CapIdTblMgr)`) y cuyo texto no está en el conjunto de `core` de la A6000.

Salida: analysis/s125_imaging_rel/diff.json
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.join(REPO, "analysis/s125_imaging_rel")
BASE = 0x43541000

PREFIXES = {"IMAGING_REL": "[IMAGING_REL]: ", "IMAGING": "[IMAGING]: "}


def load(path):
    with open(path, "rb") as fh:
        return fh.read()


def nul_strings(data):
    out = []
    n = len(data)
    i = 0
    while i < n:
        c = data[i]
        if 32 <= c < 127:
            e = data.find(b"\x00", i)
            if e < 0:
                e = n
            if e > i:
                out.append((i, data[i:e].decode("latin-1")))
                i = e + 1
                continue
        i += 1
    return out


def tag_of(core):
    """Etiqueta distintiva entre corchetes del texto (o el prefijo `Nombre)`).

    Se descartan los corchetes que solo contienen especificadores de formato
    (`[0x%x]`, `[%s]`, ...).
    """
    for t in re.findall(r"\[[^\[\]]{3,40}\]", core):
        if "%" in t or not re.search(r"[A-Za-z]", t):
            continue
        return t
    m = re.match(r"([A-Za-z][A-Za-z0-9_]{2,}\))", core)
    if m:
        return m.group(1)
    return None


def main():
    scans = {}
    for prof in ("A6000", "A7S", "A6300"):
        scans[prof] = json.load(open(os.path.join(HERE, f"{prof.lower()}_scan.json")))

    others = {}
    for prof in ("A7S", "A6300"):
        d = json.load(open(os.path.join(HERE, f"{prof.lower()}_scan.json")))
        others[prof] = d["bin"]

    out = {"base": hex(BASE), "modules": {}}
    for mod, pref in PREFIXES.items():
        rows = scans["A6000"]["modules"][mod]["strings"]
        cores = {r["text"][len(pref):] for r in rows}
        mod_out = {"prefix": pref, "n_a6000": len(rows), "n_cores": len(cores), "per_profile": {}}
        tags = sorted({t for t in (tag_of(c) for c in cores) if t})
        mod_out["tags"] = tags
        for prof in ("A7S", "A6300"):
            data = load(os.path.join(REPO, others[prof]))
            strs = nul_strings(data)
            idx = {}
            for off, s in strs:
                idx.setdefault(s, []).append(off)
            comunes = sorted(c for c in cores if c in idx)
            solo6 = sorted(c for c in cores if c not in idx)
            # cadenas del blob ajeno con una marca del módulo y que no son core de la A6000
            own = []
            for off, s in strs:
                hit = [t for t in tags if t in s]
                if hit and s not in cores:
                    own.append({"offset": hex(off), "vaddr": hex(BASE + off), "text": s})
            own.sort(key=lambda r: r["offset"])
            mod_out["per_profile"][prof] = {
                "n_comunes": len(comunes),
                "n_solo_a6000": len(solo6),
                "solo_a6000": solo6,
                "comunes": [{"text": c, "vaddr": [hex(BASE + o) for o in idx[c]]} for c in comunes],
                "n_own": len(own),
                "own": own,
            }
        out["modules"][mod] = mod_out

    dest = os.path.join(HERE, "diff.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    for mod, mo in out["modules"].items():
        print(f"== {mod}: {mo['n_a6000']} cadenas A6000, {len(mo['tags'])} marcas")
        for prof, po in mo["per_profile"].items():
            print(f"   {prof}: comunes={po['n_comunes']} solo_a6000={po['n_solo_a6000']} "
                  f"propias_del_ajeno={po['n_own']}")
    print("->", dest)


if __name__ == "__main__":
    main()
