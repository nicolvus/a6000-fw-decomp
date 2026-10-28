#!/usr/bin/env python3
"""Utilidades ELF/ARM-Thumb para el subsistema GUI (sin REA, reproducible).

Subcomandos:
    sym    <elf> <regex>              símbolos dinámicos que casan con el regex (dirección + nombre)
    str    <elf> <texto>              offset/vaddr y referencias literales a una cadena
    refs   <elf> <vaddr>              sitios de .text que cargan un literal de 32 bits (pool)
    dis    <elf> <vaddr> [n]          desensambla n instrucciones Thumb desde vaddr
    func   <elf> <regex>              desensambla la función cuyo símbolo casa (primer match)
    xrefs  <elf> <vaddr>              funciones (símbolo contenedor) que referencian vaddr o la llaman
    plt    <elf>                      tabla completa stub .plt -> símbolo importado
    resolve <elf> <vaddr>...          nombre del importado si la dirección es un stub .plt

Este script no ejecuta el binario ni escribe en el firmware: solo lee.
"""
from __future__ import annotations

import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
except ImportError:  # pragma: no cover
    Cs = None


@dataclass
class Section:
    name: str
    addr: int
    offset: int
    size: int
    flags: str


@dataclass
class Symbol:
    addr: int
    size: int
    name: str
    kind: str


