#!/usr/bin/env python3
"""S339 - verificacion independiente de `block_f292b.json`."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

BASE = 0x43541000
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
DATA = HERE / "block_f292b.json"

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


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()
    check(hashlib.sha256(a7).hexdigest() == data["firmware"]["a7s_fw320"]["sha256"],
          "sha256 A7S")
    check(hashlib.sha256(a6).hexdigest() == data["firmware"]["a6000_fw321"]["sha256"],
          "sha256 A6000")

    for reg, info in data["literal_sites"].items():
        for s in info["a7s"]:
            check(u32(a7, int(s, 16)) == int(reg, 16), f"A7S {s}")
        for s in info["a6000"]:
            check(u32(a6, int(s, 16)) == int(reg, 16), f"A6000 {s}")
        check(len(info["a7s"]) == len(info["a6000"]), f"{reg}: mismos sitios")

    # todos los sitios A7S caen en el rango de los accesores
    for info in data["literal_sites"].values():
        for s in info["a7s"]:
            check(0x436F8290 <= int(s, 16) < 0x436F82F0, f"{s} en accesores")
    check(data["all_sites_in_accessors"] is True, "solo accesores")

    # ventana 0xf292x000
    win = data["window_0xf292x000"]["a7s"]
    check("0xf292b000" in win and win["0xf292b000"] == 6, "ventana: 6 sitios")
    check("0xf292d000" in win, "ventana: DSP de lente presente")

    v = data["verdicts"]
    check(v["identity"] == "NO_VERIFICADO", "identidad no verificada")
    check(v["documented_in_repo"] is False, "no documentado")
    check(v["same_sites_in_both_models"] is True, "mismos sitios")

    print(f"{OK} comprobaciones OK, {len(FAIL)} fallos")
    for msg in FAIL:
        print("  FALLO:", msg)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
