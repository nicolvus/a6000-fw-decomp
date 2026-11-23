#!/usr/bin/env python3
"""G97/G98 — lado `av-cam` de las simulaciones de película: LUT 5×9×9 + curva 1D tras la gamma desde el blob «FILM» del Backup.

El userland (`film_userland`, hilo en `viewUnified2.so`) deja en el id `0x150005` el look activo (tabla empaquetada a 21 bits en la ranura 0 y curva de 1024 u16
en +0x1000) y en el id de 1 B `ACK_ID` su número (0 = Off). Aquí, todo en la zona A verificada (G72):
- **LUT**: los dos ganchos de `lut_patch` (`0x4381d2fe` SA, `0x4381d372` MOV/MON/CAP): con ACK ≠ 0 y blob válido del mismo look entregan su tabla desempaquetada
  (búfer de `malloc` de 0x654 B) y anotan el look aplicado; si no, el puntero de fábrica.
- **Máquina** (`0x437a2502`, FN-LUT-2): fuerza el Copy3DLUT al cambiar el ACK y, mientras el look aplicado no sea el del ACK (blob aún sin llegar), lo
  reintenta cada 32 pasadas (G98: el 3.87 daba el cambio por atendido aunque el blob no hubiera llegado y se quedaba con la LUT de fábrica).
- **Curva** (G98, mecanismo de la gamma extendida de Sony, el de `CameraEx.setExtendedGammaTable`): en las cuatro llamadas a `FUN_43852f7c` que preceden a la
  construcción de la curva (`0x438548b0`, `0x43854c46`, `0x43854ff6`, `0x43b098cc`; `r0` = objeto de tono, indicadores ya copiados de la config), con look
  activo y curva en el blob: copia la curva a un búfer propio, `c68[8]` (`0x440013ec`) = ese búfer y `bd5 = 1`, `be1 = 8`, `bd1 = bd3 = 0` (el firmware
  da prioridad a `bd1`/`bd3` sobre `bd5`). Así la aplican
  igual la curva de 512 puntos (`FUN_438538e4`) y la rejilla de 96 nodos que va al hardware (`FUN_43853200`); el 3.87 solo reescribía la de 512 puntos.
  Off: indicadores de fábrica y `c68[8]` vuelve a la identidad si era nuestro búfer.
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
CELDA = D.ZONA_A[0]          # +0 búfer del ISP (0x654) · +4 búfer del blob (16 KB) · +8 último ACK visto · +9 look aplicado · +0xa contador · +0xc búfer de la curva
CODIGO = CELDA + 0x10
F_PREP = 0x43852F7C          # FUN_43852f7c(obj de tono): primer paso de la curva, tras copiar los indicadores bd1/bd3/bd5/be1 de la config
SITIOS_T = (0x438548B0, 0x43854C46, 0x43854FF6, 0x43B098CC)
C68_8 = 0x440013EC           # c68[8]: ranura de la gamma extendida (G92 §3)
IDENTIDAD = 0x43BFAF2A
F_REJILLA, F_CADENA = 0x43853200, 0x438538E4
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
    mov r8, r0
    {_c('r1', CELDA)}
    movs r2, #0
    strb r2, [r1, #9]
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
    strb.w r8, [r5, #9]
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
    bne.w m_forzar
    ldrb r2, [r1, #1]
    cmp r0, r2
    beq.w m_sal
    ldrb r2, [r1, #2]
    adds r2, #1
    strb r2, [r1, #2]
    tst.w r2, #31
    bne.w m_sal
m_forzar:
    ldr r3, [sp]
    cmp r3, #0
    beq.w m_sal
    ldr r2, [r3, #0xc]
    ldr r3, [r3, #8]
    cmp r2, #0
    beq.w m_sal
    cmp r3, #0
    beq.w m_sal
    strb r0, [r1]
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
    bl lee_ack
    cmp r0, #0
    beq.w c_off
    bl blob
    cmp r0, #0
    beq.w c_off
    ldrb r1, [r0, #9]
    cmp r1, #1
    bne.w c_off
    add.w r5, r0, #{FU.OFF_T:#x}
    {_c('r7', CELDA)}
    ldr r6, [r7, #0xc]
    cmp r6, #0
    bne.w c_hay
    movw r0, #2048
    {_c('r1', D.MALLOC | 1)}
    blx r1
    cmp r0, #0
    beq.w c_off
    str r0, [r7, #0xc]
    mov r6, r0
c_hay:
    movs r3, #0
c_copia:
    ldr.w r1, [r5, r3, lsl #2]
    str.w r1, [r6, r3, lsl #2]
    adds r3, #1
    cmp.w r3, #512
    blo.w c_copia
    {_c('r1', C68_8)}
    str r6, [r1]
    movs r1, #1
    strb.w r1, [r4, #0xbd5]
    movs r1, #8
    strb.w r1, [r4, #0xbe1]
    movs r1, #0
    strb.w r1, [r4, #0xbd1]
    strb.w r1, [r4, #0xbd3]
    b.w c_fin
c_off:
    {_c('r7', CELDA)}
    ldr r6, [r7, #0xc]
    cmp r6, #0
    beq.w c_fin
    {_c('r1', C68_8)}
    ldr r2, [r1]
    cmp r2, r6
    bne.w c_fin
    {_c('r2', IDENTIDAD)}
    str r2, [r1]
c_fin:
    mov r0, r4
    pop {{r4-r7, lr}}
    b.w #{F_PREP:#x}
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
    orig_t = [bl(h, F_PREP) for h in SITIOS_T]
    for va, old, _, _ in L.HOOKS:
        if data[va - BASE:va - BASE + 4] != old:
            raise ValueError(f"gancho {va:#x} distinto del original")
    if data[L.HOOK_MAQ[0] - BASE:L.HOOK_MAQ[0] - BASE + 4] != L.HOOK_MAQ[1]:
        raise ValueError("gancho de la máquina distinto del original")
    for h, o in zip(SITIOS_T, orig_t):
        if data[h - BASE:h - BASE + 4] != o:
            raise ValueError(f"gancho de curva {h:#x} distinto del original")
    if struct.unpack_from("<I", data, C68_8 - BASE)[0] != IDENTIDAD:
        raise ValueError("c68[8] no es la identidad")
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
    for h in SITIOS_T:
        out[h - BASE:h - BASE + 4] = bl(h, ent["curva"])
    return bytes(out)


# ---------- emulación ----------
BK_SIM = 0x32000000


def _bk(mu, ack: int, blob: bytes | None) -> None:
    mu.mem_write(BK_SIM, blob if blob is not None else bytes(FU.BK_TAM))
    mu.mem_write(BK_SIM + 0x7000, bytes([ack]))


def _maquina_unicorn(img: bytes, ack: int, blob: bytes | None):
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE & ~0xFFF, ((len(img) + (BASE & 0xFFF)) + 0x200000) & ~0xFFF)
    mu.mem_write(BASE, img)
    stack, obj, end, heap, cnt, bk = 0x10000000, 0x20000000, 0x30000000, 0x31000000, 0x30100000, BK_SIM
    for a, s in ((stack - 0x10000, 0x20000), (obj, 0x2000), (end, 0x1000), (heap, 0x100000), (cnt, 0x1000), (bk, 0x8000)):
        mu.mem_map(a, s)
    _bk(mu, ack, blob)
    # Backup_read(id, buf) simulado: ACK → 1 byte (en BK_SIM + 0x7000); BK_ID → 16 KB del blob (o ceros)
    stub = cfw.ensamblar(f"""
    {_c('r2', FU.ACK_ID)}
    cmp r0, r2
    bne.w otro
    {_c('r2', bk + 0x7000)}
    ldrb r2, [r2]
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
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_R1,
        UC_ARM_REG_R3,
        UC_ARM_REG_R5,
        UC_ARM_REG_SP,
    )
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


