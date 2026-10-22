"""S205 — Análisis de bytes profundo: slots GOT que apuntan a S (0x43eb35d0) y su uso.
Busca escritores de campos de la estructura S (incluido S[0] selector de fila).
"""
import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
A6000 = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000
d = A6000.read_bytes()

S_ADDR = 0x43eb35d0
GOT_START, GOT_END = 0x44010000, 0x44020000  # región de GOT/slots globales

def u32(a): return struct.unpack_from('<I', d, a - B)[0]

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail = False; md.skipdata = True

# 1. Encontrar slots GOT con valor S_ADDR
got_slots = []
a = GOT_START
while a < GOT_END:
    v = u32(d, a)
    if v == S_ADDR:
        got_slots.append(a)
    a += 4

print(f'Slots GOT con valor S=0x{S_ADDR:x}: {len(got_slots)}')
for s in got_slots:
    print(f'  slot 0x{s:08x} -> 0x{S_ADDR:x}')

# 2. Para cada slot GOT de S, buscar ldr [pc,#imm] que cargue ese slot en regiones de código
def literal_target(i):
    m = re.match(r'(r\d+), \[pc, #(-?0x[0-9a-f]+|-?\d+)\]$', i.op_str)
    if not m: return None
    la = ((i.address + 4) & ~3) + int(m.group(2), 0)
    if 0 <= la - B < len(d) - 4:
        return u32(la)
    return None

regions = [
    (0x436d5000, 0x436daa00),   # C_Imager
    (0x4383a000, 0x4383d000),   # pipeline
    (0x43843a38, 0x43843c00),   # staging extendido
    (0x437b5000, 0x437b6000),   # S init/memset (S142)
]

print('\nUsos de slots GOT de S en código:')
for slot in got_slots:
    for start, end in regions:
        for i in md.disasm(d[start - B:end - B], start):
            lit = literal_target(i)
            if lit == slot:
                print(f'  {i.address:#x}: {i.mnemonic} {i.op_str}  -> slot 0x{slot:08x} (S)')

# 3. Desensamblar staging completo 0x43843a44 hasta el pop/bx lr
print('\n=== Staging 0x43843a44-0x43843d00 (hasta literal pool) ===')
for i in md.disasm(d[0x43843a44 - B:0x43843d00 - B], 0x43843a44):
    print(f'{i.address:#x}: {i.mnemonic} {i.op_str}')
    if i.mnemonic in ('bx lr', 'pop') and 'pc' in i.op_str:
        break
