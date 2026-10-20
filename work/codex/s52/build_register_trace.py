#!/usr/bin/env python3
"""Genera la traza de campos de matriz IMX235 para S52."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MATRIX = ROOT / "work/claude/out/a7s-imx235-setmode-matrix.json"
OUT = ROOT / "work/codex/s52_sensor_register_trace.csv"


def main() -> None:
    matrix = json.loads(MATRIX.read_text())
    with OUT.open("w", newline="") as stream:
        fields = [
            "sensor", "row", "field", "values_col0_0x0b", "values_col12_0x4e",
            "values_col13_0x4f", "reader", "use", "class", "status",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row, item in enumerate(matrix["rows_main"]):
            cols = item["cols"]
            if cols[0] == cols[12] and cols[0] == cols[13]:
                continue
            writer.writerow({
                "sensor": "IMX235",
                "row": row,
                "field": item["reg_u16_at_ptr_minus2"],
                "values_col0_0x0b": f"0x{cols[0]:02x}",
                "values_col12_0x4e": f"0x{cols[12]:02x}",
                "values_col13_0x4f": f"0x{cols[13]:02x}",
                "reader": "0x436f3928 (iterates rows_main; ldr [row], strb [field_ptr])",
                "use": "copies selected-column byte to field pointer; downstream consumer not resolved",
                "class": "NO VERIFICADO",
                "status": "VERIFICADO values+reader; NO VERIFICADO semantics",
            })


if __name__ == "__main__":
    main()
