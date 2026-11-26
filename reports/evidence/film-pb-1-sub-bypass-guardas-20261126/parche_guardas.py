#!/usr/bin/env python3
"""FILM-PB-1 · parche de las DOS guardas del manejador FUN_00437BC0 (libmpr.so 3.21).

Anula las dos llamadas del manejador PlayMovie (0x437BC0) sustituyendo cada `bl` (4 B) por
`movs r0,#1 ; nop` (2+2 B), de modo que el `cbnz r0` posterior siga tomando el camino bueno.

  A) 0x437BFA  0f f0 10 ff  (bl 0x447A1E)  ->  01 20 00 bf  (movs r0,#1 ; nop)
  B) 0x437C2C  10 f0 7b f9  (bl 0x447F26)  ->  01 20 00 bf  (movs r0,#1 ; nop)

No toca el original: lee la libreria de fabrica (solo lectura) y escribe la copia en
`build/cfw_bypass_guardas/libmpr.so`. Comprueba:
  1. sha256 del original, 4 bytes originales en cada sitio y los dos `cbnz` (0x437BFE, 0x437C30),
  2. que los dos sitios caen en `.text` y en un PT_LOAD ejecutable, alineados a 2 (Thumb),
  3. que el conjunto de bytes distintos es EXACTAMENTE el previsto (8 B) y el tamano no cambia,
  4. que cabecera, tabla de segmentos y tabla de secciones quedan byte a byte iguales,
  5. que NO hay ninguna relocacion (.rel*/SHT_REL/SHT_RELA) con r_offset en las direcciones tocadas,
  6. desensambla el resultado (capstone 5).
Uso: python3 parche_guardas.py [--out build/cfw_bypass_guardas/libmpr.so]
"""
from __future__ import annotations

import argparse
import hashlib
import os
import struct
import sys

ROOT = "/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter"
LIB_ORIG = os.path.join(
    ROOT,
    "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
    "nflasha15_unpacked_unpacked/lib/libmpr.so",
)
SHA_ORIG = "9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30"

PARCHES = [
    (0x437BFA, bytes.fromhex("0ff010ff"), bytes.fromhex("012000bf"), "bl 0x447A1E -> movs r0,#1 ; nop"),
    (0x437C2C, bytes.fromhex("10f07bf9"), bytes.fromhex("012000bf"), "bl 0x447F26 -> movs r0,#1 ; nop"),
]
SALTOS_INTACTOS = [(0x437BFE, "38b9", "cbnz r0, #0x437C10"), (0x437C30, "f0b9", "cbnz r0, #0x437C70")]

SHT_REL, SHT_RELA = 9, 4


def u32(d: bytes, off: int) -> int:
    return struct.unpack_from("<I", d, off)[0]


def ehdr(d: bytes) -> dict:
    return {
        "phoff": u32(d, 28), "shoff": u32(d, 32),
        "phentsize": struct.unpack_from("<H", d, 42)[0], "phnum": struct.unpack_from("<H", d, 44)[0],
        "shentsize": struct.unpack_from("<H", d, 46)[0], "shnum": struct.unpack_from("<H", d, 48)[0],
        "shstrndx": struct.unpack_from("<H", d, 50)[0],
    }


def secciones(d: bytes) -> list[dict]:
    h = ehdr(d)
    out = []
    for i in range(h["shnum"]):
        o = h["shoff"] + i * h["shentsize"]
        name, typ, flags, addr, off, size, link, info, align, entsize = struct.unpack_from("<10I", d, o)
        out.append(dict(name_off=name, type=typ, flags=flags, addr=addr, off=off, size=size,
                        link=link, info=info, entsize=entsize, idx=i))
    st = out[h["shstrndx"]]
    for s in out:
        a = st["off"] + s["name_off"]
        s["name"] = d[a:d.index(b"\0", a)].decode("latin1")
    return out


def segmentos(d: bytes) -> list[dict]:
    h = ehdr(d)
    out = []
    for i in range(h["phnum"]):
        o = h["phoff"] + i * h["phentsize"]
        p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack_from("<8I", d, o)
        out.append(dict(type=p_type, off=p_offset, vaddr=p_vaddr, filesz=p_filesz, flags=p_flags, raw=d[o:o + h["phentsize"]]))
    return out


def reloc_a(d: bytes, va: int) -> list[str]:
    """Todas las entradas de .rel/.rela cuyo r_offset sea `va` (o caiga dentro de 4 B)."""
    hits = []
    for s in secciones(d):
        if s["type"] not in (SHT_REL, SHT_RELA) or not s["size"]:
            continue
        n = s["size"] // s["entsize"]
        for k in range(n):
            o = s["off"] + k * s["entsize"]
            r_off, r_info = struct.unpack_from("<II", d, o)
            addend = u32(d, o + 8) if s["type"] == SHT_RELA and s["entsize"] >= 12 else None
            if va - 3 <= r_off <= va:
                hits.append("%s[%d] r_offset=%08x type=%d sym=%d addend=%s"
                            % (s["name"], k, r_off, r_info & 0xFF, r_info >> 8, addend))
    return hits


