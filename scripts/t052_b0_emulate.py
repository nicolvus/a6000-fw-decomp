#!/usr/bin/env python3
"""T052-B0 — emulación de `0x4383fa40` con VTS/predicado reales y C3-B.

No toca la cámara. Ejecuta la función del firmware `av-cam.bin` (3.21) en
Unicorn con un registro sintético y escribe `analysis/t052-b0/emulacion.json`.

Escenarios:
  A: VTS 4219, predicado 0 (sin cuadro extra).
  B: VTS 4266, predicado 0.
  C: VTS 4219, predicado 1 (NVRAM/rest: 0 -> cuadro extra activo).
  D: VTS 4266, predicado 1.
  E: VTS 1000, predicado 0/1 (control de que `lines` no depende del VTS).

La alternativa C3-B usa `record+0xf0` (líneas calculadas) y la referencia
medida 4219: `r5 = 4219 - lineas`. Es independiente del VTS del descriptor y
del predicado; la emulación lo comprueba.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/e25_16"))

from emu_core import thumb_stub_ret  # type: ignore[import-not-found]
from emular_r5 import (  # type: ignore[import-not-found]
    LINE_Q8,
    NATIVE_RECORD,
    NATIVE_SETTINGS,
    TV_TO_R5,
    Harness,
)

OUT = ROOT / "analysis/t052-b0/emulacion.json"
VTS_REF = 4219  # referencia efectiva medida en T046/T047
SPEEDS = {
    "1/4000": (0x1BF7, 0.25),
    "1/250": (0x17F7, 4.0),
    "1/60": (0x15E8, 16.674),
}
T047 = {"1/4000": 4203, "1/250": 3956, "1/60": 3122}


def run_case(tv: int, vts: int, extra: int) -> dict:
    h = Harness()
    # El stub del predicado se reescribe antes de cada llamada: Unicorn no
    # invalida de forma fiable el bloque ya decodificado entre llamadas.
    h.mu.mem_write(0x43A12CA8, thumb_stub_ret(extra))
    h.mu.mem_write(NATIVE_RECORD, b"\x00" * 0x200)
    h.mu.mem_write(NATIVE_SETTINGS, b"\x00" * 0x600)
    h.mu.mem_write(NATIVE_RECORD + 0xC, struct.pack("<I", LINE_Q8))
    h.mu.mem_write(NATIVE_RECORD + 0x1C, struct.pack("<H", 1))
    h.mu.mem_write(NATIVE_RECORD + 0x20, struct.pack("<H", vts))
    h.mu.mem_write(NATIVE_RECORD + 0xF6, struct.pack("<H", tv))
    h.mu.mem_write(NATIVE_SETTINGS + 0x4B8, b"\x01")
    h.call(TV_TO_R5, NATIVE_RECORD, NATIVE_SETTINGS)
    r5 = struct.unpack("<I", h.read(NATIVE_RECORD + 0x64, 4))[0]
    frames = struct.unpack("<H", h.read(NATIVE_RECORD + 0x68, 2))[0]
    shutmode = h.read(NATIVE_RECORD + 0x6D, 1)[0]
    lines = struct.unpack("<I", h.read(NATIVE_RECORD + 0xF0, 4))[0]
    d8, da, dc = (struct.unpack("<H", h.read(NATIVE_RECORD + o, 2))[0] for o in (0xD8, 0xDA, 0xDC))
    return {
        "vts": vts,
        "predicado": extra,
        "r5_nativo": r5,
        "frames": frames,
        "shutmode": shutmode,
        "lineas": lines,
        "d8_da_dc": [d8, da, dc],
        "r5_c3b": max(VTS_REF - lines, 0),
        "r5_nativo_valido": int(2 <= r5 < vts),
        "r5_c3b_valido": int(2 <= VTS_REF - lines),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, default=OUT)
    args = ap.parse_args()

    rows: dict[str, dict] = {}
    const_lines: dict[str, bool] = {}
    for name, (tv, nominal_ms) in SPEEDS.items():
        cases = {}
        for vts in (4219, 4266, 1000):
            for extra in (0, 1):
                cases[f"vts{vts}_extra{extra}"] = run_case(tv, vts, extra)
        values = {c["lineas"] for c in cases.values()}
        const_lines[name] = len(values) == 1
        ref = cases["vts4219_extra0"]
        rows[name] = {
            "tv": f"0x{tv:04x}",
            "nominal_ms": nominal_ms,
            "casos": cases,
            "lineas_constantes": const_lines[name],
            "r5_c3b": ref["r5_c3b"],
            "r5_t047": T047[name],
            "delta_c3b_vs_t047": ref["r5_c3b"] - T047[name],
        }

    out = {
        "firmware": "av-cam.bin fw3.21",
        "sha256": "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9",
        "line_us": 15.2,
        "line_q8": LINE_Q8,
        "vts_ref": VTS_REF,
        "stub": "0x43a12ca8 se sustituye por 0/1; el firmware real lee [0x43deb360+0x10]",
        "velocidades": rows,
        "conclusion": {
            "lineas_independientes_de_vts_y_predicado": all(const_lines.values()),
            "c3a_invalido_con_predicado_activo": all(
                rows[n]["casos"]["vts4219_extra1"]["r5_nativo"] > 4219 for n in SPEEDS
            ),
            "c3b_reproduce_t047": all(abs(rows[n]["delta_c3b_vs_t047"]) <= 1 for n in SPEEDS),
        },
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"escrito {args.json}")
    for n, r in rows.items():
        print(f"{n}: lineas={r['casos']['vts4219_extra0']['lineas']} "
              f"r5_nat(4219,e0)={r['casos']['vts4219_extra0']['r5_nativo']} "
              f"r5_nat(4219,e1)={r['casos']['vts4219_extra1']['r5_nativo']} "
              f"c3b={r['r5_c3b']} T047={r['r5_t047']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
