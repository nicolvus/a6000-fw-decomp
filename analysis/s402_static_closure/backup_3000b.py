"""Clave Backup 0x3000b: tamaño, valores por defecto y gates +3/+6 del objeto de estado 0x43f72d02.

El formato lo define backup.ko (Data_init / Data_SearchId / Data_GetSize); los valores por defecto salen de las
imágenes CX775xx_*.bin del paquete (0110_backup). No incluye valores ajustados de fábrica de una cámara concreta.
"""

import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked"
KO = PKG / "0700_part_image/dev/nflasha15_unpacked_unpacked/kmod/backup.ko"
DEFAULTS = sorted((PKG / "0110_backup/SYSMUSASHI-DSLR/DM_UUD3").glob("*.bin"))
OUT = Path(__file__).with_name("backup_3000b.json")
KEY = 0x3000B
STATE_BASE = 0x43F72D02  # fila 18 de la tabla GOT 0x43ff3200 (S305)

# (offset en .text de backup.ko, palabra ARM) que fijan el formato; coinciden con el desensamblado de LLVM.
KO_WORDS = {
    0x3C6C: 0xE2843C01,  # Data_init: tabla de grupos = cabecera + 0x100
    0x3C98: 0xE0233291,  # Data_init: registros = tabla + 6 * n_grupos
    0x3E70: 0xE1A0C820,  # Data_SearchId: grupo = id >> 16
    0x3EA0: 0xE3A01006,  # Data_SearchId: entradas y registros de 6 bytes
    0x3EEC: 0xE0203091,  # Data_SearchId: registro = base_registros + 6 * (indice + base_grupo)
    0x4380: 0xE1B00C23,  # Data_GetSize: byte alto del desplazamiento = tamaño en linea o 0xff
    0x4388: 0xE35000FF,
    0x4398: 0x019200B3,  # Data_GetSize: tamaño u16 en cabecera + desplazamiento
    0x4190: 0x03A02004,  # Flash_Data_GetDataPt: sin byte alto, datos tras 4 bytes
    0x419C: 0x03A02002,  # idem: byte alto 0xff, datos tras 2 bytes
}


def ko_text(data: bytes) -> bytes:
    shoff = struct.unpack_from("<I", data, 32)[0]
    shentsize, shnum, shstrndx = struct.unpack_from("<3H", data, 46)
    sections = [struct.unpack_from("<10I", data, shoff + i * shentsize) for i in range(shnum)]
    names = data[sections[shstrndx][4]:sections[shstrndx][4] + sections[shstrndx][5]]
    for s in sections:
        if names[s[0]:].split(b"\0", 1)[0] == b".text":
            return data[s[4]:s[4] + s[5]]
    raise ValueError(".text no encontrada")


def ko_calls(data: bytes, offsets) -> dict:
    """Símbolo de la relocación R_ARM_CALL en cada offset de .text (núcleo de lectura)."""
    shoff = struct.unpack_from("<I", data, 32)[0]
    shentsize, shnum, shstrndx = struct.unpack_from("<3H", data, 46)
    sections = [struct.unpack_from("<10I", data, shoff + i * shentsize) for i in range(shnum)]
    names = data[sections[shstrndx][4]:sections[shstrndx][4] + sections[shstrndx][5]]
    by_name = {names[s[0]:].split(b"\0", 1)[0]: s for s in sections}
    symtab, strtab = by_name[b".symtab"], by_name[b".strtab"]
    strings = data[strtab[4]:strtab[4] + strtab[5]]
    symbols = [struct.unpack_from("<IIIBBH", data, symtab[4] + 16 * i) for i in range(symtab[5] // 16)]
    rel = by_name[b".rel.text"]
    found = {}
    for offset, info in struct.iter_unpack("<II", data[rel[4]:rel[4] + rel[5]]):
        if offset in offsets:
            found[hex(offset)] = strings[symbols[info >> 8][0]:].split(b"\0", 1)[0].decode()
    return found


READ_CORE_CALLS = {0xC40: "Data_SearchId", 0xC50: "Data_GetSize", 0xC8C: "Data_GetDataPt"}


def verify_ko() -> dict:
    data = KO.read_bytes()
    text = ko_text(data)
    calls = ko_calls(data, set(READ_CORE_CALLS))
    bad = {hex(o): hex(struct.unpack_from("<I", text, o)[0]) for o, w in KO_WORDS.items()
           if struct.unpack_from("<I", text, o)[0] != w}
    wrong = {hex(o): n for o, n in READ_CORE_CALLS.items() if calls.get(hex(o)) != n}
    return {"sha256": hashlib.sha256(data).hexdigest(), "mismatches": bad, "read_core_calls": calls,
            "read_core_call_mismatches": wrong}


def lookup(image: bytes, key: int) -> dict:
    groups = struct.unpack_from("<I", image, 0x10)[0]
    group, index = key >> 16, key & 0xFFFF
    if group >= groups:
        raise KeyError(key)
    maximum, base = struct.unpack_from("<HI", image, 0x100 + 6 * group)
    if index >= maximum:
        raise KeyError(key)
    record = 0x100 + 6 * groups + 6 * (index + base)
    attribute, offset = struct.unpack_from("<H", image, record)[0], struct.unpack_from("<I", image, record + 2)[0]
    top, position = offset >> 24, offset & 0xFFFFFF
    if top == 0xFF:
        size, data = struct.unpack_from("<H", image, position)[0], position + 2
    elif top == 0:
        size, data = struct.unpack_from("<H", image, position + 2)[0], position + 4
    else:
        size, data = top, position
    return {"groups": groups, "group_max": maximum, "group_base": base, "record": record, "attribute": attribute,
            "offset_word": offset, "size": size, "data_offset": data, "data": image[data:data + size]}


def build() -> dict:
    images: dict[bytes, list[str]] = {}
    for path in DEFAULTS:
        image = path.read_bytes()
        found = lookup(image, KEY)
        images.setdefault(found["data"], []).append(path.name)
        meta = {k: v for k, v in found.items() if k != "data"}
    result = {"key": hex(KEY), "state_base": hex(STATE_BASE), "backup_ko": verify_ko(), "default_images": len(DEFAULTS),
              "distinct_default_payloads": len(images), "layout": {k: hex(v) for k, v in meta.items() if k != "size"}}
    payload, names = next(iter(images.items()))
    result.update(size=len(payload), files=sorted(names),
                  nonzero={hex(i): b for i, b in enumerate(payload) if b},
                  gate_plus3={"address": hex(STATE_BASE + 3), "default": payload[3]},
                  gate_plus6={"address": hex(STATE_BASE + 6), "default": payload[6]},
                  byte_plus_0xac={"address": hex(STATE_BASE + 0xAC), "default": payload[0xAC]},
                  limits=("Valores de fábrica del paquete; la cámara puede conservar datos ajustados en su "
                          "almacenamiento Backup. Los gates +3/+6 valen 0 en TODAS las imágenes por defecto."))
    return result


if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(json.dumps({k: data[k] for k in ("size", "nonzero", "gate_plus3", "gate_plus6", "byte_plus_0xac", "distinct_default_payloads", "default_images")}))
    print(data["backup_ko"]["mismatches"])
