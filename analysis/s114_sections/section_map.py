#!/usr/bin/env python3
"""S114 — identifica las 17 secciones del motor de captura (tabla de 0x43ff8fb4).

Cada entrada de la tabla es {id de sección u32, manejador u32}. El despachador
(`SectionController.cpp`) copia 0x88 B y llama al manejador del id pedido; cada
manejador devuelve un bloque de 20 B (5 u32) con los parámetros de la sección.

Cada *selector* de etapa se identifica por el nombre de fichero que su código
registra (`Capture<Etapa>_Selector.cpp`). 14 de los 17 manejadores registran el
nombre de su propia etapa; los 3 restantes (`0x00`, `0x01`, `0x06`) se identifican
por el hecho de que **llaman** a la función que registra el nombre de una etapa
que ningún manejador registra (`CapturePrelight`, `SequenceFilter`).

Método:
  * referencias PIC (ver `analysis/s106_imaging_cap/scan_pic_refs.py`):
    destino = literal_del_pool + (add rX,pc + 4);
  * inicio de función: prólogo Thumb `push {..,lr}` (0xb5xx) o `push.w {..,lr}`
    (0xE92D + 2ª mitad con bit 14);
  * llamadas: `bl`/`blx` leídos con capstone.
"""
import json
import os
import re
import struct
from collections import defaultdict

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
TABLE = 0x43FF8FB4
N = 17
HERE = os.path.dirname(os.path.abspath(__file__))
S106 = os.path.join(os.path.dirname(HERE), "s106_imaging_cap")

B = open(BIN, "rb").read()


def u32(a):
    return struct.unpack("<I", B[a - BASE:a - BASE + 4])[0]


def u16(a):
    return struct.unpack("<H", B[a - BASE:a - BASE + 2])[0]


def table():
    return [(u32(TABLE + i * 8), u32(TABLE + i * 8 + 4) & ~1) for i in range(N)]


def prologues(lo=0x43541000, hi=0x43A00000):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = u16(a)
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = u16(a + 2)
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def func_of(site, prols):
    cand = [p for p in prols if p <= site and site - p <= 0x4000]
    return cand[-1] if cand else None


def calls_from(start, max_insn=400):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    out = set()
    count = 0
    for ins in md.disasm(B[start - BASE:start - BASE + 0x1000], start):
        count += 1
        if count > max_insn:
            break
        if ins.mnemonic.startswith("bl"):
            try:
                out.add(int(ins.op_str.lstrip("#"), 0))
            except ValueError:
                pass
        if ins.mnemonic in ("pop", "bx") and count > 4:
            break
    return out


def main():
    prols = prologues()
    strings = json.load(open(os.path.join(S106, "strings_raw.json")))
    if isinstance(strings, dict):
        strings = strings["strings"]
    refs = json.load(open(os.path.join(S106, "pic_refs.json")))

    # Los nombres `*_Selector.cpp` son cadenas SUELTAS (sin prefijo de modulo), asi
    # que no estan en el listado de IMAGING_CAP: se buscan en el binario.
    sel = {}
    for m in re.finditer(rb"[A-Za-z0-9_]{3,40}_Selector\.cpp", B):
        vaddr = f"0x{BASE + m.start():x}"
        sites = [int(x, 16) if isinstance(x, str) else int(x)
                 for x in refs.get(vaddr, [])]
        funcs = sorted({func_of(x, prols) for x in sites if func_of(x, prols)})
        sel[m.group().decode()] = {"vaddr": vaddr,
                                   "sites": [f"0x{x:x}" for x in sites],
                                   "funcs": [f"0x{x:x}" for x in funcs]}

    handlers = table()
    hfuncs = {sid: f for sid, f in handlers}
    rows = []
    for sid, fn in handlers:
        calls = calls_from(fn)
        own = [name for name, info in sel.items()
               if f"0x{fn:x}" in info["funcs"]]
        called = []
        for name, info in sel.items():
            for f in info["funcs"]:
                if int(f, 16) in calls:
                    called.append((name, f))
        rows.append({"id": sid, "handler": f"0x{fn:x}",
                     "n_calls": len(calls),
                     "propia": own,
                     "llama_a_selector": called,
                     "calls": sorted(f"0x{c:x}" for c in calls)})
        print(f"id=0x{sid:02x} handler=0x{fn:x}  propia={own}  "
              f"llama_a={[(n, f) for n, f in called]}")

    out = {"table": f"0x{TABLE:x}", "selectors": sel, "sections": rows}
    dest = os.path.join(HERE, "section_map.json")
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print("escrito", dest)


if __name__ == "__main__":
    main()
