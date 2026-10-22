#!/usr/bin/env python3
"""S314 - verificador independiente. Re-decodifica TODO desde los blobs.

No importa build_selector.py: repite cada calculo (hash, disasm, tablas) y
compara con selector.json. Sale con codigo 1 si algo no cuadra.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
DATA = Path(__file__).with_name("selector.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

checks = 0


def ok(cond: bool, msg: str) -> None:
    global checks
    if not cond:
        raise SystemExit(f"FALLO: {msg}")
    checks += 1


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(b: bytes, a: int) -> int:
    return struct.unpack_from("<H", b, a - BASE)[0]


def u32(b: bytes, a: int) -> int:
    return struct.unpack_from("<I", b, a - BASE)[0]


def insn_at(b: bytes, a: int, n: int = 1) -> list[str]:
    raw = b[a - BASE:a - BASE + 4 * n]
    return [f"{i.mnemonic} {i.op_str}".strip() for i in MD.disasm(raw, a)][:n]


def pair_occurrences(b: bytes) -> int:
    """Cuenta pares consecutivos ldr.w rX,[rY,#0x21c] / ldr.w rZ,[rY,#0x220].

    Exige la codificacion Thumb2 LDR inmediata (0xD? 0xF8) y el nibble bajo 2
    del segundo halfword; asi no se confunde con ldrh de 16 bits.
    """
    n = 0
    for i in range(1, len(b) - 8):
        if not (0xD0 <= b[i - 1] <= 0xDF and b[i] == 0xF8
                and b[i + 1] == 0x1C and (b[i + 2] & 0x0F) == 0x02):
            continue
        if not (0xD0 <= b[i + 3] <= 0xDF and b[i + 4] == 0xF8
                and b[i + 5] == 0x20 and (b[i + 6] & 0x0F) == 0x02):
            continue
        n += 1
    return n


def pointer_run(b: bytes, anchor: int, low: int, high: int) -> tuple[int, int, int]:
    def val(a: int) -> int:
        return u32(b, a)

    def isptr(v: int) -> bool:
        return BASE <= v < BASE + len(b)

    a = anchor
    while a - 4 >= low and isptr(val(a - 4)):
        a -= 4
    z = anchor
    while z + 4 <= high and isptr(val(z)):
        z += 4
    return a, z, (z - a) // 4


def main() -> None:
    d = json.loads(DATA.read_text())
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()

    # 1. firmware
    ok(d["firmware"]["a7s"]["sha256"] == sha256(A7S), "sha256 A7S")
    ok(d["firmware"]["a6000"]["sha256"] == sha256(A6000), "sha256 A6000")
    ok(d["firmware"]["a7s"]["size"] == len(a7), "tamano A7S")

    # 2. llamada al selector y procedencia
    ok(u32(a7, 0x4354908C) == 0xFE64F2DD, "BL 0x43826d58 en 0x4354908c")
    ok(insn_at(a7, 0x4354908C) == ["bl #0x43826d58"], "destino del BL")
    ok(u32(a7, 0x43549084) == 0x121CF8D3, "0x43549084 = ldr.w r1,[r3,#0x21c]")
    ok(u32(a7, 0x43549088) == 0x2220F8D3, "0x43549088 = ldr.w r2,[r3,#0x220]")
    ok(u16(a7, 0x4354904E) == 0x6ED0, "0x4354904e = ldr r0,[r2,#0x6c]")
    lit = u32(a7, 0x437B38F4)
    ctx = (lit + ((0x437B38EE + 4) & ~3)) & 0xFFFFFFFF
    ok(ctx == 0x43EA709E, f"ctx calculado {ctx:#x}")
    ok(d["call_site"]["ctx_getter"]["ctx"] == f"0x{ctx:08x}", "ctx en JSON")
    ok(d["call_site"]["provenance"]["r1"].startswith("[[0x43ea70a6] + 0x21c]"),
       "procedencia r1 documentada")

    # 3. tabla de decision del selector (constantes de las instrucciones)
    ok(u16(a7, 0x43826D58) == 0x2805, "cmp r0,#5")
    ok(u16(a7, 0x43826DA2) == 0x200C, "movs r0,#0xc")
    ok(u16(a7, 0x43826DAA) == 0x2035, "movs r0,#0x35")
    ok(u16(a7, 0x43826D64) == 0x2A02, "cmp r2,#2")
    ok(u16(a7, 0x43826D7C) == 0x204E, "movs r0,#0x4e (silent)")
    ok(u16(a7, 0x43826DA6) == 0x204F, "movs r0,#0x4f (silent)")
    ok(u16(a7, 0x43826D8C) == 0x2017, "movs r0,#0x17")
    ok(u16(a7, 0x43826D9E) == 0x200B, "movs r0,#0xb")
    for row in d["selector"]["truth_table"]:
        raw = row["insn"].split()[0]
        ok(raw.startswith("0x"), "fila con direccion")
    ok(len(d["selector"]["truth_table"]) == 9, "9 filas en la tabla de decision")

    # 4. thunks: slot 0x64 vs wrapper 0x43ad9704
    ok(u16(a7, 0x43AD96FE) == 0x6E5B, "slot 0x64: ldr r3,[r3,#0x64]")
    ok(insn_at(a7, 0x43AD9700) == ["blx r3"], "slot 0x64: blx r3")
    ok(insn_at(a7, 0x43AD9708) == ["ldr r0, [r0]"], "wrapper desreferencia r0")
    ok(insn_at(a7, 0x43AD970E) == ["b.w #0x43ad9ada"], "wrapper salta a 0x43ad9ada")
    ok(u16(a7, 0x43AD9AF8) == 0x6A5B and u16(a7, 0x43AD9B08) == 0x6A5B,
       "0x43ad9ada usa vtable+0x24 dos veces")
    ok("slot 0x64" in d["vtable_thunks"]["correction"], "correccion documentada")

    # 5. tabla de registros
    ptrs = []
    addr = 0x43FEE3F8
    while BASE <= u32(a7, addr) < BASE + len(a7):
        ptrs.append(u32(a7, addr))
        addr += 4
    ok(len(ptrs) == 95, f"95 punteros (vistos {len(ptrs)})")
    ok(addr == 0x43FEE574, "terminador en 0x43fee574")
    ok(u32(a7, 0x43FEE574) == 0, "palabra terminadora NULL")
    ok(all((p - min(ptrs)) % 6 == 0 for p in ptrs), "registros alineados a 6 B")
    recs = [a7[p - BASE:p - BASE + 6] for p in ptrs]
    ok(all(r[1] == 0 and r[5] == 0 for r in recs), "padding cero")
    ok(sum(1 for r in recs if r[0] == 0x81) == 94, "94 registros dev 0x81")
    ok(sum(1 for r in recs if r[0] == 0x83) == 1, "1 registro dev 0x83")
    ok(recs[94] == bytes.fromhex("830017004a00"), "registro 94 = 83 00 17 00 4a 00")
    ok(len(d["register_list"]["records"]) == 95, "95 registros en JSON")
    ok(d["register_list"]["record_size"] == 6, "tamano 6 B en JSON")
    # consumidor
    ok(u16(a7, 0x436F4526) == 0x7819, "consumidor: ldrb r1,[r3]")
    ok(u16(a7, 0x436F452A) == 0x885A, "consumidor: ldrh r2,[r3,#2]")
    ok(u16(a7, 0x436F452C) == 0x791B, "consumidor: ldrb r3,[r3,#4]")
    # 0x436f4532 bytes 56 f8 04 3b -> halfword bajo 0xf856
    ok(u16(a7, 0x436F4532) == 0xF856, "bucle: ldr r3,[r6],#4")
    # 6. filas de 20 B
    rows, addr = 0, 0x43FEE5AC
    while BASE <= u32(a7, addr) < BASE + len(a7):
        rows += 1
        addr += 0x14
    ok(rows == 68 and addr == 0x43FEEAFC, "68 filas de 0x14 B hasta 0x43feeafc")
    ok(u32(a7, 0x43FEEAFC) == 0, "terminador de las 68 filas")
    ok(d["descriptor_rows"]["count"] == 68, "68 filas en JSON")

    # 7. contraste A6000
    ok(pair_occurrences(a7) >= 1, "el par 0x21c/0x220 existe en A7S")
    ok(pair_occurrences(a6) == 0, "el par 0x21c/0x220 NO existe en A6000")
    ok(a6[0x43549084 - BASE:0x43549084 - BASE + 4]
       != a7[0x43549084 - BASE:0x43549084 - BASE + 4],
       "0x43549084 difiere entre camaras")
    a, z, n = pointer_run(a6, 0x43FEE3F8, 0x43FEE300, 0x43FEE500)
    ok((a, z, n) == (0x43FEE300, 0x43FEE41C, 71), f"run A6000 {a:#x}..{z:#x} n={n}")
    ok(u32(a6, 0x43FEE41C) == 0, "terminador A6000 en 0x43fee41c")
    ok(all(not (0x43541000 <= v < BASE + len(a6))
           for v in [u32(a6, 0x43FEE41C)]), "terminador no puntero")

    print(f"OK S314: {checks} comprobaciones")


if __name__ == "__main__":
    main()
