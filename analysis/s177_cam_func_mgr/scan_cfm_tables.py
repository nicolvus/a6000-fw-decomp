#!/usr/bin/env python3
"""S177 — parsea las tablas de nombres de petición/respuesta del gestor de funciones.

Las tablas están en .data como arrays de 12 B: {u32 name_ptr, u32 id, u32 pad}.
Se localizan barriendo la imagen: toda palabra u32 alineada a 4 que apunte a una
cadena ASCII que empiece por 'REQ_' / 'REPLY_' y cuya entrada siguiente tenga
id pequeño y pad 0.

Salida: analysis/s177_cam_func_mgr/cfm_reqreply_tables.json
"""
import json
import os
import re
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
FILES = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
ENTRY = 12


def cstr(B, a):
    o = a - BASE
    if o < 0 or o >= len(B):
        return None
    e = B.find(b"\x00", o)
    if e < 0 or e - o > 120:
        return None
    try:
        s = B[o:e].decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if s and all(32 <= ord(c) < 127 for c in s) else None


def scan(B):
    """Devuelve las series contiguas de entradas {name_ptr,id,pad} con nombre REQ_/REPLY_."""
    names = {}
    for m in re.finditer(rb"(?:REQ_|REPLY_)[A-Z0-9_]{2,40}", B):
        s = m.group().decode("ascii")
        names.setdefault(m.start() + BASE, s)
    N = len(B)
    hits = []
    for a in range(BASE, BASE + N - 4, 4):
        p = struct.unpack_from("<I", B, a - BASE)[0]
        if p in names:
            hits.append(a)
    runs = []
    cur = []
    for a in hits:
        if cur and a - cur[-1] == ENTRY:
            cur.append(a)
        else:
            if len(cur) >= 3:
                runs.append(cur)
            cur = [a]
    if len(cur) >= 3:
        runs.append(cur)
    return runs, names


out = {}
for fw, path in FILES.items():
    B = open(os.path.join(ROOT, path), "rb").read()
    runs, names = scan(B)
    fwres = {}
    for r in runs:
        entries = []
        for a in r:
            name_ptr, idv, pad = struct.unpack_from("<III", B, a - BASE)
            entries.append({"slot": hex(a), "nombre": cstr(B, name_ptr),
                            "id": idv, "id_hex": hex(idv), "pad": pad})
        tag = entries[0]["nombre"].split("_")[0]
        key = tag
        if key in fwres:
            key = f"{tag}_{r[0]:x}"
        fwres[key] = {"tabla_base": hex(r[0]), "n": len(entries), "entradas": entries}
    out[fw] = fwres
    print(f"== {fw}")
    for tag, t in fwres.items():
        print(f"   {tag}: base={t['tabla_base']} n={t['n']}")
        for e in t["entradas"]:
            print(f"      {e['slot']}  id={e['id_hex']}  {e['nombre']}")

json.dump(out, open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_reqreply_tables.json"),
                    "w"), indent=1)
