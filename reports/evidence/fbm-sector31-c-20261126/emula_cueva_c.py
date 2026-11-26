#!/usr/bin/env python3
"""Pre-vuelo de la cueva C en Unicorn (sin QEMU): comprueba que la cueva llama EXACTAMENTE a lo que
llama la vía de consola, con los argumentos en el orden real de cada función, y que la guarda es
estricta (si idx 10 ya tiene handle no se llama a nada).

Modelo: se mapea el libmpr PARCHEADO con base = 0xAE3E5000 (la que dio el arnés en run-r1/r1v3), se
pone PC = base+0x93B000 (cueva) y LR = (base+0x7126EA)|1 (lo que deja el `bl` del gancho) y se
interceptan las tres llamadas: FBM::Init 0x2B4820, EntryWriteBaseDataFunction 0x2B1DEC e
InitBackupData 0x2B43F0.  También se emula 0x2B1DEC de verdad sobre una copia de la tabla 0x9D23FC
para ver las filas que quedan con `fn != 0` y cuál elegiría 0x2B3000.

Uso: emula_cueva_c.py [build/cfw_fbm_sector31_c/libmpr.so]
"""
from __future__ import annotations

import struct
import sys

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB
from unicorn.arm_const import UC_CPU_ARM_CORTEX_A15
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1,
                               UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_R5,
                               UC_ARM_REG_SP)

BASE = 0xAE3E5000          # base de carga medida en el arnés
CAVE = 0x93B000
VUELTA = 0x7126EA
FBM_INIT = 0x2B4820
EWBDF = 0x2B1DEC
INITB = 0x2B43F0
TABLA = 0xA3699C
PARES = 0x9D23FC           # 37 filas de 0x18 {userID, mediaID, sector, OM, fn, arg}
IDX = 10
PAGE = 0x1000


def alinea(x: int) -> int:
    return (x + PAGE - 1) & ~(PAGE - 1)


