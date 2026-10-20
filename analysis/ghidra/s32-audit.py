"""Contrasta exports estáticos S32 con los bytes originales, sin ejecutar firmware."""

from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
BLOB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE = 0x43541000
EXPECTED = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def branches(data: bytes, targets: set[int]) -> list[dict[str, str]]:
    """Decodifica B.W/BL Thumb-2; candidatos crudos, contrastables con el listing."""
    hits = []
    for offset in range(0, len(data) - 3, 2):
        first, second = struct.unpack_from("<HH", data, offset)
        if first & 0xF800 != 0xF000 or second & 0xD000 not in (0x9000, 0xD000):
            continue
        sign = (first >> 10) & 1
        i1 = 1 ^ ((second >> 13) & 1) ^ sign
        i2 = 1 ^ ((second >> 11) & 1) ^ sign
        immediate = (sign << 24) | (i1 << 23) | (i2 << 22)
        immediate |= ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
        if sign:
            immediate -= 1 << 25
        target = (BASE + offset + 4 + immediate) & 0xFFFFFFFF
        if target in targets:
            hits.append({"site": f"{BASE + offset:08x}", "target": f"{target:08x}",
                         "kind": "BL" if second & 0x4000 else "B.W"})
    return hits


def pic_candidates(data: bytes, targets: set[int]) -> list[dict[str, str]]:
    """Busca LDR literal T1 + ADD PC; no presume continuidad ni flujo válido."""
    hits = []
    for offset in range(2, len(data) - 2, 2):
        instruction = struct.unpack_from("<H", data, offset)[0]
        if instruction & 0xFF78 != 0x4478:
            continue
        register = (instruction & 7) | ((instruction >> 4) & 8)
        for previous in range(max(0, offset - 40), offset, 2):
            load = struct.unpack_from("<H", data, previous)[0]
            if load & 0xF800 != 0x4800 or (load >> 8) & 7 != register:
                continue
            pool = ((previous + 4) & ~3) + (load & 255) * 4
            if pool + 4 > len(data):
                continue
            target = (struct.unpack_from("<I", data, pool)[0] + BASE + offset + 4) & 0xFFFFFFFF
            if target in targets:
                hits.append({"ldr": f"{BASE + previous:08x}", "pool": f"{BASE + pool:08x}",
                             "add": f"{BASE + offset:08x}", "target": f"{target:08x}",
                             "register": f"r{register}"})
    return hits


