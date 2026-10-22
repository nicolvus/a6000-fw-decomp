#!/usr/bin/env python3
"""S137 — el token `[CTRLCORE]` en el firmware de la A6000 fw3.21.

Qué hace:
  1. extrae las 55 cadenas que contienen `[CTRLCORE]` (con su inicio real de cadena);
  2. las agrupa por el prefijo de módulo que las contiene (`[CDIAG]`, `[MCSENS]`, `[AMSENS]`);
  3. toma los sitios PIC de la regla **estricta** ya calculados en
     `analysis/s106_imaging_cap/pic_refs_strict_global.json` (destino → sitios `add rX,pc`);
  4. atribuye cada sitio a su función (prólogo Thumb `push {..,lr}` más cercano por detrás);
  5. calcula los llamadores `bl` directos de cada función (barrido Capstone de todo el código);
  6. busca punteros absolutos de 4 B a las cadenas y a los nombres RTTI `*CtrlCore`;
  7. compara texto a texto con la A7S fw3.20 y el A6300 fw2.01.

Salida: analysis/s137_ctrlcore/ctrlcore_raw.json (datos crudos; el informe usa ctrlcore.json).
"""
import bisect
import json
import os
import re
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A63 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GLOBAL = os.path.join(ROOT, "analysis", "s106_imaging_cap", "pic_refs_strict_global.json")

CODE_LO, CODE_HI = 0x43541000, 0x43A00000


def strings_with(token):
    """[(inicio_cadena, offset_del_token, texto)] para cada ocurrencia de `token`."""
    b = open(os.path.join(ROOT, BIN), "rb").read()
    out = []
    for m in re.finditer(re.escape(token), b):
        s = m.start()
        while s > 0 and b[s - 1] != 0 and 32 <= b[s - 1] < 127:
            s -= 1
        e = b.find(b"\0", m.start())
        out.append((BASE + s, BASE + m.start(), b[s:e].decode("latin1")))
    return out


