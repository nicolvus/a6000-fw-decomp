#!/usr/bin/env python3
"""S130 — los 20 módulos "NUEVO/PROPIO" del mapa de etiquetado (S128): ¿contenido nuevo o
solo otra etiqueta?

Método: para cada prefijo clasificado como NUEVO/PROPIO en S128, se extrae el **núcleo** de
cada mensaje (el texto que sigue a "[PREFIX]: ") y se busca esa cadena como **subcadena** en
la A7S fw3.20 y en el A6300 fw2.01. Si aparece, se anota con qué etiqueta la envuelve el otro
firmware (o si va sin etiqueta).

  * ETIQUETADO     : ≥ 80 % de los núcleos existen en la A7S (con otra etiqueta o sin ella);
  * PARCIAL        : 20-80 %;
  * CONTENIDO NUEVO: < 20 % -> la fw3.21 de la A6000 trae mensajes que el otro firmware no
                      tiene (núcleo o etiqueta).

Salida: analysis/s130_new_modules/new_modules.json
"""
import json
import os
import re
from collections import Counter, defaultdict

A6000 = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
S128 = "analysis/s128_label_map/label_map.json"
HERE = os.path.dirname(os.path.abspath(__file__))
PAT = re.compile(rb"[\x20-\x7e]{4,}")
PREF = re.compile(r"^\[([A-Z][A-Z0-9_]{1,24})\]")


def runs(data):
    out = []
    for m in PAT.finditer(data):
        t = m.group().decode("latin1")
        mm = PREF.match(t)
        out.append((t, mm.group(1) if mm else None))
    return out


def nucleo(pref, texto):
    """Texto sin la etiqueta "[PREFIX]: " (queda el "resto")."""
    i = texto.find("]")
    if i < 0:
        return texto
    resto = texto[i + 1:]
    if resto.startswith(":"):
        resto = resto[1:]
    if resto.startswith(" "):
        resto = resto[1:]
    return resto


def main():
    a6000 = open(A6000, "rb").read()
    a7s = open(A7S, "rb").read()
    a6300 = open(A6300, "rb").read()
    mapa = json.load(open(S128))
    nuevos = [r for r in mapa["modulos"] if r["clase"] == "NUEVO/PROPIO"]

    # prefijo -> texto completo, por runs de la A6000
    por_pref = defaultdict(list)
    for t, p in runs(a6000):
        if p:
            por_pref[p].append(t)

    # runs del A7S con su prefijo, para saber qué etiqueta envuelve a un núcleo
    runs7s = runs(a7s)

    filas = []
    for r in sorted(nuevos, key=lambda x: -x["n_a6000"]):
        pref = r["prefijo"]
        cores = []
        for t in por_pref[pref]:
            c = nucleo(pref, t)
            if c:
                cores.append(c)
        n7 = n6 = 0
        et7 = Counter()
        ejemplos = []
        for c in cores:
            cb = c.encode("latin1")
            if cb in a7s:
                n7 += 1
                # ¿con qué etiqueta aparece en la A7S?
                et = None
                for t, p in runs7s:
                    if c in t:
                        et = p
                        break
                et7[et or "(sin etiqueta)"] += 1
                if len(ejemplos) < 2:
                    ejemplos.append({"a6000": f"[{pref}]: {c[:70]}",
                                     "a7s": f"[{et}] {c[:60]}" if et else c[:70]})
            if cb in a6300:
                n6 += 1
        frac = n7 / max(1, len(cores))
        if frac >= 0.8:
            clase = "ETIQUETADO"
        elif frac >= 0.2:
            clase = "PARCIAL"
        else:
            clase = "CONTENIDO NUEVO"
        filas.append({
            "prefijo": pref,
            "n_a6000": len(cores),
            "nucleos_en_a7s": n7,
            "nucleos_en_a6300": n6,
            "fraccion": round(frac, 3),
            "etiqueta_en_a7s": dict(et7.most_common(4)),
            "clase": clase,
            "ejemplos": ejemplos,
        })

    out = {"milestone": "S130",
           "counts": dict(Counter(f["clase"] for f in filas)),
           "modulos": filas}
    dest = os.path.join(HERE, "new_modules.json")
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print("modulos:", len(filas), out["counts"])
    for f in filas:
        print(f"  {f['prefijo']:16s} n={f['n_a6000']:4d} a7s={f['nucleos_en_a7s']:4d} "
              f"a6300={f['nucleos_en_a6300']:4d} frac={f['fraccion']:.2f} {f['clase']:14s} "
              f"{f['etiqueta_en_a7s']}")
    print("escrito", dest)


if __name__ == "__main__":
    main()
