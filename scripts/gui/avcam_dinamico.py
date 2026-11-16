"""G73: cuevas de `av-cam.bin` que usan memoria dinámica (el `malloc` propio del núcleo) y datos compactos, en los dos fragmentos libres VERIFICADOS por G72.

Sustituye a la zona a cero de 2,3 MB (memoria viva, G72). `malloc` = `0x43561164` (trampolín `os->[0x14]->[0x1ac]`; `free` = `0x43561180`, `operator delete` lo usa).
Las cuevas reservan UNA vez (reserva perezosa en el primer uso; no hay punto de arranque único y conocido) y guardan el puntero en una celda de 4 B; si `malloc` devuelve 0
no escriben nada y el núcleo sigue como de fábrica (HLG: selectores y punteros originales; LUT: el puntero original del búfer).
HLG: 3 curvas de 4122 B generadas en el montón desde 58 nodos con interpolación lineal por tramos de ancho 2^s (sin división) + la rodilla de nivel aplicada a los nodos.
LUT: 3 tablas de 405 nodos × 21 bits (3 × 7 bits, sin pérdida) = 1064 B cada una, desempaquetadas con la permutación `perm` del propio núcleo.
shortcut: la reserva nunca se libera (una sola vez por arranque); el tamaño del montón del SO no se conoce (HLG-3)."""
from __future__ import annotations

import itertools
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui")]
import cfw_ajustes as cfw
import pp_hlg_curves as H

BASE = 0x43541000
MALLOC = 0x43561164
ZONA_A = (0x43BE3B28, 0x43BE4330)        # 2056 B, ceros idénticos fichero/vivo (G72)
ZONA_B = (0x43C1FF24, 0x43C20C8C)        # 3432 B (el hueco G72 empieza en ...21)
PROHIBIDAS = ((0x43D620D9, 0x43FA8F00), (0x43FAF28C, 0x43FB9000))   # zona viva de G72 y hueco G18 (Color Chrome, pp_tone, Silent, curvas)
CURVE, STRIDE_BUF = 0x101A, 0x101A
TAB_PTR, SEL, SLOG3_COLA = 0x44001404, 0x43CB56E6, None
HOOK_HLG = (0x43853ECE, bytes.fromhex("93f8ca37"))   # ldrb.w r3,[r3,#0x7ca] en la selección de gamma 0x43853ec0 (primer uso de la gamma de PP)
V0 = 12237                                            # 16·(64 + 876·0,8): rodilla de HLG en unidades de 1/16 de código
MUL = {1: round((H.NIVEL[1] - .8) / .2 * 256), 2: round((H.NIVEL[2] - .8) / .2 * 256), 3: 256}
PERM, TAM = 0x43BEF2AC, 0x654
LUT_CODE, LUT_TABLAS, LUT_BYTES = ZONA_A[0] + 0x400, ZONA_B[0], 1064
HLG_CELDA, LUT_CELDA = ZONA_A[0], LUT_CODE


# ---------- HLG compacto ----------
def _knee(v: int, m: int) -> int:
    return v if v <= V0 else V0 + (((v - V0) * m) >> 8)


def _y0(i: int) -> float:
    return H.oetf(H.BLANCO * i * H.K)


def esquema(tol: float = 0.95) -> tuple[list[int], list[int]]:
    """(shifts, nodos u16 en 1/16 de código): tramos de 2^s entradas, el más ancho que mantenga |salida entera − referencia real| < `tol` en las tres curvas."""
    v = [round(16 * (64 + 876 * _y0(i))) for i in range(2049)]
    def nivel(y: float, n: int) -> float:
        return y if y <= H.RODILLA else H.RODILLA + (y - H.RODILLA) * (H.NIVEL[n] - H.RODILLA) / (1 - H.RODILLA)

    exacta = {n: [64 + 876 * nivel(_y0(i), n) for i in range(2048)] for n in (1, 2, 3)}
    ik = next(i for i in range(2048) if v[i] > V0)
    ic = next(i for i in range(2048) if H.BLANCO * i * H.K >= 1.0)
    sh, i = [], 0
    for b in (ik, ic, 2048):
        while i < b:
            s = min(7, (b - i).bit_length() - 1)
            while s and max(abs(interp(v, i, s, j, n) - exacta[n][i + j]) for n in (1, 2, 3) for j in range(1 << s)) >= tol:
                s -= 1
            sh.append(s)
            i += 1 << s
    nodos, i = [0], 0
    for s in sh:
        i += 1 << s
        nodos.append(i)
    return sh, [v[k] for k in nodos]


def interp(v: list[int], i: int, s: int, j: int, n: int) -> int:
    a, b = _knee(v[i], MUL[n]), _knee(v[i + (1 << s)], MUL[n])
    return (a + (((b - a) * j) >> s) + 8) >> 4


def generar_hlg(sh: list[int], nodos: list[int], n: int) -> list[int]:
    """Réplica en Python de lo que hace la cueva."""
    out = []
    for k, s in enumerate(sh):
        a, b = _knee(nodos[k], MUL[n]), _knee(nodos[k + 1], MUL[n])
        out += [(a + (((b - a) * j) >> s) + 8) >> 4 for j in range(1 << s)]
    assert len(out) == 2048
    return out


