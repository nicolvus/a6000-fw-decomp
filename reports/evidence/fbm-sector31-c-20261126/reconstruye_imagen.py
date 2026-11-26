#!/usr/bin/env python3
"""Reconstruye (en /tmp, no en el repo) la imagen de nflasha4 que escribió el arranque C1 a partir
del volcado de origen y de las tres páginas de 1 KiB que sí se versionan.

    python3 reconstruye_imagen.py [/tmp/nflasha4-C1.img]

Debe dar sha256 6d2ab43aa2fe386dc4c4df0e3ed3c8633328f74d24112ef2e87770b57a5dca51 (1 300 B distintos).
Es la imagen que se usó como entrada de runC2 (fábrica) y runC3 (parche con el sector ya presente).
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../.."))
ORIGEN = os.path.join(REPO, "analysis/camera-dumps/nand-20261020/dev_nflasha4.bin")
PAGINAS = [(0x9D400, "pagina-9D400.bin"), (0xBD400, "pagina-BD400.bin"), (0x380000, "pagina-380000.bin")]
ESPERADO = "6d2ab43aa2fe386dc4c4df0e3ed3c8633328f74d24112ef2e87770b57a5dca51"


def main() -> int:
    dst = sys.argv[1] if len(sys.argv) > 1 else "/tmp/nflasha4-tras-C1.img"
    buf = bytearray(open(ORIGEN, "rb").read())
    for off, nom in PAGINAS:
        pag = open(os.path.join(HERE, nom), "rb").read()
        assert len(pag) == 0x400, nom
        buf[off:off + 0x400] = pag
    sh = hashlib.sha256(bytes(buf)).hexdigest()
    open(dst, "wb").write(bytes(buf))
    print("origen : %s (%d B) sha256 %s" % (ORIGEN, len(buf), hashlib.sha256(open(ORIGEN, "rb").read()).hexdigest()))
    print("escrito: %s" % dst)
    print("sha256 : %s   %s" % (sh, "== el de runC1" if sh == ESPERADO else "¡DISTINTO del de runC1 (%s)!" % ESPERADO))
    return 0 if sh == ESPERADO else 1


if __name__ == "__main__":
    sys.exit(main())
