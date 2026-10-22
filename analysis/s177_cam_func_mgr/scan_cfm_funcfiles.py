#!/usr/bin/env python3
"""S177 — para cada función emisora de [CAM_FUNC_MGR], ¿qué fichero fuente
de la zona `Camera::Function` referencia?

Busca, dentro del cuerpo de la función, todos los destinos PIC que apuntan a
cadenas que parecen nombres de fichero (`*.cpp`) o nombres de clase RTTI.
"""
import bisect
import json
import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
B = open(os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"), "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from

FM = json.load(open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_func_map.json")))
SITES = json.load(open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_pic_sites.json")))


def cstr(a):
    o = a - BASE
    if o < 0 or o >= N:
        return None
    e = B.find(b"\x00", o)
    if e < 0 or e - o > 160:
        return None
    try:
        s = B[o:e].decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if all(32 <= ord(c) < 127 for c in s) else None


def pic_all(lo, hi):
    """[(addr_add, dest, reg)] de los `add rX,pc` en [lo,hi)."""
    ldrs = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None and 0 <= lit - BASE <= N - 4:
            ldrs.append((a, reg, U32(B, lit - BASE)[0], lit))
        a += 2
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            reg = (((h >> 7) & 1) << 3) | (h & 7)
            v = by_reg.get(reg)
            if v:
                ks = keys[reg]
                i = bisect.bisect_left(ks, a) - 1
                if i >= 0:
                    la, w, lit = v[i]
                    if a - la <= 4096:
                        out.append((a, (w + a + 4) & 0xFFFFFFFF, reg))
        a += 2
    return out


def func_starts(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = U16(B, o)[0]
        if (h & 0xFE00) == 0xB400 and (h & 0x0100) and (h & 0x00FF):
            out.append(a)
        elif h == 0xE92D:
            h2 = U16(B, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


funcs = [(int(f["func"], 16), f) for f in FM["funciones"]]
funcs.sort()
starts = sorted(func_starts(0x43541000, 0x44017000))


def enclosing(addr):
    i = bisect.bisect_right(starts, addr) - 1
    return starts[i] if i >= 0 else None


res = []
for fstart, f in funcs:
    i = bisect.bisect_right(starts, fstart)
    nxt = starts[i] if i < len(starts) else fstart + 0x4000
    end = min(nxt, fstart + 0x4000)
    nombres = []
    for a, dest, reg in pic_all(fstart, end):
        s = cstr(dest)
        if s and (s.endswith(".cpp") or s.endswith(".h") or "/" in s
                  or s.startswith("N6Camera") or s.startswith("__")):
            if (hex(dest), s) not in nombres:
                nombres.append((hex(dest), s))
    res.append({"func": hex(fstart), "n_sitios": f["n_sitios"],
                "sitios": [s["sitio"] for s in f["sitios"]],
                "cadenas": sorted({s["texto"] for s in f["sitios"]}),
                "ficheros_y_rtti": nombres})
    print(f"{hex(fstart)}  n={f['n_sitios']}")
    for d, s in nombres:
        print(f"      {d}  {s!r}")

json.dump(res, open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_func_files.json"),
                    "w"), indent=1)
