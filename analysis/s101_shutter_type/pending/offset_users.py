"""Todos los ldr/str/add/movw con inmediato en [lo,hi) (barrido global, Thumb lineal).
Uso: offset_users.py lo hi [mnemonicos-prefijo,...]"""
import os
import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

b = Path(os.environ.get('AVCAM', 'analysis/rea-independent/input/av-cam.bin')).read_bytes(); base = int(os.environ.get('BASE', '0x43541000'), 16)
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.skipdata = True
lo, hi = int(sys.argv[1], 16), int(sys.argv[2], 16)
pref = tuple(sys.argv[3].split(',')) if len(sys.argv) > 3 else ('ldr', 'str', 'add', 'movw', 'mov')
for i in md.disasm(b[:0x9c0000], base):
    if not i.mnemonic.startswith(pref): continue
    for imm in re.findall(r'#(0x[0-9a-f]+)', i.op_str):
        if lo <= int(imm, 16) < hi: print(hex(i.address), i.mnemonic, i.op_str); break
