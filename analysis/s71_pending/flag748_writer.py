"""S71-3: escritor de captura+0x748 (A7S) vs +0x740 (A6000). Imprime contexto desensamblado de ambos."""
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

A7 = 'firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
def ctx(path, addr, before=0x30, after=0x14, base=0x43541000):
    b = Path(path).read_bytes(); md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    return [f'{i.address:x}: {i.mnemonic} {i.op_str}' for i in md.disasm(b[addr-before-base:addr+after-base], addr-before)]
print('A7S'); print('\n'.join(ctx(A7, 0x4389efc2)))
print('A6000'); print('\n'.join(ctx('analysis/rea-independent/input/av-cam.bin', 0x438acc24)))
