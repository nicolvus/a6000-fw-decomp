"""Referencias a cadenas del ELF av-cam (ldr rX,[pc,#i] + add rX,pc, y ldr.w literal). Uso: python3 -I scripts/string_xrefs.py 0x43c9b335 [...]"""
import struct
import sys

BASE, OFF = 0x43541000, 0x1F0


def xrefs(d: bytes, targets: set[int]) -> dict[int, list[int]]:
    h = memoryview(d)[OFF:OFF + (len(d) - OFF) // 2 * 2].cast("H")
    out: dict[int, list[int]] = {t: [] for t in targets}
    for i in range(len(h) - 8):
        a = h[i]
        reg = lit = None
        if a & 0xF800 == 0x4800:  # ldr rt,[pc,#imm8*4]
            reg, lit, size = (a >> 8) & 7, ((BASE + 2 * i + 4) & ~3) + (a & 0xFF) * 4, 1
        elif a == 0xF8DF and (h[i + 1] >> 12) < 8:  # ldr.w rt,[pc,#imm12]
            imm = h[i + 1] & 0xFFF
            reg, lit, size = h[i + 1] >> 12, ((BASE + 2 * i + 4) & ~3) + imm, 2
        if reg is None or not BASE <= lit < BASE + len(d) - OFF - 4:
            continue
        w = struct.unpack_from("<I", d, lit - BASE + OFF)[0]
        for j in range(i + size, i + size + 8):
            if h[j] & 0xFF78 == 0x4478 and (h[j] & 7 | (h[j] >> 4) & 8) == reg:  # add rd,pc
                v = (w + BASE + 2 * j + 4) & 0xFFFFFFFF
                if v in out:
                    out[v].append(BASE + 2 * i)
    return out


if __name__ == "__main__":
    with open("analysis/av-cam-analysis-view.elf", "rb") as f:
        data = f.read()
    for t, r in xrefs(data, {int(x, 0) for x in sys.argv[1:]}).items():
        print(hex(t), [hex(x) for x in r])
