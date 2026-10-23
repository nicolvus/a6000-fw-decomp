#!/usr/bin/env python3
"""S332 - carril B: el mecanismo por modo del A6000 frente al del A7S.

S331 demostro que en el A7S la fila de T1/T2/T3 la elige la **posicion del modo**
y que cada fila es `(indice a una tabla de descriptores, mascara de 12 bits)`.
Esta sesion mide lo mismo en la A6000 fw3.21:

* setter de modo `0x436d6b50` (vtable `0x43fcc090` slot 8): busqueda lineal
  `0x43ad9438` sobre una lista de **13** codigos, indice a `obj+0x17c`, flag a
  `obj+0x26c`, matriz de registros por el slot 40 (`0x436d6570`) y despues
  `0x436d8e6c(obj+0x18, indice, flag)`.
* consumidor `0x436d8e6c`: stride `0x1c`, lee `+0x14` (indice de descriptor) y
  `+0x18` (mascara), y rellena **dos** bloques (`obj+0x14` y `obj+0xa1`) con
  `0x436d8c48` (ventana `ip+0x20`) y `0x436d8e20` (ventana `ip+0x60`).
* descriptores compartidos en `0x43c949a7`: **3** filas (identidad, permutacion,
  `1,1,1,1,0,...`).

Comparacion: el mecanismo es **compartido**; lo que cambia es el dato (13 modos
frente a 34, 2 bloques frente a 3, descriptores usados 0 frente a 0/1, mascaras
sin cero frente a mascaras con cero).

Solo lectura de los blobs: sin firmware en ejecucion, sin camara, sin flasheo.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("a6000_tables.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

A6_SETTER = 0x436D6B50
A6_SEARCH = 0x43AD9438
A6_CONSUMER = 0x436D8E6C
A6_TABLES: dict[str, tuple[int, int, str]] = {
    "TA1": (0x436D8EB0, 0x436D8EB8, "obj+0x14"),
    "TA2": (0x436D8EC8, 0x436D8ECC, "obj+0xa1"),
}
A6_GOT_LIT = (0x436D6B50, 0x436D6B56)       # base PIC de la GOT
A6_LIST_OFF_LIT = 0x436D6B86                # offset del slot de la lista
A6_COUNT = 13
A6_DESC_HELPERS: dict[str, tuple[int, int]] = {
    "desc_20": (0x436D8C60, 0x436D8C62),
    "desc_60": (0x436D8E38, 0x436D8E3A),
}

A7_TABLES = {"T1": 0x43BBEB70, "T2": 0x43BBF2E8, "T3": 0x43BBEF30}
A7_MODE_LIST = 0x43FEE370
A7_DESC = 0x43C9D09B
A7_COUNT = 34
STRIDE = 0x1C


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<H", blob, addr - BASE)[0]


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def raw(blob: bytes, addr: int, size: int) -> bytes:
    return blob[addr - BASE:addr - BASE + size]


def dis(blob: bytes, start: int, size: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw(blob, start, size), start)]


def pic(blob: bytes, ldr: int, add: int) -> int:
    h = u16(blob, ldr)
    assert (h & 0xF800) == 0x4800, f"0x{ldr:08x} no es ldr pc-rel"
    lit = ((ldr + 4) & ~3) + (h & 0xFF) * 4
    return (u32(blob, lit) + ((add + 4) & ~1)) & 0xFFFFFFFF


def rows(blob: bytes, base: int, count: int) -> list[dict[str, Any]]:
    out = []
    for i in range(count):
        a = base + STRIDE * i
        out.append({"index": i, "addr": f"0x{a:08x}",
                    "w0": u32(blob, a), "w4": f"0x{u32(blob, a + 4):08x}",
                    "descriptor_index": u32(blob, a + 0x14),
                    "mask": u16(blob, a + 0x18),
                    "hex": raw(blob, a, STRIDE).hex()})
    return out


def stats(table_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"index_values": sorted({r["descriptor_index"] for r in table_rows}),
            "mask_values": sorted({r["mask"] for r in table_rows}),
            "zero_masks": sum(1 for r in table_rows if r["mask"] == 0),
            "w0_values": sorted({r["w0"] for r in table_rows}),
            "w4_values": sorted({r["w4"] for r in table_rows})}


def main() -> None:
    a6 = A6000.read_bytes()
    a7 = A7S.read_bytes()

    # lista de modos de la A6000 via GOT
    got = pic(a6, *A6_GOT_LIT)
    off = u32(a6, ((A6_LIST_OFF_LIT + 4) & ~3) + (u16(a6, A6_LIST_OFF_LIT) & 0xFF) * 4)
    slot = (got + off) & 0xFFFFFFFF
    list_ptr = u32(a6, slot)
    a6_codes = [u32(a6, list_ptr + 4 * i) for i in range(A6_COUNT)]

    a6_tables: dict[str, dict[str, Any]] = {}
    for name, (ldr, add, dest) in A6_TABLES.items():
        base = pic(a6, ldr, add)
        rs = rows(a6, base, A6_COUNT)
        a6_tables[name] = {"base": f"0x{base:08x}", "dest": dest,
                           "rows": rs, "stats": stats(rs)}

    desc_ptr = pic(a6, *A6_DESC_HELPERS["desc_20"])
    desc_ptr2 = pic(a6, *A6_DESC_HELPERS["desc_60"])
    a6_desc_rows = [list(raw(a6, desc_ptr + 12 * k, 12)) for k in range(3)]

    a7_codes = [u32(a7, A7_MODE_LIST + 4 * i) for i in range(A7_COUNT)]
    a7_tables: dict[str, dict[str, Any]] = {}
    for name, base in A7_TABLES.items():
        rs = rows(a7, base, A7_COUNT)
        a7_tables[name] = {"base": f"0x{base:08x}", "rows": rs, "stats": stats(rs)}
    a7_desc_rows = [list(raw(a7, A7_DESC + 12 * k, 12)) for k in range(2)]

    data: dict[str, Any] = {
        "milestone": "S332",
        "title": "El mecanismo por modo (indice de descriptor + mascara 12 bits) "
                 "es compartido con el A6000; cambia el dato, no la estructura",
        "base": f"0x{BASE:08x}",
        "firmware": {"a7s_fw320": {"sha256": sha256(A7S), "size": len(a7)},
                     "a6000_fw321": {"sha256": sha256(A6000), "size": len(a6)}},
        "a6000": {
            "setter": {"address": f"0x{A6_SETTER:08x}",
                       "disasm": dis(a6, A6_SETTER, 0x140)},
            "search": {"address": f"0x{A6_SEARCH:08x}",
                       "disasm": dis(a6, A6_SEARCH, 0x1C)},
            "mode_list": {"slot": f"0x{slot:08x}", "pointer": f"0x{list_ptr:08x}",
                          "count": A6_COUNT,
                          "codes": [f"0x{c:02x}" for c in a6_codes]},
            "consumer": {"address": f"0x{A6_CONSUMER:08x}",
                         "disasm": dis(a6, A6_CONSUMER, 0x74),
                         "signature": "(obj, posicion_modo, flag)"},
            "tables": a6_tables,
            "descriptor": {"base": f"0x{desc_ptr:08x}",
                           "rows": a6_desc_rows,
                           "shared_by_helpers": desc_ptr == desc_ptr2,
                           "helpers": {k: [f"0x{v[0]:08x}", f"0x{v[1]:08x}"]
                                       for k, v in A6_DESC_HELPERS.items()}},
            "helper_windows": {"desc_20": "ip+0x20", "desc_60": "ip+0x60",
                               "ip_got_base": f"0x{got:08x}"},
        },
        "a7s": {"mode_list": {"address": f"0x{A7_MODE_LIST:08x}", "count": A7_COUNT,
                              "codes": [f"0x{c:02x}" for c in a7_codes]},
                "tables": a7_tables,
                "descriptor": {"base": f"0x{A7_DESC:08x}", "rows": a7_desc_rows}},
        "comparison": {
            "counts": {"a6000": A6_COUNT, "a7s": A7_COUNT},
            "blocks": {"a6000": ["obj+0x14", "obj+0xa1"],
                       "a7s": ["obj+0x16", "obj+0x2e", "obj+0xa5"]},
            "descriptor_rows": {"a6000": 3, "a7s": 2},
            "descriptor_index_used": {
                "a6000": sorted({r["descriptor_index"] for t in a6_tables.values()
                                 for r in t["rows"]}),
                "a7s": sorted({r["descriptor_index"] for t in a7_tables.values()
                               for r in t["rows"]})},
            "mask_union": {
                "a6000": sorted({r["mask"] for t in a6_tables.values() for r in t["rows"]}),
                "a7s": sorted({r["mask"] for t in a7_tables.values() for r in t["rows"]})},
            "zero_masks": {"a6000": sum(t["stats"]["zero_masks"]
                                        for t in a6_tables.values()),
                           "a7s": sum(t["stats"]["zero_masks"]
                                      for t in a7_tables.values())},
            "silent_codes_present": {"a6000": False, "a7s": True},
        },
        "verdicts": {
            "same_mechanism": True,
            "a6000_has_silent_mode": False,
            "a6000_uses_permutation_descriptor": False,
            "a6000_has_zero_masks": False,
            "a6000_mode_limit": "0x47 (cmp r2,#0x47 en 0x436d6b62)",
            "a7s_mode_limit": "0x51 (cmp r3,#0x51 en 0x436f3b54)",
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("Que los bloques rellenados sean el mismo tipo de mensaje en ambos "
             "modelos es INFERENCIA: los offsets destino difieren (0x14/0xa1 frente "
             "a 0x16/0x2e/0xa5)."),
            "No se asigna semantica fisica a las mascaras ni a los descriptores.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("A6000 lista:", data["a6000"]["mode_list"]["codes"])
    print("A6000 tablas:", {k: (v["base"], v["stats"]) for k, v in a6_tables.items()})
    print("A6000 descriptor:", hex(desc_ptr), a6_desc_rows)
    print("comparison:", data["comparison"])


if __name__ == "__main__":
    main()
