#!/usr/bin/env python3
"""S109 — volcado de desensamblado Thumb de un rango del firmware A6000.

Uso: python3 disasm.py 0x435a15e8 [n_insn]

AVISO: el `capstone` 5.0.7 disponible en este entorno decodifica de forma
incompleta algunas instrucciones Thumb de 32 bits (p. ej. 0xAB08), de modo que
las direcciones que imprime pueden desplazarse.  Para comprobaciones que
dependan de direcciones, usar la lectura directa de halfwords (como hacen los
tests de S109) en vez de este script.
"""
import sys
import capstone

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
md.detail = False


def dis(va, n=60):
    o = va - BASE
    for i in md.disasm(B[o:o + 8 * n], va | 1):
        print(f"{i.address & ~1:#010x}  {i.mnemonic:8s} {i.op_str}")
        if i.mnemonic in ("bx", "pop") and "pc" in i.op_str:
            break


if __name__ == "__main__":
    va = int(sys.argv[1], 0)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    dis(va, n)
