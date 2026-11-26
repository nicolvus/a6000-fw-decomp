#!/usr/bin/env python3
"""G113 — lado `av-cam` del opengate (vídeo 3:2): altura 3:2 del sensor y raster 1440×960 del codificador.

Tres cambios, todos en rodata/código de `av-cam.bin` y reversibles al apagar:

1. **Readout 3:2 (OG-A).** Fila 72 B del modo `0x19` (24p, `693×1625`, 20,83 ms) en la tabla Camcore
   `0x43bc16dc`: alto activo `1124` → `1333`. `1333 < 1625` líneas de cuadro ⇒ el modo conserva su
   periodo (48 Hz de lectura, 24p de película) y no hay que tocar las tablas A/B.
2. **Aceptación del raster (OG-B).** `FUN_436124b8` (elección de perfil del codificador) exige
   coincidencia EXACTA de (ancho, alto); el perfil `0x5a0×0x438` (1440×1080, índice 1) es el único 3:2
   posible porque 1920 exige 1080 (`FUN_4391c540`). Se sustituye su `cmp.w r3,#0x438` por `bl` a una cueva
   que acepta **1080 o 960** (no rompe AVCHD 1440×1080). Solo se parchea el camino progresivo (`0x4361255c`,
   byte `+0x4e` ∈ {1,2} → perfil 1 = 1440×1080): el otro camino (`0x4361254a`, `+0x4e` = 0) lleva al perfil 4 =
   1440×540, el campo entrelazado del 1440×1080i, y pasarlo a 960 rompería el AVCHD entrelazado.
3. **Raster del perfil 1 (OG-C).** Constructor `0x43a7bf56`: alto del perfil `0x438` (1080) → `0x3c0` (960).
   Con 1440×960 de salida y `1996×1333` de lectura la escala es uniforme (0,7214 H / 0,7202 V, 0,2 % de
   diferencia) ⇒ píxel cuadrado: el 3:2 del fichero no necesita marca de aspecto.

Aritmética del readout (54,054 MHz, tablas `0x43bc1ae8`/`0x43bc1b84`): período = a·b/54,054 MHz. El modo
`0x19` tiene 1625 líneas de cuadro y 1124 activas, así que 1333 caben sin cambiar `a·b`. A 59,94 Hz (a·b =
900 900) **1333 no cabe** (1333·675 = 899 775 sí, con línea de 675 ciclos en vez de 693: eso es el modo
60p, OG-D, no incluido aquí).

Dos entradas: `apply_24p(data)` = OG-A/B/C/E (3:2 a 24p) y `apply_bytes(data)` = lo anterior + OG-D (3:2 también a
60p, 59,99 Hz), que es lo que construye `build_cfw_film --funciones og`. Ambas son idempotentes y validan los bytes
originales. Con el opengate completo el 16:9 a 1080p desaparece: queda en 720p y en AVCHD 1440×1080i.

Uso: og_avcam_patch.py ENTRADA SALIDA
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts/gui")]
import avcam_dinamico as D

BASE = D.BASE

# --- OG-A: alto del modo 0x19 (fila 11 de 72 B: 0x43bc16dc + 11·72 + 0x3c) -------------------------
CAMCORE = 0x43BC16DC
MODO_OG = 11                 # modo 0x19 de la lista 0x43fea070 (24p, 693×1625)
ALTO_VIEJO, ALTO_OG = 1124, 1333     # 1333·3 = 3999 ≈ 4000 líneas del sensor con binning 3
ALTO_PTR = CAMCORE + 72 * MODO_OG + 0x3C

# --- OG-B: aceptar 1440×960 además de 1440×1080 --------------------------------------------------
CHECKS = (0x4361255C,)                # cmp.w r3,#0x438; bne error (camino progresivo, perfil 1 = 1440×1080)
CMP_438 = "b3f5876f"
CUEVA = D.ZONA_G18[0] + 0x600         # Film ≤ +0x29c, ISO +0x400/+0x420: 0x600 libre
CUEVA_ASM = "movw r2, #0x3c0; subs r2, r3, r2; cmp r2, #0x78; it eq; moveq r2, #0; cmp r2, #0; bx lr"
ALTURAS = (1080, 960)                 # 0x438 y 0x3c0; 0x438-0x3c0 = 0x78

# --- OG-C: raster del perfil 1 (ctor 0x43a7bf56) --------------------------------------------------
CTOR_ALTO = 0x43A7BFBA               # mov.w r3,#0x438 ; strh r3,[r4,#0x10]
MOV_438 = "4ff48763"


def _asm(src: str, va: int) -> bytes:
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    return bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, va)[0])


# --- OG-D (opcional): opengate a 59,94 Hz ---------------------------------------------------------
# 1333 líneas no caben en el cuadro NTSC de 1300 (693·1300 = 900 900); con línea de 676 ciclos el cuadro
# dura 901 108 ciclos → 59,986 Hz (675 daría 60,07; el exacto, 675,8, no es entero). Afecta a los modos 0x10/0x1a (1080p60): el 60p pasa a ser 3:2 y no queda
# 16:9 a 60p (los modos 0x18/0x05 siguen en 16:9).
MODOS_60P = (3, 10)                 # índices de 0x10 y 0x1a en la lista 0x43fea070
AB_VIEJO, AB_60P = (693, 1300), (676, 1333)   # 676·1333 = 901 108 → 59,986 Hz (675 daría 60,07)


# --- OG-E: el pedido del codificador pasa a 1440×960 (sólo si pedía 1920×1080) ----------------
# `0x43612364` (`bl 0x43a7c8fa`) es el único embudo al selector de perfil: en `r4+0x404` va el
# bloque de formato de 0x84 B, cuyo `+0x56/+0x58` (u16) son ancho/alto que elige perfil.
SITIO_PEDIDO = 0x43612364
BL_ORIG = "6af0c9f2"
CUEVA_PEDIDO = D.ZONA_G18[0] + 0x680
CUEVA_PEDIDO_ASM = """ldrh.w ip, [r4, #0x45a]
cmp.w ip, #0x780
bne skip
ldrh.w ip, [r4, #0x45c]
cmp.w ip, #0x438
bne skip
movw ip, #0x5a0
strh.w ip, [r4, #0x45a]
movw ip, #0x3c0
strh.w ip, [r4, #0x45c]
skip: b.w 0x43a7c8fa"""
PEDIDO_VIEJO, PEDIDO_OG = (1920, 1080), (1440, 960)


def alto_camcore(data: bytes) -> int:
    return struct.unpack_from("<H", data, ALTO_PTR - BASE)[0]


def apply_24p(data: bytes) -> bytes:
    """OG-A + OG-B + OG-C + OG-E: 3:2 en el sensor (modo 0x19) y 1440×960 en el codificador."""
    out = bytearray(data)
    # OG-A
    assert alto_camcore(bytes(data)) in (ALTO_VIEJO, ALTO_OG), f"{ALTO_PTR:#x}: {alto_camcore(data)}"
    struct.pack_into("<H", out, ALTO_PTR - BASE, ALTO_OG)
    # OG-B
    cueva = _asm(CUEVA_ASM, CUEVA)
    for va in CHECKS:
        cur = bytes(out[va - BASE:va - BASE + 4])
        nueva = _asm(f"bl {CUEVA:#x}", va)
        assert cur in (bytes.fromhex(CMP_438), nueva), f"{va:#x}: {cur.hex()}"
        D.comprobar_zonas([(CUEVA, CUEVA + len(cueva))], (D.ZONA_G18,))
        if not any(out[CUEVA - BASE:CUEVA - BASE + len(cueva)]):
            out[CUEVA - BASE:CUEVA - BASE + len(cueva)] = cueva
        out[va - BASE:va - BASE + 4] = nueva
    assert bytes(out[CUEVA - BASE:CUEVA - BASE + len(cueva)]) == cueva, "la cueva de ZONA_G18 no es la esperada"
    # OG-E
    cueva_pedido = _asm(CUEVA_PEDIDO_ASM, CUEVA_PEDIDO)
    cur = bytes(out[SITIO_PEDIDO - BASE:SITIO_PEDIDO - BASE + 4])
    nuevo_pedido = _asm(f"bl {CUEVA_PEDIDO:#x}", SITIO_PEDIDO)
    assert cur in (bytes.fromhex(BL_ORIG), nuevo_pedido), f"{SITIO_PEDIDO:#x}: {cur.hex()}"
    D.comprobar_zonas([(CUEVA_PEDIDO, CUEVA_PEDIDO + len(cueva_pedido))], (D.ZONA_G18,))
    if not any(out[CUEVA_PEDIDO - BASE:CUEVA_PEDIDO - BASE + len(cueva_pedido)]):
        out[CUEVA_PEDIDO - BASE:CUEVA_PEDIDO - BASE + len(cueva_pedido)] = cueva_pedido
    out[SITIO_PEDIDO - BASE:SITIO_PEDIDO - BASE + 4] = nuevo_pedido
    assert bytes(out[CUEVA_PEDIDO - BASE:CUEVA_PEDIDO - BASE + len(cueva_pedido)]) == cueva_pedido
    # OG-C
    cur = bytes(out[CTOR_ALTO - BASE:CTOR_ALTO - BASE + 4])
    mov_3c0 = _asm("mov.w r3, #0x3c0", CTOR_ALTO)
    assert cur in (bytes.fromhex(MOV_438), mov_3c0), f"{CTOR_ALTO:#x}: {cur.hex()}"
    out[CTOR_ALTO - BASE:CTOR_ALTO - BASE + 4] = mov_3c0
    return bytes(out)


def apply_bytes(data: bytes) -> bytes:
    """Opengate completo: `apply_24p` + OG-D (alto 3:2 y línea de 676 ciclos en 0x10/0x1a). Idempotente."""
    out = bytearray(apply_24p(data))
    viejos = {(693, 1300), (800, 1350), (720, 1500)}
    for i in MODOS_60P:
        struct.pack_into("<H", out, CAMCORE + 72 * i + 0x3C - BASE, ALTO_OG)
        for tabla in (0x43BC1AE8, 0x43BC1B84):
            off = tabla - BASE + 12 * i
            a, b, c = struct.unpack_from("<III", out, off)
            assert (a, b) in viejos | {AB_60P}, f"modo {i} tabla {tabla:#x}: {a}×{b}"
            struct.pack_into("<III", out, off, AB_60P[0], AB_60P[1], c)
    return bytes(out)


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(apply_bytes(Path(sys.argv[1]).read_bytes()))
    print("ok", sys.argv[2])
