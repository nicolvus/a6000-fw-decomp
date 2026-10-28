#!/usr/bin/env python3
"""E25-19e P2 — todos los stores que cubren el byte cap+0x74f (strb@74f, strh@74e, str@74c), incl. los que 19d no contó.

Reutiliza el barrido de E25-19d y añade la clasificación de objeto/valor (revisión manual de cada sitio, ver informe §3).
Salida: analysis/e25-19e/cubren-74f.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "e25_19d"))
import escritores_74f as barrido  # type: ignore[import-not-found]

CLASE = {
    0x438ACC9C: "W1 plan[0x142] (par, 8/8 ramas): no puede ser 1",
    0x437DF5E8: "W2 valor 0",
    0x438C2562: "W3 valor 0",
    0x4354AF88: "EndExps 0x4354a678 bloque 1: 74e <- cap[0x19c] (=0 en vivo; 0xc30 sigue 0: no ejecutado)",
    0x4354B0AC: "EndExps 0x4354a678 bloque 2: 74e <- sp+0x312 (geometría 0x43af54d8/0x43af5504); valor NO evaluado",
    0x4354C868: "secuenciador 0x4354c6d0 (modo 0xa): 74e <- alto de la tabla global 0x43e9515e/0x43e95182 (240/288)",
}
CUBREN = {"strb.w": 0x74F, "strh.w": 0x74E, "str.w": 0x74C}


def cubren(data: bytes) -> list[dict]:
    out = []
    for x in barrido.barrido(data):
        mn, _, ops = x["ins"].partition(" ")
        if x["tipo"] == "mem" and CUBREN.get(mn) is not None and ops.endswith(f"#{CUBREN[mn]:#x}]"):
            out.append({"addr": x["addr"], "ins": x["ins"], "clase": CLASE.get(x["addr"], "otro objeto (str.w@74c de 0x439c80xx: valores negados, punteros en +4/+8): sin alias demostrado")})
    return sorted(out, key=lambda r: r["addr"])


if __name__ == "__main__":
    r = cubren(barrido.BIN.read_bytes())
    (ROOT / "analysis/e25-19e/cubren-74f.json").write_text(json.dumps([{**x, "addr": hex(x["addr"])} for x in r], indent=1) + "\n")
    for x in r:
        print(hex(x["addr"]), x["ins"], "|", x["clase"])
