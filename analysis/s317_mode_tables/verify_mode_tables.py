#!/usr/bin/env python3
"""S317 - verificador independiente de mode_tables.json."""
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
DATA = Path(__file__).with_name("mode_tables.json")

checks = 0


def ok(cond: bool, msg: str) -> None:
    global checks
    if not cond:
        raise SystemExit(f"FALLO: {msg}")
    checks += 1


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(b: bytes, a: int) -> int:
    return struct.unpack_from("<H", b, a - BASE)[0]


def u32(b: bytes, a: int) -> int:
    return struct.unpack_from("<I", b, a - BASE)[0]


def main() -> None:
    d = json.loads(DATA.read_text())
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()

    ok(d["firmware"]["a7s"]["sha256"] == sha256(A7S), "sha256 A7S")
    ok(d["firmware"]["a6000"]["sha256"] == sha256(A6000), "sha256 A6000")

    # entrada y stride
    ok(u16(a7, 0x436F618C) == 0x29FF, "0x436f618c: cmp r1,#0xff")
    ok(u16(a7, 0x436F61A4) == 0x221C, "0x436f61a4: movs r2,#0x1c")
    ok(u16(a7, 0x436F61A6) == 0x4355, "0x436f61a6: muls r5,r2,r5")
    ok(d["entry"]["stride"] == "0x1c", "stride en JSON")

    # tres bases recomputadas desde literales
    for ldr, imm, add, expected in [
            (0x436F61A2, 0x48, 0x436F61AA, 0x43BBEB6E),
            (0x436F61BA, 0x34, 0x436F61C2, 0x43BBF2EA),
            (0x436F61CE, 0x24, 0x436F61D6, 0x43BBEF32)]:
        la = ((ldr + 4) & ~3) + imm
        base = (u32(a7, la) + ((add + 4) & ~3)) & 0xFFFFFFFF
        ok(base == expected, f"base {expected:#x} (vista {base:#x})")
    ok(d["tables"]["T1"]["computed"] == 0x43BBEB6E, "T1")
    ok(d["tables"]["T2"]["computed"] == 0x43BBF2EA, "T2")
    ok(d["tables"]["T3"]["computed"] == 0x43BBEF32, "T3")

    # espaciado
    ok(0x43BBF2EA - 0x43BBEF32 == 34 * 0x1C, "T3->T2 = 34 filas")
    ok(d["spacing"]["T3_to_T2_rows"] == 34, "34 filas en JSON")
    ok(0x43BBEF32 - 0x43BBEB6E == 0x3C4, "T1->T3 = 0x3c4")
    ok(d["spacing"]["T1_to_T3"] == "0x3c4", "0x3c4 en JSON")

    # campos leidos por la entrada
    ok(u16(a7, 0x436F61AE) == 0x8B19, "ldrh r1,[r3,#0x18]")
    ok(u16(a7, 0x436F61B0) == 0x695A, "ldr r2,[r3,#0x14]")

    # filas documentadas coinciden con el blob
    for name in ("T1", "T2", "T3"):
        table = d["tables"][name]
        for row in table["rows_computed_base"]:
            a = int(row["addr"], 16)
            ok(row["u32_14"] == f"0x{u32(a7, a + 0x14):08x}", f"{name} +0x14")
            ok(row["u16_18"] == f"0x{u16(a7, a + 0x18):04x}", f"{name} +0x18")

    # A6000
    ok(d["a6000_entry_hits"] == 0, "entrada exclusiva A7S")
    ok(a6.count(a7[0x436F618C - BASE:0x436F618C - BASE + 24]) == 0, "0 hits A6000")

    # limites
    text = " ".join(d["limits"])
    ok("NO_VERIFICADA" in text and "NO_VERIFICADAS" in text, "limites explicitos")

    print(f"OK S317: {checks} comprobaciones")


if __name__ == "__main__":
    main()
