#!/usr/bin/env python3
"""Barrido de tablas CmnViewMenuItemStruct (0x28 B) que referencian un recurso de texto."""
import struct, sys, json
sys.path.insert(0, '/tmp')
from elfhelper import Elf

UXC = ('firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/'
       'nflasha15_unpacked_unpacked/share/app/string_english.uxc')

def parse_uxc(d):
    assert d[:4] == b'uxc\x07'
    count = struct.unpack_from('<I', d, 0xc)[0] & 0x1fff
    base = 0x10 + 2 * count
    recs = {}
    for v in struct.unpack_from('<%dH' % count, d, 0x10):
        if v == 0xffff:
            continue
        off = base + 4 * v
        rid, = struct.unpack_from('<H', d, off)
        recs[rid] = d[off + 4:d.index(b'\0', off + 4)].decode('utf-8', 'replace')
    return recs

def main(lib, textids):
    texts = parse_uxc(open(UXC, 'rb').read())
    e = Elf(lib)
    out = []
    for tid in textids:
        pat = struct.pack('<I', 0x02040000 | tid)
        for va in e.xrefs(0x02040000 | tid):
            if va is None:
                continue
            # table cell offset: 0x0c mod 0x28
            off = (va - 0x0c) % 0x28
            start = va - 0x0c - off
            rows = []
            cur = start
            for i in range(64):
                w = e.read(cur, 0x28)
                if len(w) < 0x28:
                    break
                f = struct.unpack('<10I', w)
                txt = f[3]
                if txt >> 16 not in (0x204, 0x205, 0x206):
                    if i == 0:
                        break
                    # continuar solo si parece item con icono
                    break
                rows.append({'va': hex(cur + off), 'id': hex(f[2]), 'txt': hex(txt),
                             'str': texts.get(txt & 0xffff, '?'), 'icon': hex(f[4]),
                             'help': hex(f[5]), 'icon_help': hex(f[6]),
                             'flags': hex(f[7]), 'w8': hex(f[8]), 'w9': hex(f[9])})
                cur += 0x28
            out.append({'lib': lib, 'textid': hex(tid), 'cell': hex(va),
                        'table_start': hex(start - off), 'rows': rows})
    print(json.dumps(out, indent=1, ensure_ascii=False))

if __name__ == '__main__':
    main(sys.argv[1], [int(x, 0) for x in sys.argv[2:]])
