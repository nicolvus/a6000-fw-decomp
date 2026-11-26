#!/usr/bin/env python3
"""Emulación Unicorn de dos fragmentos REALES de libmpr.so (fw 3.21).

A) 0x61A9F2-0x61AA6E  núcleo de la guarda de AviMMgr::isSupportContent
   (entrada: r0=TvSystem, [r7+0x124]=frameRate; salida: r0 = 0/1)
B) 0x6E0CD6-0x6E0D1E  conversión de la cadencia de AviIf al enum del
   struct de 0x13C bytes que consume la guarda ([out+0x124])

No se ejecuta ninguna instrucción de E/S: solo se emula el .text real cargado
tal cual desde el fichero. Las llamadas a log (0x65062C / 0x6F0A54) se saltan.
"""
import struct
import sys

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_R5,
                               UC_ARM_REG_R7, UC_ARM_REG_LR, UC_ARM_REG_PC,
                               UC_ARM_REG_SP)

LIB = sys.argv[1]
IMG = open(LIB, 'rb').read()
SCRATCH = 0x40000000
TAM_SCRATCH = 0x4000


def nueva_uc():
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(0x0, 0xA00000)
    uc.mem_write(0x0, IMG[:0xA00000])
    uc.mem_map(SCRATCH, TAM_SCRATCH)
    return uc


def leer32(uc, va):
    return struct.unpack('<I', uc.mem_read(va, 4))[0]


def cadena(uc, va):
    out = b''
    while True:
        b = bytes(uc.mem_read(va + len(out), 1))
        if b == b'\0':
            return out.decode('latin1')
        out += b


LOGS = (0x65062C, 0x6F0A54)


def guarda(tvsys, fr):
    uc = nueva_uc()
    uc.mem_write(SCRATCH + 0x124, struct.pack('<I', fr))     # [r7+0x124]
    uc.mem_write(SCRATCH + 0x1000, struct.pack('<I', 0))     # objeto falso
    uc.mem_write(SCRATCH + 0x2000, b'\0')                    # byte de nivel de log
    msgs = []
    fin = {'r0': None}

    def hook(uc, addr, size, _):
        if addr == 0x61AA6E:
            fin['r0'] = uc.reg_read(UC_ARM_REG_R0)
            uc.emu_stop()
        elif addr in LOGS:
            r2 = uc.reg_read(UC_ARM_REG_R2)
            try:
                msgs.append(cadena(uc, r2))
            except Exception:
                msgs.append('?')
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    for r, v in ((UC_ARM_REG_R0, tvsys), (UC_ARM_REG_R4, SCRATCH + 0x1000),
                 (UC_ARM_REG_R5, SCRATCH + 0x2000), (UC_ARM_REG_R7, SCRATCH),
                 (UC_ARM_REG_SP, SCRATCH + 0x3000)):
        uc.reg_write(r, v)
    uc.emu_start(0x61A9F3, 0x61AA7A, count=400)
    return fin['r0'], msgs


def enum_avi(valor):
    uc = nueva_uc()
    uc.mem_write(SCRATCH + 0x100, struct.pack('<I', valor))   # [r7+0x100]
    uc.mem_write(SCRATCH + 0x1000, b'\0' * 0x200)             # struct de salida
    fin = {'pc': None}

    def hook(uc, addr, size, _):
        if addr == 0x6E0D1E:
            fin['pc'] = uc.reg_read(UC_ARM_REG_PC)
            uc.emu_stop()

    uc.hook_add(UC_HOOK_CODE, hook)
    for r, v in ((UC_ARM_REG_R7, SCRATCH), (UC_ARM_REG_R4, SCRATCH + 0x1000),
                 (UC_ARM_REG_SP, SCRATCH + 0x3000)):
        uc.reg_write(r, v)
    uc.emu_start(0x6E0CD7, 0x6E0D40, count=200)
    return leer32(uc, SCRATCH + 0x1000 + 0x124)


print('== A) guarda isSupportContent  ELF 0x61A9F2-0x61AA6E (libmpr fw 3.21)')
print('   TvSystem  frameRate  r0  mensaje')
for tv in (0, 1, 2):
    for fr in list(range(0, 11)) + [0xFF]:
        r0, msgs = guarda(tv, fr)
        print('   %8d  %9d  %2s  %s' % (tv, fr, r0, msgs[-1].strip() if msgs else '-'))

print()
print('== B) conversión AviIf -> struct de 0x13C  ELF 0x6E0CD6-0x6E0D1E')
print('   entrada[r7+0x100]   [salida+0x124]')
for v in range(1, 12):
    print('   %16d   %d' % (v, enum_avi(v)))
