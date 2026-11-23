#!/usr/bin/env python3
"""G97 — lado `av-cam` de las simulaciones de película: LUT 5×9×9 + curva 1D tras la gamma (LUT-T-1) desde el blob «FILM» del Backup.

El userland (`film_userland`, hilo en `viewUnified2.so`) deja en el id `0x150005` el look activo (tabla empaquetada a 21 bits en la ranura 0 y curva de 1024 u16
en +0x1000) y en el id de 1 B `ACK_ID` su número (0 = Off). Aquí, todo en la zona A verificada (G72):
- **LUT**: los dos ganchos de `lut_patch` (`0x4381d2fe` SA, `0x4381d372` MOV/MON/CAP): con ACK ≠ 0 y blob válido del mismo look entregan su tabla desempaquetada
  (búfer de `malloc` de 0x654 B); si no, el puntero de fábrica.
- **Máquina** (`0x437a2502`, FN-LUT-2): al cambiar el ACK fuerza el Copy3DLUT en esa misma pasada (la LUT cambia en vivo).
- **Curva** (LUT-T-1): las dos llamadas a `FUN_438538e4` (`0x43854da0`, `0x43854e54`) pasan por una cueva que llama a la original y, con look activo y curva
  en el blob, reescribe los 512 valores de `obj+0x26e` como `T[min(v, 1023)]` antes de que `FUN_43854a28` los copie (`memcpy` siguiente). Es lo mismo que la
  ranura `c68[8]` con `bd5` (G92 §3) sin tocar tablas globales ni indicadores. Off = la función original intacta.
`python3 film_patch.py` = autocomprobación con Unicorn.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/lut")]
import avcam_dinamico as D
import cfw_ajustes as cfw
import film_userland as FU
import lut_patch as L
from e25_24.thumb import bl

BASE, SIZE = L.BASE, L.SIZE
CELDA = D.ZONA_A[0]                         # +0 búfer del ISP (0x654) · +4 búfer del blob (16 KB) · +8 último ACK visto por la máquina
CODIGO = CELDA + 0x10
F_CADENA = 0x438538E4
HOOKS_T = (0x43854DA0, 0x43854E54)          # bl FUN_438538e4 dentro de FUN_43854a28
NLOOKS = len(FU.orden())


def _c(r: str, v: int) -> str:
    return f"movw {r}, #{v & 0xFFFF:#x}\n    movt {r}, #{v >> 16:#x}\n"


def codigo() -> tuple[bytes, dict[str, int]]:
    """Código de la cueva (ensamblado en CODIGO) y sus entradas: lut0, lut1, maquina, curva."""
    guard = [h[3] for h in L.HOOKS]
    dst = [h[2] for h in L.HOOKS]
    src = f"""
lee_ack:
    push {{lr}}
    sub sp, #8
    movs r0, #0
    str r0, [sp]
    {_c('r0', FU.ACK_ID)}
    mov r1, sp
    bl #{cfw.BACKUP_READ:#x}
    ldrb r0, [sp]
    add sp, #8
    cmp r0, #{NLOOKS + 1}
    blo.w ack_ok
    movs r0, #0
ack_ok:
    pop {{pc}}

