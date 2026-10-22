#!/usr/bin/env python3
"""S125 — inventario de los módulos de trazas `[IMAGING_REL]` y `[IMAGING]`.

Trabaja **solo sobre bytes** (sin REA/Ghidra) y con una huella de memoria pequeña:
el binario se lee en un bloque, no se copia.

Salidas (JSON) por perfil:
  * las cadenas del módulo (vaddr + texto), con su **bloque** (sub-bloque semántico),
  * los sitios de referencia PIC (regla **estricta** canónica de S106,
    ver analysis/s106_imaging_cap/pic_xref_methodology.md),
  * la atribución sitio → función (prólogo Thumb `push {..,lr}` más cercano por detrás),
  * los ficheros fuente `.cpp`/`.h` referenciados por esas funciones.

Uso:  scan_imaging_modules.py A6000 | A7S | A6300
"""
import bisect
import json
import os
import re
import struct
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
MAX_LDR_GAP = 4096          # ventana del esquema PIC (canónica)
MAX_FUNC = 0x4000           # tamaño máximo admitido de una función

PROFILES = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/"
            "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/"
              "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}

# prefijos de módulo (el texto de la cadena empieza por ellos)
MODULES = {
    "IMAGING_REL": "[IMAGING_REL]:",
    "IMAGING": "[IMAGING]:",
}

# mensajes genéricos del módulo `[IMAGING]`: el macro `FATAL!` y el formato `%s:%d`.
# No describen una función concreta del subsistema, sino el punto de fallo.
GENERIC_SUFFIXES = ("FATAL! %s:%d", "FATAL! %s:%d [0x%x]", "%s:%d \n")


def is_generic(text):
    """True si el texto (ya sin prefijo de módulo) es un mensaje genérico."""
    for pre in MODULES.values():
        if text.startswith(pre):
            text = text[len(pre):].lstrip(" ")
            break
    return text in GENERIC_SUFFIXES


# --------------------------------------------------------------------------- utils
def load(path):
    with open(path, "rb") as fh:
        return fh.read()


def nul_strings(data):
    """[(offset, texto)] de todas las cadenas terminadas en NUL.

    Una cadena empieza justo después de un NUL (o en el offset 0) y termina en el
    siguiente NUL.  Se aceptan bytes de control (< 0x20) dentro del texto: el firmware
    tiene literales con '\\n' (p. ej. `[IMAGING]: %s:%d \\n`).
    """
    out = []
    n = len(data)
    i = 0
    while i < n:
        c = data[i]
        if 32 <= c < 127:
            e = data.find(b"\x00", i)
            if e < 0:
                e = n
            if e > i:
                out.append((i, data[i:e].decode("latin-1")))
                i = e + 1
                continue
        i += 1
    return out


def string_start_set(data):
    """Offsets de inicio de cadena NUL-terminada (los mismos que `nul_strings`)."""
    return {off for off, _ in nul_strings(data)}


# --------------------------------------------------------------------------- PIC
def ldr_sites(data):
    out = []
    n = len(data)
    a = 0
    while a + 4 <= n:
        h = struct.unpack_from("<H", data, a)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:                       # ldr rT, [pc, #imm5*4]
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:                     # ldr.w rT, [pc, #imm12]
            if a + 6 <= n:
                h2 = struct.unpack_from("<H", data, a + 2)[0]
                reg = (h2 >> 12) & 0xF
                lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit
            if 0 <= o2 <= n - 4:
                out.append((a, reg, struct.unpack_from("<I", data, o2)[0]))
        a += 2
    return out


def add_sites(data):
    out = []
    n = len(data)
    a = 0
    while a + 2 <= n:
        h = struct.unpack_from("<H", data, a)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    return out


def pic_refs(data, starts):
    """Regla estricta canónica: `add rX,pc` + `ldr` más cercano del mismo registro."""
    ldrs = ldr_sites(data)
    adds = add_sites(data)
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
        if i < 0:
            continue
        la, w = v[i]
        if a - la > MAX_LDR_GAP:
            continue
        tgt = (w + (a + 4)) & 0xFFFFFFFF
        if tgt in starts:
            out.setdefault(tgt, []).append(a)
    return {k: sorted(set(v)) for k, v in sorted(out.items())}


# ------------------------------------------------------------------- funciones
def prologues(data):
    """Offsets de prólogos Thumb `push {..,lr}` (16 bits 0xb5xx y 32 bits 0xe92d)."""
    out = []
    n = len(data)
    a = 0
    while a + 2 <= n:
        h = struct.unpack_from("<H", data, a)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D and a + 4 <= n:
            h2 = struct.unpack_from("<H", data, a + 2)[0]
            if h2 & 0x4000:                       # bit de LR en el registro lista
                out.append(a)
        a += 2
    return out


def build_func_index(data, starts_list):
    """Índice de funciones: para cada offset, la función (prólogo previo) que lo contiene."""
    keys = sorted(starts_list)
    return keys


def func_of(site, keys):
    i = bisect.bisect_right(keys, site) - 1
    if i < 0:
        return None
    f = keys[i]
    if site - f > MAX_FUNC:
        return None
    return f


