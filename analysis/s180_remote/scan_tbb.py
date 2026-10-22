#!/usr/bin/env python3
"""S180 - decodificar tablas TBB/TBH del sub-bloque [REMOTE] (A6000)."""
import struct, sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()


def cstr(a):
    o = a - BASE
    if o < 0 or o >= len(B):
        return None
    e = o
    while e < len(B) and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1") if e > o else None


def decode_tbb(addr, n):
    base = (addr + 4) & ~3
    print(f"TBB @0x{addr:08x}  base 0x{base:08x}  n={n}   (entradas de 1 byte, offset = 2*byte)")
    for i in range(n):
        a = base + i
        byte = B[a - BASE]
        tgt = base + 2 * byte
        print(f"   [{i}] byte@0x{a:08x}=0x{byte:02x} -> target 0x{tgt:08x}  {cstr(tgt)!r}")


def decode_tbh(addr, n):
    base = (addr + 4) & ~3
    print(f"TBH @0x{addr:08x}  base 0x{base:08x}  n={n}")
    for i in range(n):
        a = base + 2 * i
        hw = struct.unpack_from("<H", B, a - BASE)[0]
        off = hw if hw < 0x8000 else hw - 0x10000
        tgt = base + 4 * off
        print(f"   [{i}] halfword@0x{a:08x}=0x{hw:04x} -> target 0x{tgt:08x}  {cstr(tgt)!r}")


if __name__ == "__main__":
    # NotifyUartCommand: categoria -> caracter  (tbb @0x435662f4)
    decode_tbb(0x435662f4, 6)
    print()
    # ExecUartCommand: caracter de comando -> 4 grupos de botones (tbb @0x43566638)
    decode_tbb(0x43566638, 4)
    print()
    # TallyControlCmd: estado del tally -> '1'/'2'/'3' (tbb @0x43566960)
    decode_tbb(0x43566960, 4)
    print()
    # SendCmd / RetrySendCmd
    decode_tbb(0x435668b4, 2)
