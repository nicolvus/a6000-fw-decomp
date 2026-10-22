#!/usr/bin/env python3
"""S320 - verificador independiente de frames.json."""
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
DATA = Path(__file__).with_name("frames.json")

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


def main() -> None:
    d = json.loads(DATA.read_text())
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()

    ok(d["firmware"]["a7s"]["sha256"] == sha256(A7S), "sha256 A7S")
    ok(d["firmware"]["a6000"]["sha256"] == sha256(A6000), "sha256 A6000")

    # prefijo comun
    ok(u16(a7, 0x436F25F0) == 0xB573, "retry: push {r0,r1,r4,r5,r6,lr}")
    ok(u16(a7, 0x43AD968A) == 0xB573, "plain: push {r0,r1,r4,r5,r6,lr}")
    common = 0
    for i in range(7):
        if a7[0x436F25F0 - BASE + 2 * i:0x436F25F0 - BASE + 2 * i + 2] == \
                a7[0x43AD968A - BASE + 2 * i:0x43AD968A - BASE + 2 * i + 2]:
            common += 1
    ok(common == 7, f"7 instrucciones comunes (vistas {common})")
    ok(d["common_insn"] == 7, "common_insn en JSON")

    # bloque extra
    ok(u16(a7, 0x436F260C) == 0x2802, "cmp r0,#2")
    ok(u16(a7, 0x436F260E) == 0xD10D, "bne (fin si no esta ocupado)")
    ok(u16(a7, 0x436F2612) == 0xF3E6, "bl 0x43ad92e6")
    ok(u16(a7, 0x436F2618) == 0x4629, "mov r1,r5 (retry)")
    ok(u16(a7, 0x436F261C) == 0xF3E7, "bl 0x43ad9666 (retry)")
    ok(u16(a7, 0x436F2620) == 0x2802, "cmp r0,#2 (retry)")

    # plain: llama al formateador una vez
    ok(u16(a7, 0x43AD96A2) == 0xF7FF, "plain: bl 0x43ad9666")
    ok(u16(a7, 0x43AD96A6) == 0xBD7C, "plain: pop")

    # presencia A6000
    for name in ("retry", "plain", "formatter", "busy"):
        ok(d["presence"][name]["a6000_hits"] == 0, f"{name} exclusivo A7S")
    ok(all(a6.count(bytes.fromhex(d["presence"][n]["signature"])) == 0
           for n in ("retry", "plain", "formatter", "busy")), "0 firmas en A6000")

    text = " ".join(d["limits"])
    ok("NO_VERIFICADO" in text and "S51" in text, "limites")

    print(f"OK S320: {checks} comprobaciones")


if __name__ == "__main__":
    main()
