#!/usr/bin/env python3
"""FILM-PB-1 · parche MÍNIMO de libmpr.so 3.21: crear el sector FBM 0x31 (userID 0x04/0x21,
mediaID 3, OM 6) llamando UNA vez a BackupMgr::InitBackupData(6, 3) tras FBM::Init.

Cambios (20 bytes, tamaño del fichero intacto):

  gancho  0x7126E6  a2 f7 9b f0  `bl 0x2B4820 (FBM::Init)`   ->  bl 0x93B000 (cueva)
  cueva   0x93B000  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
                  -> 01 b5 | bl 0x2B4820 | 06 20 | 03 21 | bl 0x2B43F0 | 01 bd
                     push {r0,lr}  FBM::Init  r0=6  r1=3  InitBackupData(6,3)  pop {r0,pc}
                  `pop {r0,pc}` devuelve a 0x7126EA (lr que dejó el `bl` del gancho), así que
                  la instrucción original de 0x7126EA (bl 0x4A8864) se ejecuta igual que antes.

Comprueba antes de escribir:
  1. sha256 del original (3.21), bytes originales del gancho y de la cueva;
  2. que el `bl` sustituido en 0x7126E6 llama de verdad a 0x2B4820 y que 0x7126EA es `bl 0x4A8864`;
  3. que gancho y cueva caen en el PT_LOAD R+X (VA == offset), alineados a 2;
  4. que la cueva es un tramo de ceros NO referenciado: sin relocación (.rel.dyn/.rel.plt),
     sin `ldr rX,[pc,#imm]`/`ldr.w`/`adr` que la lea, sin ningún u32 del fichero igual a una de
     sus direcciones;
  5. que el conjunto de bytes distintos es EXACTAMENTE el previsto y el tamaño no cambia;
  6. que cabecera ELF, tabla de segmentos y tabla de secciones quedan byte a byte iguales;
  7. que no hay relocación con r_offset en ninguno de los dos sitios;
  8. desensambla el resultado (capstone 5) y comprueba la codificación del BL.
Uso: parche_fbm31.py [--lib ORIGEN] [--out build/cfw_fbm_sector31/libmpr.so]
"""
from __future__ import annotations

import argparse
import hashlib
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

GANCHO = 0x7126E6            # bl 0x2B4820 (FBM::Init) en MprIf::Create
GANCHO_ORIG = bytes.fromhex("a2f79bf0")
GANCHO_DESTINO_ORIG = 0x2B4820
SIGUIENTE = 0x7126EA         # bl 0x4A8864 ; debe seguir siendo un bl (no lo tocamos)
SIGUIENTE_ORIG = bytes.fromhex("96f5bbf8")

CUEVA = 0x93B000
CUEVA_LEN = 0x10
CUEVA_ORIG = bytes(CUEVA_LEN)

FBM_INIT = 0x2B4820          # FlashLib/FBM::Init
INIT_BACKUP_DATA = 0x2B43F0  # BackupMgr::InitBackupData(unsigned long OM, unsigned long mediaID)
OM = 6
MEDIAID = 3

RX_END = 0x9BB1C8            # PT_LOAD 1: off=0 vaddr=0 filesz=memsz=0x9BB1C8 flags=R|X


def bl_thumb(pc: int, destino: int) -> bytes:
    """Codifica `BL <destino>` (T1) situado en `pc`."""
    off = destino - (pc + 4)
    assert -0x1000000 <= off <= 0xFFFFFE, hex(off)
    s = 1 if off < 0 else 0
    imm = off & 0x1FFFFFF
    i1, i2 = (imm >> 23) & 1, (imm >> 22) & 1
    j1, j2 = (1 - i1) ^ s, (1 - i2) ^ s
    imm10, imm11 = (imm >> 12) & 0x3FF, (imm >> 1) & 0x7FF
    hw1 = 0xF000 | (s << 10) | imm10
    hw2 = 0xD000 | (j1 << 13) | (j2 << 11) | imm11
    return struct.pack("<HH", hw1, hw2)


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