def ejecuta(lib: bytes, orig: bytes, handle: int, etiqueta: str, ret_initb: int = 0) -> tuple[int, list[str]]:
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_A15)     # Thumb-2 (movw/movt)
    uc.mem_map(BASE, max(alinea(len(lib)), alinea(0xA3A000)))
    uc.mem_write(BASE, lib)
    # la tabla de pares está en el PT_LOAD 2 (off=0x9BB1C8, vaddr=0x9C31C8): VA != offset de fichero
    PARES_OFF = 0x9CA3FC
    uc.mem_write(BASE + PARES, orig[PARES_OFF:PARES_OFF + 37 * 0x18])   # tabla de pares de fábrica
    for f in (FBM_INIT, EWBDF, INITB):              # las tres llamadas se sustituyen por `bx lr`
        uc.mem_write(BASE + f, b"\x70\x47")
    pila = 0x80000000
    uc.mem_map(pila - 0x8000, 0x8000)
    uc.reg_write(UC_ARM_REG_SP, pila)
    uc.reg_write(UC_ARM_REG_LR, BASE + VUELTA)      # lo que deja el `bl` del gancho (UC_MODE_THUMB)
    uc.reg_write(UC_ARM_REG_PC, (BASE + CAVE) | 1)
    uc.mem_write(BASE + TABLA, bytes(30 * 0x14))    # FBM::Init no abrió nada
    if handle:
        uc.mem_write(BASE + TABLA + 0x14 * IDX, struct.pack("<II", 0x31, handle))
    llamadas: list[str] = []

    def on_code(uc: Uc, addr: int, size: int, _u) -> None:
        off = addr - BASE
        if off == FBM_INIT:
            llamadas.append("FBM::Init()")
            uc.reg_write(UC_ARM_REG_R0, 0)
        elif off == EWBDF:
            r0, r1, r2, r3 = (uc.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1,
                                                       UC_ARM_REG_R2, UC_ARM_REG_R3))
            stub = bytes(uc.mem_read(r1 & ~1, 4))       # el fn registrado tiene que ser el stub del cueva
            ok_stub = stub == b"\x00\x20\x70\x47"
            llamadas.append("EntryWriteBaseDataFunction(userID=%#x, fn=%#x %s, arg=%#x, mediaID=%#x)"
                            % (r0, r1, "=stub 'movs r0,#0; bx lr'" if ok_stub else "=NO ES EL STUB(%s)"
                               % stub.hex(), r2, r3))
            for k in range(37):                     # efecto real de 0x2B1DEC
                a = BASE + PARES + k * 0x18
                uid, mid = struct.unpack("<II", uc.mem_read(a, 8))
                if uid == r0 and mid == r3:
                    uc.mem_write(a + 0x10, struct.pack("<II", r1, r2))
            uc.reg_write(UC_ARM_REG_R0, 0)          # 0 == hecho
        elif off == INITB:
            r0, r1 = uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)
            llamadas.append("InitBackupData(OM=%#x, mediaID=%#x)" % (r0, r1))
            uc.reg_write(UC_ARM_REG_R0, ret_initb)

    uc.hook_add(UC_HOOK_CODE, on_code)
    uc.emu_start((BASE + CAVE) | 1, BASE + VUELTA, count=400)   # corta al volver a 0x7126EA
    pc = uc.reg_read(UC_ARM_REG_PC)
    t = struct.unpack("<IIIII", uc.mem_read(BASE + TABLA + 0x14 * IDX, 0x14))
    print("== %s ==" % etiqueta)
    print("   llamadas : %s" % (" · ".join(llamadas) or "NINGUNA"))
    print("   PC final : %#x (%s)" % (pc - BASE, "vuelve a 0x7126EA" if pc - BASE == VUELTA else "NO vuelve"))
    print("   idx10    : sector=%#06x handle=%#010x valido=%u om=%u b10=%#x" % t)
    filas = []
    for k in range(37):
        uid, mid, sec, om, fn, arg = struct.unpack("<IIIIII", uc.mem_read(BASE + PARES + k * 0x18, 0x18))
        if fn:
            filas.append("fila %d (userID=%#x mediaID=%#x sector=%#x OM=%#x) fn=%#x arg=%#x"
                         % (k, uid, mid, sec, om, fn, arg))
    print("   filas con fn != 0: %s" % ("; ".join(filas) or "NINGUNA"))
    print("   regs preservados: r4=%#x r5=%#x (valores de vuelta de la cueva)"
          % (uc.reg_read(UC_ARM_REG_R4), uc.reg_read(UC_ARM_REG_R5)))
    otras = [i for i in range(30) if i != IDX and struct.unpack("<I", uc.mem_read(BASE + TABLA + 0x14 * i, 4))[0]]
    print("   otras entradas de 0xA3699C tocadas: %s" % (otras or "NINGUNA"))
    return pc - BASE, llamadas


def main() -> int:
    lib = open(sys.argv[1] if len(sys.argv) > 1 else "build/cfw_fbm_sector31_c/libmpr.so", "rb").read()
    orig = open("analysis/camera-extract/usr/lib/libmpr.so", "rb").read()
    pcs = []
    pc1, ll1 = ejecuta(lib, orig, 0, "handle 0 (falta el sector): debe registrarlo y llamar a InitB 6 3")
    pcs.append(pc1)
    pc2, ll2 = ejecuta(lib, orig, 1, "handle 1 (ya existe, como tras reiniciar): la guarda debe salir antes")
    pcs.append(pc2)
    pc3, ll3 = ejecuta(lib, orig, 3, "handle 3 (ya existe)", )
    pcs.append(pc3)
    pc4, ll4 = ejecuta(lib, orig, 0, "handle 0 e InitBackupData devolviendo error 0x10800010", ret_initb=0x10800010)
    pcs.append(pc4)
    print()
    ok = (pc1 == pc2 == pc3 == pc4 == VUELTA
          and ll2 == ["FBM::Init()"] and ll3 == ["FBM::Init()"]
          and [c.split("(")[0] for c in ll1] == ["FBM::Init", "EntryWriteBaseDataFunction",
                                                "EntryWriteBaseDataFunction", "InitBackupData"]
          and "userID=0x4, fn=" in ll1[1] and "=stub" in ll1[1] and ll1[1].endswith("arg=0x0, mediaID=0x3)")
          and "userID=0x21, fn=" in ll1[2] and "=stub" in ll1[2] and ll1[2].endswith("arg=0x0, mediaID=0x3)")
          and ll1[3].endswith("OM=0x6, mediaID=0x3)")
          and [c.split("(")[0] for c in ll4] == [c.split("(")[0] for c in ll1])
    print("VEREDICTO: %s" % ("OK" if ok else "FALLO"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
