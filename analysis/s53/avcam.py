"""Desensamblado Thumb de solo lectura de av-cam.bin (base 0x43541000)."""
import sys
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[2]
P = {'a7s': 'a7s-fw320/payload', 'a6000': 'fw321'}
BASE = 0x43541000


def load(m):
    return (ROOT / f'firmware/extracted/{P[m]}/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin').read_bytes()


md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
if __name__ == '__main__':
    d = load(sys.argv[1]); a = int(sys.argv[2], 16); n = int(sys.argv[3])
    for i in md.disasm(d[a - BASE:a - BASE + n * 4], a):
        print(f'{i.address:x}  {i.mnemonic:<8} {i.op_str}'); n -= 1
        if n <= 0: break
