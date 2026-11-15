"""G71 — ajuste CFW «LUT» (Off/LUT1/LUT2/LUT3): sustituye el búfer de 0x654 B de la LUT 3D 5×9×9 que `av-cam` entrega al hardware por una tabla propia del `.dat`.

Dos ganchos de 4 B (`ldr.w rX,[r5,#0xc4]` → `bl cueva`) en la escritura de `0x4381d2a0…0x4381d386`: SA (`0x4381d2fe`, rX = r3, hacia `0x43b67a68`) y MOV/MON/CAP (`0x4381d372`, rX = r1, hacia `memcpy`).
Off = ningún byte cambia en la ruta (la cueva devuelve el puntero original). La cueva y las 3 tablas van en `0x43FA4000` (zona a cero de 2,3 MB, como HLG; G72: NO está libre, es memoria viva; parche bloqueado por `ZONA_VERIFICADA`: LUT-C).
shortcut: solo la etapa LUT 3D está integrada; matriz y curva del `cube_a6000` no (la matriz vive en el preset de Backup y la curva no tiene hueco: LUT-A). `python3 scripts/lut/lut_patch.py` = autocomprobación con Unicorn.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/lut")]
import cfw_ajustes as cfw
import cube_a6000 as C
from e25_24.thumb import bl

BASE = 0x43541000
SIZE = 11_427_236
AJ = cfw.POR_ID["lut"]
HOOKS = ((0x4381D2FE, bytes.fromhex("d5f8c430"), "r3", "r0, r1, r2"),     # ldr.w r3,[r5,#0xc4]
         (0x4381D372, bytes.fromhex("d5f8c410"), "r1", "r0, r2, r3"))     # ldr.w r1,[r5,#0xc4]
CODE, TABLES = 0x43FA4000, 0x43FA4200
ZONA_VERIFICADA = False  # G72: 0x43FA4000 es memoria viva (402 B no nulos en el volcado de RAM, `completed` en 0x43FA4B1E); bloqueado hasta reubicar (LUT-C)
TAM = 0x654
FUENTES = ("teal_orange", "pelicula", "identidad")                         # LUT1…3 por defecto; `--cube` de cube_a6000 las sustituye


def tablas_por_defecto() -> list[bytes]:
    img = C.BIN.read_bytes()
    out = []
    for n in FUENTES:
        ch = C.descompone(C.SINT[n], False, False, True)
        out.append(C.empaqueta_hw(ch.q, img))
    return out


def asm_src() -> str:
    partes = []
    for k, (_, _, dst, guardar) in enumerate(HOOKS):
        partes.append(f"""
    f{k}:
        push {{{guardar}, lr}}
        {cfw.leer_asm(AJ, f"t{k}")}
        cmp r0, #0
        beq.w o{k}
        subs r0, r0, #1
        movw r1, #{TAM:#x}
        muls r0, r0, r1
        movw r1, #{TABLES & 0xFFFF:#x}
        movt r1, #{TABLES >> 16:#x}
        adds {dst}, r0, r1
        pop {{{guardar}, lr}}
        bx lr
    o{k}:
        ldr.w {dst}, [r5, #0xc4]
        pop {{{guardar}, lr}}
        bx lr
        .align 2
        """)
    return "\n".join(partes)


def entradas() -> list[int]:
    """Direcciones de f0/f1: se miden ensamblando cada una por separado."""
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    ks, a, out = Ks(KS_ARCH_ARM, KS_MODE_THUMB), CODE, []
    for k in range(len(HOOKS)):
        out.append(a)
        a += len(ks.asm(_una(k), a)[0])
        a = (a + 3) & ~3
    return out


def _una(k: int) -> str:
    return asm_src().split("    f1:")[0] if k == 0 else "    f1:" + asm_src().split("    f1:")[1]


def apply_bytes(data: bytes, tablas: list[bytes] | None = None) -> bytes:
    if len(data) != SIZE:
        raise ValueError("tamaño inesperado")
    if not ZONA_VERIFICADA:
        raise RuntimeError("LUT: 0x43FA4000 es memoria viva (G72); reubicar antes de construir (LUT-C)")
    tablas = tablas or tablas_por_defecto()
    assert len(tablas) == 3 and all(len(t) == TAM for t in tablas)
    for va, old, _, _ in HOOKS:
        if data[va - BASE:va - BASE + 4] != old:
            raise ValueError(f"gancho {va:#x} distinto del original")
    if any(data[CODE - BASE:TABLES + 3 * TAM - BASE]):
        raise ValueError("la zona 0x43FA4000 no está a cero")
    out = bytearray(data)
    a = CODE
    for k, (va, _, _, _) in enumerate(HOOKS):
        code = cfw.ensamblar(_una(k), a)
        out[a - BASE:a - BASE + len(code)] = code
        out[va - BASE:va - BASE + 4] = bl(va, a)
        a = (a + len(code) + 3) & ~3
    assert a <= TABLES, hex(a)
    for i, t in enumerate(tablas):
        out[TABLES + i * TAM - BASE:TABLES + (i + 1) * TAM - BASE] = t
    return bytes(out)


def emular(img: bytes, k: int, opcion: int, orig: int = 0x11223344) -> int:
    """Ejecuta la cueva `k` (0 = SA/r3, 1 = MOV/r1) con el Backup simulado = `opcion` y `[r5+0xc4]` = `orig`; devuelve el registro destino."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_R1,
        UC_ARM_REG_R3,
        UC_ARM_REG_R5,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE & ~0xFFF, ((len(img) + (BASE & 0xFFF)) + 0x200000) & ~0xFFF)
    mu.mem_write(BASE, img)
    mu.mem_write(0x435613B0, bytes([opcion, 0x22, 0x0A, 0x70, 0x00, 0x20, 0x70, 0x47]))
    stack, obj, end = 0x10000000, 0x20000000, 0x30000000
    for a, s in ((stack - 0x10000, 0x20000), (obj, 0x1000), (end, 0x1000)):
        mu.mem_map(a, s)
    mu.mem_write(obj + 0xC4, struct.pack("<I", orig))
    mu.reg_write(UC_ARM_REG_SP, stack)
    mu.reg_write(UC_ARM_REG_R5, obj)
    mu.reg_write(UC_ARM_REG_LR, end | 1)
    mu.emu_start(entradas()[k] | 1, end, count=5000)
    return mu.reg_read(UC_ARM_REG_R3 if k == 0 else UC_ARM_REG_R1)


if __name__ == "__main__":
    ZONA_VERIFICADA = True  # autocomprobación de bytes; no apto para construir (G72)
    img = C.BIN.read_bytes()
    p = apply_bytes(img)
    print("código", entradas(), "diff", sum(a != b for a, b in zip(img, p)), "B")
    for k in (0, 1):
        print(k, [hex(emular(p, k, o)) for o in range(5)])
