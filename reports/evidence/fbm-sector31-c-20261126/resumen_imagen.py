#!/usr/bin/env python3
"""Resumen medible de la imagen nflasha4 escrita por el arranque con el parche C.

    python3 resumen_imagen.py runC1/nflash4.img [runC2/nflash4.img ...]

Imprime: sha256, bytes distintos frente al volcado de origen (agrupados en páginas de 1 KiB),
las entradas de fileType de cada página de control cambiada, el sha256 de la página de datos base
0x380000 y la comparación con la página de control que dejó la vía de consola
(`reports/evidence/fbm-initb-6-3-nflasha4-20261126/run3/ctrl_page_9d400.bin`).
"""
from __future__ import annotations

import hashlib
import struct
import sys

ORIGEN = "analysis/camera-dumps/nand-20261020/dev_nflasha4.bin"
PAGINA_CONSOLA = "reports/evidence/fbm-initb-6-3-nflasha4-20261126/run3/ctrl_page_9d400.bin"


def entradas_control(pag: bytes) -> list[str]:
    out = []
    for k in range(18):
        off = 8 + 8 * k
        ft = struct.unpack_from("<I", pag, off)[0]
        if ft in (0, 0xFFFFFFFF):
            continue
        out.append("fileType %#04x status=%d bloquesBase=%d bloquesMax=%d cola=%#04x"
                   % (ft, pag[off + 4], pag[off + 5], pag[off + 6], pag[off + 7]))
    return out


def main() -> int:
    orig = open(ORIGEN, "rb").read()
    print("origen  : %s  sha256 %s  (%d B)" % (ORIGEN, hashlib.sha256(orig).hexdigest(), len(orig)))
    ref = open(PAGINA_CONSOLA, "rb").read()
    for ruta in sys.argv[1:]:
        img = open(ruta, "rb").read()
        print("\n== %s" % ruta)
        print("   sha256 %s  (%d B)" % (hashlib.sha256(img).hexdigest(), len(img)))
        paginas = set()
        total = 0
        for i in range(min(len(orig), len(img))):
            if orig[i] != img[i]:
                total += 1
                paginas.add(i & ~0x3FF)
        print("   bytes distintos frente al origen: %d en %d página(s) de 1 KiB" % (total, len(paginas)))
        for p in sorted(paginas):
            pag = img[p:p + 0x400]
            print("   %#08x..%#08x sha256 %s" % (p, p + 0x3FF, hashlib.sha256(pag).hexdigest()))
            if p == 0x380000:
                print("      página de datos base: primeros 32 B %s" % pag[:32].hex(" "))
                continue
            print("      seq=%d cks=%#010x" % (struct.unpack_from("<I", pag, 0x3F8)[0],
                                               struct.unpack_from("<I", pag, 0x3FC)[0]))
            for ln in entradas_control(pag):
                print("      " + ln)
        pag = img[0x9D400:0x9D400 + 0x400]
        print("   página de control 0x9D400 == la de la vía de consola (run3): %s" % (pag == ref))
    return 0


if __name__ == "__main__":
    sys.exit(main())
