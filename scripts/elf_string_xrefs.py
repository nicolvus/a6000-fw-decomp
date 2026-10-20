"""Referencias PC-relativas Thumb (ldr rX,[pc]; add rX,pc) a cadenas de un .so ARM con VA==offset en .text/.rodata.
Uso: python3 -I scripts/elf_string_xrefs.py lib.so 'regex'   (imprime cadena, VA y llamantes; VA ELF, Ghidra = +0x10000)"""
import re
import struct
import sys


def sections(b):
    shoff = struct.unpack_from("<I", b, 0x20)[0]
    ent, num, strx = struct.unpack_from("<HHH", b, 0x2E)
    secs = [struct.unpack_from("<10I", b, shoff + i * ent) for i in range(num)]
    st = secs[strx][4]
    return {b[st + s[0]:b.index(b"\0", st + s[0])].decode(): s for s in secs}


def xrefs(b, targets):
    t = sections(b)[".text"]
    va, off, size = t[3], t[4], t[5]
    h = memoryview(b)[off:off + size // 2 * 2].cast("H")
    out = {x: [] for x in targets}
    for i in range(len(h) - 10):
        a = h[i]
        if a & 0xF800 == 0x4800:
            reg, lit, n = (a >> 8) & 7, ((va + 2 * i + 4) & ~3) + (a & 0xFF) * 4, 1
        elif a == 0xF8DF and (h[i + 1] >> 12) < 8:
            reg, lit, n = h[i + 1] >> 12, ((va + 2 * i + 4) & ~3) + (h[i + 1] & 0xFFF), 2
        else:
            continue
        if not 0 <= lit < len(b) - 4:
            continue
        w = struct.unpack_from("<I", b, lit)[0]
        for j in range(i + n, i + n + 8):
            if h[j] & 0xFF78 == 0x4478 and (h[j] & 7 | (h[j] >> 4) & 8) == reg:
                v = (w + va + 2 * j + 4) & 0xFFFFFFFF
                if v in out:
                    out[v].append(va + 2 * i)
    return out


if __name__ == "__main__":
    b = open(sys.argv[1], "rb").read()
    rx = re.compile(sys.argv[2].encode())
    found = {m.start(): m.group() for m in re.finditer(rb"[\x20-\x7e]{6,}", b) if rx.search(m.group())}
    x = xrefs(b, set(found))
    for a, s in found.items():
        print(hex(a), s[:100].decode(), [hex(c) for c in x[a]])
