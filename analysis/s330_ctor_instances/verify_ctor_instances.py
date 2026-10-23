#!/usr/bin/env python3
"""S330 - verificacion independiente de `ctor_instances.json` contra los bytes.

Re-decodifica los BL con capstone (operando inmediato) en lugar de la formula
aritmetica del build, y re-comprueba literales, vtable y el bloque de la
factoria singleton.

Uso: ``.venv/bin/python analysis/s330_ctor_instances/verify_ctor_instances.py``
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
DATA = HERE / "ctor_instances.json"
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


def u16(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<H", blob, addr - BASE)[0]


def branch_sites(blob: bytes) -> list[tuple[int, int]]:
    """(direccion, destino) de cada BL/BLX, leidos del operando de capstone."""
    out = []
    for i in range(0, len(blob) - 4, 2):
        h1 = struct.unpack_from("<H", blob, i)[0]
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = struct.unpack_from("<H", blob, i + 2)[0]
        if (h2 & 0xD000) not in (0xD000, 0xC000):
            continue
        addr = BASE + i
        ins = next(iter(MD.disasm(blob[i:i + 4], addr)), None)
        if ins is None or ins.mnemonic not in ("bl", "blx"):
            continue
        target = ins.operands[0].imm
        out.append((addr, target))
    return out


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    blob = A7S.read_bytes()
    check(hashlib.sha256(blob).hexdigest() == data["scan_a7s"]["sha256"], "sha256 A7S")

    ctor = int(data["ctor"]["address"], 16)
    check(ctor == 0x436F3FC0, "ctor direccion")

    calls = [(a, t) for a, t in branch_sites(blob) if t == ctor]
    check(len(calls) == 1, f"un solo BL al ctor (vistos {len(calls)})")
    check(bool(calls) and calls[0][0] == 0x436F2A8A,
          "el BL esta en 0x436f2a8a")
    check([c["addr"] for c in data["scan_a7s"]["direct_calls"]] ==
          [f"0x{a:08x}" for a, _ in calls], "JSON coincide con la re-decodificacion")

    for value in (ctor, ctor + 1):
        hits = []
        pat = struct.pack("<I", value)
        i = blob.find(pat)
        while i >= 0:
            hits.append(BASE + i)
            i = blob.find(pat, i + 1)
        check(not hits, f"sin literales de 0x{value:08x}")
    check(data["scan_a7s"]["literal_ctor"] == [], "JSON: sin literal")
    check(data["scan_a7s"]["literal_ctor_thumb"] == [], "JSON: sin literal thumb")

    vt_base = int(data["vtable"]["base"], 16)
    check(vt_base == 0x43FCE050, "vtable base")
    values = [u32(blob, vt_base + 4 * e["slot"]) for e in data["vtable"]["entries"]]
    check(values == [int(e["value"], 16) for e in data["vtable"]["entries"]],
          "vtable: valores")
    check(ctor not in values and ctor + 1 not in values, "ctor fuera de la vtable")
    check(data["vtable"]["ctor_slots"] == [], "JSON: ctor_slots vacio")

    # idx constante: movs r1,#0 inmediatamente antes del BL
    pre = next(iter(MD.disasm(blob[0x436F2A7E - BASE:0x436F2A8A - BASE], 0x436F2A7E)))
    check(pre.mnemonic == "movs" and pre.op_str == "r1, #0", "movs r1,#0 antes del BL")

    # factoria: singleton y registro
    fac = data["factory"]
    check(fac["direct_callers"] == [], "factoria sin BL directos")
    order = [i["insn"] for i in data["known_caller"]["disasm"]]
    check(order[0].startswith("push"), "factoria: prologo")
    check(any("movs r1, #0" in i for i in order), "factoria: idx=0")
    check(any(i.startswith("bl ") for i in order), "factoria: BL al ctor")
    slot = int(fac["singleton_slot"], 16)
    check(slot == 0x440245CC, "slot singleton")
    check(u32(blob, slot) == int(fac["singleton_value"], 16), "valor singleton")

    # el store de +0x2b4 en el ctor (S327) sigue siendo `str` con r6=r1
    store = int(data["ctor"]["store_field"], 16)
    ins = next(iter(MD.disasm(blob[store - BASE:store - BASE + 4], store)))
    check(ins.mnemonic.startswith("str") and "0x2b4" in ins.op_str,
          "store +0x2b4")

    print(f"{OK} comprobaciones OK, {len(FAIL)} fallos")
    for msg in FAIL:
        print("  FALLO:", msg)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
