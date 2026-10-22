#!/usr/bin/env python3
"""S136 — grafo de llamadas hacia/desde el módulo `[ACCY]`.

Decodifica las instrucciones `bl` (Thumb-2 T2) de toda la imagen y selecciona las que
apuntan a la región del módulo ACCY. Sirve para (a) saber qué funciones externas
consumen el subsistema y (b) reconstruir la jerarquía interna (fabricas de dispositivo).

Uso: .venv/bin/python analysis/s136_accy/scan_calls.py [ACCY_LO] [ACCY_HI]
"""
import json
import os
import struct
from collections import defaultdict

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
ACCY_LO, ACCY_HI = 0x43562000, 0x43567000


def bl_targets(data, lo, hi):
    """[(addr, target)] de las instrucciones `bl` Thumb-2 en [lo,hi)."""
    out = []
    U16 = struct.Struct("<H").unpack_from
    n = len(data)
    a = lo - BASE
    end = hi - BASE
    while a <= end - 4:
        h1 = U16(data, a)[0]
        if (h1 & 0xF800) == 0xF000:
            h2 = U16(data, a + 2)[0]
            if (h2 & 0xD000) == 0xD000:
                s = (h1 >> 10) & 1
                imm10 = h1 & 0x3FF
                j1 = (h2 >> 13) & 1
                j2 = (h2 >> 11) & 1
                imm11 = h2 & 0x7FF
                i1 = (~(j1 ^ s)) & 1
                i2 = (~(j2 ^ s)) & 1
                # imm32 = SignExtend(S:I1:I2:imm10:imm11:'0', 32): el bit de signo es S (bit24)
                imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
                if s:
                    imm -= 1 << 25
                out.append((BASE + a, (BASE + a + 4 + imm) & 0xFFFFFFFF))
                a += 4
                continue
        a += 2
    return out


def main():
    data = open(BIN, "rb").read()
    calls = bl_targets(data, BASE, BASE + len(data))
    into = [(c, t) for c, t in calls if ACCY_LO <= t < ACCY_HI]
    out_of = [(c, t) for c, t in calls if ACCY_LO <= c < ACCY_HI]
    print(f"bl totales: {len(calls)}")
    print(f"bl -> region ACCY: {len(into)}  (sitios distintos: {len({c for c,_ in into})})")
    print(f"bl desde la region ACCY: {len(out_of)}  (destinos distintos: {len({t for _,t in out_of})})")
    into_by_t = defaultdict(list)
    for c, t in into:
        into_by_t[t].append(c)
    print("\n--- llamadores externos (fuera de la region) hacia ACCY ---")
    ext = defaultdict(list)
    for c, t in into:
        if not (ACCY_LO <= c < ACCY_HI):
            ext[t].append(c)
    for t in sorted(ext):
        print(f"0x{t:x}  <- {len(ext[t])} call(s): {', '.join(hex(x) for x in sorted(ext[t])[:8])}")
    print("\n--- destinos externos llamados desde ACCY ---")
    outt = defaultdict(list)
    for c, t in out_of:
        if not (ACCY_LO <= t < ACCY_HI):
            outt[t].append(c)
    for t in sorted(outt, key=lambda x: -len(outt[x]))[:60]:
        print(f"0x{t:x}  x{len(outt[t])}  desde {', '.join(hex(x) for x in sorted(outt[t])[:5])}")
    json.dump({"into": {f"0x{k:x}": v for k, v in into_by_t.items()},
               "out": {f"0x{k:x}": v for k, v in outt.items()}},
              open(os.path.join(HERE, "accy_calls.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
