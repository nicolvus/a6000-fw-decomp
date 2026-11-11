#!/usr/bin/env python3
"""G30 — dos arreglos de `libObj.so` (A6000 fw3.21) para el menú Picture Profile (CFW 3.67). NO instala nada.

Prueba en cámara con el 3.66 (10-11-2026): (a) el menú no repinta el valor recién elegido hasta salir y volver a entrar; (b) el selector Off/PP1–PP9 siempre marca Off.
Causas (estáticas, sin probar en cámara):
  (a) La lectura `getModelInfo` 0x49 (`0x4a77bc`) devuelve un estado en caché (`0x4a5adc(obj, 1)`) que solo actualiza la notificación del núcleo `0x8577`
      (`0x4b4498` → `0x4a5836(obj, 1, valor_app)`); en la A6000 esa notificación no llega (mismo defecto que Silent, ver `g22/patch_libobj_eco.py`).
      Arreglo: en `pvt_ActionSetPictureProfile` (`0x4c0a78`), segundo bucle, cuando el parámetro i de la lista se convierte bien (rama del log «ok» en `0x4c0be2`),
      se llama a `0x4a5836(obj_i, 1, valor_app)` con el mismo cálculo de objeto que `0x4b4638`. Sustituye al log (14 B) por un salto a código nuevo.
  (b) El selector se leía con 0x49 y clave 0x276, pero ese recorrido solo trae 31 claves (`0x1f8 + 4·i`, +1/+2 → hasta 0x272). El caso `0x4a` de `getModelInfo`
      (`0x4a7820`) devuelve el perfil actual con la clave `0x275`; lo lee de la NVRAM `[this+0xf8c]`, que esta acción no actualiza. La acción sí guarda el perfil enviado
      en `[this+0x274]` (`0x4c0d6c`, tras un envío correcto); aquí el caso `0x4a` usa `[this+0x274]` si es ≤ 9 y, si no, la NVRAM original.
El código nuevo va en un segmento PT_LOAD R-X añadido en el hueco de VA entre los dos LOAD (0xFCB000, alcanzable con b.w/bl desde 0x4c0be2).
Uso: patch_libobj_ppeco.py ENTRADA.so SALIDA.so
"""
import struct
import sys
from pathlib import Path

from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks

CAVE_VA = 0xFCB000                         # entre el fin del 1.er LOAD (0xFCA5A4) y el inicio de la página del 2.º (0xFD2000)
ALIGN = 0x1000
# (dirección, bytes originales, descripción)
SITE_PERFIL = (0x4A784C, bytes.fromhex("d5f88c0f"), "ldr.w r0,[r5,#0xf8c]")          # inicio del bloque que lee la NVRAM en el caso 0x4a
SITE_ECO = (0x4C0BE2, bytes.fromhex("874907f59e70"), "ldr r1,[pc,#0x21c]; add.w r0,r7,#0x13c")  # inicio del log «ok» del 2.º bucle
SETTER_ESTADO, VUELVE_PERFIL_OK, VUELVE_PERFIL_NVRAM, VUELVE_ECO = 0x4A5836, 0x4A785E, 0x4A7850, 0x4C0BFC


def _asm(src: str, addr: int) -> bytes:
    enc, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, addr)
    return bytes(enc)


def cave_code(base: int) -> tuple[bytes, dict[int, int]]:
    """Código nuevo (concatenado) y {sitio: dirección del tramo}."""
    p = base
    perfil = f"""
        ldr.w r3, [r5, #0x274]
        cmp r3, #9
        bhi.n nvram
        str r3, [r7, #0x54]
        b.w {VUELVE_PERFIL_OK:#x}
    nvram:
        ldr.w r0, [r5, #0xf8c]
        b.w {VUELVE_PERFIL_NVRAM:#x}
    """
    b1 = _asm(perfil, p)
    e = base + ((len(b1) + 3) & ~3)
    eco = f"""
        ldr r3, [r7, #4]
        ldr.w r3, [r3, #0x560]
        addw r3, r3, #0x4b6
        add.w r3, r4, r3, lsl #2
        ldr r0, [r3, #4]
        movs r1, #1
        ldr.w r2, [r7, #0x148]
        bl {SETTER_ESTADO:#x}
        add.w sb, sb, #1
        b.w {VUELVE_ECO:#x}
    """
    b2 = _asm(eco, e)
    return b1.ljust(e - base, b"\0") + b2, {SITE_PERFIL[0]: p, SITE_ECO[0]: e}


def patch(d: bytes) -> bytes:
    for va, orig, what in (SITE_PERFIL, SITE_ECO):
        assert d[va:va + len(orig)] == orig, f"{va:#x} ({what}): {d[va:va + len(orig)].hex()}"
    phoff, phnum = struct.unpack_from("<I", d, 28)[0], struct.unpack_from("<H", d, 44)[0]
    segs = [list(struct.unpack_from("<8I", d, phoff + 32 * i)) for i in range(phnum)]
    loads = [s for s in segs if s[0] == 1]
    assert loads[0][2] == 0 and loads[0][1] == 0 and loads[0][2] + loads[0][5] <= CAVE_VA and CAVE_VA + ALIGN <= (loads[1][2] & ~(ALIGN - 1)), "hueco de VA no libre"
    code, hooks = cave_code(CAVE_VA)
    new_off = (len(d) + ALIGN - 1) // ALIGN * ALIGN                  # offset ≡ VA (mod página)
    new_seg = [1, new_off, CAVE_VA, CAVE_VA, 0, 0, 5, ALIGN]         # PT_LOAD R-X
    i1 = segs.index(loads[0]) + 1
    order = segs[:i1] + [new_seg] + segs[i1:]                         # los LOAD deben ir en orden ascendente de VA
    assert [s[2] for s in order if s[0] == 1] == sorted(s[2] for s in order if s[0] == 1)
    seg = bytearray(code)
    seg += b"\0" * (-len(seg) % 16)
    phdr_off = new_off + len(seg)
    new_seg[4] = new_seg[5] = len(seg) + 32 * len(order)
    seg += b"".join(struct.pack("<8I", *s) for s in order)
    out = bytearray(d)
    for va, src in hooks.items():
        patch_bytes = _asm(f"b.w {src:#x}", va)
        orig = SITE_PERFIL[1] if va == SITE_PERFIL[0] else SITE_ECO[1]
        out[va:va + len(orig)] = patch_bytes.ljust(len(orig), b"\0")
        if len(orig) > len(patch_bytes):
            out[va + len(patch_bytes):va + len(orig)] = b"\x00\xbf" * ((len(orig) - len(patch_bytes)) // 2)
    out = out.ljust(new_off, b"\0") + seg
    struct.pack_into("<I", out, 28, phdr_off)
    struct.pack_into("<H", out, 44, len(order))
    return bytes(out)


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()))
