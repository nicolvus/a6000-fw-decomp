#!/usr/bin/env python3
"""S118 — diferencial con la A7S fw3.20 a nivel de **código**.

La A7S tiene su propio `av-cam.bin` (blob raw, sin convención de vaddr
compartida).  El escaneo es **independiente de la base**: para un `add rX, pc`
situado en el offset de fichero `f` con un `ldr` que carga `W`, la cadena a la
que apunta está en el offset de fichero `W + f + 4`.  Con eso se localiza el
código de la A7S que referencia las 100 trazas `[SFRA]` y se compara con la
A6000 (mismo número de funciones, mismos ids de comando, etc.).

Se aplica el mismo *kill analysis* que en `pic_dataflow.py`: un `ldr` deja de
ser válido si entre el `ldr` y el `add` se escribe ese registro.
"""
import bisect
import json
import os
import re
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

HERE = os.path.dirname(os.path.abspath(__file__))
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6K = "analysis/rea-independent/input/av-cam.bin"
MAX_LDR_GAP = 4096


def sfra_strings(data):
    out = {}
    i = data.find(b"[SFRA")
    while i >= 0:
        e = i
        while e < len(data) and 32 <= data[e] < 127:
            e += 1
        out[i] = data[i:e].decode("latin1")
        i = data.find(b"[SFRA", i + 1)
    return out


def starts(data):
    out = set()
    prev = False
    for i in range(len(data)):
        cur = 32 <= data[i] < 127
        if cur and not prev:
            out.add(i)
        prev = cur
    return out


def ldr_literal(data, f):
    """(reg, W) si en el offset `f` hay un `ldr rX,[pc,#imm]`."""
    h = struct.unpack_from("<H", data, f)[0]
    if (h & 0xF800) == 0x4800:
        reg = (h >> 8) & 7
        lit = ((f + 4) & ~3) + (h & 0xFF) * 4
    elif (h & 0xFF7F) == 0xF85F:
        h2 = struct.unpack_from("<H", data, f + 2)[0]
        reg = (h2 >> 12) & 0xF
        imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
        lit = ((f + 4) & ~3) + imm12
    else:
        return None
    if not (0 <= lit < len(data) - 4):
        return None
    return reg, struct.unpack_from("<I", data, lit)[0]


def add_pc_reg(data, f):
    h = struct.unpack_from("<H", data, f)[0]
    if (h & 0xFF00) != 0x4400 or ((h >> 3) & 0xF) != 15:
        return None
    return (((h >> 7) & 1) << 3) | (h & 7)


def prologues(data):
    """offsets de `push {..,lr}` (prólogo de función Thumb)."""
    out = []
    for f in range(0, len(data) - 4, 2):
        h = struct.unpack_from("<H", data, f)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(f)
        elif h == 0xE92D:
            h2 = struct.unpack_from("<H", data, f + 2)[0]
            if h2 & 0x4000:
                out.append(f)
    return out


def writes_reg(md, data, lo, hi, reg):
    a = lo
    while a < hi:
        try:
            ins = next(md.disasm(data[a:a + 4], a, count=1))
        except StopIteration:
            a += 2
            continue
        if ins is None:
            a += 2
            continue
        try:
            _, wr = ins.regs_access()
        except Exception:
            wr = []
        for r in wr:
            if md.reg_name(r) == f"r{reg}":
                return True
        a += ins.size
    return False


def scan(data, strings):
    """offset de cadena -> [offsets de los sitios `add`] (con kill analysis)."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    st = starts(data)
    ldrs = {}
    adds = []
    f = 0
    while f < len(data) - 4:
        lit = ldr_literal(data, f)
        if lit is not None:
            ldrs.setdefault(lit[0], []).append((f, lit[1]))
        r = add_pc_reg(data, f)
        if r is not None:
            adds.append((f, r))
        f += 2
    keys = {}
    for r, v in ldrs.items():
        v.sort()
        keys[r] = [x[0] for x in v]
    refs = {}
    for f, reg in adds:
        v = ldrs.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, f) - 1
        while i >= 0:
            lf, w = v[i]
            if f - lf > MAX_LDR_GAP:
                break
            tgt = w + f + 4
            if tgt in st and tgt in strings:
                if not writes_reg(md, data, lf + 2, f, reg):
                    refs.setdefault(tgt, []).append(f)
            i -= 1
    return refs


def main():
    a7s = open(A7S, "rb").read()
    a6k = open(A6K, "rb").read()
    s7 = sfra_strings(a7s)
    s6 = sfra_strings(a6k)
    refs7 = scan(a7s, s7)
    refs6 = scan(a6k, s6)
    pros7 = prologues(a7s)
    pros6 = prologues(a6k)

    def func_of(off, pros):
        cands = [p for p in pros if p <= off and off - p <= 0x4000]
        return cands[-1] if cands else None

    out = {}
    for tag, ss, refs, pros in (("a6000", s6, refs6, pros6), ("a7s", s7, refs7, pros7)):
        sites = [f for v in refs.values() for f in v]
        funcs = {func_of(f, pros) for f in sites}
        funcs.discard(None)
        out[tag] = {
            "strings": len(ss),
            "sites": len(sites),
            "distinct_sites": len(set(sites)),
            "functions": len(funcs),
            "code_lo": hex(min(sites)) if sites else None,
            "code_hi": hex(max(sites)) if sites else None,
            "str_lo": hex(min(ss)),
            "str_hi": hex(max(ss)),
        }
        print(tag, out[tag])
    print("textos idénticos:", set(s7.values()) == set(s6.values()))
    print("A7S sólo:", sorted(set(s7.values()) - set(s6.values())))
    print("A6000 sólo:", sorted(set(s6.values()) - set(s7.values())))
    json.dump(out, open(os.path.join(HERE, "a7s_diff.json"), "w"), indent=1)
    # sólo las entradas [SFRA] (el resto son 95 000 cadenas sin relación)
    json.dump({"a6000": {f"0x{k:x}": sorted(set(v)) for k, v in refs6.items()},
               "a7s": {f"0x{k:x}": sorted(set(v)) for k, v in refs7.items()}},
              open(os.path.join(HERE, "a7s_pic_refs.json"), "w"), indent=0)


if __name__ == "__main__":
    main()