def cueva_bytes() -> bytes:
    out = b""
    out += struct.pack("<H", 0xB501)            # push {r0, lr}   (8 B: sp sigue alineado a 8)
    out += bl_thumb(CUEVA + len(out), FBM_INIT)
    out += struct.pack("<H", 0x2006)            # movs r0, #6
    out += struct.pack("<H", 0x2103)            # movs r1, #3
    out += bl_thumb(CUEVA + len(out), INIT_BACKUP_DATA)
    out += struct.pack("<H", 0xBD01)            # pop {r0, pc} -> vuelve a 0x7126EA
    assert len(out) <= CUEVA_LEN
    return out + bytes(CUEVA_LEN - len(out))


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
    """Todos los destinos de `ldr rX,[pc,#imm]` (T16/T32), `adr`/`adr.w`: barrido por PATRÓN en
    posiciones pares (un barrido lineal se desincroniza en las islas de literales de .text)."""
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
    ap.add_argument("--out", default=os.path.join(ROOT, "build/cfw_fbm_sector31/libmpr.so"))
    a = ap.parse_args()
    orig = open(a.lib, "rb").read()
    sha = hashlib.sha256(orig).hexdigest()
    print("original : %s" % a.lib)
    print("sha256   : %s%s" % (sha, "" if sha == SHA_ORIG else "   (AVISO: no es el 3.21 esperado)"))
    if sha != SHA_ORIG:
        print("ERROR: sha256 distinto del de fábrica")
        return 2

    nuevo = cueva_bytes()
    print("gancho   : %08x  %s -> %s   bl 0x%08x  (antes: bl 0x%08x)"
          % (GANCHO, GANCHO_ORIG.hex(" "), bl_thumb(GANCHO, CUEVA).hex(" "), CUEVA, GANCHO_DESTINO_ORIG))
    print("cueva    : %08x  %s" % (CUEVA, " ".join("%02x" % b for b in CUEVA_ORIG)))
    print("        -> %08x  %s" % (CUEVA, " ".join("%02x" % b for b in nuevo)))

    # 1. bytes originales
    if orig[GANCHO:GANCHO + 4] != GANCHO_ORIG:
        print("ERROR: en %08x esperaba %s y hay %s" % (GANCHO, GANCHO_ORIG.hex(), orig[GANCHO:GANCHO + 4].hex()))
        return 3
    if orig[CUEVA:CUEVA + CUEVA_LEN] != CUEVA_ORIG:
        print("ERROR: la cueva %08x no está a cero: %s" % (CUEVA, orig[CUEVA:CUEVA + CUEVA_LEN].hex()))
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
    for pc, dst in ((CUEVA + 2, FBM_INIT), (CUEVA + 10, INIT_BACKUP_DATA)):
        cod = nuevo[pc - CUEVA:pc - CUEVA + 4]
        if decode_bl(pc, cod) != dst:
            print("ERROR: la cueva no codifica bl 0x%08x en %08x (%s)" % (dst, pc, cod.hex()))
            return 7
    print("cueva    : bl 0x%08x en %08x y bl 0x%08x en %08x (decodificados = pedidos)"
          % (FBM_INIT, CUEVA + 2, INIT_BACKUP_DATA, CUEVA + 10))

    # 3. segmento R+X y alineación
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

    # 4. cueva sin referencias ni relocaciones
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
    vals = set(struct.unpack_from("<I", orig, i)[0] for i in range(0, len(orig) & ~3, 4))
    ptr = sorted(vals & set(range(CUEVA, CUEVA + CUEVA_LEN)))
    print("punteros : u32 del fichero iguales a una dirección de la cueva: %s" % (ptr or "NINGUNO"))
    if ptr:
        print("ERROR: alguien guarda un puntero a la cueva")
        return 13

    # 5. aplicar y comprobar el diff exacto
    buf = bytearray(orig)
    buf[GANCHO:GANCHO + 4] = bl_thumb(GANCHO, CUEVA)
    buf[CUEVA:CUEVA + CUEVA_LEN] = nuevo
    previstos = set(range(GANCHO, GANCHO + 4)) | set(range(CUEVA, CUEVA + CUEVA_LEN))
    if len(buf) != len(orig):
        print("ERROR: cambió el tamaño")
        return 14
    reales = {i for i in range(len(orig)) if orig[i] != buf[i]}
    if reales != previstos:
        print("ERROR: difieren bytes no previstos: %s" % sorted(reales ^ previstos))
        return 15
    print("diff     : %d bytes en 2 rangos (%08x..%08x, %08x..%08x), tamaño %d B sin cambios"
          % (len(reales), GANCHO, GANCHO + 3, CUEVA, CUEVA + CUEVA_LEN - 1, len(buf)))

    # 6. cabeceras, segmentos y secciones idénticos
    import io
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
    print("ELF      : cabecera, %d PT_* y %d secciones idénticas byte a byte"
          % (len(segs), len(secs)))

    # 7. desensamblado del resultado
    print("desasm   : cueva %08x" % CUEVA)
    for l in desasm(bytes(buf), CUEVA, CUEVA_LEN):
        print("   " + l)
    print("desasm   : gancho 0x7126DE..0x7126F0")
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
