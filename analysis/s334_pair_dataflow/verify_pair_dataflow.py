#!/usr/bin/env python3
"""S334 - verificacion independiente de `pair_dataflow.json`.

Uso: ``.venv/bin/python analysis/s334_pair_dataflow/verify_pair_dataflow.py``
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
DATA = HERE / "pair_dataflow.json"
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

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


def u16(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<H", blob, addr - BASE)[0]


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    blob = A7S.read_bytes()
    check(hashlib.sha256(blob).hexdigest() == data["firmware"]["a7s_fw320"]["sha256"],
          "sha256 A7S")

    # 1) colapso en mascara u16: bucle de 24 B, 1<<byte, OR, uxth, strh +0x68
    check(insn(blob, 0x43ADA378) == "ldrb r4, [r1, r2]", "colapso: flag")
    check(insn(blob, 0x43ADA37A) == "cbz r4, #0x43ada38a", "colapso: if flag")
    check(insn(blob, 0x43ADA380) == "ldrb r4, [r4, #1]", "colapso: byte del par")
    check(insn(blob, 0x43ADA382) == "lsls.w r4, r5, r4", "colapso: 1 << byte")
    check(insn(blob, 0x43ADA386) == "orrs r0, r4", "colapso: OR")
    check(insn(blob, 0x43ADA388) == "uxth r0, r0", "colapso: u16")
    check(insn(blob, 0x43ADA38C) == "cmp r2, #0x18", "colapso: 24 B")
    check(insn(blob, 0x43ADA390) == "strh.w r0, [r3, #0x68]", "colapso: guarda +0x68")
    check(insn(blob, 0x43ADA3A0) == "b.w #0x436f822c", "colapso: tail apply")

    # 2) variante con destino y op
    check(insn(blob, 0x43ADA408) == "ldrb r6, [r1, r4]", "dst: flag")
    check(insn(blob, 0x43ADA412) == "lsls.w r6, r7, r6", "dst: 1 << byte")
    check(insn(blob, 0x43ADA41C) == "cmp r4, #0x18", "dst: 24 B")
    check(insn(blob, 0x43ADA420) == "strh r5, [r2]", "dst: guarda en [r2]")
    check(insn(blob, 0x43ADA42C) == "b.w #0x436f822c", "dst: tail apply")

    # 3) quien colapsa: 0x436f61f8 (obj+0x16 -> +0x68; obj+0xa5 -> +0xf8, op 1)
    check(insn(blob, 0x436F6212) == "add.w r1, r4, #0x16", "61f8: pares +0x16")
    check(insn(blob, 0x436F6216) == "bl #0x43ada370", "61f8: colapso +0x68")
    check(insn(blob, 0x436F6226) == "add.w r1, r4, #0xa5", "61f8: pares +0xa5")
    check(insn(blob, 0x436F622A) == "add.w r2, r4, #0xf8", "61f8: destino +0xf8")
    check(insn(blob, 0x436F622E) == "movs r3, #1", "61f8: op 1")
    check(insn(blob, 0x436F6234) == "b.w #0x43ada402", "61f8: colapso dst")

    # 4) 0x436f60ac aplica obj+0x68 con op 0
    check(insn(blob, 0x436F60C8) == "add.w r1, r4, #0x68", "60ac: mascara +0x68")
    check(insn(blob, 0x436F60CE) == "movs r2, #0", "60ac: op 0")
    check(insn(blob, 0x436F60D4) == "bl #0x436f81b4", "60ac: apply")

    # 5) selector de operacion por w0
    check(insn(blob, 0x436F5EC0) == "movs r2, #0x1c", "5eac: stride")
    check(insn(blob, 0x436F5EC2) == "muls r2, r5, r2", "5eac: fila")
    check(insn(blob, 0x436F5EC6) == "ldr r2, [r3, r2]", "5eac: lee w0")
    check(insn(blob, 0x436F5ED0) == "cmp r2, #1", "5eac: w0 == 1")
    check(insn(blob, 0x436F5EF2) == "cmp r1, #2", "5eac: segundo w0 == 2")
    check(insn(blob, 0x436F5EFC) == "cmp r1, #3", "5eac: segundo w0 == 3")

    # 6) apply: lectura, complemento, xor, escritura
    check(insn(blob, 0x436F823C) == "bl #0x436f82b0", "apply: lectura op0")
    check(insn(blob, 0x436F8242) == "mvns r0, r0", "apply: complemento")
    check(insn(blob, 0x436F8244) == "eors r0, r3", "apply: xor con la mascara")
    check(insn(blob, 0x436F8246) == "uxth r0, r0", "apply: u16")
    check(insn(blob, 0x436F8248) == "bl #0x436f82a0", "apply: escritura")
    check(insn(blob, 0x436F825C) == "bl #0x436f8314", "apply: lectura op1")

    # 7) tablas por modo
    codes = [u32(blob, 0x43FEE370 + 4 * i) for i in range(34)]
    pos = {c: i for i, c in enumerate(codes)}
    bases = {"T1": 0x43BBEB70, "T2": 0x43BBF2E8, "T3": 0x43BBEF30}
    for code, meta in data["per_code"].items():
        c = int(code, 16)
        check(meta["position"] == pos[c], f"{code}: posicion")
        for name, base in bases.items():
            addr = base + 0x1C * pos[c]
            check(u32(blob, addr) == meta[name]["w0"], f"{code} {name}: w0")
            check(u16(blob, addr + 0x18) == meta[name]["mask"],
                  f"{code} {name}: mascara")
            check(u32(blob, addr + 0x14) == meta[name]["descriptor_index"],
                  f"{code} {name}: indice")

    silent_ops = data["verdicts"]["silent_op_codes"]
    check(silent_ops["0x4c"] == [0, 2] and silent_ops["0x50"] == [1, 3],
          "op por modo: 0x4c frente a 0x50")
    check(data["per_code"]["0x4e"]["T2"]["mask"] == 0, "0x4e: mascara T2 cero")
    check(data["per_code"]["0x4c"]["T2"]["mask"] == 0x3FF, "0x4c: mascara T2 0x3ff")
    check(data["verdicts"]["pair_second_byte_is_bit_index"], "byte = indice de bit")
    check(not data["verdicts"]["pair_second_byte_is_state_offset"],
          "byte != offset de estado")

    print(f"{OK} comprobaciones OK, {len(FAIL)} fallos")
    for msg in FAIL:
        print("  FALLO:", msg)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
