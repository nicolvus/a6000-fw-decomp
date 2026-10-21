"""S71-6/7: llamadores de Backup_read (wrapper 0x435613b0) con ID 0x3e0005; llamadores de 0x43789cc0; referencias al ID 0x301d7."""
import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

b = Path('analysis/rea-independent/input/av-cam.bin').read_bytes(); base = 0x43541000
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.skipdata = True
ins = list(md.disasm(b[:0x9c0000], base))
pool = {base+o: struct.unpack_from('<I', b, o)[0] for o in range(0, len(b)-3, 4)}
def lit(i):
    m = re.match(r'(r\d+), \[pc, #(0x[0-9a-f]+)\]$', i.op_str)
    return (m.group(1), pool.get(((i.address+4) & ~3)+int(m.group(2), 16))) if m and i.mnemonic.startswith('ldr') else None
print('-- Backup_read(0x435613b0): ID inmediato/literal en r0 previo')
ids = {}
for k, i in enumerate(ins):
    if i.mnemonic == 'bl' and i.op_str == '#0x435613b0':
        v = None
        for x in reversed(ins[max(0, k-8):k]):
            if re.match(r'r0,', x.op_str):
                l = lit(x)
                m = re.match(r'r0, #(0x[0-9a-f]+|\d+)$', x.op_str)
                v = l[1] if l else int(m.group(1), 0) if m else None
                break
        ids.setdefault(v, []).append(hex(i.address))
for v, a in sorted(ids.items(), key=lambda t: str(t[0])): print(hex(v) if v is not None else None, len(a), a[:6])
print('-- llamadores de 0x43789cc0:', [hex(i.address) for i in ins if i.mnemonic in ('bl', 'b.w') and i.op_str == '#0x43789cc0'])
print('-- literales 0x301d7 / 0x3e0005 en pools:', [hex(a) for a, v in pool.items() if v in (0x301d7, 0x3e0005)])
