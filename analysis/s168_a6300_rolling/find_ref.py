#!/usr/bin/env python3
"""S170 — busca la referencia a una cadena en el A6300 fw2.01 por el metodo inverso.

El pool de literales guarda el desplazamiento RELATIVO:

    destino = W + (direccion_del_add + 4)   =>   add_addr = destino - W - 4

Recorremos todos los pool-candidatos W (palabras de 4 B alineadas) y comprobamos si la
direccion resultante es realmente un `add rD, pc` (Thumb T1) y si el `ldr` que lo
precede pertenece al mismo registro. Es una comprobacion INDEPENDIENTE del escaner
`scan_refs.py` (que recorre el codigo y empareja hacia atras).

Uso: find_ref.py <blob> <base> <dest_vaddr_hex>
"""
import struct
import sys

blob = sys.argv[1]
BASE = int(sys.argv[2], 16)
DEST = int(sys.argv[3], 16)
B = open(blob, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def is_add_rd_pc(a):
    """(reg, size) si en `a` hay un `add rD, pc` (T1 o T3)."""
    o = a - BASE
    if o < 0 or o + 4 > N:
        return None
    h = U16(B, o)[0]
    if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
        return (((h >> 7) & 1) << 3) | (h & 7), 2
    h2 = U16(B, o + 2)[0]
    if (h2 & 0xFFF0) == 0xEB10 and ((h2 >> 12) & 0xF) == 15:
        return ((h2 >> 12) & 0xF), 4
    return None


def ldr_reg_before(a, reg):
    """(addr_ldr, valor_pool) del `ldr reg,[pc,#imm]` mas cercano por detras (<=4 KB)."""
    best = None
    p = a - 2
    limit = a - 4096
    while p >= limit and p >= BASE:
        o = p - BASE
        h = U16(B, o)[0]
        if (h & 0xF800) == 0x4800 and ((h >> 8) & 7) == reg:
            lit = ((p + 4) & ~3) + ((h & 0xFF) * 4)
            lo = lit - BASE
            if 0 <= lo <= N - 4:
                return p, U32(B, lo)[0], lit
            return None
        if (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            if ((h2 >> 12) & 0xF) == reg:
                lit = ((p + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
                lo = lit - BASE
                if 0 <= lo <= N - 4:
                    return p, U32(B, lo)[0], lit
                return None
        p -= 2
    return best


found = []
for (w,) in struct.iter_unpack("<I", B[: (N // 4) * 4]):
    add_addr = DEST - w - 4
    if not (BASE <= add_addr < BASE + N):
        continue
    if add_addr & 1:
        continue
    r = is_add_rd_pc(add_addr)
    if r is None:
        continue
    reg, _ = r
    lr = ldr_reg_before(add_addr, reg)
    if lr is None:
        continue
    ldr_a, val, pool = lr
    if val != w:
        continue
    found.append((add_addr, ldr_a, pool, w))

print(f"destino 0x{DEST:08x}: {len(found)} referencia(s)")
for (add_a, ldr_a, pool, w) in sorted(found):
    print(f"  ldr 0x{ldr_a:08x} (pool 0x{pool:08x} = 0x{w:08x})  add 0x{add_a:08x}")
