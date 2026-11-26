#!/usr/bin/env python3
"""Extrae las tablas (const char* nombre, u32 id) de libScalarDaemon.so de A6000 y A6300.
Salida: analysis/eyeaf/data/diff/scalar_param_table.json  (solo estático)."""
import json, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from elfmap import ELF

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..'))
LIBS = {'A6000': 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libScalarDaemon.so',
        'A6300': 'firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libScalarDaemon.so'}
ANCHOR = 'PARAMID_CAMSETTING_EYE_START_AF'
out = {}
for tag, rel in LIBS.items():
    e = ELF(os.path.join(ROOT, rel)); d = e.data
    anchor = None
    for o in e.find_str(ANCHOR):
        va = e.off2va(o); pat = struct.pack('<I', va); k = 0
        while True:
            j = d.find(pat, k)
            if j < 0: break
            anchor = j; k = j + 1
    def entry(k):
        v, q = struct.unpack_from('<II', d, k)
        t = e.va2off(v)
        if t is None: return None
        end = d.find(b'\0', t)
        if end < 0 or not (4 <= end - t <= 96) or q > 0xffff: return None
        try: s = d[t:end].decode('ascii')
        except Exception: return None
        return (s, q) if s.isprintable() and s else None
    s_ = anchor
    while entry(s_ - 8): s_ -= 8
    seq = []
    k = s_
    while entry(k):
        seq.append(entry(k)); k += 8
    out[tag] = seq
    print(f'{tag}: {len(seq)} entradas en {s_:#x}..{k:#x}; {ANCHOR} -> {dict(seq).get(ANCHOR, 0):#06x}')
a, b = dict(out['A6000']), dict(out['A6300'])
common = set(a) & set(b)
print(f'comunes {len(common)}, con id distinto {sum(1 for n in common if a[n] != b[n])}')
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scalar_param_table.json'), 'w'), indent=1)