def colas(a6300: bytes, tab_a6300: int, slog3: int) -> list[bytes]:
    """Las tres colas de 26 B (`+0x1012` = 4, `+0x1014` = gamma 0x1c…0x1e), de la curva S-Log3 de la A6300 como en G67."""
    p = struct.unpack_from("<I", a6300, tab_a6300 + 8 * slog3 + 4 - BASE)[0]
    c = bytearray(a6300[p - BASE + 0x1000:p - BASE + CURVE])
    c[0x12] = 4
    return [bytes(c[:0x14]) + bytes([0x1B + n]) + bytes(c[0x15:]) for n in (1, 2, 3)]


def hlg_asm(celda: int, nodos_va: int, sh_va: int, sh_fin: int, mt: int, colas_va: int) -> str:
    c = lambda r, v: f"movw {r}, #{v & 0xFFFF:#x}\n movt {r}, #{v >> 16:#x}\n"
    return f"""
    push.w {{r0-r12, lr}}
    {c('r4', celda)}
    ldr r0, [r4]
    cmp r0, #0
    bne.w fin
    movw r0, #{3 * STRIDE_BUF:#x}
    {c('r1', MALLOC | 1)}
    blx r1
    cmp r0, #0
    beq.w fin
    str r0, [r4]
    mov r9, r0
    movs r10, #0
curva:
    {c('r1', mt)}
    ldrh.w r11, [r1, r10, lsl #1]
    mov r0, r9
    {c('r2', nodos_va)}
    {c('r3', sh_va)}
    {c('r12', sh_fin)}
tramo:
    ldrh r4, [r2]
    ldrh r5, [r2, #2]
    movw r6, #{V0:#x}
    cmp r4, r6
    bls.w k1
    subs r7, r4, r6
    mul r7, r7, r11
    lsrs r7, r7, #8
    adds r4, r6, r7
k1:
    cmp r5, r6
    bls.w k2
    subs r7, r5, r6
    mul r7, r7, r11
    lsrs r7, r7, #8
    adds r5, r6, r7
k2:
    subs r5, r5, r4
    ldrb r6, [r3], #1
    movs r7, #1
    lsls r7, r7, r6
    movs r8, #0
punto:
    mul r1, r5, r8
    lsrs r1, r1, r6
    adds r1, r1, r4
    adds r1, #8
    lsrs r1, r1, #4
    strh r1, [r0], #2
    adds r8, #1
    cmp r8, r7
    blo.w punto
    adds r2, #2
    cmp r3, r12
    blo.w tramo
    {c('r1', colas_va)}
    movs r2, #26
    mla r1, r10, r2, r1
    movs r2, #0
cola:
    ldrb r3, [r1, r2]
    strb r3, [r0, r2]
    adds r2, #1
    cmp r2, #26
    blo.w cola
    {c('r1', TAB_PTR + 8 * 0x1C + 4)}
    add.w r1, r1, r10, lsl #3
    str r9, [r1]
    {c('r1', SEL + 2 * 12)}
    add.w r1, r1, r10, lsl #1
    adds r2, r10, #0x1c
    orr.w r2, r2, r2, lsl #8
    strh r2, [r1]
    movw r1, #{STRIDE_BUF:#x}
    add r9, r9, r1
    adds r10, #1
    cmp r10, #3
    blo.w curva
fin:
    pop.w {{r0-r12, lr}}
    ldrb.w r3, [r3, #0x7ca]
    bx lr
"""


# ---------- LUT empaquetada ----------
def empaqueta_21(tabla: bytes, perm: list[int]) -> bytes:
    """0x654 B del hardware → 405 × 21 bits (c0<<14 | c1<<7 | c2) en el orden lógico j·81+a·9+b."""
    bits = 0
    for i in range(405):
        w = struct.unpack_from("<I", tabla, 4 * perm[i])[0]
        bits |= (((w >> 16 & 0x7F) << 14) | ((w >> 8 & 0x7F) << 7) | (w & 0x7F)) << (21 * i)
    return bits.to_bytes(LUT_BYTES, "little")


