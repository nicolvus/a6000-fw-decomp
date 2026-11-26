#!/usr/bin/env python3
"""FILM-PB-1 · parche v2 de libmpr.so 3.21: crear el sector FBM 0x31 (userID 0x04/0x21,
mediaID 3, OM 6, índice 10 de 0xA3699C) con la primitiva DIRECTA `FlashLib::CreateSector32`,
sin pasar por `BackupMgr::InitBackupData` (que aborta en 0x2B4072 con 0x10800010 porque las 37
filas de 0x9D23FC tienen `fn` a 0).

Cambios (64 bytes, tamaño del fichero intacto):

  gancho  0x7126E6  a2 f7 9b f0  `bl 0x2B4820 (FBM::Init)`      ->  `bl 0x93B000`
  0x7126EA  96 f5 bb f8  `bl 0x4A8864`                          ->  NO se toca
  cueva   0x93B000  60 B a cero  ->  ver CUEVA_HEX (0x36 B de código + 2 de alineado +
                                     literal 0x00A36A64 = &0xA3699C[10] en 0x93B038)

La cueva hace, y sólo eso:
  push {r4,lr} / bl FBM::Init 0x2B4820        ; el efecto original del gancho, igual que antes
  sub sp,#8 ; movs r0,#0 ; str r0,[sp] ; str r0,[sp,#4]
                                              ; cero los 2 slots de salida COMO WriteBaseData
                                              ; 0x2B4042..0x2B404A (por si CreateSector32 sólo
                                              ; escribe 16 bits)
  ldr r4,=&0xA36A64 ; ldr r0,[r4,#4] ; cbnz r0,fin
                                              ; IDEMPOTENTE: si idx 10 ya tiene handle, no hace nada
  r0=0x31, r1=0, r2=sp, r3=sp+4 ; bl CreateSector32 0x2B7080
  cbnz r0,fin                                 ; si CreateSector32 falla, NO se escribe la entrada
  [+0]=*r3 ; [+4]=*r2 ; [+8]=1 ; [+0xC]=6      ; igual que WriteBaseData 0x2B40DA..0x2B40EA
  add sp,#8 ; pop {r4,pc}                      ; vuelve a 0x7126EA (lr del bl del gancho)

Comprueba antes de escribir: sha256 del original, bytes originales del gancho/siguiente/cueva,
semántica de los bl, PT_LOAD R+X con VA==offset, ausencia de relocaciones / `ldr|adr` pc-relativos /
punteros u32 en TODO el rango usado, diff exacto, cabeceras idénticas y desensamblado.
Uso: parche_fbm31_v2.py [--lib ORIGEN] [--out build/cfw_fbm_sector31_v2/libmpr.so]
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
CUEVA_LEN = 0x3C
CUEVA_ORIG = bytes(CUEVA_LEN)
CUEVA_HEX = bytes.fromhex(
    "10 b5 79 f5 0d f4 82 b0 00 20 00 90 01 90 0a 4c 60 68 70 b9 31 20 00 21 6a 46 01 ab"
    " 7c f5 30 f0 38 b9 00 99 01 9a 22 60 61 60 01 21 a1 60 06 21 e1 60 02 b0 10 bd"
    " 00 00 64 6a a3 00")
assert len(CUEVA_HEX) == CUEVA_LEN

FBM_INIT = 0x2B4820               # FBM::Init  (efecto original del gancho)
CREATE_SECTOR32 = 0x2B7080        # _ZN8FlashLib14CreateSector32Em12FBS_MOVEFLAGPmS1_
ENTRADA = 0xA3699C + 0x14 * 10    # 0xA36A64: entrada idx 10 (sector 0x31)
FILE_TYPE = 0x31
OM = 6

RX_END = 0x9BB1C8                 # PT_LOAD 1: off=0 vaddr=0 filesz=memsz=0x9BB1C8 R|X

# desensamblado esperado de la cueva, instrucción a instrucción (capstone 5 / ARM / Thumb)
INTENCION = [
    "push {r4, lr}", "bl #0x2b4820", "sub sp, #8", "movs r0, #0", "str r0, [sp]",
    "str r0, [sp, #4]", "ldr r4, [pc, #0x28]", "ldr r0, [r4, #4]", "cbnz r0, #0x93b032",
    "movs r0, #0x31", "movs r1, #0", "mov r2, sp", "add r3, sp, #4", "bl #0x2b7080",
    "cbnz r0, #0x93b032", "ldr r1, [sp]", "ldr r2, [sp, #4]", "str r2, [r4]",
    "str r1, [r4, #4]", "movs r1, #1", "str r1, [r4, #8]", "movs r1, #6",
    "str r1, [r4, #0xc]", "add sp, #8", "pop {r4, pc}",
]
LIT_OFF = 0x38


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
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    return ["%08x: %-10s %-8s %s" % (i.address, i.bytes.hex(), i.mnemonic, i.op_str)
            for i in md.disasm(d[va:va + n], va)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lib", default=LIB_ORIG)
    ap.add_argument("--out", default=os.path.join(ROOT, "build/cfw_fbm_sector31_v2/libmpr.so"))
    a = ap.parse_args()
    orig = open(a.lib, "rb").read()
    sha = hashlib.sha256(orig).hexdigest()
    print("original : %s" % a.lib)
    print("sha256   : %s%s" % (sha, "" if sha == SHA_ORIG else "   (AVISO: no es el 3.21 esperado)"))
    if sha != SHA_ORIG:
        print("ERROR: sha256 distinto del de fábrica")
        return 2

    print("gancho   : %08x  %s -> %s   bl 0x%08x  (antes: bl 0x%08x)"
          % (GANCHO, GANCHO_ORIG.hex(" "), bl_thumb(GANCHO, CUEVA).hex(" "), CUEVA, GANCHO_DESTINO_ORIG))
    print("cueva    : %08x  %s" % (CUEVA, " ".join("%02x" % b for b in CUEVA_ORIG)))
    print("        -> %08x  %s" % (CUEVA, " ".join("%02x" % b for b in CUEVA_HEX)))

    # 1. bytes originales
    if orig[GANCHO:GANCHO + 4] != GANCHO_ORIG:
        print("ERROR: en %08x esperaba %s y hay %s" % (GANCHO, GANCHO_ORIG.hex(), orig[GANCHO:GANCHO + 4].hex()))
        return 3
    if orig[CUEVA:CUEVA + CUEVA_LEN] != CUEVA_ORIG:
        print("ERROR: la cueva %08x no está a cero" % CUEVA)
        return 4
    # 2. semántica del original
    if decode_bl(GANCHO, orig[GANCHO:GANCHO + 4]) != GANCHO_DESTINO_ORIG:
        print("ERROR: %08x no es `bl 0x%08x`" % (GANCHO, GANCHO_DESTINO_ORIG))
        return 5
    if orig[SIGUIENTE:SIGUIENTE + 4] != SIGUIENTE_ORIG:
        print("ERROR: %08x no es %s" % (SIGUIENTE, SIGUIENTE_ORIG.hex()))
        return 6
    print("original : %08x = bl 0x%08x (FBM::Init) · %08x = %s (no se toca)"
          % (GANCHO, decode_bl(GANCHO, orig[GANCHO:GANCHO + 4]), SIGUIENTE, SIGUIENTE_ORIG.hex(" ")))
    # 3. la cueva se decodifica EXACTAMENTE como se pretende
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    dis = ["%s %s" % (i.mnemonic, i.op_str) for i in md.disasm(CUEVA_HEX[:0x36], CUEVA)]
    if dis != INTENCION:
        for k, (x, y) in enumerate(zip(INTENCION, dis)):
            if x != y:
                print("ERROR: instr %d de la cueva: quería %r y es %r" % (k, x, y))
        if len(dis) != len(INTENCION):
            print("ERROR: la cueva decodifica %d instrucciones, no %d" % (len(dis), len(INTENCION)))
        return 7
    for pc, dst in ((CUEVA + 2, FBM_INIT), (CUEVA + 0x1C, CREATE_SECTOR32)):
        if decode_bl(pc, CUEVA_HEX[pc - CUEVA:pc - CUEVA + 4]) != dst:
            print("ERROR: la cueva no codifica bl 0x%08x en %08x" % (dst, pc))
            return 7
    if struct.unpack_from("<I", CUEVA_HEX, LIT_OFF)[0] != ENTRADA:
        print("ERROR: el literal no es %#x" % ENTRADA)
        return 7
    print("cueva    : %d instrucciones verificadas; literal en %08x = %#x (&0xA3699C[10])"
          % (len(INTENCION), CUEVA + LIT_OFF, ENTRADA))
    print("vuelta   : pop {r4,pc} usa el lr del bl del gancho -> continua en %08x (%s)"
          % (SIGUIENTE, SIGUIENTE_ORIG.hex(" ")))

    # 4. segmento R+X y alineación
    with open(a.lib, "rb") as f:
        e = ELFFile(f)
        segs, secs = segmentos(e), secciones(e)
    for va in (GANCHO, CUEVA):
        if va % 2:
            print("ERROR: %08x no está alineado a 2" % va)
            return 8
        x = [s for s in segs if s["type"] == "PT_LOAD" and s["off"] <= va < s["off"] + s["filesz"]]
        if not x or not (x[0]["flags"] & 0x1):
            print("ERROR: %08x no cae en un PT_LOAD ejecutable" % va)
            return 9
        if x[0]["vaddr"] != x[0]["off"]:
            print("ERROR: en %08x VA != offset; el parche usa offset == VA" % va)
            return 10
        sec = next((s["name"] for s in secs if s["addr"] and s["addr"] <= va < s["addr"] + s["size"]), "?")
        print("sitio    : %08x en %s, PT_LOAD R+X off=%08x" % (va, sec, x[0]["off"]))
    if CUEVA + CUEVA_LEN > 0x93B081:
        print("ERROR: la cueva se sale del tramo de ceros (0x93AFD4..0x93B080)")
        return 10

    # 5. cueva sin referencias ni relocaciones en TODO el rango
    rel = relocs(ELFFile(open(a.lib, "rb")))
    dentro = [(n, r) for n, r, _ in rel if GANCHO <= r < GANCHO + 4 or CUEVA <= r < CUEVA + CUEVA_LEN]
    print("reloc    : %d entradas en .rel*; en los sitios parcheados: %s" % (len(rel), dentro or "NINGUNA"))
    if dentro:
        print("ERROR: hay relocaciones en los sitios parcheados")
        return 11
    refs = pc_rel_refs(orig) & set(range(CUEVA, CUEVA + CUEVA_LEN))
    print("refs     : ldr/adr pc-relativos que leen la cueva: %s" % (sorted(refs) or "NINGUNO"))
    if refs:
        print("ERROR: la cueva está referenciada")
        return 12
    # punteros: un u32 igual a una dirección de la cueva. En secciones NO ejecutables (.data,
    # .rodata, .got…) sería un puntero de verdad; en .text hay que descartar que sea una ventana de
    # 4 B a caballo de dos instrucciones (falso positivo), así que se comprueba si alguna
    # instrucción decodificada cubre esos bytes.
    ejec = [s for s in secs if s["addr"] and s["size"]]
    def sec_de(va):
        return next((s for s in ejec if s["addr"] <= va < s["addr"] + s["size"]), None)
    md2 = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    ptr, coinc = [], []
    for i in range(0, len(orig) & ~3, 4):
        w = struct.unpack_from("<I", orig, i)[0]
        if w not in range(CUEVA, CUEVA + CUEVA_LEN):
            continue
        s = sec_de(i)
        flags = 0
        for sec in ELFFile(open(a.lib, "rb")).iter_sections():
            if sec["sh_addr"] and sec["sh_addr"] <= i < sec["sh_addr"] + sec["sh_size"]:
                flags = sec["sh_flags"]
                break
        cubierto = False
        if flags & 0x4:                        # SHF_EXECINSTR: ¿cae dentro de una instrucción?
            for ini in (i - 8, i - 4, i - 2, i):
                for ins in md2.disasm(orig[ini:ini + 10], ini):
                    if ins.address < i + 4 and ins.address + ins.size > i and ins.address != i:
                        cubierto = True
                    break
        (coinc if cubierto else ptr).append((i, w, s["name"] if s else "?"))
    print("punteros : u32 iguales a una dirección de la cueva: %s"
          % (["%08x=%#010x(%s)" % x for x in ptr] or "NINGUNO"))
    if coinc:
        print("           descartados por caer dentro de una instrucción: %s"
              % ["%08x=%#010x(%s)" % x for x in coinc])
    if ptr:
        print("ERROR: alguien guarda un puntero a la cueva")
        return 13

    # 6. aplicar y comprobar el diff exacto
    buf = bytearray(orig)
    buf[GANCHO:GANCHO + 4] = bl_thumb(GANCHO, CUEVA)
    buf[CUEVA:CUEVA + CUEVA_LEN] = CUEVA_HEX
    previstos = set(range(GANCHO, GANCHO + 4)) | set(range(CUEVA, CUEVA + CUEVA_LEN))
    if len(buf) != len(orig):
        print("ERROR: cambió el tamaño")
        return 14
    reales = {i for i in range(len(orig)) if orig[i] != buf[i]}
    deben = {i for i in range(GANCHO, GANCHO + 4) if orig[i] != buf[i]}
    deben |= {i for i in range(CUEVA, CUEVA + CUEVA_LEN) if orig[i] != buf[i]}
    if reales != deben:
        print("ERROR: difieren bytes no previstos: %s" % sorted(reales ^ deben))
        return 15
    print("diff     : %d bytes escritos en 2 rangos (%08x..%08x, %08x..%08x); %d de ellos cambian "
          "de valor (%d ya eran 0x00); tamaño %d B sin cambios"
          % (len(previstos), GANCHO, GANCHO + 3, CUEVA, CUEVA + CUEVA_LEN - 1, len(reales),
             len(previstos) - len(reales), len(buf)))

    # 7. cabeceras, segmentos y secciones idénticos
    e2 = ELFFile(io.BytesIO(bytes(buf)))
    if segs != segmentos(e2):
        print("ERROR: cambió la tabla de segmentos")
        return 16
    if secs != secciones(e2):
        print("ERROR: cambió la tabla de secciones")
        return 17
    if orig[:e.header.e_phoff + e.header.e_phnum * e.header.e_phentsize] != \
            bytes(buf[:e.header.e_phoff + e.header.e_phnum * e.header.e_phentsize]):
        print("ERROR: cambió la cabecera/PT_*")
        return 18
    print("ELF      : cabecera, %d PT_* y %d secciones idénticas byte a byte" % (len(segs), len(secs)))

    # 8. desensamblado del resultado
    print("desasm   : cueva %08x" % CUEVA)
    for l in desasm(bytes(buf), CUEVA, CUEVA_LEN):
        print("   " + l)
    print("desasm   : gancho 0x7126DE..0x7126F2")
    for l in desasm(bytes(buf), 0x7126DE, 0x14):
        print("   " + l)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    if os.path.abspath(a.out).startswith(os.path.join(ROOT, "firmware") + os.sep):
        print("ERROR: la salida no puede estar dentro de firmware/")
        return 19
    open(a.out, "wb").write(bytes(buf))
    print("salida   : %s" % a.out)
    print("sha256   : %s" % hashlib.sha256(bytes(buf)).hexdigest())
    print("original intacto: %s" % hashlib.sha256(open(a.lib, "rb").read()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
