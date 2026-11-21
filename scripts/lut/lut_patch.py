"""G71 — ajuste CFW «LUT» (Off/LUT1/LUT2/LUT3): sustituye el búfer de 0x654 B de la LUT 3D 5×9×9 que `av-cam` entrega al hardware por una tabla propia del `.dat`.

Dos ganchos de 4 B (`ldr.w rX,[r5,#0xc4]` → `bl cueva`) en la escritura de `0x4381d2a0…0x4381d386`: SA (`0x4381d2fe`, rX = r3, hacia `0x43b67a68`) y MOV/MON/CAP (`0x4381d372`, rX = r1, hacia `memcpy`).
Off = ningún byte cambia en la ruta (la cueva devuelve el puntero original). G73: la cueva va en el fragmento libre verificado `0x43BE3B28` y las 3 tablas, empaquetadas a 21 bits por nodo (1064 B), en `0x43C1FF24`; se desempaquetan al búfer de `malloc` (una sola reserva, celda `LUT_CELDA`); si `malloc` falla se entrega el puntero original (fábrica).
shortcut: solo la etapa LUT 3D está integrada; matriz y curva del `cube_a6000` no (la matriz vive en el preset de Backup y la curva no tiene hueco: LUT-A). `python3 scripts/lut/lut_patch.py` = autocomprobación con Unicorn.
"""
from __future__ import annotations

import dataclasses
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/lut")]
import avcam_dinamico as D
import cfw_ajustes as cfw
import cube_a6000 as C
from e25_24.thumb import bl

BASE = 0x43541000
SIZE = 11_427_236
AJ = cfw.POR_ID["lut"]
SD_RANURAS = 6                                                             # G89: Off + 6 ranuras = 7 opciones (tope medido de la fila, G36)
AJ_SD = dataclasses.replace(AJ, opciones=(("Off", 0),) + tuple((f"LUT {i}", i) for i in range(1, SD_RANURAS + 1)))
HOOKS = ((0x4381D2FE, bytes.fromhex("d5f8c430"), "r3", "r0, r1, r2"),     # ldr.w r3,[r5,#0xc4]
         (0x4381D372, bytes.fromhex("d5f8c410"), "r1", "r0, r2, r3"))     # ldr.w r1,[r5,#0xc4]
HOOK_MAQ = (0x437A2502, bytes.fromhex("87680368"))                         # ldr r7,[r0,#8]; ldr r3,[r0] al entrar la máquina «[LUT] Write Cnt» 0x437a24fc (FN-LUT-2)
TAM = 0x654
FUENTES = ("teal_orange", "pelicula", "identidad")                         # LUT1…3 por defecto; `--cube` de cube_a6000 las sustituye


_DEFECTO: list[bytes] = []                                                 # G90: el ajuste en ΔE2000 tarda ~15 s por tabla; se calcula una vez por proceso


def tablas_por_defecto() -> list[bytes]:
    if not _DEFECTO:
        img = C.BIN.read_bytes()
        _DEFECTO.extend(C.empaqueta_hw(C.descompone(C.SINT[n], False, False, True).q, img) for n in FUENTES)
    return list(_DEFECTO)


MODO_SD = False                                                            # G89: los builds (build_fn_lut/build_cfw_objetivos) lo activan con sd=True; `apply_bytes` lo usa por defecto


def entradas(sd: bool = False) -> list[int]:
    """Direcciones de f0/f1 (SA/r3, MOV/r1)."""
    return D.lut_codigo(AJ_SD if sd else AJ, HOOKS, sd)[1]


def cueva_maquina(sd: bool = False) -> tuple[int, list[tuple[int, bytes]]]:
    """(entrada, escrituras) de la cueva del gancho de la máquina; va tras el código de la LUT en la zona A."""
    cueva, _ = D.lut_codigo(AJ_SD if sd else AJ, HOOKS, sd)
    fin = max(a + len(b) for a, b in cueva)
    esc, entrada = D.lut_maquina_codigo(AJ_SD if sd else AJ, (fin + 3) & ~3)
    return entrada, esc


