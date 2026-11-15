"""LUT 3D del BIONZ X: ejecuta el generador `Create3DLUT` (`av-cam` 0x437a1d7e) en Unicorn con una tabla de referencia conocida (g71)."""
from __future__ import annotations

import struct
from pathlib import Path

from unicorn import (
    UC_ARCH_ARM,
    UC_HOOK_MEM_READ_UNMAPPED,
    UC_HOOK_MEM_WRITE_UNMAPPED,
    UC_MODE_THUMB,
    Uc,
)
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE, ENTRY, PERM = 0x43541000, 0x437A1D7E, 0x43BEF2AC
N = 405
CTX, PKT, CFG, HW, REF, STK, END = 0x10000000, 0x10001000, 0x10002000, 0x10010000, 0x10020000, 0x10040000, 0x10050000


def perm(img: bytes) -> list[int]:
    return list(struct.unpack_from("<405H", img, PERM - BASE))


def generar(ref: bytes | None, pkt: dict[int, int] | None = None, cfg: dict[int, int] | None = None, trace=False) -> bytes:
    """Devuelve los 0x654 B que `Create3DLUT` deja en el búfer del hardware (modo 0). `ref` = 3×405 s8 (planos 0, 0x195, 0x32a)."""
    img = BIN.read_bytes()
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE & ~0xFFF, (len(img) + 0x200FFF) & ~0xFFF)
    mu.mem_write(BASE, img)
    for a, s in ((CTX, 0x1000), (PKT, 0x1000), (CFG, 0x1000), (HW, 0x10000), (REF, 0x10000), (STK, 0x10000), (END, 0x1000)):
        mu.mem_map(a, s)
    mu.mem_write(CTX, struct.pack("<III I", PKT, 0, CFG, HW))
    for k, v in (pkt or {}).items():
        mu.mem_write(PKT + k, bytes([v & 0xFF]))
    base_cfg = {0xD8: 1, 0xD9: 0, 2: 0}    # d8 = modo de lectura de la referencia (1 = directa), d9 = ConvSD (0 = sin conversión SD→HD)
    base_cfg.update(cfg or {})
    for k, v in base_cfg.items():
        mu.mem_write(CFG + k, bytes([v & 0xFF]))
    mu.mem_write(CFG + 0xD4, struct.pack("<I", REF if ref else 0))
    if ref:
        mu.mem_write(REF, ref)
    def fallo(uc, acc, addr, size, val, ud):  # globales del firmware fuera de la imagen: página a cero
        uc.mem_map(addr & ~0xFFF, 0x1000)
        fallos.append(addr)
        return True

    fallos: list[int] = []
    mu.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED, fallo)
    mu.reg_write(UC_ARM_REG_R0, CTX)
    mu.reg_write(UC_ARM_REG_SP, STK + 0x8000)
    mu.reg_write(UC_ARM_REG_LR, END | 1)
    mu.emu_start(ENTRY | 1, END, count=20_000_000)
    return bytes(mu.mem_read(HW + 0x8C8, 0x654))


def decodificar(buf: bytes, p: list[int]) -> list[tuple[int, int, int]]:
    """Vuelve del orden del hardware al orden lógico j*81+a*9+b: (c0,c1,c2) con signo de 7 bit."""
    sg = lambda v: v - 128 if v & 64 else v
    out = []
    for i in range(N):
        w = struct.unpack_from("<I", buf, 4 * p[i])[0]
        out.append((sg(w >> 16 & 0x7F), sg(w >> 8 & 0x7F), sg(w & 0x7F)))
    return out


if __name__ == "__main__":
    img = BIN.read_bytes()
    p = perm(img)
    ref = bytes(N * 3)
    b = generar(ref)
    d = decodificar(b, p)
    print(sum(1 for t in d if t != (0, 0, 0)), "nodos no nulos de", N)
