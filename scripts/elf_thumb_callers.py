"""Llamadores BL/BLX Thumb-2 y punteros de datos hacia una función de un .so ARM de nflasha15.
Uso: python3 -I scripts/elf_thumb_callers.py lib.so 0xVA... (VA ELF, sin +0x10000 de Ghidra)"""
import struct
import sys


def text_range(b: bytes):
    # shortcut: solo ELF32 LE con .text identidad VA==offset (libObj/libmpr); revisar si se usa otra biblioteca
    shoff, shentsize, shnum, shstrndx = struct.unpack_from("<I10xHHH", b, 0x20)[0], *struct.unpack_from("<HHH", b, 0x2E)
    secs = [struct.unpack_from("<10I", b, shoff + i * shentsize) for i in range(shnum)]
    strtab = secs[shstrndx][4]
    for s in secs:
        if b[strtab + s[0]:b.index(b"\0", strtab + s[0])] == b".text":
            return s[3], s[4], s[5]
    raise ValueError(".text")


def callers(b: bytes, targets: set[int]):
    va, off, size = text_range(b)
    h = memoryview(b)[off:off + size // 2 * 2].cast("H")
    for i in range(len(h) - 1):
        a, c = h[i], h[i + 1]
        if a & 0xF800 == 0xF000 and c & 0xC000 == 0xC000:
            s = (a >> 10) & 1; j1 = (c >> 13) & 1; j2 = (c >> 11) & 1
            i1 = ~(j1 ^ s) & 1; i2 = ~(j2 ^ s) & 1
            imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((a & 0x3FF) << 12) | ((c & 0x7FF) << 1)
            if s:
                imm -= 1 << 25
            pc = va + 2 * i + 4
            t = (pc if c & 0x1000 else pc & ~3) + imm
            if t in targets:
                yield va + 2 * i, t


if __name__ == "__main__":
    b = open(sys.argv[1], "rb").read()
    want = {int(x, 0) & ~1 for x in sys.argv[2:]}
    for a, t in callers(b, want):
        print(f"{a:#x} -> {t:#x}")
    for t in want:
        pat = struct.pack("<I", t | 1)
        i = b.find(pat)
        while i >= 0:
            print(f"ptr {i:#x} -> {t:#x}")
            i = b.find(pat, i + 1)
