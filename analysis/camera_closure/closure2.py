#!/usr/bin/env python3
"""CAM-01: resuelve con bytes las preguntas abiertas de S110/S119/S122/S123/S126/S127/S129/S138/S164.

Referencias a una función F (Thumb): `bl/b.w` directo, literal de 32 bits (F|1 ó F) en cualquier alineación de 4,
`ldr`+`add pc` (regla estricta) con destino F|1/F, y `adr`.
shortcut: no sigue despacho por registro calculado (tablas con índice); alcance = llamadas directas y punteros.
"""
import bisect, json, re, struct, sys
sys.path.insert(0, "analysis/s106_imaging_cap"); sys.path.insert(0, "analysis/camera_closure")
import scan_pic_refs_strict as S
import closure as C
B, BASE, N = S.B, S.BASE, S.N
u32 = lambda o: struct.unpack_from("<I", B, o)[0]

def literal_ptrs(addr):
    v = {addr, addr | 1}
    return [BASE + o for o in range(0, N - 3, 4) if u32(o) in v]

def pic_targets():
    ldrs = S.ldr_sites(BASE, BASE + N); adds = S.add_sites(BASE, BASE + N)
    by = {}
    for a, r, w in ldrs: by.setdefault(r, []).append((a, w))
    for v in by.values(): v.sort()
    keys = {r: [x[0] for x in v] for r, v in by.items()}
    out = {}
    for a, r in adds:
        if r not in by: continue
        i = bisect.bisect_left(keys[r], a) - 1
        if i < 0 or a - by[r][i][0] > 4096: continue
        out.setdefault((by[r][i][1] + a + 4) & 0xFFFFFFFF, []).append(a)
    return out

_cache = {}
_ldr = {}
def by_ldr(add_site):
    """`ldr` emparejado con el `add rX,pc` (mismo registro, el más cercano por detrás)."""
    if not _ldr:
        for a, r, w in S.ldr_sites(BASE, BASE + N): _ldr.setdefault(r, []).append(a)
    h = struct.unpack_from("<H", B, add_site - BASE)[0]
    r = (((h >> 7) & 1) << 3) | (h & 7)
    ks = sorted(_ldr[r]); i = bisect.bisect_left(ks, add_site) - 1
    return ks[i]
def bl_callers():
    """Todos los `bl`/`blx`/`b.w` Thumb-2 por patrón de halfwords (sin desensamblado lineal, que se desincroniza con datos)."""
    if "bl" not in _cache:
        d = {}
        for o in range(0, N - 4, 2):
            h1, h2 = struct.unpack_from("<HH", B, o)
            if (h1 & 0xF800) != 0xF000 or (h2 & 0xC000) != 0xC000 and (h2 & 0xD000) != 0x9000: continue
            if (h2 & 0xD000) not in (0xD000, 0xC000, 0x9000): continue
            s = (h1 >> 10) & 1; j1 = (h2 >> 13) & 1; j2 = (h2 >> 11) & 1
            i1 = (~(j1 ^ s)) & 1; i2 = (~(j2 ^ s)) & 1
            if (h2 & 0xD000) == 0x9000:      # b.w (T4)
                imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
            else:                             # bl / blx
                imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
            if imm & (1 << 24): imm -= 1 << 25
            a = BASE + o
            tgt = ((a + 4) & ~3 if (h2 & 0xD000) == 0xC000 else a + 4) + imm
            d.setdefault(tgt & 0xFFFFFFFF, []).append(a)
        _cache["bl"] = d
    return _cache["bl"]

def refs(addr):
    pic = _cache.setdefault("pic", pic_targets())
    return {"bl": [hex(x) for x in bl_callers().get(addr, [])],
            "literal": [hex(x) for x in literal_ptrs(addr)],
            "movw_movt": movw_movt(addr), "pic": [hex(x) for x in pic.get(addr | 1, []) if C.func_start(x) == C.func_start(by_ldr(x))]}



def movw_movt(addr):
    """Pares `movw rX,#lo` + `movt rX,#hi` (T3) que forman addr|1 ó addr (≤ 12 B de separación)."""
    def dec(o):
        h1, h2 = struct.unpack_from("<HH", B, o)
        imm = ((h1 & 0xF) << 12) | (((h1 >> 10) & 1) << 11) | (((h2 >> 12) & 7) << 8) | (h2 & 0xFF)
        return (h1 & 0xFBF0), (h2 >> 8) & 0xF, imm
    lo = {}; out = []
    for o in range(0, N - 4, 2):
        h1 = struct.unpack_from("<H", B, o)[0]
        if (h1 & 0xFBF0) not in (0xF240, 0xF2C0): continue
        h2 = struct.unpack_from("<H", B, o + 2)[0]
        if h2 & 0x8000: continue
        k, rd, imm = dec(o)
        if k == 0xF240: lo[rd] = (o, imm)
        elif rd in lo and o - lo[rd][0] <= 12 and ((imm << 16) | lo[rd][1]) in (addr, addr | 1):
            out.append(hex(BASE + lo[rd][0]))
    return out


if __name__ == "__main__":
    q = [int(x, 16) for x in sys.argv[1:]]
    for a in q: print(hex(a), json.dumps(refs(a)))
