#!/usr/bin/env python3
"""S118 — decodifica la **tabla de comandos** de `[SFRA]`.

El despachador `ScalarInfraAsyncMain` (`0x439a1864`) no compara ids en línea:
llama a una función-predicado de la familia `0x43b63xxx` que dice "¿este mensaje
es de tipo X?".  Cada predicado tiene esta forma:

    ldrh rX, [r0, #2]        ; id de mensaje (16 bits) en el offset +2
    cmp.w rX, #0x100         ;  ó   movw rX, #0x9010 / #0x8110 / #0x8120
    ...
    ldrb rX, [r0, #0xf]      ; sub-comando (8 bits) en el offset +0x0f
    sub.w  rY, rX, #0xNN     ; -> id de comando

Este script:
  1. decodifica todos los predicados de la zona 0x43b631xx-0x43b634xx,
  2. empareja cada predicado con la traza de comando que protege en
     `ScalarInfraAsyncMain`,
  3. genera la tabla de comandos (nombre, id de mensaje, id de comando,
     predicado, línea del .cpp).
"""
import json
import os
import re
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_sfra import BASE, BIN  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN_LO, MAIN_HI = 0x439A1864, 0x439A1E00
PRED_LO, PRED_HI = 0x43B63100, 0x43B63410


def decode_predicate(data, addr):
    """(tipo_mensaje, id_comando) de un predicado, o (None, None)."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    mtype = None
    mcmd = None
    first = None
    for i in md.disasm(data[addr - BASE:addr - BASE + 40], addr):
        if first is None:
            first = i
            if not i.mnemonic.startswith("ldrh"):
                return None, None
        t = i.mnemonic
        o = i.op_str
        if t in ("cmp", "cmp.w") and "#0x" in o:
            v = int(o.split("#")[1].split(",")[0], 16)
            if mtype is None:
                mtype = v
        if t == "movw" and "#0x" in o:
            v = int(o.split("#")[1], 16)
            if v > 0xFF and mtype is None:
                mtype = v
        if t in ("sub.w", "sub") and "#0x" in o:
            v = int(o.split("#")[1], 16)
            if mcmd is None:
                mcmd = v
        if t == "bx" or t.startswith("pop"):
            break
    return mtype, mcmd


def main():
    data = open(BIN, "rb").read()
    smap = {}
    for s, lst in json.load(open(os.path.join(HERE, "site_best.json"))).items():
        smap[int(s, 16)] = int(lst[0], 16)

    def cstr(va):
        off = va - BASE
        end = off
        while end < len(data) and 32 <= data[end] < 127:
            end += 1
        return data[off:end].decode("latin1")

    # --- predicados candidatos -------------------------------------------------
    preds = {}
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    a = PRED_LO
    while a < PRED_HI:
        t, c = decode_predicate(data, a)
        if t is not None:
            preds[a] = (t, c)
            a += 2
        else:
            a += 2

    # --- recorrido de ScalarInfraAsyncMain -------------------------------------
    rows = []
    pred = None
    line = None
    for ins in md.disasm(data[MAIN_LO - BASE:MAIN_HI - BASE], MAIN_LO):
        if ins.mnemonic == "bl":
            t = int(ins.op_str.lstrip("#"), 16) & ~1
            if t in preds:
                pred = t
        if ins.mnemonic in ("movs", "mov") and re.match(r"r1, #0x[0-9a-f]+$", ins.op_str):
            v = int(ins.op_str.split("#")[1], 16)
            if 0x40 <= v <= 0x400:
                line = v
        tgt = smap.get(ins.address)
        if tgt is None:
            continue
        txt = cstr(tgt)
        if "***" not in txt:
            continue
        mt, mc = preds.get(pred, (None, None)) if pred else (None, None)
        rows.append({"name": re.search(r"\*\*\*(.+?)\*\*\*", txt).group(1),
                     "level": "CMD" if "[CMD]" in txt else "CMP",
                     "vaddr": f"0x{tgt:x}", "text": txt,
                     "site": f"0x{ins.address:x}",
                     "pred": f"0x{pred:x}" if pred else None,
                     "msg_type": f"0x{mt:x}" if mt is not None else None,
                     "cmd_id": f"0x{mc:x}" if mc is not None else None,
                     "line_ScalarInfraAsyncMain_cpp": line})
        pred = None
        line = None
    for r in rows:
        print(f"{r['level']:<4}{r['name']:<26} msg={r['msg_type']} cmd={r['cmd_id']} "
              f"pred={r['pred']} linea={r['line_ScalarInfraAsyncMain_cpp']}  {r['vaddr']}")
    json.dump(rows, open(os.path.join(HERE, "command_table.json"), "w"), indent=1,
              ensure_ascii=False)


if __name__ == "__main__":
    main()
