#!/usr/bin/env python3
"""E25-11: emula con Unicorn las funciones de av-cam (fw 3.21) que convierten el código de velocidad (Tv) en tiempo.

`0x4382fac8(x)` devuelve µs y `0x4382fa94(x)` el mismo tiempo en 1/256 µs (−1 si x ≤ 0xC00); x = 0x1000 + 256·log2(1/t).
Uso: e25_11_tv_emu.py [x ...] (hex o decimal); sin argumentos, una tabla de referencia. Solo lectura del firmware, sin cámara."""
import sys
from pathlib import Path

from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, UC_PROT_ALL, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP

FW = Path(__file__).resolve().parents[1] / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE, SENT = 0x43541000, 0x20000000


def emulator() -> Uc:
    data = FW.read_bytes()
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE, ((len(data) + 0xFFF) & ~0xFFF) + 0x100000, UC_PROT_ALL)
    mu.mem_write(BASE, data)
    mu.mem_map(0x10000000, 0x100000, UC_PROT_ALL)
    mu.mem_map(SENT, 0x1000, UC_PROT_ALL)
    mu.mem_write(SENT, b"\x00\xbe")  # bkpt: fin de la llamada
    return mu


def call(mu: Uc, addr: int, r0: int) -> int:
    mu.reg_write(UC_ARM_REG_R0, r0)
    mu.reg_write(UC_ARM_REG_SP, 0x100F0000)
    mu.reg_write(UC_ARM_REG_LR, SENT | 1)
    mu.emu_start(addr | 1, SENT, count=20000)
    return mu.reg_read(UC_ARM_REG_R0)


if __name__ == "__main__":
    mu = emulator()
    xs = [int(a, 0) for a in sys.argv[1:]] or [0xC00, 0xC01, 0xE00, 0x1000, 0x1200, 0x1400, 0x1800, 0x17F6, 0x2000]
    for x in xs:
        print(f"x={x:#06x}  µs={call(mu, 0x4382FAC8, x)}  1/256µs={call(mu, 0x4382FA94, x)}  fórmula µs={1e6 * 2 ** ((4096 - x) / 256):.1f}")
