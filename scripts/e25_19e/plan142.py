#!/usr/bin/env python3
"""E25-19e P0/P1 — ¿puede W1 (0x438acc9c) copiar un 1 a cap+0x74f?

W1 copia byte a byte plan[0x13f..0x142] -> cap[0x74c..0x74f]. plan+0x142 es un halfword escrito en 8 ramas del constructor 0x438ab3e8;
se comprueba que en cada una el valor sale de `lsls r0,r0,#1` (paridad) y que el destino de W1 viene de 0x43b13b2c (id 0x9405).
Salida: analysis/e25-19e/plan142.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from desmontar import dis

ROOT = Path(__file__).resolve().parents[2]


def ramas() -> list[dict]:
    ins = dis(0x438ab3e8, 0x438acd48)
    out = []
    for k, linea in enumerate(ins):
        if re.search(r"strh\.w r0, \[r4, #0x142\]$", linea):
            prev = [x.split(": ", 1)[1] for x in ins[k - 3:k]]
            out.append({"store": linea.split(":")[0], "previas": prev, "par": any(p == "lsls r0, r0, #1" for p in prev)})
    return out


def copia_w1() -> list[dict]:
    """Pares (plan_off -> cap_off) de la copia de bytes que contiene W1."""
    ins = dis(0x438acc40, 0x438acca4)
    m = []
    for a, b in zip(ins[0::2], ins[1::2], strict=False):
        ra = re.search(r"\[r4, #(0x[0-9a-f]+)\]", a)
        rb = re.search(r"\[r3, #(0x[0-9a-f]+)\]", b)
        if ra and rb:
            m.append({"plan": ra.group(1), "cap": rb.group(1)})
    return m


if __name__ == "__main__":
    res: dict[str, Any] = {"ramas": ramas(), "copia": copia_w1()}
    res["todas_pares"] = len(res["ramas"]) == 8 and all(r["par"] for r in res["ramas"])
    (ROOT / "analysis/e25-19e/plan142.json").write_text(json.dumps(res, indent=1) + "\n")
    print(len(res["ramas"]), "ramas; todas pares:", res["todas_pares"])
    print([c for c in res["copia"] if c["cap"] in ("0x74c", "0x74d", "0x74e", "0x74f")])
