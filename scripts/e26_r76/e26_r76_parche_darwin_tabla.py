#!/usr/bin/env python3
"""E26-R76 v3 (R82) - Tabla de compensacion EFCS por velocidad para Darwin (solo offline).

v3 (R82): el parche vive EN SITIO. El prefijo 0x18d6e..0x18e0f (162 B) de la funcion de tiempos se reescribe mas corto
y con la busqueda en tabla integrada (e26_r82/e26_r82_compactacion.py): sin gancho, sin cave, mismo tamano de imagen.
`parchear()` lo aplica. `parchear_anexo()` (via C, anexar tras 0x2a85c) queda como alternativa y como oraculo de la
emulacion: exige que el cargador admita un darwin_core mas largo (solo se decide en camara).
El cave de R76 en 0x13d5a (R81: funcion viva) sigue BLOQUEADO (`parchear_hueco_r76`).

Tabla en RAM de Darwin G+0x48..G+0x7f (0x200004c8, propiedad NVRAM 0x1850000): 14 entradas {s16 Tmax', u16 c} SIN
terminador, T' = T - G42 (el valor que devuelve 0x18a2e), gana la primera con T' <= Tmax' (con signo); relleno
{-32768, 0}. Solo con EFCS ((S+0x31 & 3) != 0, como 0x18a2e) y S+0x60 bit 1 = 0. c fuera de [0, 2000] us se ignora.
Tabla a ceros = neutra. La tabla viene de la NVRAM: se recalibra sin reflashear.

Uso:  python e26_r76_parche_darwin_tabla.py selftest      (no toca la camara; requiere keystone-engine, capstone, unicorn)
      python e26_r76_parche_darwin_tabla.py tabla         (imprime la tabla del modelo R74)
"""

from __future__ import annotations

import bisect
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
BASE, HOOK = 0x4200, 0x18D7C
HOOK_OLD = bytes.fromhex("fff7 57fe".replace(" ", ""))   # se verifica contra el binario en selftest
F18A2E, SADDR, GADDR = 0x18A2E, 0x200036D8, 0x20000480
TAB_OFF = 0x48                      # G+0x48..G+0x7f: 14 entradas de 4 B; G+0x44..47 lo lee Darwin (rama B+0xcd & 3 != 0)
TAB_ADDR, TAB_MAX = GADDR + TAB_OFF, 14
PAD = (-32768, 0)                   # entrada de relleno: nunca casa
C_MAX = 2000                        # c fuera de [0, C_MAX] us se ignora (NVRAM corrupta); el bucle no pasa de TAB_MAX entradas
ANEXO = 0x2A860                     # via C: cave anexado tras el fin de imagen 0x2a85c (alineado a 4)
CAVE_DEFAULT, CAVE_END, FUNC_REAL = 0x13D5A, 0x13DC0, 0x13D58   # R76: hueco BLOQUEADO (R81: la funcion viva empieza en 0x13d58)

# --- modelo de perdida (R74 s4, delta normalizada) en funcion de x = B - A (ms -> us) ----------------
_X = [-2070, -1400, -540, 570, 1570, 4570, 7670]
_D = [1240, 1320, 1300, 1290, 1040, 0, 0]   # R82/R80 s3: cola a 0 (R62 s2: ~0 por franjas a 8 ms; R74 s4: se anula hacia B-A = 4..5 ms)
G42, B86, B8A = 3407, 6, -21        # valores de la unidad (R66 s2)
MARG = 8                            # margen alrededor de la ventana: T sale exacto de 0x19a12 (R80 s3 proponia 10 us; era 40)
WIN_LO, WIN_HI = 3257 - MARG, 3457 + MARG         # S+0x48 in [-150, 50]: rama intermedia 0x20544 (no modelada)


def perdida(x: float, X=_X, D=_D) -> float:
    if x <= X[0]:
        return D[0]
    if x >= X[-1]:
        return D[-1]
    i = bisect.bisect_right(X, x) - 1
    return D[i] + (D[i + 1] - D[i]) * (x - X[i]) / (X[i + 1] - X[i])


def usar_unidad(g42: int = 3407, b86: int = 6, b8a: int = -21) -> None:
    """R80 s3: G+0x42, B+0x86 y B+0x8a son datos de ESTA unidad (se leen del volcado NVRAM), no constantes."""
    global G42, B86, B8A, WIN_LO, WIN_HI
    G42, B86, B8A = g42, b86, b8a
    WIN_LO, WIN_HI = g42 - 150 - MARG, g42 + 50 + MARG


