#!/usr/bin/env python3
"""Desensambla un rango de `av-cam.bin` (A6000 fw3.21 o A7S fw3.20) con capstone. Solo lee. Uso: avcam_dis.py a6000|a7s INICIO [LONGITUD_HEX]"""
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
FILES = {"a6000": "av-cam.bin", "a7s": "av-cam-a7s.bin"}


def dis(model: str, start: int, length: int = 0x100):
    d = (ROOT / "analysis/rea-independent/input" / FILES[model]).read_bytes()
    yield from Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(d[start - BASE:start - BASE + length], start)


if __name__ == "__main__":
    for i in dis(sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x100):
        print(f"{i.address:#x}: {i.mnemonic} {i.op_str}")
