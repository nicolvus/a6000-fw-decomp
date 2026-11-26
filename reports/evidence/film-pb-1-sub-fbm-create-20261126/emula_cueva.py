#!/usr/bin/env python3
"""Pre-vuelo de la cueva v3 en Unicorn (sin QEMU): comprueba que el cálculo de la dirección de la
tabla es PC-relativo (no un literal absoluto sin reubicar) y que la entrada idx 10 de 0xA3699C se
escribe sólo si CreateSector32 devuelve 0.

Modelo: se mapea el libmpr PARCHEADO con base = 0xAE3E5000 (la que dio el arnés en run-r1), se pone
PC = base+0x93B000 (cueva), LR = (base+0x7126EA)|1 (lo que deja el `bl` del gancho) y se interceptan
las dos llamadas: FBM::Init (0x2B4820) y CreateSector32 (0x2B7080), que se simulan.

Uso: emula_cueva.py build/cfw_fbm_sector31_v3/libmpr.so
"""
from __future__ import annotations

import struct
import sys

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB
from unicorn.arm_const import UC_CPU_ARM_CORTEX_A15
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
                               UC_ARM_REG_R4, UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_SP)

BASE = 0xAE3E5000          # base de carga medida en el arnés (run-r1: libmpr base=0xae3e5000)
CAVE = 0x93B000
HOOK = 0x7126E6
VUELTA = 0x7126EA
FBM_INIT = 0x2B4820
CS32 = 0x2B7080
TABLA = 0xA3699C
IDX = 10
PAGE = 0x1000


def alinea(x: int) -> int:
    return (x + PAGE - 1) & ~(PAGE - 1)


def ejecuta(lib: bytes, ret_cs32: int, handle: int, sector: int, etiqueta: str) -> int:
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_A15)     # Thumb-2 (movw/movt): sin esto Unicorn usa ARMv5
    # la tabla 0xA3699C cae MÁS ALLÁ del fichero (10 321 204 B = 0x9D7C74): está en la parte memsz
    # del PT_LOAD (BSS, a cero al cargar). Se mapea de sobra para cubrirla.
    uc.mem_map(BASE, max(alinea(len(lib)), alinea(0xA3A000)))
    uc.mem_write(BASE, lib)
    pila = 0x80000000
    uc.mem_map(pila - 0x8000, 0x8000)
    uc.reg_write(UC_ARM_REG_SP, pila)
    uc.reg_write(UC_ARM_REG_LR, (BASE + VUELTA) | 1)
    uc.reg_write(UC_ARM_REG_PC, (BASE + CAVE) | 1)
    # tabla a cero antes de la cueva (como tras un FBM::Init que no abre nada)
    uc.mem_write(BASE + TABLA, bytes(30 * 0x14))
    llamadas: list[str] = []

    def on_code(uc: Uc, addr: int, size: int, _u) -> None:
        off = addr - BASE
        if off == FBM_INIT:
            llamadas.append("FBM::Init")
            uc.reg_write(UC_ARM_REG_PC, (uc.reg_read(UC_ARM_REG_LR) & ~1) | 1)   # bit0 = Thumb
        elif off == CS32:
            r0, r1, r2, r3 = (uc.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1,
                                                       UC_ARM_REG_R2, UC_ARM_REG_R3))
            llamadas.append("CreateSector32(fileType=%#x, flag=%#x, p2=%#x, p3=%#x)" % (r0, r1, r2, r3))
            if r2:
                uc.mem_write(r2, struct.pack("<I", handle))
            if r3:
                uc.mem_write(r3, struct.pack("<I", sector))
            uc.reg_write(UC_ARM_REG_R0, ret_cs32)
            uc.reg_write(UC_ARM_REG_PC, (uc.reg_read(UC_ARM_REG_LR) & ~1) | 1)   # bit0 = Thumb

    uc.hook_add(UC_HOOK_CODE, on_code)
    uc.emu_start((BASE + CAVE) | 1, BASE + VUELTA, count=200)
    pc = uc.reg_read(UC_ARM_REG_PC)
    t = uc.mem_read(BASE + TABLA + 0x14 * IDX, 0x14)
    campos = struct.unpack("<IIIII", t)
    print("== %s ==" % etiqueta)
    print("   llamadas      : %s" % " · ".join(llamadas))
    print("   PC final      : %#x (%s)" % (pc - BASE, "vuelve a 0x7126EA" if pc - BASE == VUELTA else "NO vuelve"))
    print("   idx10         : sector=%#06x handle=%#010x valido=%u om=%u b10=%#x" % campos)
    otras = [i for i in range(30) if i != IDX and struct.unpack("<I", uc.mem_read(BASE + TABLA + 0x14 * i, 4))[0]]
    print("   otras entradas tocadas: %s" % (otras or "NINGUNA"))
    return pc - BASE


def main() -> int:
    lib = open(sys.argv[1] if len(sys.argv) > 1 else "build/cfw_fbm_sector31_v3/libmpr.so", "rb").read()
    ok = ejecuta(lib, 0, 3, 0x31, "CreateSector32 -> 0 (éxito), handle 3, sector 0x31")
    ok2 = ejecuta(lib, 0x7, 0, 0, "CreateSector32 -> 0x7 (FBS_INVALID_PROCESS)")
    ok3 = ejecuta(lib, 0, 0x55, 0x31, "CreateSector32 -> 0, handle 0x55 (no debe hardcodear 3)")
    print()
    print("VEREDICTO: %s" % ("OK" if ok == ok2 == ok3 == VUELTA else "FALLO"))
    return 0 if ok == ok2 == ok3 == VUELTA else 1


if __name__ == "__main__":
    sys.exit(main())