def separacion(t_darwin: int) -> float | None:
    """B - A (us) que impone 0x18d6e para T' = T + c; None en la rama intermedia. La rama corta satura en A = 1 us."""
    s48 = t_darwin - G42
    if s48 < -150:
        return min(s48 + B86, -1)
    if s48 > 50:
        return s48 + B8A
    return None


def exposicion_real(t_darwin: int, perd=perdida) -> float:
    x = separacion(t_darwin)
    return t_darwin - (perd(0) if x is None else perd(x))


def resolver_c(t: int, perd=perdida) -> int:
    """Punto fijo c = perdida(x(T + c)); si T + c cae en la ventana intermedia, se empuja al borde mas cercano."""
    c = 0.0
    for _ in range(60):
        x = separacion(round(t + c))
        c_new = perd(x if x is not None else 0)
        if abs(c_new - c) < 0.5:
            break
        c = c_new
    c = round(c)
    if WIN_LO <= t + c <= WIN_HI:
        c = WIN_LO - 1 - t if (t + c) - WIN_LO < WIN_HI - (t + c) else WIN_HI + 1 - t
    return c


def velocidades_tercio(n_max=40) -> list[int]:
    """Tv = 0x1000 + k*256/3 (k = 0..): los T en us los da 0x19a12 emulado."""
    return [0x1000 + round(256 * k / 3) for k in range(8, n_max)]


def construir_tabla(ts: list[int], perd=perdida, max_n=TAB_MAX, tol=8) -> list[tuple[int, int]]:
    """[(Tmax, c)] ascendente. Fusiona velocidades vecinas con un c comun si, para todas, el error modelado
    |E - T| <= tol us y T + c queda fuera de la ventana intermedia. Corte entre velocidades = punto medio."""
    ts = sorted(set(ts))
    cs = [resolver_c(t, perd) for t in ts]

    def valido(i, j, c):
        return all(not WIN_LO <= t + c <= WIN_HI and abs(exposicion_real(t + c, perd) - t) <= max(tol, 0.03 * t) for t in ts[i:j + 1])

    bins, i = [], 0
    while i < len(ts):
        j = i
        while j + 1 < len(ts) and valido(i, j + 1, round(sum(cs[i:j + 2]) / (j - i + 2))):
            j += 1
        c = round(sum(cs[i:j + 1]) / (j - i + 1))
        tmax = ts[j] if j + 1 == len(ts) else (ts[j] + ts[j + 1]) // 2
        bins.append((tmax, c))
        i = j + 1
    bins = _guardas(bins)
    if len(bins) > max_n:
        raise ValueError(f"{len(bins)} tramos > {max_n}")
    return bins


def _guardas(bins: list[tuple[int, int]], t_max=12000) -> list[tuple[int, int]]:
    """Ningun T continuo con T + c(T) dentro de [WIN_LO, WIN_HI]: en cada tramo problematico parte en dos con un
    salto de c que salta la ventana (error <= ~5 % solo en ese tramo, que no contiene velocidades de la escala 1/3 EV)."""
    def c_de(t):
        return next((c for tm, c in bins if t <= tm), 0)
    cs = [c_de(t) for t in range(t_max + 1)]
    t = 1
    while t <= t_max:
        if WIN_LO <= t + cs[t] <= WIN_HI:
            a = t
            while t <= t_max and WIN_LO <= t + cs[t] <= WIN_HI:
                t += 1
            b = t - 1
            m = (a + b) // 2
            for u in range(a, m + 1):
                cs[u] = WIN_LO - 1 - m
            for u in range(m + 1, b + 1):
                cs[u] = WIN_HI + 1 - (m + 1)
        else:
            t += 1
    out = []
    for t in range(1, t_max + 1):
        if t == t_max or cs[t + 1] != cs[t]:
            out.append((t, cs[t]))
    while out and out[-1][1] == 0:      # c = 0 por encima de la tabla: lo da el terminador
        out.pop()
    return out


