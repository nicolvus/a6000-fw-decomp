#!/usr/bin/env python3
"""G76 VFR-F4 — S&Q a 120/100 fps: la tabla O/U Crank de av-cam 3.21 (`0x43b93bf4`, 57 filas) no admite captura 120 ni 100.

Parche mínimo, sin tocar la búsqueda de fábrica: el único `bl 0x435d709c` (en `0x43a5d2a0`) pasa a una cueva en la cola libre de la
zona B de g72/g73. La cueva lee (fR, sR) con el mismo lector (`0x43a5d844`) y, si el S&Q está activo y coincide una de las filas nuevas,
devuelve su valor; si no, salta a `0x435d709c`, que hace lo de siempre (incluidos sus registros y el reinicio del error).
Filas nuevas por analogía con las de fábrica (NTSC fR 2/4/6, PAL fR 3/5; NO_VERIFICADO que av-cam traduzca el código 7 a sR 120/100).
Solo escribe una copia de av-cam.bin. Uso: sq120_patch.py ENTRADA SALIDA
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui")]
import avcam_dinamico as D
from e25_24.thumb import bl

B = D.BASE
HOOK = (0x43A5D2A0, bytes.fromhex("79f7fcf6"))  # bl 0x435d709c (único llamador)
BUSCA, LEE = 0x435D709C, 0x43A5D844
CUEVA = 0x43C20BA0                                # cola de ZONA_B tras las 3 tablas LUT de g73 (3·1064+3 B)
FILAS = ((2, 120), (4, 120), (6, 120), (3, 100), (5, 100))


def cueva() -> bytes:
    tabla = CUEVA + 0x60
    asm = f"""
        push {{r0, r4, r5, lr}}
        sub sp, #0x18
        mov r4, r0
        add.w r0, r4, #0xc
        add r1, sp, #8
        add r2, sp, #0xc
        add r3, sp, #0xd
        add r5, sp, #0x10
        str r5, [sp]
        add r5, sp, #0x14
        str r5, [sp, #4]
        bl {LEE:#x}
        ldrb.w r0, [sp, #0xc]
        cbz r0, fabrica
        ldr r1, [sp, #0x10]
        ldrb.w r2, [sp, #0xd]
        movw r3, #{tabla & 0xffff:#x}
        movt r3, #{tabla >> 16:#x}
        movs r5, #{len(FILAS)}
    bucle:
        ldr r0, [r3]
        cmp r0, r1
        bne sigue
        ldrb r0, [r3, #4]
        cmp r0, r2
        bne sigue
        ldrb r0, [r3, #5]
        add sp, #0x18
        pop {{r1, r4, r5, pc}}
    sigue:
        adds r3, #8
        subs r5, #1
        bne bucle
    fabrica:
        add sp, #0x18
        pop {{r0, r4, r5, lr}}
        b.w {BUSCA:#x}
    """
    code = D._ens(asm, CUEVA)
    assert len(code) <= 0x60, hex(len(code))
    filas = b"".join(struct.pack("<IBBH", fr, sr, 1, 0) for fr, sr in FILAS)
    return code.ljust(0x60, b"\0") + filas


def patch(d: bytes) -> bytes:
    a, old = HOOK
    if d[a - B:a - B + 4] == bl(a, CUEVA):
        return d
    assert d[a - B:a - B + 4] == old, "gancho distinto del av-cam 3.21"
    c = cueva()
    assert set(d[CUEVA - B:CUEVA - B + len(c)]) == {0}, "la cola de la zona B no está libre"
    D.comprobar_zonas([(CUEVA, CUEVA + len(c))])
    assert CUEVA >= D.ZONA_B[0] + 3 * D.LUT_BYTES + 3  # detrás de las tablas LUT
    out = bytearray(d)
    out[CUEVA - B:CUEVA - B + len(c)] = c
    out[a - B:a - B + 4] = bl(a, CUEVA)
    return bytes(out)


if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.write_bytes(patch(src.read_bytes()))
    print("ok", dst)
