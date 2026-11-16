"""G57 — Focus Bracket (Focus Shift Shooting): tras cada captura mueve el enfoque un paso con el comando de lente 0x1D (s16 con signo).

Primitiva real de `av-cam` 3.21 (la que usa `Camera::LC` de `lc_BracketAF.cpp`, `0x437c74b6`): `0x43adb5e6(r0 = paso s16, r1 = bit «flag»)` → `0x43adb17a` arma la trama
`{1D, paso_lo, paso_hi, 00, mode|flags}` y la encola con `0x43adb15c`. Fin del movimiento: `0x43adcc22` (¿cmd 0x1D en curso?, `movs r0,#0x1d; b.w 0x436f6358`).
Cueva `fb_paso` (la llamaría el gancho de «fin de captura», **aún sin localizar**, FOCUSSHIFT-HOOK): lee N y paso de los ajustes de `cfw_ajustes`, cuenta tomas y,
mientras `tomas < N`, emite el movimiento relativo; en la N-ésima reinicia el contador sin mover (N tomas → N-1 movimientos). N = Off → no hace nada.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import cfw_ajustes as cfw

BASE = 0x43541000
CAVE, CAVE_END = 0x43541500, 0x435415C0       # hueco cero verificado (G74); g55 usa 0x43541600, g65 0x43541700, e25 0x43541800
CELDA = 0x435417F0                             # contador de tomas (u32, RAM del propio av-cam; cero al arrancar)
MOVER = 0x43ADB5E6                             # (paso s16, flag) -> encola cmd 0x1D
PROLOGO = {0x43ADB5E6: bytes.fromhex("1fb500230222"), 0x43ADB17A: bytes.fromhex("f0b585b0"), 0x43ADCC22: bytes.fromhex("1d20")}
ENVIAR = 0x43ADB15C
SRC = ROOT / "analysis/rea-independent/input/av-cam.bin"


def cave_bytes() -> bytes:
    n, p = cfw.POR_ID["fb_n"], cfw.POR_ID["fb_paso"]
    asm = f"""
        push {{r4, lr}}
        {cfw.leer_asm(n, "tn")}
        cbz r0, fin
        mov r4, r0
        movw r3, #{CELDA & 0xFFFF:#x}
        movt r3, #{CELDA >> 16:#x}
        ldr r1, [r3]
        adds r1, #1
        cmp r1, r4
        bhs.w ultima
        str r1, [r3]
        {cfw.leer_asm(p, "tp")}
        movs r1, #0
        bl {MOVER:#x}
        b.w fin
    ultima:
        movw r3, #{CELDA & 0xFFFF:#x}
        movt r3, #{CELDA >> 16:#x}
        movs r1, #0
        str r1, [r3]
    fin:
        pop {{r4, pc}}
    """
    code = cfw.ensamblar(asm, CAVE)
    assert len(code) <= CAVE_END - CAVE, len(code)
    return code


def apply_bytes(data: bytes) -> bytes:
    for a, b in PROLOGO.items():
        if data[a - BASE:a - BASE + len(b)] != b:
            raise ValueError(f"primitiva {a:#x} distinta del original")
    if any(data[CAVE - BASE:CAVE_END - BASE]) or any(data[CELDA - BASE:CELDA + 4 - BASE]):
        raise ValueError("la cueva 0x43541500 no está a cero")
    out = bytearray(data)
    code = cave_bytes()
    out[CAVE - BASE:CAVE - BASE + len(code)] = code
    return bytes(out)      # sin gancho: FOCUSSHIFT-HOOK (dirección del fin de captura) pendiente


def emular(img: bytes, idx_n: int, idx_paso: int, tomas: int):
    """Llama `fb_paso` `tomas` veces; devuelve las tramas que `0x43adb15c` recibió (5 B cada una)."""
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE & ~0xFFF, ((len(img) + 0x1000) + 0x200000) & ~0xFFF)
    mu.mem_write(BASE, img)
    stack, end = 0x10000000, 0x30000000
    mu.mem_map(stack - 0x10000, 0x20000)
    mu.mem_map(end, 0x1000)
    ids = {cfw.POR_ID["fb_n"].backup: idx_n, cfw.POR_ID["fb_paso"].backup: idx_paso}
    tramas = []

    def code(uc, addr, size, _):
        if addr == cfw.BACKUP_READ:
            uc.mem_write(uc.reg_read(UC_ARM_REG_R1), bytes([ids[uc.reg_read(UC_ARM_REG_R0)]]))
            uc.reg_write(UC_ARM_REG_R0, 0)
        elif addr == ENVIAR:
            tramas.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0), 5)))
        else:
            return
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    for a in (cfw.BACKUP_READ, ENVIAR):
        mu.hook_add(UC_HOOK_CODE, code, begin=a, end=a)
    for _ in range(tomas):
        mu.reg_write(UC_ARM_REG_SP, stack)
        mu.reg_write(UC_ARM_REG_LR, end | 1)
        mu.emu_start(CAVE | 1, end, count=100000)
    return tramas


def trama(paso: int) -> bytes:
    """Trama esperada de `0x43adb17a(paso, 0, 2, 1, 0, 2, r1)`: cmd, paso LE, byte3 = 0, byte4 = 2 | 1<<2 | 2<<4 | r1<<6 (r1 = 0)."""
    return bytes([0x1D]) + struct.pack("<H", paso) + bytes([0x00, 0x26])


if __name__ == "__main__":
    orig = SRC.read_bytes()
    img = apply_bytes(orig)
    n_op, p_op = cfw.POR_ID["fb_n"].opciones, cfw.POR_ID["fb_paso"].opciones
    assert emular(img, 0, 1, 10) == [], "Off: no hace nada"
    assert emular(img, 200, 1, 10) == [], "byte fuera de tabla = Off"
    i5 = [v for _, v in n_op].index(5)
    for ip, (_, paso) in enumerate(p_op):
        assert emular(img, i5, ip, 5) == [trama(paso)] * 4, (ip, "N=5 -> 4 movimientos con el paso del ajuste")
    assert emular(img, i5, 1, 10) == [trama(p_op[1][1])] * 8, "contador reiniciado: dos series de 5 tomas = 8 movimientos"
    print("OK")
