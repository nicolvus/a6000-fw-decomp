#!/usr/bin/env python3
"""S636: campos `[D0]`–`[D7]` dentro de dos trazas de `[CAM_UTIL_ADJ]` (A6000 fw3.21; presencia en A7S fw3.20 / A6300 fw2.01)."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "analysis/camera_closure"), str(ROOT / "analysis"), str(ROOT / "analysis/s106_imaging_cap")]
import labels as L, closure as C, closure2 as K, verify_s6xx as V

B, BASE = K.B, K.BASE


def build():
    s = L.prep(); refs = s["refs"]
    out = {"cadenas": [], "tokens": {}}
    for m in re.finditer(rb"\[CAM_UTIL_ADJ\]:   : \[D\d\]:%04x[^\x00]*", B):
        a = BASE + m.start()
        sites = refs.get(a, [])
        funcs = sorted({C.func_start(x) for x in sites if C.func_start(x)})
        out["cadenas"].append({"vaddr": hex(a), "texto": m.group().decode(), "sitios": [hex(x) for x in sites], "funciones": [hex(f) for f in funcs],
                               "refs_funcion": {hex(f): K.refs(f) for f in funcs},
                               "obturador": sorted({C.SHUTTER[x] for f in funcs for x in C.reach(f, 3) if x in C.SHUTTER})})
    for i in range(8):
        out["tokens"][f"[D{i}]"] = {k: C.tokens(p, f"[D{i}]:%04x") for k, p in V.FIRMWARE.items()}
    return out


if __name__ == "__main__":
    d = build()
    (ROOT / "analysis/s636_dfields/dfields.json").write_text(json.dumps(d, indent=1, ensure_ascii=False))
    for c in d["cadenas"]: print(c["vaddr"], c["texto"], c["sitios"], c["funciones"], c["refs_funcion"], c["obturador"])
    print(d["tokens"])
