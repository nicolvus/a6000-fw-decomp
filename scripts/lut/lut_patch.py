"""G71 — ajuste CFW «LUT» (Off/LUT1/LUT2/LUT3): sustituye el búfer de 0x654 B de la LUT 3D 5×9×9 que `av-cam` entrega al hardware por una tabla propia del `.dat`.

Dos ganchos de 4 B (`ldr.w rX,[r5,#0xc4]` → `bl cueva`) en la escritura de `0x4381d2a0…0x4381d386`: SA (`0x4381d2fe`, rX = r3, hacia `0x43b67a68`) y MOV/MON/CAP (`0x4381d372`, rX = r1, hacia `memcpy`).
Off = ningún byte cambia en la ruta (la cueva devuelve el puntero original). G73 puso la cueva en `ZONA_A` (`0x43BE3B28`) y las 3 tablas
empaquetadas a 21 bits por nodo (1064 B) en `ZONA_B` (`0x43C1FF24`); se desempaquetan al búfer de `malloc` (una sola reserva, celda
`LUT_CELDA`); si `malloc` falla se entrega el puntero original (fábrica).
**G107 §3 corrige a G72/G73: esas dos zonas NO son huecos** (`ZONA_A` es la tabla T1 de estabilización y `ZONA_B` las tablas BOKS del
YC de captura), así que el parche histórico escribe en memoria viva. Es la deuda **ZONA-1**: hay que reubicar cueva y tablas antes de
instalar. Lo que añade G115 va fuera de esas zonas (`lut_t.ZONA_T18`, hueco G18).
G115 (LUT-T-1): además de la tabla, el ajuste lleva la **curva 1D tras la gamma** (`lut_t`): cuatro ganchos en las llamadas a `FUN_43852f7c` y una cueva que, con el ajuste activo *y* curva para esa LUT, pone `bd5 = 1`, `be1 = 8`, `bd1 = bd3 = 0` y `c68[8]` = la curva expandida desde 33 nodos. Con Off no escribe nada (ni el objeto ni `c68[8]`). El mecanismo es el mismo de `film_patch` (G98), que ocupa esos mismos ganchos y el mismo id de Backup: **un build lleva Film o LUT, no los dos** (aquí se comprueba y se rechaza si ya están puestos).
shortcut: la matriz del `cube_a6000` no (vive en el preset de Backup: LUT-A); transición por LUT: solo las que se eligen con curva la llevan. `python3 scripts/lut/lut_patch.py` = autocomprobación con Unicorn.
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
import lut_t as TT
from e25_24.thumb import bl

BASE = 0x43541000
SIZE = 11_427_236
AJ = cfw.POR_ID["lut"]          # id/backup del ajuste (Backup 0x1070211 guarda el índice de ranura)
SD_RANURAS = 6                                                             # G89: Off + 6 ranuras = 7 opciones (tope medido de la fila, G36)
AJ_SD = dataclasses.replace(AJ, opciones=(("Off", 0),) + tuple((f"LUT {i}", i) for i in range(1, SD_RANURAS + 1)))
HOOKS = ((0x4381D2FE, bytes.fromhex("d5f8c430"), "r3", "r0, r1, r2"),     # ldr.w r3,[r5,#0xc4]
         (0x4381D372, bytes.fromhex("d5f8c410"), "r1", "r0, r2, r3"))     # ldr.w r1,[r5,#0xc4]
HOOK_MAQ = (0x437A2502, bytes.fromhex("87680368"))                         # ldr r7,[r0,#8]; ldr r3,[r0] al entrar la máquina «[LUT] Write Cnt» 0x437a24fc (FN-LUT-2)
TAM = 0x654
FUENTES = ("teal_orange", "pelicula", "identidad")                         # LUT1…3 por defecto; `--cube` de cube_a6000 las sustituye


def entradas() -> list[int]:
    """Direcciones de f0/f1 (SA/r3, MOV/r1)."""
    return D.lut_codigo(AJ_SD, HOOKS)[1]


def cueva_maquina() -> tuple[int, list[tuple[int, bytes]]]:
    """(entrada, escrituras) de la cueva del gancho de la máquina; va tras el código de la LUT en `ZONA_L18` (G18)."""
    cueva, _ = D.lut_codigo(AJ_SD, HOOKS)
    fin = max(a + len(b) for a, b in cueva)
    esc, entrada = D.lut_maquina_codigo(AJ_SD, (fin + 3) & ~3)
    return entrada, esc


def entrada_t() -> int:
    """Entrada de la cueva de la curva (`lut_t`) en la disposición que monta `apply_bytes`."""
    return TT.escrituras(AJ_SD)[1]


def apply_bytes(data: bytes) -> bytes:
    """Parche `av-cam` del ajuste LUT (G116): cueva, máquina y curva en `ZONA_L18`/`ZONA_T18` (hueco G18); tablas y curvas salen del blob de la SD.
    Sin tarjeta no hay tabla ni curva y el ajuste queda en fábrica."""
    if len(data) != SIZE:
        raise ValueError("tamaño inesperado")
    for va, old, _, _ in HOOKS:
        if data[va - BASE:va - BASE + 4] != old:
            raise ValueError(f"gancho {va:#x} distinto del original")
    cueva, ent = D.lut_codigo(AJ_SD, HOOKS)
    esc = list(cueva) + [(D.LUT_CELDA, bytes(8))]
    entrada, maq = cueva_maquina()
    if data[HOOK_MAQ[0] - BASE:HOOK_MAQ[0] - BASE + 4] != HOOK_MAQ[1]:
        raise ValueError(f"gancho {HOOK_MAQ[0]:#x} distinto del original")
    esc += maq
    t_esc, t_ent = TT.escrituras(AJ_SD)                   # la curva va a G18, no a ZONA_A/ZONA_B (G107)
    esc += t_esc
    for h in TT.SITIOS_T:
        if data[h - BASE:h - BASE + 4] != bl(h, TT.F_PREP):
            raise ValueError(f"gancho de curva {h:#x} distinto del original (¿build con la curva de Film?)")
    D.comprobar_zonas([(a, a + len(b)) for a, b in esc], (D.ZONA_L18, TT.ZONA_T18))
    out = bytearray(data)
    for a, b in esc:
        if any(data[a - BASE:a + len(b) - BASE]):
            raise ValueError(f"la zona {a:#x} no está a cero")
        out[a - BASE:a - BASE + len(b)] = b
    for (va, _, _, _), e in zip(HOOKS, ent):
        out[va - BASE:va - BASE + 4] = bl(va, e)
    out[HOOK_MAQ[0] - BASE:HOOK_MAQ[0] - BASE + 4] = bl(HOOK_MAQ[0], entrada)
    for h in TT.SITIOS_T:
        out[h - BASE:h - BASE + 4] = bl(h, t_ent)
    return bytes(out)


def emular(img: bytes, k: int, opcion: int, blob: bytes, orig: int = 0x11223344,
           malloc_falla_en: int | None = None) -> tuple[int, bytes | None, dict]:
    """Ejecuta la cueva `k` (0 = SA/r3, 1 = MOV/r1) con el Backup simulado: `[Ajustes]` = `opcion` y el blob de la SD (id `BK_ID`) = `blob`.
    Devuelve (registro destino, búfer del ISP de 0x654 B o None si quedó el puntero original, estado con `mallocs`/`lecturas`)."""
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R3,
        UC_ARM_REG_R5,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE & ~0xFFF, ((len(img) + (BASE & 0xFFF)) + 0x200000) & ~0xFFF)
    mu.mem_write(BASE, img)
    mu.mem_write(0x435613B0, bytes([opcion, 0x22, 0x0A, 0x70, 0x00, 0x20, 0x70, 0x47]))
    stack, obj, end, heap = 0x10000000, 0x20000000, 0x30000000, 0x31000000
    for a, t in ((stack - 0x10000, 0x20000), (obj, 0x1000), (end, 0x1000), (heap, 0x100000)):
        mu.mem_map(a, t)
    mu.mem_write(obj + 0xC4, struct.pack("<I", orig))
    est = {"mallocs": [], "lecturas": []}
    brk = [heap]

    def hook(mu, a, _s, _):
        if a == D.MALLOC & ~1:
            n = mu.reg_read(UC_ARM_REG_R0)
            est["mallocs"].append(n)
            r = 0 if malloc_falla_en == len(est["mallocs"]) else brk[0]
            brk[0] += (n + 15) & ~15
            mu.reg_write(UC_ARM_REG_R0, r)
        elif a == cfw.BACKUP_READ:
            i = mu.reg_read(UC_ARM_REG_R0)
            est["lecturas"].append(i)
            mu.mem_write(mu.reg_read(UC_ARM_REG_R1), bytes([opcion]) if i == AJ.backup else blob)
            mu.reg_write(UC_ARM_REG_R0, 0)
        else:
            return
        mu.reg_write(UC_ARM_REG_PC, mu.reg_read(UC_ARM_REG_LR) | 1)

    mu.hook_add(UC_HOOK_CODE, hook, begin=D.MALLOC & ~1, end=(D.MALLOC & ~1) + 1)
    mu.hook_add(UC_HOOK_CODE, hook, begin=0x435613B0, end=0x435613B1)
    mu.reg_write(UC_ARM_REG_SP, stack)
    mu.reg_write(UC_ARM_REG_R5, obj)
    mu.reg_write(UC_ARM_REG_LR, end | 1)
    mu.emu_start(entradas()[k] | 1, end, count=500000)
    r = mu.reg_read(UC_ARM_REG_R3 if k == 0 else UC_ARM_REG_R1)
    return r, (bytes(mu.mem_read(r, TAM)) if r != orig else None), est


if __name__ == "__main__":
    import lut_sd_userland as U
    img = C.BIN.read_bytes()
    p = apply_bytes(img)
    fin = max(a + len(b) for a, b in cueva_maquina()[1])
    print("código", [hex(e) for e in entradas()], "curva", hex(TT.cueva((fin + 3) & ~3)[1]),
          "diff", sum(a != b for a, b in zip(img, p)), "B")
    blob = bytes(U.BK_TAM)                                                   # sin tabla válida: siempre el puntero de fábrica
    for k in (0, 1):
        print(k, [hex(emular(p, k, o, blob)[0]) for o in range(5)])
