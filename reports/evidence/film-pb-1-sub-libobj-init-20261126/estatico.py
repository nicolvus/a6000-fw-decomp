"""Volcado estático de la comparación libObj.so 3.21 de fábrica vs. parcheado del CFW 3.93.

Sin cámara y sin ejecutar nada: cabecera, phdrs, secciones, `.init_array`, rangos de bytes
distintos, `.dynamic` y contenido de los segmentos añadidos.

Uso: python3 estatico.py > estatico.txt
"""
from __future__ import annotations

import struct
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
ORIG = (RAIZ / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
        "nflasha15_unpacked_unpacked/lib/libObj.so")
PATCH = RAIZ / "build/cfw_func393/pp/files/lib/libObj.so"


def secciones(d: bytes) -> dict[str, tuple[int, int, int]]:
    shoff = struct.unpack_from("<I", d, 0x20)[0]
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", d, 0x2E)
    crudas = [struct.unpack_from("<10I", d, shoff + i * shentsize) for i in range(shnum)]
    nombres = d[crudas[shstrndx][4]:]
    return {nombres[s[0]:nombres.index(b"\0", s[0])].decode(): (s[3], s[4], s[5]) for s in crudas}


def main() -> None:
    do = ORIG.read_bytes()
    dp = PATCH.read_bytes()
    print("# libObj.so 3.21 de fábrica  %s  %d B" % (ORIG.relative_to(RAIZ), len(do)))
    print("# libObj.so parcheado (CFW) %s  %d B" % (PATCH.relative_to(RAIZ), len(dp)))
    print()
    for etiqueta, d in (("fábrica", do), ("parcheado", dp)):
        phoff = struct.unpack_from("<I", d, 0x1C)[0]
        phnum = struct.unpack_from("<H", d, 0x2C)[0]
        print("## phdrs (%s): %d" % (etiqueta, phnum))
        for i in range(phnum):
            t, off, va, _pa, fsz, msz, fl, al = struct.unpack_from("<8I", d, phoff + i * 32)
            print("  [%d] type=%#010x off=%#09x va=%#09x fsz=%#08x msz=%#08x fl=%d al=%d"
                  % (i, t, off, va, fsz, msz, fl, al))
        print()
    for etiqueta, d in (("fábrica", do), ("parcheado", dp)):
        print("## .dynamic (%s)" % etiqueta)
        _va, off, size = secciones(d)[".dynamic"]
        i = 0
        while i < size:
            tag, val = struct.unpack_from("<iI", d, off + i)
            if tag == 0:
                break
            if tag in (12, 13, 17, 18, 23, 25, 26, 27, 28):
                print("  tag %-3d = %#x" % (tag, val))
            i += 8
        print()
    so, sp = secciones(do), secciones(dp)
    print("## secciones comparadas")
    for n in (".dynsym", ".dynstr", ".gnu.hash", ".rel.dyn", ".rel.plt", ".init", ".fini",
              ".init_array", ".fini_array", ".data.rel.ro", ".got", ".data"):
        a, b = so[n], sp[n]
        x = do[a[1]:a[1] + a[2]]
        y = dp[b[1]:b[1] + b[2]]
        print("  %-13s va=%#09x tamaño=%#x/%#x igual=%s" % (n, a[0], a[2], b[2], x == y))
    print()
    ia_va, ia_off, ia_sz = so[".init_array"]
    a = do[ia_off:ia_off + ia_sz]
    b = dp[sp[".init_array"][1]:sp[".init_array"][1] + ia_sz]
    print("## .init_array: va=%#x tamaño=%#x (%d entradas)  idéntico=%s"
          % (ia_va, ia_sz, ia_sz // 4, a == b))
    print("  entradas:", ", ".join("%#x" % v for v in struct.unpack("<%dI" % (ia_sz // 4), a)))
    print()
    print("## rangos de bytes distintos en el prefijo común")
    n = min(len(do), len(dp))
    i, total, rangos = 0, 0, []
    while i < n:
        if do[i] != dp[i]:
            j = i
            while j < n and do[j] != dp[j]:
                j += 1
            rangos.append((i, j))
            total += j - i
            i = j
        else:
            i += 1
    exp = {va: off for va, off, fsz in
           [(s[0], s[1], s[2]) for s in so.values()] for _ in (0,)}
    for a0, b0 in rangos:
        va = None
        for seccion, (sva, soff, ssz) in so.items():
            if soff <= a0 < soff + ssz:
                va = sva + (a0 - soff)
                nombre = seccion
                break
        print("  %#09x..%#09x (%d B)  va=%#09x  %s" % (a0, b0 - 1, b0 - a0, va or 0,
                                                       nombre if va else "?"))
    print("  total: %d rangos, %d B ; cola añadida: %d B" % (len(rangos), total, len(dp) - len(do)))
    print("  (mapa esperado: %d secciones)" % len(exp))
    print()
    print("## contenido de los segmentos añadidos")
    for va, off, fsz in ((0x00FCB000, 0x01149000, 0xA70), (0x010E8000, 0x010A8000, 0xA0380)):
        seg = dp[off:off + fsz]
        i = seg.find(struct.pack("<I", 0x6474E551))
        print("  va=%#x  %d B  primeros 16 B: %s  PT_GNU_STACK (copia de phdrs) en +%#x"
              % (va, fsz, seg[:16].hex(" "), i))
    rel = do[so[".rel.dyn"][1]:so[".rel.dyn"][1] + so[".rel.dyn"][2]]
    print("  copia de .rel.dyn en 0x010E8000: idéntica=%s (%d entradas)"
          % (rel == dp[0x010A8000:0x010A8000 + len(rel)], len(rel) // 8))


if __name__ == "__main__":
    main()
