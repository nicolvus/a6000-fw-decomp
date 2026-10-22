#!/usr/bin/env python3
"""S138 — localizador de punteros a función materializados al estilo PIC.

En código PIC un puntero a función se materializa como
    ldr  rX, [pc, #imm]      ; el pool guarda un valor RELATIVO
    add  rX, pc              ; destino = pool + (addr_add + 4)
Por eso no basta con buscar los 4 bytes del valor absoluto: hay que calcular
todos los pares `ldr`/`add` de la imagen.

Salida: para cada objetivo, los sitios donde se materializa.
"""
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


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
            lit = ((a + 4) & ~3) + (h & 0xFF) * 4
        elif (h & 0xFF7F) == 0xF85F:
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


def main():
    targets = set(int(x, 16) for x in sys.argv[1:])
    ldrs = ldr_sites(BASE, BASE + N)
    adds = add_sites(BASE, BASE + N)
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    import bisect
    out = {t: [] for t in targets}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > 4096:
            continue
        val = (w + a + 4) & 0xFFFFFFFF
        if val in targets:
            out[val].append({"add": f"0x{a:x}", "ldr": f"0x{la:x}", "value": f"0x{val:x}"})
    for t in sorted(targets):
        print(f"0x{t:x}: {len(out[t])} materializaciones PIC  {out[t][:8]}")
    json.dump({f"0x{t:x}": out[t] for t in sorted(targets)},
              open(os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_pic_pointers.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
