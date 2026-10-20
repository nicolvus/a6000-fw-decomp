"""Candidatos Thumb PIC crudos; exigen contraste posterior con listado y flujo."""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000


def main() -> None:
    blob = (ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin").read_bytes()
    pending: dict[int, list[tuple[int, int, int]]] = {}
    rows = []
    for offset in range(0, len(blob) - 4, 2):
        half = struct.unpack_from("<H", blob, offset)[0]
        address = BASE + offset
        if half & 0xFF78 == 0x4478:
            reg = half & 7 | (half >> 4 & 8)
            for value, site, literal in pending.get(reg, []):
                target = (value + address + 4) & 0xFFFFFFFF
                if address - site < 128 and 0x43ED4000 <= target < 0x43ED4800:
                    rows.append({"site": hex(address), "target": hex(target),
                                 "load": hex(site), "literal": hex(literal)})
        if half & 0xF800 == 0x4800:
            reg = half >> 8 & 7
            literal = ((address + 4) & ~3) + (half & 255) * 4
        elif half in (0xF8DF, 0xF85F):
            tail = struct.unpack_from("<H", blob, offset + 2)[0]
            reg = tail >> 12
            delta = tail & 0xFFF
            literal = ((address + 4) & ~3) + (delta if half == 0xF8DF else -delta)
        else:
            continue
        if BASE <= literal <= BASE + len(blob) - 4:
            recent = [item for item in pending.get(reg, []) if address - item[1] < 128]
            recent.append((struct.unpack_from("<I", blob, literal - BASE)[0], address, literal))
            pending[reg] = recent
    (ROOT / "analysis/ghidra/s47-raw-pic.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
