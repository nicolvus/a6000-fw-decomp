#!/usr/bin/env python3
"""S118 — extracción del módulo `[SFRA]` (ScalarInfra) del firmware A6000 fw3.21.

Salidas (en este directorio):
  * `strings_raw.json`  — las 100 trazas con vaddr/offset/texto.
  * `func_map.json`     — función que referencia cada traza (esquema PIC + descent
                          recursivo con capstone para delimitar funciones Thumb).
  * `summary.json`      — sub-bloques, catálogo de comandos, contadores y
                          diferencial con la A7S fw3.20.

Convención: vaddr = 0x43541000 + file_offset.
"""
import json
import os
import re
import struct
from collections import Counter, defaultdict

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
HERE = os.path.dirname(os.path.abspath(__file__))
PREFIX = b"[SFRA]"

# Región de código donde caen los sitios PIC de las trazas [SFRA].
CODE_LO, CODE_HI = 0x4398E000, 0x439B0000


def extract(data):
    out = []
    i = data.find(PREFIX)
    while i >= 0:
        e = i
        while e < len(data) and 32 <= data[e] < 127:
            e += 1
        out.append({"vaddr": f"0x{BASE + i:x}", "off": i,
                    "text": data[i:e].decode("latin1")})
        i = data.find(PREFIX, i + 1)
    return out


# ---------------------------------------------------------------- funciones ---
def _next_insn(md, data, addr):
    off = addr - BASE
    if off < 0 or off + 4 > len(data):
        return None
    for ins in md.disasm(data[off:off + 4], addr, count=1):
        return ins
    return None


def function_ranges(data, lo, hi):
    """Delimita funciones Thumb por descendencia recursiva con capstone.

    Función = `push {..,lr}` ... `pop {..,pc}` / `bx lr`.
    Devuelve [(start, end)] con end exclusivo (último+2).
    """
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    ranges = []
    # candidatos a inicio de función: prólogos y destinos de `bl`
    todo = set()
    a = lo
    while a < hi:
        h = struct.unpack_from("<H", data, a - BASE)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            todo.add(a)
        elif h == 0xE92D:
            h2 = struct.unpack_from("<H", data, a - BASE + 2)[0]
            if h2 & 0x4000:
                todo.add(a)
        a += 2
    pending = sorted(todo)
    seen_starts = set()
    while pending:
        start = pending.pop()
        if start in seen_starts:
            continue
        seen_starts.add(start)
        stack = [start]
        visited = set()
        last = start
        targets = []
        while stack:
            pc = stack.pop()
            if pc in visited:
                continue
            visited.add(pc)
            while True:
                ins = _next_insn(md, data, pc)
                if ins is None:
                    break
                visited.add(ins.address)
                last = max(last, ins.address)
                mn = ins.mnemonic
                op = ins.op_str
                if mn in ("bl", "blx"):
                    try:
                        t = int(op.lstrip("#").split()[0], 16)
                    except ValueError:
                        t = None
                    if t is not None:
                        t &= ~1
                        if t not in seen_starts:
                            targets.append(t)
                        if not (lo <= t < hi):
                            break
                    pc += ins.size
                    continue
                if mn == "b":
                    try:
                        t = int(op.lstrip("#").split()[0], 16)
                    except ValueError:
                        t = None
                    if t is not None:
                        t &= ~1
                        if t in seen_starts or not (lo <= t < hi):
                            break
                        stack.append(t)
                    break
                if mn in ("bx", "pop", "popw", "ldmia", "ldmdb") and (
                        mn == "bx" and "lr" in op or "pc" in op):
                    break
                pc += ins.size
        ranges.append((start, last + 2))
        for t in targets:
            if t not in seen_starts:
                pending.append(t)
    ranges.sort()
    return ranges


def site_to_func(site, ranges):
    best = None
    for s, e in ranges:
        if s <= site < e:
            if best is None or (e - s) < (best[1] - best[0]):
                best = (s, e)
    if best:
        return best[0]
    # sin coincidencia exacta: la función cuyo inicio es el más cercano por detrás
    cands = [s for s, _ in ranges if s <= site]
    return cands[-1] if cands else None


# ------------------------------------------------------------ sub-bloques ----
SUB_RE = re.compile(r"^\[SFRA\](?:\[([A-Z_0-9]+)\])?")


def subblock(text):
    m = SUB_RE.match(text)
    if not m:
        return None
    return m.group(1) or "(sin etiqueta)"


CMD_RE = re.compile(r"\*\*\*(.+?)\*\*\*")


