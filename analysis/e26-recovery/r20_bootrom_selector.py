"""E26-R20 — selector del BootROM (`FUN_ffff1062`) por emulación con las rutinas auxiliares sustituidas.

Modelo: se carga `bootrom.bin` en 0xffff0000 (Thumb), se fijan los registros leídos (`MODEREG` 0xf2915010 bit0 y
GPIO(4,RDATA) 0xf2910410 bits 21/22) y se sustituyen las llamadas por valores de retorno controlados. Se registra el orden
de llamadas. No emula el hardware ni las rutinas sustituidas; solo comprueba la lógica de decisión de `main`.
"""

import struct
import sys
from pathlib import Path

from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_SP,
)

ROM = (
    Path(__file__).resolve().parents[2]
    / "analysis/camera-dumps/updater-20261020-175427/bootrom.bin"
)
BASE = 0xFFFF0000
MAIN = 0xFFFF1062
# nombre -> dirección; las que no retornan marcan el final del escenario
FUNCS = {
    "init": 0xFFFF0D14,
    "fmt": 0xFFFF1584,
    "print": 0xFFFF0C98,
    "trace": 0xFFFF0CB6,
    "hw1": 0xFFFF0EFC,
    "hw2": 0xFFFF0D4C,
    "hw3": 0xFFFF0244,
    "storage_init": 0xFFFF028C,
    "load_loader2": 0xFFFF02C6,
    "load_header": 0xFFFF0332,
    "find_key": 0xFFFF039C,
    "timing": 0xFFFF0554,
    "rx_packet": 0xFFFF0876,
    "load_payload": 0xFFFF03DE,
    "blank_check": 0xFFFF044E,
    "prepare_jump": 0xFFFF0486,
    "crc_key": 0xFFFF0C52,
    "nread_flag": 0xFFFF0BD4,
}
STOP = {
    "error_led": 0xFFFF0D62,
    "serial_boot": 0xFFFF0FA0,
    "jump_loader2": 0xFFFF013C,
    "jump_ram": 0xFFFF0144,
}
DEFAULT_RET = {
    "storage_init": 0,
    "load_loader2": 0,
    "load_header": 0,
    "find_key": 0,
    "rx_packet": 0x3001,
    "load_payload": 0,
    "blank_check": 0,
    "prepare_jump": 0,
    "crc_key": 0xFFFFFFFF,
    "nread_flag": 1,
}


def run(modereg_bit0, gpio_bit22=0, gpio_bit21=0, clave=None, recibida=None, **ret):
    """Devuelve la secuencia de llamadas hasta la primera rutina que no retorna."""
    rom = ROM.read_bytes()
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE, 0x8000)
    mu.mem_write(BASE, rom)
    for base, size in (
        (0xC0000000, 0x100000),
        (0xF2910000, 0x6000),
        (0xF2400000, 0x20000),
    ):
        mu.mem_map(base, size)
    mu.mem_write(0xF2915010, struct.pack("<I", modereg_bit0 & 1))
    mu.mem_write(0xF2910410, struct.pack("<I", (gpio_bit22 << 22) | (gpio_bit21 << 21)))
    sp, ret_addr = 0xC00F0000, 0xFFFF2000
    mu.reg_write(UC_ARM_REG_SP, sp)
    mu.reg_write(UC_ARM_REG_LR, ret_addr | 1)
    valores = {**DEFAULT_RET, **ret}
    por_dir = {a: n for n, a in {**FUNCS, **STOP}.items()}
    secuencia, fin = [], []

    def codigo(uc, addr, _size, _):
        n = por_dir.get(addr)
        if n is None:
            return
        if n == "trace":
            secuencia.append(
                f"trace({uc.reg_read(UC_ARM_REG_R0)},{uc.reg_read(UC_ARM_REG_R1)})"
            )
        elif n != "fmt":
            secuencia.append(n if n not in valores else f"{n}->{valores[n]:#x}")
        if n in STOP:
            fin.append(n)
            uc.emu_stop()
            return
        if (
            n == "find_key" and clave is not None
        ):  # entrada de clave encontrada (4 B + CRC) en la tabla 0xc0001200
            uc.mem_write(uc.reg_read(UC_ARM_REG_R0), struct.pack("<II", clave, 0))
        if n == "rx_packet" and recibida is not None:  # clave recibida por serie
            uc.mem_write(uc.reg_read(UC_ARM_REG_R0), struct.pack("<I", recibida))
        if n in valores:
            uc.reg_write(UC_ARM_REG_R0, valores[n])
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) | 1)

    mu.hook_add(UC_HOOK_CODE, codigo)
    mu.emu_start(MAIN | 1, ret_addr, count=100000)
    return secuencia, (fin[0] if fin else "retorno")


ESCENARIOS = {
    "bit0=0 normal": {"modereg_bit0": 0},
    "bit0=0 fallo almacenamiento": {"modereg_bit0": 0, "storage_init": 0x1003},
    "bit0=1 gpio4.22=1": {"modereg_bit0": 1, "gpio_bit22": 1},
    "bit0=1 fallo almacenamiento": {"modereg_bit0": 1, "storage_init": 0x1003},
    "bit0=1 fallo cabecera": {"modereg_bit0": 1, "load_header": 0x1006},
    "bit0=1 sin clave": {"modereg_bit0": 1, "find_key": 1},
    "bit0=1 clave presente, sin serie": {
        "modereg_bit0": 1,
        "find_key": 0,
        "rx_packet": 0x3001,
    },
    "bit0=1 clave coincide": {
        "modereg_bit0": 1,
        "find_key": 0,
        "rx_packet": 0,
        "clave": 0x1234,
        "recibida": 0x1234,
    },
    "bit0=1 clave distinta": {
        "modereg_bit0": 1,
        "find_key": 0,
        "rx_packet": 0,
        "clave": 0x1234,
        "recibida": 0x4321,
    },
    "bit0=1 CRC de clave inválida": {
        "modereg_bit0": 1,
        "find_key": 0,
        "rx_packet": 0,
        "crc_key": 0,
        "clave": 0x1234,
        "recibida": 0x1234,
    },
}

if __name__ == "__main__":
    for nombre, kw in ESCENARIOS.items():
        sec, fin = run(**kw)
        llamadas = [x for x in sec if not x.startswith("trace(")]
        print(f"{nombre:36} -> {fin:13} {' '.join(llamadas)}", file=sys.stdout)