def tabla_bytes(tab: list[tuple[int, int]], g42: int = G42) -> bytes:
    """[(Tmax us, c us)] ascendente -> 14 entradas {s16 Tmax - G42, u16 c}; relleno {-32768, 0}. Valida rangos."""
    if len(tab) > TAB_MAX:
        raise ValueError(f"{len(tab)} entradas > {TAB_MAX}")
    ent = [(t - g42, c) for t, c in tab] + [PAD] * (TAB_MAX - len(tab))
    for tp, c in ent:
        if not -32768 <= tp <= 32767 or not 0 <= c <= C_MAX:
            raise ValueError(f"entrada fuera de rango ({tp}, {c})")
    return b"".join(struct.pack("<hH", tp, c) for tp, c in ent)


# --- via C: cave anexado (alternativa; exige que el cargador admita un core mas largo) -------------------
def ensamblar_cave(cave: int) -> bytes:
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    src = f"""
        push {{lr}}
        bl {F18A2E:#x}
        ldr r1, S_
        ldrb.w r2, [r1, #0x31]
        lsls r2, r2, #30
        beq done
        ldrb.w r2, [r1, #0x60]
        lsls r2, r2, #30
        bmi done
        ldr r1, T_
        add.w r3, r1, #{4 * TAB_MAX}
    loop:
        cmp r1, r3
        bhs done
        ldrsh r2, [r1], #4
        cmp r0, r2
        bgt loop
        ldrh r2, [r1, #-2]
        cmp.w r2, #{C_MAX}
        bhi done
        add r0, r2
    done:
        pop {{pc}}
        .align 2
    S_: .word {SADDR:#x}
    T_: .word {TAB_ADDR:#x}
    """
    code, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, cave)
    return bytes(code)


def bl_thumb(addr: int, target: int) -> bytes:
    sys.path.insert(0, str(ROOT / "scripts"))
    from e25_24.thumb import bl
    return bl(addr, target)


def parchear_anexo(img: bytes) -> bytes:
    """Via C: imagen + 4 B de relleno + cave en ANEXO y el gancho `bl cave` en 0x18d7c. Tamano mayor (157 276 + 4 + cave)."""
    if len(img) != 157_276:
        raise ValueError("darwin_core.bin de tamano inesperado")
    assert img[HOOK - BASE:HOOK - BASE + 4] == bl_thumb(HOOK, F18A2E), "gancho: bytes originales distintos"
    out = bytearray(img) + bytearray(ANEXO - BASE - len(img)) + ensamblar_cave(ANEXO)
    out[HOOK - BASE:HOOK - BASE + 4] = bl_thumb(HOOK, ANEXO)
    return bytes(out)


def parchear(img: bytes) -> bytes:
    """Via A (diseno elegido en R82): reescribe en sitio 0x18d6e..0x18e0f con la tabla integrada; mismo tamano."""
    sys.path.insert(0, str(ROOT / "scripts" / "e26_r82"))
    import e26_r82_compactacion as C
    return C.parchear(img)


def parchear_hueco_r76(img: bytes, cave: int = CAVE_DEFAULT) -> bytes:
    """Cave de R76 en la funcion 0x13d58: BLOQUEADO (R81). Solo existe para que la prueba lo demuestre."""
    ext = referencias_externas(img, FUNC_REAL if cave == CAVE_DEFAULT else cave, CAVE_END if cave == CAVE_DEFAULT else cave + 0x60)
    if ext:
        raise RuntimeError(f"cave {cave:#x} BLOQUEADO: el rango tiene referencias externas {ext[:3]} (R81)")
    raise RuntimeError("sin hueco libre verificado en la imagen")


