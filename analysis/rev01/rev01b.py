"""REV-01 (2): tbh REL_EVT corregida, cadenas de las funciones llamadoras y vtable de CapIdTblMgrIf."""
import json, struct, sys
sys.path.insert(0, "analysis/camera_closure"); sys.path.insert(0, "analysis/s106_imaging_cap")
import closure, closure2
import scan_pic_refs_strict as S
B, BASE = S.B, S.BASE
def s_at(a):
    i = a - BASE; j = B.find(b"\0", i); return B[i:j].decode("latin1")[:60]
def strs_in(f):
    e = closure.func_end(f); out = S.scan(f, e)
    return [(hex(t), s_at(t)) for t in sorted(out)][:6]
R = {}
base = 0x4379d856                       # tbh en 0x4379d852 (4 B) -> tabla en pc+4
tg = [base + 2 * struct.unpack_from("<H", B, base - BASE + 2 * i)[0] for i in range(0x28)]
R["tbh"] = [hex(x) for x in tg]; R["tbh_unicos"] = len(set(tg))
R["vt_CapIdTblMgrIf_words"] = [hex(struct.unpack_from("<I", B, 0x44025418 - BASE + 4 * k)[0]) for k in range(-3, 6)] if 0x44025418 - BASE + 24 < len(B) else "fuera"
for c in (0x4360b8fe, 0x437d1df4, 0x43af5972, 0x43786858, 0x439f3b90, 0x436e849a, 0x4391d12e):
    f = closure.func_start(c); R[hex(c)] = {"func": hex(f) if f else None, "cadenas": strs_in(f) if f else []}
json.dump(R, open("analysis/rev01/rev01b.json", "w"), indent=1)
print(json.dumps(R, ensure_ascii=False)[:3800])
