#!/usr/bin/env python3
"""S151 - compara la forma de una funcion entre dos blobs (A6000 fw3.21 vs A7S fw3.20).

Imprime la secuencia de llamadas (bl/blx) de ambas funciones con su desplazamiento
relativo desde el inicio, para poder contrastar la estructura.

Uso:  .venv/bin/python analysis/s151_panda/cmp_func.py <a7s|a6300|a6000> LO HI
"""
import os
import struct
import sys

import capstone

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLOBS = {
    "a6000": "analysis/rea-independent/input/av-cam.bin",
    "a7s": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "a6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}


def calls(which, lo, hi):
    B = open(os.path.join(REPO, BLOBS[which]), "rb").read()
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.detail = True
    out = []
    for ins in md.disasm(B[lo - BASE:hi - BASE], lo):
        if ins.mnemonic in ("bl", "blx"):
            out.append((ins.address - lo, ins.mnemonic, ins.op_str))
    return out


def main():
    which = sys.argv[1]
    lo = int(sys.argv[2], 0)
    hi = int(sys.argv[3], 0)
    for d, m, t in calls(which, lo, hi):
        print(f"  +0x{d:04x}  {m} {t}")


if __name__ == "__main__":
    main()
