#!/usr/bin/env python3
"""Referencias PIC del módulo `[TRK]` y función que las contiene (A6000).

Esquema verificado en este repo: la cadena se obtiene con

    ldr  rX, [pc, #imm]     ; del pool sale el desplazamiento W
    add  rX, pc             ; destino = W + (direccion_del_add + 4)

Se emparejan `ldr` y `add` por registro (ventana MAX_GAP) y se acepta el
emparejamiento solo si el destino es **exactamente** una de las 215 cadenas
`[TRK]` (216 ocurrencias). Se guarda tambien el sitio `ldr` (procedencia del
desplazamiento) para poder auditar cada pareja.

Atribucion a funcion, en dos niveles:
  * strict  : el sitio `add` cae dentro de [inicio, fin) de una funcion con
              prologo `push {..,lr}` / `push.w {..,lr}` y cierre en el primer
              `pop {..,pc}` / `bx lr`;
  * relaxed : no hay funcion strict que lo contenga, pero existe un prologo
              como maximo MAX_FUNC bytes por detras (colas de error o
              funciones que terminan en tail-call `b.w`). Se marca como tal.

Regla de emparejamiento (corregida en S111): se usa **solo el `ldr` mas
reciente del mismo registro**, no una busqueda hacia atras. Si un registro se
recarga entre el `ldr` y el `add`, el `add` ya no puede producir la direccion
del literal antiguo; buscar mas atras fabrica referencias falsas (42 sitios
espurios con MAX_GAP=0x1000 en la primera pasada). Con la regla estricta,
todos los emparejamientos validos tienen una separacion <= 0x20.

Salida: analysis/s111_trk/refs.json
Uso:    python3 scan_refs.py [BIN] [CODE_LO] [CODE_HI]
"""
import bisect
import json
import os
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
MAX_GAP = 0x40         # separacion maxima ldr -> add (todos los validos: <= 0x20)
MAX_FUNC = 0x4000       # tamano maximo admitido de una funcion

U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def targets_from(strings):
    return {int(s["vaddr"], 16): s for s in strings}


def scan_refs(data, lo, hi, targets):
    """{vaddr_cadena: [(sitio_add, sitio_ldr, W, clase_ldr)]}"""
    found = {}
    by_reg = {}
    adds = []
    n = len(data)
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o + 4 > n:
            continue
        h = U16(data, o)[0]
        lit = reg = cls = None
        if (h & 0xF800) == 0x4800:                       # ldr rT,[pc,#imm5*4]
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
            cls = "ldr16"
        elif (h & 0xFF7F) == 0xF85F:                     # ldr.w rT,[pc,#imm12]
            h2 = U16(data, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
            cls = "ldr.w"
        if reg is not None and 0 <= lit - BASE <= n - 4:
            by_reg.setdefault(reg, []).append((a, U32(data, lit - BASE)[0], cls))
        elif (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:   # add rX, pc
            adds.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
    keys = {}
    for r, v in by_reg.items():
        v.sort()
        keys[r] = [x[0] for x in v]
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        if i < 0:
            continue
        la, w, cls = v[i]           # solo el ldr mas reciente de ese registro
        if a - la > MAX_GAP:
            continue
        tgt = (w + (a + 4)) & 0xFFFFFFFF
        if tgt in targets:
            found.setdefault(tgt, []).append((a, la, w, cls))
    return found


def prologue_ends(data, lo, hi):
    """[(inicio, fin)] de funciones Thumb con prologo push{..,lr}."""
    n = len(data)
    out = []
    a = lo
    starts = []
    while a < hi:
        o = a - BASE
        if o < 0 or o + 4 > n:
            break
        h = U16(data, o)[0]
        ok = False
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            ok = True
        elif h == 0xE92D and (U16(data, o + 2)[0] & 0x4000):
            ok = True
        if ok:
            starts.append(a)
        a += 2
    for s in starts:
        end = None
        a = s
        limit = min(s + MAX_FUNC, hi)
        while a < limit:
            o = a - BASE
            h = U16(data, o)[0]
            if (h & 0xFF00) == 0xBD00 and (h & 0x0100):       # pop {..,pc}
                end = a + 2
                break
            if h == 0x4770:                                    # bx lr
                end = a + 2
                break
            if h == 0xE8BD and (U16(data, o + 2)[0] & 0x8000):  # pop.w {..,pc}
                end = a + 4
                break
            a += 2
        if end is not None:
            out.append((s, end))
    out.sort()
    return out


def owner(site, funcs, starts):
    """(inicio, 'strict'|'relaxed'|None)"""
    i = bisect.bisect_right(starts, site) - 1
    while i >= 0:
        s, e = funcs[i]
        if site < e:
            return s, "strict"
        if site - s > MAX_FUNC:
            break
        i -= 1
    i = bisect.bisect_right(starts, site) - 1
    if i >= 0 and site - funcs[i][0] <= MAX_FUNC:
        return funcs[i][0], "relaxed"
    return None, None


def main():
    bin_path = sys.argv[1] if len(sys.argv) > 1 else BIN
    lo = int(sys.argv[2], 0) if len(sys.argv) > 2 else BASE
    hi = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x43C00000
    data = open(bin_path, "rb").read()
    strings = json.load(open(os.path.join(HERE, "strings_raw.json")))["strings"]
    targets = targets_from(strings)
    refs = scan_refs(data, lo, hi, targets)
    funcs = prologue_ends(data, lo, hi)
    starts = [f[0] for f in funcs]
    rows = []
    for s in strings:
        t = int(s["vaddr"], 16)
        hits = sorted(set(refs.get(t, [])))
        owners = []
        for x, la, _w, _c in hits:
            f, kind = owner(x, funcs, starts)
            owners.append({"site": hex(x), "ldr": hex(la),
                           "func": hex(f) if f else None,
                           "kind": kind})
        rows.append({"vaddr": s["vaddr"], "text": s["text"],
                     "sites": [hex(x[0]) for x in hits],
                     "refs": owners,
                     "funcs": [o["func"] for o in owners]})
    n_strict = sum(1 for r in rows for o in r["refs"] if o["kind"] == "strict")
    n_relaxed = sum(1 for r in rows for o in r["refs"] if o["kind"] == "relaxed")
    n_none = sum(1 for r in rows for o in r["refs"] if o["kind"] is None)
    json.dump({"module": "TRK", "bin": bin_path, "code_lo": hex(lo),
               "code_hi": hex(hi), "n_functions": len(funcs),
               "n_strings": len(rows),
               "n_referenced": sum(1 for r in rows if r["sites"]),
               "n_sites": sum(len(r["sites"]) for r in rows),
               "n_sites_strict": n_strict, "n_sites_relaxed": n_relaxed,
               "n_sites_unowned": n_none,
               "strings": rows},
              open(os.path.join(HERE, "refs.json"), "w"), indent=1,
              ensure_ascii=False)
    print(f"{len(funcs)} funciones; {sum(1 for r in rows if r['sites'])}/{len(rows)} cadenas referenciadas; "
          f"{n_strict} sitios strict, {n_relaxed} relaxed, {n_none} sin dueno")


if __name__ == "__main__":
    main()
