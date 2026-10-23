#!/usr/bin/env python3
"""S336 - verificacion independiente de `table_consumers.json`.

Uso: ``.venv/bin/python analysis/s336_table_consumers/verify_table_consumers.py``
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
DATA = HERE / "table_consumers.json"
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


def insn(blob: bytes, addr: int) -> str:
    i = next(iter(MD.disasm(blob[addr - BASE:addr - BASE + 4], addr)))
    return f"{i.mnemonic} {i.op_str}".strip()


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def pic(blob: bytes, ldr: int, add: int) -> int:
    ins = next(iter(MD.disasm(blob[ldr - BASE:ldr - BASE + 4], ldr)))
    lit = ((ldr + 4) & ~3) + ins.operands[1].mem.disp
    return (u32(blob, lit) + ((add + 4) & ~1)) & 0xFFFFFFFF


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    blob = A7S.read_bytes()
    check(hashlib.sha256(blob).hexdigest() == data["firmware"]["a7s_fw320"]["sha256"],
          "sha256 A7S")

    # cada referencia del JSON resuelve al base declarado
    for ref in data["references"]:
        base = pic(blob, int(ref["ldr"], 16), int(ref["add"], 16))
        check(f"0x{base:08x}" == ref["base"], f"{ref['ldr']} -> {ref['base']}")
        check(base == int(data["tables"][ref["table"]], 16), f"{ref['ldr']} tabla")

    # recuento y reparto por funcion
    check(data["reference_count"] == len(data["references"]) == 13,
          "13 referencias")
    expected = {"op_code_w0": 2, "copy_row_patch": 3, "sum_w0": 2,
                "index_and_mask": 3, "row_selectors": 0,
                "row_selectors_entry": 1, "mask_helper_1": 1,
                "mask_helper_3": 1}
    got = {name: len(c["references"]) for name, c in data["consumers"].items()}
    check(got == expected, f"reparto por funcion {got}")

    # instrucciones clave de cada consumidor
    check(insn(blob, 0x436F5FA6) == "ldm.w lr!, {r0, r1, r2, r3}",
          "copy_row_patch: copia de 4 palabras")
    check(insn(blob, 0x436F5FAC) == "ldr.w r3, [lr]", "copy_row_patch: 5a palabra")
    check(insn(blob, 0x436F5FB8) == "ldrb r3, [r7, #0x18]", "copy_row_patch: flag")
    check(insn(blob, 0x436F5FC6) == "strb.w r3, [sp, #0xb]", "copy_row_patch: parchea +7")
    check(insn(blob, 0x436F5FD2) == "bl #0x43ada310", "copy_row_patch: escritor")
    check(insn(blob, 0x436F607E) == "ldr r1, [r3, r5]", "sum_w0: w0")
    check(insn(blob, 0x436F6080) == "bl #0x43ada4d8", "sum_w0: helper")
    check(insn(blob, 0x436F6092) == "adds r0, r0, r6", "sum_w0: suma")
    check(insn(blob, 0x436F6240) == "ldrb r3, [r0, #5]", "row_selectors: +5")
    check(insn(blob, 0x436F624A) == "ldrb r2, [r0, #6]", "row_selectors: +6")
    check(insn(blob, 0x436F6256) == "ldrb r2, [r0, #4]", "row_selectors: +4")
    check(insn(blob, 0x436F61AE) == "ldrh r1, [r3, #0x18]",
          "index_and_mask: mascara")
    check(insn(blob, 0x436F61B0) == "ldr r2, [r3, #0x14]", "index_and_mask: indice")

    v = data["verdicts"]
    check(v["only_index_and_mask"] is False, "no solo indice y mascara")
    check(v["consumer_functions"] == 7, "7 funciones con referencias")
    check(v["row_field_consumers"] == 5, "5 funciones leen campos de fila")
    check("+0x04" in v["fields_consumed_superset"], "+0x04 consumido")
    check("NO_VERIFICADO" in v["w4_semantics"], "w4 sin verificar")

    print(f"{OK} comprobaciones OK, {len(FAIL)} fallos")
    for msg in FAIL:
        print("  FALLO:", msg)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
