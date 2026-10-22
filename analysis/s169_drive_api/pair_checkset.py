#!/usr/bin/env python3
"""S169 — empareja las etiquetas `CheckSet*` del A6300 con su mensaje de traza.

El despachador de LiroSeq tiene el patrón:

    ldr r0, [pc,#a]      ; r0 = mensaje  ("LiroSeq ParamCheckErr@%s[campo] cur:%d req:%d")
    ldr r1, [pc,#b]      ; r1 = etiqueta ("CheckSetShutDrive")
    add r0, pc           ; sitio +0  -> mensaje
    add r1, pc           ; sitio +2  -> etiqueta
    bl  0x43986518

Como el mapa de referencias PIC da el sitio de cada `add`, basta con emparejar el sitio del
mensaje con el sitio +2 (la etiqueta).

Uso: pair_checkset.py <mapa_pic.json> <blob> <base>
"""
import json
import sys

mapa_path, blob, base = sys.argv[1], sys.argv[2], int(sys.argv[3], 16)
mapa = json.load(open(mapa_path))
B = open(blob, "rb").read()


def cstr(va):
    o = va - base
    if o < 0 or o >= len(B):
        return ""
    e = B.find(b"\x00", o)
    return B[o:e].decode("latin1")


sitio_de = {}
for dest, sites in mapa.items():
    for s in sites:
        sitio_de[s] = int(dest, 16)

filas = []
for s, dest in sitio_de.items():
    msg = cstr(dest)
    if "ParamCheckErr" not in msg:
        continue
    name = cstr(sitio_de.get(s + 2, 0))
    if not name.startswith("CheckSet"):
        continue
    campo = ""
    i = msg.find("[")
    j = msg.find("]", i)
    if i >= 0 and j > i:
        campo = msg[i + 1:j]
    filas.append({"propiedad": name, "campo": campo, "mensaje": msg,
                  "sitio_add_mensaje": f"{s:08x}", "sitio_add_etiqueta": f"{s+2:08x}"})

filas.sort(key=lambda r: r["propiedad"])
print(json.dumps({"n": len(filas), "pares": filas}, indent=1, ensure_ascii=False))
