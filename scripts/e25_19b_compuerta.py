#!/usr/bin/env python3
"""E25-19b — campos de la compuerta `0x43afc544` de cada gestor, solo lectura (/dev/mem por Telnet).

Por gestor E: +0x24 bloqueado (Block/Unblock 0x437e52b0/0x437e54b4), +0x2c máximo en vuelo, +0x2d en vuelo,
+0x28 último, Mide si un evento pendiente se difiere por compuerta (en vuelo >= máximo,
bloqueado) o no. Uso: --confirm-readonly [--samples N --period S] durante una foto de 4 s disparada aparte.
"""
from __future__ import annotations

import argparse
import json
import struct
import time

from e25_19_readonly import Telnet, verify_originals
from e25_19b_cadena import BIN, OUTDIR, RAM_OFF, static_chain


def snapshot(tr: Telnet, gestores: list[int]) -> dict:
    out = {}
    for e in sorted(set(gestores) - {0}):
        b = tr.read(e + RAM_OFF + 0x24, 0x10)  # +0x24..+0x33
        out[f"{e:#x}"] = {"bloqueado": b[0], "ultimo": struct.unpack_from("<I", b, 4)[0],
                          "max_vuelo": b[8], "en_vuelo": b[9]}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--confirm-readonly", action="store_true", required=True)
    ap.add_argument("--samples", type=int, default=12)
    ap.add_argument("--period", type=float, default=0.5)
    a = ap.parse_args()
    ch = static_chain(BIN.read_bytes())
    tr = Telnet()
    res: dict = {"schema": "e25-19b-compuerta/v1", "muestras": []}
    try:
        assert verify_originals(tr)["ok"], "originales T050 alterados"
        for _ in range(a.samples):
            res["muestras"].append({"t": time.time(), "g": snapshot(tr, ch["gestores"])})
            time.sleep(a.period)
        res["originales_ok_final"] = verify_originals(tr)["ok"]
    finally:
        tr.close()
    out = OUTDIR.parent / "e25-19b" / "compuerta-4s.json"
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
