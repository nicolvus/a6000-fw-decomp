"""G55 — Bulb Timer (fase 1): el temporizador por tramos del host (`0x438c74b0`) acaba solo cuando el objetivo T = 0 (BULB) se sustituye
por una celda propia en segundos (0 = desactivado = fábrica). Solo bytes del `av-cam` del `.dat`; sin construir CFW.

Enganche: `0x438c74f6 ldrh.w r0,[r3,#0x66]` (T = [ajustes+0x66], 0 en BULB) -> `bl cueva`. La cueva devuelve T si ≠ 0; si no, `celda·1000` (ms, I).
`S2` soltado sigue cortando por la misma rama (`0x8000`, E25-17 §2.2): el fin es «S2 soltado O T alcanzado».
Cueva+celda en el hueco cero `0x43541900` (0x435418e4..0x43541b00; la cueva de 0x43541800/20 es de otro parche).
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from e25_24.thumb import bl  # noqa: E402

BASE = 0x43541000
HOOK, HOOK_OLD = 0x438C74F6, bytes.fromhex("b3f86600")      # ldrh.w r0,[r3,#0x66]; sigue `b 0x438c7512`
CAVE, CELL, CAVE_END = 0x43541900, 0x43541920, 0x43541930   # CELL: u16 segundos (0 = off)
FUNC = 0x438C74B0
SRC = ROOT / "analysis/rea-independent/input/av-cam.bin"


def cave_bytes() -> bytes:
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    asm = f"""
        ldrh.w r0, [r3, #0x66]
        cbnz r0, done
        movw r1, #{CELL & 0xFFFF:#x}
        movt r1, #{CELL >> 16:#x}
        ldrh r1, [r1]
        mov.w r2, #1000
        mul r0, r1, r2
    done:
        bx lr
    """
    enc, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(asm, CAVE)
    code = bytes(enc)
    assert len(code) <= CELL - CAVE, len(code)
    return code


def apply_bytes(data: bytes) -> bytes:
    h = HOOK - BASE
    if data[h:h + 4] != HOOK_OLD:
        raise ValueError("enganche 0x438c74f6 distinto del original")
    if any(data[CAVE - BASE:CAVE_END - BASE]):
        raise ValueError("la cueva 0x43541900 no está a cero")
    out = bytearray(data)
    code = cave_bytes()
    out[CAVE - BASE:CAVE - BASE + len(code)] = code
    out[h:h + 4] = bl(HOOK, CAVE)
    return bytes(out)


def emular(img: bytes, seg: int, t_cfg: int = 0, periodo: int = 33, max_tramos: int = 3000):
    """Repite `0x438c74b0` como el flujo real (bulbFrameCount++ por tramo). Devuelve (tramos completos, ticks del tramo final) o (max, None) si no acaba."""
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R5, UC_ARM_REG_SP
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE & ~0xFFF, ((len(img) + 0x1000) + 0x200000) & ~0xFFF)
    mu.mem_write(BASE, img)
    stack, cap, end = 0x10000000, 0x20000000, 0x30000000
    mu.mem_map(stack - 0x10000, 0x20000)
    mu.mem_map(cap, 0x10000)
    mu.mem_map(end, 0x1000)
    mu.mem_write(CELL, struct.pack("<H", seg))
    mu.mem_write(0x43E95950 + 0x66, struct.pack("<H", t_cfg))
    rets = {0x43B1F1C2: 0, 0x436D6118: 0, 0x436D6264: periodo, 0x4355FAF0: 0, 0x43901A8C: 0}
    armado = []

    def code(uc, addr, size, _):
        if addr == 0x43B1F1EC:
            armado.append(uc.reg_read(UC_ARM_REG_R1))
        if addr in rets or addr == 0x43B1F1EC:
            uc.reg_write(UC_ARM_REG_R0, rets.get(addr, 0))
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    mu.hook_add(UC_HOOK_CODE, code, begin=0x43B1F1EC, end=0x43B1F1EC)
    for a in rets:
        mu.hook_add(UC_HOOK_CODE, code, begin=a, end=a)
    for n in range(max_tramos):
        mu.mem_write(cap + 0x72C, struct.pack("<I", n))
        mu.mem_write(cap + 0x4E00 + 0xE0, b"\0")
        mu.reg_write(UC_ARM_REG_SP, stack)
        mu.reg_write(UC_ARM_REG_R0, cap)
        mu.reg_write(UC_ARM_REG_LR, end | 1)
        armado.clear()
        mu.emu_start(FUNC | 1, end, count=100000)
        if mu.mem_read(cap + 0x4E00 + 0xE0, 1)[0]:
            return n, armado[0]
    return max_tramos, None


if __name__ == "__main__":
    orig = SRC.read_bytes()
    img = apply_bytes(orig)
    assert img[HOOK - BASE:HOOK - BASE + 4] != HOOK_OLD and len(img) == len(orig)
    assert emular(img, 0) == (3000, None), "con 0 debe esperar a S2 (sin fin propio)"
    assert emular(orig, 5) == (3000, None), "original: la celda no existe en fábrica"
    n, ticks = emular(img, 5)
    assert (n, ticks) == (151, (5000 - 151 * 33) * 31250), (n, ticks)       # 152 tramos: 151 de 33 ms y el último de 17 ms
    assert emular(img, 5, t_cfg=2000)[0] == 60                              # T de fábrica ≠ 0 manda sobre la celda
    n, ticks = emular(img, 900, max_tramos=30000)
    assert (n, ticks) == (27272, (900000 - 27272 * 33) * 31250), (n, ticks)
    print("OK", n)
