#!/usr/bin/env python3
"""S337 - verificacion independiente de `fef404_table.json`.

Uso: ``.venv/bin/python analysis/s337_fef404_table/verify_fef404_table.py``
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
DATA = HERE / "fef404_table.json"

OK = 0
FAIL: list[str] = []


def check(cond: bool, msg: str) -> None:
    global OK
    if cond:
        OK += 1
    else:
        FAIL.append(msg)


def u16(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<H", blob, addr - BASE)[0]


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    blob = A7S.read_bytes()
    check(hashlib.sha256(blob).hexdigest() == data["firmware"]["a7s_fw320"]["sha256"],
          "sha256 A7S")

    table = data["table"]
    base = int(table["address"], 16)
    check(base == 0x43FEF404, "direccion")
    entries = []
    addr = base
    while u16(blob, addr + 2) == 0x000D:
        entries.append((u16(blob, addr), u16(blob, addr + 2)))
        addr += 4
    check(len(entries) == table["entries"] == 69, "69 entradas")
    check(all(second == 0x000D for _, second in entries), "segundo campo 0x000d")
    check([c for c, _ in entries] == table["codes"], "codigos")
    check(f"0x{addr:08x}" == table["end"], "fin")

    # el «array de 69 u16» de S329 cruzaba dos estructuras
    vals = struct.unpack_from("<69H", blob, base - BASE)
    # la vista u16 mezcla codigos y el valor constante 0x000d
    check(vals.count(0x000D) >= 30, "u16[69]: contiene 0x000d repetido")
    check(max(vals) <= max(c for c, _ in entries) and 0x000D in vals,
          "u16[69]: vista mezclada codigos/0x000d")

    # prefijo constante
    back = base - 4
    count = 0
    while u32(blob, back) == 0x43F9C622:
        count += 1
        back -= 4
    check(count == data["prefix_43f9c622"]["count"], "prefijo 0x43f9c622")

    # sin referencias literales
    check(data["literal_references"] == [], "sin referencias literales")
    v = data["verdicts"]
    check(v["is_u16_69_timing_table"] is False, "no es tabla de tiempos")
    check(v["static_consumer"] is False, "sin consumidor estatico")

    print(f"{OK} comprobaciones OK, {len(FAIL)} fallos")
    for msg in FAIL:
        print("  FALLO:", msg)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
