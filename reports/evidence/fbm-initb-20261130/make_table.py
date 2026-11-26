"""Vuelca la tabla (userID, mediaID) -> fileType/OM de 0x9D23FC y los tamanos de 0x9D2794.
Uso: python3 make_table.py  (desde la raiz del repo)"""
import importlib.util, struct

spec = importlib.util.spec_from_file_location("eh", "/tmp/elfhelper.py")
eh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eh)
e = eh.Elf('analysis/camera-extract/usr/lib/libmpr.so')

print("tabla (userID, mediaID) -> fileType/OM en 0x9D23FC, 37 entradas de 0x18 B + terminador fileType=0xFFFFFFFF")
print("+0 userID  +4 mediaID  +8 fileType  +0xC OM  +0x10 fn  +0x14 arg")
base = 0x9D23FC
for i in range(40):
    b = e.read(base + i * 0x18, 0x18)
    uid, mid, ft = struct.unpack('<III', b[:12])
    om, fn, arg = struct.unpack('<III', b[12:24])
    print("%2d %#08x uid=%#04x mid=%d fileType=%#04x om=%-2d fn=%#x arg=%#x"
          % (i, base + i * 0x18, uid, mid, ft, om, fn, arg))
    if ft == 0xFFFFFFFF:
        break
print()
print("tamanos 0x9D2794 (16 B): fileType, flag, base, max -> bloques = ceil(x/0x20000) topado a 7")
for i in range(40):
    ft, flag, base_l, max_l = struct.unpack('<IIII', e.read(0x9D2794 + 16 * i, 16))
    if ft == 0xFFFFFFFF:
        break
    print("%#06x flag=%#x base=%#08x max=%#08x base_blk=%d max_blk=%d"
          % (ft, flag, base_l, max_l,
             min(7, (base_l + 0x1FFFF) // 0x20000), min(7, (max_l + 0x1FFFF) // 0x20000)))
