"""Referencias a cadenas por el idioma del núcleo: ldr rX,[pc,#imm] + add rX, pc."""
import struct, sys, bisect
from pathlib import Path
BASE = 0x43541000
d = Path('/tmp/avc/avcam_321.bin').read_bytes()
N = len(d)
h = memoryview(d).cast('H')


def cstr(a, n=110):
    o = a - BASE
    if not (0 <= o < N): return None
    s = d[o:o+n].split(b'\0')[0]
    if len(s) >= 4 and all(32 <= c < 127 for c in s): return s.decode()
    return None


refs = []          # (addr_del_add, target, string)
for i in range(N // 2 - 2):
    v = h[i]
    if 0x4478 <= v <= 0x447F:          # add rX, pc
        a = BASE + 2 * i
        rd = v & 7
        # buscar hacia atrás el ldr rd,[pc,#imm] que carga el desplazamiento
        for k in range(1, 5):
            w = h[i - k]
            if (w & 0xF800) == 0x4800 and ((w >> 8) & 7) == rd:
                la = BASE + 2 * (i - k)
                lit = ((la + 4) & ~3) + (w & 0xFF) * 4
                val = struct.unpack('<I', d[lit - BASE:lit - BASE + 4])[0]
                for t in ((val + a + 4) & 0xFFFFFFFF, (val - a - 4) & 0xFFFFFFFF):
                    s = cstr(t)
                    if s:
                        refs.append((a, t, s)); break
                break

print('referencias a cadenas:', len(refs), file=sys.stderr)
# volcar: cadenas que interesan
pat = sys.argv[1] if len(sys.argv) > 1 else '.'
import re
p = re.compile(pat, re.I)
seen = set()
for a, t, s in refs:
    if p.search(s) and (t, s) not in seen:
        seen.add((t, s))
        print(f'{a:08x} -> {t:08x}  "{s[:95]}"')
