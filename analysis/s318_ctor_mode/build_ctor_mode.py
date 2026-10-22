#!/usr/bin/env python3
"""S318 - constructor parametrico 0x436f3fc0, tabla 0x43bbe1cc y mapeo 0x43ad9162.

Completa S316: ademas del constructor ligero 0x436f27b4 hay un constructor con
argumento de modo, 0x436f3fc0(obj, idx):

* fija el mismo vptr (slot GOT 0x4402ac80 -> 0x43fce048, +8 -> 0x43fce050);
* lee `tabla[idx]` de 0x43bbe1cc (4 B por entrada) y lo pasa como 4.º argumento
  a 0x43ad9162(obj+0x2dc, 0, 8, 8, valor);
* 0x43ad9162 traduce 1->0x10, 2->0x40, otro->1 y lo guarda en obj+0x2dc.

El unico llamador directo localizado (0x436f2a8a) pasa idx=0 (tabla[0]=1).
La tabla cambia de forma a partir del indice 7 (pares u16), por lo que el rango
valido del argumento queda NO_VERIFICADO.

Solo bytes + evidencia REA. Sin firmware ni camara.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("ctor_mode.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

CTOR = 0x436F3FC0
CTOR_LIGHT = 0x436F27B4
MAPPER = 0x43AD9162
TABLE = 0x43BBE1CC
GOT_SLOT = 0x4402AC80


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(blob: bytes, a: int) -> int:
    return struct.unpack_from("<H", blob, a - BASE)[0]


def u32(blob: bytes, a: int) -> int:
    return struct.unpack_from("<I", blob, a - BASE)[0]


def insns(blob: bytes, start: int, size: int) -> list[dict]:
    raw = blob[start - BASE:start - BASE + size]
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw, start)]


def bl_calls(blob: bytes) -> list[tuple[int, int]]:
    out = []
    for off in range(0, len(blob) - 3, 2):
        h1, h2 = struct.unpack_from("<HH", blob, off)
        if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000:
            continue
        s = (h1 >> 10) & 1
        imm10 = h1 & 0x3FF
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        imm11 = h2 & 0x7FF
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        delta = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
        if s:
            delta -= 1 << 25
        out.append((BASE + off, (BASE + off + 4 + delta) & 0xFFFFFFFF))
    return out


def main() -> None:
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()
    ctor = insns(a7, CTOR, 0x40)
    mapper = insns(a7, MAPPER, 0x30)
    table = [{"index": i, "u32": f"0x{u32(a7, TABLE + 4 * i):08x}",
              "lo_u16": f"0x{u16(a7, TABLE + 4 * i):04x}",
              "hi_u16": f"0x{u16(a7, TABLE + 4 * i + 2):04x}"}
             for i in range(14)]
    callers = [f"0x{a:08x}" for a, t in bl_calls(a7) if t == CTOR]
    caller_ctx = insns(a7, 0x436F2A7C, 0x24)
    sig = a7[CTOR - BASE:CTOR - BASE + 32]
    data: dict = {
        "milestone": "S318",
        "title": "Constructor parametrico 0x436f3fc0, tabla 0x43bbe1cc y mapeo 0x43ad9162",
        "firmware": {"a7s": {"sha256": sha256(A7S), "size": len(a7)},
                     "a6000": {"sha256": sha256(A6000), "size": len(a6)}},
        "constructor": {"entry": f"0x{CTOR:08x}", "insn": ctor,
                        "signature": "0x436f3fc0(obj /*r0*/, idx /*r1*/)",
                        "vptr": "0x43fce050",
                        "got_slot": f"0x{GOT_SLOT:08x}",
                        "got_value": f"0x{u32(a7, GOT_SLOT):08x}",
                        "table": f"0x{TABLE:08x}",
                        "table_index": "r1 (mov r6,r1 en 0x436f3fc8)",
                        "callers": callers,
                        "caller_context": caller_ctx,
                        "light_ctor": f"0x{CTOR_LIGHT:08x}"},
        "mapper": {"entry": f"0x{MAPPER:08x}", "insn": mapper,
                   "mapping": [{"arg4": "1", "obj8": "0x10", "objc": "0x20"},
                               {"arg4": "2", "obj8": "0x40", "objc": "0x80"},
                               {"arg4": "otro", "obj8": "0x01", "objc": "0x02"}],
                   "stores": "obj+0x08 = valor; obj+0x0c = 2*valor"},
        "table": {"address": f"0x{TABLE:08x}", "stride": 4, "entries": table,
                  "shape_note": "indices 0..6 son enteros 1/2/0; desde 7 la palabra "
                                "empaqueta dos u16 (p. ej. 0x01ec0000), por lo que el "
                                "rango valido del argumento es NO_VERIFICADO"},
        "a6000_ctor_hits": a6.count(sig),
        "rea": {"pseudo_code_ctor": "FUN_436f3fc0(param_1,param_2): indice "
                                    "*(DAT_436f4134 + 0x436f3fe6 + param_2*4) -> "
                                    "FUN_43ad9162(param_1+0xb7,0,8,8,valor)",
                "xrefs_got_slot": ["0x436f27be", "0x436f3fda"]},
        "limits": [
            "Estatico: sin firmware ejecutado, sin camara, sin flasheo.",
            "El unico llamador directo usa idx=0; no se observa el resto de indices.",
            ("La tabla 0x43bbe1cc no es homogenea mas alla del indice 6; el rango valido "
             "del argumento y su relacion con el silent quedan NO_VERIFICADOS."),
            "S51 sin cambios.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print("callers ctor", callers)
    print("table[0..6]", [e["u32"] for e in table[:7]])
    print("table[7..9]", [e["u32"] for e in table[7:10]])
    print("A6000 ctor hits", data["a6000_ctor_hits"])


if __name__ == "__main__":
    main()
