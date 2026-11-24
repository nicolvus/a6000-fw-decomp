#!/usr/bin/env python3
"""G106 — tamaños de JPEG «Extra fine» para la A6000 en `libmprctrl.so` (fw 3.21). NO instala nada.

Causa (VERIFICADO en los volcados NVRAM de la cámara): los BKID `BKID_IMAGING_DATSZ_*_EXFINE_{TGT,MAX}` valen 0 (los STD/FINE no). Con TGT = 0,
`MprCtrlStillMgr::GetStillDataInfo` (0x17650) da tamaño 0 y la UI calcula 0 fotos restantes («sin espacio en la tarjeta»); `av-cam` lee los mismos BKID.
Arreglo: gancho en 0x17742 (tras leer el TGT, antes de usarlo). Si la calidad es EXFINE (arg. de pila `[r7+0x48]` = 2) y el TGT leído es 0:
  TGT = TGT_FINE·3/2 y MAX = MAX_FINE·2, y los guarda con `BackupLib::SetEepData` (así los ve también el núcleo; solo se escriben si valían 0).
Ids: en las 43 entradas EXFINE de las tres tablas, TGT_FINE = TGT+2, MAX_FINE = TGT+1, MAX = TGT−1 (comprobado en `tests/test_g106_exfine_size.py`).
INFERENCIA: los factores 3/2 y 2 no salen de Sony (no hay valores EXFINE de la A6000); MAX lleva margen por si el codificador lo usa como tope de búfer.
Código en la cola a cero del primer PT_LOAD (0x31bd0…0x32000, misma página), que se amplía. Uso: exfine_size_patch.py ENTRADA SALIDA
"""
import struct
import sys
from pathlib import Path

from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks

HOOK, HOOK_ORIG = 0x17742, bytes.fromhex("f9692046")      # ldr r1,[r7,#0x1c]; mov r0,r4
GET, SET = 0x1A988, 0x1A99E                                # BackupLib::GetEepData / SetEepData (id, tamaño, búfer)
CAVE, FIN_LOAD, FIN_PAGINA = 0x31BD0, 0x31BD0, 0x32000

SRC = f"""
    push {{r0, r1, r2, r3, r4, lr}}
    sub sp, #8
    ldr r3, [r7, #0x1c]
    cmp r3, #0
    bne fin
    ldr r3, [r7, #0x48]
    cmp r3, #2
    bne fin
    cmp r6, #0
    beq fin
    add.w r0, r6, #2
    movs r1, #4
    add.w r2, r7, #0x1c
    bl #{GET:#x}
    cmp r0, #0
    blt cero
    ldr r3, [r7, #0x1c]
    add.w r3, r3, r3, lsr #1
    str r3, [r7, #0x1c]
    cmp r3, #0
    beq fin
    mov r0, r6
    movs r1, #4
    add.w r2, r7, #0x1c
    bl #{SET:#x}
    movs r3, #0
    str r3, [sp]
    add.w r0, r6, #1
    movs r1, #4
    mov r2, sp
    bl #{GET:#x}
    cmp r0, #0
    blt fin
    ldr r3, [sp]
    lsls r3, r3, #1
    str r3, [sp]
    cmp r3, #0
    beq fin
    sub.w r0, r6, #1
    movs r1, #4
    mov r2, sp
    bl #{SET:#x}
    b fin
cero:
    movs r3, #0
    str r3, [r7, #0x1c]
fin:
    add sp, #8
    pop {{r0, r1, r2, r3, r4, lr}}
    ldr r1, [r7, #0x1c]
    mov r0, r4
    bx lr
"""


def _asm(src: str, va: int) -> bytes:
    return bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, va)[0])


def patch(d: bytes) -> bytes:
    out = bytearray(d)
    phoff, phentsize, phnum = struct.unpack_from("<I", d, 0x1C)[0], *struct.unpack_from("<HH", d, 0x2A)
    load1 = next(phoff + k * phentsize for k in range(phnum) if struct.unpack_from("<I", d, phoff + k * phentsize)[0] == 1)
    _, off, va, _, filesz, memsz = struct.unpack_from("<6I", d, load1)
    cave = _asm(SRC, CAVE)
    gancho = _asm(f"bl #{CAVE:#x}", HOOK)
    if bytes(d[HOOK:HOOK + 4]) == gancho:
        assert bytes(d[CAVE:CAVE + len(cave)]) == cave, "cueva distinta"
        return bytes(d)
    assert (off, va, filesz, memsz) == (0, 0, FIN_LOAD, FIN_LOAD), "primer LOAD distinto del fw 3.21"
    assert bytes(d[HOOK:HOOK + 4]) == HOOK_ORIG, f"{HOOK:#x}: bytes inesperados"
    assert CAVE + len(cave) <= FIN_PAGINA and not any(d[CAVE:CAVE + len(cave)]), "la cueva no está libre"
    out[HOOK:HOOK + 4] = gancho
    out[CAVE:CAVE + len(cave)] = cave
    struct.pack_into("<II", out, load1 + 16, CAVE + len(cave), CAVE + len(cave))
    return bytes(out)


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()))
    print("ok", sys.argv[2])