# --- emulacion de 0x18d6e ------------------------------------------------------------------------------
def emular_18d6e(img: bytes, tv: int, tab: list[tuple[int, int]] | bytes | None, efcs=True, s31=None, s60=0, g42=G42, b86=B86):
    """(rama, retardo_A, retardo_B, S+0x48 inicial de la espera) con llamadas externas sustituidas."""
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_R8,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    mu.mem_map(0x0, 0x40000)
    mu.mem_map(0x20000000, 0x10000)
    mu.mem_write(BASE, img)
    s31 = (0x02 if efcs else 0x40) if s31 is None else s31
    mu.mem_write(SADDR + 0x31, bytes([s31]))
    mu.mem_write(SADDR + 0x60, bytes([s60]))
    mu.mem_write(SADDR + 0x32, struct.pack("<H", tv))
    mu.mem_write(GADDR + 0x40, struct.pack("<hH", -435, g42))
    mu.mem_write(0x20000300 + 0x84, struct.pack("<hhhh", 6, b86, -22, -21))
    mu.mem_write(0x20000300 + 0xC6, bytes([29, 37, 35]))
    if tab is not None:
        mu.mem_write(TAB_ADDR, bytes(tab) if isinstance(tab, (bytes, bytearray)) else tabla_bytes(tab))
    r = {"rama": None, "A": None, "B": None}
    stubs = {0x1B308: 0, 0x1A738: 0, 0x19932: 0, 0x203AE: 1, 0x19948: 0, 0x198BC: 0, 0x93E6: 0, 0x19978: 0}

    def hook(uc, addr, size, _):
        if addr == 0x198EE:                                   # rama corta: r0 = retardo de A
            r["rama"], r["A"] = "corta", uc.reg_read(UC_ARM_REG_R0) & 0xFFFFFFFF
            r["B"] = 0
            uc.emu_stop()
        elif addr == 0x18ED2:                                 # rama larga: r8 = retardo de B
            r["rama"], r["A"], r["B"] = "larga", 0, uc.reg_read(UC_ARM_REG_R8)
            uc.emu_stop()
        elif addr == 0x19978 and r["rama"] is None:           # rama intermedia (0x20544 no modelado)
            r["rama"] = "intermedia"
            uc.emu_stop()
        elif addr in stubs:
            uc.reg_write(UC_ARM_REG_R0, stubs[addr])
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) | 1)

    mu.hook_add(UC_HOOK_CODE, hook, begin=0, end=0x40000)
    mu.reg_write(UC_ARM_REG_LR, 0x4001)
    mu.reg_write(UC_ARM_REG_SP, 0x20008000)
    try:
        mu.emu_start(0x18D6E | 1, 0x4000, count=4000)
    except Exception as e:
        if r["rama"] is None:
            raise RuntimeError(f"emulacion fallo en tv={tv:#x}: {e}") from e
    return r["rama"], r["A"], r["B"]


def t_us(img: bytes, tv: int) -> int:
    from unicorn import UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, Uc
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    mu.mem_map(0x0, 0x40000)
    mu.mem_map(0x20000000, 0x10000)
    mu.mem_write(BASE, img)
    mu.reg_write(UC_ARM_REG_LR, 0x4001)
    mu.reg_write(UC_ARM_REG_SP, 0x20008000)
    mu.reg_write(UC_ARM_REG_R0, tv)
    mu.emu_start(0x19A12 | 1, 0x4000, count=200)
    return mu.reg_read(UC_ARM_REG_R0)


def sep_emulada(rama, a, b):
    return None if rama == "intermedia" else (b - a)


def tabla_por_velocidad(img_orig: bytes) -> tuple[list[int], list[int], list[tuple[int, int]]]:
    tvs = velocidades_tercio()
    ts = [t_us(img_orig, tv) for tv in tvs]
    ts = [t for t in ts if 230 <= t <= 12000]
    tvs = [tv for tv in tvs if 230 <= t_us(img_orig, tv) <= 12000]
    return tvs, ts, construir_tabla(ts)


def referencias_externas(img: bytes, a: int, b: int) -> list:
    """Referencias desde FUERA de [a, b) hacia dentro: ramas, palabras-puntero (con/sin bit 0), adr y ldr pc-relativo."""
    import re

    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    refs, end = [], BASE + len(img)
    pos = BASE
    while pos < end:
        got = False
        for i in md.disasm(img[pos - BASE:pos - BASE + 0x1000], pos):
            got, pos = True, i.address + i.size
            if a <= i.address < b:
                continue
            m = i.mnemonic
            mm = re.search(r"#(-?0x[0-9a-f]+)", i.op_str)
            if (m.startswith(("b", "cb")) and not m.startswith(("bic", "bfi", "bfc", "bkpt"))) and mm and a <= int(mm.group(1), 16) < b:
                refs.append((i.address, "rama", int(mm.group(1), 16)))
            if mm and (m.startswith("adr") or (m.startswith("ldr") and "[pc" in i.op_str)):
                t = ((i.address + 4) & ~3) + int(mm.group(1), 16)
                if a <= t < b:
                    refs.append((i.address, "pc-rel", t))
            if m.startswith(("tbb", "tbh")):
                refs.append((i.address, "tbb/tbh (revisar a mano)", 0))
        if not got:
            pos += 2
    for o in range(0, len(img) - 3, 2):
        v = struct.unpack_from("<I", img, o)[0]
        if a <= (v & ~1) < b and not a <= BASE + o < b:
            refs.append((BASE + o, "palabra", v))
    return [r for r in refs if not r[1].startswith("tbb")]


