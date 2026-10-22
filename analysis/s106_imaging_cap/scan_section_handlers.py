#!/usr/bin/env python3
"""Mapa de los 17 manejadores de sección de IMAGING_CAP (tabla en 0x43ff8fb4).

Cada entrada de la tabla es {id de sección u32, puntero a manejador u32}. El
punto de entrada del manejador se toma del bit 0 (Thumb). Para cada manejador
se calcula una extensión aproximada (hasta `pop {..,pc}` o el siguiente
`push {..,lr}`) y se listan las cadenas que ese código referencia mediante la
secuencia PIC `ldr rX,[pc,#imm]` + `add rX,pc` (destino = literal + PC del add).

Salida: analysis/s104_imaging_cap/section_handlers.json
"""
import json
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
TABLE = 0x43FF8FB4
N_ENTRIES = 17
STR_LO, STR_HI = 0x43C90000, 0x43CD0000
MAX_SPAN = 0x400

B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def u16(va):
    o = va - BASE
    return U16(B, o)[0] if 0 <= o <= N - 2 else None


def u32(va):
    o = va - BASE
    return U32(B, o)[0] if 0 <= o <= N - 4 else None


def cstr(va, maxlen=120):
    o = va - BASE
    if o < 0 or o >= N:
        return None
    e = o
    while e < o + maxlen and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1") if e > o else None


def pic_refs(lo, hi):
    hits = []
    a = lo
    while a < hi:
        h = u16(a)
        rt = lit = None
        if (h & 0xF800) == 0x4800:          # ldr rT, [pc, #imm5*4]
            rt = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:        # ldr.w rT, [pc, #imm12]
            h2 = u16(a + 2)
            if h2 is not None:
                rt = (h2 >> 12) & 0xF
                lit = ((a + 4) & ~3) + (h2 & 0xFFF) * 4
        if rt is not None:
            w = u32(lit)
            if w is not None:
                for k in (2, 4, 6, 8, 10, 12, 14, 16):
                    hh = u16(a + k)
                    if hh is None:
                        break
                    if (hh & 0xFF00) == 0x4400:
                        rm = (hh >> 3) & 0xF
                        rd = (((hh >> 7) & 1) << 3) | (hh & 7)
                        if rm == 15 and rd == rt:
                            tgt = (w + (a + k + 4)) & 0xFFFFFFFF
                            if STR_LO <= tgt < STR_HI:
                                hits.append((tgt, a + k))
                            break
        a += 2
    return hits


def extent(start, limit):
    """Extensión aproximada: hasta `pop {..,pc}` o el siguiente `push {..,lr}`."""
    a = start
    first = True
    while a < limit:
        h = u16(a)
        if h is None:
            break
        if (h & 0xF800) == 0xBD00:      # pop {..,pc}
            return a + 2
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):   # push {..,lr}
            if first:                  # el propio prólogo de entrada
                first = False
                a += 2
                continue
            return a
        first = False
        a += 4 if (h & 0xE000) == 0xE000 and (h & 0x1800) != 0 else 2
    return limit


def main():
    ents = []
    for i in range(N_ENTRIES):
        a = TABLE + i * 8
        ents.append((u32(a), u32(a + 4) & ~1))

    rows = []
    for sid, fn in ents:
        nxt = min([f for _, f in ents if f > fn], default=fn + MAX_SPAN)
        end = extent(fn, min(nxt, fn + MAX_SPAN))
        refs = []
        seen = set()
        for tgt, site in pic_refs(fn, end):
            if tgt in seen:
                continue
            seen.add(tgt)
            txt = cstr(tgt)
            if txt:
                refs.append({"vaddr": f"0x{tgt:x}", "site": f"0x{site:x}", "text": txt[:120]})
        rows.append({
            "section_id": sid,
            "handler": f"0x{fn:x}",
            "end": f"0x{end:x}",
            "size": end - fn,
            "strings": refs,
        })
        print(f"id=0x{sid:02x} handler=0x{fn:x} end=0x{end:x} size={end-fn:4d} refs={len(refs)}")

    out = "analysis/s104_imaging_cap/section_handlers.json"
    with open(out, "w") as fh:
        json.dump(rows, fh, indent=1, ensure_ascii=False)
    print("escrito", out)


if __name__ == "__main__":
    sys.exit(main())
