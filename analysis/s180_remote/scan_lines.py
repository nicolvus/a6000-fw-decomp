#!/usr/bin/env python3
"""S180 - numero de linea del fuente en cada traza [REMOTE] (primer vararg en [sp]).

El primer vararg (el %d del formato) es el NUMERO DE LINEA del fichero fuente.
Se recorre cada sitio PIC (regla estricta, mapa global) hacia adelante hasta la
llamada al logger 0x435661e4 y se resuelve el valor inmediato escrito en [sp].
"""
import json, struct
from capstone import *
from capstone.arm import *

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
LOGGER = 0x435661e4
B = open(BIN, "rb").read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True

fm = json.load(open("analysis/s180_remote/func_map.json"))
remote = json.load(open("analysis/s180_remote/pic_sites.json"))["strings"]
rem = {r["vaddr"]: r for r in remote}

REGNUM = {ARM_REG_R0: 0, ARM_REG_R1: 1, ARM_REG_R2: 2, ARM_REG_R3: 3, ARM_REG_R4: 4,
          ARM_REG_R5: 5, ARM_REG_R6: 6, ARM_REG_R7: 7, ARM_REG_R8: 8, ARM_REG_R9: 9,
          ARM_REG_R10: 10, ARM_REG_R11: 11, ARM_REG_R12: 12, ARM_REG_SP: 13,
          ARM_REG_LR: 14, ARM_REG_PC: 15}


def dis(lo, hi):
    return list(md.disasm(B[lo - BASE:hi - BASE], lo))


def cstr(a):
    o = a - BASE
    e = o
    while e < len(B) and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1")


def hw(a):
    return struct.unpack_from("<H", B, a - BASE)[0]


def value_at(loads, reg, before):
    v = None
    for addr, r, val in loads:
        if r == reg and addr < before:
            v = val
    return v


def find_sp_write(call, lower, loads):
    """(valor, direccion) de la ultima escritura en [sp] antes de `call`."""
    for a in range(call - 2, lower, -2):
        h = hw(a)
        cands = []
        if (h & 0xFFF8) == 0x6068:                      # STR (T1) rX,[sp,#0]
            cands.append(h & 7)
        if (h & 0xF800) == 0x9000 and (h & 0xFF) == 0:  # STR (T2) SP-relativo
            cands.append((h >> 8) & 7)
        if h == 0xF8CD:                                  # STR (T3/T4) sp!,rX,#0
            cands.append((hw(a + 2) >> 12) & 0xF)
        if ((h & 0xFE00) == 0xE800 and (h & 0x0080) and (h & 0x000F) == 13) or h == 0xE92D:
            lst = hw(a + 2)                              # STM sp!,{...}
            if lst:
                cands.append((lst & -lst).bit_length() - 1)
        for r in cands:
            v = value_at(loads, r, a)
            if v is not None and 50 <= v <= 2000:
                return v, a
    return None, None


# --- limites de funcion (prologo) -------------------------------------------
starts = sorted(int(k, 16) for k in fm["funcs"])
lim = {s: (starts[i + 1] if i + 1 < len(starts) else s + 0x400) for i, s in enumerate(starts)}


def enclosing(addr):
    cand = [x for x in starts if x <= addr]
    return cand[-1] if cand else None


rows = []
for r in remote:
    vaddr = r["vaddr"]
    for site in r["pic_sites"]:
        f = enclosing(site)
        ins = dis(f, min(lim[f], f + 0x900))
        loads = []
        for p in ins:
            if p.mnemonic in ("movs", "mov", "movw", "mov.w") and len(p.operands) == 2 \
               and p.operands[0].type == ARM_OP_REG and p.operands[1].type == ARM_OP_IMM:
                n = REGNUM.get(p.operands[0].reg)
                if n is not None:
                    loads.append((p.address, n, p.operands[1].imm))
        # avanzar desde el sitio hasta el primer `bl`
        bl_addr = None
        for p in ins:
            if p.address < site:
                continue
            if p.mnemonic == "bl":
                try:
                    if p.operands[0].imm == LOGGER:
                        bl_addr = p.address
                except Exception:
                    pass
                break
        if bl_addr is None:
            print("SIN CALL:", hex(site), r["text"][:50])
            continue
        # limite inferior: la llamada al logger anterior
        lower = f
        for p in ins:
            if p.mnemonic == "bl" and p.address < bl_addr:
                try:
                    if p.operands[0].imm == LOGGER:
                        lower = p.address
                except Exception:
                    pass
        line, line_at = find_sp_write(bl_addr, lower, loads)
        rows.append({"func": f"0x{f:x}", "site": hex(site), "bl": hex(bl_addr),
                     "dest": hex(vaddr), "text": r["text"], "line": line,
                     "line_at": (hex(line_at) if line_at else None)})

json.dump(rows, open("analysis/s180_remote/log_calls.json", "w"), indent=1)
print(f"{'site':>10} {'bl':>10} {'linea':>6}  texto")
for x in sorted(rows, key=lambda y: (y["line"] if y["line"] else 0)):
    print(f"{x['site']} {x['bl']} {str(x['line']):>6}  {x['text'][:80]}")
print()
print("n =", len(rows))
print("lineas:", sorted({x["line"] for x in rows if x["line"]}))
print("sin linea:", [x["site"] for x in rows if not x["line"]])
