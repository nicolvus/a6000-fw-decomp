#!/usr/bin/env python3
"""S179 — mapa función -> traza (misma heurística que S177)."""
import bisect, json, os, struct

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
B = open(os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"), "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
LO, HI = 0x43541000, 0x44017000

def func_starts(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2; continue
        h = U16(B, o)[0]
        if (h & 0xFE00) == 0xB400 and (h & 0x0100) and (h & 0x00FF):
            out.append(a)
        elif h == 0xE92D:
            h2 = U16(B, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out

def all_bl_targets():
    out = set()
    a = LO
    while a < HI:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2; continue
        h = U16(B, o)[0]
        if (h & 0xF800) == 0xF000:
            h2 = U16(B, o + 2)[0]
            if (h2 & 0xD000) == 0xD000:
                s = (h >> 10) & 1
                imm10 = h & 0x3FF
                j1 = (h2 >> 13) & 1
                j2 = (h2 >> 11) & 1
                imm11 = h2 & 0x7FF
                i1 = 1 - (j1 ^ s); i2 = 1 - (j2 ^ s)
                imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
                if s: imm -= (1 << 25)
                out.add(a + 4 + imm)
            a += 4; continue
        a += 2
    return out

def main():
    rows = json.load(open(os.path.join(ROOT, "analysis/s179_cam_scalar/pic_sites.json")))
    sites = []
    for k, r in rows.items():
        for s in r["sites"]:
            sites.append((int(s, 16), int(k, 16), r["text"]))
    sites.sort()

    starts = set(func_starts(LO, HI)) | all_bl_targets()
    starts = sorted(x for x in starts if BASE <= x < BASE + N)
    cl = []
    for x in starts:
        if cl and x - cl[-1][-1] <= 8: cl[-1].append(x)
        else: cl.append([x])
    starts = sorted(c[0] for c in cl)

    def enclosing(addr):
        i = bisect.bisect_right(starts, addr) - 1
        return starts[i] if i >= 0 else None

    byfunc = {}
    for s, sa, txt in sites:
        byfunc.setdefault(enclosing(s), []).append({"sitio": "0x%x" % s, "string_addr": "0x%x" % sa, "texto": txt})
    res = []
    print(f"sitios={len(sites)} funciones={len(byfunc)}")
    for f in sorted(byfunc, key=lambda x: (x is None, x or 0)):
        rr = sorted(byfunc[f], key=lambda x: int(x["sitio"], 16))
        print(f"0x{f:x}" if f else "None", f" n={len(rr)}")
        for r in rr: print("   ", r["sitio"], r["string_addr"], repr(r["texto"])[:80])
        res.append({"func": "0x%x" % f if f else None, "n_sitios": len(rr), "sitios": rr})
    json.dump({"funciones": res}, open(os.path.join(ROOT, "analysis/s179_cam_scalar/func_map.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
