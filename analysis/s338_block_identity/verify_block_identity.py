#!/usr/bin/env python3
"""S338 - verificacion independiente de `block_identity.json`.

Uso: ``.venv/bin/python analysis/s338_block_identity/verify_block_identity.py``
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
DATA = HERE / "block_identity.json"
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


def insn(blob: bytes, addr: int) -> str:
    i = next(iter(MD.disasm(blob[addr - BASE:addr - BASE + 4], addr)))
    return f"{i.mnemonic} {i.op_str}".strip()


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()
    check(hashlib.sha256(a7).hexdigest() == data["firmware"]["a7s_fw320"]["sha256"],
          "sha256 A7S")
    check(hashlib.sha256(a6).hexdigest() == data["firmware"]["a6000_fw321"]["sha256"],
          "sha256 A6000")

    # literales del bloque en ambos modelos
    for name, blob in (("a7s", a7), ("a6000", a6)):
        sites = data["dfe_block"]["literal_sites"][name]
        check(bool(sites), f"{name}: sitios del bloque")
        for s in sites:
            check(u32(blob, int(s, 16)) == 0xFC02A000, f"{name}: literal en {s}")

    # el registro de S335 esta dentro del bloque
    reg = int(data["dfe_block"]["register"], 16)
    base = int(data["dfe_block"]["base"], 16)
    check(reg - base == 0xC, "registro = base + 0xc")

    # A7S: getter base+8 y writer base
    check(insn(a7, 0x436F201C) == "adds r3, #8", "A7S getter: base + 8")
    check(insn(a7, 0x436F202C) == "ldr r3, [pc, #4]", "A7S writer: literal")
    check(insn(a7, 0x436F202E) == "str r0, [r3]", "A7S writer: str")
    for name, meta in data["dfe_block"]["a7s_code"].items():
        check(meta["disasm"][0]["address"] == f"0x{int(meta['address'], 16):08x}",
              f"A7S {name}: direccion")

    # A6000 equivalentes
    for name, meta in data["dfe_block"]["a6000_code"].items():
        addr = int(meta["address"], 16)
        check(meta["disasm"][0]["address"] == f"0x{addr:08x}", f"A6000 {name}: inicio")
        ops = [i["insn"] for i in meta["disasm"]]
        if name == "getter_base_plus_8":
            check("adds r3, #8" in ops, f"A6000 {name}: base + 8")
        else:
            check("str r0, [r3]" in ops, f"A6000 {name}: str")

    # cadenas
    for needle, sites in data["strings"].items():
        check(len(sites["a7s"]) == 0 or bool(sites["a7s"]), f"cadena {needle} A7S")
        if needle in ("DFECore", "CISIF"):
            check(bool(sites["a7s"]) and bool(sites["a6000"]),
                  f"cadena {needle} en ambos")
        for s in sites["a7s"]:
            check(a7[int(s, 16) - BASE:int(s, 16) - BASE + len(needle)] ==
                  needle.encode("latin-1"), f"cadena A7S en {s}")
        for s in sites["a6000"]:
            check(a6[int(s, 16) - BASE:int(s, 16) - BASE + len(needle)] ==
                  needle.encode("latin-1"), f"cadena A6000 en {s}")

    # evidencia del repo
    ev = data["repo_evidence"]
    check(ev["ghidra_snippet"] is not None and "fc02a008" in ev["ghidra_snippet"],
          "ghidra: cita del registro")
    check(bool(ev["s56_lines"]), "S56-B: lineas citadas")

    v = data["verdicts"]
    check(v["block_is_cisif_receiver"] is True, "CISIF")
    check(v["p2s_transport_affected"] is False, "P2S no afectado")
    check(v["unknown_block_identified"] is False, "0xf292b000 sin identificar")

    print(f"{OK} comprobaciones OK, {len(FAIL)} fallos")
    for msg in FAIL:
        print("  FALLO:", msg)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
