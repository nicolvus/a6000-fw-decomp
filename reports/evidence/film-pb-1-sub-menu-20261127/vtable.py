#!/usr/bin/env python3
"""Localiza typeinfo/vtable de una clase por el nombre RTTI y lista sus ranuras (VA ELF)."""
import struct, sys, subprocess
sys.path.insert(0, '/tmp')
from elfhelper import Elf

BASE = ('firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/'
        'nflasha15_unpacked_unpacked/')


def relocs(e):
    addr, off, size = e.sec['.rel.dyn']
    sym_off, str_off = e.sec['.dynsym'][1], e.sec['.dynstr'][1]
    out = []
    for i in range(0, size, 8):
        r_off, r_info = struct.unpack_from('<II', e.d, off + i)
        si, typ = r_info >> 8, r_info & 0xff
        st = struct.unpack_from('<I', e.d, sym_off + 16 * si)[0]
        nm = e.d[str_off + st:e.d.index(b'\0', str_off + st)].decode('latin1')
        out.append((r_off, typ, r_info >> 8, nm))
    return out


def main(lib, name_substr):
    e = Elf(lib)
    rel = relocs(e)
    # localizar la cadena RTTI
    va = None
    for v, s in e.strings(name_substr):
        print('nombre RTTI %r en %#x' % (s, v))
        va = v
        break
    if va is None:
        return
    cells = [o for o, t, si, nm in rel if t == 23 and struct.unpack('<I', e.read(o, 4))[0] == va]
    for ti_name_cell in cells:
        ti = ti_name_cell - 4
        print('typeinfo %#x (name ptr @%#x)' % (ti, ti_name_cell))
        for o, t, si, nm in rel:
            if t == 23 and o in (ti - 4, ti) or (t == 23 and struct.unpack('<I', e.read(o, 4))[0] == ti):
                pass
        vt_cells = [o for o, t, si, nm in rel if t == 23 and struct.unpack('<I', e.read(o, 4))[0] == ti]
        for o in vt_cells:
            print('  vptr apunta a typeinfo desde %#x -> vtable en %#x' % (o, o + 4))
            base = o + 4
            for k in range(60):
                cell = base + 4 * k
                r = [x for x in rel if x[0] == cell]
                val = struct.unpack('<I', e.read(cell, 4))[0]
                if r:
                    t2, si2, nm2 = r[0][1], r[0][2], r[0][3]
                    print('    [%02d] %#010x %s' % (k, val, nm2 if t2 == 2 else '(RELATIVE)'))
                else:
                    if val == 0:
                        break
                    print('    [%02d] %#010x raw' % (k, val))


if __name__ == '__main__':
    main(sys.argv[1] or BASE + 'lib/viewUnified2.so', sys.argv[2])
