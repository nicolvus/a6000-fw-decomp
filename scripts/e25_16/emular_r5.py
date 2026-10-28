#!/usr/bin/env python3
"""E25-16 — emulación del cálculo autónomo de `r5` en la ruta de fotografía.

Cadena nativa (fw 3.21, `av-cam.bin`, SHA-256 b60c845c…):

    Tv (código de 1/256 EV, 0x1000 = 1 s)
      -> 0x4382fa94(Tv)              µs × 256     (Q8; Tv > 0xC54)
      -> 0x4355faf0(q8, record+0xc)  líneas       (__aeabi_uidiv, truncante)
      -> r5 = max(frame − líneas, 0) con frame = max(record+0x20, …)
      -> SetExposure (0x436d6f6c)    blk+0x50..0x57
      -> SetRead     (0x436d7e08)    blk+0x66..0x6c

`Harness.native_r5(tv)` ejecuta la función **del firmware** `0x4383fa40` con un
registro sintético: `record+0xc = 3891` (período de línea Q8), `record+0x1c = 0`
(suelo), `record+0x20 = 4219` (VTS efectivo), `record+0xf6 = Tv` y
`settings+0x4b8 = 1`. El 4219 es la calibración medida en T046/T047, no una
constante del binario: el firmware lee `record+0x20`. Para comparar se emiten:

  * `r5_funcion_nativa` = 0x4383fa40 con VTS 4219 (debe reproducir T047).
  * `r5_funcion_con_vts_nativo` = 0x4383fa40 con VTS 4266 (0x4385de94(600,1,0)).
  * `r5_medido` = 4219 − líneas (modelo reducido, para la tabla).

La diferencia 4266 − 4219 = 47 líneas ≈ 0,71 ms no se oculta: es la
discrepancia entre la función de vista en directo y la calibración física, y se
documenta como límite. No se conecta la cámara ni se escribe fuera de la
memoria del emulador.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


from emu_core import CFG, Emu

SETEXPOSURE = 0x436D6F6C
SETREAD = 0x436D7E08
TV_US = 0x4382FAC8
TV_Q8 = 0x4382FA94
UIDIV = 0x4355FAF0
VTS = 0x4385DE94
RECORD_BUILDER = 0x437B43B4
TV_TO_R5 = 0x4383FA40

LINE_US = 15.2
LINE_Q8 = round(LINE_US * 256)          # 3891
VTS_MEASURED = 4219                      # T046/T047
VTS_ARG_A = 600                          # [imager+0x134] con línea de 15,2 µs
VTS_ARG_M = 1                            # [settings+0x4b8]

OBJ_IMAGER = 0x30000000
PARAM_SE = 0x30008000
PARAM_SR = 0x30008100
NATIVE_RECORD = 0x3000C000
NATIVE_SETTINGS = 0x3000D000

SPEEDS = {
    "1/8000": 1 / 8000,
    "1/4000": 1 / 4000,
    "1/2000": 1 / 2000,
    "1/1000": 1 / 1000,
    "1/500": 1 / 500,
    "1/250": 1 / 250,
    "1/125": 1 / 125,
    "1/60": 1 / 60,
    "1/30": 1 / 30,
    "1/15": 1 / 15,
    "1/8": 1 / 8,
    "1s": 1.0,
    "10s": 10.0,
    "30s": 30.0,
}

# expectativas medidas en T047/T050 (referencia física); sólo calibración T046
T047 = {
    "1/4000": (0.24, 4203),
    "1/1000": (0.99, 4153),
    "1/250": (4.03, 3956),
    "1/60": (16.75, 3122),
}


def tv_code(seconds: float) -> int:
    """Código Tv de 1/256 EV: 0x1000 + 256·log2(1/t)."""
    return round(0x1000 + 256.0 * math.log2(1.0 / seconds))


class Harness(Emu):
    """Emulador con el objeto imager sintético que espera `SetExposure`."""

    def __init__(self):
        super().__init__()
        self.setup_imager()

    def setup_imager(self):
        mu = self.mu
        mu.mem_write(OBJ_IMAGER, b"\x00" * 0x1C0)
        desc = CFG + 0x1000
        mu.mem_write(OBJ_IMAGER + 0x294, struct.pack("<I", desc))
        mu.mem_write(desc, struct.pack("<IIII", 0x11, 30, 0, 0))
        mu.mem_write(desc + 0x18, struct.pack("<I", CFG + 0x3000))
        mu.mem_write(desc + 0x1C, struct.pack("<I", CFG + 0x2000))
        base = [14539, 14756, 14974, 15192, 15411, 15630]
        blob = b"".join(struct.pack("<III", v << 8, v << 8, v << 8) for v in base)
        mu.mem_write(CFG + 0x2000, blob + b"\x00" * (30 * 12 - len(blob)))
        r = bytearray(48)
        struct.pack_into("<H", r, 0x1A, 0x0600)
        struct.pack_into("<H", r, 0x1C, 0x1000)
        mu.mem_write(CFG + 0x3000, bytes(r) * 30)
        mu.mem_write(OBJ_IMAGER + 0x170, struct.pack("<I", 0x0B))
        mu.mem_write(OBJ_IMAGER + 0x17C, b"\x00")
        mu.mem_write(OBJ_IMAGER + 0x18, b"\x00" * 0x40)

    def tv_us(self, code: int) -> int:
        return self.call(TV_US, code, 0) & 0xFFFFFFFF

    def uidiv(self, a: int, b: int) -> int:
        return self.call(UIDIV, a & 0xFFFFFFFF, b & 0xFFFFFFFF) & 0xFFFFFFFF

    def vts(self, a: int, m: int, c: int = 0) -> int:
        return self.call(VTS, a, m, c) & 0xFFFF

    def native_r5(self, tv: int, vts: int = VTS_MEASURED,
                  line_q8: int = LINE_Q8, frame_mult: int = 1) -> int:
        """Ejecuta el productor nativo `0x4383fa40` con un registro sintético.

        Campos que lee: `record+0xc` (período de línea en Q8), `record+0x1c`
        (suelo de r5, 0 en el registro real), `record+0x20` (VTS efectivo),
        `record+0xf6` (Tv) y `settings+0x4b8` (factor de cuadro).
        """
        mu = self.mu
        mu.mem_write(NATIVE_RECORD, b"\x00" * 0x200)
        mu.mem_write(NATIVE_SETTINGS, b"\x00" * 0x600)
        mu.mem_write(NATIVE_RECORD + 0xC, struct.pack("<H", line_q8))
        mu.mem_write(NATIVE_RECORD + 0x1C, struct.pack("<H", 0))
        mu.mem_write(NATIVE_RECORD + 0x20, struct.pack("<H", vts))
        mu.mem_write(NATIVE_RECORD + 0xF6, struct.pack("<H", tv))
        mu.mem_write(NATIVE_SETTINGS + 0x4B8, bytes([frame_mult]))
        self.call(TV_TO_R5, NATIVE_RECORD, NATIVE_SETTINGS)
        return struct.unpack("<I", self.read(NATIVE_RECORD + 0x64, 4))[0]

    def setexposure(self, r5: int, shutmode: int, p4: int = 0, p6: int = 0):
        blob = struct.pack("<HHHHBBBB", r5 & 0xFFFF, p4, p6, 0, 0, shutmode, 0, 0)
        self.mu.mem_write(PARAM_SE, blob)
        self.call(SETEXPOSURE, OBJ_IMAGER, PARAM_SE)
        return self.cmd_writes()

    def setread(self, code: int):
        blob = struct.pack("<HHH", code & 0xFFFF, 0x0FFF, 0x0100) + b"\x00" * 10
        self.mu.mem_write(PARAM_SR, blob)
        self.call(SETREAD, OBJ_IMAGER, PARAM_SR)
        return self.cmd_writes()

    def cmd_writes(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for a, s, v in self.writes:
            if OBJ_IMAGER + 0xFC <= a < OBJ_IMAGER + 0x1C0:
                out[f"blk+0x{a - OBJ_IMAGER - 0xFC:02x}"] = v
        return out


def compute_table(h: Harness, vts_native: int) -> dict:
    rows = {}
    for name, sec in SPEEDS.items():
        code = tv_code(sec)
        us = h.tv_us(code)
        lines = h.uidiv(us * 256, LINE_Q8)
        r5_nat = vts_native - lines
        r5_med = VTS_MEASURED - lines
        r5_fn = h.native_r5(code, VTS_MEASURED)
        r5_fn_vts = h.native_r5(code, vts_native)
        nominal_us = sec * 1e6
        rows[name] = {
            "tv": code,
            "us_nativo": us,
            "us_nominal": round(nominal_us, 2),
            "error_tv_us": round(us - nominal_us, 2),
            "lineas": lines,
            "vts_nativo": vts_native,
            "r5_nativo": r5_nat,
            "r5_medido": r5_med,
            "r5_funcion_nativa": r5_fn,
            "r5_funcion_con_vts_nativo": r5_fn_vts,
            "error_si_vts_nativo_pct": (
                round(((VTS_MEASURED - r5_fn_vts) - lines) / lines * 100.0, 1)
                if r5_fn_vts < VTS_MEASURED and lines else None
            ),
            "representable": r5_med >= 2,
            "saturado": r5_fn < 2,
            "exposicion_nativa_us": round(lines * LINE_US, 1) if r5_nat >= 2 else None,
            "exposicion_medida_us": round(lines * LINE_US, 1) if r5_fn >= 2 else None,
            "r5_naive_sobre_limite": r5_nat > VTS_MEASURED,
            "lineas_hasta_limite": VTS_MEASURED - 1,
        }
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    h = Harness()
    vts_native = h.vts(VTS_ARG_A, VTS_ARG_M, 0)
    rows = compute_table(h, vts_native)

    # comprobación del bloque de comandos para dos escenarios límite
    scen = {}
    for name in ("1/8000", "1/250", "1/30", "1/15"):
        r = rows[name]
        if r["representable"]:
            se = h.setexposure(max(r["r5_nativo"], 1), 0)
            scen[name] = {
                "r5": max(r["r5_nativo"], 1),
                "shutmode": 0,
                "setexposure": {k: se.get(k) for k in
                                ("blk+0x50", "blk+0x52", "blk+0x54", "blk+0x56", "blk+0x57")},
                "setread": "sin cambios (E25-15: escribe blk+0x66..0x6c, no toca r5)",
            }

    # comparación con las medidas de T047 (calibración T046)
    cmp_t047 = {}
    for name, (ms, r5_ref) in T047.items():
        r = rows[name]
        cmp_t047[name] = {
            "medido_ms": ms,
            "r5_t047": r5_ref,
            "r5_nativo": r["r5_nativo"],
            "r5_medido": r["r5_medido"],
            "r5_funcion_nativa": r["r5_funcion_nativa"],
            "delta_lineas_vs_t047": r["r5_funcion_nativa"] - r5_ref,
            "error_predicho_vs_medido": round(
                (r["exposicion_medida_us"] / 1000.0 - ms) / ms * 100.0, 1),
            "error_de_cuantizacion_pct": round(
                (r["lineas"] * LINE_US - ms * 1000.0) / (ms * 1000.0) * 100.0, 1),
        }

    out = {
        "firmware": "av-cam.bin fw3.21",
        "line_us": LINE_US,
        "line_q8": LINE_Q8,
        "vts_nativo": vts_native,
        "vts_medido": VTS_MEASURED,
        "delta_vts_lineas": vts_native - VTS_MEASURED,
        "precision": {
            "cuantizacion_linea_us": LINE_US,
            "resolucion_tv_ev": 1 / 256,
            "nota": "el error de cuantización en líneas domina en 1/8000",
        },
        "velocidades": rows,
        "escenarios": scen,
        "comparacion_t047": cmp_t047,
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")

    if not args.quiet:
        print(f"VTS nativo = {vts_native}  (medido 4219, Δ={vts_native - VTS_MEASURED})")
        print(f"{'vel':>7} {'Tv':>7} {'us':>9} {'nom':>9} {'líneas':>7} "
              f"{'r5nat':>6} {'r5med':>6} {'r5fn':>6} {'T_nat ms':>9} {'T_med ms':>9}")
        def ms(v):
            return f"{v/1000:>9.3f}" if v is not None else "        —"

        for name, r in rows.items():
            print(f"{name:>7} {r['tv']:>7x} {r['us_nativo']:>9} {r['us_nominal']:>9} "
                  f"{r['lineas']:>7} {r['r5_nativo']:>6} {r['r5_medido']:>6} "
                  f"{r['r5_funcion_nativa']:>6} {ms(r['exposicion_nativa_us'])} "
                  f"{ms(r['exposicion_medida_us'])}")
        print()
        for name, d in cmp_t047.items():
            print(f"T047 {name}: medido {d['medido_ms']} ms, r5 T047 {d['r5_t047']}, "
                  f"calculado (VTS medido) {d['r5_medido']} "
                  f"(Δ {d['delta_lineas_vs_t047']:+d} líneas), "
                  f"error {d['error_predicho_vs_medido']:+.1f} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
