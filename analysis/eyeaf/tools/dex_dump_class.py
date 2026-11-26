#!/usr/bin/env python3
"""Volcado minimo de una clase DEX (campos y metodos) desde un .odex/.dex de la camara.

Uso: dex_dump_class.py FICHERO 'Lcom/sony/scalar/meta/FaceInfo;'
Solo lectura estatica; no ejecuta nada del dispositivo.
"""
import struct, sys

path, want = sys.argv[1], sys.argv[2]
raw = open(path, 'rb').read()
off = raw.find(b'dex\n')
if off < 0:
    raise SystemExit('sin cabecera dex')
d = raw[off:]
(hdr) = struct.unpack_from('<8sI20sIIIIIIIIIIIIIIIIII', d, 0)
magic, checksum, sig = hdr[0], hdr[1], hdr[2]
fsize, hsize, endian = hdr[3], hdr[4], hdr[5]
link_size, link_off, map_off = hdr[6], hdr[7], hdr[8]
string_ids_size, string_ids_off = hdr[9], hdr[10]
type_ids_size, type_ids_off = hdr[11], hdr[12]
proto_ids_size, proto_ids_off = hdr[13], hdr[14]
field_ids_size, field_ids_off = hdr[15], hdr[16]
method_ids_size, method_ids_off = hdr[17], hdr[18]
class_defs_size, class_defs_off = hdr[19], hdr[20]

def u32(o): return struct.unpack_from('<I', d, o)[0]

def uleb(o):
    r = 0; s = 0
    while True:
        b = d[o]; o += 1
        r |= (b & 0x7f) << s
        if not b & 0x80: return r, o
        s += 7

def string(i):
    o = u32(string_ids_off + 4 * i)
    n, o = uleb(o)
    return d[o:o + n].decode('utf-8', 'replace')

def typ(i):
    return string(u32(type_ids_off + 4 * i))

for ci in range(class_defs_size):
    base = class_defs_off + 32 * ci
    class_idx, access, super_idx, ifaces, srcfile, annot, class_data_off, static_vals = struct.unpack_from('<IIIIIIII', d, base)
    name = typ(class_idx)
    if name != want: continue
    print('class', name, 'access=0x%x super=%s' % (access, typ(super_idx)))
    if class_data_off == 0:
        print('  (sin class_data)')
        continue
    o = class_data_off
    sf, o = uleb(o); inf, o = uleb(o); dm, o = uleb(o); vm, o = uleb(o)
    idx = 0
    for count, kind in ((sf, 'S'), (inf, 'I')):
        idx = 0
        for _ in range(count):
            diff, o = uleb(o); acc, o = uleb(o); idx += diff
            fid = idx
            fo = field_ids_off + 8 * fid
            cls, t, nm = struct.unpack_from('<HHI', d, fo)
            print('  field %-22s %-42s acc=0x%x' % (kind, typ(t) + ' ' + string(nm), acc))
    for count, kind in ((dm, 'D'), (vm, 'V')):
        idx = 0
        for _ in range(count):
            diff, o = uleb(o); acc, o = uleb(o); code_off, o = uleb(o)
            idx += diff
            mo = method_ids_off + 8 * idx
            cls, pr, nm = struct.unpack_from('<HHI', d, mo)
            po = proto_ids_off + 12 * pr
            shorty, ret, params = struct.unpack_from('<III', d, po)
            pofs = params
            pl = []
            if pofs:
                n = u32(pofs); pofs += 4
                for k in range(n):
                    pl.append(typ(struct.unpack_from('<H', d, pofs + 2 * k)[0]))
            print('  meth  %-3s %s(%s)%s acc=0x%x code=0x%x' % (kind, string(nm), ', '.join(pl), typ(ret), acc, code_off))

# ---- modo 2: buscar clases que declaren un campo (sys.argv[3] == '--field')
