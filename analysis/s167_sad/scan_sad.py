#!/usr/bin/env python3
"""S167 — el módulo `[SAD]` (44/45 trazas) del firmware A6000 fw3.21.

Sólo bytes (sin REA/Ghidra). Salida: analysis/s167_sad/sad_raw.json

Pasos:
  1. Extrae las cadenas que empiezan por `[SAD]` (con su inicio real de cadena).
  2. Sitios PIC con la **regla estricta** (canónica del repo, S106):
     cada `add rX,pc` se empareja con el `ldr rX,[pc,#imm]` MÁS CERCANO por detrás
     (ventana 4 KB).  El mapa global ya calculado se usa como fuente; aquí se
     re-derivan y **verifican** los pares (destino == inicio de cadena, registro
     no reescrito entre `ldr` y `add`).
  3. Atribuye cada sitio a su función (prólogo Thumb `push {..,lr}` más cercano).
  4. Recolecta TODAS las cadenas referenciadas por cada función emisora (para
     poder asignar fichero fuente / clase).
  5. Calcula los llamadores `bl` directos de las funciones emisoras.
  6. Busca en el binario cualquier expansión textual de la sigla "SAD".
  7. Diferencial texto a texto con la A7S fw3.20 y el A6300 fw2.01.
"""
import bisect
import json
import os
import re
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A63 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
GLOBAL = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

CODE_LO, CODE_HI = 0x43541000, 0x43A00000
TOKEN = b"[SAD]"

