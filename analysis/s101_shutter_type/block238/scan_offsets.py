import re
from pathlib import Path

from capstone import *

b=Path('analysis/rea-independent/input/av-cam.bin').read_bytes(); base=0x43541000
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB); md.skipdata=True
for i in md.disasm(b[:0x9c0000],base):
    if re.search(r'#0x(238|280)\]',i.op_str) and i.mnemonic.startswith(('ldr','str')): print(hex(i.address),i.mnemonic,i.op_str)
