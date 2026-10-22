#!/usr/bin/env python3
"""S134 — desensamblado reproducible de la aritmética de los parámetros del imager.

Extrae:
  * la función de validación `0x4381106c` (traces de error y volcado);
  * el acceso al singleton de estado `0x4378f9b4` y su global `0x43e99208`;
  * la rutina de división sin signo `0x4355faf0`.

Salida: analysis/s134_imager_params/disasm.json
"""
import json
import os
import struct

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

RANGOS = {
    "validador": (0x4381106C, 0x43811240),
    "accesor_estado": (0x4378F9B4, 0x4378F9BC),
    "udiv": (0x4355FAF0, 0x4355FB40),
}


def main():
    data = open(BIN, "rb").read()
    out = {}
    for nombre, (ini, fin) in RANGOS.items():
        lines = []
        for ins in MD.disasm(data[ini - BASE:fin - BASE], ini):
            lines.append(f"{ins.address:#x} {ins.mnemonic} {ins.op_str}")
        out[nombre] = lines
    # global del singleton
    w = struct.unpack_from("<I", data, 0x4378F9BC - BASE)[0]
    out["global_estado"] = f"0x{(w + 0x4378F9BA) & 0xffffffff:x}"
    dest = os.path.join(HERE, "disasm.json")
    json.dump(out, open(dest, "w"), indent=1)
    print("global del estado del imager:", out["global_estado"])
    for nombre in RANGOS:
        print(f"--- {nombre} ({len(out[nombre])} insns)")
    print("escrito", dest)


if __name__ == "__main__":
    main()
