#!/usr/bin/env python3
"""Escáner PIC **estricto** (regla canónica del repo).

Esquema del firmware:

    ldr  rX, [pc, #inm]      ; W = desplazamiento del pool de literales
    ...
    add  rX, pc              ; destino = W + (dirección_del_add + 4)

Regla canónica: cada `add rX,pc` se empareja con el **`ldr rX,[pc,#imm]` más cercano
por detrás** del mismo registro (ventana de 4 KB, el máximo del desplazamiento del
literal pool). Solo se aceptan los destinos que caen en el **inicio** de una cadena.

Por qué esta regla y no otras (medido contra dos casos verificados a mano):
  * `[SFRA]`: real 118 sitios → estricta 118 ✓, kill analysis 166, ancha 186.
  * `[AIP]`:  real  37 sitios → estricta  37 ✓, kill analysis  60.
  La regla "ancha" (probar todos los `ldr` del registro) **inventa** referencias
  porque el registro se reutiliza entre el `ldr` y el `add`.

Uso:  scan_pic_refs_strict.py [LO HI] [RUTA_SALIDA]
"""
import bisect
import json
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
STR_LO, STR_HI = 0x0, 0xFFFFFFFF     # rango de cadenas válidas (toda la imagen)
MAX_LDR_GAP = 4096

B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def string_starts(lo, hi):
    """Inicio de cadena: byte imprimible cuyo byte anterior no lo es."""
    o0, o1 = max(0, lo - BASE), min(N, hi - BASE)
    out = set()
    prev_print = False
    for i in range(o0, o1):
        c = B[i]
        cur = 32 <= c < 127
        if cur and not prev_print:
            out.add(BASE + i)
        prev_print = cur
    return out


def ldr_sites(lo, hi):
    """[(addr, reg, valor_del_pool)] de los `ldr rX,[pc,#imm]`."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:              # ldr rT, [pc, #imm5*4]
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:            # ldr.w rT, [pc, #imm12]
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= N - 4:
                out.append((a, reg, U32(B, o2)[0]))
        a += 2
    return out


def add_sites(lo, hi):
    """[(addr, reg)] de los `add rX, pc` de 16 bits."""
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
        i = bisect.bisect_left(ks, a) - 1      # ldr más cercano por detrás
        if i < 0:
            continue
        la, w = v[i]
        if a - la > MAX_LDR_GAP:
            continue
        tgt = (w + (a + 4)) & 0xFFFFFFFF
        if tgt in starts:
            out.setdefault(tgt, []).append(a)
    return out


def main():
    lo = int(sys.argv[1], 0) if len(sys.argv) > 1 else BASE
    hi = int(sys.argv[2], 0) if len(sys.argv) > 2 else BASE + N
    dest = sys.argv[3] if len(sys.argv) > 3 else "analysis/s106_imaging_cap/pic_refs_strict.json"
    res = scan(lo, hi)
    with open(dest, "w") as fh:
        json.dump({f"0x{k:x}": sorted(set(v)) for k, v in sorted(res.items())},
                  fh, indent=0)
    print(f"destinos: {len(res)}  ->  {dest}")


if __name__ == "__main__":
    main()