# --------------------------------------------------------------------------- main
def analyse(prof):
    path = os.path.join(REPO, PROFILES[prof])
    data = load(path)
    strs = nul_strings(data)
    by_text = {}
    for off, s in strs:
        by_text.setdefault(off, s)

    modules = {}
    for name, prefix in MODULES.items():
        items = [(off, s) for off, s in strs if s.startswith(prefix)]
        modules[name] = items

    starts = string_start_set(data)
    refs = pic_refs(data, starts)
    prols = prologues(data)
    keys = build_func_index(data, prols)

    # ficheros fuente embebidos referenciados desde las funciones emisoras
    src_files = {}
    for off, s in strs:
        if re.fullmatch(r"[A-Za-z0-9_./]{3,60}\.(?:cpp|h|cc)", s):
            src_files[off] = s

    out = {
        "profile": prof,
        "bin": PROFILES[prof],
        "size": len(data),
        "base": hex(BASE),
        "modules": {},
        "n_prologues": len(prols),
    }
    for name, items in modules.items():
        rows = []
        for off, s in items:
            sites = refs.get(off, [])
            funcs = []
            for site in sites:
                f = func_of(site, keys)
                funcs.append({"site": hex(BASE + site),
                              "func": hex(BASE + f) if f is not None else None})
            rows.append({
                "vaddr": hex(BASE + off),
                "offset": hex(off),
                "text": s,
                "sites": [hex(BASE + x) for x in sites],
                "funcs": funcs,
            })
        funcs_count = {}
        for r in rows:
            for fu in r["funcs"]:
                if fu["func"]:
                    funcs_count[fu["func"]] = funcs_count.get(fu["func"], 0) + 1
        out["modules"][name] = {
            "n": len(rows),
            "lo": hex(BASE + min(o for o, _ in items)) if items else None,
            "hi": hex(BASE + max(o for o, _ in items)) if items else None,
            "n_referenced": sum(1 for r in rows if r["sites"]),
            "n_sites": sum(len(r["sites"]) for r in rows),
            "n_functions": len(funcs_count),
            "func_counts": dict(sorted(funcs_count.items(), key=lambda kv: -kv[1])),
            "strings": rows,
        }

    # ficheros fuente referenciados por las funciones emisoras de cada módulo:
    # se busca un sitio PIC que caiga dentro de una de esas funciones.
    # Se separan los ficheros atribuidos a las funciones que emiten un mensaje
    # **específico** del módulo de los que solo emiten el mensaje genérico `FATAL!`.
    for name in MODULES:
        rows = out["modules"][name]["strings"]
        funcs_all, funcs_spec = set(), set()
        for r in rows:
            spec = not is_generic(r["text"])
            for fu in r["funcs"]:
                if not fu["func"]:
                    continue
                fo = int(fu["func"], 16) - BASE
                funcs_all.add(fo)
                if spec:
                    funcs_spec.add(fo)
        funcs_gen = funcs_all - funcs_spec
        fset_spec, fset_gen = {}, {}
        for so, ssn in src_files.items():
            for site in refs.get(so, []):
                f = func_of(site, keys)
                if f is None:
                    continue
                if f in funcs_spec:
                    fset_spec.setdefault(ssn, []).append(hex(BASE + site))
                elif f in funcs_gen:
                    fset_gen.setdefault(ssn, []).append(hex(BASE + site))
                else:
                    break
        out["modules"][name]["src_files"] = {k: sorted(set(v)) for k, v in sorted(fset_spec.items())}
        out["modules"][name]["src_files_generic"] = {k: sorted(set(v)) for k, v in sorted(fset_gen.items())}
        out["modules"][name]["n_funcs_specific"] = len(funcs_spec)
        out["modules"][name]["n_funcs_generic"] = len(funcs_gen)

        # mapa función → trazas (para el informe)
        fmap = {}
        for r in rows:
            for fu in r["funcs"]:
                if not fu["func"]:
                    continue
                fmap.setdefault(fu["func"], []).append(
                    {"vaddr": r["vaddr"], "text": r["text"], "site": fu["site"],
                     "generic": is_generic(r["text"])})
        out["modules"][name]["func_map"] = {
            k: sorted(v, key=lambda d: d["vaddr"]) for k, v in sorted(fmap.items())}

    # fichero fuente por función: el literal `__FILE__` referenciado dentro de la función.
    # El final de la función se toma como el siguiente prólogo (acotado por MAX_FUNC).
    func_files = {}
    for so, ssn in src_files.items():
        for site in refs.get(so, []):
            f = func_of(site, keys)
            if f is None:
                continue
            func_files.setdefault(f, set()).add(ssn)
    out["func_files"] = {hex(BASE + f): sorted(v) for f, v in sorted(func_files.items())}

    dest = os.path.join(REPO, f"analysis/s125_imaging_rel/{prof.lower()}_scan.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    # mapa PIC completo (offsets -> sitios), reutilizable por otros scripts
    dest2 = os.path.join(REPO, f"analysis/s125_imaging_rel/{prof.lower()}_pic_refs.json")
    with open(dest2, "w") as fh:
        json.dump({hex(BASE + k): [hex(BASE + x) for x in v] for k, v in refs.items()},
                  fh, indent=0)
    for name in MODULES:
        m = out["modules"][name]
        print(f"{prof} {name}: {m['n']} cadenas [{m['lo']}-{m['hi']}] "
              f"referenciadas={m['n_referenced']} sitios={m['n_sites']} funciones={m['n_functions']}")
    print("->", dest)


if __name__ == "__main__":
    analyse(sys.argv[1] if len(sys.argv) > 1 else "A6000")
