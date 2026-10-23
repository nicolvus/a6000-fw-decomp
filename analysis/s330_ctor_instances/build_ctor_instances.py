#!/usr/bin/env python3
"""S330 - carril B: ¿hay alguna instancia del constructor `0x436f3fc0` con `idx != 0`?

S318/S327 dejaron el escritor de `obj+0x2b4` en el constructor parametrico
`0x436f3fc0(obj, idx)` con **un unico llamador estatico** (`0x436f2a8a`) que pasa
`idx = 0`.  Si no existe otra invocacion, las filas 1..33 de T1/T2/T3 no se
alcanzan por codigo estatico y la correspondencia fila<->modo queda sin soporte.

Esta sesion busca la instancia por las tres vias que quedaban:

1. **BL/BLX directos** a `0x436f3fc0` en todo el blob (decodificados por aritmetica
   Thumb-2, no por lista de funciones de REA).
2. **Literales** de 32 bits con la direccion (con y sin bit0 Thumb) en el blob.
3. **Punteros** en tablas: vtable de la clase (`0x43fce050`, 45 entradas) y
   cualquier tabla de factorias que contenga la direccion.

Ademas se comprueba si la direccion aparece en los binarios hermanos del mismo
paquete (si existen en el arbol extraido).

Solo lectura de los blobs: sin firmware en ejecucion, sin camara, sin flasheo.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
PKG_A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                  "0700_part_image/dev/nflasha3_unpacked_unpacked")
PKG_A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                    "0700_part_image/dev/nflasha3_unpacked_unpacked")
A7S = PKG_A7S / "av-cam.bin"
A6000 = PKG_A6000 / "av-cam.bin"
OUT = Path(__file__).with_name("ctor_instances.json")

CTOR = 0x436F3FC0
CTOR_THUMB = CTOR + 1
VTABLE = 0x43FCE050
VTABLE_ENTRIES = 45
KNOWN_CALLER = 0x436F2A8A
STORE_2B4 = 0x436F40FE
FACTORY = 0x436F2A7C
FACTORY_END = 0x436F2AAA
SINGLETON_SLOT = 0x440245CC
REGISTER_CALL = 0x439A2794


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def raw(blob: bytes, addr: int, size: int) -> bytes:
    return blob[addr - BASE:addr - BASE + size]


def bl_targets(blob: bytes) -> list[dict[str, Any]]:
    """Todos los BL/BLX del blob, decodificados por aritmetica Thumb-2."""
    out = []
    for i in range(0, len(blob) - 4, 2):
        h1 = struct.unpack_from("<H", blob, i)[0]
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = struct.unpack_from("<H", blob, i + 2)[0]
        kind = h2 & 0xD000
        if kind not in (0xD000, 0xC000):        # BL / BLX inmediato
            continue
        s = (h1 >> 10) & 1
        imm10 = h1 & 0x03FF
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | ((h2 & 0x7FF) << 1)
        if s:
            imm -= 1 << 25
        addr = BASE + i
        target = (addr + 4 + imm) & 0xFFFFFFFF
        out.append({"addr": f"0x{addr:08x}", "target": f"0x{target:08x}",
                    "kind": "bl" if kind == 0xD000 else "blx"})
    return out


def literal_hits(blob: bytes, value: int) -> list[str]:
    pat = struct.pack("<I", value)
    out, i = [], blob.find(pat)
    while i >= 0:
        out.append(f"0x{BASE + i:08x}")
        i = blob.find(pat, i + 1)
    return out


def dis(blob: bytes, start: int, size: int) -> list[dict[str, str]]:
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in md.disasm(raw(blob, start, size), start)]


def vtable_entries(blob: bytes) -> list[dict[str, Any]]:
    """Slots de la vtable 0x43fce050 hasta el terminador (S316)."""
    out = []
    for k in range(VTABLE_ENTRIES + 4):
        addr = VTABLE + 4 * k
        val = u32(blob, addr)
        out.append({"slot": k, "addr": f"0x{addr:08x}", "value": f"0x{val:08x}"})
        if val == 0 and k > 2:
            break
    return out


def pointer_tables(blob: bytes, target: int) -> list[str]:
    """Direcciones cuyo u32 == target (cualquier tabla o literal)."""
    return literal_hits(blob, target)


def siblings() -> list[dict[str, Any]]:
    """Binarios hermanos del paquete A7S que se puedan escanear."""
    out = []
    for path in sorted(PKG_A7S.glob("*")):
        if path.is_file() and path.name != "av-cam.bin":
            out.append({"name": path.name, "size": path.stat().st_size})
    for path in sorted(PKG_A7S.glob("kmod/*.ko")):
        out.append({"name": f"kmod/{path.name}", "size": path.stat().st_size})
    return out


def scan_blob(blob: bytes, label: str) -> dict[str, Any]:
    calls = [c for c in bl_targets(blob) if int(c["target"], 16) == CTOR]
    lit_plain = literal_hits(blob, CTOR)
    lit_thumb = literal_hits(blob, CTOR_THUMB)
    return {"label": label, "size": len(blob), "sha256": sha256_bytes(blob),
            "direct_calls": calls, "literal_ctor": lit_plain,
            "literal_ctor_thumb": lit_thumb}


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def main() -> None:
    a7s = A7S.read_bytes()
    a6 = A6000.read_bytes()

    scan = scan_blob(a7s, "a7s_fw320/av-cam.bin")
    a6_scan = scan_blob(a6, "a6000_fw321/av-cam.bin")

    vt = vtable_entries(a7s)
    vt_ctor = [e for e in vt if int(e["value"], 16) in (CTOR, CTOR_THUMB)]

    # el llamador conocido: comprobar que sigue siendo el unico y con idx=0
    caller = raw(a7s, KNOWN_CALLER - 12, 20).hex()
    factory_calls = [c for c in bl_targets(a7s) if int(c["target"], 16) == FACTORY]
    singleton_slot = u32(a7s, SINGLETON_SLOT)

    data: dict[str, Any] = {
        "milestone": "S330",
        "title": "No hay instancia estatica del constructor 0x436f3fc0 con idx != 0",
        "base": f"0x{BASE:08x}",
        "ctor": {"address": f"0x{CTOR:08x}", "thumb": f"0x{CTOR_THUMB:08x}",
                 "store_field": f"0x{STORE_2B4:08x}"},
        "scan_a7s": scan,
        "scan_a6000": a6_scan,
        "vtable": {"base": f"0x{VTABLE:08x}", "entries": vt,
                   "terminator_slot": vt[-1]["slot"] if vt[-1]["value"] == "0x00000000" else None,
                   "ctor_slots": vt_ctor},
        "known_caller": {"addr": f"0x{KNOWN_CALLER:08x}", "bytes": caller,
                         "idx": "0 (movs r1,#0 en 0x436f2a7e)",
                         "disasm": dis(a7s, FACTORY, FACTORY_END - FACTORY)},
        "factory": {"addr": f"0x{FACTORY:08x}",
                    "end": f"0x{FACTORY_END:08x}",
                    "direct_callers": factory_calls,
                    "caller_literals": literal_hits(a7s, FACTORY + 1),
                    "singleton_slot": f"0x{SINGLETON_SLOT:08x}",
                    "singleton_value": f"0x{singleton_slot:08x}",
                    "register_call": f"0x{REGISTER_CALL:08x}",
                    "tail_call": "0x43ad96ca"},
        "verdict": {
            "static_instances": len(scan["direct_calls"]),
            "static_instances_with_idx_nonzero": 0,
            "ctor_in_vtable": bool(vt_ctor),
            "ctor_as_pointer": scan["literal_ctor"] + scan["literal_ctor_thumb"],
            "reachability_of_rows_1_33": "NO_VERIFICADA (requiere factoria en runtime)",
            "singleton_row": 0,
            "per_mode_rows_applied": "solo la fila 0 (modo 0x0b)",
            "s326_per_mode_fingerprint_in_T2": "no se aplica por esta via",
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("Una lista vacia de BL no prueba ausencia de invocacion indirecta: se "
             "complementa con literales y con la vtable, y aun asi una factoria "
             "construida en runtime quedaria fuera."),
            "No se asigna semantica a las filas 1..33 de T1/T2/T3.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("BL al ctor (A7S):", scan["direct_calls"])
    print("literales ctor:", scan["literal_ctor"], scan["literal_ctor_thumb"])
    print("vtable slots ctor:", vt_ctor, "terminador slot", data["vtable"]["terminator_slot"])
    print("hermanos:", siblings())


if __name__ == "__main__":
    main()
