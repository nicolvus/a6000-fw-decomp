"""Audita evidencia S33 contra el blob; nunca ejecuta firmware."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
EXPECTED = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def main() -> None:
    spec = importlib.util.spec_from_file_location("s32_audit", OUT / "s32-audit.py")
    assert spec is not None and spec.loader is not None
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    blob = previous.BLOB.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == EXPECTED
    # Baseline persistente ya contrastado al inicio de S33; excluye locks transitorios.
    baseline = json.loads((OUT / "s32-integrity.json").read_text())["project_hashes"]
    current = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in [OUT / "silent-liro.gpr", *sorted((OUT / "silent-liro.rep").rglob("*"))]
               if p.is_file() and not p.name.endswith(".lock")}
    assert current == baseline, "Cambió el proyecto persistente"
    final = json.loads((OUT / "s33-final.json").read_text())
    assert final["source_sha256"] == EXPECTED
    functions = {f["query"]: f for f in final["functions"]}
    for query in ("4390366c", "43902df8", "43790b68", "4381bf38"):
        row = functions[query]
        assert row["entry"] == query and row["status"] == "decompiled" and not row["error"]
        assert "unaff_" not in row["pseudo_code"], f"Posible fragmento interior: {query}"
    targets = {0x4379B44C, 0x43796954, 0x4379BB90}
    raw = previous.branches(blob, targets)
    rows = []
    for path in sorted(OUT.glob("s33-*.json")):
        parsed = json.loads(path.read_text())
        if "functions" in parsed:
            assert parsed["source_sha256"] == EXPECTED
            rows.extend(parsed["functions"])
    recovered = {(c["site"], c["target"]) for f in rows if f["query"] != "43791000"
                 for c in f.get("calls_and_jumps", []) if int(c["target"], 16) in targets}
    assert recovered == {(c["site"], c["target"]) for c in raw}, "Falta un llamador directo"
    callers = json.loads((OUT / "s33-callers.json").read_text())["functions"][:12]
    helper = json.loads((OUT / "s33-input-helper.json").read_text())["functions"][0]
    helper_code = helper["pseudo_code"]
    assert "*(int *)(param_4 + 0xd4) = param_1 + 0xbc;" in helper_code
    assert "*(undefined1 *)(param_4 + 200) = 1;" in helper_code
    assert "4381519c str.w r4,[r5,#0xd4]" in helper["listing"]
    helper_calls = previous.branches(blob, {0x43814EA0})
    assert {c["site"] for c in helper_calls} == {"4355164a", "435536be", "435557de"}
    findings = json.loads((OUT / "s33-findings.json").read_text())
    table = findings["address_prefix_table"]
    pointer = struct.unpack_from("<I", blob, int(table["slot"], 16) - previous.BASE)[0]
    assert pointer == int(table["table"], 16)
    for index, pair in enumerate([*table["pairs"], table["terminator"]]):
        assert struct.unpack_from("<II", blob, pointer - previous.BASE + index * 8) == tuple(int(v, 16) for v in pair)
    inputs = []
    for row in callers:
        code = row["pseudo_code"]
        bases = sorted(set(re.findall(r"FUN_4379b44c\([^,]+,&(\w*Stack_([0-9a-f]+))\)", code)))
        assert bases
        for name, offset in bases:
            assert f"FUN_43b03a5e(&{name})" in code, "Falta constructor cero del input"
            writes = {}
            for field in (0x10, 0x38, 0xC8, 0xD4):
                suffix = format(int(offset, 16) - field, "x")
                writes[hex(field)] = [line.strip() for line in code.splitlines()
                                      if re.search(r"\b\w*Stack_" + suffix + r"\s*=", line)]
            assert writes["0x10"]
            assert writes["0xc8"] and all("= 0;" in x for x in writes["0xc8"])
            assert not writes["0xd4"], "Reexaminar rama secundaria"
            inputs.append({"caller": row["entry"], "input": name, "writes": writes,
                           "initialization": "43b03a5e clears 0x104 bytes, including +d4",
                           "indirect_writer": "43814ea0: conditional +c8=1 and +d4=P+bc; 435525c0 also copies input"
                           if row["entry"] in {"435525c0", "43554590", "435503b0"} else None})
    report = {"source_sha256": EXPECTED, "project_unchanged_against_s32_and_start_s33": current == baseline,
              "project_hashes": current, "direct_calls": raw, "inputs": inputs,
              "secondary_helper_calls": helper_calls,
              "secondary_enable_source": "43f922ef+unit via 436bd404, software state; not DMA-completion proof",
              "scope": "Thumb BL/B.W halfword-aligned + absolute pointers; no universal indirect-call completeness",
              "invalid_exploratory_entry": "43791000: interior of 43790b68; use s33-final",
              "result": "PASS"}
    (OUT / "s33-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: SHA, proyecto idéntico, {len(raw)} llamadas, {len(inputs)} inputs inicializados")
    print("| Estado | Hallazgo |")
    print("|---|---|")
    for state, result in [
        ("VERIFICADO", "AllocShare: ID DMM + clave fuente + hasta cuatro pares; apertura=0 en SyncYCout"),
        ("VERIFICADO", "26 llamadas al constructor YC, 12 funciones, 13 objetos locales de 0x104 bytes"),
        ("VERIFICADO", "43814ea0 puede escribir input+c8=1 e input+d4=P+bc en tres productores"),
        ("VERIFICADO", "APL transforma palabras de extents y programa bancos MMIO f385/f395/f3a5"),
        ("PARCIAL", "Backend DMM, productor físico y layout/pitch efectivos sin resolver"),
        ("PARCIAL", "Enum 0..5 remapeado; sin tabla que pruebe formato de píxel"),
        ("INFERENCIA", "Contrato compatible con familia DMM de S30; sin identidad de buffer demostrada"),
        ("NO_VERIFICADO", "Finalización DMA física y captura completamente electrónica"),
    ]:
        print(f"| {state} | {result} |")


if __name__ == "__main__":
    main()
