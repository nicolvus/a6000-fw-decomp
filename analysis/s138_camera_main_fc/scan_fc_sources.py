#!/usr/bin/env python3
"""S138 — localiza en el binario los nombres de fichero fuente relacionados con el
módulo FC (face / touch shutter) y los nombres de clase RTTI con "FC".

Salida: texto + JSON.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()

PAT_FILE = re.compile(rb"[A-Za-z0-9_./\\-]{3,80}\.(?:cpp|c|h|cc)\x00")
KEYS = ("fc", "FC", "face", "Face", "touch", "Touch", "shutter", "Shutter")


def main():
    hits = []
    for m in PAT_FILE.finditer(B):
        name = m.group()[:-1].decode("latin1")
        if any(k in name for k in KEYS):
            hits.append((BASE + m.start(), name))
    print(f"ficheros fuente candidatos: {len(hits)}")
    for a, n in hits:
        print(f"  0x{a:08x}  {n}")
    json.dump([{"vaddr": f"0x{a:x}", "name": n} for a, n in hits],
              open(os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_source_files.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
