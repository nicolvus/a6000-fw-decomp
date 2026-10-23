#!/usr/bin/env python3
"""S335 - verificacion independiente de `mmio_layer.json`.

Uso: ``.venv/bin/python analysis/s335_mmio_layer/verify_mmio_layer.py``
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
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
DATA = HERE / "mmio_layer.json"
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

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


def ops(blob: bytes, start: int, size: int) -> list[str]:
    return [i.mnemonic for i in MD.disasm(blob[start - BASE:start - BASE + size], start)]


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()
    check(hashlib.sha256(a7).hexdigest() == data["firmware"]["a7s_fw320"]["sha256"],
          "sha256 A7S")
    check(hashlib.sha256(a6).hexdigest() == data["firmware"]["a6000_fw321"]["sha256"],
          "sha256 A6000")

    # cada accesor tiene un literal absoluto en rango MMIO y una operacion acorde
    expect = {
        "0x436f8290": (0xF292B008, "str"),
        "0x436f82a0": (0xF292B004, "str"),
        "0x436f82b0": (0xF292B000, "ldr"),
        "0x436f82c0": (0xF292B008, "str"),
        "0x436f82e8": (0xFC02A00C, "str"),
        "0x436f8300": (0xFC02A00C, "str"),
        "0x436f8314": (0xFC02A00C, "ldr"),
        "0x436f8324": (0xFC02A00C, "str"),
    }
    for name, (value, op) in expect.items():
        entry = data["a7s_layer"][name]
        lits = [int(lit["value"], 16) for lit in entry["literals"]]
        check(value in lits, f"{name}: literal 0x{value:08x}")
        check(op in ops(a7, int(name, 16), 0x12), f"{name}: operacion {op}")

    # 0x436f82d0: dos destinos (0xf292b008 / 0xf292b004) segun r0
    d0 = [int(lit["value"], 16) for lit in data["a7s_layer"]["0x436f82d0"]["literals"]]
    check(d0 == [0xF292B008, 0xF292B004], "82d0: dos destinos")
    check(ops(a7, 0x436F82D0, 0x14).count("str") == 1, "82d0: un store con dos destinos")

    # campo de 12 bits: lsls #0x14 / lsrs #0x14 y bfi #0,#0xc
    check(ops(a7, 0x436F82B0, 0xA).count("lsls") == 1, "82b0: lsls")
    check(ops(a7, 0x436F82B0, 0xA).count("lsrs") == 1, "82b0: lsrs")
    check(ops(a7, 0x436F8300, 0x10).count("bfi") == 1, "8300: bfi")
    check(ops(a7, 0x436F8324, 0xE).count("bfc") == 1, "8324: bfc (bit 12)")

    # A6000: cada sitio MMIO va precedido de un ldr pc-rel que lo carga
    def loaded_by_ldr(blob: bytes, site: int) -> bool:
        for back in range(2, 0x18, 2):
            addr = site - back
            ins = next(iter(MD.disasm(blob[addr - BASE:addr - BASE + 2], addr)), None)
            if ins is None or ins.mnemonic != "ldr" or "[pc" not in ins.op_str:
                continue
            imm = int(ins.op_str.split("#")[1].rstrip("]"), 16)
            if ((addr + 4) & ~3) + imm == site:
                return True
        return False

    for addr, site in data["mmio"]["sites"].items():
        for s in site["a6000"]:
            check(loaded_by_ldr(a6, int(s, 16)), f"A6000: {s} cargado por ldr pc-rel")

    # conteo de sitios identico en ambos modelos
    for addr, site in data["mmio"]["sites"].items():
        check(len(site["a7s"]) == len(site["a6000"]),
              f"sitios {addr}: mismo numero en ambos")
        for s in site["a7s"]:
            check(u32(a7, int(s, 16)) == int(addr, 16), f"valor A7S en {s}")
        for s in site["a6000"]:
            check(u32(a6, int(s, 16)) == int(addr, 16), f"valor A6000 en {s}")

    v = data["verdicts"]
    check(v["mask_path_ends_in_mmio"] and v["p2s_hypothesis"] == "DESCARTADA",
          "veredicto MMIO")
    check(v["same_layer_in_a6000"], "misma capa en A6000")

    print(f"{OK} comprobaciones OK, {len(FAIL)} fallos")
    for msg in FAIL:
        print("  FALLO:", msg)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
