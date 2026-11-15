"""G65 (MULTIEXP-ACC F1) — gancho mínimo en `Stage_EncodeJpeg_MainYC`: contador de llamadas antes de pedir la codificación JPEG del YC principal.

Enganche: `bl 0x438c6d30` en 0x438c6f68 (FUN_43b1aca6, caso 1; r0 = petición, r6 = handle del YC ya revelado, aún sin liberar).
Cueva vacía (solo cuenta) en 0x44018250 (zona a cero del `av-cam`), contador en 0x44018290. Termina con `b 0x438c6d30` (cola): r0/r1/lr intactos.
shortcut: contador en la propia imagen (RAM de código, escritura no comprobada en cámara); sin NEON aún, F2 sustituye el cuerpo.
Solo bytes del `av-cam`; sin construir CFW. `python3 scripts/g65/jpeg_hook_patch.py` = autocomprobación con Unicorn.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts")]
from e25_24.thumb import bl

BASE = 0x43541000
HOOK, HOOK_OLD, TARGET = 0x438C6F68, bytes.fromhex("fff7e2fe"), 0x438C6D30
CAVE, CAVE_END, COUNTER = 0x44018250, 0x44018290, 0x44018290
RET_OK = 0x438C6F6C


def cave_bytes() -> bytes:
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    asm = f"ldr r2, =0x{COUNTER:x}\n ldr r3, [r2]\n adds r3, #1\n str r3, [r2]\n b.w 0x{TARGET:x}"
    enc, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(asm, CAVE)
    code = bytes(enc)
    assert len(code) <= CAVE_END - CAVE, len(code)
    return code


def apply_bytes(data: bytes) -> bytes:
    h = HOOK - BASE
    if data[h:h + 4] != HOOK_OLD:
        raise ValueError("enganche distinto del original")
    if any(data[CAVE - BASE:COUNTER + 4 - BASE]):
        raise ValueError("la cueva no está a cero")
    out = bytearray(data)
    code = cave_bytes()
    out[CAVE - BASE:CAVE - BASE + len(code)] = code
    out[h:h + 4] = bl(HOOK, CAVE)
    return bytes(out)


def emular(img: bytes, veces: int = 3) -> tuple[int, int, int]:
    """Ejecuta el enganche `veces` veces con Unicorn: (r0 devuelto, contador, pc final). El destino se sustituye por `movs r0,#1; bx lr`."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    lo = BASE & ~0xFFF
    mu.mem_map(lo, (len(img) + 0x300000) & ~0xFFF)
    mu.mem_write(BASE, img)
    mu.mem_write(TARGET, bytes.fromhex("0120" "7047"))
    mu.mem_map(0x10000000, 0x10000)
    r0 = pc = 0
    for _ in range(veces):
        mu.reg_write(UC_ARM_REG_SP, 0x10008000)
        mu.reg_write(UC_ARM_REG_R0, 0x1234)
        mu.reg_write(UC_ARM_REG_LR, 0x10000001)
        mu.emu_start(HOOK | 1, RET_OK, count=50)
        r0, pc = mu.reg_read(UC_ARM_REG_R0), mu.reg_read(UC_ARM_REG_PC)
    return r0, struct.unpack("<I", mu.mem_read(COUNTER, 4))[0], pc


if __name__ == "__main__":
    img = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
    new = apply_bytes(img)
    assert sum(a != b for a, b in zip(img, new)) <= 4 + 16 and len(new) == len(img)
    assert emular(img)[1] == 0                      # original: sin contador
    r0, n, pc = emular(new, 3)
    assert (r0, n, pc) == (1, 3, RET_OK), (r0, n, pc)
    print("OK: 3 llamadas, contador =", n)
