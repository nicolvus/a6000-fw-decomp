#!/usr/bin/env python3
"""S119 — genera `analysis/s119_apl/apl.json` (datos estructurados del modulo `[APL]`).

Entrada: recalcula el mapa PIC de la A6000 (regla estricta y canonica) y reutiliza
`apl_a7s_map.json` (A7S fw3.20) y `callers.json` (call sites de las funciones).
Salida : apl.json
"""
import json
import os
import re
import struct
from collections import defaultdict

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
A6300 = os.path.join(ROOT, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
MAX_GAP = 4096
CODE_LO, CODE_HI = BASE, 0x43C90000
MODULE = "[APL]"

B = open(BIN, "rb").read()
N = len(B)

# Las 5 funciones emisoras (verificadas por desensamblado: prologo + `pop {..,pc}`)
APL_FUNCS = {
    "0x439cea30": "APL Open (HW + SA + InputPrm)",
    "0x439cebe4": "APL Close (7 handles + SA + HW)",
    "0x439cedd0": "APL Free & Close (InputPrm)",
    "0x439ceeb8": "APL Open + ejecucion (GetMemInfo/MMU/HW SetMode)",
    "0x439cf3b8": "APL SA open/close (ExecuteOpenMSG/ExecuteCloseMSG)",
}


def cstr(a):
    o = a - BASE
    if o < 0 or o >= N:
        return None
    e = o
    while e < N and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1") if e > o else None


def starts():
    out = set()
    prev = False
    for i in range(N):
        cur = 32 <= B[i] < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


def ldr_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 8:
            continue
        h = struct.unpack_from("<H", B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = struct.unpack_from("<H", B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
            lit = ((a + 4) & ~3) + imm12
        if reg is None:
            continue
        o2 = lit - BASE
        if 0 <= o2 <= N - 4:
            out.append((a, reg, struct.unpack_from("<I", B, o2)[0]))
    return out


def add_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 4:
            continue
        h = struct.unpack_from("<H", B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
    return out


def prologues(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 4:
            break
        h = struct.unpack_from("<H", B, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            continue
        if h == 0xE92D:
            h2 = struct.unpack_from("<H", B, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
    return out


LEAF_API = {0x43ae071a, 0x43ae0752, 0x43ae073a, 0x43ae1eee, 0x43b65f4c,
            0x43902718, 0x439ce984, 0x43b6d5ac, 0x43b6d5b4}


def bl_targets(lo, hi, valid=None):
    """Destinos de `bl` Thumb en el rango (scan del encoding, no desensamblado lineal)."""
    out = []
    for i in range(lo - BASE, hi - BASE - 4, 2):
        hw1 = struct.unpack_from("<H", B, i)[0]
        if (hw1 & 0xF800) != 0xF000:
            continue
        hw2 = struct.unpack_from("<H", B, i + 2)[0]
        if (hw2 & 0xD000) != 0xD000:
            continue
        S = (hw1 >> 10) & 1
        I1 = (~(((hw2 >> 13) & 1) ^ S)) & 1
        I2 = (~(((hw2 >> 11) & 1) ^ S)) & 1
        imm = (S << 24) | (I1 << 23) | (I2 << 22) | ((hw1 & 0x3FF) << 12) | ((hw2 & 0x7FF) << 1)
        if S:
            imm -= (1 << 25)
        addr = BASE + i
        tgt = (addr + 4 + imm) & 0xFFFFFFFF
        if valid is not None and tgt not in valid:
            continue
        out.append((addr, tgt))
    return out


def main():
    st = starts()
    ldrs = ldr_sites(CODE_LO, CODE_HI)
    adds = add_sites(CODE_LO, CODE_HI)
    by_reg = defaultdict(list)
    for a, reg, w in ldrs:
        by_reg[reg].append((a, w))
    for v in by_reg.values():
        v.sort()

    canon = defaultdict(list)
    strict = defaultdict(list)
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        best = None
        for la, w in reversed(v):
            if la > a or a - la > MAX_GAP:
                continue
            tgt = (w + (a + 4)) & 0xFFFFFFFF
            if best is None:
                best = (tgt, la)
            if tgt in st:
                canon[tgt].append(a)
        if best and best[0] in st:
            strict[best[0]].append((a, best[1]))

    cands = sorted(prologues(CODE_LO, CODE_HI))

    def func_of(site):
        import bisect
        i = bisect.bisect_right(cands, site) - 1
        while i >= 0:
            c = cands[i]
            if site - c > 0x4000:
                break
            limit = cands[i + 1] if i + 1 < len(cands) else c + 0x4000
            if site < limit:
                return c
            i -= 1
        return None

    # trazas [APL]
    traces = []
    i = 0
    while True:
        i = B.find(MODULE.encode(), i)
        if i < 0:
            break
        e = i
        while e < N and 32 <= B[e] < 127:
            e += 1
        s = i
        while s > 0 and 32 <= B[s - 1] < 127:
            s -= 1
        full = BASE + s
        tag = BASE + i
        text = B[s:e].decode("latin1")
        core = text
        prefix = ""
        for p in ("[CAMERA_SA]: ", "[APL]: "):
            if text.startswith(p):
                prefix, core = p, text[len(p):]
                break
        traces.append({"vaddr_full": full, "vaddr_tag": tag, "text": text,
                       "core": core, "prefix": prefix, "off": s})
        i += 1
    seen = set()
    uniq = []
    for t in traces:
        if t["vaddr_full"] in seen:
            continue
        seen.add(t["vaddr_full"])
        uniq.append(t)

    for t in uniq:
        a = t["vaddr_full"]
        ss = sorted({(x[0], func_of(x[0])) for x in strict.get(a, [])})
        cs = sorted({(x, func_of(x)) for x in canon.get(a, [])})
        t["strict_sites"] = [{"site": f"0x{s:x}", "func": (f"0x{f:x}" if f else None)}
                             for s, f in ss]
        t["canon_sites"] = [{"site": f"0x{s:x}", "func": (f"0x{f:x}" if f else None)}
                            for s, f in cs]
        t["funcs"] = sorted({x["func"] for x in t["strict_sites"] if x["func"]})

    # mapa funcion -> trazas (regla estricta)
    fmap = defaultdict(list)
    for t in uniq:
        for x in t["strict_sites"]:
            fmap[x["func"]].append(t)
    functions = []
    for f, ts in sorted(fmap.items(), key=lambda kv: -len(kv[1])):
        functions.append({
            "func": f,
            "role": APL_FUNCS.get(f, ""),
            "n_traces": len(ts),
            "traces": [{"vaddr_tag": f"0x{t['vaddr_tag']:x}",
                        "vaddr_full": f"0x{t['vaddr_full']:x}",
                        "text": t["text"], "core": t["core"],
                        "site": x["site"]}
                       for t in ts for x in t["strict_sites"] if x["func"] == f],
        })

    # sub-bloques: particion exacta y disjunta de las 42 trazas
    FAMILIES = [
        ("HW Open/Close", [r"^HW Open Err", r"^HW Close Err"]),
        ("SA Open/Close", [r"^SA Open Err", r"^SA Close Err"]),
        ("Handles: Open/Close/Free", [r"^Open Err", r"^Close Err", r"^Free & Close Err"]),
        ("Rollback SA & HW", [r"^SA & HW Close Err"]),
        ("InputPrm", [r"InputPrm"]),
        ("GetMemInfo", [r"^GetMemInfo Err"]),
        ("Direcciones de memoria (HME/Work/Vec/Result)",
         [r"^`(HME_[A-Za-z_]+|Work_Addr|Vec_Addr|Result_Addr)' invalid"]),
        ("GetZimaNo", [r"^GetZimaNo Err"]),
        ("Programacion HW/MMU", [r"^HW GetCoreNum Err", r"^HW SetMode Err",
                                 r"^MmuMakeParam Err", r"^HW Abort Err"]),
        ("Ejecucion", [r"^HW TimeOut", r"^Output Ref Img"]),
    ]
    blocks = []
    assigned = set()
    for name, pats in FAMILIES:
        rows = []
        for t in uniq:
            if t["vaddr_full"] in assigned:
                continue
            core = t["core"][len("[APL] "):] if t["core"].startswith("[APL] ") else t["core"]
            if any(re.search(p, core) for p in pats):
                rows.append(t)
                assigned.add(t["vaddr_full"])
        if not rows:
            continue
        blocks.append({"name": name, "n": len(rows),
                       "vaddr_lo": f"0x{min(t['vaddr_tag'] for t in rows):x}",
                       "vaddr_hi": f"0x{max(t['vaddr_tag'] for t in rows):x}",
                       "traces": [f"0x{t['vaddr_tag']:x}" for t in rows]})
    sin_asignar = [f"0x{t['vaddr_tag']:x}" for t in uniq if t["vaddr_full"] not in assigned]

    # API llamada por cada funcion (bl) — el rango acaba en el `pop {..,pc}` final
    ends = {"0x439cea30": 0x439ceb9c, "0x439cebe4": 0x439ced7e,
            "0x439cedd0": 0x439cee8e, "0x439ceeb8": 0x439cf38c,
            "0x439cf3b8": 0x439cf428}
    api = {}
    valid = set(prologues(CODE_LO, CODE_HI)) | LEAF_API
    for f, e in ends.items():
        api[f] = [{"site": f"0x{s:x}", "target": f"0x{t:x}"}
                  for s, t in bl_targets(int(f, 16), e, valid)]

    callers = json.load(open(os.path.join(HERE, "callers.json")))
    a7s = json.load(open(os.path.join(HERE, "apl_a7s_map.json")))
    a7s_txt = {t["text"] for t in a7s["traces"]}
    a6300 = open(A6300, "rb").read()
    a6300_txt = set()
    for m in re.finditer(rb"\[APL\]", a6300):
        e = m.start()
        while e < len(a6300) and 32 <= a6300[e] < 127:
            e += 1
        a6300_txt.add(a6300[m.start():e].decode("latin1"))

    cores = {t["core"] for t in uniq}
    diff = {
        "a6000_fw321": {"n": len(uniq), "prefix": "[CAMERA_SA]: ",
                        "range": [f"0x{min(t['vaddr_full'] for t in uniq):x}",
                                  f"0x{max(t['vaddr_full'] for t in uniq):x}"]},
        "a7s_fw320": {"n": len(a7s["traces"]), "prefix": "",
                      "range": [a7s["traces"][0]["vaddr_full"], a7s["traces"][-1]["vaddr_full"]],
                      "funcs": a7s["funcs"]},
        "a6300_fw201": {"n": len(a6300_txt)},
        "comunes_texto_a_texto_a7s": len(cores & a7s_txt),
        "solo_a6000_vs_a7s": sorted(cores - a7s_txt),
        "solo_a7s": sorted(a7s_txt - cores),
        "comunes_texto_a_texto_a6300": len(cores & a6300_txt),
        "solo_a6000_vs_a6300": sorted(cores - a6300_txt),
    }
    # falsos positivos de la regla canonica (verificados por desensamblado)
    fp = []
    for t in uniq:
        sset = {x["site"] for x in t["strict_sites"]}
        for x in t["canon_sites"]:
            if x["site"] not in sset:
                fp.append({"trace": f"0x{t['vaddr_tag']:x}", "text": t["core"],
                           "false_site": x["site"], "canon_func": x["func"]})

    out = {
        "milestone": "S119",
        "module": "[APL]",
        "firmware": "A6000 fw3.21",
        "base_vaddr": "0x43541000",
        "counts": {
            "traces": len(uniq),
            "functions": len(functions),
            "subblocks": len(blocks),
            "traces_with_pic_ref": sum(1 for t in uniq if t["strict_sites"]),
            "canon_rule_extra_pairs": len(fp),
            "traces_sin_subbloque": len(sin_asignar),
        },
        "strings": [{**{k: v for k, v in t.items() if k != "off"},
                      "vaddr_full": f"0x{t['vaddr_full']:x}",
                      "vaddr_tag": f"0x{t['vaddr_tag']:x}"} for t in uniq],
        "functions": functions,
        "subblocks": blocks,
        "traces_sin_subbloque": sin_asignar,
        "api_calls": api,
        "callers": callers,
        "differential": diff,
        "canon_false_positives": fp,
        "source_files": {
            "embedded_for_apl_module": [],
            "note": ("Las 42 trazas [APL] no incluyen `file=%s line=%d` ni el nombre de "
                     "ningun .cpp; el modulo no registra su fichero de origen. Los nombres "
                     "mas proximos en la zona de datos son Stage_Apollo.cpp 0x43cc6e0f y "
                     "Apollo.cpp 0x43cc6e15 (ambos de [IMAGING_CAP]/Stage_Apollo, S106) y "
                     "ScalarInfraSuperStableMovieManager.cpp 0x43ceb0aa (bloque [SFRS])."),
        },
    }
    json.dump(out, open(os.path.join(HERE, "apl.json"), "w"), indent=1,
              ensure_ascii=False)
    print(json.dumps(out["counts"], indent=1))
    print("bloques:", [(b["name"], b["n"]) for b in blocks])
    print("falsos positivos canonicos:", len(fp))
    print("diferencial:", json.dumps(diff, indent=1))


if __name__ == "__main__":
    main()
