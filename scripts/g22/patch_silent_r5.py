"""E26-R86 — calibración del obturador electrónico (Silent) en la imagen BIONZ: ShutMode 0 + `r5` desde la velocidad, solo en foto.

Lleva a `av-cam` el parche de RAM medido en R56 §7 (RemoteShutter v8c / `camera_silent.py`). R56 ajustó `r5 = 4219 − (T/16,73 µs − 97)` con T
NOMINAL de la app (1/60 = 16 667 µs); aquí T sale del Tv (1/60 = 2^-6 s = 15 625 µs), así que se reajusta a los mismos puntos medidos
(1/60 → 3320, 1/250 → 4077): `r5 = 4219 − (T/15,48 µs − 110)` (1/15 → 292 frente a 331 de R56: +1 % de exposición).
Enganche (el de C3-B de E25-26): `0x438c82fe bl 0x436d6118` de la secuencia de foto `0x438c828c`, paso 0, justo antes de
`SetExposure` (`0x438c830c`, `r1 = cap+0x64c`). La cueva:
  * llama a `0x436d6118` como el original y devuelve su r0;
  * solo actúa con Silent activado: byte vivo `0x43EDF684+0x238` (el mismo que usa el envío a Darwin). R87 (medido en RAM):
    `cap+0x41d` vale 0 en el objeto de esta secuencia (`r4` ≠ objeto del copiador de `patch_tristate`), así que la versión del 3.76 nunca actuaba;
  * Tv = `ajustes+0x162` (ajustes = `0x4383fbc4([cap+0x1e0], [cap+0x1d8])`, el mismo par que `0x4383fd6c` con r6 = cap+0x20);
  * solo 1/16 s … 1/16000 (`0x1400 <= Tv <= 0x1e00`); `q8 = 0x4382fa94(Tv)` (µs·256);
  * `líneas = q8·K >> 32` (K = 2^32/(17,135·256)), `r5 = 4252 − líneas` (R87; el ajuste R56 de 3.35 dejaba 1/250 en 0,73 y 1/500 en 0,40); si `r5 < 10` (no cabe en un cuadro) no toca nada;
    `r5 <= 4218` (por encima de ~1/600 el modelo da ≤ 0 líneas: 1 línea, NO medido);
  * escribe `cap+0x64c` (u16, `param+0` = r5 de SetExposure) y `cap+0x655 = 0` (`param+9` = ShutMode).
Cueva en el hueco de G18 tras el código de `pp_tone_patch` y antes de su búfer `W` (`0x43FB7EC0`).
"""
from __future__ import annotations

import struct

from e25_24 import patch_bionz as PB
from e25_24.thumb import bl

BASE = PB.BASE
HOOK, HOOK_OLD, IMAGER = 0x438C82FE, bytes.fromhex("0df60bff"), 0x436D6118
SETTINGS, TV2US = 0x4383FBC4, 0x4382FA94
LIVE_SILENT = 0x43EDF684 + 0x238           # ajuste Silent vivo (patch_tristate.LIVE_BASE + 0x238)
CAVE, CAVE_END = 0x43FB7E00, 0x43FB7EC0      # W de pp_tone_patch empieza en 0x43FB7EC0
LINE_US, R5_LAG, R5_FULL, R5_MIN = 17.135, 33, 4219, 10   # R87: E = 17,135 µs·n + 564 µs medido en cámara (7 velocidades, 1/2000…1/50)
K = round(2**32 / (LINE_US * 256))
TV_MIN, TV_MAX = 0x1400, 0x1E00


