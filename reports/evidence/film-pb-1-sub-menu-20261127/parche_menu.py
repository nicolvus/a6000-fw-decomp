#!/usr/bin/env python3
"""Parche mínimo: meter el nodo «Selector PAL/NTSC» en la página Setup de las
configuraciones de menú de viewUnified2.so (fw 3.21) que no lo llevan.

Método: los hijos de cada página/menú son un array de punteros en .data; cada
celda es un `R_ARM_ABS32` (tipo 2) con addendo 0 cuyo símbolo está en .dynsym
(`cmnViewSettingNodeRootXxx`, definido en CautionConfig.so). Cambiar de qué nodo
cuelga una celda = reescribir el índice de símbolo de SU entrada de `.rel.dyn`
(r_info = (sym << 8) | 2): 4 bytes por celda, sin mover nada ni cambiar tamaños.

Solo lee la librería del repo y escribe /tmp/<nombre>.menu.so. No toca el repo.
Verifica, antes de escribir: addendo 0, tipo 2, símbolo de origen esperado,
una sola entrada .rel.dyn por celda y una sola aparición de los 4 bytes viejos.

Uso: parche_menu.py [LIB_SO] [SALIDA]
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

R_ARM_ABS32 = 2
TARGET = "cmnViewSettingNodeRootSettingSetupNtscPalSEL"

# (config, sección Setup, objeto página, array de hijos, índice, símbolo que se sustituye)
CELLS = (
    (0x4C43C8, 0x4C3324, 0x4C6980, 0x4A353C, 3, "cmnViewSettingNodeRootDropSensor"),
    (0x4C53F4, 0x4C6360, 0x4C6700, 0x4A2F64, 1, "cmnViewSettingNodeRootSetupMenuStart"),
    (0x4C5820, 0x4C4340, 0x4C3E64, 0x4A49F0, 0, "cmnViewSettingNodeRootSetupMenuStart"),
    (0x4C5D88, 0x4C4208, 0x4C63E0, 0x4A495C, 4, "cmnViewSettingNodeRootSetupGPSSettings"),
    (0x4C5DB8, 0x4C4800, 0x4C4A58, 0x4A40CC, 4, "cmnViewSettingNodeRoot24pMode"),
    (0x4C6660, 0x4C5640, 0x4C51B4, 0x4A3368, 0, "cmnViewSettingNodeRootSetupMenuStart"),
)

DEFAULT_LIB = ("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
               "nflasha15_unpacked_unpacked/lib/viewUnified2.so")


class Elf:
    """Vista mínima (segmentos, secciones, .rel.dyn, .dynsym/.dynstr)."""

    def __init__(self, path: Path) -> None:
        self.data = path.read_bytes()
        d = self.data
        phoff, phentsize, phnum = struct.unpack_from("<I", d, 28)[0], struct.unpack_from("<H", d, 42)[0], struct.unpack_from("<H", d, 44)[0]
        self.segs = []
        for i in range(phnum):
            t, off, va, _pa, fsz, _msz, _fl, _al = struct.unpack_from("<8I", d, phoff + phentsize * i)
            if t == 1:
                self.segs.append((off, va, fsz))
        shoff, shentsize, shnum, shstrndx = (struct.unpack_from("<I", d, 32)[0], struct.unpack_from("<H", d, 46)[0],
                                             struct.unpack_from("<H", d, 48)[0], struct.unpack_from("<H", d, 50)[0])
        secs = [struct.unpack_from("<10I", d, shoff + shentsize * i) for i in range(shnum)]
        stroff = secs[shstrndx][4]
        self.sec = {}
        for s in secs:
            name = d[stroff + s[0]:d.index(b"\0", stroff + s[0])].decode()
            self.sec[name] = (s[3], s[4], s[5])

    def read(self, va: int, n: int) -> bytes:
        for off, base, fsz in self.segs:
            if base <= va < base + fsz:
                o = off + va - base
                return self.data[o:o + n]
        raise ValueError(f"VA fuera de segmento: {va:#x}")

    def va2off(self, va: int) -> int:
        for off, base, fsz in self.segs:
            if base <= va < base + fsz:
                return off + va - base
        raise ValueError(f"VA fuera de segmento: {va:#x}")

    def symbols(self) -> list[str]:
        sym_off = self.sec[".dynsym"][1]
        str_off = self.sec[".dynstr"][1]
        n = self.sec[".dynsym"][2] // 16
        out = []
        for i in range(n):
            st_name, value, size, info, other, shndx = struct.unpack_from("<IIIBBH", self.data, sym_off + 16 * i)
            out.append(self.data[str_off + st_name:self.data.index(b"\0", str_off + st_name)].decode("latin1"))
        return out

    def relocs(self) -> dict[int, tuple[int, int]]:
        """{r_offset: (tipo, índice de símbolo)} de .rel.dyn."""
        off, size = self.sec[".rel.dyn"][1], self.sec[".rel.dyn"][2]
        out = {}
        for i in range(0, size, 8):
            r_off, r_info = struct.unpack_from("<II", self.data, off + i)
            out[r_off] = (r_info & 0xFF, r_info >> 8)
        return out


def main(lib: Path, dest: Path) -> int:
    e = Elf(lib)
    syms = e.symbols()
    if TARGET not in syms:
        print(f"ERROR: no existe el símbolo {TARGET}")
        return 1
    new_sym = syms.index(TARGET)
    new_info = (new_sym << 8) | R_ARM_ABS32
    rel = e.relocs()
    rel_off = e.sec[".rel.dyn"][1]
    rel_size = e.sec[".rel.dyn"][2]
    by_symbol: dict[int, list[int]] = {}
    for i in range(0, rel_size, 8):
        r_off, r_info = struct.unpack_from("<II", e.data, rel_off + i)
        by_symbol.setdefault(r_info >> 8, []).append(r_off)

    out = bytearray(e.data)
    print(f"LIB {lib}\n  símbolo destino {TARGET} = dynsym[{new_sym}] -> r_info {new_info:#010x}")
    print(f"  celdas que ya lo usan: {len(by_symbol.get(new_sym, []))}")
    changes = 0
    for cfg, sect, page, arr, idx, old in CELLS:
        cell = arr + 4 * idx
        word = struct.unpack("<I", e.read(cell, 4))[0]
        assert word == 0, f"{cell:#x}: addendo {word:#x} != 0"
        assert cell in rel, f"{cell:#x}: sin entrada en .rel.dyn"
        typ, si = rel[cell]
        assert typ == R_ARM_ABS32, f"{cell:#x}: tipo {typ} != R_ARM_ABS32"
        assert syms[si] == old, f"{cell:#x}: símbolo actual {syms[si]} != {old}"
        assert old != TARGET
        off = rel_off + 8 * list(rel).index(cell) if False else None
        # localizar la posición exacta de la entrada
        positions = [rel_off + 8 * i for i in range(rel_size // 8)
                     if struct.unpack_from("<I", e.data, rel_off + 8 * i)[0] == cell]
        assert len(positions) == 1, f"{cell:#x}: {len(positions)} entradas .rel.dyn"
        old_bytes = struct.pack("<I", (si << 8) | R_ARM_ABS32)
        pat = struct.pack("<II", cell, (si << 8) | R_ARM_ABS32)
        assert e.data.count(old_bytes) >= 1
        assert e.data.count(pat) == 1, f"{cell:#x}: el par (r_offset,r_info) no es único ({e.data.count(pat)})"
        struct.pack_into("<I", out, positions[0] + 4, new_info)
        print(f"  cfg {cfg:#x} sección {sect:#x} página {page:#x}: celda {cell:#x} "
              f"(arr {arr:#x}+{idx * 4:#x}) {old.split('Root')[-1]} -> SettingSetupNtscPalSEL")
        print(f"      .rel.dyn @{positions[0]:#x}:  {old_bytes.hex(' ')}  ->  {struct.pack('<I', new_info).hex(' ')}")
        changes += 1

    dest.write_bytes(bytes(out))
    # ---- verificación sobre la copia ----
    v = Elf(dest)
    print(f"\nSALIDA {dest} ({len(out)} B, {changes * 4} bytes cambiados)")
    diffs = [i for i in range(len(e.data)) if e.data[i] != out[i]]
    print(f"  {changes * 4} bytes escritos; {len(diffs)} con valor distinto -> {[hex(x) for x in diffs]}")
    vrel = v.relocs()
    for cfg, sect, page, arr, idx, old in CELLS:
        cell = arr + 4 * idx
        typ, si = vrel[cell]
        assert (typ, si) == (R_ARM_ABS32, new_sym), (hex(cell), typ, si)
    print(f"  celdas que ahora usan el símbolo: {sum(1 for t, s in vrel.values() if s == new_sym)}")
    for cfg, sect, page, arr, idx, old in CELLS:
        names = []
        for k in range(0, 0x20, 4):  # los arrays son contiguos: basta comprobar la celda
            typ, si = vrel.get(arr + k, (0, 0))
            if typ == R_ARM_ABS32:
                names.append(syms[si].replace("cmnViewSettingNodeRoot", ""))
        print(f"  cfg {cfg:#x} arr {arr:#x}: {', '.join(names[:idx + 1])}")
    print("  OK: las 6 celdas apuntan a SettingSetupNtscPalSEL y nada más ha cambiado")
    return 0


if __name__ == "__main__":
    lib = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(DEFAULT_LIB)
    dest = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp") / (lib.name.replace(".so", "") + ".menu.so")
    raise SystemExit(main(lib, dest))
