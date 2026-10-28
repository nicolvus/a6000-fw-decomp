#!/usr/bin/env python3
"""E25-19f — arnés Unicorn común: av-cam.bin (fw 3.21, base 0x43541000) + RAM de datos con páginas a demanda.

Código real; las dependencias de periférico/log se sustituyen por `stubs` (dirección → valor de r0) documentados por llamada.
Cada lectura de datos (fuera de código/pila) se registra en `lecturas` para saber qué estado de cámara hace falta.
"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from unicorn import (
    UC_ARCH_ARM,
    UC_HOOK_CODE,
    UC_HOOK_MEM_READ,
    UC_HOOK_MEM_READ_UNMAPPED,
    UC_HOOK_MEM_WRITE,
    UC_HOOK_MEM_WRITE_UNMAPPED,
    UC_MODE_THUMB,
    UC_PROT_ALL,
    Uc,
)
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000
SENT = 0x20000000
STACK_TOP = 0x30100000
PAGE = 0x1000
VFP_ON = 0x40000000


class Emu:
    def __init__(self, ram: dict[int, bytes] | None = None):
        self.data = BIN.read_bytes()
        self.end = BASE + len(self.data)
        self.mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        mu = self.mu
        mu.mem_map(BASE, ((len(self.data) + 0xFFF) & ~0xFFF) + 0x200000, UC_PROT_ALL)
        mu.mem_write(BASE, self.data)
        mu.mem_map(SENT, PAGE, UC_PROT_ALL)
        mu.mem_write(SENT, b"\x00\xbe")
        mu.mem_map(STACK_TOP - 0x100000, 0x100000, UC_PROT_ALL)
        for a, b in (ram or {}).items():  # instantánea física: sobrescribe la imagen
            self._map(a, len(b))
            mu.mem_write(a, b)
        # CPACR/FPEXC: habilita VFP
        mu.reg_write(UC_ARM_REG_R0, 0)
        try:
            from unicorn.arm_const import UC_ARM_REG_C1_C0_2, UC_ARM_REG_FPEXC

            mu.reg_write(UC_ARM_REG_C1_C0_2, 0xF00000)
            mu.reg_write(UC_ARM_REG_FPEXC, VFP_ON)
        except ImportError:  # pragma: no cover
            pass
        # llamada indirecta nula (objeto de periférico/log ausente de la instantánea): `bx lr` en ARM y Thumb, contada en `nulas`
        self._map(0, 8)
        mu.mem_write(0, b"\x1e\xff\x2f\xe1")
        self.nulas = 0
        self.stubs: dict[int, int | Callable[[Emu], int]] = {}
        self.lecturas: dict[int, int] = {}
        self.escrituras: list[tuple[int, int, int]] = []
        self.llamadas: list[tuple[int, int, int, int, int]] = []
        self.pcs: list[int] = []
        self.hooks_pc: dict[int, Callable[[Emu, int], object]] = {}
        self.trazar = False
        self.auto: list[int] = []
        mu.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED, self._unmapped)
        mu.hook_add(UC_HOOK_MEM_READ, self._read)
        mu.hook_add(UC_HOOK_MEM_WRITE, self._write)
        mu.hook_add(UC_HOOK_CODE, self._code)

    def _map(self, a: int, n: int) -> None:
        lo, hi = a & ~(PAGE - 1), (a + n + PAGE - 1) & ~(PAGE - 1)
        p = lo
        while p < hi:
            try:
                self.mu.mem_map(p, PAGE, UC_PROT_ALL)
            except Exception:  # noqa: BLE001, S110 - ya mapeada
                pass
            p += PAGE

    def _unmapped(self, mu, _acc, addr, size, _val, _ud) -> bool:
        self.auto.append(addr)
        self._map(addr, size)
        return True

    def _read(self, mu, _acc, addr, size, _val, _ud) -> None:
        if not (STACK_TOP - 0x100000 <= addr < STACK_TOP):
            self.lecturas[addr] = self.lecturas.get(addr, 0) + 1

    def _write(self, mu, _acc, addr, size, val, _ud) -> None:
        if not (STACK_TOP - 0x100000 <= addr < STACK_TOP):
            self.escrituras.append((addr, size, val & 0xFFFFFFFF))

    def _code(self, mu, addr, size, _ud) -> None:
        a = addr & ~1
        if a == 0:
            self.nulas += 1
        if self.trazar:
            self.pcs.append(a)
        if (h := self.hooks_pc.get(a)) is not None:
            h(self, a)
        if a in self.stubs:
            v = self.stubs[a]
            r0 = v(self) if callable(v) else v
            self.llamadas.append((a, *(mu.reg_read(UC_ARM_REG_R0 + i) for i in range(4))))
            mu.reg_write(UC_ARM_REG_R0, r0 & 0xFFFFFFFF)
            mu.reg_write(UC_ARM_REG_PC, mu.reg_read(UC_ARM_REG_LR) & ~1 | 1)

    def r32(self, a: int) -> int:
        return int.from_bytes(self.mu.mem_read(a, 4), "little")

    def w32(self, a: int, v: int) -> None:
        self._map(a, 4)
        self.mu.mem_write(a, (v & 0xFFFFFFFF).to_bytes(4, "little"))

    def wr(self, a: int, b: bytes) -> None:
        self._map(a, len(b))
        self.mu.mem_write(a, b)

    def call(self, addr: int, *args: int, sp: int = STACK_TOP - 0x1000, count: int = 3_000_000, stop: int | None = None) -> int:
        mu = self.mu
        for i, v in enumerate(args[:4]):
            mu.reg_write(UC_ARM_REG_R0 + i, v & 0xFFFFFFFF)
        for i, v in enumerate(args[4:]):  # argumentos de pila
            mu.mem_write(sp + 4 * i, (v & 0xFFFFFFFF).to_bytes(4, "little"))
        mu.reg_write(UC_ARM_REG_SP, sp)
        mu.reg_write(UC_ARM_REG_LR, SENT | 1)
        mu.emu_start(addr | 1, SENT if stop is None else stop, count=count)
        return mu.reg_read(UC_ARM_REG_R0)
