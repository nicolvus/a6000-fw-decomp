"""Contrasta evidencia estática S50; no ejecuta instrucciones del firmware."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = 0x43541000
EXPECTED = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def main() -> None:
    raw = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED

    def word(address: int) -> int:
        return struct.unpack_from("<I", raw, address - BASE)[0]

    elf_path = ROOT / "analysis/rea-independent/run/av-cam-view.elf"
    elf = elf_path.read_bytes()
    shoff = struct.unpack_from("<I", elf, 32)[0]
    size, count = struct.unpack_from("<HH", elf, 46)
    code = []
    for index in range(count):
        header = struct.unpack_from("<10I", elf, shoff + index * size)
        if header[2] & 4:
            code.append(elf[header[4] : header[4] + header[5]])
    assert code == [raw]

    checks = []
    batch_items = []
    for path in sorted(OUT.glob("0[1-5]-*.jsonl")):
        for line in path.read_text().splitlines():
            row = json.loads(line)
            result = row.get("result", {}).get("structuredContent", {}).get("normalized_result")
            if row["call"]["tool"] == "read_bytes" and isinstance(result, dict):
                address = int(result["address"], 16)
                actual = bytes.fromhex(result["bytes_hex"])
                assert actual == raw[address - BASE : address - BASE + len(actual)]
                checks.append({"file": path.name, "address": hex(address), "bytes": len(actual)})
            if row["call"]["tool"] == "batch_decompile" and isinstance(result, dict):
                for item in result["items"]:
                    batch_items.append({
                        "query": item["address"],
                        "status": item["status"],
                        "canonical": item.get("procedure", {}).get("address"),
                    })

    historical_functions = []
    for path in sorted(OUT.glob("0[6-9]-*.json")):
        historical = json.loads(path.read_text())
        assert historical["sha256"] == EXPECTED
        for function in historical["functions"]:
            address = int(function["query"], 16)
            assert bytes.fromhex(function["raw64"]) == raw[address - BASE : address - BASE + 64]
            historical_functions.append({"file": path.name, **function})

    ranges = {
        "exposure-switch": (0x436D70BE, 0x436D71E8),
        "stage-gate": (0x438C2538, 0x438C2730),
        "stage-pic": (0x438C27BC, 0x438C2804),
        "curtain-request": (0x438D033C, 0x438D03FC),
        "capture-cancel": (0x437DF5D6, 0x437DF5F6),
        "copy-field": (0x438ACC7C, 0x438ACCB4),
        "error-flags": (0x43AE7636, 0x43AE7660),
        "outer-selector": (0x437EABFC, 0x437EAC98),
        "special-row": (0x43B1C0E2, 0x43B1C118),
        "exposure-selector": (0x437EA8CC, 0x437EABF0),
        "service-copy": (0x43AF6870, 0x43AF68A0),
        "exposure-getter": (0x43AD9202, 0x43AD920A),
        "init-table": (0x437EBED8, 0x437EBFD2),
        "special-stage": (0x43B1D9DC, 0x43B1DA80),
        "special-caif": (0x438D0D30, 0x438D0DC8),
        "initial-request": (0x438D0420, 0x438D050C),
        "descriptor-init": (0x437DE944, 0x437DE980),
        "callback-dispatch": (0x437DA2D8, 0x437DA378),
        "callback-count-copy": (0x43AF6870, 0x43AF68D0),
        "tag12-dispatch": (0x436B93B0, 0x436B942C),
        "tag12-mmio-thunk": (0x43B5E2B0, 0x43B5E2BC),
        "tag12-mmio": (0x4398F9A4, 0x4398F9DE),
    }
    listings = {}
    for label, (start, end) in ranges.items():
        command = [
            "llvm-objdump", "-D", "--triple=thumbv7-none-eabi", "--adjust-vma=0x43541000",
            f"--start-address={hex(start - BASE)}", f"--stop-address={hex(end - BASE)}", str(elf_path),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        assert re.search(r"^[0-9a-f]{8}:", result.stdout, re.MULTILINE), label
        listings[label] = {"command": command, "stdout": result.stdout, "stderr": result.stderr}

    table_address = 0x436D70CA
    table = raw[table_address - BASE : table_address - BASE + 5]
    destinations = [table_address + 2 * value for value in table]
    assert destinations == [0x436D70D0, 0x436D70E0, 0x436D7114, 0x436D717A, 0x436D71AE]
    pic_base = (word(0x438C27BC) + 0x438C2546) & 0xFFFFFFFF
    diag_slot = (pic_base + word(0x438C27C0)) & 0xFFFFFFFF
    assert (pic_base, diag_slot, word(diag_slot)) == (0x4401EEE4, 0x4402546C, 0x43E95950)
    assert (word(0x437ECCB4) + 0x437EBEE6) & 0xFFFFFFFF == 0x4401EEE4
    assert word(0x4401EEE4 + word(0x437ECCB8)) == 0x43EDCCF8
    assert word(0x4401EEE4 + word(0x437ECCF8)) == 0x43B1C0E3
    geometry = [word(0x43BC16DC + 28), word(0x43BC16DC + 60)]
    assert geometry == [6000, 4000]
    assert [word(0x43BC1AE8), word(0x43BC1AEC)] == [864, 4176]
    callbacks = []
    for key, slot, count, *_ in json.loads((ROOT / "analysis/s49/rows2.json").read_text()):
        if key in [0xCE, 0xB7, 0xBA, 0xB8]:
            callbacks.append({
                "key": hex(key), "slot": hex(slot), "count": count,
                "callbacks": [hex(word(slot + 4 * index)) for index in range(count)],
            })

    mismatches = []
    protected = 0
    for line in (ROOT / "analysis/s50/shared/sha256-initial.txt").read_text().splitlines():
        if not line.strip():
            continue
        expected, name = line.split(None, 1)
        path = ROOT / name.strip()
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        protected += 1
        if digest.hexdigest() != expected:
            mismatches.append(name)
    assert not mismatches, mismatches
    metrics = list(csv.DictReader((OUT / "run/metrics.csv").open()))
    summary = {
        "sha256": EXPECTED, "protected_files": protected, "mismatches": mismatches,
        "rea_byte_reads": checks, "batch_items": batch_items,
        "historical_functions": [
            {key: row.get(key) for key in ["file", "query", "entry", "completed", "status"]}
            for row in historical_functions
        ],
        "callback_lists": callbacks,
        "geometry_row": {"address": "0x43bc16dc", "dimensions": geometry},
        "tbb_destinations": [hex(value) for value in destinations],
        "stage_diag": {"pic": hex(pic_base), "slot": hex(diag_slot), "object": hex(word(diag_slot))},
        "metrics": {
            "samples": len(metrics), "start_ts": metrics[0]["ts"], "last_ts": metrics[-1]["ts"],
            "peak_rss_mb": max(int(row["rss_mb"]) for row in metrics),
            "min_available_mb": min(int(row["mem_available_mb"]) for row in metrics),
        },
    }
    (OUT / "llvm-evidence.json").write_text(json.dumps(listings, indent=2) + "\n")
    (OUT / "audit-result.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({
        "result": "PASS", "protected_files": protected, "rea_byte_reads": len(checks),
        "historical_functions": len(historical_functions), "llvm_ranges": len(listings),
        "metrics": summary["metrics"],
    }))


if __name__ == "__main__":
    main()
