"""Cargador mínimo de ELF32/ARM para emular con unicorn el código real de las `.so` de la cámara.

Mapea los PT_LOAD, aplica las relocaciones (ABS32/GLOB_DAT/JUMP_SLOT/RELATIVE) y reapunta los símbolos no definidos a
«stubs» en una región propia; cada stub ejecuta un manejador Python (modelo del símbolo importado) y vuelve a `lr`.
"""

from __future__ import annotations

import struct
import subprocess
from collections.abc import Callable
from contextlib import suppress

from unicorn import (
    UC_ARCH_ARM,
    UC_HOOK_CODE,
    UC_HOOK_MEM_UNMAPPED,
    UC_MODE_THUMB,
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

PAGE = 0x1000
STUB_BASE, STACK_TOP, STACK_SIZE, HEAP_BASE = (
    0x7F000000,
    0x7E100000,
    0x100000,
    0x60000000,
)
R = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)


def _demangle(names: list[str]) -> list[str]:
    out = subprocess.run(
        ["c++filt"], input="\n".join(names), capture_output=True, text=True, check=True
    ).stdout.split("\n")
    return out[: len(names)]


class Machine:
    """Un `Uc` ARM/Thumb con pila, montón y stubs; admite varias librerías."""

    def __init__(self) -> None:
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        self.uc.mem_map(STACK_TOP - STACK_SIZE, STACK_SIZE)
        self.heap = HEAP_BASE
        self.uc.mem_map(HEAP_BASE, 0x400000)
        self.uc.mem_map(STUB_BASE, 0x10000)
        self.stubs: dict[int, str] = {}
        self.handlers: dict[str, Callable[[Machine], int | None]] = {}
        self.default_calls: list[str] = []
        self.overrides: dict[int, Callable[[Machine], int | None]] = {}
        self._nstub = 0
        self.uc.hook_add(UC_HOOK_CODE, self._code)
        self.uc.hook_add(UC_HOOK_MEM_UNMAPPED, self._unmapped)
        self.automap = False

    def _unmapped(self, uc, access, addr, size, value, _):
        if not self.automap:
            return False
        uc.mem_map(addr & ~(PAGE - 1), PAGE)
        return True

    def stub(self, name: str) -> int:
        for a, n in self.stubs.items():
            if n == name:
                return a | 1
        a = STUB_BASE + 4 * self._nstub
        self._nstub += 1
        self.stubs[a] = name
        return a | 1

    def _code(self, uc, addr, size, _):
        h = None
        if addr in self.overrides:
            h = self.overrides[addr]
        elif addr in self.stubs:
            name = self.stubs[addr]
            h = self.handlers.get(name)
            if h is None:
                self.default_calls.append(name)
                h = lambda m: 0
        if h is None:
            return
        r = h(self)
        if r is not None:
            uc.reg_write(UC_ARM_REG_R0, r & 0xFFFFFFFF)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    # --- utilidades de memoria / registros
    def reg(self, i: int) -> int:
        return self.uc.reg_read(R[i])

    def u32(self, a: int) -> int:
        return struct.unpack("<I", self.uc.mem_read(a, 4))[0]

    def w32(self, a: int, v: int) -> None:
        self.uc.mem_write(a, struct.pack("<I", v & 0xFFFFFFFF))

    def cstr(self, a: int) -> str:
        out = b""
        while (c := bytes(self.uc.mem_read(a, 1))) != b"\0":
            out += c
            a += 1
        return out.decode("latin-1")

    def alloc(self, n: int) -> int:
        a = self.heap
        self.heap += (n + 15) & ~15
        return a

    def call(
        self, fn: int, *args: int, stop: int = 0x7FFF0000, count: int = 3_000_000
    ) -> int:
        """Llama a `fn` (dirección Thumb con bit 0) y devuelve r0."""
        uc = self.uc
        with suppress(UcError):
            uc.mem_map(stop & ~(PAGE - 1), PAGE)
        sp = STACK_TOP - 0x100
        regs = list(args[:4])
        extra = args[4:]
        sp -= 4 * len(extra)
        sp &= ~7
        for i, v in enumerate(extra):
            self.w32(sp + 4 * i, v)
        for i, v in enumerate(regs):
            uc.reg_write(R[i], v & 0xFFFFFFFF)
        uc.reg_write(UC_ARM_REG_SP, sp)
        uc.reg_write(UC_ARM_REG_LR, stop | 1)
        uc.emu_start(fn | 1, stop, count=count)
        return uc.reg_read(UC_ARM_REG_R0)


class Lib:
    def __init__(self, m: Machine, data: bytes, base: int) -> None:
        self.m, self.base, d = m, base, data
        (phoff,) = struct.unpack_from("<I", d, 0x1C)
        phentsize, phnum = struct.unpack_from("<HH", d, 0x2A)
        dyn: tuple[int, int] = (0, 0)
        for i in range(phnum):
            t, off, va, _pa, fsz, msz, _fl, _al = struct.unpack_from(
                "<8I", d, phoff + i * phentsize
            )
            if t == 1:
                lo, hi = (
                    (base + va) & ~(PAGE - 1),
                    (base + va + msz + PAGE - 1) & ~(PAGE - 1),
                )
                for p in range(lo, hi, PAGE):
                    with suppress(UcError):
                        m.uc.mem_map(p, PAGE)
                m.uc.mem_write(base + va, d[off : off + fsz])
            elif t == 2:
                dyn = (off, fsz)
        tags: dict[int, int] = {}
        for i in range(0, dyn[1], 8):
            tg, v = struct.unpack_from("<II", d, dyn[0] + i)
            if tg == 0:
                break
            tags[tg] = v
        rd = lambda va, n: bytes(m.uc.mem_read(base + va, n))
        strtab, symtab = tags[5], tags[6]
        nsym = (tags[5] - tags[6]) // 16 if tags[5] > tags[6] else 0
        self.syms: list[tuple[str, int, int]] = []
        raw_syms = [
            struct.unpack_from("<IIIBBH", rd(symtab + 16 * i, 16)) for i in range(nsym)
        ]
        names = []
        for nm, *_ in raw_syms:
            s = rd(strtab + nm, 256)
            names.append(s.split(b"\0")[0].decode("latin-1"))
        dem = _demangle(names)
        self.by_name: dict[str, int] = {}
        self.plain: dict[str, int] = {}
        self.sym_addr: list[int | None] = []
        for (nm, val, sz, info, oth, shndx), n, dn in zip(raw_syms, names, dem):
            if shndx != 0 and n:
                self.by_name[dn] = base + val
                self.plain[n] = base + val
                self.sym_addr.append(base + val)
            else:
                self.sym_addr.append(None)
        self.dem = dem
        for rel_t, rel_s in ((tags.get(17), tags.get(18)), (tags.get(23), tags.get(2))):
            if not rel_t or not rel_s:
                continue
            for i in range(0, rel_s, 8):
                off, info = struct.unpack_from("<II", rd(rel_t + i, 8))
                typ, si = info & 0xFF, info >> 8
                where = base + off
                if typ == 23:  # RELATIVE
                    m.w32(where, m.u32(where) + base)
                elif typ in (2, 21, 22):
                    tgt = self.sym_addr[si]
                    if tgt is None:
                        tgt = m.stub(dem[si])
                    add = m.u32(where) if typ == 2 else 0
                    m.w32(where, tgt + add)
        self.dyn_tags = tags
