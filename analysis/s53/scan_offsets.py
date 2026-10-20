"""Barrido Thumb lineal (capstone, skipdata) de cargas/almacenes byte con un desplazamiento dado."""
import re
import sys

from dz import BASE, _md, rom

name, disp = sys.argv[1], int(sys.argv[2], 16)
d = rom(name)
_md.skipdata = True
pat = re.compile(rf'\[r\d+, #0x{disp:x}\]')
for i in _md.disasm(d, BASE):
    if i.mnemonic.startswith(('ldrb', 'strb')) and pat.search(i.op_str):
        print(f'{i.address:06x} {i.mnemonic} {i.op_str}')