def apply_bytes(data: bytes, tablas: list[bytes] | None = None, sd: bool | None = None) -> bytes:
    sd = MODO_SD if sd is None else sd
    if len(data) != SIZE:
        raise ValueError("tamaño inesperado")
    tablas = tablas or tablas_por_defecto()
    assert len(tablas) == 3 and all(len(t) == TAM for t in tablas)
    for va, old, _, _ in HOOKS:
        if data[va - BASE:va - BASE + 4] != old:
            raise ValueError(f"gancho {va:#x} distinto del original")
    perm = list(struct.unpack_from("<405H", data, D.PERM - BASE))
    cueva, ent = D.lut_codigo(AJ_SD if sd else AJ, HOOKS, sd)
    esc = list(cueva) + [(D.LUT_TABLAS, b"".join(D.empaqueta_21(t, perm) for t in tablas)), (D.LUT_CELDA, bytes(8 if sd else 4))]
    D.comprobar_zonas([(a, a + len(b)) for a, b in esc])
    entrada, maq = cueva_maquina(sd)
    if data[HOOK_MAQ[0] - BASE:HOOK_MAQ[0] - BASE + 4] != HOOK_MAQ[1]:
        raise ValueError(f"gancho {HOOK_MAQ[0]:#x} distinto del original")
    esc += maq
    D.comprobar_zonas([(a, a + len(b)) for a, b in esc])
    out = bytearray(data)
    for a, b in esc:
        if any(data[a - BASE:a + len(b) - BASE]):
            raise ValueError(f"la zona {a:#x} no está a cero")
        out[a - BASE:a - BASE + len(b)] = b
    for (va, _, _, _), e in zip(HOOKS, ent):
        out[va - BASE:va - BASE + 4] = bl(va, e)
    out[HOOK_MAQ[0] - BASE:HOOK_MAQ[0] - BASE + 4] = bl(HOOK_MAQ[0], entrada)
    return bytes(out)


def emular(img: bytes, k: int, opcion: int, orig: int = 0x11223344, malloc: int | None = 0x30001000, cuenta: list | None = None) -> int:
    """Ejecuta la cueva `k` (0 = SA/r3, 1 = MOV/r1) con el Backup simulado = `opcion`, `[r5+0xc4]` = `orig` y un `malloc` simulado (devuelve `malloc`, 0 = fallo); devuelve el registro destino.
    `cuenta` (lista de 1 elemento) recibe el nº de llamadas a `malloc`; el búfer simulado se deja en `emular.mem`."""
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
    stack, obj, end, heap, cnt = 0x10000000, 0x20000000, 0x30000000, 0x30001000, 0x30100000
    for a, s in ((stack - 0x10000, 0x20000), (obj, 0x1000), (end, 0x1000), (heap, 0x2000), (cnt, 0x1000)):
        mu.mem_map(a, s)
    mu.mem_write(D.MALLOC, D.malloc_simulado(cnt))
    mu.mem_write(cnt + 4, struct.pack("<I", malloc or 0))
    mu.mem_write(obj + 0xC4, struct.pack("<I", orig))
    mu.reg_write(UC_ARM_REG_SP, stack)
    mu.reg_write(UC_ARM_REG_R5, obj)
    mu.reg_write(UC_ARM_REG_LR, end | 1)
    mu.emu_start(entradas()[k] | 1, end, count=200000)
    if cuenta is not None:
        cuenta[0] = struct.unpack("<I", mu.mem_read(cnt, 4))[0]
    emular.mem = bytes(mu.mem_read(heap, TAM))
    return mu.reg_read(UC_ARM_REG_R3 if k == 0 else UC_ARM_REG_R1)


if __name__ == "__main__":
    img = C.BIN.read_bytes()
    p = apply_bytes(img)
    print("código", [hex(e) for e in entradas()], "diff", sum(a != b for a, b in zip(img, p)), "B")
    for k in (0, 1):
        print(k, [hex(emular(p, k, o)) for o in range(5)])