class Elf:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.raw = self.path.read_bytes()
        if self.raw[:4] != b"\x7fELF":
            raise ValueError("no es ELF")
        if self.raw[4] != 1:
            raise ValueError("se espera ELF32")
        (self.e_shoff,) = struct.unpack_from("<I", self.raw, 0x20)
        self.e_shentsize, self.e_shnum, self.e_shstrndx = struct.unpack_from("<HHH", self.raw, 0x2E)
        self.sections = self._sections()
        self.symbols = self._symbols()

    def _sections(self) -> list[Section]:
        out = []
        strtab_off = self._section_header(self.e_shstrndx)["offset"]
        for i in range(self.e_shnum):
            sh = self._section_header(i)
            name = self._cstr(strtab_off + sh["name"])
            out.append(Section(name, sh["addr"], sh["offset"], sh["size"], sh["flags"]))
        return out

    def _section_header(self, i: int) -> dict:
        o = self.e_shoff + i * self.e_shentsize
        name, typ, flags, addr, offset, size, link, info, align, entsize = struct.unpack_from(
            "<IIIIIIIIII", self.raw, o
        )
        return {"name": name, "type": typ, "flags": flags, "addr": addr, "offset": offset,
                "size": size, "link": link, "info": info, "align": align, "entsize": entsize}

    def _cstr(self, off: int) -> str:
        end = self.raw.index(b"\x00", off)
        return self.raw[off:end].decode("latin-1")

    def _symbols(self) -> list[Symbol]:
        out = []
        for sh in [s for s in self.sections if s.name in (".dynsym", ".symtab")]:
            idx = next(i for i, s in enumerate(self.sections) if s.name == sh.name)
            hdr = self._section_header(idx)
            strtab = self.sections[hdr["link"]]
            for o in range(sh.offset, sh.offset + sh.size, 16):
                st_name, st_value, st_size, st_info, _other, _shndx = struct.unpack_from(
                    "<IIIBBH", self.raw, o
                )
                if not st_value:
                    continue
                out.append(Symbol(st_value, st_size, self._cstr(strtab.offset + st_name),
                                  "T" if (st_info & 0xF) == 2 else "?"))
        return sorted(out, key=lambda s: s.addr)

    def section_of(self, addr: int) -> Section | None:
        for s in self.sections:
            if s.addr <= addr < s.addr + s.size:
                return s
        return None

    def read_vaddr(self, addr: int, n: int) -> bytes:
        s = self.section_of(addr)
        if not s:
            return b""
        return self.raw[s.offset + (addr - s.addr): s.offset + (addr - s.addr) + n]

    def symbol_at(self, addr: int) -> Symbol | None:
        best = None
        for s in self.symbols:
            if s.addr <= addr and (best is None or s.addr > best.addr):
                best = s
        return best

    def find_string(self, text: str) -> list[int]:
        needle = text.encode()
        out, start = [], 0
        while True:
            i = self.raw.find(needle, start)
            if i < 0:
                return out
            s = self.section_of_offset(i)
            if s:
                out.append(s.addr + (i - s.offset))
            start = i + 1

    def section_of_offset(self, off: int) -> Section | None:
        for s in self.sections:
            if s.offset <= off < s.offset + s.size and s.size:
                return s
        return None

    def find_address_builders(self, target: int) -> list[tuple[int, str]]:
        """Sitios de .text que construyen `target` con movw/movt (Thumb-2) o add pc-relativo.

        Devuelve (dirección, instrucciones) por cada par detectado. La dirección es la
        de la primera instrucción de la secuencia.
        """
        if Cs is None:
            return []
        text = next(s for s in self.sections if s.name == ".text")
        cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        cs.skipdata = True
        code = self.raw[text.offset:text.offset + text.size]
        pending: dict[int, tuple[int, str]] = {}
        out = []
        for ins in cs.disasm(code, text.addr):
            m = ins.mnemonic
            if m == "movw":
                parts = ins.op_str.replace(" ", "").split(",")
                if len(parts) == 2 and parts[1].startswith("#"):
                    val = int(parts[1][1:], 0) & 0xFFFF
                    pending[ins.address] = (val, f"movw {parts[0]},#0x{val:04x}")
            elif m == "movt":
                parts = ins.op_str.replace(" ", "").split(",")
                if len(parts) == 2 and parts[1].startswith("#"):
                    hi = (int(parts[1][1:], 0) & 0xFFFF) << 16
                    for addr, (lo, text0) in list(pending.items()):
                        if addr >= ins.address - 16:
                            full = hi | lo
                            if full == target:
                                out.append((addr, f"{text0} ; movt {parts[0]},#0x{hi >> 16:04x}"))
                            pending.pop(addr, None)
            elif ins.address - 0 not in pending and len(pending) > 64:
                pending.clear()
        return out

    def find_literal_refs(self, vaddr: int) -> list[int]:
        """Posiciones de .text que contienen el literal de 32 bits (little endian)."""
        pat = struct.pack("<I", vaddr)
        text = next(s for s in self.sections if s.name == ".text")
        out, start = [], 0
        while True:
            i = self.raw.find(pat, start, text.offset + text.size)
            if i < 0:
                return out
            if i >= text.offset:
                out.append(text.addr + (i - text.offset))
            start = i + 1


    # --- PLT ---------------------------------------------------------------
    def jump_slots(self) -> list[tuple[int, str]]:
        """(slot GOT, nombre del símbolo) de cada R_ARM_JUMP_SLOT de .rel.plt."""
        rel = next((s for s in self.sections if s.name == ".rel.plt"), None)
        dynsym = next((s for s in self.sections if s.name == ".dynsym"), None)
        if rel is None or dynsym is None:
            return []
        hdr = self._section_header(next(i for i, s in enumerate(self.sections) if s.name == ".dynsym"))
        strtab = self.sections[hdr["link"]]
        out = []
        for o in range(rel.offset, rel.offset + rel.size, 8):
            r_offset, r_info = struct.unpack_from("<II", self.raw, o)
            if (r_info & 0xFF) != 22:  # R_ARM_JUMP_SLOT
                continue
            idx = r_info >> 8
            st_name = struct.unpack_from("<I", self.raw, dynsym.offset + idx * 16)[0]
            out.append((r_offset, self._cstr(strtab.offset + st_name)))
        return out

    def plt_map(self) -> dict[int, str]:
        """Dirección del stub .plt -> símbolo importado.

        Los stubs ARM son de 12 B: `add ip, pc, #hi ; add ip, ip, #lo ;
        ldr pc, [ip, #off]!`.  El stub resuelve el slot GOT que le asigna
        `.rel.plt` en orden creciente de slot; se verifica decodificando el
        destino del `ldr`, no se asume el orden.
        """
        plt = next((s for s in self.sections if s.name == ".plt"), None)
        if plt is None:
            return {}
        slots = dict(self.jump_slots())
        out: dict[int, str] = {}
        for addr in range(plt.addr, plt.addr + plt.size - 12, 4):
            chunk = self.read_vaddr(addr, 12)
            if len(chunk) < 12:
                continue
            hdr, a1, a2 = struct.unpack("<III", chunk)
            if (hdr & 0xFFF00000) != 0xE2800000 or ((hdr >> 16) & 0xF) != 15:  # add ip, pc, #imm12
                continue
            if (a1 & 0xFFF00000) != 0xE2800000 or ((a1 >> 16) & 0xF) != 12:  # add ip, ip, #imm12
                continue
            if (a2 & 0xFFFFF000) != 0xE5BCF000:  # ldr pc, [ip, #imm12]!
                continue

            def rotimm(w: int) -> int:
                imm8, rot = w & 0xFF, ((w >> 8) & 0xF) * 2
                return ((imm8 >> rot) | (imm8 << (32 - rot))) & 0xFFFFFFFF if rot else imm8

            ip = (addr + 8 + rotimm(hdr) + rotimm(a1)) & 0xFFFFFFFF
            slot = (ip + (a2 & 0xFFF)) & 0xFFFFFFFF
            if slot in slots:
                out[addr] = slots[slot]
        return out

    def name_of(self, addr: int, plt: dict[int, str] | None = None) -> str | None:
        """Nombre del símbolo si `addr` es un stub .plt."""
        plt = self.plt_map() if plt is None else plt
        return plt.get(addr & ~1)


