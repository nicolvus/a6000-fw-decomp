#!/usr/bin/env python3
"""S318 - verificador independiente de ctor_mode.json."""
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
DATA = Path(__file__).with_name("ctor_mode.json")

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
    ok(u16(a7, 0x436F3FC0) == 0xB5F0, "push {r4,r5,r6,r7,lr}")
    ok(u16(a7, 0x436F3FDA) == 0x58EB, "ldr r3,[r5,r3] (slot GOT)")
    ok(u16(a7, 0x436F3FDE) == 0x6023, "str r3,[r4] (vptr)")
    ok(u16(a7, 0x436F3FE4) == 0xF853 and u16(a7, 0x436F3FE6) == 0x3026,
       "ldr.w r3,[r3,r6,lsl#2]")
    ok(u16(a7, 0x436F3FEC) == 0xF3E5, "bl 0x43ad9162")
    ok(u32(a7, 0x4402AC80) == 0x43FCE048, "slot GOT 0x4402ac80")
    ok(u32(a7, 0x4402AC80) + 8 == 0x43FCE050, "vptr 0x43fce050")

    # base de la tabla
    lit = u32(a7, 0x436F4134)
    base = (lit + ((0x436F3FE2 + 4) & ~1)) & 0xFFFFFFFF
    ok(base == 0x43BBE1CC, f"tabla {base:#x}")
    ok(u32(a7, 0x43BBE1CC) == 1 and u32(a7, 0x43BBE1D0) == 2,
       "tabla[0]=1, tabla[1]=2")
    ok(u32(a7, 0x43BBE1E8) == 0x01EC0000, "tabla[7] empaqueta dos u16")

    # mapper
    ok(u16(a7, 0x43AD916A) == 0x2C01, "cmp r4,#1")
    ok(u16(a7, 0x43AD917C) == 0x2310, "movs r3,#0x10")
    ok(u16(a7, 0x43AD9180) == 0x2340, "movs r3,#0x40")
    ok(u16(a7, 0x43AD9184) == 0x2301, "movs r3,#1")
    ok(u16(a7, 0x43AD9188) == 0x6083, "str r3,[r0,#8]")
    ok(u16(a7, 0x43AD918C) == 0x60C3, "str r3,[r0,#0xc]")

    # llamador unico y su indice 0
    ok(d["constructor"]["callers"] == ["0x436f2a8a"], "llamador unico")
    ok(u16(a7, 0x436F2A8A) == 0xF001, "bl 0x436f3fc0 en 0x436f2a8a")
    ok(u16(a7, 0x436F2A7E) == 0x2100, "movs r1,#0 (idx=0)")

    # A6000
    ok(d["a6000_ctor_hits"] == 0, "0 hits en JSON")
    ok(a6.count(a7[0x436F3FC0 - BASE:0x436F3FC0 - BASE + 32]) == 0,
       "constructor exclusivo A7S")

    text = " ".join(d["limits"])
    ok("NO_VERIFICADOS" in text and "S51" in text, "limites")

    print(f"OK S318: {checks} comprobaciones")


if __name__ == "__main__":
    main()
