#!/usr/bin/env python3
"""S116 — extracción del módulo `[SFRS]` a partir de los bytes del firmware.

Genera, sin cargar el binario en estructuras ni ejecutar nada:

1. `strings_raw.json`    — las cadenas `[SFRS]...` con vaddr/offset/texto.
2. `pic_refs_sfrs.json`  — pares PIC verificados `(ldr rX,[pc,#imm] ; add rX,pc)`
   que resuelven exactamente al inicio de una cadena `[SFRS]`.
3. `func_map.json`       — función Thumb (prólogo `push {..,lr}`) que contiene
   cada sitio `add`; por tanto, la función que emite cada traza.
4. `sfrs.json`           — resumen estructurado (recuentos, sub-bloques,
   funciones, ficheros fuente y diferencial A7S) usado por el informe y los
   tests.

Emparejamiento PIC (regla corregida en S116, ver `sfrs.md` § «Corrección
metodológica»):

* Barrido Thumb con fronteras: si el halfword es prefijo de instrucción de
  32 bits (`(h >> 11) in (0x1d, 0x1e, 0x1f)`) se avanza 4 bytes; si no, 2.
  Así no se interpreta como `add rX,pc` el segundo halfword de otra
  instrucción.
* Para cada `add rX,pc` se toma **solo** el `ldr rX,[pc,#imm]` inmediatamente
  anterior del **mismo registro**, con separación <= 0x20 bytes. No se
  retrocede a `ldr` más antiguos (eso produce falsos positivos por
  reutilización de registro).
* Semántica del PC en este firmware (verificada en SETPIN/GETPIN): el literal
  se suma a `add_addr + 4` **sin alinear**. La variante alineada cae 2 bytes
  antes del inicio de la cadena.

El destino debe coincidir exactamente con el inicio de una racha imprimible.

Convención verificada: vaddr = 0x43541000 + file_offset.

Uso:  .venv/bin/python analysis/s116_sfrs/scan_sfrs.py
"""
import bisect
import hashlib
import json
import os
import re
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
PREFIX = b"[SFRS]"
MAX_LDR_GAP = 0x20          # separación máxima ldr -> add (bytes)
MAX_FUNC_SPAN = 0x8000      # un sitio no puede estar a más de 32 KB del prólogo
CODE_LO = 0x439a0000        # clúster de código SFRS
CODE_HI = 0x439c0000

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from

UNVERIFIED = [
    "Significado de las siglas SFRS: no aparece expandida en ningún byte del binario.",
    "Significado de las siglas AIC, RC, VFX, IIB y del identificador PINSEND.",
    "Tipo y estructura de datos de cada campo de las trazas (%x, %02d, %s).",
    "Si el número de línea (line=%d) corresponde al fichero citado en file=%s;"
    " no se ha reconstruido la tabla de líneas de los .cpp.",
    "El fichero fuente de las 40 funciones que no pasan un literal file=%s:"
    " solo 12 de las 52 se pueden atribuir por esta vía.",
]


# --------------------------------------------------------------------------
# cadenas
# --------------------------------------------------------------------------
def sfrs_strings(data):
    """Todas las apariciones de `[SFRS]`, con el texto imprimible completo."""
    out = []
    start = 0
    while True:
        i = data.find(PREFIX, start)
        if i < 0:
            break
        if i > 0 and 32 <= data[i - 1] < 127:
            raise SystemExit(f"[SFRS] en {BASE + i:#x} no inicia cadena")
        e = i
        while e < len(data) and 32 <= data[e] < 127:
            e += 1
        out.append({"vaddr": f"0x{BASE + i:x}", "off": i,
                    "text": data[i:e].decode("latin1")})
        start = i + 1
    return out


def string_starts(data):
    """Inicio de cada racha imprimible (byte previo no imprimible)."""
    out = set()
    prev = False
    for i, b in enumerate(data):
        cur = 32 <= b < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


