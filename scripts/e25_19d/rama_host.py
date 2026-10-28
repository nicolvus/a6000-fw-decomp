#!/usr/bin/env python3
"""E25-19d P2 — emula el código real de av-cam.bin (fw 3.21): Tv → µs (0x4382fac8) → ticks de la rama de host de sub 9.

Tramo ejecutado: 0x438c8abc..0x438c8b18 con un `cap` falso (74f=0, 740=0, 4b84=0). El global de µs (0x43eee76c) lo escribe la
construcción del 0x0c (0x4384157c, `str r0,[r3]` tras 0x4382fac8([sl+0x162])); aquí se rellena con la salida real de 0x4382fac8.
Se intercepta la llamada a 0x43b1f1ec (armado del temporizador 0) para leer (id, ticks, callback).
Salida: analysis/e25-19d/rama-host-emulacion.json
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, UC_PROT_ALL, Uc
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R4,
    UC_ARM_REG_R5,
    UC_ARM_REG_SP,
)

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE, SENT, CAP, GLOBAL_US = 0x43541000, 0x20000000, 0x10000000, 0x43EEE76C
TICK_US = 32
CASOS = {"1/8000": 1 / 8000, "1/1000": 1 / 1000, "1/250": 1 / 250, "1/60": 1 / 60, "1/30": 1 / 30, "1/15": 1 / 15,
         "1/8": 1 / 8, "1 s": 1, "4 s": 4, "8 s": 8, "15 s": 15, "30 s": 30}


def tv_de(seg: float) -> int:
    """Tv (APEX×256) con Tv = 4096 − 256·log2(t), la relación que invierte 0x4382fac8."""
    return round(4096 - 256 * math.log2(seg))


def maquina() -> Uc:
    data = BIN.read_bytes()
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE, ((len(data) + 0xFFF) & ~0xFFF) + 0x100000, UC_PROT_ALL)
    mu.mem_write(BASE, data)
    mu.mem_map(0x10000000, 0x100000, UC_PROT_ALL)
    mu.mem_map(SENT, 0x1000, UC_PROT_ALL)
    mu.mem_write(SENT, b"\x00\xbe")
    return mu


def llama(mu: Uc, addr: int, r0: int) -> int:
    mu.reg_write(UC_ARM_REG_R0, r0)
    mu.reg_write(UC_ARM_REG_SP, 0x100F0000)
    mu.reg_write(UC_ARM_REG_LR, SENT | 1)
    mu.emu_start(addr | 1, SENT, count=20000)
    return mu.reg_read(UC_ARM_REG_R0)


def rama_host(mu: Uc, tv: int, w74f: int = 0, w740: int = 0, w4b84: int = 0) -> dict:
    us = llama(mu, 0x4382FAC8, tv)
    mu.mem_write(GLOBAL_US, us.to_bytes(4, "little"))
    mu.mem_write(CAP, bytes(0x6000))
    mu.mem_write(CAP + 0x74F, bytes([w74f]))
    mu.mem_write(CAP + 0x740, w740.to_bytes(4, "little"))
    mu.mem_write(CAP + 0x4B84, bytes([w4b84]))
    visto: dict = {}

    def hook(uc: Uc, addr: int, size: int, _u: object) -> None:
        if addr == 0x43B1F1EC:  # armado del temporizador: se captura y se detiene
            visto.update(id=uc.reg_read(UC_ARM_REG_R0), ticks=uc.reg_read(UC_ARM_REG_R1), cb=uc.reg_read(UC_ARM_REG_R2))
            uc.emu_stop()

    h = mu.hook_add(UC_HOOK_CODE, hook, begin=0x43B1F1EC, end=0x43B1F1EC)
    mu.reg_write(UC_ARM_REG_R4, CAP)
    mu.reg_write(UC_ARM_REG_R5, CAP + 0x4B00)
    mu.reg_write(UC_ARM_REG_SP, 0x100F0000)
    mu.reg_write(UC_ARM_REG_LR, SENT | 1)
    try:
        mu.emu_start(0x438C8ABC | 1, SENT, count=2000)
    finally:
        mu.hook_del(h)
    visto["us"] = us
    visto["cap728"] = int.from_bytes(mu.mem_read(CAP + 0x728, 4), "little")
    return visto


def tabla() -> list[dict]:
    mu = maquina()
    filas = []
    for nombre, seg in CASOS.items():
        tv = tv_de(seg)
        r = rama_host(mu, tv)
        filas.append({"caso": nombre, "tv": tv, "us": r["us"], "ticks": r["ticks"], "cb": hex(r["cb"]), "cap728": r["cap728"],
                      "seg_ticks": r["ticks"] * TICK_US / 1e6, "error_rel": (r["ticks"] * TICK_US / 1e6) / seg - 1})
    return filas


def otras_ramas() -> dict:
    mu = maquina()
    tv = tv_de(4)
    return {"74f=1": rama_host(mu, tv, w74f=1), "740=1": rama_host(mu, tv, w740=1)}


if __name__ == "__main__":
    t = tabla()
    o = {k: {**v, "cb": hex(v["cb"])} for k, v in otras_ramas().items()}
    out = ROOT / "analysis/e25-19d/rama-host-emulacion.json"
    out.write_text(json.dumps({"schema": "e25-19d-rama-host/v1", "tick_us": TICK_US, "casos": t, "otras_ramas_4s": o}, indent=1) + "\n")
    for f in t:
        print(f"{f['caso']:>7} tv={f['tv']:>5} us={f['us']:>9} ticks={f['ticks']:>8} t={f['seg_ticks']:.6f}s err={f['error_rel']:+.4%}")
    print(o)
