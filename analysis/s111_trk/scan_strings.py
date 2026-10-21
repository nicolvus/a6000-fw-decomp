#!/usr/bin/env python3
"""Extrae las trazas del módulo `[TRK]` del `av-cam.bin` (A6000 fw3.21).

Se cuenta cada ocurrencia del literal `[TRK` (216 en A6000, 216 en A7S fw3.20)
y se guarda la cadena imprimible completa que la contiene, con su vaddr
(`BASE + file_offset`, BASE = 0x43541000).

Salida: analysis/s111_trk/strings_raw.json
Uso:    python3 scan_strings.py [BIN] [BASE] [OUT]
"""
import json
import os
import re
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = re.compile(rb"[ -~]{2,}")


def extract(bin_path, base):
    data = open(bin_path, "rb").read()
    out = []
    for m in RUN.finditer(data):
        s = m.group()
        if b"[TRK" not in s:
            continue
        out.append({"file_offset": m.start(), "vaddr": hex(base + m.start()),
                    "text": s.decode("latin1")})
    return out, data.count(b"[TRK")


def main():
    bin_path = sys.argv[1] if len(sys.argv) > 1 else BIN
    base = int(sys.argv[2], 0) if len(sys.argv) > 2 else BASE
    dest = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "strings_raw.json")
    rows, n_occ = extract(bin_path, base)
    json.dump({"module": "TRK", "bin": bin_path, "base": hex(base),
               "n_occurrences": n_occ, "n_runs": len(rows), "strings": rows},
              open(dest, "w"), indent=1, ensure_ascii=False)
    print(f"{n_occ} ocurrencias de [TRK en {len(rows)} cadenas; escrito {dest}")


if __name__ == "__main__":
    main()
