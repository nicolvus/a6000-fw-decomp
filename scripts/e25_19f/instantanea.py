#!/usr/bin/env python3
"""E25-19f P4 — instantánea SOLO LECTURA de la región de datos de BIONZ (virtual → físico +0x40000000) para alimentar Unicorn.

Uso: PYTHONPATH=scripts python instantanea.py DESDE HASTA SALIDA.bin   (direcciones virtuales)
"""
from __future__ import annotations

import sys
from pathlib import Path

from e25_19_readonly import HOST, Telnet, sha, verify_originals  # type: ignore[import-not-found]

RAM_OFF = 0x40000000
CH = 0x8000


def main(desde: int, hasta: int, out: Path) -> int:
    tr = Telnet(HOST)
    try:
        assert verify_originals(tr)["ok"], "originales T050 alterados"
        buf = bytearray()
        for a in range(desde, hasta, CH):
            buf += tr.read(a + RAM_OFF, min(CH, hasta - a))
        assert verify_originals(tr)["ok"]
    finally:
        tr.close()
    out.write_bytes(bytes(buf))
    print(out, len(buf), sha(bytes(buf)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1], 0), int(sys.argv[2], 0), Path(sys.argv[3])))