def cpp_strings(data):
    """Nombres de fichero fuente (`*.cpp`) presentes como cadena literal."""
    out = []
    n = len(data)
    i = 0
    while i < n:
        if 32 <= data[i] < 127:
            e = i
            while e < n and 32 <= data[e] < 127:
                e += 1
            s = data[i:e].decode("latin1")
            if s.endswith(".cpp") and " " not in s and len(s) < 120:
                out.append({"vaddr": f"0x{BASE + i:x}", "name": s})
            i = e
        else:
            i += 1
    return out


# --------------------------------------------------------------------------
# barrido Thumb con fronteras
# --------------------------------------------------------------------------
def is_32bit_prefix(h):
    return (h >> 11) in (0x1D, 0x1E, 0x1F)


def scan(data, lo=BASE, hi=None):
    """Devuelve (ldr, add): listas de (addr, reg, palabra_literal) y (addr, reg)."""
    if hi is None:
        hi = BASE + len(data)
    ldr, add = [], []
    a = lo
    while a + 2 <= hi:
        o = a - BASE
        h = U16(data, o)[0]
        if (h & 0xF800) == 0x4800:                       # ldr rT,[pc,#imm8*4]
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
            o2 = lit - BASE
            if 0 <= o2 <= len(data) - 4:
                ldr.append((a, reg, U32(data, o2)[0]))
        elif (h & 0xFF7F) == 0xF85F:                     # ldr.w rT,[pc,#imm12]
            h2 = U16(data, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
            lit = ((a + 4) & ~3) + imm12
            o2 = lit - BASE
            if 0 <= o2 <= len(data) - 4:
                ldr.append((a, reg, U32(data, o2)[0]))
        elif (h & 0xFF00) == 0x4400:                     # add rX,pc
            rm = (h >> 3) & 0xF
            rd = (((h >> 7) & 1) << 3) | (h & 7)
            if rm == 15:
                add.append((a, rd))
        a += 4 if is_32bit_prefix(h) else 2
    return ldr, add


def pair_refs(ldrs, adds, starts):
    """Empareja cada add con el ldr del mismo registro inmediatamente anterior."""
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    keys = {}
    for r, v in by_reg.items():
        v.sort()
        keys[r] = [x[0] for x in v]

    refs = {}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        i = bisect.bisect_left(keys[reg], a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > MAX_LDR_GAP or a <= la:
            continue
        # PC no alineado: add_addr + 4 (verificado en SETPIN/GETPIN)
        tgt = (w + (a + 4)) & 0xFFFFFFFF
        if tgt in starts:
            refs.setdefault(tgt, []).append([f"0x{la:x}", f"0x{a:x}"])
    return refs


# --------------------------------------------------------------------------
# funciones
# --------------------------------------------------------------------------
def prologues(data, lo, hi):
    out = []
    a = lo
    while a + 2 <= hi:
        o = a - BASE
        h = U16(data, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):      # push {..,lr}
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = U16(data, o + 2)[0]
            if h2 & 0x4000:                              # push.w {..,lr}
                out.append(a)
        a += 4 if is_32bit_prefix(h) else 2
    return out


def owner(site, starts_func):
    """Función (prólogo más cercano por delante) que contiene el sitio."""
    cand = [x for x in starts_func if x <= site]
    if not cand:
        return None
    f = cand[-1]
    return f if site - f <= MAX_FUNC_SPAN else None


def func_map(strings, refs, starts_func):
    by_func = {}
    for s in strings:
        for la, aa in refs.get(int(s["vaddr"], 16), []):
            f = owner(int(aa, 16), starts_func)
            if f is None:
                continue
            e = by_func.setdefault(f, {"func": f"0x{f:x}", "refs": 0,
                                       "strings": []})
            e["refs"] += 1
            if s["text"] not in [x["text"] for x in e["strings"]]:
                e["strings"].append({"vaddr": s["vaddr"], "text": s["text"]})
    return by_func


def source_attribution(data, refs_all, starts_func, clusters):
    """Ficheros `.cpp` citados como literal y funciones que los citan."""
    out = []
    for src in cpp_strings(data):
        sites = refs_all.get(int(src["vaddr"], 16), [])
        if not sites:
            continue
        funcs = []
        for _, aa in sites:
            f = owner(int(aa, 16), starts_func)
            if f is not None and f not in funcs:
                funcs.append(f)
        hit = {"name": src["name"], "vaddr": src["vaddr"],
               "add_sites": len(sites),
               "functions": [f"0x{f:x}" for f in sorted(funcs)],
               "sfrs_cluster_functions": [f"0x{f:x}" for f in sorted(funcs)
                                          if clusters(f)]}
        if hit["sfrs_cluster_functions"]:
            out.append(hit)
    return out


# --------------------------------------------------------------------------
# sub-bloques (reglas por texto, sin inventar significado)
# --------------------------------------------------------------------------
def classify(text):
    t = text
    if "SUPERSTABLEMOVIE" in t:
        return "SUPERSTABLEMOVIE"
    if "MOTIONSHOTVIDEO" in t or "RC_OUT_BUFFER_FULL" in t:
        return "MOTIONSHOTVIDEO"
    if "EFFECT" in t or "SEND_MSG_TO_EXECUTER" in t or "ExecSRC canvas" in t:
        return "EFFECTMOVIEREC"
    if ("PINSEND" in t or "[SETPIN]" in t or "[GETPIN]" in t
            or "Send RecPin" in t or "Send EEPin" in t):
        return "PINSEND"
    if "[SFRS] ***SA_" in t:
        return "SA"
    if "MultiplexTrigger" in t:
        return "MULTIPLEXTRIGGER"
    if ("SET_PATH" in t or "PATH_STATUS" in t or "STATUS_" in t
            or "TRANS_WAIT" in t or "ScalarInfraPathCmdSetPath" in t
            or "SETRECSTATE" in t or "NowVfc" in t):
        return "SET_PATH_STATUS"
    if ("RC_CALLBACK" in t or "CtSetAicParam" in t or "SendExecTrigger" in t):
        return "RC_AIC_TRIGGER"
    raise SystemExit(f"sub-bloque sin clasificar: {t!r}")


# --------------------------------------------------------------------------
# diferencial A7S
# --------------------------------------------------------------------------
FMT = re.compile(r"%(?:[-+ #0]*\d*(?:\.\d+)?(?:hh|h|ll|l|j|z|t|L)?[diouxXeEfgGaAcspn%])")


def norm(text):
    """Normaliza especificadores de formato: `%04d` -> `%`, `0x%x` -> `0x%`."""
    return FMT.sub("%", text)


def differential(a6000_texts, a7s_texts):
    a7s_norm = {norm(t): t for t in a7s_texts}
    common, only_a6000 = [], []
    for t in a6000_texts:
        if norm(t) in a7s_norm:
            common.append(t)
        else:
            only_a6000.append(t)
    a6_norm = {norm(t) for t in a6000_texts}
    only_a7s = [t for t in a7s_texts if norm(t) not in a6_norm]
    return {
        "a7s_count": len(a7s_texts),
        "common": len(common),
        "a6000_only": len(only_a6000),
        "a7s_only": len(only_a7s),
        "a6000_only_texts": only_a6000,
        "a7s_only_texts": only_a7s,
    }


# --------------------------------------------------------------------------
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_summary(data, strings, refs, fmap, sources, diff):
    blocks = {}
    for s in strings:
        blocks.setdefault(classify(s["text"]), []).append(s)
    fmap_by_string = {}
    for f in fmap.values():
        for s in f["strings"]:
            fmap_by_string.setdefault(s["vaddr"], []).append(f["func"])

    sub_blocks = []
    for name in sorted(blocks, key=lambda k: (-len(blocks[k]), k)):
        items = blocks[name]
        funcs = sorted({f for s in items
                        for f in fmap_by_string.get(s["vaddr"], [])})
        sub_blocks.append({
            "name": name,
            "count": len(items),
            "first_vaddr": items[0]["vaddr"],
            "last_vaddr": items[-1]["vaddr"],
            "functions": funcs,
            "strings": [{"vaddr": s["vaddr"], "text": s["text"]}
                        for s in items],
        })

    funcs = [fmap[k] for k in sorted(fmap)]
    return {
        "module": "SFRS",
        "milestone": "S116",
        "artifact": {
            "path": BIN,
            "size": len(data),
            "sha256": sha256(os.path.join(ROOT, BIN)),
            "base_vaddr": f"0x{BASE:x}",
        },
        "counts": {
            "strings": len(strings),
            "add_sites": sum(len(v) for v in refs.values()),
            "functions": len(fmap),
            "unreferenced_strings": 0,
            "strings_with_more_than_one_function": sum(
                1 for v in fmap_by_string.values() if len(v) > 1),
        },
        "ranges": {
            "strings": [strings[0]["vaddr"], strings[-1]["vaddr"]],
            "functions": [funcs[0]["func"], funcs[-1]["func"]],
            "scan_cluster": [f"0x{CODE_LO:x}", f"0x{CODE_HI:x}"],
        },
        "sub_blocks": sub_blocks,
        "functions": funcs,
        "source_files": sources,
        "differential_a7s": {
            "artifact": {"path": A7S, "sha256": sha256(os.path.join(ROOT, A7S))},
            "a7s_strings": diff["a7s_count"],
            "common": diff["common"],
            "a6000_only": diff["a6000_only"],
            "a7s_only": diff["a7s_only"],
            "a7s_only_texts": diff["a7s_only_texts"],
        },
        "unverified": UNVERIFIED,
    }


def main():
    data = open(os.path.join(ROOT, BIN), "rb").read()
    strings = sfrs_strings(data)
    starts = string_starts(data)
    ldrs, adds = scan(data)
    all_refs = pair_refs(ldrs, adds, starts)
    # solo interesan las cadenas [SFRS]
    sfrs_va = {int(s["vaddr"], 16) for s in strings}
    refs = {va: v for va, v in all_refs.items() if va in sfrs_va}
    starts_func = prologues(data, CODE_LO, CODE_HI)
    fmap = func_map(strings, refs, starts_func)
    sources = source_attribution(
        data, all_refs, starts_func,
        lambda f: CODE_LO <= f < CODE_HI)

    # coherencia: toda cadena referenciada y todo sitio atribuido
    missing = [s["vaddr"] for s in strings
               if int(s["vaddr"], 16) not in refs]
    sites = sum(len(v) for v in refs.values())
    attributed = sum(e["refs"] for e in fmap.values())
    if missing or attributed != sites:
        raise SystemExit(f"incoherente: sin ref {missing}, "
                         f"sitios {sites} atribuidos {attributed}")

    json.dump({"module": "SFRS", "count": len(strings), "strings": strings},
              open(os.path.join(HERE, "strings_raw.json"), "w"),
              indent=1, ensure_ascii=False)
    json.dump({f"0x{k:x}": v for k, v in sorted(refs.items())},
              open(os.path.join(HERE, "pic_refs_sfrs.json"), "w"),
              indent=0, ensure_ascii=False)
    json.dump({"module": "SFRS",
               "functions": [fmap[k] for k in sorted(fmap)]},
              open(os.path.join(HERE, "func_map.json"), "w"),
              indent=1, ensure_ascii=False)

    print(f"cadenas: {len(strings)}  con ref PIC: {len(strings) - len(missing)}")
    print(f"sitios add: {sites}  atribuidos: {attributed}")
    print(f"funciones: {len(fmap)}")
    blocks = {}
    for s in strings:
        blocks.setdefault(classify(s["text"]), []).append(s)
    for k in sorted(blocks, key=lambda x: -len(blocks[x])):
        print(f"  {k:20s} {len(blocks[k]):3d}")

    try:
        a7s = open(os.path.join(ROOT, A7S), "rb").read()
    except OSError:
        print("A7S no disponible: diferencial omitido")
        return 0
    a7s_strings = [s["text"] for s in sfrs_strings(a7s)]
    d = differential([s["text"] for s in strings], a7s_strings)
    print(f"A7S: {d['a7s_count']} cadenas; comunes {d['common']}; "
          f"solo A6000 {d['a6000_only']}; solo A7S {d['a7s_only']}")

    summary = build_summary(data, strings, refs, fmap, sources, d)
    json.dump(summary, open(os.path.join(HERE, "sfrs.json"), "w"),
              indent=1, ensure_ascii=False)
    print(f"fuentes .cpp citadas desde el clúster: {len(sources)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
