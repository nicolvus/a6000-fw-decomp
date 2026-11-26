#!/usr/bin/env python3
"""Vuelca un rango de .data de un ELF anotando relocaciones (símbolo + addendo). Solo lectura."""
import struct, sys
sys.path.insert(0, '/tmp')
from elfhelper import Elf

def reloc_map(e):
    addr, off, size = e.sec['.rel.dyn']
    sym_off = e.sec['.dynsym'][1]
    str_off = e.sec['.dynstr'][1]
    out = {}
    for i in range(0, size, 8):
        r_off, r_info = struct.unpack_from('<II', e.d, off + i)
        si, typ = r_info >> 8, r_info & 0xff
        st_name, value, sz, info, other, shndx = struct.unpack_from('<IIIBBH', e.d, sym_off + 16 * si)
        name = e.d[str_off + st_name:e.d.index(b'\0', str_off + st_name)].decode('latin1')
        out[r_off] = (name, typ, value)
    return out

def main(path, lo, hi):
    e = Elf(path)
    rel = reloc_map(e)
    for va in range(lo, hi, 4):
        raw = e.read(va, 4)
        w = struct.unpack('<I', raw)[0] if len(raw) == 4 else 0
        note = ''
        if va in rel:
            n, t, v = rel[va]
            note = f'  REL{t} {n}'
            if t == 23 and w:
                note += f' -> {w:#x}'
        print(f'{va:#08x}: {raw.hex()}  {w:#010x}{note}')

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16))
