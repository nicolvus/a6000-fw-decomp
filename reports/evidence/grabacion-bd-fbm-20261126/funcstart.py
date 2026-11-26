#!/usr/bin/env python3
"""Busca el inicio de la funcion que contiene una VA en libmpr.so.

Criterio: retrocede en pasos de 2 B desde la VA y se queda con el candidato mas
cercano que (a) decodifica como `push {..,lr}` / `stmdb sp!,{..,lr}` y (b) va
precedido de relleno (0000 / bf00) o de un final de funcion (pop {..,pc} /
bx lr / b.w).  Imprime tambien los simbolos .dynsym que caen en el rango.
"""
import sys

sys.path.insert(0, "reports/evidence/fbm-sector31-consola-20261126/evidencia")
import mprdis as M
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

TEXT = M.sec(".text")
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def ins_at(va):
    b = M.rd(va, 4)
    for i in md.disasm(b, va):
        return i
    return None


def has_lr(va):
    i = ins_at(va)
    if not i:
        return None
    if i.mnemonic in ("push", "stmdb") and "lr" in i.op_str:
        return i
    return None


def is_pad(va):
    b = M.rd(va, 2)
    return b in (b"\x00\x00", b"\x00\xbf")


def is_end(va):
    i = ins_at(va)
    if not i:
        return False
    if i.mnemonic in ("pop", "ldm") and "pc" in i.op_str:
        return True
    return i.mnemonic == "bx" and i.op_str == "lr"


def func_start(va, back=0x800):
    for d in range(0, back, 2):
        v = va - d
        if has_lr(v) and (is_pad(v - 2) or is_end(v - 2) or is_pad(v - 4)):
            return v
    return None


if __name__ == "__main__":
    for a in sys.argv[1:]:
        va = int(a, 0) & ~1
        s = func_start(va)
        print(f"{va:#010x}: inicio={s:#x}" if s else f"{va:#010x}: inicio=?")
        if s:
            names = [f"{k:#x}={v}" for k, v in sorted(M.SYM.items()) if s <= k <= s + 0x2000]
            print("   syms:", ", ".join(names[:8]) if names else "(ninguno)")
