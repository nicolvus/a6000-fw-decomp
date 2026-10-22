#!/usr/bin/env python3
"""S167 — verificación a mano de los pares PIC (regla estricta) de las trazas [SAD].

Para cada sitio `add rX,pc` que referencia una cadena [SAD] comprueba:
  (a) que el `ldr rX,[pc,#imm]` MÁS CERCANO por detrás es el que se empareja
      (misma ventana de 4 KB) -> regla estricta;
  (b) que el literal del pool es el que se lee;
  (c) que destino == literal + (add + 4);
  (d) que el registro NO se reescribe entre el `ldr` y el `add`
      (si se reescribiera, el `add` no usaría el valor del `ldr`).

Salida: analysis/s167_sad/sad_pic_verified.json
"""
import bisect
import json
import os
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GLOBAL = "analysis/s106_imaging_cap/pic_refs_strict_global.json"

B = open(os.path.join(ROOT, BIN), "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def cstr(a):
    o = a - BASE
    if o < 0 or o >= N:
        return None
    e = B.find(b"\x00", o)
    return B[o:e].decode("latin1")


def ldr_sites(lo, hi):
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


def add_sites(lo, hi):
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


def writes_to_reg(lo, hi, reg):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        note = None
        if (h & 0xF800) == 0x4800 and ((h >> 8) & 7) == reg:
            note = "ldr-lit"
        elif (h & 0xFF7F) == 0xF85F and ((U16(B, o + 2)[0] >> 12) & 0xF) == reg:
            note = "ldr.w-lit"
        elif (h & 0xF800) == 0x6800 and ((h >> 8) & 7) == reg:
            note = "ldr-mem"
        elif (h & 0xF800) == 0x9800 and ((h >> 8) & 7) == reg:
            note = "ldr-mem.w"
        elif 0x2000 <= (h & 0xF800) <= 0x3800 and ((h >> 8) & 7) == reg:
            note = "movs-imm"
        elif (h & 0xFC00) == 0x4000 and ((h & 7) | ((h >> 4) & 8)) == reg:
            note = "ops-reg"
        if note:
            out.append((a, note))
        a += 2
    return out


def main():
    gm = {int(k, 16): sorted(set(v)) for k, v in
          json.load(open(os.path.join(ROOT, GLOBAL))).items()}
    raw = json.load(open(os.path.join(HERE, "sad_raw.json")))
    cad = {c["vaddr"]: c["texto"] for c in raw["cadenas"]}

    lo, hi = 0x43541000, 0x43A00000
    ldrs = ldr_sites(lo, hi)
    adds = add_sites(lo, hi)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}

    verificados = []
    for va, texto in sorted(cad.items()):
        for site in gm.get(va, []):
            # (a) emparejamiento por la regla estricta
            reg = None
            for a, r in adds:
                if a == site:
                    reg = r
                    break
            assert reg is not None, hex(site)
            ks = keys[reg]
            i = bisect.bisect_left(ks, site) - 1
            la, w, lit = by_reg[reg][i]
            gap = site - la
            # (b) literal del pool
            w2 = U32(B, lit - BASE)[0]
            # (c) destino
            dest = (w + (site + 4)) & 0xFFFFFFFF
            # (d) reescrituras entre ldr y add
            entre = writes_to_reg(la + 2, site, reg)
            verificados.append({
                "cadena": hex(va), "texto": texto,
                "sitio": hex(site), "reg": f"r{reg}",
                "ldr_mas_cercano": hex(la), "gap_bytes": gap,
                "pool": hex(lit), "literal": hex(w),
                "literal_releido": hex(w2),
                "destino_calculado": hex(dest),
                "destino_coincide": dest == va,
                "reescritura_entre_ldr_y_add": [[hex(x), n] for x, n in entre],
                "ok": (dest == va and w == w2 and gap <= 4096 and not entre),
            })

    n = len(verificados)
    ok = sum(1 for v in verificados if v["ok"])
    out = {
        "milestone": "S167",
        "regla": "estricta (ldr rX,[pc,#imm] mas cercano por detras, ventana 4 KB)",
        "n_sitios_verificados": n,
        "n_ok": ok,
        "n_fallo": n - ok,
        "detalle": verificados,
    }
    dest = os.path.join(HERE, "sad_pic_verified.json")
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print(f"pares verificados: {n}  ok: {ok}  fallos: {n - ok}")
    for v in verificados:
        if not v["ok"]:
            print("  FALLO", v)
    print("escrito", dest)


if __name__ == "__main__":
    main()