def emula_tono(img: bytes, ack: int, blob: bytes | None, gamma_idx: int = 0, bd1: int = 1, entrada: str | None = "curva") -> dict:
    """Un paso de la construcción de la curva como en `FUN_43854a28`: gancho (`entrada`; None = `FUN_43852f7c` de fábrica) sobre un objeto de tono con los
    indicadores de fábrica (`bd1` = Black Gamma, `bd5 = 0`), y después las dos funciones reales que componen la curva: la rejilla de 96 nodos (`FUN_43853200`,
    va al hardware) y la curva de 512 puntos (`FUN_438538e4`). → {"rejilla": 96 valores, "curva": 512, "x96", "ok" (FUN_43853200 devolvió 0), "c68_8"}."""
    import numpy as np
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP
    mu, m = _maquina_unicorn(img, ack, blob)
    o = bytearray(0x2000)
    o[0xBD9], o[0xBD1], o[0xBDB] = gamma_idx, bd1, 3
    o[0xBDF], o[0xBDD] = 7, 3
    x96 = np.linspace(0, 2047, 96).astype(int)
    o[0x1AE:0x1AE + 192] = np.asarray(x96, "<u2").tobytes()
    o[0x66E:0x66E + 1024] = np.asarray(np.arange(512) * 4, "<u2").tobytes()
    struct.pack_into("<H", o, 0x66C, 0x3FF)
    mu.mem_write(m["obj"], bytes(o))
    mu.mem_write(CELDA + 4, struct.pack("<I", m["heap"] + 0x10000))      # el malloc simulado repite dirección: blob en la 2.ª mitad
    ent = codigo()[1]

    def llama(f):
        mu.reg_write(UC_ARM_REG_R0, m["obj"])
        mu.reg_write(UC_ARM_REG_SP, m["stack"])
        mu.reg_write(UC_ARM_REG_LR, m["end"] | 1)
        mu.emu_start(f | 1, m["end"], count=20_000_000)
        return mu.reg_read(UC_ARM_REG_R0)
    llama(ent[entrada] if entrada else F_PREP)
    ok = llama(F_REJILLA) == 0
    rejilla = list(struct.unpack("<96I", mu.mem_read(m["obj"], 384)))
    llama(F_CADENA)
    return {"rejilla": rejilla, "curva": list(struct.unpack("<512H", mu.mem_read(m["obj"] + 0x26E, 1024))), "x96": x96.tolist(), "ok": ok,
            "c68_8": struct.unpack("<I", mu.mem_read(C68_8, 4))[0]}


