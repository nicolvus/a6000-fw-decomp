#!/usr/bin/env python3
"""E25-19c — `cap+0x728` frente al tiempo nominal: cronómetro de 32 µs y Tv real, a partir de las capturas de E25-19b.

Entrada: analysis/e25-19b/cap-{2,4,8}s.json (solo lectura física ya hecha). Salida: analysis/e25-19c/temporizador.json.
"""

from __future__ import annotations

import json
import math
import struct
from pathlib import Path

from e25_19c_emisor import tv_a_segundos

DIR = Path(__file__).resolve().parents[1] / "analysis"
TICK_S = 32e-6
# Velocidades pedidas y Tv real leído: la de 8 s se confirmó en pkt[2..3]=3243 (10,07 s); 2 s y 4 s por 728 (inferencia).
PEDIDAS = {"2s": 2.0, "4s": 4.0, "8s": 8.0}


def primer_valor(res: dict) -> dict:
    """Primera muestra con `cap+0x728` != 0: instante respecto a /shoot y ticks."""
    for m in res["muestras"]:
        c = m.get("cap")
        if not c:
            continue
        v = struct.unpack_from("<I", bytes.fromhex(c["campos"]["tmr728@0x728"]))[0]
        if v:
            return {"t_desde_shoot_s": round(m["t"] - res["t_shoot"], 2), "ticks": v}
    raise ValueError("cap+0x728 no cambió")


def analiza() -> dict:
    out = {}
    for k, pedido in PEDIDAS.items():
        r = primer_valor(json.loads((DIR / "e25-19b" / f"cap-{k}.json").read_text()))
        seg = r["ticks"] * TICK_S
        tv = round(4096 - 256 * math.log2(seg))
        out[k] = {**r, "pedido_s": pedido, "ticks_x32us_s": round(seg, 4), "tv_inferido": tv,
                  "t_tv_s": round(tv_a_segundos(tv), 4), "ratio_vs_pedido": round(seg / pedido, 3)}
    return out


if __name__ == "__main__":
    res = {"schema": "e25-19c-temporizador/v1", "tick_us": 32, "casos": analiza()}
    path = DIR / "e25-19c" / "temporizador.json"
    path.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
