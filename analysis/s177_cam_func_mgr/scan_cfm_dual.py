#!/usr/bin/env python3
"""S177 — comprueba el patrón de "doble instrumentación" de la fw3.21 en los
sitios de `[CAM_FUNC_MGR]`.

Para cada sitio (add rX,pc con X!=0 que apunta a una cadena [CAM_FUNC_MGR]):
  - la llamada siguiente (`bl`) es la traza NUEVA (wrapper por fichero),
  - a continuación aparece un `add r0,pc` que apunta a la MISMA cadena + 16
    (el literal sin prefijo) seguido de `bl 0x43902718` (traza VIEJA).
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
OLD_LOG = 0x43902718


def cstr(a):
    o = a - BASE
    if o < 0 or o >= N:
        return None
    e = B.find(b"\x00", o)
    if e < 0 or e - o > 200:
        return None
    try:
        s = B[o:e].decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if all(32 <= ord(c) < 127 for c in s) else None


def pic_all(lo, hi):
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


def bls(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xF800) == 0xF000:
            h2 = U16(B, o + 2)[0]
            if (h2 & 0xD000) == 0xD000:
                s = (h >> 10) & 1
                imm10 = h & 0x3FF
                j1 = (h2 >> 13) & 1
                j2 = (h2 >> 11) & 1
                imm11 = h2 & 0x7FF
                i1 = 1 - (j1 ^ s)
                i2 = 1 - (j2 ^ s)
                imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
                if s:
                    imm -= (1 << 25)
                out.append((a, a + 4 + imm))
            a += 4
            continue
        a += 2
    return out


def main():
    rows = json.load(open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_pic_sites.json")))
    sites = []
    for r in rows["cadenas"]:
        for s in r["sitios"]:
            sites.append((int(s, 16), int(r["vaddr"], 16), r["texto"]))
    sites.sort()
    LO, HI = 0x43780000, 0x4380b000
    pics = pic_all(LO, HI)
    pic_by = {a: (d, r) for a, d, r in pics}
    bl_list = bls(LO, HI)
    bl_by = dict(bl_list)
    bl_addrs = sorted(bl_by)

    out = []
    n_dual = 0
    wrappers = {}
    for sit, sva, txt in sites:
        i = bisect.bisect_left(bl_addrs, sit)
        new_bl = None
        if i < len(bl_addrs) and bl_addrs[i] < sit + 0x40:
            new_bl = (hex(bl_addrs[i]), hex(bl_by[bl_addrs[i]]))
            wrappers.setdefault(bl_by[bl_addrs[i]], 0)
            wrappers[bl_by[bl_addrs[i]]] += 1
        # traza antigua: primer `add r0,pc` + `bl 0x43902718` posterior
        old = None
        for a, d, r in pics:
            if a <= sit or a > sit + 0x100:
                continue
            if r != 0:
                continue
            # el bl siguiente
            j = bisect.bisect_left(bl_addrs, a)
            if j < len(bl_addrs) and bl_addrs[j] < a + 0x20 and \
                    bl_by[bl_addrs[j]] == OLD_LOG:
                old = (hex(a), hex(d), cstr(d))
                break
        dual = old is not None and int(old[1], 16) == sva + 16
        n_dual += bool(dual)
        out.append({"sitio": hex(sit), "string": hex(sva), "texto": txt,
                    "bl_nuevo": new_bl, "log_viejo": old, "dual": dual})
    for o in out:
        print(f"{o['sitio']} nuevo={o['bl_nuevo']} viejo={o['log_viejo']} "
              f"dual={o['dual']}")
    print(f"\nsitios con doble instrumentación verificada: {n_dual}/{len(out)}")
    print("wrappers de traza nueva (destino -> nº de sitios):")
    for k, v in sorted(wrappers.items()):
        print(f"   {k:#x}  {v}")
    json.dump({"sitios": out, "n_dual": n_dual,
               "wrappers": {hex(k): v for k, v in wrappers.items()}},
              open(os.path.join(ROOT,
                                "analysis/s177_cam_func_mgr/cfm_dual_log.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
