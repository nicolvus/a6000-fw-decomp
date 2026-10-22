#!/usr/bin/env python3
"""S166 — utilidades de bytes: lectura u32/u16 en vaddr, busqueda de punteros absolutos.

Uso:
  rd.py u32 0xADDR [n]
  rd.py u16 0xADDR [n]
  rd.py str 0xADDR
  rd.py ptr 0xADDR       # busca punteros de 32 bits (LE) al valor de la word en 0xADDR
  rd.py findptr 0xVALUE  # busca la word 0xVALUE en toda la imagen y devuelve vaddrs
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
DATA = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()


def main():
    mode = sys.argv[1]
    if mode in ("u32", "u16"):
        a = int(sys.argv[2], 0)
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
        fmt = "<I" if mode == "u32" else "<H"
        sz = 4 if mode == "u32" else 2
        for i in range(n):
            off = a - BASE + i * sz
            v = struct.unpack_from(fmt, DATA, off)[0]
            print("%08x  %s  0x%x" % (a + i * sz, " ".join("%02x" % x for x in
                  DATA[off:off + sz]), v))
    elif mode == "str":
        a = int(sys.argv[2], 0)
        off = a - BASE
        end = off
        while end < len(DATA) and DATA[end] != 0:
            end += 1
        print(repr(DATA[off:end].decode("latin1")))
    elif mode == "findptr":
        val = int(sys.argv[2], 0)
        pat = struct.pack("<I", val)
        i = 0
        while True:
            j = DATA.find(pat, i)
            if j < 0:
                break
            print("%08x" % (BASE + j))
            i = j + 1


if __name__ == "__main__":
    main()
