import struct
from pathlib import Path
BASE = 0x43541000
a = Path('/tmp/avc/avcam_321.bin').read_bytes()
b = Path('/tmp/avc/avcam_pp.bin').read_bytes()


def zero_runs(d, lo, hi, minlen=256):
    out, i = [], lo
    while i < hi:
        if d[i] == 0:
            j = i
            while j < hi and d[j] == 0: j += 1
            if j - i >= minlen: out.append((i, j))
            i = j
        else:
            i += 1
    return out


print('tramos cero >=256 B en 3.21 desde 0x9E0000:')
for s, e in zero_runs(a, 0x9E0000, len(a)):
    print(f'  0x{BASE+s:08X}..0x{BASE+e-1:08X}  ({e-s} B)')
print('\ntramos cero en la imagen completa >=1024 B:')
for s, e in zero_runs(a, 0, len(a), 1024):
    print(f'  0x{BASE+s:08X}..0x{BASE+e-1:08X}  ({e-s} B)')
print('\ncabecera LIRO:')
for i in range(0, 0x60, 16):
    w = [struct.unpack_from('<I', a, i + k)[0] for k in (0, 4, 8, 12)]
    print(f'  {BASE+i:08x}  {a[i:i+16].hex()}  ' + ' '.join(f'{x:08x}' for x in w))
