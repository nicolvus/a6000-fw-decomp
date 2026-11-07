#!/usr/bin/env python3
"""E26-R76 v2 - Parche de Darwin con tabla de compensacion EFCS por velocidad (solo offline).

Cambios respecto a v1 (verificacion-r76.md):
  * tabla en G+0x48..0x7f (no G+0x44): Darwin ya LEE G+0x44..0x47 (rama B+0xcd&3 >= 2 de 0x182d8/0x18daa/0x18fbc).
  * cave dentro de la imagen, en la funcion muerta 0x13d5a (sin llamadores ni punteros): el tamano no cambia.
  * compuerta igual que 0x18a2e/0x18d96: (S+0x31 & 3) != 0 (v1 solo miraba el bit 1).
  * tramos guarda: ningun T de 230..12000 us (continuo) cae en la ventana intermedia 0x20544.

Gancho: en 0x18d7c, `bl 0x18a2e` (T -> T - G42 con EFCS) pasa a `bl CAVE`. El cave llama a 0x18a2e y,
solo con EFCS activado (S+0x31 bit 1) y sin la compuerta S+0x60 bit 1, suma c(T) (s16, us) leido de una
tabla en RAM de Darwin: G+0x44.. (0x200004c4), pares {u16 Tmax, s16 c}, terminada en Tmax = 0.
La tabla viene de la NVRAM (propiedad 0x1850000, 128 B, hoy ceros salvo +0x40 y +0x42), asi que
se puede recalibrar sin reflashear.

Uso:  python e26_r76_parche_darwin_tabla.py selftest      (no toca la camara; requiere keystone, capstone, unicorn)
      python e26_r76_parche_darwin_tabla.py tabla         (imprime la tabla del modelo R74)
"""
from __future__ import annotations

import bisect
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "kslib"))  # keystone instalado solo en el scratchpad
ROOT = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter")
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
BASE, HOOK = 0x4200, 0x18D7C
HOOK_OLD = bytes.fromhex("fff7 57fe".replace(" ", ""))   # se verifica contra el binario en selftest
F18A2E, SADDR, GADDR = 0x18A2E, 0x200036D8, 0x20000480
TAB_OFF = 0x48                      # G+0x48..G+0x7f: 14 palabras de 4 B (13 entradas + terminador); G+0x44..47 lo lee Darwin
TAB_ADDR, TAB_MAX = GADDR + TAB_OFF, 13
CAVE_DEFAULT = 0x13D5A              # funcion muerta 0x13d5a..0x13dc0 (102 B; el cave ocupa 54 B)
CAVE_END = 0x13DC0
CAVE_ORIG_SHA256 = "8df02fff317feacba1c26210f1ca161fe2c70d4cc41d47b56777ce41674d1ca2"  # sha256 de 0x13d5a..0x13dc0 original

# --- modelo de perdida (R74 s4, delta normalizada) en funcion de x = B - A (ms -> us) ----------------
_X = [-2070, -1400, -540, 570, 1570, 4570, 7670]
_D = [1240, 1320, 1300, 1290, 1040, 170, 160]
G42, B86, B8A = 3407, 6, -21        # valores de la unidad (R66 s2)
MARG = 40                           # margen de seguridad alrededor de la ventana (Tv no exacto)
WIN_LO, WIN_HI = 3257 - MARG, 3457 + MARG         # S+0x48 in [-150, 50]: rama intermedia 0x20544 (no modelada)


def perdida(x: float, X=_X, D=_D) -> float:
    if x <= X[0]:
        return D[0]
    if x >= X[-1]:
        return D[-1]
    i = bisect.bisect_right(X, x) - 1
    return D[i] + (D[i + 1] - D[i]) * (x - X[i]) / (X[i + 1] - X[i])


def separacion(t_darwin: int) -> float | None:
    """B - A (us) que impone 0x18d6e para T' = T + c; None en la rama intermedia."""
    s48 = t_darwin - G42
    if s48 < -150:
        return s48 + B86
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


def tabla_bytes(tab: list[tuple[int, int]]) -> bytes:
    out = b"".join(struct.pack("<Hh", t, c) for t, c in tab)
    return out.ljust(4 * (TAB_MAX + 1), b"\0")


