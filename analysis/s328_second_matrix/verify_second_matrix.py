#!/usr/bin/env python3
"""S328 - verificador independiente de second_matrix.json."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
JSON = Path(__file__).with_name("second_matrix.json")

checks = 0


def ok(cond: bool, msg: str) -> None:
    global checks
    if not cond:
        raise SystemExit(f"FALLO: {msg}")
    checks += 1


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def u16(b: bytes, a: int) -> int:
    return struct.unpack_from("<H", b, a - BASE)[0]


def u32(b: bytes, a: int) -> int:
    return struct.unpack_from("<I", b, a - BASE)[0]


def main() -> None:
    d = json.loads(JSON.read_text(encoding="utf-8"))
    a7s = A7S.read_bytes()
    a6 = A6000.read_bytes()

    ok(sha256(A7S) == d["firmware"]["a7s_fw320"]["sha256"], "sha256 A7S")
    ok(sha256(A6000) == d["firmware"]["a6000_fw321"]["sha256"], "sha256 A6000")

    for name, blob, slot, base, off, site, table in (
            ("a7s_fw320", a7s, 0x44026088, 0x44024540, 0x1B48, 0x436F394E, 0x43E8DE00),
            ("a6000_fw321", a6, 0x44026694, 0x4401EEE4, 0x77B0, 0x436D65A0, 0x43E80160)):
        e = d["cases"][name]
        ok(e["slot"] == f"0x{slot:08x}", f"{name}: slot")
        ok(e["slot_base"] == f"0x{base:08x}", f"{name}: base")
        ok(base + off == slot, f"{name}: base + offset = slot")
        ok(u32(blob, slot) == table, f"{name}: contenido del slot")
        ok(e["slot_value"] == f"0x{table:08x}", f"{name}: valor en el JSON")
        ok(e["offset_sites"] == [f"0x{site:08x}"], f"{name}: unico sitio del offset")
        h = u16(blob, site)
        ok((h & 0xF800) == 0x4800, f"{name}: instruccion ldr")
        lit = ((site + 4) & ~3) + (h & 0xFF) * 4
        ok(u32(blob, lit) == off, f"{name}: literal = offset")
        ok(e["slot_value_refs"] == [f"0x{slot:08x}"], f"{name}: unico literal del valor")
        ok(e["table_nonzero_bytes_64"] == sum(1 for b in
                                             blob[table - BASE:table - BASE + 0x40] if b) == 0,
           f"{name}: tabla a cero")
        ok(e["table_first_word"] == f"0x{u32(blob, table):08x}" == "0x00000000",
           f"{name}: primera palabra = terminador")

    v = d["verdict"]
    ok(v["static_producer"] is False, "sin productor estatico")
    ok(v["loop_executes_on_blob"] is False, "el bucle no ejecuta")
    ok(any("runtime" in x for x in d["scope_limit"]), "limite de runtime")
    ok("S51" in v["s51"] or "sin cambios" in v["s51"], "S51 declarado")

    print(f"OK S328: {checks} comprobaciones")


if __name__ == "__main__":
    main()
