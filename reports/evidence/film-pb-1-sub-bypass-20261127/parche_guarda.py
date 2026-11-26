#!/usr/bin/env python3
"""FILM-PB-1 · parche de AviMMgr::isSupportContent (libmpr.so 3.21, ELF VA == offset de fichero).

Dos variantes, ninguna toca el repo: escribe SIEMPRE una copia en /tmp y verifica que
(a) el conjunto de bytes distintos es exactamente el previsto,
(b) el resultado sigue siendo un ELF32 ARM ET_DYN coherente (cabeceras, phdrs, shdrs),
(c) la zona parcheada desensambla como se espera (capstone 5).

Uso:
  python3 parche_guarda.py --variante solo-tvsystem
  python3 parche_guarda.py --variante todo-1
  python3 parche_guarda.py --variante solo-tvsystem --out /tmp/x.so --lib /ruta/libmpr.so
"""
from __future__ import annotations

import argparse
import hashlib
import os
import struct
import sys

SHA_LIBMPR_321 = "9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30"
LIB_DEF = (
    "/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/firmware/extracted/fw321/"
    "firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so"
)
REPO = "/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter"

# --- VA (= offset de fichero en .text, verificado: .text addr == .text off == 0x120228) ---
VA_ENTRADA = 0x61A8F0           # AviMMgr::isSupportContent, vtable 0x8E6E58 + 0x58
VA_BNE_TV1 = 0x61AA04           # TvSystem==1 : tst (1<<f),#0x2A8 ; bne 0x61AA3A (Invalid)
VA_BNE_TV0 = 0x61AA30           # TvSystem!=1 : tst (1<<f),#0x154 ; bne 0x61AA3A (Invalid)
VA_LABEL_VALID = 0x61AA4A       # "isSupportContent : Valid TvSystem detected, frameRate %d"
VA_THUMB_FAIL = 0x61AA5C        # rama del fallo de GetPlayThumbnailInfo -> return 0

VARIANTES = {
    # 4 bytes: movs r0,#1 ; bx lr  -> salta toda la funcion (incluida la guarda de miniatura)
    "todo-1": [(VA_ENTRADA, bytes.fromhex("01207047"), "movs r0,#1 ; bx lr")],
    # 2 bytes: los dos bne de desajuste pasan a saltar a la etiqueta VALID (no a Invalid)
    "solo-tvsystem": [
        (VA_BNE_TV1, bytes.fromhex("21d1"), "bne 0x61AA4A (Valid) en vez de 0x61AA3A"),
        (VA_BNE_TV0, bytes.fromhex("0bd1"), "bne 0x61AA4A (Valid) en vez de 0x61AA3A"),
    ],
}

ESPERADO_ORIGINAL = {
    VA_ENTRADA: "84b02de9",
    VA_BNE_TV1: "19d1",
    VA_BNE_TV0: "03d1",
}


def elf_check(d: bytes) -> list[str]:
    """Devuelve la lista de problemas de coherencia ELF (vacia = valido)."""
    err = []
    if d[:4] != b"\x7fELF":
        return ["magic != \\x7fELF"]
    if d[4] != 1:
        err.append("EI_CLASS != ELFCLASS32")
    if d[5] != 1:
        err.append("EI_DATA != little endian")
    e_type, e_machine = struct.unpack_from("<HH", d, 16)
    if e_type != 3:
        err.append("e_type=%d (se esperaba 3 = ET_DYN)" % e_type)
    if e_machine != 40:
        err.append("e_machine=%d (se esperaba 40 = EM_ARM)" % e_machine)
    e_phoff, e_shoff = struct.unpack_from("<II", d, 28)[0], struct.unpack_from("<I", d, 32)[0]
    e_phentsize, e_phnum = struct.unpack_from("<HH", d, 42)
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", d, 46)
    if e_phnum == 0 or e_phoff + e_phnum * e_phentsize > len(d):
        err.append("tabla de program headers fuera de fichero")
    if e_shnum == 0 or e_shoff + e_shnum * e_shentsize > len(d):
        err.append("tabla de section headers fuera de fichero")
    if e_shstrndx >= e_shnum:
        err.append("e_shstrndx fuera de rango")
    # .text presente y no vacio
    if not err:
        shstr = e_shoff + e_shstrndx * e_shentsize
        strtab_off = struct.unpack_from("<I", d, shstr + 16)[0]
        tiene_text = False
        for i in range(e_shnum):
            o = e_shoff + i * e_shentsize
            nm_off = struct.unpack_from("<I", d, o)[0]
            fin = d.index(b"\0", strtab_off + nm_off)
            if d[strtab_off + nm_off:fin] == b".text":
                tiene_text = struct.unpack_from("<I", d, o + 20)[0] > 0
        if not tiene_text:
            err.append("sin seccion .text")
    return err


