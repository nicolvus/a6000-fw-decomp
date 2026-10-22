#!/usr/bin/env python3
"""S138 — verificación **a mano** de los 13 sitios PIC del módulo `[CAMERA_MAIN_FC]`.

Para cada sitio (dirección del `add rX,pc`) se:
  1. localiza el `ldr rX,[pc,#imm]` más cercano por detrás (mismo registro),
  2. lee el valor del pool de literales,
  3. calcula destino = pool + (dirección_del_add + 4),
  4. comprueba que el destino es el inicio de la cadena esperada (bytes reales).

Salida: fc_sites_verified.json
"""
import json
import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()

# (sitio add rX,pc, dirección de la cadena esperada)
SITES = [
    (0x437b7268, 0x43ca6944),
    (0x437b72a6, 0x43ca6944),
    (0x437b72ee, 0x43ca6944),
    (0x437b7326, 0x43ca6944),
    (0x437b7548, 0x43ca6980),
    (0x437b7570, 0x43ca69af),
    (0x437b77f4, 0x43ca69dc),
    (0x437b787c, 0x43ca6a0a),
    (0x437b7db6, 0x43ca6a3c),
    (0x437b7df6, 0x43ca6a3c),
    (0x437b7fae, 0x43ca6a66),
    (0x437b8200, 0x43ca6aa2),
    (0x437b820e, 0x43ca6aec),
]


def cstr(addr):
    o = addr - BASE
    e = B.find(b"\x00", o)
    return B[o:e].decode("latin1")


def decode_ldr(a):
    """(reg, literal_addr) del `ldr rX,[pc,#imm]` en la dirección a, o None."""
    o = a - BASE
    h = struct.unpack_from("<H", B, o)[0]
    if (h & 0xF800) == 0x4800:                    # T1: ldr rT,[pc,#imm5*4]
        reg = (h >> 8) & 7
        lit = ((a + 4) & ~3) + (h & 0xFF) * 4
        return reg, lit
    if (h & 0xFF7F) == 0xF85F:                    # T2: ldr.w rT,[pc,#imm12]
        h2 = struct.unpack_from("<H", B, o + 2)[0]
        reg = (h2 >> 12) & 0xF
        imm = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
        return reg, ((a + 4) & ~3) + imm
    return None


def decode_add(a):
    """registro destino del `add rX,pc` en la dirección a, o None."""
    h = struct.unpack_from("<H", B, a - BASE)[0]
    if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
        return (((h >> 7) & 1) << 3) | (h & 7)
    return None


def verify(site):
    """Devuelve (ok, ldr_addr, destino, texto) verificando el par ldr/add."""
    reg_add = decode_add(site)
    if reg_add is None:
        return (False, None, None, "el sitio no es un `add rX,pc`")
    # ldr más cercano por detrás con el mismo registro (regla estricta)
    best = None
    for a in range(site - 2, max(site - 0x1000, BASE), -2):
        d = decode_ldr(a)
        if d and d[0] == reg_add:
            best = (a, d[1])
            break
    if best is None:
        return (False, None, None, "sin `ldr` previo del mismo registro")
    ldr_a, lit = best
    pool = struct.unpack_from("<I", B, lit - BASE)[0]
    dest = (pool + site + 4) & 0xFFFFFFFF
    return (True, ldr_a, dest, cstr(dest))


def main():
    out = []
    for site, expected in SITES:
        ok, ldr_a, dest, txt = verify(site)
        row = {"site": f"0x{site:x}", "ldr": None if ldr_a is None else f"0x{ldr_a:x}",
               "dest": None if dest is None else f"0x{dest:x}",
               "text": txt, "expected": f"0x{expected:x}", "ok": bool(ok and dest == expected)}
        out.append(row)
        print(f"site 0x{site:x}  ldr {row['ldr']}  dest {row['dest']}  "
              f"{'OK ' if row['ok'] else 'FALLO'}  {txt[:70]!r}")
    n_ok = sum(1 for r in out if r["ok"])
    print(f"\n{n_ok}/{len(out)} sitios verificados a mano")
    json.dump(out, open(os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_sites_verified.json"),
                        "w"), indent=1)


if __name__ == "__main__":
    main()
