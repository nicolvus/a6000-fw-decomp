#!/usr/bin/env python3
"""S151 - localiza el inicio de la funcion que contiene una direccion (prologo Thumb).

Heuristica: se busca hacia atras el `push`/`push.w` mas cercano (16 o 32 bits).

Uso:  .venv/bin/python analysis/s151_panda/func_start.py 0x43793efe
"""
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from


def is_push16(h):
    return (h & 0xFE00) == 0xB400 and (h & 0x00FF) != 0


def is_push32(h1, h2):
    # push.w {regs,lr}: 0xE92D 0x4xxx  (bit14 = LR)  | 0xE92D con lista de 16 bits
    return h1 == 0xE92D


def is_pop16(h):
    return (h & 0xFE00) == 0xBC00 and (h & 0x00FF) != 0


def is_pop32(h1, h2):
    return h1 == 0xE8BD


def main():
    addr = int(sys.argv[1], 0)
    o = addr - BASE
    best = None
    a = o - (o % 2)
    while a >= max(0, o - 0x4000):
        h1 = U16(B, a)[0]
        hit = False
        if is_push16(h1):
            hit = True
        elif a + 4 <= N and is_push32(h1, U16(B, a + 2)[0]):
            hit = True
        if hit:
            # el prologo mas cercano es el candidato
            best = a
            break
        a -= 2
    if best is None:
        print("sin prologo encontrado")
        return
    print(f"candidato de inicio de funcion: 0x{BASE + best:08x}  (dir examinada 0x{addr:08x})")


if __name__ == "__main__":
    main()
