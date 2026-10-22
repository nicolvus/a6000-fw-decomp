#!/usr/bin/env python3
"""Escáner PIC v2: referencias a cadenas con ANÁLISIS DE FLUJO (kill analysis).

El esquema del firmware es:

    ldr  rX, [pc, #inm]      ; W = desplazamiento desde el pool
    ...
    add  rX, pc              ; destino = W + (dir_add + 4)

Problema: el registro se reutiliza, así que un `add rX,pc` no siempre corresponde al
`ldr rX,[pc]` más cercano (regla "estricta", que pierde referencias) ni a *cualquier*
`ldr` anterior (regla "ancha", que inventa referencias: p. ej. 186 pares frente a
118 reales en [SFRA]).

Este script resuelve el emparejamiento comprobando, entre el `ldr` candidato y el
`add`, que **nadie vuelve a escribir rX** (kill analysis): si el `ldr` es la última
escritura de ese registro antes del `add`, el valor que se suma es el que se cargó.

Uso:  scan_pic_refs_v2.py [LO HI] [RUTA_SALIDA]
"""
import bisect
import json
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
STR_LO, STR_HI = 0x0, 0xFFFFFFFF       # rango de cadenas válidas (toda la imagen)
MAX_LDR_GAP = 4096                      # ventana de emparejamiento ldr -> add

B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = True          # imprescindible: sin detail, ins.operands lanza CsError

# Capstone codifica los registros ARM como ARM_REG_R0 + n (66 + n); no sirve
# `reg & 0xF` (confundiría r1 con r3, p. ej.).
ARM_REG_R0 = 66


def _reg_index(reg):
    """0..15 para r0..r12/sp/lr/pc; None si no es un registro de 32 bits."""
    if ARM_REG_R0 <= reg < ARM_REG_R0 + 13:
        return reg - ARM_REG_R0
    if 13 <= reg <= 15:       # sp, lr, pc
        return reg
    return None


def u16(a):
    return U16(B, a - BASE)[0]


def u32(a):
    return U32(B, a - BASE)[0]


def string_starts(lo, hi):
    """Inicio de cadena: byte imprimible cuyo anterior no lo es."""
    o0, o1 = max(0, lo - BASE), min(N, hi - BASE)
    out = set()
    prev_print = False
    for i in range(o0, o1):
        c = B[i]
        cur = 32 <= c < 127
        if cur and not prev_print:
            out.add(BASE + i)
        prev_print = cur
    return out


def ldr_sites(lo, hi):
    """[(addr, reg, valor_del_pool)]"""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:              # ldr rT, [pc, #imm5*4]
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:            # ldr.w rT, [pc, #imm12]
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= N - 4:
                out.append((a, reg, U32(B, o2)[0]))
        a += 2
    return out


def add_sites(lo, hi):
    """[(addr, reg)] de los `add rX, pc` de 16 bits."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    return out


def _writes_to(ins, reg):
    """¿La instrucción deja el registro `reg` con un valor distinto al cargado?

    - instrucciones con destino de registro: sí, si el destino es ese registro;
    - `push`/`stm`: salvan el valor (lo destruyen) solo si el registro está en la lista;
    - `pop`/`ldm`: restauran (destruyen) el valor si el registro está en la lista.
    """
    mn = ins.mnemonic
    try:
        ops = ins.operands
    except Exception:
        return False
    if not ops:
        return False
    reg = reg & 0xF
    if mn.startswith("push") or mn.startswith("stm"):
        # salvan: el registro queda con el valor antiguo solo si está en la lista
        return any(op.type == 1 and _reg_index(op.reg) == reg for op in ops[1:])
    if mn.startswith("pop") or mn.startswith("ldm"):
        return any(op.type == 1 and _reg_index(op.reg) == reg for op in ops)
    op = ops[0]
    if op.type != 1:            # no es un registro destino
        return False
    return _reg_index(op.reg) == reg


def killed_between(ldr_addr, add_addr, reg):
    """True si alguien escribe `reg` entre el ldr y el add (o el código no es lineal)."""
    n = 0
    for ins in MD.disasm(B[ldr_addr - BASE:add_addr - BASE], ldr_addr):
        n += 1
        if n > 600:
            return True          # no se puede analizar: se descarta el par
        if ins.address == ldr_addr:
            continue
        if _writes_to(ins, reg):
            return True
    return False


def scan(lo, hi, verbose=False):
    starts = string_starts(STR_LO, STR_HI)
    ldrs = ldr_sites(lo, hi)
    adds = add_sites(lo, hi)
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}

    out = {}
    stats = {"adds": len(adds), "candidatos": 0, "confirmados": 0, "descartados": 0}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        while i >= 0:
            la, w = v[i]
            if a - la > MAX_LDR_GAP:
                break
            stats["candidatos"] += 1
            tgt = (w + (a + 4)) & 0xFFFFFFFF
            if tgt in starts:
                if killed_between(la, a, reg):
                    stats["descartados"] += 1
                else:
                    stats["confirmados"] += 1
                    out.setdefault(tgt, []).append(a)
            i -= 1
    if verbose:
        print("  ", stats)
    return out, stats


def main():
    lo = int(sys.argv[1], 0) if len(sys.argv) > 1 else BASE
    hi = int(sys.argv[2], 0) if len(sys.argv) > 2 else BASE + N
    dest = sys.argv[3] if len(sys.argv) > 3 else "analysis/s106_imaging_cap/pic_refs_v2.json"
    res, stats = scan(lo, hi, verbose=True)
    with open(dest, "w") as fh:
        json.dump({f"0x{k:x}": sorted(set(v)) for k, v in sorted(res.items())},
                  fh, indent=0)
    print(f"destinos: {len(res)}  ->  {dest}")


if __name__ == "__main__":
    main()