def lut_unpack_asm(celda: int, tablas: int) -> str:
    c = lambda r, v: f"movw {r}, #{v & 0xFFFF:#x}\n movt {r}, #{v >> 16:#x}\n"
    return f"""
    push {{r4-r8, lr}}
    mov r4, r0
    {c('r5', celda)}
    ldr r6, [r5]
    cmp r6, #0
    bne.w tengo
    movw r0, #{TAM:#x}
    {c('r1', MALLOC | 1)}
    blx r1
    cmp r0, #0
    beq.w fallo
    str r0, [r5]
    mov r6, r0
tengo:
    subs r4, r4, #1
    movw r1, #{LUT_BYTES}
    mul r4, r4, r1
    {c('r1', tablas)}
    adds r4, r4, r1
    {c('r7', PERM)}
    movs r5, #0
    movs r3, #0
bucle:
    lsrs r0, r5, #3
    adds r0, r4, r0
    ldrb r1, [r0]
    ldrb r2, [r0, #1]
    orr.w r1, r1, r2, lsl #8
    ldrb r2, [r0, #2]
    orr.w r1, r1, r2, lsl #16
    ldrb r2, [r0, #3]
    orr.w r1, r1, r2, lsl #24
    and r2, r5, #7
    lsrs r1, r1, r2
    and r2, r1, #0x7f
    ubfx r0, r1, #7, #7
    orr.w r2, r2, r0, lsl #8
    ubfx r0, r1, #14, #7
    orr.w r2, r2, r0, lsl #16
    ldrh.w r0, [r7, r3, lsl #1]
    str.w r2, [r6, r0, lsl #2]
    adds r5, #21
    adds r3, #1
    movw r1, #405
    cmp r3, r1
    blo.w bucle
    mov r0, r6
    pop {{r4-r8, pc}}
fallo:
    movs r0, #0
    pop {{r4-r8, pc}}
"""


# ---------- construcción ----------
def _ens(src: str, va: int) -> bytes:
    return cfw.ensamblar(src, va)


def hlg_parches(a6300: bytes, tab_a6300: int, slog3: int) -> list[tuple[int, bytes, str]]:
    """Cueva HLG (datos + código) en ZONA_A y el gancho de 4 B. Formato (dirección, bytes, «dato …»/«gancho …») como `pp_curves_patch`."""
    from e25_24.thumb import bl
    sh, nodos = esquema()
    a = HLG_CELDA
    mt, nv, sv = a + 8, a + 0x10, a + 0x10 + 2 * len(nodos)
    cv = (sv + len(sh) + 3) & ~3
    code = (cv + 78 + 3) & ~3
    datos = bytearray(code - a)
    datos[8:8 + 6] = struct.pack("<3H", *(MUL[n] for n in (1, 2, 3)))
    datos[nv - a:nv - a + 2 * len(nodos)] = struct.pack(f"<{len(nodos)}H", *nodos)
    datos[sv - a:sv - a + len(sh)] = bytes(sh)
    datos[cv - a:cv - a + 78] = b"".join(colas(a6300, tab_a6300, slog3))
    cueva = _ens(hlg_asm(HLG_CELDA, nv, sv, sv + len(sh), mt, cv), code)
    assert code + len(cueva) <= LUT_CODE, hex(code + len(cueva))
    return [(a, bytes(datos) + cueva, "dato cueva HLG (zona A)"), (HOOK_HLG[0], bl(HOOK_HLG[0], code), "gancho HLG init")]


def lut_codigo(ajuste, hooks) -> tuple[list[tuple[int, bytes]], list[int]]:
    """(escrituras (va, bytes) de la cueva de la LUT, entradas f0/f1). `hooks` = (va, original, registro destino, registros a guardar) de `lut_patch`."""
    a, out = LUT_CODE + 4, []
    unp = _ens(lut_unpack_asm(LUT_CELDA, LUT_TABLAS), a)
    out.append((a, unp))
    a = (a + len(unp) + 3) & ~3
    entradas = []
    for k, (_, _, dst, guardar) in enumerate(hooks):
        src = f"""
    push {{{guardar}, lr}}
    {cfw.leer_asm(ajuste, f"t{k}")}
    cmp r0, #0
    beq.w o{k}
    bl #{LUT_CODE + 4:#x}
    cmp r0, #0
    beq.w o{k}
    mov {dst}, r0
    pop {{{guardar}, lr}}
    bx lr
o{k}:
    ldr.w {dst}, [r5, #0xc4]
    pop {{{guardar}, lr}}
    bx lr
    .align 2
"""
        c = _ens(src, a)
        out.append((a, c))
        entradas.append(a)
        a = (a + len(c) + 3) & ~3
    assert a <= ZONA_A[1], hex(a)
    return out, entradas


def comprobar_zonas(escrituras: list[tuple[int, int]]) -> None:
    """Ninguna escritura (inicio, fin) sale de las zonas verificadas ni toca las prohibidas ni se solapa con otra."""
    for lo, hi in escrituras:
        assert any(z[0] <= lo and hi <= z[1] for z in (ZONA_A, ZONA_B)), (hex(lo), hex(hi))
        assert not any(lo < p[1] and p[0] < hi for p in PROHIBIDAS), (hex(lo), hex(hi))
    s = sorted(escrituras)
    assert all(a[1] <= b[0] for a, b in itertools.pairwise(s)), "solape"


def malloc_simulado(cnt: int) -> bytes:
    """Trozo Thumb para el `malloc` de las pruebas: cuenta llamadas en [cnt] y devuelve [cnt+4] (0 = fallo)."""
    return _ens(f"movw r1, #{cnt & 0xFFFF:#x}\n movt r1, #{cnt >> 16:#x}\n ldr r2, [r1]\n adds r2, #1\n str r2, [r1]\n ldr r0, [r1, #4]\n bx lr\n", MALLOC)
