#!/usr/bin/env python3
"""S122 — mapa del módulo `[CAMERA_MAIN_TC]` (127 trazas) de la A6000 fw3.21.

Combina:
  * `strings_raw.json`      — las 127 cadenas y su posición,
  * `refs_targeted.json`    — referencias PIC por conjunto de destinos
                              (inicio de cadena, etiqueta `[CAMERA_MAIN_TC]` y texto interior),
                              regla **estricta** canónica (`scan_pic_refs_strict.py`),
  * `diff_versions.json`    — las mismas 127 trazas en A7S fw3.20 / A6300 fw2.01.

Atribuye cada sitio a su función Thumb por el prólogo (`push {..,lr}` / `push.w {..,lr}`).
Salida: tc_map.json
Uso: scan_tc.py
"""
import bisect
import json
import os
import re
import struct
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
PREFIX = b"[CAMERA_MAIN_TC]"
U16 = struct.Struct("<H").unpack_from

B = open(BIN, "rb").read()


def prologues(data, lo=0x43541000, hi=0x43C90000):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > len(data) - 4:
            break
        h = U16(data, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
        elif h == 0xE92D and (U16(data, o + 2)[0] & 0x4000):
            out.append(a)
        a += 2
    return out


def subblock(s):
    """Sub-bloque por el prefijo estructurado de la traza (tras `[CAMERA_MAIN_TC]: `)."""
    t = s["text_after_prefix"]
    m = re.match(r":?\s*(TC:[A-Za-z0-9_]+(?::[A-Za-z0-9_]+)?):", t)
    if m:
        return m.group(1).rstrip(":")
    if t.startswith("ApolloSA_"):
        return "ApolloSA"
    if ("SMART ZOOM" in t or "ARC_" in t or "RC." in t or "Ratio" in t
            or "GmvStitScl" in t or "GmvCoarScl" in t or "Stit" in t):
        return "SMART ZOOM"
    if "DDT" in t:
        return "TC:DDT"
    return "TC (varios)"


# Partición por CONTENIDO (rangos de índice sobre el orden de dirección de
# `strings_raw.json`): los siete bloques contiguos de la zona de cadenas.
CONTENT_BLOCKS = [
    (0, 31, "GYRO/CALIB"),
    (32, 44, "DIST"),
    (45, 91, "APL/ApolloSA"),
    (92, 107, "SMART ZOOM"),
    (108, 125, "DDT"),
    (126, 126, "JudgeBdroRslt"),
]


def content_blocks(strs):
    out = []
    for lo, hi, name in CONTENT_BLOCKS:
        v = strs[lo:hi + 1]
        out.append({
            "name": name,
            "idx_lo": lo,
            "idx_hi": hi,
            "n": len(v),
            "lo": v[0]["vaddr"],
            "hi": v[-1]["vaddr"],
            "sites": sum(len(x["sites"]) for x in v),
            "referenced": sum(1 for x in v if x["refs"]),
            "functions": sorted({f for x in v for f in x["funcs"]}),
            "strings": [x["vaddr"] for x in v],
        })
    return out


def main():
    strs = json.load(open(os.path.join(HERE, "strings_raw.json")))["strings"]
    refs = json.load(open(os.path.join(HERE, "refs_targeted.json")))["hits"]
    diff = json.load(open(os.path.join(HERE, "diff_versions.json")))
    starts = prologues(B)

    by_idx = defaultdict(list)
    for x in refs:
        by_idx[x["idx"]].append(x)

    funcs_sites = defaultdict(list)
    n_ref = n_sites = 0
    for i, s in enumerate(strs):
        rows = []
        for x in by_idx.get(i, []):
            a = int(x["add"], 16)
            k = bisect.bisect_right(starts, a) - 1
            f = starts[k] if k >= 0 else None
            row = {"add": x["add"], "ldr": x["ldr"], "kind": x["kind"],
                   "dest": x["dest"], "func": f"0x{f:x}" if f else None}
            rows.append(row)
            if f is not None:
                funcs_sites[f].append((i, a, x["kind"]))
        rows.sort(key=lambda r: int(r["add"], 16))
        s["refs"] = rows
        s["sites"] = [r["add"] for r in rows]
        s["funcs"] = sorted({r["func"] for r in rows if r["func"]})
        s["kinds"] = sorted({r["kind"] for r in rows})
        if rows:
            n_ref += 1
        n_sites += len(rows)

    dead = [s for s in strs if not s["refs"]]
    subs = defaultdict(list)
    for s in strs:
        subs[subblock(s)].append(s)

    a7s = diff["a7s_fw320"]
    a6300 = diff["a6300_fw201"]
    out = {
        "milestone": "S122",
        "module": "CAMERA_MAIN_TC",
        "counts": {
            "strings": len(strs),
            "distinct_texts": len({s["text"] for s in strs}),
            "referenced": n_ref,
            "dead": len(dead),
            "sites": n_sites,
            "functions": len(funcs_sites),
            "subblocks": len(subs),
            "refs_by_kind": {
                k: sum(1 for x in refs if x["kind"] == k)
                for k in ("string", "prefix", "inner")
            },
            "traces_with_two_pointers": sum(
                1 for s in strs if len([r for r in s["refs"]
                                        if r["kind"] in ("string", "prefix")]) >= 1
                and any(r["kind"] == "inner" for r in s["refs"])),
        },
        "rule": {
            "name": "strict",
            "file": "analysis/s106_imaging_cap/scan_pic_refs_strict.py",
            "description": "add rX,pc emparejado con el ldr rX,[pc,#imm] mas cercano por "
                           "detras del mismo registro (ventana 4 KB); destinos restringidos "
                           "al conjunto {inicio de cadena, etiqueta, texto interior}",
            "targeted_scanner": "analysis/s122_camera_main_tc/scan_refs_targeted.py",
        },
        "versions": {
            "a7s_fw320": {
                "token_camera_main_tc": a7s["token_camera_main_tc"],
                "texts_found": a7s["texts_found"],
                "texts_ref_pic": a7s["texts_ref_pic"],
                "pic_sites": a7s["pic_sites"],
            },
            "a6300_fw201": {
                "token_camera_main_tc": a6300["token_camera_main_tc"],
                "texts_found": a6300["texts_found"],
                "texts_ref_pic": a6300["texts_ref_pic"],
                "pic_sites": a6300["pic_sites"],
            },
        },
        "functions": [
            {"func": f"0x{f:x}", "n": len(v),
             "strings": [f"0x{strs[i]['vaddr']}" if False else strs[i]["vaddr"]
                         for i, _, _ in v],
             "sites": [f"0x{a:x}" for _, a, _ in v]}
            for f, v in sorted(funcs_sites.items())
        ],
        "subblocks": [
            {"name": k, "n": len(v),
             "lo": min(x["vaddr"] for x in v),
             "hi": max(x["vaddr"] for x in v),
             "functions": sorted({f for x in v for f in x["funcs"]}),
             "strings": [x["vaddr"] for x in v]}
            for k, v in sorted(subs.items(), key=lambda kv: -len(kv[1]))
        ],
        "subblocks_content": content_blocks(strs),
        "dead": [{"vaddr": s["vaddr"], "text": s["text"]} for s in dead],
        "strings": strs,
    }
    json.dump(out, open(os.path.join(HERE, "tc_map.json"), "w"), indent=1,
              ensure_ascii=False)
    print(json.dumps(out["counts"], indent=1))
    print("subbloques:", [(r["name"], r["n"]) for r in out["subblocks"]])
    print("contenido:", [(r["name"], r["n"], r["lo"], r["hi"], r["sites"],
                          r["referenced"], len(r["functions"]))
                         for r in out["subblocks_content"]])
    print("muertas:", [(d["vaddr"], d["text"]) for d in out["dead"]])


if __name__ == "__main__":
    main()
