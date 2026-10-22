#!/usr/bin/env python3
"""S128 — mapa de etiquetado de la fw3.21: qué módulos son nuevos y cuáles se renombraron.

Para cada prefijo de módulo del mapa de S79 (`analysis/s79_modules/module_map.json`):
  * cuántas cadenas lleva en la A6000 fw3.21 y en la A7S fw3.20;
  * si la A7S usa ese prefijo;
  * cuántos de los textos de la A6000 existen en la A7S **sin** el prefijo.

De ahí se deriva la clasificación:
  * NUEVO      : la A7S no tiene ni el prefijo ni los textos;
  * RENOMBRADO : la A7S no usa el prefijo pero los textos coinciden (≥ 60 %);
  * PARCIAL    : coincidencias entre el 20 % y el 60 %;
  * PROPIO     : casi sin coincidencias (fw3.21 los escribió de nuevo).

Salida: analysis/s128_label_map/label_map.json
"""
import json
import os
import re
from collections import Counter

BASE = 0x43541000
A6000 = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
HERE = os.path.dirname(os.path.abspath(__file__))
S79 = "analysis/s79_modules/module_map.json"

PAT = re.compile(rb"[\x20-\x7e]{4,}")


def runs(data):
    return [m.group().decode("latin1") for m in PAT.finditer(data)]


def main():
    a6000 = open(A6000, "rb").read()
    a7s = open(A7S, "rb").read()
    modmap = json.load(open(S79))
    r6000 = runs(a6000)
    r7s = runs(a7s)
    set7s = set(r7s)
    # textos por prefijo en la A6000
    by_pref = defaultdict(list)
    for t in r6000:
        m = re.match(r"\[([A-Z][A-Z0-9_]{1,24})\]", t)
        if m:
            by_pref[m.group(1)].append(t)
    rows = []
    for pref, texts in sorted(by_pref.items(), key=lambda kv: -len(kv[1])):
        if len(texts) < 8:
            continue
        usa_prefijo_7s = sum(1 for t in r7s if t.startswith("[" + pref + "]"))
        if usa_prefijo_7s:
            # la A7S usa el mismo prefijo: se comparan los textos completos
            comunes = sum(1 for t in texts if t in set7s)
        else:
            # el texto es "[PREFIX]: resto" -> el "resto" empieza en len(pref)+4
            comunes = sum(1 for t in texts if t[len(pref) + 4:] in set7s)
        frac = comunes / len(texts)
        if usa_prefijo_7s and frac >= 0.6:
            clase = "IGUAL"
        elif frac >= 0.6:
            clase = "RENOMBRADO"
        elif frac >= 0.2:
            clase = "PARCIAL"
        else:
            clase = "NUEVO/PROPIO"
        rows.append({
            "prefijo": pref,
            "n_a6000": len(texts),
            "usa_prefijo_en_a7s": usa_prefijo_7s,
            "comunes_sin_prefijo": comunes,
            "fraccion": round(frac, 3),
            "clase": clase,
            "ejemplo": texts[0][:110],
        })
    out = {
        "milestone": "S128",
        "modulos": rows,
        "counts": dict(Counter(r["clase"] for r in rows)),
    }
    dest = os.path.join(HERE, "label_map.json")
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print("modulos analizados:", len(rows), out["counts"])
    for r in rows[:18]:
        print(f"  {r['prefijo']:18s} n={r['n_a6000']:4d} a7s_prefijo={r['usa_prefijo_en_a7s']:3d} "
              f"comunes={r['comunes_sin_prefijo']:4d} ({r['fraccion']:.2f}) {r['clase']}")
    print("escrito", dest)


from collections import defaultdict  # noqa: E402

if __name__ == "__main__":
    main()
