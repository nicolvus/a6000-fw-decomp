#!/usr/bin/env python3
"""S156 — diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01 del módulo TP.

Escanea un av-cam.bin dado y devuelve, para un conjunto de cadenas objetivo:
  - las direcciones de las cadenas,
  - los sitios de referencia PIC (regla estricta: `add rX,pc` con el `ldr rX,[pc,#imm]`
    más cercano) y la función que los contiene.
"""
import bisect
import json
import re
import struct
import sys

BASE = 0x43541000
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from

FILES = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}


class Img:
    def __init__(self, path):
        self.B = open(path, "rb").read()
        self.N = len(self.B)

    def cstr(self, addr):
        o = addr - BASE
        if o < 0 or o >= self.N:
            return None
        e = self.B.find(b"\x00", o)
        if e < 0:
            return None
        try:
            return self.B[o:e].decode("utf-8")
        except UnicodeDecodeError:
            return None

    def strings(self, minlen=2):
        out = []
        start = None
        cur = bytearray()
        for i in range(self.N):
            c = self.B[i]
            if 32 <= c < 127:
                if start is None:
                    start = i
                cur.append(c)
            else:
                if start is not None and len(cur) >= minlen:
                    out.append((BASE + start, bytes(cur).decode("ascii", "replace")))
                start = None
                cur = bytearray()
        return out

    def ldr_sites(self, lo, hi):
        out = []
        a = lo
        while a < hi:
            o = a - BASE
            if o < 0 or o > self.N - 8:
                a += 2
                continue
            h = U16(self.B, o)[0]
            reg = lit = None
            if (h & 0xF800) == 0x4800:
                reg = (h >> 8) & 7
                lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
            elif (h & 0xFF7F) == 0xF85F:
                h2 = U16(self.B, o + 2)[0]
                reg = (h2 >> 12) & 0xF
                lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
            if reg is not None and 0 <= lit - BASE <= self.N - 4:
                out.append((a, reg, U32(self.B, lit - BASE)[0], lit))
            a += 2
        return out

    def add_sites(self, lo, hi):
        out = []
        a = lo
        while a < hi:
            o = a - BASE
            if o < 0 or o > self.N - 4:
                a += 2
                continue
            h = U16(self.B, o)[0]
            if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
                out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
            a += 2
        return out

    def strict_map(self, lo=BASE, hi=None):
        hi = hi if hi is not None else BASE + self.N
        ldrs = self.ldr_sites(lo, hi)
        adds = self.add_sites(lo, hi)
        by_reg = {}
        for a, reg, w, lit in ldrs:
            by_reg.setdefault(reg, []).append((a, w))
        for v in by_reg.values():
            v.sort()
        keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
        out = {}
        for a, reg in adds:
            v = by_reg.get(reg)
            if not v:
                continue
            ks = keys[reg]
            i = bisect.bisect_left(ks, a) - 1
            if i < 0:
                continue
            la, w = v[i]
            if a - la > 4096:
                continue
            tgt = (w + (a + 4)) & 0xFFFFFFFF
            out.setdefault(tgt, []).append(a)
        return {k: sorted(set(v)) for k, v in out.items()}

    def func_start(self, addr, back=0x8000):
        o = addr - BASE
        a = o - (o % 2)
        while a >= max(0, o - back):
            h1 = U16(self.B, a)[0]
            if (h1 & 0xFE00) == 0xB400 and (h1 & 0x00FF) != 0:
                return BASE + a
            if a + 4 <= self.N and h1 == 0xE92D:
                return BASE + a
            a -= 2
        return None

    def abs_ptrs(self, addr):
        """Direcciones de punteros absolutos de 4 B al valor `addr`."""
        w = struct.pack("<I", addr)
        out = []
        i = self.B.find(w)
        while i >= 0:
            out.append(BASE + i)
            i = self.B.find(w, i + 1)
        return out


if __name__ == "__main__":
    which = sys.argv[1]
    img = Img(FILES[which])
    pat = sys.argv[2]
    smap = img.strict_map()
    for a, s in img.strings():
        if re.search(pat, s):
            refs = smap.get(a, [])
            print(f"{a:#x} {s!r}")
            for r in refs:
                print(f"     ref {r:#x}  func~{img.func_start(r):#x}")
