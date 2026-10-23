#!/usr/bin/env python3
"""S341 - sintesis del carril B: comprueba que las cifras del informe existen.

No introduce hallazgos: lee los JSON de S321-S340 y verifica las cifras que la
sintesis cita, para que el documento no derive de los artefactos.

Uso: ``.venv/bin/python analysis/s341_synthesis_b2/verify_synthesis.py``
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "analysis"

CHECKS: list[tuple[str, str, Any]] = [
    # (fichero, ruta dentro del JSON, valor esperado)
    ("s321_matrix_rows/matrix_rows.json", "matrix_a7s.rows", 69),
    ("s333_mode_vocabulary/mode_vocabulary.json", "vocabulary.counts", {"a6000": 13, "a7s": 34, "shared": 12}),
    ("s333_mode_vocabulary/mode_vocabulary.json", "vocabulary.a6000_only", ["0x2f"]),
    ("s333_mode_vocabulary/mode_vocabulary.json", "a6000.columns.distinct_vectors", 7),
    ("s333_mode_vocabulary/mode_vocabulary.json", "a7s.columns.distinct_vectors", 15),
    ("s329_mode_timing_tables/mode_timing.json", "bases_from_pic.T2.base", "0x43bbf2e8"),
    ("s329_mode_timing_tables/mode_timing.json", "bases_from_pic.T3.base", "0x43bbef30"),
    ("s329_mode_timing_tables/mode_timing.json", "descriptor_b.rows_available", 2),
    ("s329_mode_timing_tables/mode_timing.json", "verdicts.0x4e_vs_0x4c_diff_count", 14),
    ("s329_mode_timing_tables/mode_timing.json", "verdicts.0x4f_vs_0x4d_diff_count", 11),
    ("s331_consumer_signature/consumer_signature.json", "consumer.signature",
     "0x436f618c(obj, posicion_modo, flag)"),
    ("s331_consumer_signature/consumer_signature.json", "verdicts.obj_2b4_is_row_index", False),
    ("s332_a6000_tables/a6000_tables.json", "comparison.counts", {"a6000": 13, "a7s": 34}),
    ("s332_a6000_tables/a6000_tables.json", "comparison.descriptor_rows", {"a6000": 3, "a7s": 2}),
    ("s332_a6000_tables/a6000_tables.json", "comparison.zero_masks", {"a6000": 0, "a7s": 30}),
    ("s334_pair_dataflow/pair_dataflow.json", "verdicts.pair_second_byte_is_bit_index", True),
    ("s334_pair_dataflow/pair_dataflow.json", "verdicts.mask_destinations", ["obj+0x68", "obj+0xf8"]),
    ("s335_mmio_layer/mmio_layer.json", "verdicts.mask_path_ends_in_mmio", True),
    ("s335_mmio_layer/mmio_layer.json", "verdicts.p2s_hypothesis", "DESCARTADA"),
    ("s336_table_consumers/table_consumers.json", "reference_count", 13),
    ("s336_table_consumers/table_consumers.json", "verdicts.only_index_and_mask", False),
    ("s337_fef404_table/fef404_table.json", "verdicts.is_u16_69_timing_table", False),
    ("s338_block_identity/block_identity.json", "dfe_block.register", "0xfc02a00c"),
    ("s338_block_identity/block_identity.json", "verdicts.p2s_transport_affected", False),
    ("s339_block_f292b/block_f292b.json", "verdicts.identity", "NO_VERIFICADO"),
    ("s340_w0_selector/w0_selector.json", "verdicts.w0_is_mmio_selector", True),
    ("s340_w0_selector/w0_selector.json", "switch.case_count", 6),
]


def get(data: Any, path: str) -> Any:
    cur = data
    for part in path.split("."):
        cur = cur[part]
    return cur


def main() -> int:
    ok = 0
    fails: list[str] = []
    for rel, path, expected in CHECKS:
        f = A / rel
        if not f.exists():
            fails.append(f"falta {rel}")
            continue
        try:
            value = get(json.loads(f.read_text(encoding="utf-8")), path)
        except (KeyError, TypeError) as exc:
            fails.append(f"{rel}:{path} no resoluble ({exc})")
            continue
        if value == expected:
            ok += 1
        else:
            fails.append(f"{rel}:{path} = {value!r}, esperado {expected!r}")
    print(f"{ok} cifras verificadas, {len(fails)} fallos")
    for msg in fails:
        print("  FALLO:", msg)
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
