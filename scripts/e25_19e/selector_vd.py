#!/usr/bin/env python3
"""E25-19e P4 — selector 3/4 de 0x438c83ce → 0x43795dec → 0x43ad3b92 → 0x436c74c8 (controlador VD/imager 0xf3120000).

0x436c74c8(obj, sel, …) guarda `sel` en obj+0x20 y despacha con `tbb` sobre sel-1. Extrae la tabla y los bloques de sel=3 y sel=4.
Salida: analysis/e25-19e/selector-vd.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from desmontar import BASE, BIN, dis

ROOT = Path(__file__).resolve().parents[2]
TBB, NCASOS = 0x436C7580, 4


def tabla(data: bytes) -> dict[int, int]:
    off = TBB + 4 - BASE
    return {s: TBB + 4 + 2 * data[off + s - 1] for s in range(1, NCASOS + 1)}


def bloque(sel: int, fin: int, data: bytes) -> list[str]:
    return dis(tabla(data)[sel], fin, data)


if __name__ == "__main__":
    d = BIN.read_bytes()
    t = tabla(d)
    res: dict[str, Any] = {"tbb": {s: hex(a) for s, a in t.items()},
           "sel3": bloque(3, t[4], d),
           "sel4": bloque(4, 0x436C7744, d)}
    (ROOT / "analysis/e25-19e/selector-vd.json").write_text(json.dumps(res, indent=1) + "\n")
    print(res["tbb"])
    print("\n".join(res["sel3"]))
    print("--")
    print("\n".join(res["sel4"]))