def main() -> None:
    data = BLOB.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == EXPECTED, "SHA-256 del blob incorrecto"
    project_files = [OUT / "silent-liro.gpr", *sorted((OUT / "silent-liro.rep").rglob("*"))]
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in project_files if path.is_file() and not path.name.endswith(".lock")}
    manifest_path = OUT / "s32-integrity.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        assert manifest["project_hashes"] == hashes, "Cambió un archivo persistente del proyecto"
        manifest["subsequent_check"] = "all persistent project file contents unchanged"
    else:
        manifest = {"source_sha256": digest, "project_hashes": hashes,
                    "scope": "baseline captured after initial readOnly exports; subsequent export compared byte-for-byte"}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    targets = {0x43AD6034, 0x43AD6052, 0x4379704C, 0x43797090}
    raw = branches(data, targets)
    rows = []
    exports = []
    for path in sorted(OUT.glob("s32-*.json")):
        parsed = json.loads(path.read_text())
        if "functions" not in parsed:
            continue
        assert parsed["source_sha256"] == EXPECTED
        exports.append(path.name)
        rows.extend(parsed["functions"])
    expected_branches = set()
    for row in rows:
        for call in row.get("calls_and_jumps", []):
            if int(call["target"], 16) in targets:
                expected_branches.add((call["site"], call["target"]))
    decoded = {(hit["site"], hit["target"]) for hit in raw}
    assert expected_branches <= decoded, f"Decodificador difiere de Ghidra: {expected_branches - decoded}"
    assert {(site, "43ad6034") for site in ("43ad6052", "437b6668", "437d0c18")} == {
        pair for pair in decoded if pair[1] == "43ad6034"
    }
    required = {"43796954", "4379bb90", "43797afc", "43797b10", "43797b24", "43797b38", "435a9928"}
    assert required <= {row["query"] for row in rows if row.get("status") == "decompiled"}
    findings = json.loads((OUT / "s32-findings.json").read_text())
    for branch, registrar in (("VD_Drive", "4379704c"), ("VD_Post", "43797090")):
        documented = {site.removeprefix("0x")
                      for sites in findings["registrar_callsites_by_real_target"][branch].values()
                      for site in sites}
        actual = {site for site, target in decoded if target == registrar}
        assert actual == documented, f"Callsites faltantes/extras en {branch}: {actual ^ documented}"
    for slot, expected in findings["original_pointer_slots"].items():
        value = struct.unpack_from("<I", data, int(slot, 16) - BASE)[0]
        assert value == int(expected, 16), f"Slot incorrecto: {slot}"
    words = []
    for address in (0x440259B4, 0x44026238, 0x440204B4, 0x44020EE4,
                    0x44023820, 0x44021E0C, 0x440212AC, 0x44023940):
        value = struct.unpack_from("<I", data, address - BASE)[0]
        words.append({"slot": f"{address:08x}", "value": f"{value:08x}",
                      "thumb_entry_if_code": f"{value & ~1:08x}"})
    strings = []
    for match in re.finditer(b"YC out window overflow", data):
        start = data.rfind(b"\0", 0, match.start()) + 1
        end = data.index(b"\0", match.start())
        strings.append({"string_start": f"{BASE + start:08x}",
                        "phrase_address": f"{BASE + match.start():08x}",
                        "file_offset": f"{match.start():x}",
                        "text": data[start:end].decode("ascii")})
    invalid = {"43796522", "435498ca", "43549d42"}
    failures = [{"query": row["query"], "status": row.get("status"),
                 "error": row.get("error", "")}
                for row in rows if row.get("status") not in (None, "decompiled")]
    report = {
        "source_sha256": digest,
        "physical_behavior": "NO_VERIFICADO: no camera, no firmware execution",
        "raw_branch_scope": "all halfword-aligned B.W/BL encodings in original blob; may include data false positives",
        "raw_branches": raw,
        "ghidra_branches_crosschecked": len(expected_branches),
        "pic_scope": "heuristic candidates only; validate live register flow using Ghidra instructions",
        "pic_candidates": pic_candidates(data, {0x43E9D7A8, 0x43E9D7E4, 0x43CA519F, 0x43CA51AC}),
        "original_pointer_slots": words,
        "overflow_strings": strings,
        "exports": exports,
        "export_failures": failures,
        "do_not_treat_as_function_entries": sorted(invalid),
        "boundary_note": "Exploratory callsite/interior queries above are partial fragments, not full functions. 4379cdb0 has no function; use complete 4379bb90 export.",
    }
    (OUT / "s32-raw-evidence.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"SHA-256 OK; {len(raw)} raw branches; {len(expected_branches)} Ghidra branches checked; {len(rows)} queries")
    print("\n| Estado | Dirección | Hallazgo / evidencia estática |")
    print("|---|---|---|")
    summary = [
        ("VERIFICADO", "0x43ad6034 / 0x43ad6052", "Despachador BLX y thunk; 3 xrefs directas + 26 al thunk"),
        ("VERIFICADO", "0x4380f5b4 / 0x4379704c / 0x43797090", "Construcción y copia del callback a las listas VD"),
        ("VERIFICADO", "0x43811324 / 0x43b03abe", "Destinos Drive, vía adaptador 0x43b03a48; 12 altas directas"),
        ("VERIFICADO", "0x438106ec / 0x43810e7c / 0x4381061c / 0x4354a678", "Destinos Post; 14 altas directas"),
        ("VERIFICADO", "0x43796954 / 0x4379bb90", "Decompilación completa: 372 / 671 líneas, sin error"),
        ("VERIFICADO", "0x4379cb2e", "YC overflow: reloj menos inicio frente a ventana; no flag DMA"),
        ("VERIFICADO", "0x4379b44c -> 0x4390366c", "Productor de bloque YC con handle DMM compartido y geometría"),
        ("PARCIAL", "0x43e9f388 / 0x435a9928", "Faltan mapeo del handle a píxeles, pitch/formato y consumidor efectivo"),
        ("INFERENCIA", "0x43ad6034", "Codificación compatible con puntero a método C++ ARM"),
        ("NO_VERIFICADO", "hardware", "Sin cámara ni ejecución de firmware; fin DMA/captura silenciosa no observados"),
    ]
    for status, location, evidence in summary:
        print(f"| {status} | {location} | {evidence} |")


if __name__ == "__main__":
    main()
