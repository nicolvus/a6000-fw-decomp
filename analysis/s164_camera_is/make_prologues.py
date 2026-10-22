#!/usr/bin/env python3
"""S164 — cache de prologos Thumb (push {...,lr}) para resolver la funcion contenedora
de cualquier direccion. Guarda analysis/s164_camera_is/prologues.json
"""
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
DATA = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False

def main():
    prol = []
    off = 0
    n = len(DATA)
    while off < n:
        got = False
        for i in MD.disasm(DATA[off:off + 16], BASE + off):
            got = True
            if i.mnemonic.startswith("push") and "lr" in i.op_str:
                prol.append(i.address)
            off += i.size
        if not got:
            off += 2
    prol.sort()
    out = Path(__file__).with_name("prologues.json")
    out.write_text(json.dumps(prol))
    print(len(prol), "prologos ->", out)


if __name__ == "__main__":
    main()
