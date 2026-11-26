import struct
from pathlib import Path
BASE = 0x43541000
a = Path('/tmp/avc/avcam_321.bin').read_bytes()
REGS = [(0x43FAF28C, 0x43FB8EE0, 'hueco G18 (curvas+cuevas)'), (0x43D620D9, 0x43FA8F00, 'hueco grande 2.38 MB'),
        (0x44001404, 0x44001500, 'tabla de punteros de curva'), (0x43CB56E6, 0x43CB5700, 'tabla selector->gamma')]
for lo, hi, name in REGS:
    hits = []
    for off in range(0, len(a) - 4, 2):
        v = struct.unpack_from('<I', a, off)[0]
        if lo <= v < hi:
            hits.append((BASE + off, v))
    # también medias palabras (movw/movt)
    print(f'{name}: {lo:08x}..{hi:08x}  referencias de 32 bits alineadas a 2: {len(hits)}')
    for x in hits[:12]:
        print(f'   en {x[0]:08x} -> {x[1]:08x}')
