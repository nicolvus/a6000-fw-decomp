"""Equivalencia estática A6000↔A7S de RecordStill, RecordImage y sus destinos locales (flujo alcanzable normalizado)."""

import hashlib
import json
from pathlib import Path
from typing import Any

import s402_fw as fw

OUT = Path(__file__).with_name("recordstill_equivalence.json")
ROOTS = {"RecordStill": (0x908AFC, 0x847E1C), "RecordImage_Execute": (0x90B248, 0x84A568)}
LOCAL_PAIRS = [(0x37CC14, 0x27DC78), (0x38CB9C, 0x286CBC), (0x8FDC04, 0x83C504), (0x915F04, 0x84E824),
               (0x8FDC70, 0x83C570), (0x8FDCDC, 0x83C5DC), (0x8FE0A0, 0x83C9A0), (0x90F038, 0x840618)]


def build() -> dict:
    a, b = fw.Lib("A6000"), fw.Lib("A7S")
    result: dict[str, Any] = {"limits": ("Flujo alcanzable por descenso recursivo; excluye pools, tablas y cleanup de excepciones. "
                         "Llamadas indirectas (blx reg, vtables) no se siguen. Emparejado de destinos por posición. "
                         "No prueba equivalencia física ni de datos en tiempo de ejecución."),
              "sha256": {m: hashlib.sha256(x.e.data).hexdigest() for m, x in (("A6000", a), ("A7S", b))}, "roots": {}}
    for name, (pa, pb) in ROOTS.items():
        pairs = fw.closure(a, b, pa, pb)
        result["roots"][name] = {
            "A6000": hex(pa), "A7S": hex(pb), "pairs": len(pairs),
            "identical": sum(v["identical"] for v in pairs.values()),
            "differ_only_in_source_line": sum(not v["identical"] and not v["residue"] for v in pairs.values()),
            "with_other_differences": sum(bool(v["residue"]) for v in pairs.values()),
            "local_pairs_present": {f"{x:#x}/{y:#x}": (x, y) in pairs for x, y in LOCAL_PAIRS},
            "root_identical_modulo_lines": not pairs[(pa, pb)]["residue"],
            "root_instruction_count": pairs[(pa, pb)]["len"],
        }
    return result


if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(json.dumps({k: {x: y for x, y in v.items() if x != "local_pairs_present"} for k, v in data["roots"].items()}))
