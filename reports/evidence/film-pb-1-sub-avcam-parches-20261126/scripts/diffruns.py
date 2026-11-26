import hashlib
from pathlib import Path

BASE = 0x43541000
a = Path('/tmp/avc/avcam_321.bin').read_bytes()
b = Path('/tmp/avc/avcam_cfw.bin').read_bytes()
assert len(a) == len(b)
diff = [i for i in range(len(a)) if a[i] != b[i]]
print('bytes distintos:', len(diff), 'sha cfw', hashlib.sha256(b).hexdigest()[:16])

# exact runs (no gap tolerance)
runs = []
start = prev = diff[0]
for i in diff[1:]:
    if i == prev + 1:
        prev = i
        continue
    runs.append((start, prev))
    start = prev = i
runs.append((start, prev))
print('runs exactos:', len(runs))
tot_after_0xA00000 = 0
for s, e in runs:
    n = e - s + 1
    print(f'  0x{s:08X}..0x{e:08X}  ({n:5d} B)  VA 0x{BASE+s:08X}..0x{BASE+e:08X}  {"TABLA" if s >= 0xA00000 else "CODIGO/OTRO"}')
    if s >= 0xA00000:
        tot_after_0xA00000 += n
print('total en zona tablas >=0xA00000:', tot_after_0xA00000)
print('total codigo <0xA00000:', len(diff) - tot_after_0xA00000)