B = open(os.path.join(ROOT, BIN), "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def cstr(addr, blob=None):
    blob = B if blob is None else blob
    o = addr - BASE
    if o < 0 or o >= len(blob):
        return None
    e = blob.find(b"\x00", o)
    if e < 0:
        return None
    return blob[o:e].decode("latin1")


# ---------------------------------------------------------------- PIC (estricta)
def pic_ldr_sites(lo, hi):
    """[(addr, reg, valor_literal, dir_literal)] de `ldr rX,[pc,#imm]`."""
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
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None and 0 <= lit - BASE <= N - 4:
            out.append((a, reg, U32(B, lit - BASE)[0], lit))
        a += 2
    return out


def pic_add_sites(lo, hi):
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


def writes_to_reg(lo, hi, reg):
    """Direcciones de escritura a `reg` en [lo,hi) -> (addr, etiqueta)."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        note = None
        if (h & 0xF800) == 0x4800 and ((h >> 8) & 7) == reg:
            note = "ldr-lit"
        elif (h & 0xFF7F) == 0xF85F and ((U16(B, o + 2)[0] >> 12) & 0xF) == reg:
            note = "ldr.w-lit"
        elif (h & 0xF800) == 0x6800 and ((h >> 8) & 7) == reg:
            note = "ldr-mem"
        elif (h & 0xF800) == 0x9800 and ((h >> 8) & 7) == reg:
            note = "ldr-mem.w"
        elif 0x2000 <= (h & 0xF800) <= 0x3800 and ((h >> 8) & 7) == reg:
            note = "movs-imm"
        elif (h & 0xFC00) == 0x4000 and ((h & 7) | ((h >> 4) & 8)) == reg:
            note = "ops-reg"
        if note:
            out.append((a, note))
        a += 2
    return out


def string_starts(lo, hi):
    """Inicio de cadena: byte imprimible cuyo byte anterior no lo es."""
    o0, o1 = max(0, lo - BASE), min(N, hi - BASE)
    out = set()
    prev = False
    for i in range(o0, o1):
        cur = 32 <= B[i] < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


def strict_pairs(lo=CODE_LO, hi=CODE_HI):
    """{destino: [sitios]} con la regla estricta (verificada contra el mapa global)."""
    starts = string_starts(BASE, BASE + N)
    ldrs = pic_ldr_sites(lo, hi)
    adds = pic_add_sites(lo, hi)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = {}
    detail = {}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        if i < 0:
            continue
        la, w, lit = v[i]
        if a - la > 4096:
            continue
        dest = (w + (a + 4)) & 0xFFFFFFFF
        if dest in starts:
            out.setdefault(dest, []).append(a)
            between = writes_to_reg(la + 2, a, reg)
            detail.setdefault(dest, []).append({
                "sitio": hex(a), "ldr": hex(la), "pool": hex(lit),
                "W": hex(w), "destino": hex(dest),
                "reescritura_entre": [[hex(x), n] for x, n in between],
            })
    return out, detail


# ---------------------------------------------------------------- funciones
def prologues(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = U16(B, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def bl_callers(targets):
    """{destino: [sitios `bl`]} — decodificación manual del patrón de 32 bits."""
    out = {t: [] for t in targets}
    tset = set(targets)
    for a in range(CODE_LO, CODE_HI - 4, 2):
        h1 = U16(B, a - BASE)[0]
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = U16(B, a - BASE + 2)[0]
        if (h2 & 0xD000) not in (0x9000, 0xD000):
            continue
        s = (h1 >> 10) & 1
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if s:
            imm -= 1 << 25
        tgt = (a + 4 + imm) & 0xFFFFFFFF
        if tgt in tset:
            out[tgt].append(a)
    return out


def abs_pointers(va):
    pat = struct.pack("<I", va)
    return [BASE + m.start() for m in re.finditer(re.escape(pat), B)]


# ---------------------------------------------------------------- diferencial
def model_texts(path):
    blob = open(os.path.join(ROOT, path), "rb").read()
    occ = []
    for m in re.finditer(re.escape(TOKEN), blob):
        s = m.start()
        while s > 0 and blob[s - 1] != 0 and 32 <= blob[s - 1] < 127:
            s -= 1
        e = blob.find(b"\x00", m.start())
        occ.append((BASE + s, blob[s:e].decode("latin1")))
    return occ


def main():
    global_map = json.load(open(os.path.join(ROOT, GLOBAL)))
    gm = {int(k, 16): sorted(set(v)) for k, v in global_map.items()}

    # --- 1. cadenas [SAD]
    cad = []
    seen = set()
    for m in re.finditer(re.escape(TOKEN), B):
        s = m.start()
        while s > 0 and B[s - 1] != 0 and 32 <= B[s - 1] < 127:
            s -= 1
        if s in seen:
            continue
        seen.add(s)
        e = B.find(b"\x00", s)
        cad.append({"vaddr": BASE + s, "texto": B[s:e].decode("latin1")})
    cad.sort(key=lambda x: x["vaddr"])

    # --- 2. PIC: re-derivada + cotejo con el mapa global del repo
    pairs, detail = strict_pairs()
    mismatch = []
    for c in cad:
        a = c["vaddr"]
        mine = sorted(set(pairs.get(a, [])))
        theirs = sorted(set(gm.get(a, [])))
        if mine != theirs:
            mismatch.append({"vaddr": hex(a), "re_derivada": [hex(x) for x in mine],
                             "mapa_global": [hex(x) for x in theirs]})

    P = prologues(CODE_LO, CODE_HI)

    def fstart(site):
        i = bisect.bisect_right(P, site) - 1
        return P[i] if i >= 0 else None

    # --- 3. función → trazas
    funcs = {}
    for c in cad:
        a = c["vaddr"]
        for s in sorted(set(pairs.get(a, []))):
            f = fstart(s)
            key = hex(f) if f else "?"
            funcs.setdefault(key, {"func": hex(f) if f else None,
                                    "sitios": [], "cadenas": [], "vaddr_cadena": []})
            funcs[key]["sitios"].append(hex(s))
            funcs[key]["cadenas"].append(c["texto"])
            funcs[key]["vaddr_cadena"].append(hex(a))
    for v in funcs.values():
        v["sitios"] = sorted(set(v["sitios"]))

    # --- 4. todas las cadenas referenciadas por cada función emisora
    allstr = {}
    for dest, sites in pairs.items():
        for s in sites:
            f = fstart(s)
            allstr.setdefault(hex(f) if f else "?", set()).add(dest)
    for key, v in funcs.items():
        extra = sorted(hex(x) for x in allstr.get(key, set())
                       if x not in [int(h, 16) for h in v["vaddr_cadena"]])
        v["otras_cadenas"] = [(h, cstr(int(h, 16))) for h in extra]

    # --- 5. llamadores bl
    tg = [int(v["func"], 16) for v in funcs.values() if v["func"]]
    cm = bl_callers(tg)
    for v in funcs.values():
        v["llamadores_bl"] = [hex(x) for x in cm.get(int(v["func"], 16), [])] if v["func"] else []

    # --- 6. expansión textual de la sigla
    expansiones = {}
    for pat in (rb"SAD", rb"SaD", rb"sad", rb"SAD_", rb"_SAD", rb"Sad[A-Za-z]", rb"[Ss]ad\b"):
        hits = []
        for m in re.finditer(pat, B):
            o = m.start()
            s = o
            while s > 0 and B[s - 1] != 0 and 32 <= B[s - 1] < 127:
                s -= 1
            e = B.find(b"\x00", o)
            hits.append({"vaddr": hex(BASE + s), "texto": B[s:e].decode("latin1")[:120]})
        expansiones[pat.decode("latin1")] = hits

    # --- 7. diferencial
    a6000_texts = [c["texto"] for c in cad]
    dif = {}
    for name, path in (("A7S_fw320", A7S), ("A6300_fw201", A63)):
        occ = model_texts(path)
        txt = {t for _, t in occ}
        a = set(a6000_texts)
        dif[name] = {
            "ocurrencias_token": len(occ),
            "cadenas_distintas": len(txt),
            "comunes": sorted(a & txt),
            "solo_a6000": sorted(a - txt),
            "solo_modelo": sorted(txt - a),
        }

    # punteros absolutos de 4 B a las cadenas [SAD]
    abs4 = {c["vaddr"]: [hex(x) for x in abs_pointers(c["vaddr"])] for c in cad}

    out = {
        "milestone": "S167",
        "token": "[SAD]",
        "cadenas": cad,
        "n_cadenas": len(cad),
        "sitios_por_cadena": {hex(c["vaddr"]): [hex(x) for x in sorted(set(pairs.get(c["vaddr"], [])))]
                              for c in cad},
        "pic_detalle": {hex(k): v for k, v in detail.items() if k in [c["vaddr"] for c in cad]},
        "cotejo_mapa_global": {"discrepancias": mismatch,
                               "n_discrepancias": len(mismatch)},
        "funciones": funcs,
        "expansiones_sigla": expansiones,
        "diferencial": dif,
        "punteros_4B_a_cadenas": {hex(k): v for k, v in abs4.items()},
        "totales": {
            "cadenas": len(cad),
            "sitios": sum(len(v) for v in pairs.values() if any(c["vaddr"] == k for k in v)),
            "funciones": len(funcs),
        },
    }
    dest = os.path.join(HERE, "sad_raw.json")
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print("cadenas:", len(cad), "funciones:", len(funcs),
          "sitios:", sum(len(v["sitios"]) for v in funcs.values()))
    for k, v in sorted(funcs.items()):
        print(f"  {k}  sitios={len(v['sitios']):3d}  cadenas={len(v['cadenas'])}")
    print("cotejo mapa global, discrepancias:", len(mismatch))
    for name, d in dif.items():
        print(f"  {name}: token={d['ocurrencias_token']} comunes={len(d['comunes'])} "
              f"solo_a6000={len(d['solo_a6000'])} solo_modelo={len(d['solo_modelo'])}")
    print("escrito", dest)


if __name__ == "__main__":
    main()
