#!/usr/bin/env python3
"""S120 — barrido PIC *restringido* al código del módulo IDT.

Barre `analysis/s106_imaging_cap/scan_pic_refs_v2.py` (kill analysis) sobre el rango de
código del módulo (0x439d0000-0x43a00000) en lugar de todo el binario: mucho más rápido y
suficiente, porque las 165 funciones del módulo están todas en ese rango.
"""
import json
import os
import struct
import sys

BASE = 0x43541000
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
IDT_CODE = (0x439D0000, 0x43A00000)


def u16(b, a):
    return struct.unpack_from("<H", b, a - BASE)[0]


def u16o(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, a):
    return struct.unpack_from("<I", b, a - BASE)[0]


def u32o(b, o):
    return struct.unpack_from("<I", b, o)[0]


def string_starts(b, lo, hi):
    out = set()
    prev = False
    for i in range(max(0, lo - BASE), min(len(b), hi - BASE)):
        cur = 32 <= b[i] < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


def ldr_sites(b, lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > len(b) - 8:
            a += 2
            continue
        h = u16o(b, o)
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = u16o(b, o + 2)
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= len(b) - 4:
                out.append((a, reg, u32o(b, o2)))
        a += 2
    return out


def add_sites(b, lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > len(b) - 4:
            a += 2
            continue
        h = u16o(b, o)
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    return out


def _writes_to(ins, reg):
    """¿La instrucción deja el registro `reg` con un valor distinto al cargado?

    NOTA (S120): el `& 0xF` del script canónico `scan_pic_refs_v2.py` es **incorrecto**:
    en Capstone `ARM_REG_Rn == 66 + n`, así que `op.reg & 0xF` desplaza 2 bits y confunde
    r1 con r3, r2 con r4, etc.  Aquí se compara el **nombre** del registro.
    """
    mn = ins.mnemonic
    try:
        ops = ins.operands
    except Exception:
        return False
    if not ops:
        return False
    name = f"r{reg}"

    def is_reg(op):
        return op.type == 1 and ins.reg_name(op.reg) == name

    if mn.startswith("push") or mn.startswith("stm"):
        # salvan: el registro queda con el valor antiguo solo si está en la lista
        return any(is_reg(op) for op in ops[1:])
    if mn.startswith("pop") or mn.startswith("ldm"):
        # restauran (destruyen) el valor si el registro está en la lista
        return any(is_reg(op) for op in ops)
    op = ops[0]
    if op.type != 1:
        return False
    return is_reg(op)


def killed_between(b, ldr_addr, add_addr, reg, md):
    n = 0
    for ins in md.disasm(b[ldr_addr - BASE:add_addr - BASE], ldr_addr):
        n += 1
        if n > 600:
            return True
        if ins.address == ldr_addr:
            continue
        if _writes_to(ins, reg):
            return True
    return False


def scan(b, lo, hi, starts, md):
    import bisect
    ldrs = ldr_sites(b, lo, hi)
    adds = add_sites(b, lo, hi)
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = {}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        while i >= 0:
            la, w = v[i]
            if a - la > 4096:
                break
            tgt = (w + (a + 4)) & 0xFFFFFFFF
            if tgt in starts:
                if not killed_between(b, la, a, reg, md):
                    out.setdefault(tgt, []).append(a)
            i -= 1
    return out


def main():
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    # `detail` debe estar ACTIVADO para que la kill analysis funcione: sin él,
    # `ins.operands` lanza CsError y `_writes_to` devuelve False siempre (o sea, el
    # "kill analysis" del script canónico `scan_pic_refs_v2.py` es inerte).
    if os.environ.get("S120_NO_DETAIL") != "1":
        md.detail = True
    b = open(BIN, "rb").read()
    lo, hi = (int(sys.argv[1], 0), int(sys.argv[2], 0)) if len(sys.argv) > 2 else IDT_CODE
    starts = string_starts(b, 0x0, 0xFFFFFFFF)
    res = scan(b, lo, hi, starts, md)
    dest = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "pic_refs_idt_code.json")
    json.dump({f"0x{k:x}": sorted(set(v)) for k, v in sorted(res.items())},
              open(dest, "w"), indent=0)
    print(f"destinos: {len(res)} -> {dest}")


if __name__ == "__main__":
    main()
