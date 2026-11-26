import struct

f = '/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/analysis/camera-extract/usr/lib/libmpr.so'
d = open(f, 'rb').read()
VA = 0x9D23FC
# localizar el segmento que contiene la VA
e_phoff = struct.unpack_from('<I', d, 28)[0]
e_phentsize = struct.unpack_from('<H', d, 42)[0]
e_phnum = struct.unpack_from('<H', d, 44)[0]
base = None
for i in range(e_phnum):
    o = e_phoff + i * e_phentsize
    t, off, va, pa, fsz, msz, fl, al = struct.unpack_from('<8I', d, o)
    if t == 1 and va <= VA < va + fsz:
        base = off + (VA - va)
        break
assert base is not None
print('offset en fichero 0x%x' % base)
print('fila userID mediaID sector  OM   func        dato')
for i in range(40):
    u, m, s, om, fn, dat = struct.unpack_from('<6I', d, base + i * 0x18)
    if u == 0 and m == 0 and s == 0 and om == 0:
        print('terminador en fila', i)
        break
    print('%3d  0x%02x    %d     0x%02x   0x%02x  0x%08x  0x%08x' % (i, u, m, s, om, fn, dat))
