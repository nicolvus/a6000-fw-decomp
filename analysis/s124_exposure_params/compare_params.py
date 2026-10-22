#!/usr/bin/env python3
"""S124 — el bloque de parámetros de exposición/lectura por `drive_mode` del imager.

Pregunta: ¿la fw3.21 de la A6000 cambia el bloque de parámetros que el imager usa
por modo de lectura (en particular el byte `shut` de la traza `SetExps`)?

Método:
 1. localizar la cadena `SetExps : [PrevDrv:…]` en la A6000 y en la A7S;
 2. encontrar su sitio de referencia PIC (regla estricta) en cada blob;
 3. desensamblar la función que la emite en ambos y comparar instrucción a
    instrucción (mismo código => mismo comportamiento).

Salida: analysis/s124_exposure_params/result.json
"""
import json
import os
import struct
from collections import defaultdict

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
A6000 = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
HERE = os.path.dirname(os.path.abspath(__file__))
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def load(path):
    return open(path, "rb").read()


def u16(d, a):
    return struct.unpack_from("<H", d, a - BASE)[0]


def u32(d, a):
    return struct.unpack_from("<I", d, a - BASE)[0]


def string_starts(d):
    out = set()
    prev = False
    for i, c in enumerate(d):
        cur = 32 <= c < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


def ldr_sites(d, lo, hi):
    out = []
    for a in range(lo, hi, 2):
        h = u16(d, a)
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = u16(d, a + 2)
            reg = h2 >> 12
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is None:
            continue
        o2 = lit - BASE
        if 0 <= o2 <= len(d) - 4:
            out.append((a, reg, u32(d, lit)))
    return out


def add_sites(d, lo, hi):
    out = []
    for a in range(lo, hi, 2):
        h = u16(d, a)
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
    return out


def refs_to(d, target_addr, lo, hi):
    """Sitios (add) que materializan la cadena en `target_addr` (regla estricta)."""
    starts = string_starts(d)
    ldrs = defaultdict(list)
    for a, reg, w in ldr_sites(d, lo, hi):
        ldrs[reg].append((a, w))
    for v in ldrs.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in ldrs.items()}
    import bisect
    out = []
    for a, reg in add_sites(d, lo, hi):
        v = ldrs.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > 4096:
            continue
        tgt = (w + (a + 4)) & 0xFFFFFFFF
        if tgt == target_addr:
            out.append((a, la))
    return out


def find_string(d, needle):
    i = d.find(needle)
    if i < 0:
        return None
    s = i
    while s > 0 and 32 <= d[s - 1] < 127:
        s -= 1
    return BASE + s


def func_start(d, site):
    """Prólogo Thumb más cercano por delante."""
    for a in range(site, site - 0x4000, -2):
        h = u16(d, a)
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            return a
        if h == 0xE92D and (u16(d, a + 2) & 0x4000):
            return a
    return None


def disasm(d, start, n=80):
    out = []
    for k, ins in enumerate(MD.disasm(d[start - BASE:start - BASE + 0x400], start)):
        if k >= n:
            break
        out.append(f"{ins.address:#x} {ins.mnemonic} {ins.op_str}")
    return out


def main():
    res = {}
    for label, path in (("A6000", A6000), ("A7S", A7S)):
        d = load(path)
        addr = (find_string(d, b"SetExps : [PrevDrv:") if label == "A6000"
                else find_string(d, b"Exposure. [NowDriveMode:"))
        info = {"string_vaddr": f"0x{addr:x}" if addr else None}
        if addr:
            sites = refs_to(d, addr, BASE, BASE + len(d))
            info["ref_sites"] = [f"0x{a:x}" for a, _ in sites]
            if sites:
                fs = func_start(d, sites[0][0])
                info["func"] = f"0x{fs:x}" if fs else None
                if fs:
                    info["disasm"] = disasm(d, fs, 60)
        res[label] = info
        print(label, info.get("string_vaddr"), info.get("ref_sites"), info.get("func"))

    # comparación de la secuencia de instrucciones
    a = res["A6000"].get("disasm") or []
    b = res["A7S"].get("disasm") or []
    n = min(len(a), len(b))
    iguales = 0
    difs = []
    for i in range(n):
        # comparar mnemónico + operandos (sin direcciones absolutas)
        ta = a[i].split(" ", 1)[1]
        tb = b[i].split(" ", 1)[1]
        if ta == tb:
            iguales += 1
        elif len(difs) < 12:
            difs.append({"i": i, "a6000": a[i], "a7s": b[i]})
    res["compare"] = {"n": n, "identicas": iguales, "diferencias": difs}
    print(f"instrucciones comparadas: {n}, idénticas: {iguales}, diferencias: {len(difs)}")
    for d_ in difs:
        print("   ", d_["a6000"], "|", d_["a7s"])
    dest = os.path.join(HERE, "result.json")
    json.dump(res, open(dest, "w"), indent=1, ensure_ascii=False)
    print("escrito", dest)


if __name__ == "__main__":
    main()
