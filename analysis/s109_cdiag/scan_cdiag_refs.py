#!/usr/bin/env python3
"""S109 — referencias a las 270 cadenas `[CDIAG]` del firmware A6000 fw3.21.

Método (esquema PIC verificado en este repo, cf. analysis/s106_imaging_cap/scan_pic_refs.py):

    ldr  rX, [pc, #inm]      ; el pool guarda un desplazamiento W
    ...
    add  rX, pc              ; destino = W + (dirección_del_add + 4)

Se barre toda la imagen (0x43541000 + tamaño), se empareja cada `ldr` con el `add`
del mismo registro (ventana MAX_LDR_GAP) y se exige que el destino caiga
exactamente en el inicio de una cadena `[CDIAG]` (conjunto de direcciones
verificadas leyendo los bytes).  Eso hace vanishingmente improbable un falso
positivo.

Salida: analysis/s109_cdiag/cdiag_refs.json
"""
import bisect
import json
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
STR_LO, STR_HI = 0x43C24000, 0x43D10000     # zona amplia de cadenas (rodata)
MAX_LDR_GAP = 4096

B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def cdiag_strings():
    """[(vaddr, texto)] de las cadenas que empiezan por [CDIAG]."""
    out = []
    start = 0
    while True:
        i = B.find(b"[CDIAG]", start)
        if i < 0:
            break
        v = BASE + i
        e = i
        while e < N and 32 <= B[e] < 127:
            e += 1
        out.append((v, B[i:e].decode("latin1")))
        start = i + 1
    return out


def string_starts(lo, hi):
    """Direcciones de inicio de cadenas imprimibles en [lo, hi)."""
    o0, o1 = lo - BASE, hi - BASE
    out = set()
    prev = False
    for i in range(o0, o1):
        cur = 32 <= B[i] < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


def ldr_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 8:
            continue
        h = U16(B, o)[0]
        if (h & 0xF800) == 0x4800:            # ldr rT, [pc, #imm5*4]
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:          # ldr.w rT, [pc, #imm12]
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        else:
            continue
        o2 = lit - BASE
        if 0 <= o2 <= N - 4:
            out.append((a, reg, U32(B, o2)[0]))
    return out


def add_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 4:
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400:
            rm = (h >> 3) & 0xF
            rd = (((h >> 7) & 1) << 3) | (h & 7)
            if rm == 15:
                out.append((a, rd))
    return out


def scan(lo, hi):
    starts = string_starts(STR_LO, STR_HI)
    ldrs = ldr_sites(lo, hi)
    adds = add_sites(lo, hi)
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = {}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        while i >= 0:
            la, w = v[i]
            if a - la > MAX_LDR_GAP:
                break
            tgt = (w + (a + 4)) & 0xFFFFFFFF
            if tgt in starts:
                out.setdefault(tgt, []).append(a)
                break
            i -= 1
    return out


def main():
    lo = BASE
    hi = BASE + N
    res = scan(lo, hi)
    dest = "analysis/s109_cdiag/cdiag_refs.json"
    with open(dest, "w") as fh:
        json.dump({f"0x{k:x}": sorted(set(v)) for k, v in sorted(res.items())},
                  fh, indent=0)
    print(f"destinos totales en la zona de cadenas: {len(res)}")
    print("escrito", dest)


if __name__ == "__main__":
    sys.exit(main())
