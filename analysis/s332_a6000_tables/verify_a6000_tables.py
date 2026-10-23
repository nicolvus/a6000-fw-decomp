#!/usr/bin/env python3
"""S332 - verificacion independiente de `a6000_tables.json`.

Rehace las bases PIC leyendo el operando de capstone, la lista de modos por el
slot GOT y las filas de las tablas de ambos modelos.

Uso: ``.venv/bin/python analysis/s332_a6000_tables/verify_a6000_tables.py``
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
DATA = HERE / "a6000_tables.json"
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


def u16(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<H", blob, addr - BASE)[0]


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def insn(blob: bytes, addr: int) -> str:
    i = next(iter(MD.disasm(blob[addr - BASE:addr - BASE + 4], addr)))
    return f"{i.mnemonic} {i.op_str}".strip()


def pic(blob: bytes, ldr: int, add: int) -> int:
    lit_ins = next(iter(MD.disasm(blob[ldr - BASE:ldr - BASE + 4], ldr)))
    lit = ((ldr + 4) & ~3) + lit_ins.operands[1].mem.disp
    return (u32(blob, lit) + ((add + 4) & ~1)) & 0xFFFFFFFF


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    a6 = A6000.read_bytes()
    a7 = A7S.read_bytes()
    check(hashlib.sha256(a6).hexdigest() == data["firmware"]["a6000_fw321"]["sha256"],
          "sha256 A6000")
    check(hashlib.sha256(a7).hexdigest() == data["firmware"]["a7s_fw320"]["sha256"],
          "sha256 A7S")

    # lista de modos A6000
    got = pic(a6, 0x436D6B50, 0x436D6B56)
    lit = ((0x436D6B86 + 4) & ~3) + (u16(a6, 0x436D6B86) & 0xFF) * 4
    slot = (got + u32(a6, lit)) & 0xFFFFFFFF
    list_ptr = u32(a6, slot)
    codes = [u32(a6, list_ptr + 4 * i) for i in range(13)]
    check([f"0x{c:02x}" for c in codes] == data["a6000"]["mode_list"]["codes"],
          "lista de modos A6000")
    check(slot == int(data["a6000"]["mode_list"]["slot"], 16), "slot de la lista")
    check(list_ptr == int(data["a6000"]["mode_list"]["pointer"], 16), "puntero lista")

    # tablas A6000
    for name, meta in data["a6000"]["tables"].items():
        ldr, add = {"TA1": (0x436D8EB0, 0x436D8EB8),
                    "TA2": (0x436D8EC8, 0x436D8ECC)}[name]
        base = pic(a6, ldr, add)
        check(base == int(meta["base"], 16), f"{name}: base")
        for row in meta["rows"]:
            addr = base + 0x1C * row["index"]
            check(u32(a6, addr) == row["w0"], f"{name} f{row['index']}: w0")
            check(u32(a6, addr + 0x14) == row["descriptor_index"],
                  f"{name} f{row['index']}: indice")
            check(u16(a6, addr + 0x18) == row["mask"], f"{name} f{row['index']}: mascara")
            check(row["descriptor_index"] <= 2, f"{name} f{row['index']}: indice <= 2")

    # descriptores A6000 (compartidos por los dos helpers)
    d1 = pic(a6, 0x436D8C60, 0x436D8C62)
    d2 = pic(a6, 0x436D8E38, 0x436D8E3A)
    check(d1 == d2 == int(data["a6000"]["descriptor"]["base"], 16), "descriptor base")
    rows = [list(a6[d1 - BASE + 12 * k:d1 - BASE + 12 * k + 12]) for k in range(3)]
    check(rows == data["a6000"]["descriptor"]["rows"], "descriptor filas")
    check(rows[0] == list(range(12)), "descriptor fila 0 identidad")
    check(rows[1] == [0, 7, 6, 1, 2, 9, 8, 3, 4, 11, 10, 5], "descriptor fila 1")

    # consumidor A6000
    check(insn(a6, 0x436D8EB2) == "movs r2, #0x1c", "consumidor: stride")
    check(insn(a6, 0x436D8EB4) == "muls r5, r2, r5", "consumidor: muls")
    check(insn(a6, 0x436D8EBC) == "ldrh r1, [r3, #0x18]", "consumidor: mascara")
    check(insn(a6, 0x436D8EBE) == "ldr r2, [r3, #0x14]", "consumidor: indice")
    check(insn(a6, 0x436D8EC0) == "add.w r3, r4, #0x14", "consumidor: dest obj+0x14")
    check(insn(a6, 0x436D8ED0) == "add.w r3, r4, #0xa1", "consumidor: dest obj+0xa1")
    check(insn(a6, 0x436D8ED8) == "pop.w {r4, r5, r6, lr}", "consumidor: tail-call")

    # setter A6000
    check(insn(a6, 0x436D6B62) == "cmp r2, #0x47", "setter: limite 0x47")
    check(insn(a6, 0x436D6BB8) == "bl #0x43ad9438", "setter: busqueda")
    check(insn(a6, 0x436D6BC0) == "strb.w r0, [r4, #0x17c]", "setter: guarda indice")
    check(insn(a6, 0x436D6BCE) == "blx r3", "setter: slot 40")
    check(insn(a6, 0x436D6BDA) == "bl #0x436d8e6c", "setter: consumidor")
    check(insn(a6, 0x436D6BD6) == "ldr.w r2, [r4, #0x26c]", "setter: flag")

    # A7S: tablas y descriptor
    for name, meta in data["a7s"]["tables"].items():
        base = {"T1": 0x43BBEB70, "T2": 0x43BBF2E8, "T3": 0x43BBEF30}[name]
        check(base == int(meta["base"], 16), f"A7S {name}: base")
        for row in meta["rows"]:
            addr = base + 0x1C * row["index"]
            check(u32(a7, addr + 0x14) == row["descriptor_index"],
                  f"A7S {name} f{row['index']}: indice")
            check(u16(a7, addr + 0x18) == row["mask"],
                  f"A7S {name} f{row['index']}: mascara")
    d7 = [list(a7[0x43C9D09B - BASE + 12 * k:0x43C9D09B - BASE + 12 * k + 12])
          for k in range(2)]
    check(d7 == data["a7s"]["descriptor"]["rows"], "A7S descriptor filas")

    cmp_ = data["comparison"]
    check(cmp_["counts"] == {"a6000": 13, "a7s": 34}, "comparacion: conteos")
    check(cmp_["descriptor_index_used"]["a6000"] == [0], "A6000 solo descriptor 0")
    check(cmp_["descriptor_index_used"]["a7s"] == [0, 1], "A7S usa 0 y 1")
    check(cmp_["zero_masks"]["a6000"] == 0, "A6000 sin mascaras cero")
    check(cmp_["zero_masks"]["a7s"] == 30, "A7S con 30 mascaras cero")
    check(cmp_["mask_union"]["a6000"] == [3840, 4095], "A6000 mascaras {0xf00,0xfff}")
    check(cmp_["descriptor_rows"] == {"a6000": 3, "a7s": 2}, "filas de descriptor")

    print(f"{OK} comprobaciones OK, {len(FAIL)} fallos")
    for msg in FAIL:
        print("  FALLO:", msg)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
