#!/usr/bin/env python3
"""S122 — clasifica el destino de cada sitio PIC (string/prefix/inner).

Para cada `add rX,pc` que resuelve al inicio de la cadena completa (con
etiqueta), desensambla hacia delante con capstone hasta 40 instrucciones y
anota la primera llamada directa (`bl`/`blx` con inmediato):

  * `printf`     -> 0x43902718 (impresor local variadico),
  * `publisher`  -> familia de publicadores OSAL que empaquetan la cadena
                    completa en un mensaje,
  * `other`      -> otra función,
  * `none`       -> ninguna llamada en la ventana (uso como dato).

Salida: emitters.json
Uso: scan_emitters.py
"""
import json
import os
from collections import Counter

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
PRINTF = 0x43902718
PUBLISHERS = [
    0x437D4828, 0x43878570, 0x43876C08, 0x4387651C, 0x437D6CF4,
    0x43873004, 0x438737A4, 0x4387401C, 0x43874BA4, 0x437D373C,
    0x43874700, 0x437D19C4, 0x437D5090, 0x43872894, 0x43875188,
    0x438758A4, 0x438E8158,
]
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def next_call(a, limit=40):
    """Primera llamada directa tras `a` (exclusive) en <= limit instrucciones."""
    for n, ins in enumerate(MD.disasm(B[a - BASE:a - BASE + 4 * limit], a)):
        if n == 0:
            continue
        if ins.mnemonic in ("bl", "blx") and ins.op_str.startswith("#"):
            return int(ins.op_str[1:], 16)
        if ins.mnemonic in ("pop", "bx", "b") and "pc" in ins.op_str:
            return None
    return None


def main():
    refs = json.load(open(os.path.join(HERE, "refs_targeted.json")))["hits"]
    out = []
    for x in refs:
        a = int(x["add"], 16)
        call = next_call(a)
        kind = ("printf" if call == PRINTF
                else "publisher" if call in PUBLISHERS
                else "none" if call is None else "other")
        out.append({"idx": x["idx"], "kind": x["kind"], "add": x["add"],
                    "call": None if call is None else f"0x{call:x}",
                    "class": kind})
    json.dump({"printers": {"printf": f"0x{PRINTF:x}",
                            "publishers": [f"0x{p:x}" for p in sorted(PUBLISHERS)]},
               "hits": out}, open(os.path.join(HERE, "emitters.json"), "w"),
              indent=1)
    for k in ("string", "prefix", "inner"):
        sel = [r for r in out if r["kind"] == k]
        print(k, Counter(r["class"] for r in sel))
    print(Counter(r["call"] for r in out
                  if r["class"] == "publisher" and r["kind"] == "string"))
    print("string other:", [(r["idx"], r["add"], r["call"]) for r in out
                            if r["class"] == "other" and r["kind"] == "string"])
    print("string printf:", [(r["idx"], r["add"]) for r in out
                             if r["class"] == "printf" and r["kind"] == "string"])
    print("inner no-printf:", [(r["idx"], r["add"], r["call"]) for r in out
                               if r["kind"] == "inner" and r["class"] != "printf"])


if __name__ == "__main__":
    main()
