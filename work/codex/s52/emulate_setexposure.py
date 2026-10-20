#!/usr/bin/env python3
"""Emulación aislada de los selectores SetExposure S52.

Carga solamente una copia privada del blob. Las llamadas fuera del intervalo de
la función se sustituyen por retornos ABI y quedan registradas: no ejecuta
firmware ni interactúa con hardware.
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_R4,
    UC_ARM_REG_R5,
    UC_ARM_REG_R6,
    UC_ARM_REG_R7,
    UC_ARM_REG_R8,
    UC_ARM_REG_R9,
    UC_ARM_REG_R10,
    UC_ARM_REG_SP,
)
from unicorn.unicorn_const import UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_PROT_ALL

ROOT = Path(__file__).resolve().parents[3]
BASE = 0x43541000
RAM = 0x45000000
OBJ = 0x50000000
PAR = 0x50010000
STACK = 0x60000000
STOP = 0x60001000
PAGE = 0x1000

TARGETS = {
    # Entradas de los dispatchers internos: los prólogos anteriores solo
    # normalizan parámetros; aquí empieza la rama ShutMode que se compara.
    "imx235": (ROOT / "work/claude/input/a7s-av-cam.bin", 0x436F423E, 0x436F4384),
    "imx210": (ROOT / "work/claude/input/a6000-av-cam.bin", 0x436D70BE, 0x436D7298),
}


def align(n: int) -> int:
    return (n + PAGE - 1) & -PAGE


def put(uc: Uc, address: int, data: bytes) -> None:
    uc.mem_write(address, data)


def word(uc: Uc, address: int, value: int) -> None:
    put(uc, address, struct.pack("<I", value))


def half(uc: Uc, address: int, value: int) -> None:
    put(uc, address, struct.pack("<H", value))


def run(sensor: str, shutmode: int, shr: int) -> dict[str, object]:
    path, entry, end = TARGETS[sensor]
    blob = path.read_bytes()
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(BASE, align(len(blob)), UC_PROT_ALL)
    put(uc, BASE, blob)
    uc.mem_map(RAM, 0x400000, UC_PROT_ALL)
    uc.mem_map(OBJ, 0x40000, UC_PROT_ALL)
    uc.mem_map(STACK, 0x40000, UC_PROT_ALL)
    # Área privada para resultados y punteros sintetizados; la imagen ya ocupa
    # el rango 0x44000000 de sus GOT/datos PIC.
    put(uc, RAM, struct.pack("<I", OBJ + 0x20000) * (0x400000 // 4))
    word(uc, OBJ + (0x2D8 if sensor == "imx235" else 0x294), OBJ + 0x22000)
    word(uc, OBJ + 0x22004, 0x00010000)
    word(uc, OBJ + (0x1AC if sensor == "imx235" else 0x170), 0)
    put(uc, PAR, bytes(0x40))
    half(uc, PAR + 4, shr & 0xFFFF)
    half(uc, PAR + 6, (shr + 3) & 0xFFFF)
    put(uc, PAR + 8, bytes([0x12]))
    put(uc, PAR + 9, bytes([shutmode]))
    half(uc, PAR + 0x0C, (shr + 9) & 0xFFFF)
    put(uc, PAR + 0x14, bytes([0x34]))
    writes: list[dict[str, int]] = []
    calls: list[dict[str, int]] = []

    def on_write(_uc: Uc, _access: int, address: int, size: int, value: int, _user: object) -> None:
        if address >= RAM or OBJ <= address < OBJ + 0x40000:
            writes.append({"address": address, "size": size, "value": value})

    def on_code(_uc: Uc, address: int, _size: int, _user: object) -> None:
        if address == STOP:
            _uc.emu_stop()
            return
        if not (entry <= address < end):
            calls.append(
                {
                    "target": address,
                    "r0": _uc.reg_read(UC_ARM_REG_R0),
                    "r1": _uc.reg_read(UC_ARM_REG_R1),
                    "r2": _uc.reg_read(UC_ARM_REG_R2),
                    "r3": _uc.reg_read(UC_ARM_REG_R3),
                }
            )
            # La primera llamada es la frontera: se registra, pero no se
            # ejecuta ni se simula el aplicador/transporte posterior.
            _uc.emu_stop()

    uc.hook_add(UC_HOOK_MEM_WRITE, on_write)
    uc.hook_add(UC_HOOK_CODE, on_code)
    cfg1, cfg2 = OBJ + 0x24000, OBJ + 0x25000
    if sensor == "imx235":
        uc.reg_write(UC_ARM_REG_R0, OBJ)
        uc.reg_write(UC_ARM_REG_R2, cfg2)
        uc.reg_write(UC_ARM_REG_R3, cfg1)
        uc.reg_write(UC_ARM_REG_R4, OBJ)
        uc.reg_write(UC_ARM_REG_R6, shutmode)
        uc.reg_write(UC_ARM_REG_R7, shr)
        uc.reg_write(UC_ARM_REG_R10, PAR)
    else:
        uc.reg_write(UC_ARM_REG_R3, cfg1)
        uc.reg_write(UC_ARM_REG_R4, OBJ)
        uc.reg_write(UC_ARM_REG_R5, shr)
        uc.reg_write(UC_ARM_REG_R9, shutmode)
        uc.reg_write(UC_ARM_REG_R10, PAR)
        # Caso 2 accede a dos slots GOT mediante r8, que el prólogo habría
        # formado como 0x4401f1fc. Se sustituyen en la copia privada.
        uc.reg_write(UC_ARM_REG_R8, 0x4401F1FC)
        word(uc, 0x4401F1FC + 0x8AC, cfg2)
        word(uc, 0x4401F1FC + 0x6C28, cfg2 + 0x100)
    uc.reg_write(UC_ARM_REG_SP, STACK + 0x3F000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    try:
        uc.emu_start(entry | 1, STOP, count=200000)
        error = None
    except Exception as exc:  # el resultado conserva explícitamente la frontera
        error = str(exc)
    return {
        "sensor": sensor,
        "entry": hex(entry),
        "shutmode": shutmode,
        "shr": shr,
        "writes": writes,
        "calls": calls,
        "error": error,
    }


def main() -> None:
    runs = [run(sensor, mode, shr) for sensor in TARGETS for mode in range(5) for shr in (17, 257, 1023)]
    out = ROOT / "work/codex/s52_shutmode_emulation.json"
    out.write_text(json.dumps({"method": "private offline Unicorn maps; external calls stubbed", "runs": runs}, indent=2) + "\n")


if __name__ == "__main__":
    main()
