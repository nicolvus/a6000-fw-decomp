"""E26-R19 — emulación del callback USB de clase/vendor de Darwin (`darwin_core.bin`, FM3).

Mapeo verificado: dirección = offset de archivo + 0x4200 (los descriptores USB del archivo en 0x239e4 son 0x27be4 en el
código). Los punteros del callback (0x1079d…) son direcciones; los `bl`/`b` y `ldr [pc]` trabajan en offsets de archivo.
Se interceptan EP0_send (0xc8a6), la ruta de parada (0x1932e) y el registro/aviso (0x21090, 0xa930). Solo lectura.
"""

import sys
from pathlib import Path

from unicorn import (
    UC_ARCH_ARM,
    UC_HOOK_CODE,
    UC_HOOK_MEM_WRITE,
    UC_MODE_MCLASS,
    UC_MODE_THUMB,
    Uc,
    UcError,
)
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_SP,
)

BIN = (
    Path(__file__).resolve().parents[2]
    / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
)
BASE = 0x4200
SETUP = 0x20002DF0
CALLBACK = 0x1079D  # [0] del bloque registrado por 0xc650/0xce54
HOOKS = {0xC8A6: "EP0_send", 0x1932E: "stop", 0x21090: "log", 0xA930: "post"}
CASES = {
    "estándar GET_DESCRIPTOR informe HID (0x22)": (0x81, 6, 0, 0x22, 0, 0, 0xFF, 0),
    "estándar GET_DESCRIPTOR dispositivo (0x01)": (0x80, 6, 0, 1, 0, 0, 0x12, 0),
    "clase GET_REPORT": (0xA1, 1, 0, 1, 0, 0, 1, 0),
    "clase SET_REPORT": (0x21, 9, 0, 2, 0, 0, 1, 0),
    "clase SET_IDLE": (0x21, 0x0A, 0, 0, 0, 0, 0, 0),
    "clase GET_IDLE": (0xA1, 2, 0, 0, 0, 0, 1, 0),
    "clase GET_PROTOCOL": (0xA1, 3, 0, 0, 0, 0, 1, 0),
    "vendor OUT": (0x40, 1, 0x34, 0x12, 0, 0, 4, 0),
    "vendor IN": (0xC0, 1, 0, 0, 0, 0, 8, 0),
}


def run(setup, data=None):
    """Devuelve (fin, eventos [(nombre, r0, r1)], escrituras fuera de SRAM)."""
    data = BIN.read_bytes() if data is None else data
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    mu.mem_map(0x4000, 0x40000)
    mu.mem_write(BASE, data)
    for base, size in (
        (0x20000000, 0x10000),
        (0x40000000, 0x200000),
        (0x42000000, 0x2000000),
    ):
        mu.mem_map(base, size)
    mu.mem_write(SETUP, bytes(setup))
    ret = 0x3F000
    mu.reg_write(UC_ARM_REG_SP, 0x2000F000)
    mu.reg_write(UC_ARM_REG_LR, ret | 1)
    mu.reg_write(UC_ARM_REG_R0, SETUP)
    eventos, periferico = [], []

    def codigo(uc, addr, _size, _):
        if addr - BASE in HOOKS:
            eventos.append(
                (
                    HOOKS[addr - BASE],
                    uc.reg_read(UC_ARM_REG_R0),
                    uc.reg_read(UC_ARM_REG_R1),
                )
            )
            uc.reg_write(
                UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR)
            )  # no entra en el cuerpo

    def escritura(_uc, _t, addr, _size, val, _):
        if addr >= 0x40000000:
            periferico.append((hex(addr), hex(val & 0xFFFFFFFF)))

    mu.hook_add(UC_HOOK_CODE, codigo)
    mu.hook_add(UC_HOOK_MEM_WRITE, escritura)
    try:
        mu.emu_start(CALLBACK, ret, count=500)
        fin = "ret"
    except UcError as e:
        fin = f"error {e}"
    return fin, eventos, periferico


if __name__ == "__main__":
    for nombre, setup in CASES.items():
        fin, eventos, periferico = run(setup)
        print(
            f"{nombre:46} {fin} {[(n, hex(a), hex(b)) for n, a, b in eventos]} {periferico}",
            file=sys.stdout,
        )
