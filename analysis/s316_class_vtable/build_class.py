#!/usr/bin/env python3
"""S316 - clase duena de las listas: constructor, vtable y metodos 0x38/0x44.

Identifica el objeto que aplica las listas de S315:

* constructor `0x436f27b4`: carga el slot GOT `0x4402ac80` (=0x43fce048),
  suma 8 y guarda `0x43fce050` en `obj[0]` (vptr), inicializa `obj+0x394`.
* metadata de vtable en `0x43fce048`: offset-to-top 0, typeinfo `0x43feeb20`.
* tabla de 45 funciones desde `0x43fce050` hasta `0x43fce100`; terminador en
  `0x43fce104`.
* los dos metodos que aplican listas con modo (`0x436f5a14`, `0x436f53f4`)
  ocupan los slots `+0x38` y `+0x44`.
* wrapper de creacion/registro `0x43ad9840` (slot `+0x04`).

Solo bytes. Sin firmware ni camara.
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
OUT = Path(__file__).with_name("class.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

CTOR = 0x436F27B4
WRAPPER = 0x43AD9840
VTABLE_META = 0x43FCE048
VTABLE = 0x43FCE050
TYPEINFO = 0x43FEEB20
GOT_BASE = 0x44024540
GOT_OFFSET = 0x6740
GOT_SLOT = 0x4402AC80
METHOD_SLOTS = {"0x436f5a14": 0x38, "0x436f53f4": 0x44, "0x43ad9840": 0x04}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def insns(blob: bytes, start: int, size: int) -> list[dict]:
    raw = blob[start - BASE:start - BASE + size]
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw, start)]


def vtable(blob: bytes) -> dict:
    entries = []
    addr = VTABLE
    while u32(blob, addr) != 0:
        entries.append({"slot": f"0x{addr - VTABLE:02x}", "addr": f"0x{addr:08x}",
                        "target": f"0x{u32(blob, addr) & ~1:08x}"})
        addr += 4
    return {"metadata": f"0x{VTABLE_META:08x}",
            "offset_to_top": u32(blob, VTABLE_META),
            "typeinfo": f"0x{u32(blob, VTABLE_META + 4):08x}",
            "table": f"0x{VTABLE:08x}", "count": len(entries),
            "end": f"0x{addr:08x}", "terminator": u32(blob, addr),
            "entries": entries}


def main() -> None:
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()
    ctor = insns(a7, CTOR, 0x24)
    wrapper = insns(a7, WRAPPER, 0x14)
    lit_base = u32(a7, 0x436F27E0)
    base = (lit_base + 0x436F27BC) & 0xFFFFFFFF
    vt = vtable(a7)
    method_slots = {}
    for fn, slot in METHOD_SLOTS.items():
        entry = next((e for e in vt["entries"] if e["target"] == fn), None)
        method_slots[fn] = {"expected_slot": f"0x{slot:02x}",
                            "vtable_entry": entry,
                            "matches": bool(entry and entry["slot"] == f"0x{slot:02x}")}
    fields = {
        "obj+0x13c": "add.w r7,r0,#0x13c (0x436f44c8) y 0x436f450a",
        "obj+0x1ac/+0x1b0": "comparados con 0x11 (0x436f5b14..0x436f5b20)",
        "obj+0x1b4": "escrito desde +0x1b0 en 0x436f5b60",
        "obj+0x2b2": "byte leido en 0x436f5a9c/0x436f5aa0",
        "obj+0x2b4": "indice usado en 0x436f4546 y 0x436f4476",
        "obj+0x2dc": "subobjeto add.w r5,r4,#0x2dc (0x436f4514)",
        "obj+0x394": "subobjeto inicializado por el constructor (0x436f27c4)",
        "obj+0x3dc": "estado leido/escrito en 0x436f43c0..0x436f4414",
    }
    sig = {}
    for name, addr, n in [("ctor", CTOR, 32), ("wrapper", WRAPPER, 16),
                          ("method_5a14", 0x436F5A14, 32),
                          ("method_53f4", 0x436F53F4, 24)]:
        s = a7[addr - BASE:addr - BASE + n]
        sig[name] = {"address": f"0x{addr:08x}", "bytes": n,
                     "signature": s.hex(), "a6000_hits": a6.count(s)}
    data: dict = {
        "milestone": "S316",
        "title": "Clase duena de las listas: constructor 0x436f27b4, vtable 0x43fce050 y slots 0x38/0x44",
        "firmware": {"a7s": {"sha256": sha256(A7S), "size": len(a7)},
                     "a6000": {"sha256": sha256(A6000), "size": len(a6)}},
        "constructor": {"entry": f"0x{CTOR:08x}", "insn": ctor,
                        "got": {"base": f"0x{base:08x}", "literal_at": "0x436f27e0",
                                "literal": f"0x{lit_base:08x}", "offset": f"0x{GOT_OFFSET:04x}",
                                "slot": f"0x{base + GOT_OFFSET:08x}",
                                "value": f"0x{u32(a7, GOT_SLOT):08x}"},
                        "vptr_stored": f"0x{u32(a7, GOT_SLOT) + 8:08x}"},
        "wrapper": {"entry": f"0x{WRAPPER:08x}", "insn": wrapper,
                    "role": "crea (bl 0x436f27b4) y registra (bl 0x439a2780)"},
        "vtable": vt,
        "method_slots": method_slots,
        "fields": fields,
        "a6000_presence": sig,
        "limits": [
            "Estatico: sin firmware ejecutado, sin camara, sin flasheo.",
            ("Que el objeto sea 'el de las listas' se apoya en que sus metodos +0x38/+0x44 "
             "llaman a 0x436f44c4 con las listas de S315; la semantica de la clase no tiene nombre."),
            "El campo +0x2b4 se usa como indice de tabla, pero la tabla y su dominio quedan NO_VERIFICADOS.",
            "El enlace con el silent shutter sigue NO_VERIFICADO; S51 sin cambios.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print("ctor slot", data["constructor"]["got"]["slot"],
          "->", data["constructor"]["got"]["value"],
          "vptr", data["constructor"]["vptr_stored"])
    print("vtable entries", vt["count"], "end", vt["end"])
    print("slots", {k: v["vtable_entry"] for k, v in method_slots.items()})
    print("A6000 hits", {k: v["a6000_hits"] for k, v in sig.items()})


if __name__ == "__main__":
    main()
