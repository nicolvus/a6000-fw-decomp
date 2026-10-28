"""E25-17 P0 — ejecuta el productor nativo `0x4383fa40` (código real del firmware, fw 3.21) para velocidades
de 1/8000 a 30 s y vuelca `record+0x64` (r5/shd), `+0x68` (svd), `+0x6a/+0x6c/+0x6d`, `+0xf0` (líneas) y `+0xd8..+0xdc`.

Solo emulación de software: no toca la cámara. Distingue código ejecutado (esta salida) de comportamiento físico
del sensor (no demostrado). A diferencia de E25-16/T052-B0, se restaura el cociente/módulo real `0x4355fd4c`
(allí es un stub) para que `+0xd8..+0xdc` sean fiables; r5, svd y líneas no dependen de él.
"""
from __future__ import annotations

import json
import math
import struct
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/e25_16"))
from emu_core import BASE, FW, Emu

PRODUCTOR = 0x4383FA40
PREDICADO = 0x43A12CA8
MOD = 0x4355FD4C
REC, SET = 0x3000C000, 0x3000D000
LINE_Q8, VTS, SUELO = 3891, 4219, 1
SPEEDS = {"1/8000": 1 / 8000, "1/4000": 1 / 4000, "1/250": 1 / 250, "1/60": 1 / 60, "1/30": 1 / 30, "1/15": 1 / 15,
          "1/8": 1 / 8, "1/4": 0.25, "1/2": 0.5, "1 s": 1.0, "2 s": 2.0, "4 s": 4.0, "8 s": 8.0, "15 s": 15.0,
          "30 s": 30.0}


def tv_code(t: float) -> int:
    return round(0x1000 + 256.0 * math.log2(1.0 / t))


def correr(emu: Emu, t: float, vts: int, pred: int, suelo: int = SUELO) -> dict:
    mu = emu.mu
    mu.mem_write(PREDICADO, struct.pack("<HH", 0x2000 | pred, 0x4770))
    mu.mem_write(REC, b"\0" * 0x200)
    mu.mem_write(SET, b"\0" * 0x600)
    mu.mem_write(REC + 0xC, struct.pack("<H", LINE_Q8))
    mu.mem_write(REC + 0x1C, struct.pack("<H", suelo))
    mu.mem_write(REC + 0x20, struct.pack("<H", vts))
    mu.mem_write(REC + 0xF6, struct.pack("<H", tv_code(t)))
    mu.mem_write(SET + 0x4B8, b"\x01")
    emu.call(PRODUCTOR, REC, SET)
    r = emu.read(REC, 0x120)
    u16 = lambda o: struct.unpack_from("<H", r, o)[0]
    r5, svd, lineas = struct.unpack_from("<I", r, 0x64)[0], u16(0x68), struct.unpack_from("<I", r, 0xF0)[0]
    return {"tv": tv_code(t), "lineas": lineas, "r5_shd": r5, "svd": svd, "spl+0x6a": u16(0x6A), "sint+0x6c": r[0x6C],
            "shutmode+0x6d": r[0x6D], "d8": u16(0xD8), "da": u16(0xDA), "dc": u16(0xDC),
            # modelo de las unidades: lineas totales cubiertas por (svd+1) cuadros menos el desplazamiento r5
            "lineas_si_(svd+1)*VTS-r5": (svd + 1) * vts - r5,
            "ms_lineas": round(lineas * LINE_Q8 / 256 / 1000, 3)}


def main() -> None:
    def nuevo() -> Emu:
        # un emulador por valor del predicado: Unicorn cachea los bloques traducidos y no ve el parche del stub
        e = Emu()
        e.mu.mem_write(MOD, FW.read_bytes()[MOD - BASE:MOD - BASE + 0x40])  # restaura módulo real
        return e

    out: dict[str, Any] = {"vts": VTS, "linea_q8": LINE_Q8, "suelo": SUELO, "filas": {}}
    for pred in (0, 1):
        emu = nuevo()
        out["filas"][f"pred{pred}"] = {n: correr(emu, t, VTS, pred) for n, t in SPEEDS.items()}
    emu = nuevo()
    out["sin_suelo_pred0"] = {n: correr(emu, t, VTS, 0, 0) for n, t in SPEEDS.items()}
    emu = nuevo()
    out["vts4266_pred0"] = {n: correr(emu, t, 4266, 0) for n, t in SPEEDS.items()}
    dst = ROOT / "analysis/e25-17/productor.json"
    dst.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    for k in ("pred0", "pred1"):
        print(k)
        for n, v in out["filas"][k].items():
            print(f"  {n:7s} lineas={v['lineas']:6d} r5={v['r5_shd']:6d} svd={v['svd']:4d} d8/da/dc={v['d8']}/{v['da']}/{v['dc']} chk={v['lineas_si_(svd+1)*VTS-r5']}")


if __name__ == "__main__":
    main()
