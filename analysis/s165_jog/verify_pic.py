#!/usr/bin/env python3
"""S165 — verificación a mano de los pares PIC (regla estricta) en un rango.

Para cada `add rX,pc` muestra:
  - el `ldr rX,[pc,#imm]` más cercano por detrás (regla estricta) y su pool,
  - el valor del pool,
  - el destino calculado,
  - el texto en el destino,
  - AVISO si entre el ldr y el add hay otra escritura a rX (el add no usaría
    el valor del ldr: la regla estricta fallaría en ese caso).
"""
import bisect
import sys

sys.path.insert(0, "analysis/s165_jog")
from common import BASE, B, N, U16, U32, cstr, pic_ldr_sites, pic_add_sites  # noqa: E402


def writes_to_reg(lo, hi, reg):
    """Direcciones de escritura a `reg` entre [lo,hi) -> (addr, mnemonic)."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        note = None
        if (h & 0xF800) == 0x4800:            # ldr rX,[pc,#imm]  -> escribe rX
            if ((h >> 8) & 7) == reg:
                note = "ldr-lit"
        elif (h & 0xFF7F) == 0xF85F:          # ldr.w rX,[pc,#imm12]
            if ((U16(B, o + 2)[0] >> 12) & 0xF) == reg:
                note = "ldr.w-lit"
        elif (h & 0xF800) == 0x6800:          # ldr rX,[rY,#imm]  -> escribe rX
            if ((h >> 8) & 7) == reg:
                note = "ldr-mem"
        elif (h & 0xF800) == 0x9800:          # ldr rX,[rY,#imm] (T2)
            if ((h >> 8) & 7) == reg:
                note = "ldr-mem.w"
        elif 0x2000 <= (h & 0xF800) <= 0x3800:   # movs/adds/subs Rd,#imm
            if ((h >> 8) & 7) == reg:
                note = "movs-imm"
        elif (h & 0xFC00) == 0x4000:          # mov Rd,Rm / ops
            if ((h & 7) | ((h >> 4) & 8)) == reg:
                note = "mov-reg"
        elif (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            if ((((h >> 7) & 1) << 3) | (h & 7)) == reg:
                note = "add-pc"
        if note:
            out.append((a, note))
        a += 2
    return out


def main():
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    only = int(sys.argv[3], 0) if len(sys.argv) > 3 else None
    ldrs = pic_ldr_sites(lo, hi)
    adds = pic_add_sites(lo, hi)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    for a, reg in adds:
        if only is not None and a != only:
            continue
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        if i < 0:
            continue
        la, w, lit = v[i]
        if a - la > 4096:
            continue
        dest = (w + (a + 4)) & 0xFFFFFFFF
        between = [x for x in writes_to_reg(la + 2, a, reg)]
        flag = "RE-USA-REG" if between else "ok"
        print(f"{a:#x} reg=r{reg} ldr={la:#x} pool={lit:#x} W={w:#x} -> dest={dest:#x}  {cstr(dest)!r}  [{flag}]"
              + (f" entre-medio={[(hex(x), n) for x, n in between]}" if between else ""))


if __name__ == "__main__":
    main()
