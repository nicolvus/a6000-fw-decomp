#!/usr/bin/env python3
"""REV-01: medidas estáticas sobre av-cam.bin (A6000 fw3.21) para cerrar líneas NO_VERIFICADO.
shortcut: llamadores solo `bl` por patrón de halfwords y punteros absolutos de 32 B; sin vtables indirectas, cuándo mejorar: si REV-01 reabre."""
import json, struct, sys, re
sys.path.insert(0, "analysis/camera_closure"); sys.path.insert(0, "analysis/s106_imaging_cap")
import closure2, closure
B, BASE, N = closure.B, closure.BASE, closure.N
L = ROOT_LABELS = json.load(open("analysis/camera_closure/labels.json"))

def ptrs(a):
    """Offsets de palabras de 32 B alineadas a 2 que valen a o a|1 (puntero absoluto, vtable/tabla)."""
    out = []
    for v in (a, a | 1):
        p = struct.pack("<I", v); i = B.find(p)
        while i >= 0:
            out.append(BASE + i); i = B.find(p, i + 1)
    return sorted(set(out))

def callers(a): return sorted(closure2.bl_callers().get(a, []))

def strs(tok):
    return [BASE + m.start() for m in re.finditer(re.escape(tok.encode()), B)]

R = {}
d = L["[AUDPINEDTR]"]; f = d["funciones"]
R["AUDPINEDTR"] = {"cadenas": d["cadenas"], "sitios": d["sitios"], "funciones": len(f),
                   "fuentes": sorted({s for x in f for s in x["fuentes"]}), "obturador": [x["func"] for x in f if x["obturador"]]}
for tok in ("DCFStillWriter", "PreRegisterDcfContentSync", "PreRegisterImage"):
    R["str:" + tok] = [hex(x) for x in strs(tok)[:5]]
for a in (0x4381cc7c, 0x4360b6f0, 0x436150ce, 0x4391ca90, 0x43b7c470, 0x43af58f8, 0x43b71fa8, 0x43789cc0, 0x436e2f64):
    R[hex(a)] = {"bl": [hex(x) for x in callers(a)[:8]], "n_bl": len(callers(a)), "ptr": [hex(x) for x in ptrs(a)[:8]]}
# tbh de REL_EVT en 0x4379d852: 0x27 entradas de medias palabras (destino = base + 2*h)
base = 0x4379d852
tg = [base + 2 * struct.unpack_from("<H", B, base - BASE + 2 * i)[0] for i in range(0x28)]
R["REL_EVT_tbh_dest_unicos"] = len(set(tg)); R["REL_EVT_tbh"] = [hex(x) for x in tg]
R["mount_2f64"] = {"func_end": hex(closure.func_end(0x436e2f64))}
json.dump(R, open("analysis/rev01/rev01.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(R, ensure_ascii=False)[:3500])