blob:
    push {{r4, r5, lr}}
    mov r4, r0
    {_c('r5', CELDA)}
    ldr r0, [r5, #4]
    cmp r0, #0
    bne.w blob_hay
    movw r0, #{FU.BK_TAM}
    {_c('r1', D.MALLOC | 1)}
    blx r1
    cmp r0, #0
    beq.w blob_no
    str r0, [r5, #4]
blob_hay:
    mov r5, r0
    {_c('r0', FU.BK_ID)}
    mov r1, r5
    bl #{cfw.BACKUP_READ:#x}
    ldr r0, [r5]
    {_c('r1', FU.MAGIC)}
    cmp r0, r1
    bne.w blob_no
    ldrb r0, [r5, #5]
    cmp r0, r4
    bne.w blob_no
    mov r0, r5
    pop {{r4, r5, pc}}
blob_no:
    movs r0, #0
    pop {{r4, r5, pc}}

desemp:
    push {{r4-r8, lr}}
    bl lee_ack
    cmp r0, #0
    beq.w fallo
    bl blob
    cmp r0, #0
    beq.w fallo
    ldrb r1, [r0, #8]
    cmp r1, #1
    bne.w fallo
    adds r4, r0, #16
    {_c('r5', CELDA)}
    ldr r6, [r5]
    cmp r6, #0
    bne.w tengo
    movw r0, #{D.TAM:#x}
    {_c('r1', D.MALLOC | 1)}
    blx r1
    cmp r0, #0
    beq.w fallo
    str r0, [r5]
    mov r6, r0
tengo:
    {_c('r7', D.PERM)}
    movs r5, #0
    movs r3, #0
{D._LUT_BUCLE}
""" + "".join(f"""
lut{k}:
    push {{{guard[k]}, lr}}
    bl desemp
    cmp r0, #0
    beq.w orig{k}
    mov {dst[k]}, r0
    pop {{{guard[k]}, lr}}
    bx lr
orig{k}:
    ldr.w {dst[k]}, [r5, #0xc4]
    pop {{{guard[k]}, lr}}
    bx lr
""" for k in range(2)) + f"""
maquina:
    push {{r0, r1, lr}}
    bl lee_ack
    {_c('r1', CELDA + 8)}
    ldrb r2, [r1]
    cmp r0, r2
    beq.w m_sal
    strb r0, [r1]
    ldr r3, [sp]
    cmp r3, #0
    beq.w m_sal
    ldr r2, [r3, #0xc]
    ldr r3, [r3, #8]
    cmp r2, #0
    beq.w m_sal
    cmp r3, #0
    beq.w m_sal
    movs r1, #1
    strb.w r1, [r2, #0x8a0]
    strb.w r1, [r3, #0x94]
m_sal:
    pop {{r0, r1, lr}}
    ldr r7, [r0, #8]
    ldr r3, [r0]
    bx lr

curva:
    push {{r4-r7, lr}}
    mov r4, r0
    bl #{F_CADENA:#x}
    bl lee_ack
    cmp r0, #0
    beq.w c_fin
    bl blob
    cmp r0, #0
    beq.w c_fin
    ldrb r1, [r0, #9]
    cmp r1, #1
    bne.w c_fin
    add.w r5, r0, #{FU.OFF_T:#x}
    addw r6, r4, #0x26e
    movs r7, #0
    movw r2, #1023
c_bucle:
    ldrh.w r1, [r6, r7, lsl #1]
    cmp r1, r2
    it hi
    movhi r1, r2
    ldrh.w r1, [r5, r1, lsl #1]
    strh.w r1, [r6, r7, lsl #1]
    adds r7, #1
    cmp.w r7, #512
    blo.w c_bucle
c_fin:
    pop {{r4-r7, pc}}
    .align 2
"""
    sim = _simbolos(src)
    c = cfw.ensamblar(src, CODIGO)
    assert CODIGO + len(c) <= D.ZONA_A[1], hex(CODIGO + len(c))
    return c, {k: CODIGO + v for k, v in sim.items()}


def _simbolos(src: str) -> dict[str, int]:
    """Desplazamientos de las etiquetas de entrada: se ensambla hasta cada etiqueta (el código no depende de lo que sigue)."""
    out = {}
    for et in ("lut0", "lut1", "maquina", "curva"):
        pre = src[:src.index(f"\n{et}:")]
        out[et] = len(cfw.ensamblar(pre + "\n" + f"{et}:\n    nop\n", CODIGO)) - 2
    return out


def apply_bytes(data: bytes) -> bytes:
    if len(data) != SIZE:
        raise ValueError("tamaño inesperado")
    c, ent = codigo()
    orig_t = [bl(h, F_CADENA) for h in HOOKS_T]
    for va, old, _, _ in L.HOOKS:
        if data[va - BASE:va - BASE + 4] != old:
            raise ValueError(f"gancho {va:#x} distinto del original")
    if data[L.HOOK_MAQ[0] - BASE:L.HOOK_MAQ[0] - BASE + 4] != L.HOOK_MAQ[1]:
        raise ValueError("gancho de la máquina distinto del original")
    for h, o in zip(HOOKS_T, orig_t):
        if data[h - BASE:h - BASE + 4] != o:
            raise ValueError(f"gancho de curva {h:#x} distinto del original")
    esc = [(CELDA, bytes(0x10)), (CODIGO, c)]
    D.comprobar_zonas([(a, a + len(b)) for a, b in esc])
    out = bytearray(data)
    for a, b in esc:
        if any(data[a - BASE:a - BASE + len(b)]):
            raise ValueError(f"la zona {a:#x} no está a cero")
        out[a - BASE:a - BASE + len(b)] = b
    for (va, _, _, _), e in zip(L.HOOKS, (ent["lut0"], ent["lut1"])):
        out[va - BASE:va - BASE + 4] = bl(va, e)
    out[L.HOOK_MAQ[0] - BASE:L.HOOK_MAQ[0] - BASE + 4] = bl(L.HOOK_MAQ[0], ent["maquina"])
    for h in HOOKS_T:
        out[h - BASE:h - BASE + 4] = bl(h, ent["curva"])
    return bytes(out)


# ---------- emulación ----------
def _maquina_unicorn(img: bytes, ack: int, blob: bytes | None):
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE & ~0xFFF, ((len(img) + (BASE & 0xFFF)) + 0x200000) & ~0xFFF)
    mu.mem_write(BASE, img)
    stack, obj, end, heap, cnt, bk = 0x10000000, 0x20000000, 0x30000000, 0x31000000, 0x30100000, 0x32000000
    for a, s in ((stack - 0x10000, 0x20000), (obj, 0x2000), (end, 0x1000), (heap, 0x100000), (cnt, 0x1000), (bk, 0x8000)):
        mu.mem_map(a, s)
    if blob is not None:
        mu.mem_write(bk, blob)
    # Backup_read(id, buf) simulado: ACK → 1 byte; BK_ID → 16 KB del blob (o nada)
    stub = cfw.ensamblar(f"""
    {_c('r2', FU.ACK_ID)}
    cmp r0, r2
    bne.w otro
    movs r2, #{ack}
    strb r2, [r1]
    movs r0, #0
    bx lr
otro:
    {_c('r2', bk)}
    {_c('r3', FU.BK_TAM)}
cp:
    ldrb r0, [r2], #1
    strb r0, [r1], #1
    subs r3, #1
    bne.w cp
    movs r0, #0
    bx lr
""", cfw.BACKUP_READ)
    mu.mem_write(cfw.BACKUP_READ, stub)
    mu.mem_write(D.MALLOC, D.malloc_simulado(cnt))
    mu.mem_write(cnt + 4, struct.pack("<I", heap))
    return mu, dict(stack=stack, obj=obj, end=end, heap=heap, cnt=cnt)


def emula_lut(img: bytes, k: int, ack: int, blob: bytes | None, orig: int = 0x11223344) -> tuple[int, bytes]:
    """Gancho LUT `k` → (registro destino, 0x654 B del búfer del ISP)."""
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R1, UC_ARM_REG_R3, UC_ARM_REG_R5, UC_ARM_REG_SP
    mu, m = _maquina_unicorn(img, ack, blob)
    mu.mem_write(m["obj"] + 0xC4, struct.pack("<I", orig))
    mu.reg_write(UC_ARM_REG_SP, m["stack"])
    mu.reg_write(UC_ARM_REG_R5, m["obj"])
    mu.reg_write(UC_ARM_REG_LR, m["end"] | 1)
    ent = codigo()[1]
    # el heap simulado da siempre la misma dirección: la tabla del ISP y el blob se pisarían; se usa la 2.ª mitad para el blob
    mu.mem_write(CELDA + 4, struct.pack("<I", m["heap"] + 0x10000))
    mu.emu_start(ent[f"lut{k}"] | 1, m["end"], count=2_000_000)
    r = mu.reg_read(UC_ARM_REG_R3 if k == 0 else UC_ARM_REG_R1)
    return r, bytes(mu.mem_read(m["heap"], D.TAM))


def emula_curva(img: bytes, ack: int, blob: bytes | None, gamma_idx: int = 0) -> list[int]:
    """Cueva de la curva sobre un objeto mínimo como `tono_post.emula` (sin indicadores) → 512 valores de obj+0x26e."""
    import numpy as np
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP
    mu, m = _maquina_unicorn(img, ack, blob)
    o = bytearray(0x1000)
    o[0xBD9] = gamma_idx
    o[0xBDF], o[0xBDB], o[0xBDD] = 7, 3, 3
    o[0x66E:0x66E + 1024] = np.asarray(np.arange(512) * 4, "<u2").tobytes()
    struct.pack_into("<H", o, 0x66C, 0x3FF)
    mu.mem_write(m["obj"], bytes(o))
    mu.reg_write(UC_ARM_REG_R0, m["obj"])
    mu.reg_write(UC_ARM_REG_SP, m["stack"])
    mu.reg_write(UC_ARM_REG_LR, m["end"] | 1)
    mu.emu_start(codigo()[1]["curva"] | 1, m["end"], count=10_000_000)
    return list(struct.unpack("<512H", mu.mem_read(m["obj"] + 0x26E, 1024)))


if __name__ == "__main__":
    import cube_a6000 as C
    img = C.BIN.read_bytes()
    p = apply_bytes(img)
    c, ent = codigo()
    print("código", len(c), "B", {k: hex(v) for k, v in ent.items()}, "diff", sum(a != b for a, b in zip(img, p)), "B")
