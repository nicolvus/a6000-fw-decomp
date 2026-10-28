#!/usr/bin/env python3
"""E25-19d P0 — tabla curada de escritores y lectores de `cap+0x74f`, verificada contra los bytes de av-cam.bin.

Salida: analysis/e25-19d/escritores-lectores-74f.json
"""
from __future__ import annotations

import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000

# (dirección, texto esperado, función, valor escrito, condición)
ESCRITORES = [
    (0x438ACC9C, "strb.w r1, [r3, #0x74f]", "0x438ab3e8 (copia del plan de captura)", "r4[0x142] (byte bajo de un halfword del plan)",
     "siempre al construir el registro; el halfword 0x142 lo fijan 8 ramas con `2×0x4387b520(...)`"),
    (0x437DF5E8, "strb.w r8, [r4, #0x74f]", "0x437df338 (arranque de captura, r0=cap)", "0",
     "solo si r8==0, con r8=0x437e1e48(...) (petición de modo/arranque rechazada con r7≠0); además cap[0x4fd0]|=1"),
    (0x438C2562, "strb.w r3, [r4, #0x74f]", "0x438c2538 (admisión del 0x0b)", "0",
     "global G=[0x4402546c]=0x43e95950: G[0x7e]≠0 y G[0x7f]==cap[0x1d8]"),
]
# Los 21 manejadores de 0x438d025c..0x438d0dc8 + sub 9 abren con `ldrb.w r3,[r0,#0x74f]`
LECTORES = [0x438C2566, 0x438C29FA, 0x438C83CE, 0x438C8AC2, 0x43B1F15E,
            *[0x438D025C, 0x438D033C, 0x438D0420, 0x438D050C, 0x438D058C, 0x438D060C, 0x438D0660, 0x438D06E4, 0x438D082C,
              0x438D08E8, 0x438D0984, 0x438D09D8, 0x438D0A2C, 0x438D0AD2, 0x438D0B44, 0x438D0B9A, 0x438D0BE4, 0x438D0C84,
              0x438D0CD8, 0x438D0D30, 0x438D0DC8]]


def texto(data: bytes, addr: int) -> str:
    i = next(iter(Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(data[addr - BASE:addr - BASE + 4], addr, 1)))
    return f"{i.mnemonic} {i.op_str}"


def verifica() -> dict:
    data = BIN.read_bytes()
    for a, esperado, *_ in ESCRITORES:
        assert texto(data, a) == esperado, (hex(a), texto(data, a))
    for a in LECTORES:
        assert "0x74f]" in texto(data, a) and texto(data, a).startswith("ldrb"), (hex(a), texto(data, a))
    return {"schema": "e25-19d-escritores/v1", "escritores": [
        {"addr": hex(a), "ins": t, "funcion": f, "valor": v, "condicion": c} for a, t, f, v, c in ESCRITORES],
        "lectores": [hex(a) for a in LECTORES]}


if __name__ == "__main__":
    r = verifica()
    (ROOT / "analysis/e25-19d/escritores-lectores-74f.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(r, indent=1, ensure_ascii=False))