def prologues(b, lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = struct.unpack_from("<H", b, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = struct.unpack_from("<H", b, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def callers(b, targets):
    """{destino: [sitios]} con decodificación manual del patrón `bl`/`b.w` de 32 bits.

    No se usa desensamblado lineal: en zonas con datos intercalados Capstone se
    desincroniza y pierde llamadas (comprobado: perdía todos los `bl` a
    `0x435a1b64`). El patrón de bits 11110...11...1 es inequívoco y se busca en
    todas las fronteras de media palabra del rango de código.
    """
    out = {t: [] for t in targets}
    tset = set(targets)
    for a in range(CODE_LO, CODE_HI - 4, 2):
        h1 = struct.unpack_from("<H", b, a - BASE)[0]
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = struct.unpack_from("<H", b, a - BASE + 2)[0]
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


def abs_pointers(b, va):
    pat = struct.pack("<I", va)
    return [BASE + m.start() for m in re.finditer(re.escape(pat), b)]


def module_of(text):
    m = re.match(r"(?:\[ERR\])?(\[[A-Z0-9_]+\])", text)
    return m.group(1) if m else None


def fmt_free(text):
    """Texto sin especificadores de formato (para comparar entre firmwares)."""
    return re.sub(r"%[-#0-9.lh]*[a-zA-Z]", "%", text)


def diff(model_path, a6000_texts, token):
    b = open(os.path.join(ROOT, model_path), "rb").read()
    tb = token.encode()
    occ = [BASE + m.start() for m in re.finditer(re.escape(tb), b)]
    texts = set()
    for i in re.finditer(re.escape(tb), b):
        s = i.start()
        while s > 0 and b[s - 1] != 0 and 32 <= b[s - 1] < 127:
            s -= 1
        e = b.find(b"\0", i.start())
        texts.add(b[s:e].decode("latin1"))
    a = set(a6000_texts)
    return {
        "ocurrencias_token": len(occ),
        "textos": len(texts),
        "comunes": sorted(a & texts),
        "solo_a6000": sorted(a - texts),
        "solo_modelo": sorted(texts - a),
    }


def main():
    b = open(os.path.join(ROOT, BIN), "rb").read()
    g = json.load(open(GLOBAL))

    occ = strings_with(b"[CTRLCORE]")
    starts = sorted({s for s, _, _ in occ})
    strs = []
    for s in starts:
        text = [t for ss, _, t in occ if ss == s][0]
        strs.append({"vaddr": hex(s), "modulo": module_of(text), "texto": text})

    sites = {}
    for s in starts:
        sites[hex(s)] = [hex(x) for x in g.get(hex(s), [])]

    P = prologues(b, CODE_LO, CODE_HI)

    def fstart(site):
        i = bisect.bisect_right(P, site) - 1
        return P[i] if i >= 0 else None

    funcs = {}
    for s in starts:
        ss = g.get(hex(s), [])
        fs = sorted({fstart(x) for x in ss})
        for f in fs:
            funcs.setdefault(hex(f), {"sitios": [], "cadenas": []})
            funcs[hex(f)]["cadenas"].append(hex(s))
        for x in ss:
            funcs[hex(fstart(x))]["sitios"].append(hex(x))

    tgt = [int(k, 16) for k in funcs]
    callers_map = callers(b, tgt)
    for k, v in funcs.items():
        v["llamadores_bl"] = [hex(x) for x in callers_map[int(k, 16)]]

    # piezas del subsistema que no emiten cadenas pero lo gobiernan
    extra = [0x435A1424, 0x435A15E8, 0x435A157C, 0x435A1B18, 0x435A1A68, 0x43A48C6A, 0x43A48C80]
    extra_map = callers(b, extra)

    # punteros absolutos de 4 B a las cadenas y a los nombres RTTI
    rtti = {}
    for name in ("CdCtrlCore", "McSensCtrlCore", "McAvCtrlCore", "AmSensCtrlCore", "CdExtCtrlCore"):
        va = BASE + b.find(name.encode())
        if va == BASE - 1:
            continue
        rtti[name] = {"vaddr": hex(va), "punteros_4B": [hex(x) for x in abs_pointers(b, va)]}

    abs_str = {hex(s): [hex(x) for x in abs_pointers(b, s)] for s in starts}

    texts = [t for _, _, t in occ]
    out = {
        "token": "[CTRLCORE]",
        "ocurrencias": len(occ),
        "cadenas": strs,
        "sitios": sites,
        "funciones": funcs,
        "rtti": rtti,
        "punteros_4B_a_cadenas": abs_str,
        "totales": {
            "cadenas": len(starts),
            "sitios": sum(len(v) for v in sites.values()),
            "funciones": len(funcs),
        },
        "diferencial": {
            "A7S_fw320": diff(A7S, texts, "[CTRLCORE]"),
            "A6300_fw201": diff(A63, texts, "[CTRLCORE]"),
        },
        "llamadores_extra": {hex(k): [hex(x) for x in v] for k, v in extra_map.items()},
        "variantes_nombre": {
            k: len(re.findall(k.encode(), b))
            for k in ("CdCtrlCore", "McSensCtrlCore", "McAvCtrlCore", "AmSensCtrlCore")
        },
        "ficheros_fuente": {
            name: hex(BASE + b.find(name.encode()))
            for name in ("cdCtrlCore.cpp", "mcSensCtrlCore.cpp", "mcAvCtrlCore.cpp", "amSensCtrlCore.cpp")
        },
    }
    with open(os.path.join(HERE, "ctrlcore_raw.json"), "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps(out["totales"], ensure_ascii=False))
    print({k: len(v) for k, v in out["diferencial"].items()})
    for k, v in out["ficheros_fuente"].items():
        print(k, v)


if __name__ == "__main__":
    main()