def desasm(d: bytes, va: int, n: int) -> list[str]:
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    return ["%08x: %-10s %-8s %s" % (i.address, i.bytes.hex(), i.mnemonic, i.op_str)
            for i in md.disasm(d[va:va + n], va)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lib", default=LIB_ORIG)
    ap.add_argument("--out", default=os.path.join(ROOT, "build/cfw_bypass_guardas/libmpr.so"))
    a = ap.parse_args()

    orig = open(a.lib, "rb").read()
    sha = hashlib.sha256(orig).hexdigest()
    print("original : %s" % a.lib)
    print("sha256   : %s%s" % (sha, "" if sha == SHA_ORIG else "   (AVISO: no es el 3.21 esperado)"))
    if sha != SHA_ORIG:
        print("ERROR: sha256 distinto del de fabrica")
        return 2

    # 1. bytes originales y saltos intactos
    for va, viejo, nuevo, desc in PARCHES:
        got = orig[va:va + 4]
        if got != viejo:
            print("ERROR: en %08x esperaba %s y hay %s" % (va, viejo.hex(), got.hex()))
            return 3
        print("  %08x  %s -> %s   %s" % (va, viejo.hex(" "), nuevo.hex(" "), desc))
    for va, hexs, desc in SALTOS_INTACTOS:
        got = orig[va:va + 2].hex()
        if got != hexs:
            print("ERROR: el salto %08x no es %s sino %s" % (va, hexs, got))
            return 4
        print("  %08x  %s    %s  (no se toca)" % (va, hexs, desc))

    # 2. dentro de .text y de un PT_LOAD ejecutable, alineado a 4
    secs = secciones(orig)
    text = [s for s in secs if s["name"] == ".text"][0]
    segs = segmentos(orig)
    for va, *_ in PARCHES:
        if not (text["addr"] <= va < text["addr"] + text["size"]):
            print("ERROR: %08x fuera de .text" % va)
            return 5
        if va % 2:   # Thumb-2: las instrucciones de 32 bits solo exigen alineacion a semipalabra
            print("ERROR: %08x no esta alineado a 2" % va)
            return 6
        x = [p for p in segs if p["type"] == 1 and p["vaddr"] <= va < p["vaddr"] + p["filesz"]]
        if not x or not (x[0]["flags"] & 0x1):
            print("ERROR: %08x no cae en un PT_LOAD ejecutable" % va)
            return 7
    print(".text    : VA %08x..%08x  fichero %08x..%08x"
          % (text["addr"], text["addr"] + text["size"], text["off"], text["off"] + text["size"]))
    print("offset   : .text addr==off? %s (los parches van a offset = VA)" % (text["addr"] == text["off"]))

    # 3. aplicar y comprobar el diff exacto
    buf = bytearray(orig)
    previstos = set()
    for va, viejo, nuevo, _ in PARCHES:
        previstos |= set(range(va, va + 4))
        buf[va:va + 4] = nuevo
    if len(buf) != len(orig):
        print("ERROR: cambio el tamano")
        return 8
    reales = {i for i in range(len(orig)) if orig[i] != buf[i]}
    if reales != previstos:
        print("ERROR: difieren bytes no previstos: %s" % sorted(reales ^ previstos))
        return 9
    print("diff     : %d bytes en %d rangos -> %s"
          % (len(reales), len(PARCHES), ", ".join("%08x..%08x" % (va, va + 3) for va, *_ in PARCHES)))

    # 4. cabeceras, segmentos y secciones identicos
    ho, hn = ehdr(orig), ehdr(buf)
    if ho != hn:
        print("ERROR: cambio la cabecera ELF (%s != %s)" % (ho, hn))
        return 10
    if orig[:ho["phoff"] + ho["phnum"] * ho["phentsize"]] != bytes(buf[:ho["phoff"] + ho["phnum"] * ho["phentsize"]]):
        print("ERROR: cambio la tabla de segmentos (PT_*)")
        return 11
    so = {s["name"]: s for s in secs}
    sn = {s["name"]: s for s in secciones(bytes(buf))}
    if so != sn:
        print("ERROR: cambio la tabla de secciones")
        return 12
    for s in secciones(bytes(buf)):
        if s["type"] != 8 and s["name"] not in (".text", ".rel.dyn", ".rel.plt"):
            if orig[s["off"]:s["off"] + s["size"]] != bytes(buf[s["off"]:s["off"] + s["size"]]):
                print("AVISO: cambio el contenido de %s" % s["name"])
    print("ELF      : cabecera, %d PT_* y %d secciones identicas byte a byte"
          % (ho["phnum"], ho["shnum"]))

    # 5. relocaciones sobre las direcciones parcheadas
    for va, *_ in PARCHES:
        h = reloc_a(orig, va)
        print("reloc    : %08x -> %s" % (va, "NINGUNA" if not h else h))
        if h:
            print("ERROR: hay relocaciones sobre %08x; el parche no valdria" % va)
            return 13
    n_rel = sum(s["size"] // s["entsize"] for s in secs if s["type"] in (SHT_REL, SHT_RELA) and s["size"])
    print("reloc    : %d entradas revisadas en .rel* (ninguna apunta a los dos sitios)" % n_rel)

    # 6. desensamblado del resultado
    print("desasm   : 0x437BF0..0x437C38")
    for l in desasm(bytes(buf), 0x437BF0, 0x48):
        print("   " + l)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    if os.path.abspath(a.out).startswith(os.path.join(ROOT, "firmware") + os.sep):
        print("ERROR: la salida no puede estar dentro de firmware/")
        return 14
    open(a.out, "wb").write(buf)
    print("salida   : %s" % a.out)
    print("sha256   : %s" % hashlib.sha256(bytes(buf)).hexdigest())
    print("original intacto: %s" % hashlib.sha256(open(a.lib, "rb").read()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
