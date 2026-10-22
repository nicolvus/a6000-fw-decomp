#!/usr/bin/env python3
"""S122 — verificación de las 4 cadenas `[CAMERA_MAIN_TC]` sin referencia PIC.

Para cada cadena declarada muerta se comprueban los tres mecanismos alternativos
de direccionamiento que la regla estricta no cubre:

  1. puntero absoluto de 4 bytes (little-endian) en cualquier punto de la imagen,
  2. `addw rX, pc, #imm12` (ADD inmediato T3 con Rn=PC) cuyo destino cae dentro
     de la cadena,
  3. par `movw rX,#lo` + `movt rX,#hi` que componga la dirección completa.

Salida: dead_check.json
Uso: scan_dead_check.py
"""
import json
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from


def addw_pc_sites():
    """[(addr, target)] de `addw rX, pc, #imm12`."""
    out = []
    a = BASE
    while a < BASE + N - 4:
        o = a - BASE
        h1, h2 = U16(B, o)[0], U16(B, o + 2)[0]
        # ADD (imm) T3: 11110 i 0 1000 0 Rn / 0 imm3 Rd imm8 ; Rn=PC=15
        if (h1 & 0xFBFF) == 0xF20F and (h2 & 0x8000) == 0:
            imm = (((h1 >> 10) & 1) << 11) | (((h2 >> 12) & 7) << 8) | (h2 & 0xFF)
            out.append((a, (a + 4 + imm) & 0xFFFFFFFF))
        a += 2
    return out


def movw_movt_pairs():
    """[(addr_movw, reg, valor)] de pares movw/movt consecutivos (<=6 instr.)."""
    out = []
    a = BASE
    wins = []
    while a < BASE + N - 4:
        o = a - BASE
        h1, h2 = U16(B, o)[0], U16(B, o + 2)[0]
        if (h1 & 0xFB00) == 0xF200 and (h2 & 0x8000) == 0:
            rd = (h2 >> 8) & 0xF
            imm = (((h1 >> 10) & 1) << 11) | (((h2 >> 12) & 7) << 8) | (h2 & 0xFF)
            wins.append((a, rd, imm, "movw"))
        if (h1 & 0xFB00) == 0xF2C0 and (h2 & 0x8000) == 0:
            rd = (h2 >> 8) & 0xF
            imm = (((h1 >> 10) & 1) << 11) | (((h2 >> 12) & 7) << 8) | (h2 & 0xFF)
            wins.append((a, rd, imm, "movt"))
        a += 2
    for i, (a, rd, lo, k) in enumerate(wins):
        if k != "movw":
            continue
        for b, rd2, hi, k2 in wins[i + 1:i + 7]:
            if b - a > 24:
                break
            if k2 == "movt" and rd2 == rd:
                out.append((a, rd, (hi << 16) | lo))
                break
    return out


def main():
    tmap = json.load(open(os.path.join(HERE, "tc_map.json")))
    dead = tmap["dead"]
    addws = addw_pc_sites()
    pairs = movw_movt_pairs()
    out = []
    for d in dead:
        v = int(d["vaddr"], 16)
        text_len = len(d["text"]) + 1
        ptr = struct.pack("<I", v)
        abs_sites = []
        i = B.find(ptr)
        while i != -1:
            abs_sites.append(f"0x{BASE + i:x}")
            i = B.find(ptr, i + 1)
        aw = [f"0x{a:x}" for a, t in addws if v <= t < v + text_len]
        mm = [f"0x{a:x}" for a, _, val in pairs if val == v]
        out.append({"vaddr": d["vaddr"], "text": d["text"],
                    "absolute_pointers": abs_sites,
                    "addw_pc": aw,
                    "movw_movt": mm,
                    "dead": not (abs_sites or aw or mm)})
    json.dump({"dead": out}, open(os.path.join(HERE, "dead_check.json"), "w"),
              indent=1, ensure_ascii=False)
    for r in out:
        print(r["vaddr"], r["dead"], len(r["absolute_pointers"]), r["addw_pc"], r["movw_movt"])


if __name__ == "__main__":
    main()
