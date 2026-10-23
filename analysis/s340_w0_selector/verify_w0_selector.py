#!/usr/bin/env python3
"""S340 - verificacion independiente de `w0_selector.json`.

Uso: ``.venv/bin/python analysis/s340_w0_selector/verify_w0_selector.py``
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
DATA = HERE / "w0_selector.json"
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = True

OK = 0
FAIL: list[str] = []


def check(cond: bool, msg: str) -> None:
    global OK
    if cond:
        OK += 1
    else:
        FAIL.append(msg)


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def insn(blob: bytes, addr: int) -> str:
    i = next(iter(MD.disasm(blob[addr - BASE:addr - BASE + 4], addr)))
    return f"{i.mnemonic} {i.op_str}".strip()


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    blob = A7S.read_bytes()
    check(hashlib.sha256(blob).hexdigest() == data["firmware"]["a7s_fw320"]["sha256"],
          "sha256 A7S")

    # switch y tbb
    check(insn(blob, 0x436F74C2) == "cmp r1, #5", "switch: rango 0..5")
    check(insn(blob, 0x436F74C6) == "tbb [pc, r1]", "switch: tbb")
    table = list(blob[0x436F74CA - BASE:0x436F74CA - BASE + 6])
    check(table == data["switch"]["tbb_bytes"], "tabla tbb")
    check(table == [3, 6, 9, 12, 15, 18], "offsets 0,3,6,9,12,15")

    # cada caso: literal = base MMIO y lectura [base+0x30]
    for case in data["cases"]:
        addr = int(case["function"], 16)
        check(insn(blob, addr) == "ldr r3, [pc, #4]", f"{case['function']}: ldr")
        check(insn(blob, addr + 2) == f"ldr r0, [r3, #{case['offset']}]",
              f"{case['function']}: offset {case['offset']}")
        check(case["literal"] in data["verdicts"]["selector_bases"],
              f"{case['function']}: base en la lista")

    # suma
    check(insn(blob, 0x436F6092) == "adds r0, r0, r6", "suma: adds")
    check(insn(blob, 0x436F6094) == "uxth r0, r0", "suma: u16")

    # selectores por modo
    codes = [u32(blob, 0x43FEE370 + 4 * i) for i in range(34)]
    pos = {c: i for i, c in enumerate(codes)}
    bases = {"T1": 0x43BBEB70, "T2": 0x43BBF2E8, "T3": 0x43BBEF30}
    for code, meta in data["per_code"].items():
        c = int(code, 16)
        check(meta["position"] == pos[c], f"{code}: posicion")
        for name, base in bases.items():
            check(meta["selectors"][name] == u32(blob, base + 0x1C * pos[c]),
                  f"{code} {name}: w0")

    v = data["verdicts"]
    check(v["w0_is_mmio_selector"], "w0 = selector")
    check(v["selector_offsets"] == {"0x30": 4, "0x24": 2}, "offsets por canal")
    check(v["t1_channels"] == [0, 1] and v["t2_channels"] == [2, 3],
          "canales T1/T2")
    check(v["measured_quantity"] == "NO_VERIFICADO", "magnitud no verificada")

    print(f"{OK} comprobaciones OK, {len(FAIL)} fallos")
    for msg in FAIL:
        print("  FALLO:", msg)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
