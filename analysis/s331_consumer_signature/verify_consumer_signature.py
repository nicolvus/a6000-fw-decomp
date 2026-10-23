#!/usr/bin/env python3
"""S331 - verificacion independiente de `consumer_signature.json`.

Rehace con capstone las pruebas que fijan la firma `(obj, posicion_modo, flag)`:
movimientos de registro en el consumidor, los dos llamadores y la busqueda
lineal que produce el indice.

Uso: ``.venv/bin/python analysis/s331_consumer_signature/verify_consumer_signature.py``
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
DATA = HERE / "consumer_signature.json"
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

    # 1) consumidor: r5 = r1 (indice) y stride = 0x1c * r5
    check(insn(blob, 0x436F6192) == "mov r5, r1", "consumidor: mov r5,r1")
    check(insn(blob, 0x436F61A4) == "movs r2, #0x1c", "consumidor: stride 0x1c")
    check(insn(blob, 0x436F61A6) == "muls r5, r2, r5", "consumidor: muls r5,r2,r5")
    check(insn(blob, 0x436F6196) == "cmp r2, #1", "consumidor: cmp r2,#1 (flag)")
    check(insn(blob, 0x436F6198) == "bne #0x436f61a2", "consumidor: bne tras flag")
    # el flag se comprueba antes de reutilizar r2 como stride
    order = [i["insn"] for i in data["consumer"]["disasm"]]
    check(order.index("cmp r2, #1") < order.index("movs r2, #0x1c"),
          "flag comprobado antes del stride")

    # 2) llamador del setter: indice desde la busqueda, flag desde obj+0x2b4
    check(insn(blob, 0x436F3BC0) == "bl #0x43ada284", "setter: busqueda lineal")
    check(insn(blob, 0x436F3BC6) == "mov r1, r0", "setter: r1 = resultado")
    check(insn(blob, 0x436F3BC8) == "strb.w r0, [r4, #0x1b8]",
          "setter: guarda el indice en +0x1b8")
    check(insn(blob, 0x436F3BDA) == "ldrb.w r1, [r4, #0x1b8]",
          "setter: r1 = indice")
    check(insn(blob, 0x436F3BDE) == "ldr.w r2, [r4, #0x2b4]", "setter: r2 = flag")
    check(insn(blob, 0x436F3BE2) == "bl #0x436f618c", "setter: llama al consumidor")

    # 3) segundo llamador
    check(insn(blob, 0x436F4472) == "bl #0x43ada284", "segundo: busqueda")
    check(insn(blob, 0x436F447A) == "mov r6, r0", "segundo: r6 = indice")
    check(insn(blob, 0x436F4476) == "ldr.w r2, [r4, #0x2b4]", "segundo: r2 = flag")
    check(insn(blob, 0x436F447E) == "mov r1, r6", "segundo: r1 = indice")
    check(insn(blob, 0x436F4480) == "bl #0x436f618c", "segundo: llama")

    # 4) busqueda lineal: devuelve indice o 0xff
    check(insn(blob, 0x43ADA286) == "movs r0, #0", "busqueda: arranca en 0")
    check(insn(blob, 0x43ADA29C) == "movs r0, #0xff", "busqueda: 0xff si no encuentra")
    check(insn(blob, 0x43ADA296) == "adds r0, #1", "busqueda: incrementa indice")

    # 5) hermanos con la misma firma
    for addr in (0x436F61F8, 0x436F60AC):
        check(insn(blob, addr) == "cmp r1, #0xff", f"hermano 0x{addr:x}: cmp r1")
        head = [insn(blob, addr + 2 + k) for k in (0, 2, 4)]
        check(any(s.startswith("push") for s in head),
              f"hermano 0x{addr:x}: prologo")
        check(any(s == "mov r4, r0" for s in head), f"hermano 0x{addr:x}: obj")

    # 6) filas por modo y diferencias
    codes = [u32(blob, 0x43FEE370 + 4 * i) for i in range(34)]
    pos = {c: i for i, c in enumerate(codes)}
    for name, base_s in data["tables"]["bases"].items():
        base = int(base_s, 16)
        for code, meta in data["tables"]["per_code"].items():
            c = int(code, 16)
            row = meta["rows"][name]
            check(meta["position"] == pos[c], f"{name} {code}: posicion")
            addr = base + 0x1C * pos[c]
            check(u32(blob, addr) == row["w0"], f"{name} {code}: w0")
            check(u32(blob, addr + 4) == int(row["w4"], 16), f"{name} {code}: w4")
            check(u32(blob, addr + 0x14) == row["descriptor_index"],
                  f"{name} {code}: indice")
            check(u16(blob, addr + 0x18) == row["mask"], f"{name} {code}: mascara")
            check(row["descriptor_index"] <= 1, f"{name} {code}: indice <= 1")

    t2 = data["pair_diffs"]["T2"]["0x4e/0x4c"]
    check(t2["identical"] is False, "T2 0x4e/0x4c difiere")
    check(t2["fields_diff"] == {"mask": [0, 1023]}, "T2: solo cambia la mascara")
    for name in ("T1", "T3"):
        check(data["pair_diffs"][name]["0x4e/0x4c"]["identical"] is True,
              f"{name} 0x4e/0x4c identicas")

    print(f"{OK} comprobaciones OK, {len(FAIL)} fallos")
    for msg in FAIL:
        print("  FALLO:", msg)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
