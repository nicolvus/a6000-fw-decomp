#!/usr/bin/env python3
"""Reconstruye en el host la imagen de /dev/nflasha4 tal como quedó dentro del invitado.

El shim copia /usr/share/nflasha4.img a /nflasha4.img *dentro* del invitado, así que la copia
modificada no se puede sacar del QEMU. nf6inject.so imprime los tramos distintos
(`[NF6] DIFF <off> <len>` + `[NF6] DIFFB <off> <hex>`) y este script los aplica sobre el volcado
del repo para obtener la imagen equivalente.

uso: python3 patch_desde_log.py CONSOLA.LOG SALIDA.bin
"""
import hashlib
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
ORIG = REPO / "analysis/camera-dumps/nand-20261020/dev_nflasha4.bin"
SHA = "a5ab15ca743950d6a8c64c17a8ed024cddc6d5c94a24a08cf60ca5d4e9ac7247"

log = pathlib.Path(sys.argv[1]).read_text(errors="replace")
dst = pathlib.Path(sys.argv[2])

origen = ORIG.read_bytes()
img = bytearray(origen)
assert hashlib.sha256(img).hexdigest() == SHA, "el volcado de origen no es el esperado"

# [NF6] DIFF 0x9d400 15   -> tramo pendiente; [NF6] DIFFB 0x9d400 <hex> -> contenido nuevo
tramos, actual = [], None
for ln in log.splitlines():
    m = re.search(r"\[NF6\] DIFF ([0-9a-fx]+) (\d+)", ln)
    if m:
        off, ln_ = int(m.group(1), 0), int(m.group(2))
        actual = {"off": off, "len": ln_, "bytes": bytearray()}
        tramos.append(actual)
        continue
    m = re.search(r"\[NF6\] DIFFB ([0-9a-fx]+) ([0-9a-f]+)", ln)
    if m and actual is not None:
        o = int(m.group(1), 0)
        b = bytes.fromhex(m.group(2))
        assert o == actual["off"] + len(actual["bytes"]), (hex(o), hex(actual["off"]), len(actual["bytes"]))
        actual["bytes"] += b

total = 0
for t in tramos:
    assert len(t["bytes"]) == t["len"], (hex(t["off"]), len(t["bytes"]), t["len"])
    img[t["off"]:t["off"] + t["len"]] = t["bytes"]
    total += t["len"]
dst.write_bytes(img)
cambios = sum(1 for x, y in zip(img, origen) if x != y)
print(f"{len(tramos)} tramos, {total} B aplicados -> {dst}  sha256={hashlib.sha256(img).hexdigest()}")
print(f"bytes distintos respecto del volcado: {cambios}")
