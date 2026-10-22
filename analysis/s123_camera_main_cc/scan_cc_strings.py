#!/usr/bin/env python3
"""S123 — extracción de las trazas `[CAMERA_MAIN_CC]` (control de captura).

Lee el binario por trozos (sin cargarlo entero) y vuelca cada cadena con su
vaddr, offset, texto y el "bloque" (sub-módulo) que nombra.

Convención: vaddr = 0x43541000 + file_offset.

Uso:  scan_cc_strings.py [RUTA_SALIDA]
"""
import json
import os
import re
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
PREFIX = b"[CAMERA_MAIN_CC]"
HERE = os.path.dirname(os.path.abspath(__file__))
CHUNK = 1 << 22          # 4 MiB por lectura, con solape


def iter_strings(path, prefix):
    """Devuelve (offset, texto) de cada cadena que empieza por `prefix`."""
    n = os.path.getsize(path)
    out = []
    with open(path, "rb") as fh:
        pos = 0
        carry = b""
        while pos < n:
            fh.seek(pos)
            data = fh.read(CHUNK)
            if not data:
                break
            buf = carry + data
            base_off = pos - len(carry)
            start = 0
            while True:
                i = buf.find(prefix, start)
                if i < 0:
                    break
                e = i
                while e < len(buf) and 32 <= buf[e] < 127:
                    e += 1
                out.append((base_off + i, buf[i:e].decode("latin1")))
                start = i + 1
            carry = buf[-len(prefix):]
            pos += len(data)
    # dedup por offset
    seen = set()
    uniq = []
    for off, txt in out:
        if off not in seen:
            seen.add(off)
            uniq.append((off, txt))
    return uniq


def subblock(text):
    """`[CAMERA_MAIN_CC]: <Bloque> ...` -> nombre del bloque."""
    m = re.match(r"\[CAMERA_MAIN_CC\]:\s*([A-Za-z0-9_]{2,40})", text)
    return m.group(1) if m else None


def main():
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "cc_strings.json")
    rows = iter_strings(BIN, PREFIX)
    strings = []
    for off, txt in rows:
        strings.append({"vaddr": f"0x{BASE + off:x}", "off": off,
                        "text": txt, "block": subblock(txt)})
    json.dump({"module": "CAMERA_MAIN_CC", "count": len(strings), "strings": strings},
              open(dest, "w"), indent=1, ensure_ascii=False)
    print(f"cadenas: {len(strings)} -> {dest}")
    for s in strings:
        print(f"  {s['vaddr']}  {s['text']}")


if __name__ == "__main__":
    main()
