#!/usr/bin/env python3
"""S109 — reconstrucción del módulo `[CDIAG]` (270 trazas) del firmware A6000 fw3.21.

Salida: analysis/s109_cdiag/cdiag.json

Pasos:
 1. Extraer las 270 apariciones del token `[CDIAG]` con la cadena que las contiene.
 2. Agrupar las que *empiezan* por `[CDIAG]` por su etiqueta de 2º nivel
    ([TSK], [TSKCORE], [CTRLIF], [CTRLCORE], [CTRLHDDEC], ...) y calcular rangos.
 3. Localizar las referencias PIC (ldr rX,[pc,#imm] + add rX,pc) a cada cadena y
    asignarlas a la función que las contiene, delimitada por
    `push {..,lr}` … `pop {..,pc}` (con capstone para resolver los prólogos
    "hoisted" en los que el push no es la primera instrucción).
 4. Extraer las cadenas `CDIAGER <firma C++>` (nombres de función embebidos), los
    nombres de clase (`11CdCtrlHdDec`) y los ficheros fuente (`cdCtrlCore.cpp`).
 5. Diferencial con la A7S fw3.20 y la A6300 fw2.01.

Todo es lectura de bytes; no se ejecuta el firmware.
"""
import bisect
import json
import os
import re
import struct
import sys

import capstone

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")

STR_LO, STR_HI = 0x43C24000, 0x43D10000
MAX_LDR_GAP = 4096
CODE_LO, CODE_HI = 0x43580000, 0x435C0000

B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
MD = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)


def u16(v):
    o = v - BASE
    return U16(B, o)[0] if 0 <= o <= N - 2 else None


def u32(v):
    o = v - BASE
    return U32(B, o)[0] if 0 <= o <= N - 4 else None


def cstr(v, maxlen=300):
    o = v - BASE
    if o < 0 or o >= N:
        return None
    e = o
    while e < N and e < o + maxlen and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1")


# --------------------------------------------------------------- cadenas
def cdiag_occurrences():
    """[(vaddr_token, vaddr_cadena, texto)] de cada token `[CDIAG]`."""
    out = []
    start = 0
    while True:
        i = B.find(b"[CDIAG]", start)
        if i < 0:
            break
        # retrocede hasta el inicio de la cadena imprimible
        s = i
        while s > 0 and 32 <= B[s - 1] < 127:
            s -= 1
        out.append((BASE + i, BASE + s, cstr(BASE + s)))
        start = i + 1
    return out


def string_starts(lo, hi):
    o0, o1 = lo - BASE, hi - BASE
    out = set()
    prev = False
    for i in range(o0, o1):
        cur = 32 <= B[i] < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


# --------------------------------------------------------------- PIC
def ldr_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 8:
            continue
        h = U16(B, o)[0]
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        else:
            continue
        o2 = lit - BASE
        if 0 <= o2 <= N - 4:
            out.append((a, reg, U32(B, o2)[0]))
    return out


def add_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 4:
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
    return out


def scan_pic(lo, hi, starts):
    """Para cada `add rX,pc` se toma el `ldr rX,[pc,#imm]` **más cercano por detrás**
    (mismo registro).  No se sigue buscando hacia atrás si el resultado no es una
    cadena: el registro se reutiliza y eso produciría falsos positivos."""
    ldrs = ldr_sites(lo, hi)
    adds = add_sites(lo, hi)
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
        i = bisect.bisect_right(ks, a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > MAX_LDR_GAP:
            continue
        tgt = (w + (a + 4)) & 0xFFFFFFFF
        if tgt in starts:
            out.setdefault(tgt, []).append(a)
    return out


# --------------------------------------------------- límites de función
def return_sites(lo, hi):
    """Direcciones de `pop {..,pc}` (16 y 32 bits) y `bx lr`."""
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 4:
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0xBD00 and (h & 0x0100):     # pop {..,pc}
            out.append(a)
        elif h == 0xE8BD:                               # pop.w {..,pc}
            out.append(a)
        elif h == 0x4770:                                # bx lr
            out.append(a)
    return out


def push_sites(lo, hi):
    """Prólogos: `push {...,lr}` (16 bits) y `push.w {...,lr}` (32 bits).

    En los dos casos el bit 14 de la lista de registros es `lr`.
    """
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 4:
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):     # push {..,lr}
            if U16(B, o + 2)[0] & 0x4000:               # el registro lr
                out.append(a)
        elif h == 0xE92D:                               # push.w {..,lr}
            if U16(B, o + 2)[0] & 0x4000:
                out.append(a)
    return out


def build_functions(lo, hi):
    """Devuelve (rets, pushes) indexados para resolver la función de un sitio."""
    rets = return_sites(lo, hi)
    psh = push_sites(lo, hi)
    return rets, psh


