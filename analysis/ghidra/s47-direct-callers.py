"""Busca BL/BLX/B.W en bytes originales, incluso fuera de funciones definidas."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
TARGETS = {0x437D9F9C, 0x437DA100}


def main() -> None:
    targets = {int(arg, 0) for arg in sys.argv[2:]} if len(sys.argv) > 2 else TARGETS
    blob = (ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin").read_bytes()
    halves = memoryview(blob).cast("H")
    rows = []
    for index in range(len(halves) - 1):
        first, second = halves[index:index + 2]
        if first & 0xF800 != 0xF000 or not second & 0x8000:
            continue
        kind = {0x5000: "bl", 0x4000: "blx", 0x1000: "b.w"}.get(second & 0x5000)
        if kind is None:
            continue
        sign = first >> 10 & 1
        high1 = ~(second >> 13 & 1 ^ sign) & 1
        high2 = ~(second >> 11 & 1 ^ sign) & 1
        delta = (sign << 24 | high1 << 23 | high2 << 22 |
                 (first & 0x3FF) << 12 | (second & 0x7FF) << 1)
        if sign:
            delta -= 1 << 25
        site = BASE + 2 * index
        target = site + 4 + delta
        if kind == "blx":
            target &= ~3
        if target in targets:
            rows.append({"site": hex(site), "kind": kind, "target": hex(target)})
    output = sys.argv[1] if len(sys.argv) > 1 else "s47-direct-callers.json"
    (ROOT / "analysis/ghidra" / output).write_text(json.dumps(rows, indent=2) + "\n")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
