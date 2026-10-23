#!/usr/bin/env python3
"""S346 - verificacion independiente: sin productor estatico del array .bss."""
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
JSON = Path(__file__).with_name("array_producer.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
ok = 0
fails: list[str] = []


def check(name: str, cond: bool) -> None:
    global ok
    if cond:
        ok += 1
    else:
        fails.append(name)


def u16(b: bytes, a: int) -> int:
    return struct.unpack_from("<H", b, a - BASE)[0]


def u32(b: bytes, a: int) -> int:
    return struct.unpack_from("<I", b, a - BASE)[0]


def texts(b: bytes, start: int, size: int) -> list[str]:
    return [f"{i.mnemonic} {i.op_str}".strip()
            for i in MD.disasm(b[start - BASE:start - BASE + size], start)]


def refs(b: bytes, value: int) -> list[str]:
    out, pat = [], struct.pack("<I", value)
    i = b.find(pat)
    while i >= 0:
        lit = BASE + i
        for back in range(2, 0x400, 2):
            a = lit - back
            if a < BASE:
                break
            h = u16(b, a)
            if (h & 0xF800) == 0x4800 and ((a + 4) & ~3) + (h & 0xFF) * 4 == lit:
                out.append(f"0x{a:08x}")
                break
        i = b.find(pat, i + 1)
    return out


def main() -> int:
    d = json.loads(JSON.read_text())
    a7, a6 = BLOBS["a7s"].read_bytes(), BLOBS["a6000"].read_bytes()
    for k, key in (("a7s", "a7s_fw320"), ("a6000", "a6000_fw321")):
        b = a7 if k == "a7s" else a6
        check(f"sha256 {k}", hashlib.sha256(b).hexdigest() == d["firmware"][key]["sha256"])

    check("array .bss a cero", all(a7[0x43E906F4 - BASE + i] == 0 for i in range(0x114)))
    check("un solo literal del array", a7.count(struct.pack("<I", 0x43E906F4)) == 1)
    check("slot contiene el array", u32(a7, 0x44026240) == 0x43E906F4)
    check("offset del slot", 0x44026240 - 0x44024540 == 0x1D00)
    check("dos referencias", refs(a7, 0x1D00) == ["0x43705716", "0x4370575e"])
    check("sin bases PIC", d["a7s"]["pic_bases_to_array"] == [])
    check("thunk 0x4355f790 usa +0x2c8",
          any("0x2c8" in t for t in texts(a7, 0x4355F790, 0x10)))
    check("thunk 0x4355f7ac usa +0x2cc",
          any("0x2cc" in t for t in texts(a7, 0x4355F7AC, 0x10)))
    check("A6000 mismo patron", u32(a6, 0x44020730) == 0x43E8197C
          and refs(a6, 0x184C) == ["0x436eb2f6", "0x436eb33e"])
    check("veredicto sin escritor", d["verdicts"]["static_writer"] is False)
    check("productor NO_VERIFICADO", d["verdicts"]["producer_identity"] == "NO_VERIFICADO")
    check("limites citan S51", any("S51" in x for x in d["limits"]))

    total = ok + len(fails)
    print(f"{total} comprobaciones, {len(fails)} fallos")
    for f in fails:
        print("  FALLO:", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
