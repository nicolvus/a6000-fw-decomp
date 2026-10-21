"""S62: buscador robusto de referencias PIC `add rX, pc` a cadenas (barrido de bytes, sin Capstone).

Para cada candidato `add rd, pc` (encoding Thumb 0x44xx, bits[6:4]=111, bit3=1) calcula
el literal necesario (T - (A+4)) y busca esa palabra 4-alineada hasta 64 B hacia atrás
o 16 B hacia adelante (pool de literales). Uso: pic_refs.py A6000|A7S T1 T2...
"""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s58"))
from tdis import data, B  # noqa: E402


def pic_refs(model, targets, lo=None, hi=None):
    """Barrido byte-level con emparejamiento disciplinado: mantiene el último
    `ldr rt,[pc,#imm]` (T1 0x48xx o T2 F8DF) por registro; cada `add rd,pc` consume
    ese literal y produce el destino t = lit + A + 4."""
    d = data(model)
    lo = ((lo or B) - B) & ~1
    hi = (hi or B + len(d)) - B
    out = {t: [] for t in targets}
    tset = set(targets)
    last = {}   # reg -> valor (offset PIC) conocido
    for i in range(lo, hi - 3, 2):
        h = struct.unpack_from('<H', d, i)[0]
        h2v = struct.unpack_from('<H', d, i + 2)[0]
        if (h & 0xF800) == 0x4800:                      # ldr rt,[pc,#imm8*4]
            rt = (h >> 8) & 7
            la = (((B + i + 4) & ~3) - B) + (h & 0xFF) * 4
            if 0 <= la <= hi - 4:
                last[rt] = struct.unpack_from('<I', d, la)[0]
            continue
        if h == 0xF8DF:                                 # ldr.w rt,[pc,#imm12]
            rt = h2v >> 12
            la = (((B + i + 4) & ~3) - B) + (h2v & 0xFFF)
            if 0 <= la <= hi - 4:
                last[rt] = struct.unpack_from('<I', d, la)[0]
            continue
        if (h & 0xFF00) == 0x4600:                      # mov rd, rs (alta)
            rd = (h & 7) | ((h >> 4) & 8)
            rs = (h >> 3) & 0xF
            if rs in last:
                last[rd] = last[rs]
            else:
                last.pop(rd, None)
            continue
        if (h & 0xFFC0) == 0x0000:                      # movs rd, rs (lsl #0)
            rd, rs = h & 7, (h >> 3) & 7
            if rs in last:
                last[rd] = last[rs]
            else:
                last.pop(rd, None)
            continue
        if (h & 0xFF00) == 0x4400 and (h & 0x78) == 0x78:
            rd = (h & 7) | ((h >> 4) & 8)               # add rd, pc (consume)
            lit = last.pop(rd, None)
            if lit is not None:
                t = (lit + B + i + 4) & 0xffffffff
                if t in tset:
                    out[t].append(B + i)
            continue
        if (h & 0xFF00) == 0x4400:                      # add rd, rs (alta, sin pc)
            rd = (h & 7) | ((h >> 4) & 8)
            rs = (h >> 3) & 0xF
            if rs in last and rd in last:
                last[rd] = (last[rd] + last[rs]) & 0xffffffff
            continue
    return out


if __name__ == "__main__":
    model = sys.argv[1]
    targets = [int(x, 0) for x in sys.argv[2:]]
    for t, refs in pic_refs(model, targets).items():
        print(hex(t), [hex(r) for r in refs])
