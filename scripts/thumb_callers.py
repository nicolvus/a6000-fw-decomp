"""Lista llamadores BL/BLX/B.W (Thumb-2) hacia un destino dentro del ELF de análisis av-cam.
Uso: python3 -I scripts/thumb_callers.py 0x436d62e4 [...]"""
import sys
BASE, OFF = 0x43541000, 0x1f0

def bl_targets(d):
    n = len(d) - OFF
    h = memoryview(d)[OFF:OFF + n - n % 2].cast("H")
    for i in range(len(h) - 1):
        a, b = h[i], h[i + 1]
        if a & 0xF800 == 0xF000 and b & 0x8000:   # BL / BLX / B.W (T4)
            kind = "bl" if b & 0x5000 == 0x5000 else "blx" if b & 0x5000 == 0x4000 else "b" if b & 0x5000 == 0x1000 else None
            if kind is None: continue
            s = (a >> 10) & 1; j1 = (b >> 13) & 1; j2 = (b >> 11) & 1
            i1 = ~(j1 ^ s) & 1; i2 = ~(j2 ^ s) & 1
            imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((a & 0x3FF) << 12) | ((b & 0x7FF) << 1)
            if s: imm -= 1 << 25
            pc = BASE + 2 * i + 4
            t = pc + imm
            if kind == "blx": t &= ~3
            yield BASE + 2 * i, t

if __name__ == "__main__":
    d = open("analysis/av-cam-analysis-view.elf", "rb").read()
    want = {int(x, 0) & ~1 for x in sys.argv[1:]}
    for a, t in bl_targets(d):
        if t in want: print(f"{a:#x} -> {t:#x}")
