#!/usr/bin/env python3
"""G26 — desensamblador Thumb-2 mínimo (capstone) para `libObj.so` (VA == offset en el primer LOAD). Uso: libobj_dis.py LIB INI FIN"""
import sys
from pathlib import Path
import capstone

def dis(lib: Path, ini: int, fin: int):
    d = lib.read_bytes()
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    return [f"{i.address:x}: {i.mnemonic} {i.op_str}" for i in md.disasm(d[ini:fin], ini)]

if __name__ == "__main__":
    print("\n".join(dis(Path(sys.argv[1]), int(sys.argv[2], 16), int(sys.argv[3], 16))))
