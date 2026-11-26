#!/usr/bin/env python3
"""FILM-PB-1 · parche C de libmpr.so 3.21: crear el sector FBM 0x31 (idx 10 de 0xA3699C,
userID 0x04/0x21, mediaID 3, OM 6) **por la vía de consola**, es decir la que PERSISTE:

    EntryWriteBaseDataFunction(0x2B1DEC) para (userID, mediaID 3)  ← lo que hace `FBM LTC 1` / `EWBDFD`
    BackupMgr::InitBackupData(6,3)      (0x2B43F0)                 ← lo que hace `FBM InitB 6 3`
    → WriteBaseData(6,3) 0x2B4030 → 0x2B3000 (guarda `fn != 0`) → CreateSector32 0x2B7080
      → TermSectorData 0x2B4164 (escribe la página de datos base 0x380000) → Sync 0x11EE08

Por qué hace falta el primer paso (desensamblado propio): `0x2B3000` recorre las 37 filas de
0x9D23FC y **salta las que tienen `fn == 0`** (`0x2B301A cbz r2`); las 37 lo están de fábrica, así
que `InitBackupData(6,3)` sola devuelve `0x10800010` (`0x2B4072`) y no crea nada.  El único escritor
de `fn`/`arg` de la fila es `0x2B1DEC`, cuya firma real (medida, no supuesta) es:

    int EntryWriteBaseDataFunction(u32 userID /*r0*/, void *fn /*r1*/, void *arg /*r2*/, u32 mediaID /*r3*/)
      push {r4,r5,r6,r7,r8,lr}; r4=r0 userID, r6=r1 fn, r5=r2 arg, r8=r3 mediaID
      recorre 0x9D23FC (37 × 0x18) y si [fila+0]==userID y [fila+4]==mediaID:
          [fila+0x10] = fn ; [fila+0x14] = arg
      devuelve 0 (lo que vale en el terminador) ⇒ 0 == "hecho" (LTC lo usa así)

`fn` es SÓLO una puerta: ni `0x2B2F48` ni `0x2B2B18` lo llaman nunca (se comprueba en el informe).
Por eso se registra el **dummy de fábrica 0x2B5185 con arg 0**, que es exactamente lo que pasa
`FBM EWBDFD 4 3 0` (handler 0x2B5198: r1 = literal 0x2B5185, r2 = dirección del 3.er argumento).

Cambios (64 B de cueva + 4 B de gancho; tamaño del fichero intacto):

  gancho  0x7126E6  a2 f7 9b f0  `bl 0x2B4820 (FBM::Init)`  ->  `bl 0x93B000`
  0x7126EA  96 f5 bb f8  `bl 0x4A8864`                       ->  NO se toca
  cueva   0x93B000  64 B a cero (0x93B000..0x93B07F) -> ver CUEVA_ASM

La cueva hace, y sólo eso:

  push {r4,r5,lr} / bl FBM::Init 0x2B4820        ; el efecto original del gancho, igual que antes
  movw/movt r4 = 0xA36A64 = &0xA3699C[10]        ; constantes, sin literales ni relocaciones
  ldr r0,[r4,#4] ; cbnz r0,fin                   ; GUARDA: si idx 10 ya tiene handle, 0 llamadas
                                                 ; (0 escrituras por arranque cuando ya existe)
  fn = 0x2B5185 (dummy) ; arg = 0
  (4,3)  : r0=0x04, r1=fn, r2=0, r3=3 ; bl 0x2B1DEC
  (0x21,3): r0=0x21, r1=fn, r2=0, r3=3 ; bl 0x2B1DEC
  r0=6, r1=3 ; bl InitBackupData 0x2B43F0        ; crea + TermSectorData + Sync (persiste)
  fin: pop {r4,r5,pc}                            ; vuelve a 0x7126EA (lr del bl del gancho)

Comprueba antes de escribir: sha256 del original, bytes originales del gancho/siguiente, semántica del
`bl` (`decode_bl` == 0x2B4820), región de la cueva a cero hasta el literal 0x93B081, PT_LOAD R+X con
VA==offset, ausencia de relocaciones / `ldr|adr` pc-relativos / punteros u32 a la cueva en TODO el
rango, ensamblado con keystone + desensamblado con capstone instrucción a instrucción (mnemónico y
destino de cada `bl`), diff exacto, cabeceras idénticas.

Uso: parche_fbm31_c.py [--lib ORIGEN] [--out build/cfw_fbm_sector31_c/libmpr.so]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from elftools.elf.elffile import ELFFile
from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
LIB_ORIG = os.path.join(
    ROOT, "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
          "nflasha15_unpacked_unpacked/lib/libmpr.so")
SHA_ORIG = "9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30"

GANCHO = 0x7126E6                 # bl 0x2B4820 (FBM::Init) dentro de MprIf::Create
GANCHO_ORIG = bytes.fromhex("a2f79bf0")
GANCHO_DESTINO_ORIG = 0x2B4820
SIGUIENTE = 0x7126EA              # bl 0x4A8864 ; NO se toca
SIGUIENTE_ORIG = bytes.fromhex("96f5bbf8")

CUEVA = 0x93B000
CUEVA_LEN = 0x54                  # código + stub + relleno a cero (< 0x81 libres)
STUB_OFF = 0x50                   # offset del stub dentro de la cueva (0x93B050)
CUEVA_FIN_LIBRE = 0x93B081        # primer byte NO cero después de la zona libre (literal 6000)

FBM_INIT = 0x2B4820
EWBDF = 0x2B1DEC                  # EntryWriteBaseDataFunction(userID, fn, arg, mediaID)
INITB = 0x2B43F0                  # BackupMgr::InitBackupData(OM, mediaID)
FN_DUMMY = 0x2B5185               # dummy de fábrica que usa `FBM EWBDFD` (nunca se llama)
TABLA = 0xA3699C
IDX = 10
ENTRADA = TABLA + 0x14 * IDX      # 0xA36A64
OM_INITB, MEDIA_INITB = 6, 3
RX_END = 0x9BB1C8                 # PT_LOAD 1: off=0 vaddr=0 filesz=memsz=0x9BB1C8 R|X

# La dirección de la tabla NO puede ser una constante absoluta: libmpr se carga con base distinta
# de 0 (medido en el arnés: base=0xAE348000 ⇒ `0xA3699C` en 0xAED7E99C), así que el valor que hay que
# calcular es base+0xA36A64.  Se hace como la v3: `mov rX, pc` + `bic` (PC ya vale base+C+off+4, con
# los dos bits bajos a 0) más un delta que es una constante de ENLACE, sin literales ni relocaciones.
#
# `fn` sí se LLAMA: `0x2B3F7C` (llamada por `WriteBaseData` en `0x2B4130`) recorre las filas de
# 0x9D23FC con (OM, mediaID, fn!=0) y hace `blx r3` con r0 = arg (0x2B3FC6..0x2B3FC8).  Por eso el
# dummy de fábrica 0x2B5185 (`FBM EWBDFD`) NO vale aquí: medido en el arnés, aborta con SIGSEGV
# (prefetch, addr=pc=0x2B5184) al llamarlo desde este hilo.  Se registra un stub propio de 4 B,
# `movs r0,#0 ; bx lr` (devuelve 0 = "sin error", que es lo que espera 0x2B3FD4 `cbz r5`), sin
# memoria ni llamadas: no puede fallar ni ejecuta código de test de fábrica.
CUEVA_ASM = """
    push {{r4, r5, lr}}
    bl   #{FBM_INIT:#x}
    mov  r4, pc
    bic  r4, r4, #3
    movw r1, #0x{delta_lo:04x}
    movt r1, #0x{delta_hi:04x}
    add  r4, r1
    ldr  r0, [r4, #4]
    cbnz r0, fin
    movw r1, #0x{stub_lo:04x}
    movt r1, #0x{stub_hi:04x}
    sub  r5, r4, r1
    adds r5, #1
    movs r0, #4
    mov  r1, r5
    movs r2, #0
    movs r3, #3
    bl   #{EWBDF:#x}
    movs r0, #0x21
    mov  r1, r5
    movs r2, #0
    movs r3, #3
    bl   #{EWBDF:#x}
    movs r0, #{OM_INITB}
    movs r1, #{MEDIA_INITB}
    bl   #{INITB:#x}
fin:
    pop  {{r4, r5, pc}}
    nop
    nop
    movs r0, #0
    bx   lr
"""


def asm_cueva(delta: int, stub_k: int, dummy: bool = False) -> bytes:
    """ensambla la cueva (keystone).  delta: 0xA36A64 − C − off − 4 (⇒ r4 = base+0xA36A64).
    stub_k: 0xA36A64 − C − stub_off (⇒ r5 = base + C + stub_off)."""
    ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB)
    if dummy:   # variante de CONTROL (no usar): en vez del stub, el dummy de fábrica 0x2B5185
        stub_k = ENTRADA - FN_DUMMY
    enc, _ = ks.asm(CUEVA_ASM.format(FBM_INIT=FBM_INIT, EWBDF=EWBDF, INITB=INITB,
                                     OM_INITB=OM_INITB, MEDIA_INITB=MEDIA_INITB,
                                     stub_lo=stub_k & 0xFFFF, stub_hi=(stub_k >> 16) & 0xFFFF,
                                     delta_lo=delta & 0xFFFF, delta_hi=(delta >> 16) & 0xFFFF),
                    addr=CUEVA, as_bytes=True)
    return bytes(enc)


def localiza(enc: bytes) -> tuple[int, int]:
    """(offset del `mov r4, pc`, offset del stub) dentro de la cueva, leyendo el ensamblado."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    ins = list(md.disasm(enc, CUEVA))
    off_mov = next(i.address - CUEVA for i in ins if i.mnemonic == "mov" and i.op_str == "r4, pc")
    # el stub es el `movs r0, #0` inmediatamente anterior al último `bx lr`
    ult = max(k for k, i in enumerate(ins) if i.mnemonic == "bx")
    off_stub = ins[ult - 1].address - CUEVA
    if ins[ult - 1].mnemonic != "movs" or ins[ult - 1].op_str != "r0, #0":
        raise RuntimeError("el stub no es `movs r0,#0 ; bx lr`")
    return off_mov, off_stub


# lo que el desensamblador tiene que devolver, en orden (mnemónico, operando o None = no comprobar)
ESPERADO = [
    ("push", "{r4, r5, lr}"), ("bl", None), ("mov", "r4, pc"), ("bic", None), ("movw", None), ("movt", None),
    ("add", "r4, r1"),
    ("ldr", "r0, [r4, #4]"), ("cbnz", None), ("movw", None), ("movt", None),
    ("sub.w", "r5, r4, r1"), ("adds", "r5, #1"),
    ("movs", "r0, #4"), ("mov", "r1, r5"), ("movs", "r2, #0"), ("movs", "r3, #3"), ("bl", None),
    ("movs", "r0, #0x21"), ("mov", "r1, r5"), ("movs", "r2, #0"), ("movs", "r3, #3"), ("bl", None),
    ("movs", "r0, #6"), ("movs", "r1, #3"), ("bl", None), ("pop", "{r4, r5, pc}"),
    ("nop", None), ("nop", None), ("movs", "r0, #0"), ("bx", "lr"),
]
BL_ESPERADOS = [FBM_INIT, EWBDF, EWBDF, INITB]


def bl_thumb(pc: int, destino: int) -> bytes:
    off = destino - (pc + 4)
    assert -0x1000000 <= off <= 0xFFFFFE and off % 2 == 0, hex(off)
    s = 1 if off < 0 else 0
    imm = off & 0x1FFFFFF
    i1, i2 = (imm >> 23) & 1, (imm >> 22) & 1
    j1, j2 = (1 - i1) ^ s, (1 - i2) ^ s
    return struct.pack("<HH", 0xF000 | (s << 10) | ((imm >> 12) & 0x3FF),
                       0xD000 | (j1 << 13) | (j2 << 11) | ((imm >> 1) & 0x7FF))


def decode_bl(pc: int, b: bytes) -> int:
    hw1, hw2 = struct.unpack("<HH", b)
    assert (hw1 & 0xF800) == 0xF000 and (hw2 & 0xD000) == 0xD000, "no es BL"
    s = (hw1 >> 10) & 1
    imm10, imm11 = hw1 & 0x3FF, hw2 & 0x7FF
    j1, j2 = (hw2 >> 13) & 1, (hw2 >> 11) & 1
    i1, i2 = 1 - (j1 ^ s), 1 - (j2 ^ s)
    imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
    if s:
        imm -= 1 << 25
    return pc + 4 + imm


def secciones(e: ELFFile) -> list[dict]:
    return [{"name": s.name, "type": str(s["sh_type"]), "addr": s["sh_addr"],
             "off": s["sh_offset"], "size": s["sh_size"]} for s in e.iter_sections()]


def segmentos(e: ELFFile) -> list[dict]:
    return [{"type": str(s["p_type"]), "off": s["p_offset"], "vaddr": s["p_vaddr"],
             "filesz": s["p_filesz"], "memsz": s["p_memsz"], "flags": s["p_flags"]}
            for s in e.iter_segments()]


def relocs(e: ELFFile) -> list[tuple[str, int, int]]:
    out = []
    for s in e.iter_sections():
        t = str(s["sh_type"])
        if t not in ("SHT_RELA", "SHT_REL") or not s["sh_size"]:
            continue
        ent = 12 if t == "SHT_RELA" else 8
        d = s.data()
        for k in range(s["sh_size"] // ent):
            r_off, r_info = struct.unpack_from("<II", d, k * ent)
            out.append((s.name, r_off, r_info & 0xFF))
    return out


def pc_rel_refs(d: bytes) -> set[int]:
    """Destinos de `ldr rX,[pc,#imm]`, `adr`, `ldr.w`/`ldr.w rX,[pc,#±imm]` (barrido por patrón en
    posiciones pares, porque un barrido lineal se desincroniza en las islas de literales)."""
    import numpy as np
    hw = np.frombuffer(d[:RX_END], dtype="<u2")
    base = ((np.arange(len(hw), dtype=np.int64) * 2 + 4) & ~np.int64(3))
    t = set()
    m = (hw & 0xF800) == 0x4800
    t |= set(int(x) for x in base[m] + (hw[m] & 0xFF).astype(np.int64) * 4)
    m = (hw & 0xF800) == 0xA000
    t |= set(int(x) for x in base[m] + (hw[m] & 0xFF).astype(np.int64) * 4)
    for mask, signo in ((hw == 0xF8DF, +1), ((hw & 0xFF7F) == 0xF85F, -1)):
        i = np.nonzero(mask)[0]
        nx = (hw[np.minimum(i + 1, len(hw) - 1)] & 0xFFF).astype(np.int64)
        t |= set(int(x) for x in (base[i] + signo * nx))
    return t


def desasm(d: bytes, va: int, n: int) -> list[str]:
    """desensambla d[va:va+n] como si estuviera cargado en va (d = fichero completo)."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    return ["%08x: %-10s %-8s %s" % (i.address, i.bytes.hex(), i.mnemonic, i.op_str)
            for i in md.disasm(d[va:va + n], va)]


def desasm_va(code: bytes, va: int) -> list[str]:
    """desensambla `code` como si estuviera cargado en va (code = sólo el fragmento)."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    return ["%08x: %-10s %-8s %s" % (i.address, i.bytes.hex(), i.mnemonic, i.op_str)
            for i in md.disasm(code, va)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lib", default=LIB_ORIG)
    ap.add_argument("--out", default=os.path.join(ROOT, "build/cfw_fbm_sector31_c/libmpr.so"))
    ap.add_argument("--fn-dummy", action="store_true",
                    help="CONTROL negativo: registra el dummy de fábrica 0x2B5185 en vez del stub "
                         "(medido: SIGSEGV al llamarlo desde este hilo)")
    a = ap.parse_args()
    orig = open(a.lib, "rb").read()
    sha = hashlib.sha256(orig).hexdigest()
    print("original : %s" % a.lib)
    print("sha256   : %s%s" % (sha, "" if sha == SHA_ORIG else "   (AVISO: no es el 3.21 esperado)"))
    if sha != SHA_ORIG:
        print("ERROR: sha256 distinto del de fábrica")
        return 2

    # 0. ensamblar la cueva (keystone) y comprobar que cabe en la zona libre
    enc = asm_cueva(0, 0, a.fn_dummy)                      # 1ª pasada: sólo para medir offsets
    off_mov, off_stub = localiza(enc)
    delta = (ENTRADA - CUEVA) - ((off_mov + 4) & ~3)      # r4 = base+0xA36A64
    stub_k = (ENTRADA - CUEVA) - off_stub                 # r5 = base+C+off_stub
    enc = asm_cueva(delta, stub_k, a.fn_dummy)             # 2ª pasada: constantes definitivas
    off_mov2, off_stub2 = localiza(enc)
    if (off_mov2, off_stub2) != (off_mov, off_stub):
        print("ERROR: la 2ª pasada movió el código")
        return 23
    print("anclas   : mov r4,pc en C+%#x (r4 = base+%#x) · stub fn en C+%#x (r5 = base+%#x|1)"
          % (off_mov, ENTRADA, off_stub, CUEVA + off_stub))
    print("delta    : %#x · stub_k %#x" % (delta & 0xFFFFFFFF, stub_k & 0xFFFFFFFF))
    print("cueva    : %d B de código en %08x (máximo %d B libres hasta %08x)"
          % (len(enc), CUEVA, CUEVA_FIN_LIBRE - CUEVA, CUEVA_FIN_LIBRE))
    if len(enc) > CUEVA_LEN:
        print("ERROR: no cabe (%d > %d)" % (len(enc), CUEVA_LEN))
        return 3
    CUEVA_HEX = enc + bytes(CUEVA_LEN - len(enc))

    # 1. bytes originales
    if orig[GANCHO:GANCHO + 4] != GANCHO_ORIG:
        print("ERROR: en %08x esperaba %s y hay %s" % (GANCHO, GANCHO_ORIG.hex(), orig[GANCHO:GANCHO + 4].hex()))
        return 4
    if orig[CUEVA:CUEVA + CUEVA_LEN] != bytes(CUEVA_LEN):
        print("ERROR: la cueva %08x..%08x no está a cero" % (CUEVA, CUEVA + CUEVA_LEN - 1))
        return 5
    # 2. semántica del original
    if decode_bl(GANCHO, orig[GANCHO:GANCHO + 4]) != GANCHO_DESTINO_ORIG:
        print("ERROR: %08x no es `bl 0x%08x`" % (GANCHO, GANCHO_DESTINO_ORIG))
        return 6
    if orig[SIGUIENTE:SIGUIENTE + 4] != SIGUIENTE_ORIG:
        print("ERROR: %08x no es %s" % (SIGUIENTE, SIGUIENTE_ORIG.hex()))
        return 7
    print("gancho   : %08x  %s = bl 0x%08x (FBM::Init)  ->  %s = bl 0x%08x"
          % (GANCHO, GANCHO_ORIG.hex(" "), decode_bl(GANCHO, orig[GANCHO:GANCHO + 4]),
             bl_thumb(GANCHO, CUEVA).hex(" "), CUEVA))
    print("siguiente: %08x  %s (no se toca)" % (SIGUIENTE, SIGUIENTE_ORIG.hex(" ")))

    # 3. la cueva se desensambla EXACTAMENTE como se pretende (mnemónico y operando y destino de bl)
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    ins = list(md.disasm(enc, CUEVA))
    if len(ins) != len(ESPERADO):
        print("ERROR: %d instrucciones, esperaba %d" % (len(ins), len(ESPERADO)))
        return 8
    for i, (mne, ops) in zip(ins, ESPERADO):
        if i.mnemonic != mne or (ops is not None and i.op_str != ops):
            print("ERROR: en %08x leí «%s %s», esperaba «%s %s»" % (i.address, i.mnemonic, i.op_str, mne, ops))
            return 9
        if i.mnemonic == "bl":
            dst = decode_bl(i.address, i.bytes)
            if dst != BL_ESPERADOS[sum(1 for j in ins if j.address < i.address and j.mnemonic == "bl")]:
                print("ERROR: bl en %08x va a %08x" % (i.address, dst))
                return 10
    print("cueva    : %08x  %s" % (CUEVA, " ".join("%02x" % b for b in CUEVA_HEX)))
    print("desasm   :")
    for l in desasm_va(enc, CUEVA):
        print("   " + l)

    # 4. zona libre: el byte siguiente (0x93B081 = literal 6000) NO se toca
    libre = CUEVA + CUEVA_LEN
    if orig[libre:CUEVA_FIN_LIBRE] != bytes(CUEVA_FIN_LIBRE - libre):
        print("ERROR: quedan bytes no cero entre %08x y %08x" % (libre, CUEVA_FIN_LIBRE))
        return 11
    print("zona     : %08x..%08x a cero; %08x.. sin tocar (%s…)"
          % (CUEVA, libre - 1, libre, orig[libre:libre + 8].hex()))

    # 5. segmentos: la cueva tiene que ser R+X y VA==offset; el gancho, ejecutable
    e = ELFFile(open(a.lib, "rb"))
    segs, secs = segmentos(e), secciones(e)
    rx = [s for s in segs if s["type"] == "PT_LOAD" and s["flags"] & 5 == 5 and s["off"] == s["vaddr"]]
    if not rx:
        print("ERROR: no hay PT_LOAD R+X con VA==offset")
        return 12
    seg = rx[0]
    if not (seg["vaddr"] <= CUEVA and CUEVA + CUEVA_LEN <= seg["vaddr"] + seg["filesz"]):
        print("ERROR: la cueva no cae dentro del PT_LOAD R+X")
        return 13
    print("segmento : PT_LOAD R+X off=0 vaddr=0 filesz=%#x (cueva y gancho dentro)" % seg["filesz"])

    # 6. sin relocaciones, sin referencias pc-relativas y sin punteros a la cueva
    rel = relocs(e)
    dentro = [(n, r) for n, r, _ in rel if GANCHO <= r < GANCHO + 4 or CUEVA <= r < CUEVA + CUEVA_LEN]
    print("relocs   : %d en el ELF; en el gancho/cueva: %s" % (len(rel), dentro or "NINGUNA"))
    if dentro:
        print("ERROR: hay relocaciones en la zona tocada")
        return 14
    refs = pc_rel_refs(orig) & set(range(CUEVA, CUEVA + CUEVA_LEN))
    print("ldr/adr  : pc-relativos que apuntan a la cueva: %s" % (sorted(hex(x) for x in refs) or "NINGUNO"))
    if refs:
        print("ERROR: alguien lee literales de la zona de la cueva")
        return 15
    ptr, coinc = [], []
    for i in range(0, len(orig) & ~3, 4):
        w = struct.unpack_from("<I", orig, i)[0]
        if w not in range(CUEVA, CUEVA + CUEVA_LEN):
            continue
        s = None
        for sc in e.iter_sections():
            if sc["sh_addr"] and sc["sh_addr"] <= i < sc["sh_addr"] + sc["sh_size"]:
                s = sc
                break
        flags = s["sh_flags"] if s else 0
        cubierto = False
        if flags & 0x4:                        # SHF_EXECINSTR: ¿cae dentro de una instrucción?
            for ini in (i - 8, i - 4, i - 2, i):
                for it in md.disasm(orig[ini:ini + 10], ini):
                    if it.address < i + 4 and it.address + it.size > i and it.address != i:
                        cubierto = True
                    break
        (coinc if cubierto else ptr).append((i, w, s.name if s else "?"))
    print("punteros : u32 iguales a una dirección de la cueva: %s"
          % (["%08x=%#010x(%s)" % x for x in ptr] or "NINGUNO"))
    if coinc:
        print("           descartados por caer dentro de una instrucción: %s"
              % ["%08x=%#010x(%s)" % x for x in coinc])
    if ptr:
        print("ERROR: alguien guarda un puntero a la cueva")
        return 16

    # 7. aplicar y comprobar el diff exacto
    buf = bytearray(orig)
    buf[GANCHO:GANCHO + 4] = bl_thumb(GANCHO, CUEVA)
    buf[CUEVA:CUEVA + CUEVA_LEN] = CUEVA_HEX
    previstos = set(range(GANCHO, GANCHO + 4)) | set(range(CUEVA, CUEVA + CUEVA_LEN))
    if len(buf) != len(orig):
        print("ERROR: cambió el tamaño")
        return 17
    reales = {i for i in range(len(orig)) if orig[i] != buf[i]}
    deben = {i for i in range(GANCHO, GANCHO + 4) if orig[i] != buf[i]}
    deben |= {i for i in range(CUEVA, CUEVA + CUEVA_LEN) if orig[i] != buf[i]}
    if reales != deben:
        print("ERROR: difieren bytes no previstos: %s" % sorted(reales ^ deben))
        return 18
    print("diff     : %d bytes en 2 rangos (%08x..%08x, %08x..%08x); %d de ellos cambian de valor "
          "(%d ya eran 0x00); tamaño %d B sin cambios"
          % (len(previstos), GANCHO, GANCHO + 3, CUEVA, CUEVA + CUEVA_LEN - 1, len(reales),
             len(previstos) - len(reales), len(buf)))

    # 8. cabeceras, segmentos y secciones idénticos
    e2 = ELFFile(io.BytesIO(bytes(buf)))
    if segs != segmentos(e2):
        print("ERROR: cambió la tabla de segmentos")
        return 19
    if secs != secciones(e2):
        print("ERROR: cambió la tabla de secciones")
        return 20
    if orig[:e.header.e_phoff + e.header.e_phnum * e.header.e_phentsize] != \
            bytes(buf[:e.header.e_phoff + e.header.e_phnum * e.header.e_phentsize]):
        print("ERROR: cambió la cabecera/PT_*")
        return 21
    print("ELF      : cabecera, %d PT_* y %d secciones idénticas byte a byte" % (len(segs), len(secs)))

    # 9. desensamblado del gancho resultante
    print("desasm   : gancho 0x7126DE..0x7126F2")
    for l in desasm(bytes(buf), 0x7126DE, 0x14):
        print("   " + l)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    if os.path.abspath(a.out).startswith(os.path.join(ROOT, "firmware") + os.sep):
        print("ERROR: la salida no puede estar dentro de firmware/")
        return 22
    open(a.out, "wb").write(bytes(buf))
    print("salida   : %s" % a.out)
    print("sha256   : %s" % hashlib.sha256(bytes(buf)).hexdigest())
    print("original intacto: %s" % hashlib.sha256(open(a.lib, "rb").read()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
