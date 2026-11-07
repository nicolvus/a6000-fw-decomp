#!/usr/bin/env python3
"""E26-R82 via A - compactacion en sitio del prefijo de 0x18d6e con la tabla c(T) integrada. Solo offline.

El prefijo 0x18d6e..0x18e0f (162 B) se reescribe con codificaciones mas cortas (ldrh/ldrsh en vez de pares ldrb+orr,
sin el `str` muerto de 0x18d7a ni el `bl 0x1b308` = `bx lr`) y se le anade la busqueda en tabla. No hay gancho ni cave:
el codigo nuevo ocupa exactamente los mismos 162 B y empalma con 0x18e10 (sin cambios).

Tabla (propiedad 0x1850000, G+0x48..G+0x7f = 14 entradas de 4 B, SIN terminador): {s16 Tmax', u16 c}, con
T' = T - G42 (el valor de 0x18a2e: lo que ya hay en r0). Gana la primera entrada con T' <= Tmax' (con signo);
entradas de relleno: Tmax' = -32768 (nunca casan). Tabla a ceros = neutra (T' <= 0 casa con c = 0).
Compuerta igual que 0x18a2e: (S+0x31 & 3) != 0 y S+0x60 bit 1 = 0. c fuera de [0, 2000] us se ignora.

Uso: e26_r82_compactacion.py selftest | equiv [N]
"""
from __future__ import annotations

import random
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "e26_r76"))
import e26_r76_parche_darwin_tabla as P

BASE, A, JOIN = 0x4200, 0x18D6E, 0x18E10
LIT = {"S": 0x18F54, "B": 0x18F50, "G": 0x18F5C}            # palabras literales originales (no se mueven)
LITVAL = {"S": 0x200036D8, "B": 0x20000300, "G": 0x20000480}
SADDR, GADDR, BADDR = LITVAL["S"], LITVAL["G"], LITVAL["B"]
TAB_OFF, TAB_N, C_MAX = 0x48, 14, 2000
PAD = (-32768, 0)

SRC = """
    push.w {{r4, r5, r6, r7, r8, lr}}
    ldr r7, [pc, #0x100]
    ldrh r0, [r7, #0x32]
    bl 0x19a12
    bl 0x18a2e
    ldrb.w r5, [r7, #0x31]
    and r5, r5, #3
    cbz r5, skip
    ldrb.w r2, [r7, #0x60]
    lsls r2, r2, #30
    bmi skip
    ldr r1, [pc, #0x104]
    add.w r1, r1, #{toff}
    add.w r3, r1, #{tend}
loop:
    cmp r1, r3
    bhs skip
    ldrsh r2, [r1], #4
    cmp r0, r2
    bgt loop
    ldrh r2, [r1, #-2]
    cmp.w r2, #{cmax}
    bhi skip
    add r0, r2
skip:
    str r0, [r7, #0x48]
    ldr.w r0, [r7, #0x94]
    cbz r0, l1
    adds r1, r0, r0
    bne l0
    movs r0, #0
l0:
    str r0, [r7, #0x48]
l1:
    mov r0, r5
    ldrh r3, [r7, #0x3a]
    ldr r4, [pc, #0x108]
    cbnz r5, efcs
    ldrb.w r2, [r4, #0xcd]
    movs r5, #1
    ldr r1, [pc, #0x104]
    lsls r6, r2, #30
    bne caseb
    ldrh.w r1, [r1, #0x42]
    add.w ip, r1, r3
    b join
caseb:
    cmp.w r6, #0x40000000
    bne casec
    ldrh.w r1, [r4, #0x12a]
    ldrh.w r2, [r4, #0x12c]
    add.w ip, r1, r2
    b join
casec:
    ldrh.w r2, [r1, #0x44]
    ldrh.w r6, [r1, #0x46]
    adds r1, r2, r6
    ldrh.w r2, [r4, #0x12e]
    add.w ip, r1, r2
    b join
{pad}efcs:
    movs r5, #0
    mov ip, r3
join:
"""


