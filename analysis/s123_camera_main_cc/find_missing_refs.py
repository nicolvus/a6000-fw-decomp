#!/usr/bin/env python3
"""S123 — ¿de dónde salen las 2 trazas `[CAMERA_MAIN_CC]` sin referencia PIC estricta?

Para un destino dado se listan TODOS los pares (ldr rX,[pc,#imm] ; add rX,pc) que lo
producen (regla "ancha": todos los `ldr` del registro en 4 KB), y se marca si el `ldr`
pertenece a la **misma función** que el `add` (regla estricta) o no.

Uso:  find_missing_refs.py DEST1 [DEST2 ...]
"""
import bisect
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
LO, HI = BASE, BASE + 0xB00000          # zona de código
MAX_GAP = 4096


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def main():
    targets = {int(a, 0) for a in sys.argv[1:]}
    with open(BIN, "rb") as fh:
        code = fh.read()
    N = len(code)

    ldrs = {}
    a = 0
    while a + 4 <= N:
        h = u16(code, a)
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = u16(code, a + 2)
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            if 0 <= lit <= N - 4:
                ldrs.setdefault(reg, []).append((BASE + a, u32(code, lit)))
            a += 4 if (h & 0xFF7F) == 0xF85F else 2
            continue
        a += 2

    adds = []
    a = 0
    while a + 2 <= N:
        h = u16(code, a)
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            rd = (((h >> 7) & 1) << 3) | (h & 7)
            adds.append((BASE + a, rd))
        a += 2

    keys = {r: [x[0] for x in v] for r, v in ldrs.items()}

    for tgt in sorted(targets):
        print(f"=== destino {tgt:#x} ===")
        found = False
        for aa, rd in adds:
            ks = keys.get(rd)
            if not ks:
                continue
            i = bisect.bisect_left(ks, aa) - 1
            while i >= 0 and aa - ks[i] <= MAX_GAP:
                la, w = ldrs[rd][i]
                if aa > la and (w + aa + 4) & 0xFFFFFFFF == tgt:
                    found = True
                    print(f"  ANCHA  add@{aa:#x} (r{rd}) <- ldr@{la:#x}  "
                          f"W={w:#x}  (distancia {aa - la})")
                i -= 1
        if not found:
            print("  sin par (ni ancha ni alt)")


if __name__ == "__main__":
    main()
