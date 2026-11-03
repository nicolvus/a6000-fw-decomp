#!/usr/bin/env python3
"""REV-01: homólogos A7S de funciones A6000 (por cadenas comunes referenciadas) y comparación de código normalizado.
shortcut: normaliza bl/b.w/ldr-pc/add-pc/adr; no sigue llamadas; igualdad de secuencia != equivalencia física."""
import sys, re, json, collections
sys.path.insert(0, "analysis/camera_closure"); sys.path.insert(0, "analysis/s106_imaging_cap")
import scan_pic_refs_strict as S
import closure
from capstone import *
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
A6 = (S.B, S.N)
A7 = open("analysis/rea-independent/input/av-cam-a7s.bin", "rb").read()
BASE = S.BASE

def use(model):
    S.B, S.N = (A6 if model == "a6" else (A7, len(A7)))
    closure.B, closure.N = S.B, S.N

def cstr(model, a):
    B = A6[0] if model == "a6" else A7; i = a - BASE; return re.sub(rb"^\[CAMERA_SA\]: ", b"", B[i:B.find(b"\0", i)])

_cache = {}
def scan_all(model):
    if model not in _cache:
        use(model); _cache[model] = S.scan(BASE, BASE + S.N - 8)
    return _cache[model]

def fstart(model, a):
    use(model); return closure.func_start(a)

def norm(model, f, e):
    B = A6[0] if model == "a6" else A7
    out = []
    for i in md.disasm(B[f - BASE:e - BASE], f):
        m, o = i.mnemonic, i.op_str
        if m in ("bl", "blx") or m.startswith("b") and "#0x" in o: o = "T"
        elif "[pc" in o or o.endswith(", pc") or m == "adr": o = re.sub(r"#0x[0-9a-f]+", "#K", o)
        if "sp" in o: o = re.sub(r"#0x[0-9a-f]+", "#K", o)
        out.append(m + " " + o)
    return out

def homolog(f6):
    """(f7, votos, cadenas A6000, igualdad) de la función A6000 f6."""
    use("a6"); e6 = closure.func_end(f6)
    ss = {t for t, aa in scan_all("a6").items() if any(f6 <= a < e6 for a in aa)}
    texts = {cstr("a6", t) for t in ss}
    sc7 = scan_all("a7s") if False else scan_all("a7")
    votes = collections.Counter()
    for t7, aa in sc7.items():
        if cstr("a7", t7) in texts:
            for a in aa: votes[fstart("a7", a)] += 1
    if not votes: return None
    f7, v = votes.most_common(1)[0]
    use("a7"); e7 = closure.func_end(f7)
    n6, n7 = norm("a6", f6, e6), norm("a7", f7, e7)
    same = sum(a == b for a, b in zip(n6, n7))
    return {"f6": hex(f6), "f7": hex(f7), "cadenas6": len(texts), "votos": v, "ins6": len(n6), "ins7": len(n7), "iguales_posicion": same,
            "identica": n6 == n7}

if __name__ == "__main__":
    fs = [int(x, 16) for x in sys.argv[1:]]
    res = [homolog(f) for f in fs]
    print(json.dumps(res, indent=0)[:3000])
