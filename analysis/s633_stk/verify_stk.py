#!/usr/bin/env python3
"""S633: cadenas `[TRK]: [STK…]` y sus funciones (A6000 fw3.21), etiquetas `[STK_*]` del censo S178.

shortcut: la función contenedora es el primer `push {…lr}` hacia atrás (≤ 0x2000 B); llamadas indirectas no seguidas.
"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "analysis"), str(ROOT / "analysis/camera_closure"), str(ROOT / "analysis/s106_imaging_cap")]
import closure as C, closure2 as K, verify_s6xx as V

B, BASE = K.B, K.BASE
SIM = ["[STK_AUTO_SAL]", "[STK_COLOR_SIM]", "[STK_C_SIM]", "[STK_TOUCH_SIM]", "[STK_T_SIM]"]


def labels_in(refs, lo, hi):
    out = {}
    for t, ss in refs.items():
        if any(lo <= s < hi for s in ss):
            m = re.match(rb"\[([A-Z0-9_]+)\]", B[t - BASE:t - BASE + 40])
            if m: out[m.group(1).decode()] = out.get(m.group(1).decode(), 0) + 1
    return out


def build():
    refs = K.S.scan(BASE, BASE + K.N)
    strs = {BASE + m.start(): m.group().decode("latin1") for m in re.finditer(rb"\[TRK\]: \[STK[A-Z_]*\][^\x00]*", B)}
    funcs = {}
    for a in strs:
        for s in refs.get(a, []):
            funcs.setdefault(C.func_start(s), set()).add(a)
    cb = K.bl_callers()
    rows = []
    for f in sorted(funcs):
        end = min(C.func_end(f), f + 0x1800)
        r = K.refs(f)
        callers = [x for x in r["bl"]]
        rows.append({"func": hex(f), "cadenas": len(funcs[f]),
                     "etiquetas_cargadas": labels_in(refs, f, end),
                     "llamadores_bl": [{"sitio": c, "etiquetas_cercanas": labels_in(refs, int(c, 16) - 0x200, int(c, 16) + 0x200)} for c in callers[:4]],
                     "punteros": {"literal": r["literal"], "pic": r["pic"]}})
    sim = []
    for label in SIM:
        ss = [(a, t) for a, t in strs.items() if label in t]
        sim.append({"etiqueta": label, "cadenas": [{"vaddr": hex(a), "texto": t} for a, t in ss],
                    "sitios": [hex(s) for a, _ in ss for s in refs.get(a, [])],
                    "funcion": sorted({hex(C.func_start(s)) for a, _ in ss for s in refs.get(a, [])}),
                    "a7s": C.tokens(V.FIRMWARE["a7s_fw320"], label), "a6300": C.tokens(V.FIRMWARE["a6300_fw201"], label)})
    stk_total = sum(1 for t in strs.values() if t.startswith("[TRK]: [STK] "))
    return {"cadenas_trk_stk": len(strs), "cadenas_stk": stk_total, "sin_sitio": [hex(a) for a in strs if not refs.get(a)],
            "sitios": sum(len(refs.get(a, [])) for a in strs), "funciones": rows, "stk_sim": sim,
            "tokens_stk": {k: C.tokens(p, "[STK]") for k, p in V.FIRMWARE.items()},
            "alcance_obturador": {r["func"]: sorted(C.SHUTTER[x] for x in C.reach(int(r["func"], 16), 3) if x in C.SHUTTER) for r in rows}}


if __name__ == "__main__":
    d = build()
    (ROOT / "analysis/s633_stk/stk.json").write_text(json.dumps(d, indent=1, ensure_ascii=False))
    print({k: v for k, v in d.items() if k not in ("funciones", "stk_sim")})
    for r in d["funciones"]: print(r["func"], r["cadenas"], r["etiquetas_cargadas"], [(x["sitio"], x["etiquetas_cercanas"]) for x in r["llamadores_bl"]], r["punteros"])
    for s in d["stk_sim"]: print(s["etiqueta"], len(s["cadenas"]), s["funcion"], s["a7s"], s["a6300"])
