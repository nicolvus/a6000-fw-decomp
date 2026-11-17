"""G84 — «Zebra Nivel» (rango libre, origen ≈Sony α6400 «Zebra 0–109 %») en `libObj` 3.21: ajuste CFW Off/10/20/…/60 (`cfw_ajustes`, id de Backup 1 B).
Solo bytes de `libObj.so` del `.dat`; sin construir CFW. `ObjRenderer` (0x2b9944…) convierte el índice de menú Zebra en un centro `c` y manda al VDF la banda L = c−5, U = c+5
(g83). Gancho único: las dos instrucciones `mov r0,r5; adds r2,r3,#5` de 0x2b99a4 (r3 = c) pasan por la cueva: con «Zebra Nivel» ≠ Off, r3 = valor del ajuste (el centro en %);
con Off (o byte fuera de tabla) la cueva reejecuta las dos instrucciones sin cambiar nada. Registros r0–r3 y lr restaurados.
Cueva: +0xD00…+0xE00 del cuerpo de la función muerta 0x2648d8 (la de g76 acaba en +0xC00).
shortcut: el nivel solo se aplica al emitir SetZebra (al elegir Cebra o al arrancar); NO_VERIFICADO que el VDF acepte U < 65 % (g83).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/g61")]
import cfw_ajustes as cfw
import intervalo_patch as g61

SRC = g61.SRC
CAVE, CAVE_FIN = 0x2648D8 + 0xD00, 0x2648D8 + 0xE00
HOOK = (0x2B99A4, bytes.fromhex("28465a1d"))          # mov r0, r5 ; adds r2, r3, #5
VUELTA = 0x2B99A8                                       # subs r3, #5


def piezas() -> dict[str, tuple[int, bytes]]:
    a = cfw.POR_ID["zebra_nivel"]
    asm = f"""
        push {{r0, r1, r2, r3, lr}}
        {cfw.leer_asm(a, "tz", g61.BLX_BACKUP)}
        cmp r0, #0
        beq.w sal
        str r0, [sp, #12]
    sal:
        pop {{r0, r1, r2, r3, lr}}
        mov r0, r5
        adds r2, r3, #5
        @@b.w {VUELTA:#x}
    """
    code = g61._ens(asm, CAVE)
    assert CAVE + len(code) <= CAVE_FIN, hex(CAVE + len(code))
    return {"zebra": (CAVE, code)}


def apply_bytes(data: bytes) -> bytes:
    from e25_24.thumb import b_w
    out = bytearray(data)
    a, old = HOOK
    if data[a:a + 4] != old:
        raise ValueError(f"gancho {a:#x} distinto del original")
    for va, code in piezas().values():
        out[va:va + len(code)] = code
    out[a:a + 4] = b_w(a, CAVE)
    return bytes(out)


def emular(img: bytes, backup: dict[int, int], c: int = 70):
    """Unicorn: ejecuta desde el gancho con r3 = c y r5 de marcador; devuelve (r0, r2, r3, lr) al llegar a `VUELTA`."""
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R2,
        UC_ARM_REG_R3,
        UC_ARM_REG_R5,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, 0x10E4000)
    mu.mem_write(0, img)
    stack = 0x30000000
    mu.mem_map(stack - 0x1000, 0x4000)
    rd = mu.reg_read
    fin = {}

    def code(uc, addr, size, _):
        if addr == 0xDD5F4:
            uc.mem_write(rd(UC_ARM_REG_R1), bytes([backup.get(rd(UC_ARM_REG_R0), 0)]))
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, rd(UC_ARM_REG_LR))
        elif addr == VUELTA:
            fin["r"] = tuple(rd(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_LR, UC_ARM_REG_SP))
            uc.emu_stop()

    mu.hook_add(UC_HOOK_CODE, code)
    for r, v in ((UC_ARM_REG_R0, 0x111), (UC_ARM_REG_R1, 0x222), (UC_ARM_REG_R2, 0x333), (UC_ARM_REG_R3, c), (UC_ARM_REG_R5, 0xAAA5)):
        mu.reg_write(r, v)
    mu.reg_write(UC_ARM_REG_SP, stack - 0x40)
    mu.reg_write(UC_ARM_REG_LR, 0x7FFF0001)
    mu.emu_start(HOOK[0] | 1, 0x2B99B0, count=20000)
    return fin["r"] + (stack - 0x40,)


def comprobar() -> None:
    orig = SRC.read_bytes()
    img = apply_bytes(orig)
    assert len(img) == len(orig) and apply_bytes(orig) == img
    B = cfw.POR_ID["zebra_nivel"].backup
    for bk in ({}, {B: 0}, {B: 9}):                         # sin ajuste, Off, fuera de tabla: r2 = c+5 de fábrica
        r0, r1, r2, r3, lr, sp, sp0 = emular(img, bk, 80)
        assert (r0, r1, r2, r3, lr, sp) == (0xAAA5, 0x222, 85, 80, 0x7FFF0001, sp0), (bk, r0, r2, r3)
    for k, (_, v) in enumerate(cfw.POR_ID["zebra_nivel"].opciones):
        if v:
            r0, r1, r2, r3, lr, sp, sp0 = emular(img, {B: k}, 80)
            assert (r0, r1, r2, r3, lr, sp) == (0xAAA5, 0x222, v + 5, v, 0x7FFF0001, sp0), (k, v, r2, r3)


if __name__ == "__main__":
    comprobar()
    print("OK")
