#!/usr/bin/env python3
"""CAM-01: ficheros fuente (.cpp/.h/.c) citados por las funciones de cada módulo CAMERA_MAIN*/APL (bytes, regla estricta)."""
import json, re, sys
sys.path.insert(0, "analysis/camera_closure")
import closure2 as K, closure as C
B, BASE, N = K.B, K.BASE, K.N
MODS = ["CAMERA_MAIN", "CAMERA_MAIN_CC", "CAMERA_MAIN_FC", "CAMERA_MAIN_IM", "CAMERA_MAIN_LC", "CAMERA_MAIN_TC", "CAMERA_MAIN_YC", "CAMERA_SA", "CAMERA_IS", "CAM_CMD", "CAM_DMM", "CAM_FUNC_MGR", "CAM_IMAGER", "CAM_SCALAR", "CAM_UTIL_ADJ", "CAM_UTIL_SENS", "CAMCORE"]

def cstr(a):
    o = a - BASE; e = B.index(b"\0", o)
    return B[o:e].decode("latin1")

def main():
    refs = K.S.scan(BASE, BASE + N)            # destino de cadena -> sitios
    starts = {}
    for t, sites in refs.items():
        s = cstr(t)
        for s0 in sites: starts[s0] = (t, s)
    srcs = {s0: v for s0, v in starts.items() if re.fullmatch(r"[\w./-]+\.(cpp|h|c|hpp)", v[1])}
    out = {}
    for m in MODS:
        pat = re.compile(r"^\[%s\](?!_)" % m)
        funcs = {}
        for s0, (t, s) in starts.items():
            if pat.match(s):
                funcs.setdefault(C.func_start(s0), []).append(s0)
        rows = []
        for f, ss in sorted((k, v) for k, v in funcs.items() if k):
            end = min(C.func_end(f), f + 0x1000)
            fs = sorted({v[1] for s0, v in srcs.items() if f <= s0 < end})
            rows.append({"func": hex(f), "n_trazas": len(ss), "fuentes": fs})
        con = [r for r in rows if r["fuentes"]]
        out[m] = {"funciones": len(rows), "con_fuente": len(con), "sin_fuente": len(rows) - len(con),
                  "fuentes": sorted({x for r in rows for x in r["fuentes"]}), "detalle": rows}
        print(m, len(rows), len(con), out[m]["fuentes"][:6])
    json.dump(out, open("analysis/camera_closure/sources.json", "w"), indent=1)

if __name__ == "__main__": main()
