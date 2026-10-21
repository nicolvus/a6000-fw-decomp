"""S71-1: de dónde sale cada byte de dst+0xdd0..0xde7 en el constructor 0x437b1048 (pares ldrb -> strb)."""
import re
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
b = open('analysis/rea-independent/input/av-cam.bin', 'rb').read(); base = 0x43541000
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
src = {}
prev = None
for i in md.disasm(b[0x437b1048-base:0x437b2400-base], 0x437b1048):
    m = re.match(r'(\w+), \[(\w+)(?:, #(0x[0-9a-f]+))?\]$', i.op_str)
    if i.mnemonic.startswith('ldrb') and m: prev = (m.group(1), f'{m.group(2)}+{m.group(3) or "0"}', i.address)
    elif i.mnemonic.startswith('strb') and m and m.group(2) == 'r4' and m.group(3):
        o = int(m.group(3), 16)
        if 0xdd0 <= o < 0xde8:
            src[o] = prev[1] if prev and prev[0] == m.group(1) else '?'
for o in sorted(src): print(hex(o), src[o])