def cave_bytes() -> bytes:
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    asm = f"""
        push {{r3, r4, r5, r6, r7, lr}}
        mov r5, r4
        bl {IMAGER:#x}
        mov r6, r0
        movw r3, #{LIVE_SILENT & 0xFFFF:#x}
        movt r3, #{LIVE_SILENT >> 16:#x}
        ldrb r3, [r3]
        cmp r3, #1
        bne done
        ldr.w r0, [r5, #0x1e0]
        ldr.w r1, [r5, #0x1d8]
        bl {SETTINGS:#x}
        ldrh.w r0, [r0, #0x162]
        movw r3, #{TV_MIN:#x}
        cmp r0, r3
        blo done
        movw r3, #{TV_MAX:#x}
        cmp r0, r3
        bhi done
        bl {TV2US:#x}
        movw r3, #{K & 0xFFFF:#x}
        movt r3, #{K >> 16:#x}
        umull r1, r2, r0, r3
        movw r3, #{R5_FULL + R5_LAG}
        subs r3, r3, r2
        cmp r3, #{R5_MIN}
        blt done
        movw r2, #{R5_FULL - 1}
        cmp r3, r2
        it gt
        movgt r3, r2
        strh.w r3, [r5, #0x64c]
        movs r3, #0
        strb.w r3, [r5, #0x655]
    done:
        mov r0, r6
        pop {{r3, r4, r5, r6, r7, pc}}
    """
    enc, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(asm, CAVE)
    code = bytes(enc)
    assert len(code) <= CAVE_END - CAVE, len(code)
    return code


def apply_bytes(data: bytes) -> bytes:
    if len(data) != PB.SIZE:
        raise PB.ImageError("tamaño inesperado")
    h = HOOK - BASE
    if data[h:h + 4] != HOOK_OLD:
        raise PB.ImageError("enganche 0x438c82fe distinto del original")
    if any(data[CAVE - BASE:CAVE_END - BASE]):
        raise PB.ImageError("la cueva 0x43FB7E00 no está a cero")
    if data[0x43841472 - BASE:0x43841476 - BASE] != bytes.fromhex("99f81d34"):
        raise PB.ImageError("falta el parche de tres estados (cap+0x41d)")
    out = bytearray(data)
    code = cave_bytes()
    out[CAVE - BASE:CAVE - BASE + len(code)] = code
    out[h:h + 4] = bl(HOOK, CAVE)
    return bytes(out)


def r5_esperado(tv: int, q8: int) -> int | None:
    if not TV_MIN <= tv <= TV_MAX:
        return None
    r5 = R5_FULL + R5_LAG - ((q8 * K) >> 32)
    return None if r5 < R5_MIN else min(r5, R5_FULL - 1)


def emular(img: bytes, tv: int, silent: int = 1) -> tuple[int, int, int]:
    """Ejecuta el enganche con Unicorn sobre la imagen parcheada: devuelve (r0, cap+0x64c, cap+0x655)."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_R4,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    lo, size = BASE & ~0xFFF, ((len(img) + (BASE & 0xFFF)) + 0x200000) & ~0xFFF
    mu.mem_map(lo, size)
    mu.mem_write(BASE, img)
    mu.mem_write(IMAGER, bytes.fromhex("41f23420") + bytes.fromhex("7047"))    # stub: movw r0,#0x1234; bx lr
    stack, cap, end = 0x10000000, 0x20000000, 0x30000000
    mu.mem_map(stack - 0x10000, 0x20000)
    mu.mem_map(cap, 0x10000)
    mu.mem_map(end, 0x1000)
    mu.mem_write(LIVE_SILENT, bytes([silent]))
    mu.mem_write(cap + 0x64C, struct.pack("<H", 1))
    mu.mem_write(cap + 0x655, b"\x03")
    mu.mem_write(cap + 0x1E0, struct.pack("<I", 0))
    mu.mem_write(cap + 0x1D8, struct.pack("<I", 0))
    # ajustes: se resuelve con el propio accesor y se escribe el Tv
    mu.reg_write(UC_ARM_REG_SP, stack)
    mu.reg_write(UC_ARM_REG_R0, 0)
    mu.reg_write(UC_ARM_REG_LR, end | 1)
    mu.emu_start(SETTINGS | 1, end, count=200)
    sett = mu.reg_read(UC_ARM_REG_R0)
    mu.mem_write(sett + 0x162, struct.pack("<H", tv))
    mu.reg_write(UC_ARM_REG_SP, stack)
    mu.reg_write(UC_ARM_REG_R4, cap)
    mu.reg_write(UC_ARM_REG_LR, end | 1)
    mu.emu_start(HOOK | 1, HOOK + 4, count=100000)
    assert mu.reg_read(UC_ARM_REG_PC) == HOOK + 4
    return (mu.reg_read(UC_ARM_REG_R0), struct.unpack("<H", mu.mem_read(cap + 0x64C, 2))[0], mu.mem_read(cap + 0x655, 1)[0])
