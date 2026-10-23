#!/usr/bin/env python3
"""S344 - verificacion independiente de las dos tablas de 0x436f6240."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
FW = ROOT / "firmware/extracted"
BLOBS = {
    "a7s": FW / ("a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/"
                 "nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6000": FW / ("fw321/firmware.tar_unpacked/0700_part_image/dev/"
                   "nflasha3_unpacked_unpacked/av-cam.bin"),
}
JSON = Path(__file__).with_name("selector_tables.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

ok = 0
fails: list[str] = []


def check(name: str, cond: bool) -> None:
    global ok
    if cond:
        ok += 1
    else:
        fails.append(name)


def u8(b: bytes, a: int) -> int:
    return b[a - BASE]


def u16(b: bytes, a: int) -> int:
    return struct.unpack_from("<H", b, a - BASE)[0]


def u32(b: bytes, a: int) -> int:
    return struct.unpack_from("<I", b, a - BASE)[0]


def texts(b: bytes, start: int, size: int) -> list[str]:
    return [f"{i.mnemonic} {i.op_str}".strip()
            for i in MD.disasm(b[start - BASE:start - BASE + size], start)]


def pic(b: bytes, ldr: int, add: int) -> int:
    h = u16(b, ldr)
    lit = ((ldr + 4) & ~3) + (h & 0xFF) * 4
    return (u32(b, lit) + ((add + 4) & ~1)) & 0xFFFFFFFF


def mapping(r4: int, r5: int, r6: int) -> int:
    if r5 == 0:
        return 6 if r6 > 1 else [6, 5][r6]
    if r5 == 1:
        return 0 if r4 > 2 else [0, 1, 4][r4]
    return 0


def count_bl(b: bytes, target: int) -> int:
    n = 0
    for off in range(0, len(b) - 4, 2):
        h = struct.unpack_from("<H", b, off)[0]
        if (h & 0xF800) != 0xF000:
            continue
        h2 = struct.unpack_from("<H", b, off + 2)[0]
        if (h2 & 0xD000) != 0xD000:
            continue
        s = (h >> 10) & 1
        j1, j2 = (h2 >> 13) & 1, (h2 >> 11) & 1
        v = ((s << 24) | ((1 - (j1 ^ s)) << 23) | ((1 - (j2 ^ s)) << 22)
             | ((h & 0x3FF) << 12) | ((h2 & 0x7FF) << 1))
        if s:
            v -= 1 << 25
        if (BASE + off + 4 + v) & 0xFFFFFFFF == target:
            n += 1
    return n


def main() -> int:
    d = json.loads(JSON.read_text())
    a7, a6 = BLOBS["a7s"].read_bytes(), BLOBS["a6000"].read_bytes()
    for k, key in (("a7s", "a7s_fw320"), ("a6000", "a6000_fw321")):
        b = a7 if k == "a7s" else a6
        check(f"sha256 {k}", hashlib.sha256(b).hexdigest() == d["firmware"][key]["sha256"])

    check("tabla A", [u32(a7, 0x43BBEB64 + 4 * i) for i in range(3)] == [0, 1, 4])
    check("tabla B", [u32(a7, 0x43BBEF28 + 4 * i) for i in range(3)] == [6, 5, 4])
    check("A termina en T1", 0x43BBEB64 + 12 == 0x43BBEB70)
    check("B empieza en fin T1", d["tables"]["table_b"]["starts_at_t1_end"])
    check("T1 34x0x1c", 0x43BBEB70 + 34 * 0x1C == 0x43BBEF28)

    core = texts(a7, 0x436F6240, 0x34)
    check("core lee row[5]", "ldrb r3, [r0, #5]" == core[0])
    check("core dos tablas", pic(a7, 0x436F6250, 0x436F6252) == 0x43BBEF28
          and pic(a7, 0x436F625C, 0x436F625E) == 0x43BBEB64)
    check("core indice row[6]", any(t.startswith("ldrb r2, [r0, #6]") for t in core))
    check("core indice row[4]", any(t.startswith("ldrb r2, [r0, #4]") for t in core))
    check("core tope 2/1", "cmp r2, #2" in core and "cmp r2, #1" in core)

    wrap = texts(a7, 0x436F6278, 0x28)
    check("wrapper limite 0x21", "cmp r0, #0x21" in wrap)
    check("wrapper stride 0x1c", "movs r0, #0x1c" in wrap)
    check("wrapper base T1", pic(a7, 0x436F628E, 0x436F6292) == 0x43BBEB70)
    check("wrapper tail-call core", any(t == "b.w #0x436f6240" for t in wrap))

    per7 = d["per_mode_a7s"]
    modes7 = [u32(a7, 0x43FEE370 + 4 * i) for i in range(34)]
    check("34 modos A7S", [p["mode"] for p in per7] == modes7)
    recomputed = []
    for pos in range(34):
        row = 0x43BBEB70 + 0x1C * pos
        recomputed.append(mapping(u8(a7, row + 4), u8(a7, row + 5), u8(a7, row + 6)))
    check("mapping A7S", recomputed == [p["value"] for p in per7])
    check("A7S 32x1 y 2x4", recomputed.count(1) == 32 and recomputed.count(4) == 2)
    check("modos 4 = 0x37,0x38", [f"0x{modes7[i]:02x}" for i, v in enumerate(recomputed)
                                  if v == 4] == ["0x37", "0x38"])

    per6 = d["per_mode_a6000"]
    for pos in (0, 6, 12):
        row = 0x43BC20DC + 0x1C * pos
        check(f"A6000 fila {pos}", (u8(a6, row + 4), u8(a6, row + 5), u8(a6, row + 6)) == (1, 1, 0))
    check("A6000 13x1", [p["value"] for p in per6] == [1] * 13)

    check("sin BL core", count_bl(a7, 0x436F6240) == 0)
    check("sin BL wrapper", count_bl(a7, 0x436F6278) == 0)
    check("sin literal core", a7.find(struct.pack("<I", 0x436F6241)) < 0)
    check("sin literal wrapper", a7.find(struct.pack("<I", 0x436F6279)) < 0)
    check("A6000 sin patron", a7.find(bytes.fromhex("437913b1012b")) >= 0
          and a6.find(bytes.fromhex("437913b1012b")) < 0)

    total = ok + len(fails)
    print(f"{total} comprobaciones, {len(fails)} fallos")
    for f in fails:
        print("  FALLO:", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