def lectores_de_G(img: bytes) -> set[int]:
    """Offsets G+x que leen las 5 funciones que cargan el literal 0x20000480 (revision de ventana de 80 instr.)."""
    import re

    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    sitios = [0x182DA, 0x18398, 0x18A30, 0x18DAA, 0x18FBC]
    pool = [BASE + o for o in range(0, len(img) - 3, 4) if struct.unpack_from("<I", img, o)[0] == GADDR]
    found = []
    for o in range(0, len(img) - 3, 2):
        pass
    for pos in range(BASE, BASE + len(img) - 2, 2):
        for i in md.disasm(img[pos - BASE:pos - BASE + 4], pos):
            if i.mnemonic.startswith("ldr") and "[pc" in i.op_str and pos in sitios:
                t = ((pos + 4) & ~3) + int(re.search(r"#(-?0x[0-9a-f]+)", i.op_str).group(1), 16)
                assert t in pool, (hex(pos), hex(t))
                found.append(pos)
            break
    assert sorted(found) == sitios, [hex(x) for x in found]
    # cargas del literal G desde cualquier otro sitio -> no deben existir
    otros = []
    for pos in range(BASE, BASE + len(img) - 2, 2):
        for i in md.disasm(img[pos - BASE:pos - BASE + 4], pos):
            if i.mnemonic.startswith("ldr") and "[pc" in i.op_str and pos not in sitios:
                m = re.search(r"#(-?0x[0-9a-f]+)", i.op_str)
                if m and ((pos + 4) & ~3) + int(m.group(1), 16) in pool:
                    otros.append(pos)
            break
    assert not otros, [hex(x) for x in otros]
    # inmediatos que se suman al registro cargado con G en cada sitio (ventana lineal de 60 instr.); cubre ambas ramas
    offs = set()
    for pos in sitios:
        win = list(md.disasm(img[pos - BASE:pos - BASE + 400], pos))[:60]
        regs = {win[0].op_str.split(",")[0].strip()}
        for i in win[1:]:
            if i.mnemonic.startswith("push"):
                break
            ops = [x.strip() for x in i.op_str.split(",")]
            if i.mnemonic.startswith("add") and ops[-1].startswith("#") and (ops[1] if len(ops) == 3 else ops[0]) in regs:
                regs.add(ops[0])
                offs.add(int(ops[-1][1:], 16))
    return offs


