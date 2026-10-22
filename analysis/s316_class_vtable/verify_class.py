#!/usr/bin/env python3
"""S316 - verificador independiente de class.json."""
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
DATA = Path(__file__).with_name("class.json")

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

    # constructor
    ok(u16(a7, 0x436F27B4) == 0x4B0A, "ctor: ldr r3,[pc,#0x28]")
    ok(u16(a7, 0x436F27B6) == 0x4A0B, "ctor: ldr r2,[pc,#0x2c]")
    ok(u16(a7, 0x436F27B8) == 0x447B, "ctor: add r3,pc")
    ok(u16(a7, 0x436F27C0) == 0x3308, "ctor: adds r3,#8")
    ok(u16(a7, 0x436F27C2) == 0x6003, "ctor: str r3,[r0]")
    lit = u32(a7, 0x436F27E0)
    base = (lit + 0x436F27BC) & 0xFFFFFFFF
    ok(base == 0x44024540, f"base GOT {base:#x}")
    ok(u32(a7, 0x436F27E4) == 0x6740, "offset GOT 0x6740")
    ok(base + 0x6740 == 0x4402AC80, "slot GOT 0x4402ac80")
    ok(u32(a7, 0x4402AC80) == 0x43FCE048, "slot -> metadata vtable")
    ok(u32(a7, 0x4402AC80) + 8 == 0x43FCE050, "vptr almacenado 0x43fce050")

    # vtable
    ok(u32(a7, 0x43FCE048) == 0, "offset-to-top 0")
    ok(u32(a7, 0x43FCE04C) == 0x43FEEB20, "typeinfo 0x43feeb20")
    entries = []
    a = 0x43FCE050
    while u32(a7, a) != 0:
        entries.append((a, u32(a7, a)))
        a += 4
    ok(len(entries) == 45, f"45 entradas (vistas {len(entries)})")
    ok(a == 0x43FCE104, "terminador en 0x43fce104")
    ok({addr: val for addr, val in entries}[0x43FCE088] & ~1 == 0x436F5A14,
       "slot +0x38 -> 0x436f5a14")
    ok({addr: val for addr, val in entries}[0x43FCE094] & ~1 == 0x436F53F4,
       "slot +0x44 -> 0x436f53f4")
    ok({addr: val for addr, val in entries}[0x43FCE054] & ~1 == 0x43AD9840,
       "slot +0x04 -> wrapper 0x43ad9840")
    for entry in d["vtable"]["entries"]:
        ok(entry["target"].startswith("0x"), "entrada con destino")

    # wrapper
    ok(u16(a7, 0x43AD9840) == 0xB510, "wrapper: push {r4,lr}")
    ok(u16(a7, 0x43AD9844) == 0xF418 and u16(a7, 0x43AD9846) == 0xFFB6,
       "wrapper: bl 0x436f27b4")
    ok(u16(a7, 0x43AD984A) == 0xF6C8, "wrapper: bl 0x439a2780")

    # slots declarados
    for fn, slot in [("0x436f5a14", "0x38"), ("0x436f53f4", "0x44"),
                     ("0x43ad9840", "0x04")]:
        ok(d["method_slots"][fn]["expected_slot"] == slot, f"slot {fn}")
        ok(d["method_slots"][fn]["matches"] is True, f"match {fn}")

    # A6000
    for name, addr, n in [("ctor", 0x436F27B4, 32), ("wrapper", 0x43AD9840, 16),
                          ("method_5a14", 0x436F5A14, 32),
                          ("method_53f4", 0x436F53F4, 24)]:
        sig = a7[addr - BASE:addr - BASE + n]
        ok(a6.count(sig) == 0, f"{name} exclusivo A7S")
        key = {"ctor": "ctor", "wrapper": "wrapper", "method_5a14": "method_5a14",
               "method_53f4": "method_53f4"}[name]
        ok(d["a6000_presence"][key]["a6000_hits"] == 0, f"{name} 0 hits en JSON")

    print(f"OK S316: {checks} comprobaciones")


if __name__ == "__main__":
    main()
