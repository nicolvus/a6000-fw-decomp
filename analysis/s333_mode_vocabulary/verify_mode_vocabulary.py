#!/usr/bin/env python3
"""S333 - verificacion independiente de `mode_vocabulary.json`.

Uso: ``.venv/bin/python analysis/s333_mode_vocabulary/verify_mode_vocabulary.py``
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

BASE = 0x43541000
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
DATA = HERE / "mode_vocabulary.json"

OK = 0
FAIL: list[str] = []


def check(cond: bool, msg: str) -> None:
    global OK
    if cond:
        OK += 1
    else:
        FAIL.append(msg)


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    a6 = A6000.read_bytes()
    a7 = A7S.read_bytes()
    check(hashlib.sha256(a6).hexdigest() == data["firmware"]["a6000_fw321"]["sha256"],
          "sha256 A6000")
    check(hashlib.sha256(a7).hexdigest() == data["firmware"]["a7s_fw320"]["sha256"],
          "sha256 A7S")

    # matrices y terminadores
    a6_base = u32(a6, 0x44022F8C)
    check(f"0x{a6_base:08x}" == data["a6000"]["matrix"], "A6000 base de matriz")
    a6_rows, i = [], 0
    while True:
        dest = u32(a6, a6_base + 0x14 * i)
        if dest == 0:
            break
        a6_rows.append((dest, list(a6[a6_base - BASE + 0x14 * i + 4:
                                     a6_base - BASE + 0x14 * i + 20])))
        i += 1
    check(len(a6_rows) == data["a6000"]["rows"] == 59, "A6000 59 filas")
    check(f"0x{a6_base + 0x14 * i:08x}" == data["a6000"]["terminator"],
          "A6000 terminador")

    a7_base = 0x43FEE598
    check(f"0x{a7_base:08x}" == data["a7s"]["matrix"], "A7S base")
    a7_rows, j = [], 0
    while True:
        dest = u32(a7, a7_base + 0x14 * j)
        if dest == 0:
            break
        a7_rows.append((dest, list(a7[a7_base - BASE + 0x14 * j + 4:
                                      a7_base - BASE + 0x14 * j + 20])))
        j += 1
    check(len(a7_rows) == data["a7s"]["rows"] == 69, "A7S 69 filas")

    # columnas
    a6_codes = [u32(a6, 0x43FEA070 + 4 * k) for k in range(13)]
    check([f"0x{c:02x}" for c in a6_codes] == data["a6000"]["codes"],
          "A6000 codigos")
    vec6 = {f"0x{c:02x}": tuple(r[1][k] for r in a6_rows)
            for k, c in enumerate(a6_codes)}
    check(len(set(vec6.values())) == data["a6000"]["columns"]["distinct_vectors"] == 7,
          "A6000 7 vectores")
    groups: dict[tuple[int, ...], list[str]] = {}
    for code, vec in vec6.items():
        groups.setdefault(vec, []).append(code)
    aliases = sorted(sorted(g) for g in groups.values() if len(g) > 1)
    check(aliases == data["a6000"]["columns"]["aliases"], "A6000 alias")

    a7_codes = [u32(a7, 0x43FEE370 + 4 * k) for k in range(34)]
    colmap = list(a7[0x43C9C5B5 - BASE:0x43C9C5B5 - BASE + 34])
    check(colmap == data["a7s"]["position_map"], "A7S mapa")
    vec7 = {f"0x{c:02x}": tuple(r[1][colmap[k]] for r in a7_rows)
            for k, c in enumerate(a7_codes)}
    check(len(set(vec7.values())) == data["a7s"]["columns"]["distinct_vectors"] == 15,
          "A7S 15 vectores distintos")
    groups7: dict[tuple[int, ...], list[str]] = {}
    for code, vec in vec7.items():
        groups7.setdefault(vec, []).append(code)
    alias7 = sorted(sorted(g) for g in groups7.values() if len(g) > 1)
    check(alias7 == data["a7s"]["columns"]["aliases"], "A7S alias")
    check(len(alias7) == data["verdicts"]["a7s_alias_groups"] == 12,
          "A7S 12 grupos de alias")

    # vocabulario
    voc = data["vocabulary"]
    shared = set(a6_codes) & set(a7_codes)
    check([f"0x{c:02x}" for c in sorted(shared)] == voc["shared"], "compartidos")
    check([f"0x{c:02x}" for c in sorted(set(a6_codes) - set(a7_codes))] ==
          voc["a6000_only"] == ["0x2f"], "solo A6000")
    check(len(voc["a7s_only"]) == 22, "22 solo A7S")
    check(voc["counts"] == {"a6000": 13, "a7s": 34, "shared": 12}, "conteos")

    silent = {"0x4c", "0x4d", "0x4e", "0x4f", "0x50", "0x51"}
    check(not (silent & {f"0x{c:02x}" for c in a6_codes}), "A6000 sin silent")
    check(sorted(silent & set(voc["a7s_only"])) == data["verdicts"]["silent_codes_a7s_only"],
          "silent solo en A7S")

    print(f"{OK} comprobaciones OK, {len(FAIL)} fallos")
    for msg in FAIL:
        print("  FALLO:", msg)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
