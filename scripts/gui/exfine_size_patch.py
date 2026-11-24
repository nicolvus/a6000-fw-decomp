#!/usr/bin/env python3
"""G106 — tamaños de JPEG «Extra fine» para la A6000 en `libmprctrl.so` (fw 3.21). NO instala nada.

Causa (VERIFICADO en los volcados NVRAM de la cámara): los BKID `BKID_IMAGING_DATSZ_*_EXFINE_{TGT,MAX}` valen 0 (los STD/FINE no). Con TGT = 0,
`MprCtrlStillMgr::GetStillDataInfo` (0x17650) da tamaño 0 y la UI calcula 0 fotos restantes («sin espacio en la tarjeta»); `av-cam` lee los mismos BKID.
Arreglo: gancho en 0x17742 (tras leer el TGT, antes de usarlo). Si la calidad es EXFINE (arg. de pila `[r7+0x48]` = 2) y el TGT leído es 0:
  TGT = TGT_FINE·3/2 y MAX = MAX_FINE·2, y los guarda con `BackupLib::SetEepData` (así los ve también el núcleo; solo se escriben si valían 0).
Ids: en las 43 entradas EXFINE de las tres tablas, TGT_FINE = TGT+2, MAX_FINE = TGT+1, MAX = TGT−1 (comprobado en `tests/test_g106_exfine_size.py`).
INFERENCIA: los factores 3/2 y 2 no salen de Sony (no hay valores EXFINE de la A6000); MAX lleva margen por si el codificador lo usa como tope de búfer.
G109 — segundo gancho (`CalcStillData_JPG`, 0x16dc4): el contador de fotos y el aviso «sin espacio» NO salen de `GetStillDataInfo` sino de la tabla que
`MprCtrlStillMgr::CreateStillData` (0x27840−0x10000) construye UNA vez al arrancar con `CalcStillData_JPG` (suma TGT/MAX leídos de los BKID; con TGT = 0 devuelve 0).
El primer gancho llegaba tarde (y a veces nunca). El segundo actúa tras leer TGT/MAX (0x16e46): si el id es un `…EXFINE_TGT` (tabla de 43 ids de los índices de
`GetStillDataInfo`) y el TGT leído es 0, los deriva del FINE (TGT·3/2, MAX·2), los deja en las variables locales (la tabla ya sale bien) y los guarda en la NVRAM (el núcleo los lee).
Código en la cola a cero del primer PT_LOAD (0x31bd0…0x32000, misma página), que se amplía. Uso: exfine_size_patch.py ENTRADA SALIDA
"""
import struct
import sys
from pathlib import Path

from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks

HOOK, HOOK_ORIG = 0x17742, bytes.fromhex("f9692046")      # ldr r1,[r7,#0x1c]; mov r0,r4
HOOK2, HOOK2_ORIG = 0x16E46, bytes.fromhex("2046f96c")    # mov r0,r4; ldr r1,[r7,#0x4c]  (CalcStillData_JPG tras leer TGT y MAX; r8 = id TGT, sl = id MAX)
TABLAS = ((0x3B47C, 0x2E300, 60), (0x3A8E8, 0x2DF40, 60), (0x3ADC0, 0x25230, 9))   # (nombre→BKID, índice→entrada, nº) de GetStillDataInfo
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


def ids_exfine(d: bytes) -> list[int]:
    """Ids BKID de los `…_EXFINE_TGT` (sin repetir, ordenados) de las tres tablas de `GetStillDataInfo`."""
    phoff, phentsize, phnum = struct.unpack_from("<I", d, 0x1C)[0], *struct.unpack_from("<HH", d, 0x2A)

    def off(va):
        for k in range(phnum):
            t, o, v, _, fs, _ = struct.unpack_from("<6I", d, phoff + k * phentsize)
            if t == 1 and v <= va < v + fs:
                return va - v + o
    u = lambda va: struct.unpack_from("<I", d, off(va))[0]
    nombre = lambda va: d[off(va):d.index(b"\0", off(va))].decode()
    ids = {u(t3 + 16 * e) for t3, t2, cnt in TABLAS for e in (u(t2 + 8 * i + 4) for i in range(cnt)) if nombre(u(t3 + 16 * e + 4)).endswith("EXFINE_TGT")}
    assert len(ids) == 23, len(ids)             # 43 entradas de índice, 23 ids distintos
    return sorted(ids)


