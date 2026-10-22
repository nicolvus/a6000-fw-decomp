#!/usr/bin/env python3
"""S131 — `[VPH_API]`: la API del subsistema de display VPH (106 trazas).

Extrae las 106 cadenas `[VPH_API]`, las clasifica por su sintaxis de API
(`<nombre>` = entrada/setter, `<nombre>_sub` = variante "sub", `>nombre<` = salida/getter)
y las mapea a su función emisora con el mapa global de referencias PIC (regla estricta,
`analysis/s106_imaging_cap/pic_refs_strict_global.json`).

Salida: analysis/s131_vph_api/vph_api.json
"""
import json
import os
import re
import struct
from collections import Counter, defaultdict

BASE = 0x43541000
A6000 = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
PICMAP = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
HERE = os.path.dirname(os.path.abspath(__file__))
PAT = re.compile(rb"\[VPH_API\][\x20-\x7e]*")
API = re.compile(r"^\[VPH_API\]([<>])([a-z0-9_]+)([<>]|=)")


def main():
    data = open(A6000, "rb").read()
    a7s = open(A7S, "rb").read()
    a6300 = open(A6300, "rb").read()
    refs = json.load(open(PICMAP))

    cadenas = []
    for m in PAT.finditer(data):
        va = BASE + m.start()
        txt = m.group().decode("latin1")
        mm = API.match(txt)
        if not mm:
            kind = "otro"
            nombre = None
        else:
            signo, nombre, cierre = mm.groups()
            if signo == "<":
                kind = "entrada_sub" if nombre.endswith("_sub") else "entrada"
            else:
                kind = "salida"
        cadenas.append({
            "vaddr": f"0x{va:x}",
            "texto": txt,
            "kind": kind,
            "nombre": nombre,
            "sitios": [f"0x{s:x}" for s in refs.get(f"0x{va:x}", [])],
        })

    # funciones: prólogos Thumb
    prolog = []
    for a in range(0x43541000, 0x43A00000, 2):
        h = struct.unpack_from("<H", data, a - BASE)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            prolog.append(a)
        elif h == 0xE92D and struct.unpack_from("<H", data, a - BASE + 2)[0] & 0x4000:
            prolog.append(a)

    def func_de(sitio):
        cand = [p for p in prolog if p <= sitio and sitio - p <= 0x4000]
        return f"0x{cand[-1]:x}" if cand else None

    for c in cadenas:
        c["funciones"] = sorted({func_de(int(s, 16)) for s in c["sitios"]} - {None})

    por_func = defaultdict(list)
    for c in cadenas:
        for f in c["funciones"]:
            por_func[f].append(c)

    # nombres de API y sus variantes
    fam = defaultdict(dict)
    for c in cadenas:
        if not c["nombre"]:
            continue
        n = c["nombre"]
        base = n[:-4] if n.endswith("_sub") else n
        fam[base][c["kind"]] = c["vaddr"]

    # ficheros fuente en la zona
    lo, hi = int(cadenas[0]["vaddr"], 16), int(cadenas[-1]["vaddr"], 16)
    ficheros = sorted({
        f"0x{BASE + m.start():x}:{m.group()[:-1].decode()}"
        for m in re.finditer(rb"[A-Za-z0-9_]{3,40}\.(?:cpp|h)\x00", data)
        if lo - 0x8000 <= BASE + m.start() <= hi + 0x8000
    })

    out = {
        "milestone": "S131",
        "module": "VPH_API",
        "counts": {
            "cadenas": len(cadenas),
            "entrada": sum(1 for c in cadenas if c["kind"] == "entrada"),
            "entrada_sub": sum(1 for c in cadenas if c["kind"] == "entrada_sub"),
            "salida": sum(1 for c in cadenas if c["kind"] == "salida"),
            "otro": sum(1 for c in cadenas if c["kind"] == "otro"),
            "familias": len(fam),
            "funciones": len(por_func),
            "referenciadas": sum(1 for c in cadenas if c["sitios"]),
        },
        "rango": [cadenas[0]["vaddr"], cadenas[-1]["vaddr"]],
        "cadenas": cadenas,
        "familias": fam,
        "funciones": {f: len(v) for f, v in sorted(por_func.items(), key=lambda kv: -len(kv[1]))},
        "ficheros_fuente": ficheros,
        "diff": {
            "a7s_prefijo": a7s.count(b"[VPH_API]"),
            "a6300_prefijo": a6300.count(b"[VPH_API]"),
            "a7s_token_vph": a7s.count(b"VPH"),
            "a6300_token_vph": a6300.count(b"VPH"),
            "a6000_token_vph": data.count(b"VPH"),
            "a7s_shutter_mute": a7s.count(b"shutter_mute"),
            "a6300_shutter_mute": a6300.count(b"shutter_mute"),
            "a6000_shutter_mute": data.count(b"shutter_mute"),
        },
    }
    dest = os.path.join(HERE, "vph_api.json")
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out["counts"], indent=1))
    print("rango:", out["rango"])
    print("funciones (top):", list(out["funciones"].items())[:8])
    print("diff:", out["diff"])
    print("escrito", dest)


if __name__ == "__main__":
    main()
