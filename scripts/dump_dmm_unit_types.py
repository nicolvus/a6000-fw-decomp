"""Vuelca los tipos de unidad DMM de kmod/dmm.ko (ConfigData en .rodata): tipo -> lista de extents.
Uso: python3 -I scripts/dump_dmm_unit_types.py [salida.json]
Registro: {unitType, 0, extentId..., 0xffffffff}. ConfigData = .rodata+0x184 (64 KB). Sesión 14.
"""
import json
import struct
import sys
from pathlib import Path

KO = Path("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/kmod/dmm.ko")
RODATA_OFF, CONFIG_OFF, CONFIG_SIZE = 0xFD88, 0x184, 63976
FIRST_RECORD = 0x1E0FC  # primer registro de la lista (offset de archivo)
KNOWN = {0x50B3F: "STL_YCC_1920P (1920x1080)", 0x220B2E: "640x480 (FUN_001804e4)", 0xE0B00: "SDS_YCC", 0x243: "alt dec (no está en la lista)"}


def main(out: str) -> None:
    d = KO.read_bytes()
    u = lambda o: struct.unpack_from("<I", d, o)[0]
    end = RODATA_OFF + CONFIG_OFF + CONFIG_SIZE
    o, units = FIRST_RECORD, {}
    while o < end and u(o + 4) == 0:
        ext, p = [], o + 8
        while u(p) != 0xFFFFFFFF and len(ext) < 16:
            ext.append(u(p)); p += 4
        units[hex(u(o))] = ext
        o = p + 4
    assert units["0x50b3f"] == [0xED] and units["0xe0b00"] == [0xE4]  # self-check
    Path(out).write_text(json.dumps({"unit_types": units, "known": {hex(k): v for k, v in KNOWN.items()}, "count": len(units)}, indent=1))
    print(f"{len(units)} tipos -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "analysis/dmm-unit-types.json")