# --- cave ----------------------------------------------------------------------------------------------
def ensamblar_cave(cave: int) -> bytes:
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    src = f"""
        push {{r4, lr}}
        mov r4, r0
        bl {F18A2E:#x}
        ldr r1, S_
        ldrb r2, [r1, #0x31]
        lsls r2, r2, #30
        beq done
        ldrb r2, [r1, #0x60]
        lsls r2, r2, #30
        bmi done
        ldr r1, T_
    loop:
        ldrh r2, [r1], #4
        cbz r2, done
        cmp r4, r2
        bhi loop
        ldrsh r2, [r1, #-2]
        add r0, r0, r2
    done:
        pop {{r4, pc}}
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


def parchear(img: bytes, cave: int = CAVE_DEFAULT) -> bytes:
    """Devuelve la imagen (mismo tamano) con el gancho y el cave escrito dentro de la funcion muerta 0x13d5a."""
    assert len(img) == 157_276
    assert img[HOOK - BASE:HOOK - BASE + 4] == bl_thumb(HOOK, F18A2E), "gancho: bytes originales distintos"
    code = ensamblar_cave(cave)
    assert CAVE_DEFAULT <= cave and cave + len(code) <= CAVE_END, "el cave no cabe en la funcion muerta"
    out = bytearray(img)
    out[HOOK - BASE:HOOK - BASE + 4] = bl_thumb(HOOK, cave)
    out[cave - BASE:cave - BASE + len(code)] = code
    return bytes(out)


# --- emulacion de 0x18d6e ------------------------------------------------------------------------------
def emular_18d6e(img: bytes, tv: int, tab: list[tuple[int, int]] | None, efcs=True, s31=None, s60=0):
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
    mu.mem_write(GADDR + 0x40, struct.pack("<hH", -435, G42))
    mu.mem_write(0x20000300 + 0x84, struct.pack("<hhhh", 6, 6, -22, -21))
    mu.mem_write(0x20000300 + 0xC6, bytes([29, 37, 35]))
    if tab is not None:
        mu.mem_write(TAB_ADDR, tabla_bytes(tab))
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
    import hashlib
    img = DARWIN.read_bytes()
    assert len(img) == 157276
    # 0) la region del cave es la funcion muerta original y nada fuera de ella la referencia
    assert hashlib.sha256(img[CAVE_DEFAULT - BASE:CAVE_END - BASE]).hexdigest() == CAVE_ORIG_SHA256
    ext = referencias_externas(img, CAVE_DEFAULT, CAVE_END)
    assert not ext, f"referencias externas al hueco: {ext}"
    # 0b) lectores de G: solo G+0x40..0x47; la tabla (G+0x48..0x7f) no se lee en Darwin
    offs = lectores_de_G(img)
    print("sumandos al puntero G en las 5 funciones:", sorted(hex(x) for x in offs), "(lecturas de 1..4 B: G+0x40..0x47)")
    assert offs and max(offs) + 4 <= TAB_OFF, offs
    tvs, ts, tab = tabla_por_velocidad(img)
    print("tabla (Tmax us, c us):", tab, f"({len(tab)} de {TAB_MAX} entradas)")
    pat = parchear(img)
    assert len(pat) == len(img)
    cave = ensamblar_cave(CAVE_DEFAULT)
    # 1) solo cambian el gancho (4 B) y el cave
    dif = [i for i in range(len(img)) if img[i] != pat[i]]
    ok = lambda i: HOOK - BASE <= i < HOOK - BASE + 4 or CAVE_DEFAULT - BASE <= i < CAVE_DEFAULT - BASE + len(cave)
    assert dif and all(ok(i) for i in dif), "cambios fuera del gancho/cave"
    print(f"bytes distintos: {len(dif)} (gancho 4 B + cave {len(cave)} B en {CAVE_DEFAULT:#x}..{CAVE_END:#x}); tamano {len(pat)}")
    # 2) sin tabla (ceros) el parche es neutro: mismas esperas que el original
    for tv in tvs:
        assert emular_18d6e(img, tv, None) == emular_18d6e(pat, tv, []), f"no neutro con tabla vacia tv={tv:#x}"
    # 3) EFCS desactivado, compuerta S+0x60 bit1 y compuerta S+0x31&3 identica a 0x18a2e
    for tv in tvs[::3]:
        assert emular_18d6e(img, tv, None, efcs=False) == emular_18d6e(pat, tv, tab, efcs=False)
        assert emular_18d6e(img, tv, None, s60=2) == emular_18d6e(pat, tv, tab, s60=2)
        assert emular_18d6e(pat, tv, tab, s31=1) == emular_18d6e(pat, tv, tab, s31=2) == emular_18d6e(pat, tv, tab, s31=3)
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
        assert tp - t == next((c_ for tm, c_ in tab if t <= tm), 0)
    print(f"error relativo maximo modelado (escala 1/3 EV) |E - T| / T = {peor:.1%}")
    assert peor < 0.035
    # 5) barrido de TODOS los codigos Tv (1/256 EV) entre ~200 us y 45 ms (1/4000..1/22): nunca la rama intermedia
    n, ramas, peor_c, w, fuera = 0, {}, 0.0, None, 0.0
    for tv in range(0x1500, 0x1D00):
        t = t_us(img, tv)
        if not 200 <= t <= 45000:
            continue
        r = emular_18d6e(pat, tv, tab)
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
