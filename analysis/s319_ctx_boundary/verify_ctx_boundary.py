#!/usr/bin/env python3
"""S319 - verificador independiente de ctx_boundary.json."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
FW = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha15_unpacked_unpacked")
DATA = Path(__file__).with_name("ctx_boundary.json")

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


def count_sites(blob: bytes, target: int) -> int:
    n = 0
    for off in range(2, len(blob) - 4, 2):
        a = BASE + off
        h1 = struct.unpack_from("<H", blob, off - 2)[0]
        h2 = struct.unpack_from("<H", blob, off)[0]
        if (h2 & 0xFFF8) != 0x4478:
            continue
        rd = h2 & 7
        if (h1 & 0xF800) != 0x4800 or ((h1 >> 8) & 7) != rd:
            continue
        lit = ((a + 4) & ~3) + (h1 & 0xFF) * 4
        if not (0 <= lit - BASE < len(blob) - 3):
            continue
        if (struct.unpack_from("<I", blob, lit - BASE)[0] + ((a + 4) & ~1)) & 0xFFFFFFFF == target:
            n += 1
    for off in range(0, len(blob) - 8, 2):
        a = BASE + off
        h1, h2 = struct.unpack_from("<HH", blob, off)
        if h1 != 0xF8DF:
            continue
        rt = (h2 >> 12) & 0xF
        if rt >= 13:
            continue
        lit = ((a + 4) & ~3) + (h2 & 0xFFF)
        if not (0 <= lit - BASE < len(blob) - 3):
            continue
        h3 = struct.unpack_from("<H", blob, off + 4)[0]
        if ((h3 & 0xFFF8) == 0x4478 and (h3 & 7) == rt
                and (struct.unpack_from("<I", blob, lit - BASE)[0]
                     + ((a + 8) & ~1)) & 0xFFFFFFFF == target):
            n += 1
    return n


def main() -> None:
    d = json.loads(DATA.read_text())
    a7 = A7S.read_bytes()

    ok(d["firmware"]["a7s"]["sha256"] == sha256(A7S), "sha256 A7S")
    ok(d["ctx"]["address"] == "0x43ea70a0", "ctx en JSON")
    ok(count_sites(a7, 0x43EA70A0) == 40, "40 sitios a ctx")
    ok(count_sites(a7, 0x43EA70A8) == 0, "0 sitios directos a ctx+8")
    ok(d["ctx"]["stores_at_offset_0_or_8"] == [], "sin store a offset 0/8")
    ok(d["ctx"]["classification"]["load"] == 31, "31 lecturas")
    ok(d["ctx"]["classification"]["store"] == 1, "1 store a +0x44")
    ok(d["ctx"]["classification_detail"][
        [x["add"] for x in d["ctx"]["classification_detail"]].index("0x437b5d4a")]["offset"] == 68,
       "store en +0x44")

    ok(d["absolute_words_av_cam"] == {"ctx": 0, "ctx8": 0}, "0 palabras absolutas en av-cam")
    ok(a7.count(struct.pack("<I", 0x43EA70A0)) == 0, "av-cam sin literal ctx")
    ok(a7.count(struct.pack("<I", 0x43EA70A8)) == 0, "av-cam sin literal ctx+8")

    mods = [p for dname in ("kmod", "lib") for p in (FW / dname).glob("*") if p.is_file()]
    ok(len(mods) > 0, "hay modulos")
    ok(all(struct.pack("<I", 0x43EA70A0) not in p.read_bytes()
           and struct.pack("<I", 0x43EA70A8) not in p.read_bytes() for p in mods),
       "0 literales ctx en modulos")
    ok(all(not m["hits"] for m in d["sibling_modules"]), "0 hits en JSON")

    ok(d["verdict"] == "NO_VERIFICADO", "veredicto")
    text = " ".join(d["limits"])
    ok("memoria compartida" in text and "S51" in text, "limites")

    print(f"OK S319: {checks} comprobaciones")


if __name__ == "__main__":
    main()
