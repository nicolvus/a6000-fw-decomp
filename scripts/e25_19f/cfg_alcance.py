#!/usr/bin/env python3
"""Alcance en el CFG de EndExps (analysis/e25-19f/endexps.asm): ¿desde ORIGEN se llega a DESTINO? Ignora tbb y llamadas (bl/blx vuelven).

Uso: cfg_alcance.py ORIGEN DESTINO [sin1,sin2..]   (direcciones; 'sin' = nodos que no se atraviesan)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ASM = Path(__file__).resolve().parents[2] / "analysis/e25-19f/endexps.asm"
INCOND = ("b", "b.w", "bx", "pop", "pop.w")


def cargar() -> tuple[dict[int, str], list[int]]:
    ins, orden = {}, []
    for ln in ASM.read_text().splitlines():
        m = re.match(r"(0x[0-9a-f]+): (.*)", ln)
        if m:
            ins[int(m[1], 16)] = m[2]
            orden.append(int(m[1], 16))
    return ins, orden


def alcanza(origen: int, destino: int, sin: set[int] | None = None) -> list[int] | None:
    ins, orden = cargar()
    sig = {a: orden[i + 1] for i, a in enumerate(orden[:-1])}
    sin = sin or set()
    vistos: dict[int, int] = {}
    pila = [(origen, 0)]
    while pila:
        a, prev = pila.pop()
        if a in vistos or a in sin or a not in ins:
            continue
        vistos[a] = prev
        if a == destino:
            ruta, x = [], a
            while x:
                ruta.append(x)
                x = vistos[x]
            return ruta[::-1]
        t = ins[a]
        mn = t.split()[0]
        mt = re.search(r"#(0x[0-9a-f]+)$", t)
        if mn.startswith("b") and mn not in ("bl", "blx", "bx") and mt:
            pila.append((int(mt[1], 16), a))
            if mn not in ("b", "b.w"):
                pila.append((sig.get(a, 0), a))
        elif mn in ("cbz", "cbnz") and mt:
            pila.append((int(mt[1], 16), a))
            pila.append((sig.get(a, 0), a))
        elif mn in INCOND or mn == "bx" or (mn == "pop.w" and "pc" in t):
            continue
        elif a in sig:
            pila.append((sig[a], a))
    return None


if __name__ == "__main__":
    o, d = int(sys.argv[1], 0), int(sys.argv[2], 0)
    s = {int(x, 0) for x in sys.argv[3].split(",")} if len(sys.argv) > 3 else set()
    r = alcanza(o, d, s)
    print("alcanzable" if r else "NO alcanzable", [hex(x) for x in r[:6]] if r else "", len(r) if r else "")
