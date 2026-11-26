#!/usr/bin/env python3
"""Reconstruye las imágenes de trabajo de esta prueba a partir del volcado del repo.

  python3 make_page.py            -> deja en /tmp las dos copias (no en reports/: son 10 MiB cada una)
      /tmp/nflasha4-origen.bin          copia exacta del volcado
      /tmp/nflasha4-con-sector-31.bin   copia + página de control 0x9D400 creada por CreateSector32(0x31)
                                        (la de run3/ctrl_page_9d400.bin, seq 0x2C2)

El volcado de origen NO se toca nunca: sha256
  a5ab15ca743950d6a8c64c17a8ed024cddc6d5c94a24a08cf60ca5d4e9ac7247  analysis/camera-dumps/nand-20261020/dev_nflasha4.bin
"""
import hashlib
import pathlib
import shutil

REPO = pathlib.Path(__file__).resolve().parents[3]
ORIG = REPO / "analysis/camera-dumps/nand-20261020/dev_nflasha4.bin"
PAGE = pathlib.Path(__file__).resolve().parent.parent / "fbm-initb-6-3-nflasha4-20261126/run3/ctrl_page_9d400.bin"
SHA = "a5ab15ca743950d6a8c64c17a8ed024cddc6d5c94a24a08cf60ca5d4e9ac7247"

dst = pathlib.Path("/tmp/nflasha4-origen.bin")
shutil.copyfile(ORIG, dst)
h = hashlib.sha256(dst.read_bytes()).hexdigest()
print("origen:", dst, h, "OK" if h == SHA else "¡NO COINCIDE CON EL SHA256 ESPERADO!")

img = bytearray(dst.read_bytes())
pg = PAGE.read_bytes()
assert len(pg) == 0x400 and img[0x9D400:0x9D800] == b"\xff" * 0x400
img[0x9D400:0x9D800] = pg
out = pathlib.Path("/tmp/nflasha4-con-sector-31.bin")
out.write_bytes(img)
print("con sector 0x31:", out, hashlib.sha256(img).hexdigest())
