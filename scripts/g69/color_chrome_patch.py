"""G69 — «Color Chrome / Film»: ajuste CFW (`cfw_ajustes`, id `color_chrome`) que suma desplazamientos fijos a la Saturación y a los 6 Color Depth (R, Y, G, C, B, M) del mensaje de colorimetría del `av-cam` (builder `0x437aa65c`).

El builder arma el paquete que el núcleo envía al procesador de imagen: `pkt+0x24` = saturación (`cfg+0x14e` + estilo creativo), `pkt+0x2a…0x2f` = Color Depth (`cfg+0x148…14d` + `cfg+0x3f0…3f5`), `pkt+0x29` = «hay Color Depth». El gancho
sustituye el `strb.w r2,[r7,#0x29]` de `0x437aa8ec` por `bl cueva`: la cueva suma la fila de la opción elegida (7 s8: Sat, R, Y, G, C, B, M), recorta a ±7 y fuerza el indicador `pkt+0x29` = 1. Off = ningún byte cambia.
shortcut: Color Chrome real es una corrección de luminancia dependiente de la saturación; aquí es Color Depth por sector de tono (el procesador aplica su propia función, que no está en `av-cam`); los pesos son estimaciones, no medidos en cámara.
Solo bytes del `av-cam` del `.dat`; sin construir CFW. `python3 scripts/g69/color_chrome_patch.py` = autocomprobación con Unicorn.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui")]
import cfw_ajustes as cfw
from e25_24.thumb import bl

BASE = 0x43541000
AJ = cfw.POR_ID["color_chrome"]
HOOK, HOOK_OLD = 0x437AA8EC, bytes.fromhex("87f82920")           # strb.w r2,[r7,#0x29]
CAVE, CAVE_END = 0x43FB7C00, 0x43FB7E00                          # entre el código de pp_tone (acaba ~0x43FB7990) y Silent (0x43FB7E00)
FILAS = ((0, 0, 0, 0, 0, 0, 0),                                  # (Sat, R, Y, G, C, B, M); +Color Depth = más profundo/oscuro, −Sat = menos saturado
         (0, 2, 2, 2, 2, 2, 2),                                  # Color Chrome Débil
         (0, 4, 4, 4, 4, 4, 4),                                  # Color Chrome Fuerte
         (-2, 2, -1, 2, 2, 3, 1),                                # Clásico (Classic Chrome): poco saturado, azules/verdes/rojos profundos
         (3, 2, 1, 3, 2, 3, 2),                                  # Vivo (Velvia): saturado y profundo
         (-1, -2, -1, -1, -1, -1, -1))                           # Suave (Pro Neg. Std): menos saturado, tonos de piel claros


def asm_src() -> str:
    leer = cfw.leer_asm(AJ, "cc")
    return f"""
        push {{r0-r6, lr}}
        {leer}
        cbz r0, nada
        adr.w r4, filas
        adds r4, r4, r0
        adds r3, r7, #0x24
        ldrsb r1, [r3]
        cmn r1, #8
        beq sinsat
        ldrsb r0, [r4]
        bl adj
    sinsat:
        adds r4, r4, #1
        adds r3, r7, #0x2a
        movs r6, #6
    lazo:
        ldrsb r0, [r4]
        bl adj
        adds r3, r3, #1
        adds r4, r4, #1
        subs r6, r6, #1
        bne lazo
        movs r0, #1
        str r0, [sp, #8]
    nada:
        pop {{r0-r6, lr}}
        strb.w r2, [r7, #0x29]
        bx lr
    adj:
        cbz r0, ret
        ldrsb r2, [r3]
        adds r1, r2, r0
        cmp r1, #7
        ble tope
        movs r1, #7
    tope:
        cmn r1, #7
        bge fin
        movs r1, #0
        subs r1, r1, #7
    fin:
        strb r1, [r3]
    ret:
        bx lr
        .align 2
    filas:
        {"".join(".byte " + ",".join(str(v & 0xFF) for v in f) + ",0" + chr(10) + "        " for f in FILAS)}
    """


def cave_bytes() -> bytes:
    code = cfw.ensamblar(asm_src(), CAVE)
    assert len(code) <= CAVE_END - CAVE, len(code)
    return code


def apply_bytes(data: bytes) -> bytes:
    if len(data) != 11_427_236:
        raise ValueError("tamaño inesperado")
    h = HOOK - BASE
    if data[h:h + 4] != HOOK_OLD:
        raise ValueError("gancho 0x437aa8ec distinto del original")
    if any(data[CAVE - BASE:CAVE_END - BASE]):
        raise ValueError("la cueva 0x43FB7C00 no está a cero")
    out = bytearray(data)
    code = cave_bytes()
    out[CAVE - BASE:CAVE - BASE + len(code)] = code
    out[h:h + 4] = bl(HOOK, CAVE)
    return bytes(out)


def emular(img: bytes, opcion: int | None, depth=(0,) * 6, sat: int = 0, r2: int = 0):
    """Ejecuta el tramo `0x437aa856…0x437aa8f0` del builder (cfg falso, Backup simulado con el índice `opcion`) y devuelve (pkt+0x24, pkt+0x2a…0x2f, pkt+0x29).
    `depth` = Color Depth del usuario en el orden del cfg 0x148…0x14d (R, G, B, C, M, Y); `sat` = cfg+0x14e."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_R3,
        UC_ARM_REG_R7,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE & ~0xFFF, ((len(img) + (BASE & 0xFFF)) + 0x200000) & ~0xFFF)
    mu.mem_write(BASE, img)
    if opcion is not None:     # Backup_read simulado: escribe `opcion` en [r1] y devuelve 0 (g56)
        mu.mem_write(0x435613B0, bytes([opcion, 0x22, 0x0A, 0x70, 0x00, 0x20, 0x70, 0x47]))
    stack, cfg, pkt, end = 0x10000000, 0x20000000, 0x21000000, 0x30000000
    mu.mem_map(stack - 0x10000, 0x20000)
    mu.mem_map(cfg, 0x1000)
    mu.mem_map(pkt, 0x1000)
    mu.mem_map(end, 0x1000)
    mu.mem_write(cfg + 0x148, bytes(v & 0xFF for v in depth))
    mu.mem_write(cfg + 0x14E, bytes([sat & 0xFF]))
    mu.reg_write(UC_ARM_REG_SP, stack)
    mu.reg_write(UC_ARM_REG_R3, cfg)
    mu.reg_write(UC_ARM_REG_R7, pkt)
    mu.reg_write(UC_ARM_REG_LR, end | 1)
    mu.emu_start(0x437AA856 | 1, 0x437AA8F0, count=2000)
    p = bytes(mu.mem_read(pkt, 0x40))
    s = lambda b: struct.unpack("b", bytes([b]))[0]
    return s(p[0x24]), [s(b) for b in p[0x2A:0x30]], p[0x29]


if __name__ == "__main__":
    img = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
    p = apply_bytes(img)
    print("cueva", len(cave_bytes()), "B")
    for o in range(len(FILAS)):
        print(o, FILAS[o], emular(p, o))
