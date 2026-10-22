#!/usr/bin/env python3
"""S109 — diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01 del módulo `[CDIAG]`.

Extrae las cadenas `[CDIAG]` de cada firmware, las compara por texto y reporta:
 - cadenas presentes solo en un modelo;
 - clases (nombres `11CdCtrlHdDec`) y ficheros fuente embebidos en cada modelo.

Salida: analysis/s109_cdiag/cdiag_diff.json
"""
import json
import os
import re

BASE = 0x43541000
MODELS = {
    "A6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "A7S_fw320": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                  "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300_fw201": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}


def cstr(blob, off, maxlen=300):
    e = off
    while e < len(blob) and e < off + maxlen and 32 <= blob[e] < 127:
        e += 1
    return blob[off:e].decode("latin1")


def extract(path):
    blob = open(path, "rb").read()
    out = []
    s = 0
    while True:
        i = blob.find(b"[CDIAG]", s)
        if i < 0:
            break
        st = i
        while st > 0 and 32 <= blob[st - 1] < 127:
            st -= 1
        out.append((BASE + i, BASE + st, cstr(blob, st)))
        s = i + 1
    # las clases y los ficheros se buscan SOLO en la vecindad de las cadenas
    # [CDIAG] (si no, se recoge todo el RTTI del binario)
    idx = [i for i in range(len(blob)) if blob.startswith(b"[CDIAG]", i)]
    lo = max(0, min(idx) - 0x600)
    hi = min(len(blob), max(idx) + 0x900)
    classes = []
    for m in re.finditer(rb"\d{1,3}[A-Z][A-Za-z0-9_]{3,40}\x00", blob[lo:hi]):
        v = BASE + lo + m.start()
        t = m.group()[:-1].decode("latin1")
        if re.match(r"^\d+Cd", t):
            classes.append({"vaddr": f"0x{v:x}", "text": t})
    srcs = []
    for m in re.finditer(rb"[A-Za-z0-9_]{2,40}\.(?:cpp|h)\x00", blob[lo:hi]):
        v = BASE + lo + m.start()
        t = m.group()[:-1].decode("latin1")
        if t.lower().startswith("cd"):
            srcs.append({"vaddr": f"0x{v:x}", "text": t})

    sigs = []
    for m in re.finditer(rb"CDIAGER [ -~]{3,}", blob):
        v = BASE + m.start()
        sigs.append({"vaddr": f"0x{v:x}", "text": m.group().decode("latin1")})
    return {
        "path": path,
        "size": len(blob),
        "tokens": len(out),
        "strings": [{"token_vaddr": f"0x{t:x}", "vaddr": f"0x{s:x}", "text": x}
                    for t, s, x in out],
        "classes": classes,
        "source_files": srcs,
        "signatures": sigs,
    }


def main():
    data = {}
    for model, path in MODELS.items():
        if not os.path.exists(path):
            print(f"{model}: no disponible ({path})")
            continue
        data[model] = extract(path)
        print(f"{model}: {data[model]['tokens']} tokens [CDIAG], "
              f"{len(data[model]['classes'])} clases, "
              f"{len(data[model]['source_files'])} ficheros cd*")

    # comparación por texto
    texts = {m: {s["text"] for s in d["strings"]} for m, d in data.items()}
    cmp = {}
    base_model = "A6000_fw321"
    if base_model in texts:
        for m, t in texts.items():
            if m == base_model:
                continue
            cmp[m] = {
                "solo_en_A6000": sorted(texts[base_model] - t),
                "solo_en_" + m: sorted(t - texts[base_model]),
                "comunes": len(texts[base_model] & t),
            }
    out = {"models": {m: {k: v for k, v in d.items() if k != "strings"}
                      for m, d in data.items()},
           "comparison": cmp}
    dest = "analysis/s109_cdiag/cdiag_diff.json"
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    # tabla de registro de clases (scan_class_table.py) por modelo
    tablas = {}
    if os.path.exists("analysis/s109_cdiag/cdiag_class_table.json"):
        with open("analysis/s109_cdiag/cdiag_class_table.json") as fh:
            tablas = json.load(fh)

    # se fusiona la comparación textual en cdiag.json
    cj = "analysis/s109_cdiag/cdiag.json"
    if os.path.exists(cj):
        with open(cj) as fh:
            dat = json.load(fh)
        dat.setdefault("differential", {})
        for m, c in cmp.items():
            dat["differential"].setdefault(m, {})
            dat["differential"][m].update({
                "text_comparison": {
                    "comunes": c["comunes"],
                    "solo_en_A6000": c["solo_en_A6000"],
                    "solo_en_" + m: c["solo_en_" + m],
                },
                "classes": [{"vaddr": x["vaddr"], "text": x["text"]}
                            for x in data[m]["classes"]],
                "source_files": data[m]["source_files"],
                "n_signatures_cdiager": len(data[m]["signatures"]),
            })
        for m, t in tablas.items():
            dat.setdefault("differential", {}).setdefault(m, {})
            dat["differential"][m]["class_registry_table"] = {
                "table_vaddr": t["table_vaddr"],
                "table_end_vaddr": t["table_end_vaddr"],
                "n_entries": t["n_entries"],
                "classes": [e["class"] for e in t["entries"]],
            }
        with open(cj, "w") as fh:
            json.dump(dat, fh, indent=1, ensure_ascii=False)
        print("fusionado en", cj)
    for m, c in cmp.items():
        print(f"--- {m}: comunes={c['comunes']} "
              f"solo_A6000={len(c['solo_en_A6000'])} solo_{m}={len(c['solo_en_' + m])}")
        for x in c["solo_en_A6000"][:40]:
            print("   solo A6000:", x)
        for x in c["solo_en_" + m][:40]:
            print(f"   solo {m}:", x)
    print("escrito", dest)


if __name__ == "__main__":
    main()
