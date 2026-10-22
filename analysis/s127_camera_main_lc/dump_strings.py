#!/usr/bin/env python3
"""S127 — volcado de cadenas (separadas por NUL) en un rango de vaddr.

Uso: .venv/bin/python analysis/s127_camera_main_lc/dump_strings.py 0x43ca7900 0x43ca7e80 [bin]
"""
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"


def main():
    lo = int(sys.argv[1], 16)
    hi = int(sys.argv[2], 16)
    path = sys.argv[3] if len(sys.argv) > 3 else BIN
    data = open(path, "rb").read()
    i = lo - BASE
    e = hi - BASE
    start = i
    while i < e:
        if data[i] == 0:
            if i > start:
                print(f"0x{BASE + start:x}\t{data[start:i].decode('latin1')}")
            start = i + 1
        i += 1


if __name__ == "__main__":
    main()
