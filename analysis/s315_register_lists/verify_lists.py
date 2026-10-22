#!/usr/bin/env python3
"""S315 - verificador independiente de lists.json, re-decodificado desde los blobs."""
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
DATA = Path(__file__).with_name("lists.json")

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


def bl_calls(b: bytes):
    for off in range(0, len(b) - 3, 2):
        h1, h2 = struct.unpack_from("<HH", b, off)
        if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000:
            continue
        s = (h1 >> 10) & 1
        imm10 = h1 & 0x3FF
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        imm11 = h2 & 0x7FF
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        delta = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
        if s:
            delta -= 1 << 25
        yield BASE + off, (BASE + off + 4 + delta) & 0xFFFFFFFF


def read_list(b: bytes, table: int):
    ptrs = []
    a = table
    while u32(b, a) != 0:
        ptrs.append(u32(b, a))
        a += 4
    return ptrs, a


def main() -> None:
    d = json.loads(DATA.read_text())
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()

    ok(d["firmware"]["a7s"]["sha256"] == sha256(A7S), "sha256 A7S")
    ok(d["firmware"]["a6000"]["sha256"] == sha256(A6000), "sha256 A6000")

    # consumidor y sus tres llamadas
    callers = [a for a, t in bl_calls(a7) if t == 0x436F44C4]
    ok(callers == [0x436F5422, 0x436F5B32, 0x436F5B52], f"callers {callers}")
    ok([c["call"] for c in d["consumer"]["call_sites"]]
       == ["0x436f5422", "0x436f5b32", "0x436f5b52"], "callers en JSON")
    ok(u16(a7, 0x436F541E) == 0x2102, "movs r1,#2 en 0x436f541e")
    ok(u16(a7, 0x436F5B2C) == 0x2102, "movs r1,#2 en 0x436f5b2c")
    ok(u16(a7, 0x436F5B4E) == 0x2100, "movs r1,#0 en 0x436f5b4e")
    ok(d["modes"] == {"0x436f5422": 2, "0x436f5b32": 2, "0x436f5b52": 0},
       "modos en JSON")

    # getter de L95 y slots GOT
    ok(u32(a7, 0x436F4594) == 0x0092FFB0 and u32(a7, 0x436F4598) == 0x00008400,
       "literales del getter")
    base = (u32(a7, 0x436F4594) + 0x436F4590) & 0xFFFFFFFF
    ok(base == 0x44024540, f"base GOT del getter {base:#x}")
    ok(u32(a7, 0x4402C940) == 0x43FEE3F8, "slot 0x4402c940 -> L95")
    ok(u32(a7, 0x44025EC0) == 0x43FEE578, "slot 0x44025ec0 -> L5")
    ok(u32(a7, 0x440292B0) == 0x43FEE590, "slot 0x440292b0 -> L1")

    # listas
    for name, table, count, term in [
            ("L95", 0x43FEE3F8, 95, 0x43FEE574),
            ("L5", 0x43FEE578, 5, 0x43FEE58C),
            ("L1", 0x43FEE590, 1, 0x43FEE594)]:
        ptrs, addr = read_list(a7, table)
        ok(len(ptrs) == count, f"{name} n={len(ptrs)}")
        ok(addr == term, f"{name} terminador")
        ok(d["lists"][name]["count"] == count, f"{name} n en JSON")
        ok(d["lists"][name]["terminator"] == f"0x{term:08x}", f"{name} term en JSON")
        for p in ptrs:
            rec = a7[p - BASE:p - BASE + 6]
            ok(rec[1] == 0 and rec[5] == 0, f"{name} padding en {p:#x}")
    ok([r["reg"] for r in d["lists"]["L5"]["records"]]
       == [0x5F, 0x61, 0x88, 0x94, 0xE3], "registros de L5")
    ok(d["lists"]["L1"]["records"][0]["reg"] == 0
       and d["lists"]["L1"]["records"][0]["data"] == 4, "registro unico de L1")
    ok(sum(1 for r in d["lists"]["L95"]["records"] if r["dev"] == 0x81) == 94,
       "94 dev 0x81 en L95")
    ok(sum(1 for r in d["lists"]["L95"]["records"] if r["dev"] == 0x83) == 1,
       "1 dev 0x83 en L95")

    # bucle del consumidor
    ok(u16(a7, 0x436F4526) == 0x7819, "ldrb r1,[r3]")
    ok(u16(a7, 0x436F452A) == 0x885A, "ldrh r2,[r3,#2]")
    ok(u16(a7, 0x436F452C) == 0x791B, "ldrb r3,[r3,#4]")
    ok(u16(a7, 0x436F4532) == 0xF856, "ldr r3,[r6],#4")
    ok(u16(a7, 0x436F4538) == 0xD1F5, "bne al cuerpo del bucle")

    # contraste A6000
    for name, addr, n in [("consumer", 0x436F44C4, 24), ("getter", 0x436F4588, 16)]:
        sig = a7[addr - BASE:addr - BASE + n]
        ok(a6.count(sig) == 0, f"{name} exclusivo A7S")
        ok(d["a6000_presence"][name if name != "getter" else "getter_L95"]["a6000_hits"] == 0,
           f"{name} 0 hits en JSON")

    print(f"OK S315: {checks} comprobaciones")


if __name__ == "__main__":
    main()