def function_of(site, psh, rets):
    """(start, end, push) de la función que contiene `site`.

    Regla: la función termina en el primer retorno posterior al sitio.  Su
    prólogo es el último `push {..,lr}` anterior a ese retorno; si el prólogo
    está *después* del sitio (el compilador "hoistea" el cálculo de una
    dirección global antes del `push`), el inicio de la función se extiende
    hasta el retorno anterior.
    """
    i = bisect.bisect_left(rets, site)
    if i >= len(rets):
        return None
    end = rets[i]
    j = bisect.bisect_right(psh, end) - 1
    if j < 0:
        return None
    push = psh[j]
    if push <= site:
        return (push, end, push)
    # prólogo hoisteado: la función empieza tras el retorno anterior
    k = bisect.bisect_left(rets, push) - 1
    if k < 0:
        return None
    start = rets[k] + 2
    if start > site:
        return None
    return (start, end, push)


# ------------------------------------------------------------------ main
def main():
    occ = cdiag_occurrences()
    starts = string_starts(STR_LO, STR_HI)
    pic = scan_pic(BASE, BASE + N, starts)
    rets, psh = build_functions(CODE_LO, CODE_HI)

    tag_re = re.compile(r"^\[CDIAG\]\[([A-Z0-9_]+)\]")

    # --- cadenas que empiezan por [CDIAG]
    items = []
    for tok_v, str_v, text in occ:
        if text.startswith("[CDIAG]"):
            m = tag_re.match(text)
            items.append({
                "token_vaddr": f"0x{tok_v:x}",
                "vaddr": f"0x{str_v:x}",
                "tag": m.group(1) if m else "?",
                "text": text,
                "pic_sites": [f"0x{s:x}" for s in sorted(set(pic.get(str_v, [])))],
            })
    for it in items:
        fns = []
        for s in it["pic_sites"]:
            sv = int(s, 16)
            f = function_of(sv, psh, rets)
            if f:
                fns.append({"ref_site": s, "func_start": f"0x{f[0]:x}",
                            "func_end": f"0x{f[1]:x}",
                            "push": f"0x{f[2]:x}" if f[2] else None})
        it["functions"] = fns

    # --- cadenas con el token [CDIAG] pero con prefijo [ERR]
    err_items = []
    for tok_v, str_v, text in occ:
        if text.startswith("[CDIAG]"):
            continue
        sites = sorted(set(pic.get(str_v, [])))
        fns = []
        for s in sites:
            f = function_of(s, psh, rets)
            if f:
                fns.append({"ref_site": f"0x{s:x}", "func_start": f"0x{f[0]:x}",
                            "func_end": f"0x{f[1]:x}"})
        err_items.append({"token_vaddr": f"0x{tok_v:x}", "vaddr": f"0x{str_v:x}",
                           "text": text,
                           "pic_sites": [f"0x{s:x}" for s in sites],
                           "functions": fns})

    # --- sub-bloques
    blocks = {}
    for it in items:
        b = blocks.setdefault(it["tag"], {"tag": it["tag"], "count": 0,
                                         "vaddr_min": int(it["vaddr"], 16),
                                         "vaddr_max": int(it["vaddr"], 16),
                                         "strings": []})
        v = int(it["vaddr"], 16)
        b["count"] += 1
        b["vaddr_min"] = min(b["vaddr_min"], v)
        b["vaddr_max"] = max(b["vaddr_max"], v)
        b["strings"].append({"vaddr": it["vaddr"], "text": it["text"]})

    # --- firmas CDIAGER
    sigs = []
    for m in re.finditer(rb"CDIAGER [ -~]{3,}", B):
        v = BASE + m.start()
        if not (0x43C3B000 <= v <= 0x43C3F000):
            continue
        txt = m.group().decode("latin1")
        sites = sorted(set(pic.get(v, [])))
        fns = []
        for s in sites:
            f = function_of(s, psh, rets)
            if f:
                fns.append({"ref_site": f"0x{s:x}", "func_start": f"0x{f[0]:x}",
                            "func_end": f"0x{f[1]:x}"})
        sigs.append({"vaddr": f"0x{v:x}", "text": txt,
                     "pic_sites": [f"0x{s:x}" for s in sites], "functions": fns})

    # --- clases y ficheros fuente
    classes, srcfiles = [], []
    for m in re.finditer(rb"\d{1,3}[A-Z][A-Za-z0-9_]{3,40}\x00", B):
        v = BASE + m.start()
        if 0x43C3B000 <= v <= 0x43C3F000:
            s = m.group()[:-1].decode("latin1")
            if re.match(r"^\d+[A-Z]", s):
                classes.append({"vaddr": f"0x{v:x}", "text": s})
    for m in re.finditer(rb"[A-Za-z0-9_]{2,40}\.(?:cpp|h)\x00", B):
        v = BASE + m.start()
        if 0x43C3B000 <= v <= 0x43C3F000:
            srcfiles.append({"vaddr": f"0x{v:x}", "text": m.group()[:-1].decode()})

    # --- diferencial
    diff = {}
    toks = ["SENS_MODE_PROC_START", "SENS_RUN_CODEC", "SENS_CMP_DATA",
            "SENS_SET_DIAG_MODE", "cdCtrlCore.cpp", "cdCtrlIf.cpp",
            "DbgDiagAvc", "ClkState IDLE->OPEN", "VideoES Differ!!",
            "JPEG ENC FAILED !!", "Scenario END", "CDIAGER",
            "CdCtrlCore", "CdCtrlHdRec", "cdMsgCore", "cdTskCore"]
    for model, path in (("A7S_fw320", A7S), ("A6300_fw201", A6300)):
        if not os.path.exists(path):
            diff[model] = {"available": False}
            continue
        blob = open(path, "rb").read()
        base7 = 0x43541000
        occ7 = []
        s = 0
        while True:
            i = blob.find(b"[CDIAG]", s)
            if i < 0:
                break
            occ7.append(base7 + i)
            s = i + 1
        diff[model] = {
            "available": True,
            "path": path,
            "count_cdiag_token": len(occ7),
            "token_vaddr_min": f"0x{min(occ7):x}" if occ7 else None,
            "token_vaddr_max": f"0x{max(occ7):x}" if occ7 else None,
            "tokens": {t: blob.count(t.encode()) for t in toks},
        }

    # --- agregado por clase
    TAG2CLS = {"TSK": "CdTskCore", "TSKCORE": "CdTskCore",
               "CTRLIF": "CdCtrlIf", "CTRLCORE": "CdCtrlCore",
               "CTRLHDDEC": "CdCtrlHdDec", "CTRLHDREC": "CdCtrlHdRec",
               "CTRLJPGDEC": "CdCtrlJpgDec", "CTRLJPGENC": "CdCtrlJpgEnc",
               "CTRLJPGENCDEC": "CdCtrlJpgEncDec",
               "CTRLSDDEC": "CdCtrlSdDec", "CTRLSDREC": "CdCtrlSdRec",
               "CMPDATA": "CdUtilCmpData"}
    agg = {}
    for it in items:
        cls = TAG2CLS.get(it["tag"], "?")
        a = agg.setdefault(cls, {"class": cls, "count": 0, "tags": set(),
                                 "vaddr_min": 0xFFFFFFFF, "vaddr_max": 0,
                                 "funcs": set(), "code_min": 0xFFFFFFFF,
                                 "code_max": 0})
        v = int(it["vaddr"], 16)
        a["count"] += 1
        a["tags"].add(it["tag"])
        a["vaddr_min"] = min(a["vaddr_min"], v)
        a["vaddr_max"] = max(a["vaddr_max"], v)
        for f in it["functions"]:
            a["funcs"].add((f["func_start"], f["func_end"]))
            a["code_min"] = min(a["code_min"], int(f["func_start"], 16))
            a["code_max"] = max(a["code_max"], int(f["func_end"], 16))
    by_class = []
    for cls, a in sorted(agg.items()):
        fs = sorted(a["funcs"], key=lambda x: int(x[0], 16))
        by_class.append({
            "class": cls,
            "tags": sorted(a["tags"]),
            "count_strings": a["count"],
            "strings_vaddr_min": f"0x{a['vaddr_min']:x}",
            "strings_vaddr_max": f"0x{a['vaddr_max']:x}",
            "n_functions": len(fs),
            "code_vaddr_min": f"0x{a['code_min']:x}" if fs else None,
            "code_vaddr_max": f"0x{a['code_max']:x}" if fs else None,
            "functions": [{"start": s, "end": e} for s, e in fs],
        })

    out = {
        "milestone": "S109",
        "model": "A6000",
        "firmware": "fw3.21",
        "base_vaddr": f"0x{BASE:x}",
        "bin": BIN,
        "count_cdiag_token": len(occ),
        "count_strings_starting_with_prefix": len(items),
        "count_strings_with_ERR_prefix": len(occ) - len(items),
        "range": [f"0x{min(int(i['vaddr'],16) for i in items):x}",
                  f"0x{max(int(i['vaddr'],16) for i in items):x}"],
        "by_class": by_class,
        "subblocks": [
            {"tag": b["tag"], "count": b["count"],
             "vaddr_min": f"0x{b['vaddr_min']:x}",
             "vaddr_max": f"0x{b['vaddr_max']:x}",
             "strings": b["strings"]}
            for b in sorted(blocks.values(), key=lambda x: x["vaddr_min"])
        ],
        "strings": items,
        "err_strings": err_items,
        "function_signatures": sigs,
        "class_names": classes,
        "source_files": srcfiles,
        "differential": diff,
    }
    dest = "analysis/s109_cdiag/cdiag.json"
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)

    print(f"tokens [CDIAG]: {len(occ)}   cadenas que empiezan por [CDIAG]: {len(items)}")
    for b in sorted(blocks.values(), key=lambda x: x["vaddr_min"]):
        print(f"  {b['tag']:14s} {b['count']:4d}  {hex(b['vaddr_min'])}-{hex(b['vaddr_max'])}")
    print("firmas CDIAGER:", len(sigs), " clases:", len(classes), " ficheros:", len(srcfiles))
    noref = [i for i in items if not i["pic_sites"]]
    print("cadenas sin referencia PIC:", len(noref))
    print("escrito", dest)


if __name__ == "__main__":
    sys.exit(main())
