#!/usr/bin/env python3
"""S170 — localiza los sitios de referencia (regla PIC estricta) de las cadenas [ILLUMI].

Usa el mapa global canónico `analysis/s106_imaging_cap/pic_refs_strict_global.json`
(site -> [destinos]) y lo contrasta con un escaneo local propio (misma regla) para
no depender de la cobertura del mapa global.
"""
import json
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from

STRINGS = json.load(open("analysis/s170_illumi/illumi_strings_raw.json"))["A6000_fw321"]["cadenas"]
STR_ADDRS = {int(s["vaddr"], 16): s["texto"] for s in STRINGS}

PIC = json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json"))
# el mapa global es  destino -> [sitios]
PIC_INT = {int(k, 16): [int(x) for x in v] for k, v in PIC.items()}

# --- mapa local (misma regla estricta) sobre todo el rango de código ---
LO, HI = 0x43541000, 0x44017000


def pic_ldr_sites(lo, hi):
    out = []
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
            out.append((a, reg, U32(B, lit - BASE)[0], lit))
        a += 2
    return out


def pic_add_sites(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    return out


def local_strict(lo=LO, hi=HI):
    """regla estricta: cada `add rX,pc` se empareja con el `ldr` más cercano del
    mismo registro (ventana 4 KB)."""
    ldrs = pic_ldr_sites(lo, hi)
    adds = pic_add_sites(lo, hi)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    import bisect
    out = {}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        if i < 0:
            continue
        la, w, lit = v[i]
        if a - la > 4096:
            continue
        dest = (w + (a + 4)) & 0xFFFFFFFF
        out.setdefault(dest, []).append((a, la, lit, w, reg))
    return out


def main():
    local = local_strict()
    glob = PIC_INT   # destino -> [sitios]

    rows = []
    for sa, txt in sorted(STR_ADDRS.items()):
        ls = sorted(local.get(sa, []))
        gs = sorted(glob.get(sa, []))
        rows.append({
            "string_addr": hex(sa),
            "texto": txt,
            "n_sitios_local": len(ls),
            "n_sitios_global": len(gs),
            "sitios_local": [hex(x[0]) for x in ls],
            "sitios_global": [hex(x) for x in gs],
            "solo_global": [hex(x) for x in gs if x not in [y[0] for y in ls]],
            "solo_local": [hex(x[0]) for x in ls if x[0] not in gs],
        })
    tot_l = sum(r["n_sitios_local"] for r in rows)
    tot_g = sum(r["n_sitios_global"] for r in rows)
    dead = [r["string_addr"] for r in rows if r["n_sitios_local"] == 0]
    print(f"cadenas={len(rows)} sitios_local={tot_l} sitios_global={tot_g} muertas(local)={dead}")
    for r in rows:
        print(r["string_addr"], r["n_sitios_local"], r["n_sitios_global"], r["texto"][:60])
    json.dump(rows, open("analysis/s170_illumi/illumi_pic_sites.json", "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