def desasm(d: bytes, va: int, n: int) -> list[str]:
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    return ["%08x: %-10s %s" % (i.address, i.mnemonic, i.op_str)
            for i in md.disasm(d[va:va + n], va)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lib", default=LIB_DEF)
    ap.add_argument("--variante", default="solo-tvsystem", choices=sorted(VARIANTES))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    out = a.out or "/tmp/libmpr-parche-%s.so" % a.variante
    if os.path.abspath(out).startswith(REPO + os.sep):
        print("ERROR: la salida no puede estar dentro del repo (%s)" % out)
        return 2
    orig = open(a.lib, "rb").read()
    sha = hashlib.sha256(orig).hexdigest()
    print("entrada : %s" % a.lib)
    print("sha256  : %s%s" % (sha, "" if sha == SHA_LIBMPR_321 else "  (AVISO: no es el 3.21 esperado)"))
    print("variante: %s" % a.variante)

    # 1. bytes originales esperados
    for va, hexs in ESPERADO_ORIGINAL.items():
        got = orig[va:va + len(hexs) // 2].hex()
        if got != hexs:
            print("ERROR: en %08x esperaba %s y hay %s" % (va, hexs, got))
            return 3

    parches = VARIANTES[a.variante]
    buf = bytearray(orig)
    previstos = {}
    for va, nuevo, desc in parches:
        viejo = bytes(buf[va:va + len(nuevo)])
        for i, (b0, b1) in enumerate(zip(viejo, nuevo)):
            if b0 != b1:
                previstos[va + i] = (b0, b1)
        buf[va:va + len(nuevo)] = nuevo
        print("  %08x  %-20s -> %-20s  %s" % (va, viejo.hex(" "), nuevo.hex(" "), desc))

    # 2. diferencias reales
    reales = {i: (orig[i], buf[i]) for i in range(len(orig)) if orig[i] != buf[i]}
    if set(reales) != set(previstos):
        print("ERROR: difieren bytes no previstos: %s" % sorted(set(reales) ^ set(previstos)))
        return 4
    print("bytes distintos: %d  ->  %s" % (
        len(reales), " ".join("%08x:%02x>%02x" % (i, a0, b1) for i, (a0, b1) in sorted(reales.items()))))
    if len(orig) != len(buf):
        print("ERROR: cambio el tamano")
        return 5

    # 3. ELF resultante
    err = elf_check(bytes(buf))
    if err:
        print("ERROR: ELF invalido -> %s" % err)
        return 6
    print("ELF     : valido (ELF32 LE, ET_DYN, EM_ARM, %d phdrs, %d shdrs)"
          % (struct.unpack_from("<H", buf, 44)[0], struct.unpack_from("<H", buf, 48)[0]))

    # 4. desensamblado de la zona tocada
    print("desasm 0x%08x (entrada):" % VA_ENTRADA)
    for l in desasm(bytes(buf), VA_ENTRADA, 8):
        print("   " + l)
    print("desasm 0x%08x (comparacion de TvSystem):" % (0x61A9EE))
    for l in desasm(bytes(buf), 0x61A9EE, 0x48):
        print("   " + l)

    open(out, "wb").write(buf)
    print("salida  : %s  sha256=%s" % (out, hashlib.sha256(bytes(buf)).hexdigest()))
    print("Nada aplicado en el repo: la libreria de fabrica sigue intacta "
          "(sha256 %s)." % hashlib.sha256(open(a.lib, "rb").read()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
