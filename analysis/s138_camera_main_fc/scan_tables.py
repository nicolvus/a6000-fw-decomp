#!/usr/bin/env python3
"""S138 — tablas de salto Thumb (`tbb`/`tbh`): calcula todos los destinos posibles.

`tbb`: target = PC + mem8[PC + Rm]
`tbh`: target = PC + 2*mem16[PC + 2*Rm]     (PC = dirección_de_la_instrucción + 4)

Sirve para descartar que una función se alcance por tabla de saltos (y no por
`bl` directo), que es el caso típico de un dispatcher.
"""
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
N = len(B)


def tables():
    """[(dir_tabla, [destinos])] para cada tbb/tbh de la imagen."""
    out = []
    a = BASE
    while a < BASE + N - 4:
        o = a - BASE
        h = struct.unpack_from("<H", B, o)[0]
        if (h & 0xFFE0) == 0xE8C0:            # TBB
            rm = h & 0xF
            pc = a + 4
            base = pc + rm
            if BASE <= base < BASE + N:
                tg = sorted({pc + B[base - BASE] for _ in (0,)})
                out.append((a, base, "tbb", tg))
        elif (h & 0xFFE0) == 0xE8E0:          # TBH
            rm = h & 0xF
            pc = a + 4
            base = pc + 2 * rm
            n = 0
            while base + 2 * n + 1 < BASE + N and n < 256:
                half = struct.unpack_from("<H", B, base + 2 * n - BASE)[0]
                tg = pc + 2 * half
                if not (BASE <= tg < BASE + N):
                    break
                n += 1
            if n:
                out.append((a, base, "tbh", None))
        a += 2
    return out


def main():
    targets = set(int(x, 16) for x in sys.argv[1:])
    res = []
    for a, base, kind, _ in tables():
        if kind == "tbb":
            tg = sorted({(a + 4) + B[base - BASE]})
        else:
            tg = []
            n = 0
            while base + 2 * n + 1 < BASE + N and n < 256:
                half = struct.unpack_from("<H", B, base + 2 * n - BASE)[0]
                t = (a + 4) + 2 * half
                if not (BASE <= t < BASE + N):
                    break
                tg.append(t)
                n += 1
        hit = sorted(t for t in tg if t in targets)
        if hit:
            res.append({"site": f"0x{a:x}", "kind": kind, "table": f"0x{base:x}",
                        "targets": [f"0x{t:x}" for t in hit],
                        "all": [f"0x{t:x}" for t in tg]})
            print(f"{kind} en 0x{a:x} (tabla 0x{base:x}) -> {[hex(t) for t in hit]}")
            print(f"    todos: {[hex(t) for t in tg]}")
    if not res:
        print("ninguna tabla de saltos alcanza los objetivos")
    json.dump(res, open(os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_tables.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