def src2(n: int) -> str:
    return f"""
    push {{r4, r5, r6, lr}}
    sub sp, #8
    ldr r3, [r7, #0x1c]
    cmp r3, #0
    bne fin2
    adr r2, tabla
    movs r1, #{n}
bucle:
    ldr r0, [r2], #4
    cmp r0, r8
    beq hit
    subs r1, r1, #1
    bne bucle
    b fin2
hit:
    add.w r0, r8, #2
    movs r1, #4
    mov r2, sp
    movs r3, #0
    str r3, [sp]
    bl #{GET:#x}
    cmp r0, #0
    blt fin2
    ldr r3, [sp]
    add.w r3, r3, r3, lsr #1
    cmp r3, #0
    beq fin2
    str r3, [r7, #0x1c]
    mov r0, r8
    movs r1, #4
    add.w r2, r7, #0x1c
    bl #{SET:#x}
    add.w r0, r8, #1
    movs r1, #4
    mov r2, sp
    movs r3, #0
    str r3, [sp]
    bl #{GET:#x}
    cmp r0, #0
    blt fin2
    ldr r3, [sp]
    lsls r3, r3, #1
    cmp r3, #0
    beq fin2
    str r3, [r7, #0x18]
    sub.w r0, r8, #1
    movs r1, #4
    add.w r2, r7, #0x18
    bl #{SET:#x}
fin2:
    add sp, #8
    pop {{r4, r5, r6, lr}}
    mov r0, r4
    ldr r1, [r7, #0x4c]
    bx lr
    .align 2
tabla:
"""


def cave2(d: bytes, va: int) -> bytes:
    ids = ids_exfine(d)
    code = _asm(src2(len(ids)), va)
    return code + b"\0" * (-len(code) % 4) + b"".join(struct.pack("<I", i) for i in ids)


def _asm(src: str, va: int) -> bytes:
    return bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, va)[0])


def patch(d: bytes) -> bytes:
    out = bytearray(d)
    phoff, phentsize, phnum = struct.unpack_from("<I", d, 0x1C)[0], *struct.unpack_from("<HH", d, 0x2A)
    load1 = next(phoff + k * phentsize for k in range(phnum) if struct.unpack_from("<I", d, phoff + k * phentsize)[0] == 1)
    _, off, va, _, filesz, memsz = struct.unpack_from("<6I", d, load1)
    cave = _asm(SRC, CAVE)
    cave += b"\0" * (-len(cave) % 4)
    cave_2 = CAVE + len(cave)
    c2 = cave2(d, cave_2)
    gancho, gancho2 = _asm(f"bl #{CAVE:#x}", HOOK), _asm(f"bl #{cave_2:#x}", HOOK2)
    if bytes(d[HOOK:HOOK + 4]) == gancho:
        assert bytes(d[HOOK2:HOOK2 + 4]) == gancho2 and bytes(d[CAVE:CAVE + len(cave) + len(c2)]) == cave + c2, "cueva distinta"
        return bytes(d)
    assert (off, va, filesz, memsz) == (0, 0, FIN_LOAD, FIN_LOAD), "primer LOAD distinto del fw 3.21"
    assert bytes(d[HOOK:HOOK + 4]) == HOOK_ORIG and bytes(d[HOOK2:HOOK2 + 4]) == HOOK2_ORIG, "bytes inesperados en los ganchos"
    fin = cave_2 + len(c2)
    assert fin <= FIN_PAGINA and not any(d[CAVE:fin]), "la cueva no está libre"
    out[HOOK:HOOK + 4], out[HOOK2:HOOK2 + 4] = gancho, gancho2
    out[CAVE:fin] = cave + c2
    struct.pack_into("<II", out, load1 + 16, fin, fin)
    return bytes(out)


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()))
    print("ok", sys.argv[2])
