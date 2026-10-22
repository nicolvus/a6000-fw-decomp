#!/usr/bin/env python3
"""S166 — para cada llamada `bl 0x43561228` (servicio generico por vtable) de la imagen,
resuelve el "handle" (r0) desde el `ldr r0,[pc,#imm]` mas cercano hacia atras y agrupa.

Salida: JSON {"0x<handle>": ["0x<site>", ...]}
"""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
DATA = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()


def u32(a):
    o = a - BASE
    if 0 <= o and o + 4 <= len(DATA):
        return struct.unpack_from("<I", DATA, o)[0]
    return None


def bl_target(a):
    o = a - BASE
    if o + 4 > len(DATA):
        return None
    hw1, hw2 = struct.unpack_from("<HH", DATA, o)
    if (hw1 & 0xF800) != 0xF000 or (hw2 & 0xD000) != 0xD000:
        return None
    S = (hw1 >> 10) & 1
    imm10 = hw1 & 0x3FF
    J1 = (hw2 >> 13) & 1
    J2 = (hw2 >> 11) & 1
    imm11 = hw2 & 0x7FF
    I1 = 1 - (J1 ^ S)
    I2 = 1 - (J2 ^ S)
    off = (S << 24) | (I1 << 23) | (I2 << 22) | (imm10 << 12) | (imm11 << 1)
    if S:
        off -= (1 << 25)
    return a + 4 + off


def main():
    target = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x43561228
    res = {}
    n = len(DATA)
    i = 0
    while i < n - 4:
        hw1 = int.from_bytes(DATA[i:i + 2], "little")
        if (hw1 & 0xF800) == 0xF000:
            a = BASE + i
            if bl_target(a) == target:
                # buscar hacia atras el 'ldr r0,[pc,#imm]' mas cercano
                handle = None
                j = i - 2
                while j >= max(i - 60, 0):
                    hj = int.from_bytes(DATA[j:j + 2], "little")
                    if (hj >> 11) == 0b01001 and ((hj >> 8) & 7) == 0:
                        imm = (hj & 0xFF) * 4
                        lit = ((BASE + j + 4) & ~3) + imm
                        handle = u32(lit)
                        break
                    j -= 2
                res.setdefault("%08x" % (handle if handle is not None else 0), []).append("%08x" % a)
            i += 4
        else:
            i += 2
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
