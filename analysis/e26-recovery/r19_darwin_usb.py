"""E26-R19 — auditoría estática de la capa USB de darwin_core.bin (Cortex-M, base 0).

Uso: python3 r19_darwin_usb.py [ruta_darwin_core.bin]. Solo lectura; Capstone solo para listar BL.
"""

import struct
import sys
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_MCLASS, CS_MODE_THUMB, Cs

DEFAULT = (
    Path(__file__).resolve().parents[2]
    / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
)
CODE_END = 0x21000  # el resto son tablas y cadenas (DWN en 0x21938)


def literal_refs(d, lo, hi):
    """Instrucciones `ldr r,[pc,#imm]` (T1 y .w) cuyo literal es una dirección de periférico."""
    out = defaultdict(list)
    for o in range(lo, hi, 2):
        h = struct.unpack_from("<H", d, o)[0]
        a = None
        if h >> 11 == 9:
            a = ((o + 4) & ~3) + (h & 0xFF) * 4
        elif h in (0xF8DF, 0xF85F):
            imm = struct.unpack_from("<H", d, o + 2)[0] & 0xFFF
            a = ((o + 4) & ~3) + (imm if h == 0xF8DF else -imm)
        if a and a + 4 <= len(d):
            w = struct.unpack_from("<I", d, a)[0]
            if 0x40000000 <= w < 0x60000000 or 0xE0000000 <= w < 0xE0100000:
                out[w].append(o)
    return out


def callers(d, end=CODE_END):
    """Mapa destino -> direcciones de `bl`/`b.w` (desensamblado resincronizando tras datos)."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    calls, o = defaultdict(list), 0
    while o < end:
        for i in md.disasm(d[o : o + 4], o):
            if i.mnemonic in ("bl", "b.w") and i.op_str.startswith("#"):
                calls[int(i.op_str[1:], 16)].append(i.address)
            o += i.size
            break
        else:
            o += 2
    return calls


def main(path):
    d = Path(path).read_bytes()
    refs = literal_refs(d, 0, CODE_END)
    print(
        "USB (0x40042000..):",
        {
            hex(k): [hex(x) for x in v][:3]
            for k, v in refs.items()
            if 0x40042000 <= k < 0x40042200
        },
    )
    print(
        "controlador de flash FM3 (0x4000_0xxx..0x4000_2xxx):",
        {hex(k) for k in refs if 0x40000000 <= k < 0x40003000} or "sin referencias",
    )
    print(
        "MFS/UART (0x40038000..):",
        {hex(k) for k in refs if 0x40038000 <= k < 0x40039000}
        or "sin referencias en código",
    )
    tabla = [struct.unpack_from("<I", d, 0x21950 + 4 * i)[0] for i in range(22)]
    print("tabla DWN:", d[0x21938:0x21943], [hex(x) for x in tabla][:4], "...")
    print(
        "llamadores 0xce54 (registro de callbacks USB):",
        [hex(x) for x in callers(d).get(0x19284, [])],
        "-> init 0x19284",
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
