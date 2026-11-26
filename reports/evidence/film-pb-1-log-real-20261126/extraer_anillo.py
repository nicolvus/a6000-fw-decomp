#!/usr/bin/env python3
"""Extrae el anillo de log del proceso MPR (VA 0x82DF9300-0x82DFC400) del dump del 20-10-2026.

Uso: extraer_anillo.py <ram_0x80000000.bin> <salida.txt>
Comprueba el SHA-256 del dump antes de extraer; si no coincide, aborta.
"""
import hashlib
import sys
from pathlib import Path

SHA256 = "f96c6152f697a8680f6d342cfdc0133bc28b8ab85a6baf48c19358546ff2fdbf"
BASE = 0x80000000
INI, FIN = 0x2DF9300, 0x2DFC400

def main(src: Path, dst: Path) -> None:
    b = src.read_bytes()
    h = hashlib.sha256(b).hexdigest()
    print(f"dump: {len(b)} B  sha256={h}")
    if SHA256 != "PENDIENTE" and h != SHA256:
        raise SystemExit("dump inesperado")
    txt = b[INI:FIN].decode("latin1")
    lineas = [l.strip() for l in txt.replace("\r", "\n").split("\n")]
    lineas = [l for l in lineas if len(l) >= 6 and all(32 <= ord(c) < 127 for c in l)]
    dst.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"{len(lineas)} líneas -> {dst}")

if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
