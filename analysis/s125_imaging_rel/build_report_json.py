#!/usr/bin/env python3
"""S125 — construye `imaging_rel.json` (datos estructurados del hito).

Entradas: `a6000_scan.json`, `a7s_scan.json`, `a6300_scan.json`, `diff.json`
(generados por `scan_imaging_modules.py` y `build_diff.py`).

Salida:  analysis/s125_imaging_rel/imaging_rel.json
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PREFIXES = {"IMAGING_REL": "[IMAGING_REL]: ", "IMAGING": "[IMAGING]: "}
GENERIC_SUFFIXES = ("FATAL! %s:%d", "FATAL! %s:%d [0x%x]", "%s:%d \n")


def core(text):
    for p in PREFIXES.values():
        if text.startswith(p):
            return text[len(p):]
    return text


def is_generic(text):
    return core(text) in GENERIC_SUFFIXES


def tag_of(c):
    for t in re.findall(r"\[[^\[\]]{3,40}\]", c):
        if "%" in t or not re.search(r"[A-Za-z]", t):
            continue
        return t
    m = re.match(r"([A-Za-z][A-Za-z0-9_]{2,}\))", c)
    if m:
        return m.group(1)
    return "(sin etiqueta)"


def main():
    scan = json.load(open(os.path.join(HERE, "a6000_scan.json")))
    diff = json.load(open(os.path.join(HERE, "diff.json")))
    ff = scan["func_files"]

    out = {
        "hito": "S125",
        "titulo": "Los módulos de trazas [IMAGING_REL] y [IMAGING] de la A6000 fw3.21",
        "perfil": scan["profile"],
        "binario": scan["bin"],
        "base": scan["base"],
        "metodo": {
            "referencias": "esquema PIC, regla estricta canónica (analysis/s106_imaging_cap/"
                           "scan_pic_refs_strict.py): cada `add rX,pc` se empareja con el "
                           "`ldr rX,[pc,#imm]` más cercano por detrás (ventana 4 KB)",
            "funciones": "prólogo Thumb `push {..,lr}` más cercano por detrás (máx. 16 KB)",
            "ficheros": "literal `__FILE__` (nombre .cpp/.h) referenciado dentro de la función",
            "nota": "toda cifra de sitios indica la regla usada",
        },
        "modulos": {},
        "diferencial": {},
    }

    for mod, pref in PREFIXES.items():
        m = scan["modules"][mod]
        blocks = {}
        for r in m["strings"]:
            c = core(r["text"])
            tg = tag_of(c)
            gen = is_generic(r["text"])
            key = "(genérico)" if gen else tg
            b = blocks.setdefault(key, {
                "tag": tg, "n": 0, "n_sites": 0, "generico": gen,
                "funciones": {}, "cadenas": [],
            })
            b["n"] += 1
            b["n_sites"] += len(r["sites"])
            b["cadenas"].append({
                "vaddr": r["vaddr"], "texto": r["text"], "sitios": r["sites"],
                "funciones": [fu["func"] for fu in r["funcs"]],
            })
            for fu in r["funcs"]:
                if not fu["func"]:
                    continue
                b["funciones"].setdefault(fu["func"], []).append(r["vaddr"])

        # atribución de fichero por cadena (primer fichero del dueño de la función)
        for key, b in blocks.items():
            b["ficheros"] = sorted({f for fn in b["funciones"] for f in ff.get(fn, [])})

        out["modulos"][mod] = {
            "prefijo": pref,
            "n_cadenas": m["n"],
            "rango": [m["lo"], m["hi"]],
            "n_referenciadas": m["n_referenced"],
            "n_sin_referencia": m["n"] - m["n_referenced"],
            "n_sitios": m["n_sites"],
            "n_funciones": m["n_functions"],
            "n_cadenas_genericas": sum(1 for r in m["strings"] if is_generic(r["text"])),
            "n_sitios_genericos": sum(len(r["sites"]) for r in m["strings"] if is_generic(r["text"])),
            "n_cadenas_especificas": sum(1 for r in m["strings"] if not is_generic(r["text"])),
            "n_sitios_especificos": sum(len(r["sites"]) for r in m["strings"] if not is_generic(r["text"])),
            "n_funciones_con_especifico": sum(
                1 for f, msgs in m["func_map"].items()
                if any(not x["generic"] for x in msgs)),
            "bloques": dict(sorted(blocks.items(), key=lambda kv: -kv[1]["n"])),
            "ficheros_fuente": m["src_files"],
            "cadenas": [
                {"vaddr": r["vaddr"], "texto": r["text"], "sitios": r["sites"],
                 "funciones": [fu["func"] for fu in r["funcs"]],
                 "fichero": sorted({f for fu in r["funcs"] if fu["func"]
                                    for f in ff.get(fu["func"], [])})}
                for r in m["strings"]],
        }

    for mod in PREFIXES:
        d = diff["modules"][mod]
        out["diferencial"][mod] = {}
        for prof in ("A7S", "A6300"):
            po = d["per_profile"][prof]
            out["diferencial"][mod][prof] = {
                "n_cadenas_etiquetadas_en_esa_camara": 0,
                "n_comunes_texto_a_texto": po["n_comunes"],
                "n_solo_a6000": po["n_solo_a6000"],
                "solo_a6000": po["solo_a6000"],
                "n_propias_del_ajeno": po["n_own"],
                "propias_del_ajeno": po["own"],
            }

    dest = os.path.join(HERE, "imaging_rel.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    for mod in PREFIXES:
        m = out["modulos"][mod]
        print(f"{mod}: {m['n_cadenas']} cadenas, {m['n_sitios']} sitios, "
              f"{m['n_funciones']} funciones, {len(m['bloques'])} bloques")
    print("->", dest)


if __name__ == "__main__":
    main()
