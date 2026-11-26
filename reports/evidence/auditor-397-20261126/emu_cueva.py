"""Emulación del gancho + cueva con Unicorn (independiente de capstone): comprueba
la aritmética de la tabla, los argumentos de las 3 llamadas, la guarda y el retorno."""
import sys
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

NEW = Path("build/aud397/work/libmpr-397.so").read_bytes()
CAVE, STUB, CALLER = 0x93B000, 0x93B04E, 0x7126E6
RET = 0x7126EA
TABLE = 0xA3699C


def correr(guard_value: int):
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0x900000, 0x200000)          # cubre cueva 0x93Bxxx y la tabla 0xA36A64
    mu.mem_map(0x2B0000, 0x10000)           # stubs de las funciones llamadas
    mu.mem_map(0x710000, 0x10000)           # llamante
    mu.mem_map(0x7F0000, 0x10000)           # pila
    mu.mem_write(CAVE, NEW[CAVE:CAVE + 0x52])
    mu.mem_write(TABLE, bytes(0x14 * 12))   # tabla a cero
    # guarda: campo +4 de la entrada 10
    mu.mem_write(TABLE + 0x14 * 10 + 4, guard_value.to_bytes(4, "little"))
    for fn in (0x2B4820, 0x2B1DEC, 0x2B43F0):
        mu.mem_write(fn, bytes.fromhex("7047"))  # bx lr
    mu.mem_write(CALLER, NEW[CALLER:CALLER + 4])
    mu.mem_write(RET, b"\x00\xbf")               # nop: aterrizaje del retorno
    for r, v in ((UC_ARM_REG_SP, 0x7F8000), (UC_ARM_REG_LR, RET), (UC_ARM_REG_R4, 0x11111111),
                 (UC_ARM_REG_R5, 0x22222222), (UC_ARM_REG_R0, 0xaaaaaaaa), (UC_ARM_REG_R1, 0xbbbbbbbb),
                 (UC_ARM_REG_R2, 0xcccccccc), (UC_ARM_REG_R3, 0xdddddddd)):
        mu.reg_write(r, v)

    log = []
    def hook(mu, addr, size, _):
        if addr == 0x2B1DEC:
            log.append(("2B1DEC", mu.reg_read(UC_ARM_REG_R0), mu.reg_read(UC_ARM_REG_R1),
                        mu.reg_read(UC_ARM_REG_R2), mu.reg_read(UC_ARM_REG_R3)))
        elif addr == 0x2B43F0:
            log.append(("2B43F0", mu.reg_read(UC_ARM_REG_R0), mu.reg_read(UC_ARM_REG_R1)))
        elif addr == 0x2B4820:
            log.append(("2B4820", mu.reg_read(UC_ARM_REG_R0), mu.reg_read(UC_ARM_REG_SP)))
        elif addr == RET:
            log.append(("RETORNO", mu.reg_read(UC_ARM_REG_R4), mu.reg_read(UC_ARM_REG_R5),
                        mu.reg_read(UC_ARM_REG_SP), mu.reg_read(UC_ARM_REG_LR)))
    mu.hook_add(UC_HOOK_CODE, hook)
    mu.emu_start(CALLER | 1, RET, count=10000)
    return log


for g in (0, 1):
    print(f"== guarda [0xA36A68] = {g} ==")
    for e in correr(g):
        print("   ", e[0], " ".join(hex(x) for x in e[1:]))