def ensamblar_prefijo() -> bytes:
    """Ensambla con keystone, rellena con nop hasta 162 B y fija los desplazamientos pc-relativos de los literales."""
    import capstone
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB)
    fmt = {"toff": TAB_OFF, "tend": 4 * TAB_N, "cmax": C_MAX}
    n = 0
    while True:
        code = bytes(ks.asm(SRC.format(pad="    nop\n" * n, **fmt), A)[0])
        if len(code) >= JOIN - A:
            break
        n += 1
    code = bytes(ks.asm(SRC.format(pad="    nop\n" * (n - 1), **fmt), A)[0]) if len(code) > JOIN - A else code
    assert len(code) == JOIN - A, f"prefijo de {len(code)} B != {JOIN - A}"
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    out = bytearray(code)
    nombres = {0x100: "S", 0x104: "G", 0x108: "B"}
    for i in md.disasm(code, A):
        if i.mnemonic == "ldr" and "[pc, #0x1" in i.op_str and i.size == 2:
            imm = int(i.op_str.split("#")[1].rstrip("]"), 16)
            tgt = LIT[nombres[imm]]
            off = tgt - ((i.address + 4) & ~3)
            assert 0 <= off <= 1020 and off % 4 == 0
            hw = struct.unpack_from("<H", out, i.address - A)[0]
            struct.pack_into("<H", out, i.address - A, (hw & 0xFF00) | (off // 4))
    return bytes(out)


def parchear(img: bytes) -> bytes:
    if len(img) != 157_276:
        raise ValueError("darwin_core.bin de tamano inesperado")
    for k, v in LIT.items():                                   # los literales que reutiliza el codigo nuevo
        assert struct.unpack_from("<I", img, v - BASE)[0] == LITVAL[k], k
    ext = P.referencias_externas(img, A + 2, JOIN)
    if ext:
        raise RuntimeError(f"hay referencias externas al prefijo: {ext[:3]}")
    code = ensamblar_prefijo()
    out = bytearray(img)
    out[A - BASE:JOIN - BASE] = code
    return bytes(out)


def tabla_bytes(tab: list[tuple[int, int]], g42: int = P.G42) -> bytes:
    """tab = [(Tmax us, c us)] ascendente -> 14 entradas {s16 Tmax - G42, u16 c}; relleno {-32768, 0}."""
    if len(tab) > TAB_N:
        raise ValueError(f"{len(tab)} entradas > {TAB_N}")
    ent = [(t - g42, c) for t, c in tab] + [PAD] * (TAB_N - len(tab))
    for tp, c in ent:
        if not -32768 <= tp <= 32767 or not 0 <= c <= C_MAX:
            raise ValueError(f"entrada fuera de rango ({tp}, {c})")
    return b"".join(struct.pack("<hH", tp, c) for tp, c in ent)


def c_modelo(tab_raw: bytes, tprima: int) -> int:
    """Modelo en Python de la busqueda (sin mirar el codigo): primera entrada con T' <= Tmax' (con signo)."""
    for i in range(TAB_N):
        tmax, c = struct.unpack_from("<hH", tab_raw, 4 * i)
        if tprima <= tmax:
            return c if c <= C_MAX else 0
    return 0


# --- emulacion del prefijo (hasta JOIN) -------------------------------------------------------------------
class Emu:
    def __init__(self, img: bytes):
        from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB, Uc
        self.mu = mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        mu.mem_map(0, 0x40000)
        mu.mem_map(0x20000000, 0x10000)
        mu.mem_write(BASE, img)
        self.hit = False
        mu.hook_add(UC_HOOK_CODE, self._h, begin=JOIN, end=JOIN)

    def _h(self, uc, addr, size, _):
        self.hit = True
        uc.emu_stop()

    def run(self, st: dict):
        """Ejecuta 0x18d6e -> 0x18e10 con el estado `st`; devuelve (registros, RAM 0x20000300..0x20003800)."""
        from unicorn.arm_const import (
            UC_ARM_REG_IP,
            UC_ARM_REG_LR,
            UC_ARM_REG_R0,
            UC_ARM_REG_R1,
            UC_ARM_REG_R2,
            UC_ARM_REG_R3,
            UC_ARM_REG_R4,
            UC_ARM_REG_R5,
            UC_ARM_REG_R6,
            UC_ARM_REG_R7,
            UC_ARM_REG_R8,
            UC_ARM_REG_SP,
        )
        mu = self.mu
        mu.mem_write(0x20000000, b"\0" * 0x8000)
        mu.mem_write(SADDR + 0x31, bytes([st["s31"]]))
        mu.mem_write(SADDR + 0x60, bytes([st["s60"]]))
        mu.mem_write(SADDR + 0x32, struct.pack("<H", st["tv"]))
        mu.mem_write(SADDR + 0x3A, struct.pack("<H", st["s3a"]))
        mu.mem_write(SADDR + 0x94, struct.pack("<I", st["s94"]))
        mu.mem_write(GADDR + 0x40, struct.pack("<hHHH", st["g40"], st["g42"], st["g44"], st["g46"]))
        mu.mem_write(GADDR + TAB_OFF, st["tab"])
        mu.mem_write(BADDR + 0xCD, bytes([st["bcd"]]))
        mu.mem_write(BADDR + 0x12A, struct.pack("<HHH", *st["b12"]))
        mu.reg_write(UC_ARM_REG_SP, 0x20008000)
        mu.reg_write(UC_ARM_REG_LR, 0x4001)
        for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_R5,
                  UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_IP):
            mu.reg_write(r, 0xDEAD0000 + r)                   # basura: lo que no se defina no puede influir
        self.hit = False
        mu.emu_start(A | 1, 0x4000, count=2000)
        assert self.hit, "no llego a 0x18e10"
        regs = {n: mu.reg_read(r) for n, r in (("r0", UC_ARM_REG_R0), ("r3", UC_ARM_REG_R3), ("r4", UC_ARM_REG_R4),
                                               ("r5", UC_ARM_REG_R5), ("r7", UC_ARM_REG_R7), ("ip", UC_ARM_REG_IP),
                                               ("sp", UC_ARM_REG_SP))}   # lr no: se vuelve a cargar en el siguiente bl
        return regs, bytes(mu.mem_read(0x20000000, 0x8000)), mu.mem_read(SADDR + 0x48, 4)


def estado_aleatorio(rnd: random.Random, tab: bytes) -> dict:
    u16 = lambda: rnd.choice([0, 1, 0xFFFF, 0x8000, rnd.randrange(65536), rnd.randrange(4000)])
    return {
        "s31": rnd.choice([0, 1, 2, 3, 0x40, 0x42, 0xFC, 0xFF, rnd.randrange(256)]),
        "s60": rnd.choice([0, 1, 2, 3, 0x80, 0xFD, 0xFF, rnd.randrange(256)]),
        "tv": rnd.choice([rnd.randrange(0x1200, 0x1E00), rnd.randrange(0x1000, 0x2000), 0x1C00, 0x1800, 0x1400]),
        "s3a": u16(),
        "s94": rnd.choice([0, 0, 0x80000000, 1, 0xFFFFFFFF, rnd.randrange(1 << 32)]),
        "g40": rnd.choice([-435, 0, 100, -32768, rnd.randrange(-32768, 32768)]),
        "g42": rnd.choice([3407, 3407, 0, 2157, 65535, u16()]),
        "g44": u16(), "g46": u16(),
        "tab": tab,
        "bcd": rnd.choice([0, 1, 2, 3, 4, 5, 0xFD, 0xFF, rnd.randrange(256)]),
        "b12": (u16(), u16(), u16()),
    }


def t_modelo(img: bytes, tv: int) -> int:
    """0x19a12 a mano desde los bytes: T = ((tabla[x & 0xff] + 0x800) * K) >> (11 - (x >> 8)), x = sxth(0x1000 - tv)."""
    def pool(pc: int, imm: int) -> int:
        return struct.unpack_from("<I", img, (((pc + 4) & ~3) + imm) - BASE)[0]
    x = (0x1000 - tv) & 0xFFFF
    x = x - 0x10000 if x & 0x8000 else x
    tab = pool(0x19A1A, 0x1A4)
    k = pool(0x19A22, 0x1A0)
    v = struct.unpack_from("<H", img, tab + 2 * (x & 0xFF) - BASE)[0]
    return ((((v + 0x800) * k) & 0xFFFFFFFF) >> ((11 - (x >> 8)) & 0xFF)) if 0 <= 11 - (x >> 8) < 32 else 0


def modelo_prefijo(img: bytes, st: dict) -> dict:
    """Semantica del prefijo escrita a mano a partir del desensamblado original (sin ejecutar nada)."""
    s31, s60 = st["s31"] & 3, st["s60"]
    t = t_modelo(img, st["tv"])
    s16 = lambda v: v - 0x10000 if v & 0x8000 else v
    if s31:
        tp = t if s60 & 2 else t - st["g42"]
    else:
        tp = t if s60 & 1 else t + s16(st["g40"] & 0xFFFF)
    c = c_modelo(st["tab"], tp) if s31 and not s60 & 2 else 0
    s48 = tp + c
    s94 = st["s94"]
    if s94:
        s48 = 0 if s94 == 0x80000000 else (s94 - (1 << 32) if s94 & 0x80000000 else s94)
    if s31:
        ip = st["s3a"]
    elif st["bcd"] & 3 == 0:
        ip = st["g42"] + st["s3a"]
    elif st["bcd"] & 3 == 1:
        ip = st["b12"][0] + st["b12"][1]
    else:
        ip = st["g44"] + st["g46"] + st["b12"][2]
    return {"r0": s31, "r3": st["s3a"], "r4": BADDR, "r5": 0 if s31 else 1, "ip": ip & 0xFFFFFFFF,
            "s48": ((s48 + 2**31) % 2**32) - 2**31}


def equivalencia(img: bytes, pat: bytes, n: int = 20000, seed: int = 82, con_tabla: bool = True) -> dict:
    """Original frente a reescrita: mismo estado de entrada; en 0x18e10 deben coincidir registros vivos, pila y RAM entera,
    salvo S+0x48, que debe valer el del original + c (c = 0 sin tabla). 3a verificacion: modelo en Python."""
    e0, e1 = Emu(img), Emu(pat)
    rnd = random.Random(seed)
    cero = bytes(4 * TAB_N)
    stats = {"n": 0, "con_c": 0, "gated": 0}
    for k in range(n):
        tab = cero
        if con_tabla and k % 2:
            tab = b"".join(struct.pack("<hH", rnd.choice([rnd.randrange(-4000, 12000), rnd.randrange(-32768, 32768), -32768, 32767]), rnd.choice([0, 100, 1250, 2000, 2001, 30000, rnd.randrange(65536)]))
                           for _ in range(TAB_N))
        st = estado_aleatorio(rnd, tab)
        r0, ram0, s48_0 = e0.run({**st, "tab": cero})        # el original no conoce la tabla (esos bytes no se leen)
        r1, ram1, s48_1 = e1.run(st)
        assert r0 == r1, (k, st, r0, r1)
        gated = (st["s31"] & 3) != 0 and not st["s60"] & 2
        s48 = struct.unpack("<i", bytes(s48_0))[0]
        exp = s48 + c_modelo(tab, s48) if st["s94"] == 0 and gated else s48   # S+0x94 != 0 lo sobrescribe tras el gancho
        assert struct.unpack("<i", bytes(s48_1))[0] == ((exp + 2**31) % 2**32) - 2**31, (k, exp, bytes(s48_1).hex())
        m = modelo_prefijo(img, st)                       # 3a vía: modelo a mano
        assert m["s48"] == struct.unpack("<i", bytes(s48_1))[0], (k, m, bytes(s48_1).hex())
        assert all(r1[x] == m[x] for x in ("r0", "r3", "r4", "r5", "ip")), (k, m, r1)
        # RAM: idem salvo S+0x48 y la tabla (G+0x48..) que el original no tiene
        a, b = bytearray(ram0), bytearray(ram1)
        for ram in (a, b):
            o = SADDR + 0x48 - 0x20000000
            ram[o:o + 4] = b"\0\0\0\0"
            t = GADDR + TAB_OFF - 0x20000000
            ram[t:t + 4 * TAB_N] = bytes(4 * TAB_N)
        assert a == b, k
        stats["n"] += 1
        stats["gated"] += gated
        stats["con_c"] += exp != s48
    return stats


def barrido_exhaustivo(img: bytes, pat: bytes, tab_raw: bytes, paso: int = 1) -> dict:
    """Todos los codigos Tv 0x1000..0x1FFF (paso) x S+0x31 x S+0x60 x S+0x94 x B+0xcd, con los valores NVRAM reales de la
    unidad (G+0x40..0x47 = 4dfe 4f0d 0000 0000, B+0x12a.. = 0) y la tabla dada: original frente a reescrita y modelo."""
    e0, e1 = Emu(img), Emu(pat)
    cero, n, con_c = bytes(4 * TAB_N), 0, 0
    for tv in range(0x1000, 0x2000, paso):
        for s31 in (0, 1, 2, 3):
            for s60 in (0, 1, 2, 3):
                for s94 in (0, 0x80000000, 7):
                    for bcd in (0, 1, 2, 3):
                        st = {"s31": s31, "s60": s60, "tv": tv, "s3a": 0x1234, "s94": s94, "g40": -435, "g42": P.G42,
                              "g44": 0, "g46": 0, "tab": tab_raw, "bcd": bcd, "b12": (0, 0, 0)}
                        r0, _, a48 = e0.run({**st, "tab": cero})
                        r1, _, b48 = e1.run(st)
                        m = modelo_prefijo(img, st)
                        assert r0 == r1 and m["s48"] == struct.unpack("<i", bytes(b48))[0], (st, r0, r1, m)
                        d0 = struct.unpack("<i", bytes(a48))[0]
                        con_c += d0 != m["s48"] and s94 == 0
                        n += 1
    return {"n": n, "con_c": con_c}


def selftest() -> None:
    img = P.DARWIN.read_bytes()
    code = ensamblar_prefijo()
    pat = parchear(img)
    assert len(pat) == len(img) and pat[:A - BASE] == img[:A - BASE] and pat[JOIN - BASE:] == img[JOIN - BASE:]
    print(f"prefijo nuevo {len(code)} B (original {JOIN - A} B), sha {__import__('hashlib').sha256(pat).hexdigest()[:12]}")
    print("equivalencia sin tabla :", equivalencia(img, pat, 4000, con_tabla=False))
    print("equivalencia con tabla :", equivalencia(img, pat, 4000))
    tab = P.tabla_por_velocidad(img)[2]
    print("barrido (paso 17)      :", barrido_exhaustivo(img, pat, tabla_bytes(tab), 17))
    print("selftest OK")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["exhaustivo"]:
        im = P.DARWIN.read_bytes()
        print(barrido_exhaustivo(im, parchear(im), tabla_bytes(P.tabla_por_velocidad(im)[2]), int(a[1]) if a[1:] else 1))
    elif a[:1] == ["equiv"]:
        im = P.DARWIN.read_bytes()
        print(equivalencia(im, parchear(im), int(a[1]) if a[1:] else 50000))
    else:
        selftest()
