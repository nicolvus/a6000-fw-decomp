#!/usr/bin/env python3
"""Matriz de registros por modo del IMX235 (A7S 3.20 av-cam, base 0x43541000), según el aplicador
vtable+0xa0 = 0x436f3928: columna = remap[índice]; filas de 20 B {u32 ptr campo, 16 B valor por columna}.
Uso: imx235_modes.py av-cam.bin > out/a7s-imx235-setmode-matrix.json"""
import json, struct, sys
B = 0x43541000
d = open(sys.argv[1], 'rb').read()
u32 = lambda a: struct.unpack_from('<I', d, a - B)[0]
u16 = lambda a: struct.unpack_from('<H', d, a - B)[0]
remap = u32(0x436f3964) + 0x436f392c + 4
got = u32(0x436f3968) + 0x436f392e + 4
modes = list(struct.unpack_from('<34I', d, 0x43fee370 - B))
def rows(slot_off):
    t = u32(got + slot_off); out = []
    while (p := u32(t + 20 * len(out))):
        r = t + 20 * len(out)
        out.append({"ptr": hex(p), "reg_u16_at_ptr_minus2": hex(u16(p - 2)), "init": d[p - B],
                    "cols": list(d[r + 4 - B:r + 20 - B])})
    return hex(t), out
col = list(d[remap - B:remap - B + 34])
t1, r1 = rows(u32(0x436f396c)); t2, r2 = rows(u32(0x436f3970))
assert len(col) == 34 and max(col) < 16
json.dump({"modes": [hex(m) for m in modes], "mode_to_col": col, "remap": hex(remap), "got": hex(got),
           "table_main": t1, "rows_main": r1, "table_alt": t2, "rows_alt": r2}, sys.stdout, indent=1)