def main():
    data = open(BIN, "rb").read()
    strings = extract(data)
    refs = json.load(open(os.path.join(HERE, "pic_refs_dataflow.json")))
    refs_canon = json.load(open(os.path.join(HERE, "pic_refs.json")))

    ranges = function_ranges(data, CODE_LO, CODE_HI)

    by_func = defaultdict(list)
    sites_total = 0
    for s in strings:
        for site in refs.get(s["vaddr"], []):
            sites_total += 1
            f = site_to_func(site, ranges)
            by_func[f].append({"vaddr": s["vaddr"], "text": s["text"], "site": f"0x{site:x}"})

    # mapa función -> trazas (una entrada por traza y función)
    funcs = []
    for f, items in sorted(by_func.items()):
        uniq = {}
        for it in items:
            uniq.setdefault(it["vaddr"], it)
        funcs.append({"func": f"0x{f:x}", "n_sites": len(items),
                      "n_strings": len(uniq),
                      "strings": [{"vaddr": k, "text": v["text"]} for k, v in sorted(uniq.items())]})

    # sub-bloques
    subs = defaultdict(list)
    for s in strings:
        subs[subblock(s["text"])].append(s)
    sub_rows = []
    for t, ss in sorted(subs.items(), key=lambda kv: -len(kv[1])):
        sub_rows.append({"submodule": t, "n": len(ss),
                         "lo": min(x["vaddr"] for x in ss),
                         "hi": max(x["vaddr"] for x in ss),
                         "sample": [x["text"] for x in ss[:3]]})

    # catálogo de comandos (marcadores *** ... ***)
    cmds = []
    for s in strings:
        m = CMD_RE.search(s["text"])
        if m:
            cmds.append({"name": m.group(1), "vaddr": s["vaddr"], "text": s["text"],
                         "level": "CMD" if "[CMD]" in s["text"] else "CMP",
                         "funcs": sorted({f["func"] for f in funcs
                                          if any(x["vaddr"] == s["vaddr"] for x in f["strings"])})})

    # ficheros fuente embebidos en la zona de cadenas (el grupo del módulo va
    # desde `ScalarInfraAsyncMain.cpp` hasta `DrvCallRc.cpp`)
    lo_s = 0x43CE59FD
    hi_s = BASE + strings[-1]["off"]
    files = []
    for m in re.finditer(rb"[A-Za-z0-9_]{3,40}\.(?:cpp|h|cc)\x00", data):
        va = BASE + m.start()
        if lo_s <= va <= hi_s:
            files.append({"vaddr": f"0x{va:x}", "name": m.group()[:-1].decode()})

    # diferencial A7S
    a7s = open(A7S, "rb").read()
    comunes, solo = [], []
    for s in strings:
        if s["text"].encode() in a7s:
            comunes.append(s["vaddr"])
        else:
            solo.append(s["vaddr"])
    # texto sin prefijo [SFRA]
    sin_prefijo = 0
    for s in strings:
        core = s["text"][len("[SFRA]"):]
        if core.encode() in a7s:
            sin_prefijo += 1

    # diferencial A6300 fw2.01 (texto)
    a6300 = open(A6300, "rb").read()
    solo6300 = []
    i = a6300.find(b"[SFRA")
    seen = set()
    while i >= 0:
        e = i
        while e < len(a6300) and 32 <= a6300[e] < 127:
            e += 1
        t = a6300[i:e].decode("latin1")
        if t not in {x["text"] for x in strings} and t not in seen:
            seen.add(t)
            solo6300.append({"vaddr": f"0x{i:x}", "text": t})
        i = a6300.find(b"[SFRA", i + 1)

    # tabla de comandos (ids de mensaje y de sub-comando)
    cmd_table = []
    p = os.path.join(HERE, "command_table.json")
    if os.path.exists(p):
        cmd_table = json.load(open(p))
    a7s_diff = {}
    p = os.path.join(HERE, "a7s_diff.json")
    if os.path.exists(p):
        a7s_diff = json.load(open(p))

    out = {
        "milestone": "S118",
        "module": "SFRA",
        "base": f"0x{BASE:x}",
        "counts": {
            "strings": len(strings),
            "distinct_texts": len({s["text"] for s in strings}),
            "pic_sites": sites_total,
            "pic_sites_regla_canonica": sum(len(refs_canon.get(s["vaddr"], []))
                                           for s in strings),
            "functions": len(funcs),
            "submodules": len(sub_rows),
            "commands": len(cmds),
            "a7s_exact": len(comunes),
            "a7s_only_a6000": len(solo),
            "a7s_core_without_prefix": sin_prefijo,
            "source_files": len(files),
        },
        "submodules": sub_rows,
        "commands": cmds,
        "command_table": cmd_table,
        "source_files": files,
        "functions": funcs,
        "strings": strings,
        "a7s": a7s_diff,
        "a7s_only_a6000": [s for s in strings if s["vaddr"] in solo],
        "a6300_only": solo6300,
    }
    json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(out, open(os.path.join(HERE, "sfra.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "SFRA", "count": len(strings), "strings": strings},
              open(os.path.join(HERE, "strings_raw.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"module": "SFRA", "functions": funcs},
              open(os.path.join(HERE, "func_map.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out["counts"], indent=1))
    print("sub-bloques:", [(r["submodule"], r["n"]) for r in sub_rows])
    print("comandos:")
    for c in cmds:
        print("  ", c["level"], c["name"], c["vaddr"], c["funcs"])
    print("funciones:", [(f["func"], f["n_sites"]) for f in funcs])
    print("ficheros fuente:", [f["name"] for f in files])
    print("solo A6000:", [s["vaddr"] for s in out["a7s_only_a6000"]])


if __name__ == "__main__":
    main()