def emula_maquina(img: bytes, pasos: list[tuple[int, bytes | None]]) -> list[bool]:
    """Pasadas de la máquina (`maquina`) con (ACK, blob) por pasada; cuando fuerza, se ejecuta el gancho LUT como haría el Copy3DLUT de esa pasada.
    → por pasada, si forzó la recarga (`[obj+0x8a0] = 1`)."""
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_R0,
        UC_ARM_REG_R5,
        UC_ARM_REG_SP,
    )
    mu, m = _maquina_unicorn(img, 0, None)
    ent = codigo()[1]
    this, cfg, work = m["obj"] + 0x1000, m["obj"] + 0x1100, m["obj"]
    mu.mem_write(this, struct.pack("<4I", m["obj"] + 0x1200, 0, cfg, work))
    mu.mem_write(CELDA + 4, struct.pack("<I", m["heap"] + 0x10000))
    out = []
    for ack, blob in pasos:
        _bk(mu, ack, blob)
        mu.mem_write(work + 0x8A0, b"\0")
        mu.reg_write(UC_ARM_REG_R0, this)
        mu.reg_write(UC_ARM_REG_SP, m["stack"])
        mu.reg_write(UC_ARM_REG_LR, m["end"] | 1)
        mu.emu_start(ent["maquina"] | 1, m["end"], count=2_000_000)
        forzo = mu.mem_read(work + 0x8A0, 1)[0] == 1
        if forzo:
            mu.reg_write(UC_ARM_REG_SP, m["stack"])
            mu.reg_write(UC_ARM_REG_R5, work)
            mu.reg_write(UC_ARM_REG_LR, m["end"] | 1)
            mu.emu_start(ent["lut0"] | 1, m["end"], count=2_000_000)
        out.append(forzo)
    return out


if __name__ == "__main__":
    import cube_a6000 as C
    img = C.BIN.read_bytes()
    p = apply_bytes(img)
    c, ent = codigo()
    print("código", len(c), "B", {k: hex(v) for k, v in ent.items()}, "diff", sum(a != b for a, b in zip(img, p)), "B")
