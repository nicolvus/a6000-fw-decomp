"""S52 coordinador: identidad del registro clase->param+9 (A7S). Ejecutar: python3 -I analysis/s52_coordinator_check.py"""
import hashlib
import struct
from pathlib import Path

BASE = 0x43541000
BLOB = (Path(__file__).resolve().parents[1] / "work/claude/input/a7s-av-cam.bin").read_bytes()
assert hashlib.sha256(BLOB).hexdigest().startswith("b857d338")


def w(va: int) -> int:
    return struct.unpack_from("<I", BLOB, va - BASE)[0]


def at(va: int, n: int) -> bytes:
    return BLOB[va - BASE : va - BASE + n]


def pcrel(lit: int, add_pc: int) -> int:
    """`ldr rX,[pc,#lit]; add rX,pc` en Thumb: valor literal + dirección del add + 4."""
    return w(lit) + add_pc + 4


# 1. Política: str r1,[r2,#0x5c] con r2 = G
assert pcrel(0x43864BD8, 0x43864A44) == 0x43F06BC8
# 2. 0x4386347a lee la copia de clase 0x43f04c8c y la escribe en r8+0x69
assert pcrel(0x438636F4, 0x43863478) == 0x43F04C8C
assert at(0x4386347C, 4) == bytes.fromhex("88f86930")  # strb.w r3,[r8,#0x69]
# 3. 0x43861f58 devuelve uno de dos buffers estáticos vía GOT
r4 = pcrel(0x43861F78, 0x43861F5E)
assert {w(r4 + w(0x43861F7C)), w(r4 + w(0x43861F80))} == {0x43EB7F0C, 0x43F0552C}
# 4. Ambos sitios la llaman con (cap+0x1c0, cap+0x1b8): ldr.w r1,[rX,#0x1b8]; ldr.w r0,[rX,#0x1c0]; bl 0x43861f58
assert at(0x438633F0, 8) == bytes.fromhex("d6f8b811d6f8c001")  # r6 = captura
assert at(0x43862184, 8) == bytes.fromhex("d4f8b811d4f8c001")  # r4 = captura
print("s52 coordinador: 4/4 OK")
