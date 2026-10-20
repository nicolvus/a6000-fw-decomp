"""Inventaría literales de destino exacto; las coincidencias no prueban ejecución."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
BASE = 0x43541000
TARGETS = (0x301D7, 0x800301D7, 0x43789CC0, 0x43789CC1,
           0x43789708, 0x43789709, 0x43FF23B0, 0x43FF29B8,
           0x435412A0, 0x435410B4)


def locations(blob: bytes, value: int) -> list[int]:
    needle = struct.pack("<I", value)
    result = []
    cursor = 0
    while (cursor := blob.find(needle, cursor)) >= 0:
        result.append(cursor)
        cursor += 1
    return result


def main() -> None:
    tree = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked"
    fw = tree / "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
    blob = fw.read_bytes()
    rows = {hex(value): [hex(BASE + offset) for offset in locations(blob, value)]
            for value in TARGETS}
    external = []
    files = 0
    for path in sorted(tree.rglob("*")):
        if not path.is_file() or path.is_symlink() or path == fw:
            continue
        files += 1
        data = path.read_bytes()
        hits = {hex(value): [hex(offset) for offset in locations(data, value)]
                for value in TARGETS[:2] if struct.pack("<I", value) in data}
        if hits:
            external.append({"path": str(path.relative_to(ROOT)), "offsets": hits,
                             "sha256": hashlib.sha256(data).hexdigest(),
                             "elf": data[:4] == b"\x7fELF"})
    result = {"literal_addresses": rows, "external_file_count": files,
              "external_matches": external,
              "limitation": "Solo u32 literales; no descarta IDs calculados, tablas o transportes indirectos."}
    (OUT / "s48-literals.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"Literales av-cam: { {key: len(value) for key, value in rows.items()} }")
    print(f"Otros archivos examinados: {files}; coincidencias: {len(external)}")
    for row in external:
        print(row["path"], row["offsets"])


if __name__ == "__main__":
    main()