def selftest() -> None:
    img = DARWIN.read_bytes()
    assert len(img) == 157276
    # 0) nada externo salta al interior del prefijo reescrito (0x18d6e es la entrada; 0x18e10 sigue igual)
    ext = referencias_externas(img, 0x18D70, 0x18E10)
    assert not ext, ext
    # 0b) lectores de G: solo G+0x40..0x47; la tabla (G+0x48..0x7f) no se lee en el original
    offs = lectores_de_G(img)
    print("sumandos al puntero G en las 5 funciones:", sorted(hex(x) for x in offs), "(lecturas de 1..4 B: G+0x40..0x47)")
    assert offs and max(offs) + 4 <= TAB_OFF, offs
    tvs, ts, tab = tabla_por_velocidad(img)
    print("tabla (Tmax us, c us):", tab, f"({len(tab)} de {TAB_MAX} entradas)")
    pat = parchear(img)
    assert len(pat) == len(img)
    # 1) solo cambia el prefijo 0x18d6e..0x18e0f
    dif = [i for i in range(len(img)) if img[i] != pat[i]]
    assert dif and all(0x18D6E - BASE <= i < 0x18E10 - BASE for i in dif), "cambios fuera del prefijo"
    print(f"bytes distintos: {len(dif)} (todos en 0x18d6e..0x18e0f); tamano {len(pat)}")
    anexo = parchear_anexo(img)                                  # oraculo independiente (via C)
    # 2) sin tabla (ceros) el parche es neutro: mismas esperas que el original
    for tv in tvs:
        assert emular_18d6e(img, tv, None) == emular_18d6e(pat, tv, []), f"no neutro con tabla vacia tv={tv:#x}"
    # 3) EFCS desactivado, compuerta S+0x60 bit1 y compuerta S+0x31&3 identica a 0x18a2e
    for tv in tvs[::3]:
        assert emular_18d6e(img, tv, None, efcs=False) == emular_18d6e(pat, tv, tab, efcs=False)
        assert emular_18d6e(img, tv, None, s60=2) == emular_18d6e(pat, tv, tab, s60=2)
        assert emular_18d6e(pat, tv, tab, s31=1) == emular_18d6e(pat, tv, tab, s31=2) == emular_18d6e(pat, tv, tab, s31=3)
    # 3b) robustez ante NVRAM corrupta: c fuera de rango, o ninguna entrada casa: el resultado es el original
    basura = [(32767 + G42, 30000)] * TAB_MAX                    # casa la primera, c > C_MAX: se ignora
    sin_casa = [(-30000 + G42, 500)] * TAB_MAX                   # ninguna casa y no hay terminador: el bucle para en TAB_MAX
    for tv in tvs[::4]:
        assert emular_18d6e(img, tv, None) == emular_18d6e(pat, tv, bytes(4 * TAB_MAX)), f"tabla a ceros tv={tv:#x}"
        for malo in (basura, sin_casa):
            raw = b"".join(struct.pack("<hH", t - G42, c) for t, c in malo)
            assert emular_18d6e(img, tv, None) == emular_18d6e(pat, tv, raw), f"NVRAM corrupta aplicada tv={tv:#x}"
    # 4) con tabla: exposicion modelada ~ T en la escala 1/3 EV; antes, perdida ~1,25 ms en las rapidas
    print(f"{'T us':>6} {'B-A orig':>9} {'E orig':>7} | {'B-A nuevo':>9} {'c':>5} {'E nueva':>7}")
    peor = 0.0
    for tv, t in zip(tvs, ts):
        r0 = emular_18d6e(img, tv, None)
        r1 = emular_18d6e(pat, tv, tab)
        x0, x1 = sep_emulada(*r0), sep_emulada(*r1)
        e0 = exposicion_real(t)
        tp = (x1 + 3401 if r1[0] == "corta" else x1 + 3428) if x1 is not None else None
        e1 = exposicion_real(tp) if tp is not None else float("nan")
        print(f"{t:6d} {x0 if x0 is not None else float('nan'):9.0f} {e0:7.0f} | "
              f"{x1 if x1 is not None else float('nan'):9.0f} {(tp - t) if tp else 0:5d} {e1:7.0f}  {r1[0]}")
        assert r1[0] != "intermedia", f"T={t} cae en la rama intermedia"
        peor = max(peor, abs(e1 - t) / t)
        assert tp is not None and tp - t == next((c_ for tm, c_ in tab if t <= tm), 0)
    print(f"error relativo maximo modelado (escala 1/3 EV) |E - T| / T = {peor:.1%}")
    assert peor < 0.035
    # 5) barrido de TODOS los codigos Tv (1/256 EV) entre ~200 us y 45 ms (1/4000..1/22): nunca la rama intermedia
    n, ramas, peor_c, w, fuera = 0, {}, 0.0, None, 0.0
    for tv in range(0x1500, 0x1D00):
        t = t_us(img, tv)
        if not 200 <= t <= 45000:
            continue
        r = emular_18d6e(pat, tv, tab)
        assert r == emular_18d6e(anexo, tv, tab), f"A != C (anexo) en Tv={tv:#x}"
        n += 1
        ramas[r[0]] = ramas.get(r[0], 0) + 1
        assert r[0] != "intermedia", f"Tv={tv:#x} T={t} us -> rama intermedia"
        x = sep_emulada(*r)
        tp = x + (3401 if r[0] == "corta" else 3428)
        if t <= 12000:
            e = abs(exposicion_real(tp) - t) / t
            if e > peor_c:
                peor_c, w = e, (tv, t)
            if not 1953 < t <= 2245:
                fuera = max(fuera, e)
    print(f"barrido continuo: {n} codigos Tv, ramas {ramas}; error modelado maximo {peor_c:.1%} en Tv={w[0]:#x} (T={w[1]} us; tramo guarda 1953<T<=2245); fuera de la guarda {fuera:.1%}")
    assert peor_c < 0.10 and fuera < 0.05, (peor_c, fuera)
    print("selftest OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["tabla"]:
        print(tabla_por_velocidad(DARWIN.read_bytes())[2])
    else:
        selftest()
