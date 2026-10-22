"""S205 — Análisis de bytes: quién escribe S[0] (selector de fila IMX210) y origen de
G+0x224 (bloque de modo). Sustituye a REA/Ghidra mientras el autoanálisis no termina.

Estructura S = 0x43eb35d0 (0x148 B). S[0] = selector de fila (offset 0).
G+0x224 = 0x43eb07fc (origen de filas de 16 B).
Regiones auditadas: C_Imager 0x436d5000-0x436daa00, pipeline 0x4383a000-0x4383d000,
staging 0x43843a38-0x43843a80.
"""
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
A6000 = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000
d = A6000.read_bytes()

S_ADDR = 0x43eb35d0   # estructura S
G_MODES = 0x43eb07fc  # G+0x224

def u32(a): return struct.unpack_from('<I', d, a - B)[0]
def u16(a): return struct.unpack_from('<H', d, a - B)[0]

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail = False; md.skipdata = True

def disasm_range(start, end):
    return [i for i in md.disasm(d[start - B:end - B], start)]

def literal_target(i):
    """Resuelve ldr rx, [pc, #imm] a la dirección absoluta del literal."""
    m = __import__('re').match(r'(r\d+), \[pc, #(-?0x[0-9a-f]+|-?\d+)\]$', i.op_str)
    if not m: return None
    la = ((i.address + 4) & ~3) + int(m.group(2), 0)
    if 0 <= la - B < len(d) - 4:
        return u32(la)
    return None

def find_stores_to(target, regions):
    """Busca instrucciones str*/str que escriban a `target` (absoluto o como literal)."""
    out = []
    for start, end in regions:
        for i in disasm_range(start, end):
            o = i.op_str
            if not i.mnemonic.startswith('str'): continue
            # strb/strh/str hacia [base, #offset] donde base se resolvió a target vía literal
            # o str hacia literal absoluto
            lit = literal_target(i)
            if lit == target:
                out.append({'addr': i.address, 'mnemonic': i.mnemonic, 'op': o,
                                'lit_target': hex(lit), 'note': 'str a literal absoluto'})
    return out

regions = [
    (0x436d5000, 0x436daa00),   # C_Imager (SetMode/SetExposure/SetRead/Execute)
    (0x4383a000, 0x4383d000),   # pipeline SetExposure/SetRead
    (0x43843a38, 0x43843a80),   # staging 0x43843a44
]

stores = find_stores_to(S_ADDR, regions)
print(f'Stores directos a S=0x{S_ADDR:x} como literal absoluto: {len(stores)}')
for s in stores:
    print(f"  {s['addr']:#x}: {s['mnemonic']} {s['op']}  ({s['note']})")

# Buscar ldr de slot GOT que apunte a S (slot = 0x4401f990 -> 0x43f72d02 es el state, no S)
# S se accede via GOT slot. Buscar literales == S_ADDR.
print(f'\nLiterales que apuntan a S=0x{S_ADDR:x}:')
for start, end in regions:
    for i in disasm_range(start, end):
        lit = literal_target(i)
        if lit == S_ADDR:
            print(f"  {i.address:#x}: {i.mnemonic} {i.op_str} -> literal {hex(lit)}")

# Buscar referencias a G+0x224 (0x43eb07fc) como literal
print(f'\nLiterales que apuntan a G+0x224=0x{G_MODES:x}:')
for start, end in regions:
    for i in disasm_range(start, end):
        lit = literal_target(i)
        if lit == G_MODES:
            print(f"  {i.address:#x}: {i.mnemonic} {i.op_str} -> literal {hex(lit)}")

# Desensamblar staging 0x43843a38-0x43843a80 para ver qué hace
print('\n=== Staging 0x43843a38-0x43843a80 ===')
for i in disasm_range(0x43843a38, 0x43843a80):
    print(f'{i.address:#x}: {i.mnemonic} {i.op_str}')

print('\n=== Código alrededor de 0x437b5b14 (pipeline AE, S141) ===')
for i in disasm_range(0x437b5b14, 0x437b5b80):
    print(f'{i.address:#x}: {i.mnemonic} {i.op_str}')
