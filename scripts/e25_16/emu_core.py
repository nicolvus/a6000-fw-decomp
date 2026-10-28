#!/usr/bin/env python3
"""E25-16 — arnés de emulación Unicorn para `av-cam.bin` (A6000 fw 3.21).

Sólo se emula software: no se conecta la cámara ni se escribe fuera de la
memoria del emulador. Los stubs sustituyen funciones externas (logs, colas,
getters de estado) por valores fijos y se documentan uno a uno.
"""
from __future__ import annotations

import hashlib
import struct
from pathlib import Path

from unicorn import (
    UC_ARCH_ARM,
    UC_HOOK_CODE,
    UC_HOOK_MEM_READ,
    UC_HOOK_MEM_WRITE,
    UC_MODE_THUMB,
    UC_PROT_ALL,
    Uc,
    UcError,
)
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_SP,
)

ROOT = Path(__file__).resolve().parents[2]
FW = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE = 0x43541000
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"

CODE = 0x20000000
STACK = 0x10000000
SCRATCH = 0x30000000
CFG = 0x30040000
SENT = 0x40000000

# stubs: dirección -> (tipo, valor).  "ret" = devuelve valor en r0;
# "ptr" = devuelve un puntero a SCRATCH+valor.
STUBS = {
    0x438FB300: ("ret", 0),   # getter de estado: 0 fuerza la rama "normal" de 0x4385de94
    0x43B08D42: ("ret", 0),   # selector de banco A/B: 0 -> banco A
    0x43A12CA8: ("ret", 0),   # predicado de cuadro extra en 0x4383fa40: 0 -> sin extra
    0x4355FD4C: ("ret", 0),   # módulo/resto auxiliar
    0x439C5A04: ("ret", 0),   # memset: no se emula (destino fuera de lo comparado)
    0x439C5320: ("ret", 0),   # memcpy
    0x439C53B4: ("ret", 0),   # memcpy variante (SetRead)
    0x439C54C8: ("ret", 0),   # memset variante
    0x436D9F70: ("ret", 0),
    0x436D6738: ("ret", 0),
    0x43901A8C: ("ret", 0),
    0x436D6450: ("ret", 0),
    0x436D6020: ("ret", 0),
    0x436D60E4: ("ret", 0),
}


def thumb_stub_ret(value: int) -> bytes:
    return struct.pack("<HH", 0x2000 | (value & 0xFF), 0x4770)


class Emu:
    def __init__(self, fw: Path = FW):
        data = fw.read_bytes()
        h = hashlib.sha256(data).hexdigest()
        if h != SHA:
            raise RuntimeError(f"SHA-256 inesperado: {h}")
        self.mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        size = ((len(data) + 0xFFF) & ~0xFFF) + 0x200000
        self.mu.mem_map(BASE, size, UC_PROT_ALL)
        self.mu.mem_write(BASE, data)
        self.mu.mem_map(STACK, 0x40000, UC_PROT_ALL)
        self.mu.mem_map(CODE, 0x10000, UC_PROT_ALL)
        self.mu.mem_map(SCRATCH, 0x10000, UC_PROT_ALL)
        self.mu.mem_map(CFG, 0x10000, UC_PROT_ALL)
        self.mu.mem_map(SENT, 0x1000, UC_PROT_ALL)
        self.mu.mem_write(SENT, b"\x00\xbe")
        self.writes: list[tuple[int, int, int]] = []
        self.reads: list[tuple[int, int, int]] = []
        self.mu.hook_add(UC_HOOK_MEM_WRITE, self._on_write)
        self.mu.hook_add(UC_HOOK_MEM_READ, self._on_read)
        self.mu.hook_add(UC_HOOK_CODE, self._on_arm_helper)
        self._patch_stubs()

    def _on_arm_helper(self, uc, address, size, user_data):
        """`memcpy` compilado en ARM: se ejecuta en Python y se retorna."""
        if address != 0x439C53A8:
            return
        dst = uc.reg_read(UC_ARM_REG_R0)
        src = uc.reg_read(UC_ARM_REG_R1)
        n = uc.reg_read(UC_ARM_REG_R2)
        if n and 0 <= n <= 0x1000:
            try:
                uc.mem_write(dst, bytes(uc.mem_read(src, n)))
            except UcError:
                pass
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) & ~1)

    def _patch_stubs(self):
        slot = CODE
        for addr, (kind, val) in STUBS.items():
            if kind == "ret":
                self.mu.mem_write(addr, thumb_stub_ret(val))
            else:
                code = struct.pack("<HH", 0x4800, 0x4770)  # ldr r0,[pc,#0]; bx lr
                self.mu.mem_write(addr, code + struct.pack("<I", val))
            slot += 8

    def _on_write(self, uc, access, address, size, value, user_data):
        if BASE <= address < BASE + 0x1000000:
            return
        self.writes.append((address, size, value))

    def _on_read(self, uc, access, address, size, value, user_data):
        if BASE <= address < BASE + 0x1000000:
            return
        self.reads.append((address, size, value))

    def call(self, addr: int, *args, timeout: int = 400000, sent: int = SENT) -> int:
        mu = self.mu
        for reg, val in zip(
            (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), args
        ):
            mu.reg_write(reg, val & 0xFFFFFFFF)
        mu.reg_write(UC_ARM_REG_SP, STACK + 0x30000)
        mu.reg_write(UC_ARM_REG_LR, sent | 1)
        self.writes = []
        self.reads = []
        mu.emu_start(addr | 1, sent, count=timeout)
        return mu.reg_read(UC_ARM_REG_R0)

    def read(self, addr: int, n: int) -> bytes:
        return bytes(self.mu.mem_read(addr, n))

    def w16(self, addr: int) -> int:
        return struct.unpack("<H", self.read(addr, 2))[0]

    def w32(self, addr: int) -> int:
        return struct.unpack("<I", self.read(addr, 4))[0]
