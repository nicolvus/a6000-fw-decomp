#!/usr/bin/env python3
"""S123 — registro de clases del firmware: `CC::`, `LC::`, `TC::`, `FC::`, `IM::`, `EC::`.

En `0x43FF8EE4` hay una tabla de punteros a **nombres de clase** (`CC::CcEncryptedTagData`,
`LC::LcEncryptedTagData`, ...) y, a continuación, los punteros a los **typeinfo** (nombres
mangled Itanium) de `Camera::Imaging::ImageParam`, `Camera::Capture::ImageParam_Capture*`.

Es la prueba de que el prefijo de log `[CAMERA_MAIN_CC]` corresponde a una clase C++ llamada
`CC`, en la misma familia que `LC` (`[CAMERA_MAIN_LC]`), `TC` (`[CAMERA_MAIN_TC]`),
`FC` (`[CAMERA_MAIN_FC]`) e `IM` (`[CAMERA_MAIN_IM]`).

Uso:  class_registry.py
"""
import json
import os
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = 0x43FF8EE4
NAMES = 14          # entradas de nombre antes de los typeinfo


def cstr(data, vaddr, maxlen=120):
    off = vaddr - BASE
    if off < 0 or off >= len(data):
        return None
    e = off
    while e < len(data) and e < off + maxlen and 32 <= data[e] < 127:
        e += 1
    return data[off:e].decode("latin1") if e > off else None


def main():
    data = open(BIN, "rb").read()
    names, typeinfos = [], []
    for i in range(NAMES):
        p = struct.unpack_from("<I", data, TABLE - BASE + 4 * i)[0]
        c = cstr(data, p)
        if c:
            names.append({"slot": f"0x{TABLE + 4 * i:x}", "ptr": f"0x{p:x}", "name": c})
    base = TABLE + 4 * NAMES
    for i in range(12):
        a = base + 4 * i
        p = struct.unpack_from("<I", data, a - BASE)[0]
        c = cstr(data, p)
        if c and (c.startswith("N") or c.startswith("N6")):
            typeinfos.append({"slot": f"0x{a:x}", "ptr": f"0x{p:x}", "typeinfo": c})
    out = {"table": f"0x{TABLE:x}", "class_names": names, "typeinfos": typeinfos}
    json.dump(out, open(os.path.join(HERE, "class_registry.json"), "w"),
              indent=1, ensure_ascii=False)
    print(f"tabla de clases en {hex(TABLE)}:")
    for n in names:
        print(f"  {n['slot']} -> {n['ptr']}  {n['name']}")
    print("typeinfo:")
    for t in typeinfos:
        print(f"  {t['slot']} -> {t['ptr']}  {t['typeinfo']}")


if __name__ == "__main__":
    main()
