#!/usr/bin/env python3
"""S345 - verificacion independiente: alcanzabilidad de la mascara."""
from __future__ import annotations

import hashlib
import json
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
JSON = Path(__file__).with_name("mask_reachability.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
COND = {"beq", "bne", "bcs", "bhs", "bcc", "blo", "bmi", "bpl", "bvs", "bvc",
        "bhi", "bls", "bge", "blt", "bgt", "ble", "cbz", "cbnz"}

ok = 0
fails: list[str] = []


def check(name: str, cond: bool) -> None:
    global ok
    if cond:
        ok += 1
    else:
        fails.append(name)


def texts(b: bytes, start: int, end: int) -> list[str]:
    return [f"{i.mnemonic} {i.op_str}".strip()
            for i in MD.disasm(b[start - BASE:end - BASE], start)]


def main() -> int:
    d = json.loads(JSON.read_text())
    a7, a6 = BLOBS["a7s"].read_bytes(), BLOBS["a6000"].read_bytes()
    for k, key in (("a7s", "a7s_fw320"), ("a6000", "a6000_fw321")):
        b = a7 if k == "a7s" else a6
        check(f"sha256 {k}", hashlib.sha256(b).hexdigest() == d["firmware"][key]["sha256"])

    t7 = texts(a7, 0x436F4476, 0x436F449C)
    check("A7S sin ramas condicionales", not [x for x in t7 if x.split()[0] in COND])
    calls7 = [x for x in t7 if x.startswith("bl ")]
    check("A7S tres llamadas en orden", calls7 == ["bl #0x436f618c", "bl #0x436f61f8",
                                                  "bl #0x436f60ac"])
    check("A7S op0 llamada desde 0x436f61f8",
          "bl #0x43ada370" in texts(a7, 0x436F6216, 0x436F621A))
    check("A7S op1 tail desde 0x436f60ac",
          "b.w #0x43ada402" in texts(a7, 0x436F6234, 0x436F6238))
    check("A7S 0x43ada370 tail a 0x436f822c",
          "b.w #0x436f822c" in texts(a7, 0x43ADA3A0, 0x43ADA3A4))
    check("A7S 0x43ada402 tail a 0x436f822c",
          "b.w #0x436f822c" in texts(a7, 0x43ADA42C, 0x43ADA430))

    t7b = texts(a7, 0x436F5AE8, 0x436F5B10)
    check("A7S segundo sitio con puerta", any(x.startswith("cbz r0") for x in t7b)
          and "bl #0x436f61f8" in t7b)
    check("A7S puerta es 0x43ad9b50", "bl #0x43ad9b50" in t7b)

    t6 = texts(a6, 0x436D8F46, 0x436D8F6E)
    check("A6000 sin ramas condicionales", not [x for x in t6 if x.split()[0] in COND])
    calls6 = [x for x in t6 if x.startswith("bl ")]
    check("A6000 dos llamadas", calls6 == ["bl #0x43ad94d8", "bl #0x436d8bd8"])
    check("A6000 op1 tail 0x43ad9512", "b.w #0x43ad9512" in t6)

    pat_a = a7[0x43ADA370 - BASE:0x43ADA370 - BASE + 16]
    pat_b = a7[0x43ADA402 - BASE:0x43ADA402 - BASE + 16]
    check("A6000 reusa el cuerpo op0", a6.find(pat_a) >= 0)
    check("A6000 reusa el cuerpo op1", a6.find(pat_b) >= 0)

    v = d["verdicts"]
    check("no condicionada por modo", v["mask_application_mode_gated_in_span"] is False)
    check("sin camino silent exclusivo", v["a7s_extra_silent_only_path"] is False)
    check("S51 sin cambios", v["s51"].startswith("sin cambios"))

    total = ok + len(fails)
    print(f"{total} comprobaciones, {len(fails)} fallos")
    for f in fails:
        print("  FALLO:", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