def disasm(elf: Elf, addr: int, count: int = 24) -> list[str]:
    if Cs is None:
        return ["capstone no disponible"]
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.detail = False
    code = elf.read_vaddr(addr & ~1, count * 4 + 16)
    lines = []
    for ins in cs.disasm(code, addr & ~1):
        lines.append(f"0x{ins.address:08x}: {ins.mnemonic:8s} {ins.op_str}")
        if len(lines) >= count:
            break
    return lines


def call_targets(elf: Elf, addr: int, count: int = 2000) -> list[tuple[int, int, str]]:
    """Lista (sitio, destino, mnemónico) de llamadas directas en una función."""
    if Cs is None:
        return []
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.detail = False
    nxt = elf.symbols
    start = next((s for s in nxt if s.addr == (addr | 1)), None) or next(
        (s for s in nxt if s.addr == addr), None)
    size = start.size if start and start.size else 0x400
    code = elf.read_vaddr(addr & ~1, max(size + 16, 32))
    out = []
    for ins in cs.disasm(code, addr & ~1):
        if ins.mnemonic in ("bl", "blx", "b.w", "b") and ins.op_str.startswith("#"):
            try:
                tgt = int(ins.op_str[1:], 0)
            except ValueError:
                continue
            out.append((ins.address, tgt, ins.mnemonic))
        if len(out) > count:
            break
    return out


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    cmd, elf_path = argv[1], argv[2]
    elf = Elf(elf_path)
    if cmd == "sym":
        rx = re.compile(argv[3])
        for s in elf.symbols:
            if rx.search(s.name):
                print(f"0x{s.addr:08x} size={s.size:<7d} {s.name}")
    elif cmd == "str":
        for va in elf.find_string(argv[3]):
            print(f"0x{va:08x}")
            for ref in elf.find_literal_refs(va):
                holder = elf.symbol_at(ref)
                print(f"   literal en 0x{ref:08x}  ({holder.name if holder else '?'}+0x{ref-holder.addr:x})" if holder
                      else f"   literal en 0x{ref:08x}")
    elif cmd == "refs":
        va = int(argv[3], 0)
        for ref in elf.find_literal_refs(va):
            holder = elf.symbol_at(ref)
            print(f"0x{ref:08x} {holder.name + f'+0x{ref-holder.addr:x}' if holder else '?'}")
    elif cmd == "dis":
        plt = elf.plt_map()
        for line in disasm(elf, int(argv[3], 0), int(argv[4]) if len(argv) > 4 else 24):
            name = None
            if " bl" in line or "\tbl" in line:
                try:
                    tgt = int(line.split("#")[-1], 16)
                    name = elf.name_of(tgt, plt)
                except ValueError:
                    name = None
            print(f"{line:<48s} ; {name}" if name else line)
    elif cmd == "func":
        rx = re.compile(argv[3])
        matches = [s for s in elf.symbols if rx.search(s.name)]
        if not matches:
            print("sin coincidencia")
            return 1
        s = matches[0]
        print(f"; {s.name} @ 0x{s.addr:08x} size={s.size}")
        n = max(8, s.size // 2) if s.size else 40
        for line in disasm(elf, s.addr, int(n)):
            print(line)
    elif cmd == "xrefs":
        va = int(argv[3], 0)
        for ref in elf.find_literal_refs(va):
            holder = elf.symbol_at(ref)
            print(f"0x{ref:08x} {holder.name if holder else '?'}")
    elif cmd == "plt":
        plt = elf.plt_map()
        for addr, name in sorted(plt.items()):
            print(f"0x{addr:08x} {name}")
        print(f"; {len(plt)} stubs resueltos")
    elif cmd == "resolve":
        plt = elf.plt_map()
        for arg in argv[3:]:
            va = int(arg, 0)
            print(f"0x{va:08x} {elf.name_of(va, plt) or '(no es un stub .plt)'}")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
