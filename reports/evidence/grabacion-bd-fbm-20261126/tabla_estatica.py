#!/usr/bin/env python3
"""Volcado de la tabla estática 0x9D23FC de libmpr.so (37 filas de 0x18 B)."""
import sys

sys.path.insert(0, "reports/evidence/fbm-sector31-consola-20261126/evidencia")
import mprdis as M

print("# tabla estatica de 0x9D23FC (libmpr.so, .data): 37 filas de 0x18 B + terminador")
print("# {u32 userID, u32 mediaID, u32 fileType, u32 OM, void* fn, void* arg}")
print("# idx  bytes(userID mediaID fileType OM)  fn        arg")
for i in range(38):
    a = 0x9D23FC + i * 0x18
    uid, mid, ft, om, fn, arg = [M.rd32(a + j) for j in (0, 4, 8, 0xC, 0x10, 0x14)]
    print(f"[{i:2}] {M.rd(a, 0x10).hex()}  fn={fn:#010x} arg={arg:#010x}")
    if ft == 0xFFFFFFFF:
        break
