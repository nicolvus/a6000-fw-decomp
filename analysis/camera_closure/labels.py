#!/usr/bin/env python3
"""CAM-01 / OTROS: métricas por etiqueta `[X]` en av-cam A6000 fw3.21 (y presencia en A7S/A6300).

Por etiqueta: cadenas que contienen el token, cadenas con sitio de carga (`ldr`+`add pc` estricta, destino dentro de la cadena
y no después del token), funciones contenedoras (primer `push {…lr}` hacia atrás, ≤ 0x2000 B), llamadores `bl`, punteros a esas
funciones (literal, `ldr`+`add pc`, `movw`+`movt`), ficheros fuente `.cpp/.h/.c` cargados en ellas, alcance `bl` ≤ 3 al obturador.
shortcut: llamadas indirectas no seguidas; función = heurística de prólogo.
"""
import bisect, json, re, struct, sys
import numpy as np
sys.path.insert(0, "analysis/camera_closure"); sys.path.insert(0, "analysis")
import closure as C, closure2 as K, verify_s6xx as V

B, BASE, N = K.B, K.BASE, K.N
_S = {}


def prep():
    if _S: return _S
    refs = K.S.scan(BASE, BASE + N)
    _S["refs"] = refs; _S["keys"] = sorted(refs)
    _S["pic"] = K.pic_targets()
    arr = np.frombuffer(B[: N // 4 * 4], dtype="<u4")
    _S["u32"] = arr
    mm = {}
    lo = {}
    for o in range(0, N - 4, 2):
        h1 = struct.unpack_from("<H", B, o)[0]
        k = h1 & 0xFBF0
        if k not in (0xF240, 0xF2C0): continue
        h2 = struct.unpack_from("<H", B, o + 2)[0]
        if h2 & 0x8000: continue
        imm = ((h1 & 0xF) << 12) | (((h1 >> 10) & 1) << 11) | (((h2 >> 12) & 7) << 8) | (h2 & 0xFF); rd = (h2 >> 8) & 0xF
        if k == 0xF240: lo[rd] = (o, imm)
        elif rd in lo and o - lo[rd][0] <= 12:
            v = (imm << 16) | lo[rd][1]
            if 0x43541000 <= v < 0x43541000 + N + 1: mm.setdefault(v & ~1, []).append(BASE + lo[rd][0])
    _S["mm"] = mm
    srcs = {}
    for t, ss in refs.items():
        o = t - BASE; e = B.index(b"\0", o); s = B[o:e].decode("latin1")
        if re.fullmatch(r"[\w./-]+\.(cpp|h|c|hpp)", s):
            for x in ss: srcs[x] = s
    _S["srcs"] = srcs
    return _S


def fn_refs(f):
    s = prep(); v = {f, f | 1}
    lit = [hex(BASE + 4 * int(i)) for i in np.nonzero(np.isin(s["u32"], list(v)))[0]]
    pic = [hex(x) for x in s["pic"].get(f | 1, []) if C.func_start(x) == C.func_start(K.by_ldr(x))]
    return {"bl": len(K.bl_callers().get(f, [])), "literal": len(lit), "pic": len(pic), "movw_movt": len(s["mm"].get(f, []))}


def evaluate(label):
    s = prep(); tok = label.encode()
    strs = {}
    for m in re.finditer(re.escape(tok), B):
        o = m.start(); st = B.rfind(b"\0", 0, o) + 1
        strs.setdefault(BASE + st, (BASE + o, B[st:B.index(b"\0", o)].decode("latin1")))
    sites = {}; keys = s["keys"]
    for a, (tpos, text) in strs.items():
        i = bisect.bisect_left(keys, a); sites[a] = []
        while i < len(keys) and keys[i] <= tpos:
            sites[a] += s["refs"][keys[i]]; i += 1
    funcs = {}
    for a, ss in sites.items():
        for x in ss:
            f = C.func_start(x)
            if f: funcs.setdefault(f, []).append(x)
    rows = []
    for f in sorted(funcs):
        end = min(C.func_end(f), f + 0x1000)
        r = fn_refs(f)
        srcs = sorted({v for x, v in s["srcs"].items() if f <= x < end})
        reach = sorted(C.SHUTTER[x] for x in C.reach(f, 3) if x in C.SHUTTER)
        rows.append({"func": hex(f), "sitios": len(funcs[f]), "fuentes": srcs, "refs": r, "obturador": reach})
    return {"etiqueta": label, "cadenas": len(strs), "sin_sitio": sum(1 for a in strs if not sites[a]), "sitios": sum(len(v) for v in sites.values()),
            "tokens": {k: C.tokens(p, label) for k, p in V.FIRMWARE.items()}, "funciones": rows,
            "fuentes": sorted({x for r in rows for x in r["fuentes"]}), "obturador": sorted({x for r in rows for x in r["obturador"]}),
            "ejemplo": next(iter(strs.values()))[1][:80] if strs else None}


if __name__ == "__main__":
    out = {l: evaluate(l) for l in sys.argv[1:]}
    json.dump(out, open("analysis/camera_closure/labels_test.json", "w"), indent=1, ensure_ascii=False)
    for l, v in out.items(): print(l, v["cadenas"], v["sitios"], len(v["funciones"]), v["tokens"], v["fuentes"], v["obturador"], v["funciones"][:1])
