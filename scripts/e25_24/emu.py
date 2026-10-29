"""E25-24 — emulación Unicorn mínima de los dos parches (offline, sin cámara).

No modela el sensor ni la captura completa.  Comprueba exactamente lo que los
parches añaden:

* Darwin: `0x20c74` (tipo de bobina) y `0x1fe66` (compuerta del motor) con el
  byte de modalidad a 0/1, comparados con la imagen original.
* BIONZ: el cave que copia `cap+0x41c` a `pkt[0x0e]` en las dos ramas del
  constructor, y el retorno/jump a `0x43841346` / `0x43841576`.
"""
from __future__ import annotations

from dataclasses import dataclass

try:
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc, UcError
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R3,
        UC_ARM_REG_R4,
        UC_ARM_REG_R9,
        UC_ARM_REG_SP,
    )
except ImportError as exc:  # pragma: no cover - los tests hacen importorskip
    raise ImportError("unicorn no está disponible") from exc

DARWIN_BASE = 0x4200
BIONZ_BASE = 0x43541000
SENTINEL = 0xFFFFFFF0


@dataclass(frozen=True)
class BionzRun:
    packet: bytes
    r0: int
    stopped_at: int


def run_darwin(code: bytes, entry: int, flag: int, type_value: int = 0x43) -> int:
    """Ejecuta una función Darwin y devuelve r0.

    `flag` se escribe en 0x20003716 (S+0x3e, copia de pkt[0x0e]); el tipo de
    mecanismo y su presencia se fijan en 0x20000050 / 0x200002c0.
    """
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(0, 0x30000)
    uc.mem_write(DARWIN_BASE, code)
    uc.mem_map(0x20000000, 0x10000)
    uc.mem_write(0x20000050, bytes([type_value]))
    uc.mem_write(0x200002C0, b"\x01")
    uc.mem_write(0x20003716, bytes([flag]))
    uc.reg_write(UC_ARM_REG_SP, 0x2000F000)
    uc.reg_write(UC_ARM_REG_LR, SENTINEL)
    try:
        uc.emu_start(entry | 1, 0)
    except UcError as exc:
        # El retorno salta al centinela no mapeado: es el final esperado.
        if "UNMAPPED" not in str(exc):
            raise
    return int(uc.reg_read(UC_ARM_REG_R0))


def run_bionz_selector(code: bytes, r1: int, field: int) -> BionzRun:
    """Ejecuta el cave desde 0x4384133e hasta una de las dos ramas."""
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    size = (len(code) + 0xFFF) & ~0xFFF
    uc.mem_map(BIONZ_BASE, size)
    uc.mem_write(BIONZ_BASE, code)
    uc.mem_map(0x50000000, 0x1000)
    bank = 0x50000800
    pkt = 0x50000000
    uc.mem_write(bank + 0x41C, field.to_bytes(4, "little"))
    uc.reg_write(UC_ARM_REG_R9, bank)
    uc.reg_write(UC_ARM_REG_R4, pkt)
    uc.reg_write(UC_ARM_REG_R1, r1)
    uc.reg_write(UC_ARM_REG_R0, 0xABCD)
    uc.reg_write(UC_ARM_REG_SP, 0x50000F00)
    uc.reg_write(UC_ARM_REG_LR, SENTINEL)
    stops = {0x43841346, 0x43841576}
    hit = [0]

    def hook(uc_, address, size, user):
        if address in stops:
            hit[0] = address
            uc_.emu_stop()

    uc.hook_add(UC_HOOK_CODE, hook)
    try:
        uc.emu_start(0x4384133E | 1, 0)
    except UcError as exc:
        if "UNMAPPED" not in str(exc):
            raise
    return BionzRun(bytes(uc.mem_read(pkt, 0x10)), int(uc.reg_read(UC_ARM_REG_R0)), hit[0])


@dataclass(frozen=True)
class Pkt1Run:
    packet: bytes
    r3: int


def run_bionz_pkt1(code: bytes, field: int = 1) -> Pkt1Run:
    """Ejecuta el bloque de clase hasta 0x43841398 y devuelve pkt[1] y r3.

    Fuerza `[sb+0x4bc] & 0x20` y el flag PIC 0x43f9b503 a 1 para pasar por
    `adds r3,#0x40`: si el cave no conserva r3=0, pkt[1] sale 0x41 en vez de 0x40.
    """
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    size = (len(code) + 0xFFF) & ~0xFFF
    uc.mem_map(BIONZ_BASE, size)
    uc.mem_write(BIONZ_BASE, code)
    uc.mem_map(0x50000000, 0x1000)
    bank = 0x50000800
    pkt = 0x50000000
    uc.mem_write(bank + 0x41C, field.to_bytes(4, "little"))
    uc.mem_write(bank + 0x4BC, (0x20).to_bytes(2, "little"))
    uc.mem_write(0x43F9B503, b"\x01")  # flag PIC del constructor
    uc.reg_write(UC_ARM_REG_R9, bank)
    uc.reg_write(UC_ARM_REG_R4, pkt)
    uc.reg_write(UC_ARM_REG_R1, 1)
    uc.reg_write(UC_ARM_REG_R0, 0xABCD)
    uc.reg_write(UC_ARM_REG_SP, 0x50000F00)
    uc.reg_write(UC_ARM_REG_LR, SENTINEL)
    try:
        uc.emu_start(0x4384133E | 1, 0x43841398 | 1)
    except UcError as exc:
        if "UNMAPPED" not in str(exc):
            raise
    return Pkt1Run(bytes(uc.mem_read(pkt, 0x10)), int(uc.reg_read(UC_ARM_REG_R3)))
