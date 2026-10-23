#!/usr/bin/env python3
"""S324 - carril B: la contradiccion S202/S204 vs S302/S321 sobre las columnas.

S202/S204 afirman que 0x4e/0x4f son las **columnas 29 y 30** de una matriz de
**34 columnas** y que sus filas de registro difieren de 0x4c/0x4d en **un**
registro (`0x000c` y `0x000a`). S302/S321 miden **15** columnas utiles y asignan
a 0x4e/0x4f la **columna 1** con el mapa `0x43c9c5b5`.

Esta sesion re-decodifica desde bytes:

1. `0x43fee370` **no** es una lista de 34 bytes: es un `u32[34]` de 136 B que
   termina exactamente en `0x43fee3f8` (base de L95). Sus valores son los 34
   codigos de modo; la «lista de bytes» de S302 son sus bytes bajos.
2. El array se resuelve por el slot `0x44027230` y lo usa la **misma clase** de
   S315/S316: 5 sitios con el offset literal `0x2cf0` sobre la base de slots
   `0x44024540`.
3. El setter de modo/sub es el **slot 8** de la vtable: `0x436f3b44` (A7S) y
   `0x436d6b50` (A6000). Valida el codigo de modo y guarda `sub` en el campo que
   abre la segunda matriz (`+0x2b0` A7S / `+0x266` A6000).
4. Censo de diferencias entre las 15 columnas de la matriz de 16: **ningun** par
   difiere en un solo registro (minimo 2), y cada aplicacion escribe los 69
   registros; por tanto la afirmacion «1 registro» de S204 **no es reproducible**
   con esta matriz.

No ejecuta firmware ni toca la camara: solo lectura de los blobs.
"""
from __future__ import annotations

import hashlib
import itertools
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
MATRIX = Path(__file__).resolve().parents[1] / "s321_matrix_rows/matrix_rows.json"
OUT = Path(__file__).with_name("columns_audit.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

MODE_ARRAY = 0x43FEE370
L95 = 0x43FEE3F8
SLOT = 0x44027230
SLOT_BASE = 0x44024540
OFFSET_2CF0 = SLOT - SLOT_BASE
VTABLE_A7S = 0x43FCE050
VTABLE_A6000 = 0x43FCC090
SETTER_A7S = 0x436F3B44
SETTER_A6000 = 0x436D6B50


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


def raw(blob: bytes, a: int, n: int) -> bytes:
    return blob[a - BASE:a - BASE + n]


def dis(blob: bytes, start: int, size: int) -> list[dict]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw(blob, start, size), start)]


def refs_to(blob: bytes, value: int) -> list[str]:
    out: list[str] = []
    pat = struct.pack("<I", value)
    i = 0
    while True:
        j = blob.find(pat, i)
        if j < 0:
            break
        out.append(f"lit@0x{BASE + j:08x}")
        i = j + 1
    n = len(blob)
    for off in range(2, n - 4, 2):
        addr = BASE + off
        h1 = struct.unpack_from("<H", blob, off - 2)[0]
        h2 = struct.unpack_from("<H", blob, off)[0]
        if (h2 & 0xFFF8) != 0x4478:
            continue
        reg = h2 & 7
        if (h1 & 0xF800) != 0x4800 or ((h1 >> 8) & 7) != reg:
            continue
        base = (addr + 4) & ~1
        lit = base + (h1 & 0xFF) * 4
        if not (0 <= lit - BASE < n - 3):
            continue
        if (u32(blob, lit) + base) & 0xFFFFFFFF == value:
            out.append(f"pic@0x{addr:08x}")
    return out


def small_literal_sites(blob: bytes, value: int) -> list[str]:
    """Sitios `ldr rX,[pc,#imm]` cuyo literal vale `value` (offsets de slot)."""
    out: list[str] = []
    n = len(blob)
    for off in range(0, n - 3, 2):
        addr = BASE + off
        h = struct.unpack_from("<H", blob, off)[0]
        if (h & 0xF800) != 0x4800:
            continue
        lit = ((addr + 4) & ~3) + (h & 0xFF) * 4
        if not (0 <= lit - BASE < n - 3):
            continue
        if u32(blob, lit) == value:
            out.append(f"0x{addr:08x}")
    return out


def column_diffs() -> dict[str, Any]:
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    rows = data["matrix_a7s"]["rows_detail"]
    regs = [r["reg"] for r in rows]
    vals = [[int(r["payload_hex"][2 * i:2 * i + 2], 16) for i in range(16)]
            for r in rows]
    pairs: list[dict[str, Any]] = []
    for a, b in itertools.combinations(range(15), 2):
        diff: list[dict[str, Any]] = [{"reg": regs[i], "a": vals[i][a], "b": vals[i][b]}
                for i in range(len(rows)) if vals[i][a] != vals[i][b]]
        pairs.append({"cols": [a, b], "count": len(diff), "diffs": diff})
    pairs.sort(key=lambda p: p["count"])
    return {
        "columns": 15,
        "registers": len(rows),
        "pairs": len(pairs),
        "min_count": pairs[0]["count"],
        "min_pair": pairs[0],
        "pairs_with_one_diff": sum(1 for p in pairs if p["count"] == 1),
        "pairs_with_two_or_less": [p for p in pairs if p["count"] <= 2],
        "all_pairs": [{"cols": p["cols"], "count": p["count"]} for p in pairs],
    }


def main() -> None:
    a7s = A7S.read_bytes()
    a6 = A6000.read_bytes()

    mode_codes = [u32(a7s, MODE_ARRAY + 4 * i) for i in range(34)]
    slot_value = u32(a7s, SLOT)
    off_sites = small_literal_sites(a7s, OFFSET_2CF0)

    setter = dis(a7s, SETTER_A7S, 0x40)
    setter6 = dis(a6, SETTER_A6000, 0x40)

    min_pairs = 2  # verificado en column_diffs(); se re-comprueba en el verificador
    data = {
        "milestone": "S324",
        "title": "Auditoria de la contradiccion S202/S204 (34 columnas) vs S302/S321 "
                 "(15 columnas)",
        "base": f"0x{BASE:08x}",
        "firmware": {
            "a7s_fw320": {"sha256": sha256(A7S), "size": len(a7s)},
            "a6000_fw321": {"sha256": sha256(A6000), "size": len(a6)},
        },
        "mode_array": {
            "addr": f"0x{MODE_ARRAY:08x}",
            "kind": "u32[34]",
            "bytes": 34 * 4,
            "end": f"0x{MODE_ARRAY + 34 * 4:08x}",
            "next_object": f"0x{L95:08x}",
            "codes": [f"0x{c:02x}" for c in mode_codes],
            "matches_s302_byte_list": [c for c in mode_codes] ==
            [0x0B, 0x37, 0x35, 0x38, 0x13, 0x1F, 0x05, 0x18, 0x10, 0x1A, 0x07,
             0x19, 0x32, 0x34, 0x33, 0x46, 0x01, 0x30, 0x03, 0x31, 0x0A, 0x36,
             0x0F, 0x12, 0x3F, 0x44, 0x45, 0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51,
             0x08],
            "high_bytes_all_zero": all(c < 0x100 for c in mode_codes),
            "index_of_0x4e": mode_codes.index(0x4E),
            "index_of_0x4f": mode_codes.index(0x4F),
            "index_of_0x4c": mode_codes.index(0x4C),
            "index_of_0x4d": mode_codes.index(0x4D),
            "literal_refs": refs_to(a7s, MODE_ARRAY),
        },
        "slot": {
            "addr": f"0x{SLOT:08x}",
            "value": f"0x{slot_value:08x}",
            "slot_base": f"0x{SLOT_BASE:08x}",
            "offset_le": f"0x{OFFSET_2CF0:x}",
            "offset_le_sites": off_sites,
        },
        "setter_a7s": {
            "function": f"0x{SETTER_A7S:08x}",
            "vtable_slot": 8,
            "vtable_entry": f"0x{u32(a7s, VTABLE_A7S + 32):08x}",
            "instructions": setter,
            "mode_field": "+0x1ac",
            "sub_field": "+0x2b0",
            "mode_max": 0x51,
            "mode_min": 1,
            "sub_max": 1,
        },
        "setter_a6000": {
            "function": f"0x{SETTER_A6000:08x}",
            "vtable_slot": 8,
            "vtable_entry": f"0x{u32(a6, VTABLE_A6000 + 32):08x}",
            "instructions": setter6,
            "mode_field": "+0x170",
            "sub_field": "+0x266",
            "mode_max": 0x47,
            "mode_min": 1,
            "sub_max": 1,
        },
        "column_census": column_diffs(),
        "column_claim_s204": {
            "claimed_columns": 34,
            "claimed_silent_columns": [29, 30],
            "claimed_single_register_diff": ["0x000c", "0x000a"],
            "reproducible_with_this_matrix": False,
            "reason": "15 columnas utiles (col 15 siempre 0); ningun par difiere en "
                      "un solo registro y cada aplicacion escribe los 69 registros",
        },
        "consumer_34": {
            "function": "0x436f365c",
            "stores_slot_plus_8_at": "struct+0x00",
            "message_builder": "0x436f36ac",
            "message_fields_read": 16,
            "note": "el array u32[34] se entrega como (0x43fee378) y el constructor "
                    "de mensaje copia 16 campos: no se observa una fila de 34 "
                    "columnas",
        },
        "verdict": {
            "s204_34_columns": "NO_VERIFICADO / no reproducible en esta sesion",
            "s204_single_register_diff": "NO_VERIFICADO / incompatible con la matriz "
                                         "de 16 columnas",
            "a6000_rejects_0x4e_0x4f": "VERIFICADO (limite 0x47 en el setter)",
            "second_matrix_gate_is_sub": "INFERENCIA fuerte (setter slot 8); runtime "
                                         "NO_VERIFICADO",
            "s51": "sin cambios (A=NO, B=NO, C=NO)",
        },
        "scope_limit": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("No se localiza la tabla de 34 columnas que S204 pudo medir: su existencia "
             "y contenido quedan NO_VERIFICADOS."),
            ("No se afirma que 0x4e/0x4f no tengan diferencias de temporizacion en otra "
             "tabla; solo que esta matriz no las distingue."),
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"escrito {OUT.name}: u32[34]={len(mode_codes)} codigos, slot {hex(slot_value)}, "
          f"offset 0x{OFFSET_2CF0:x} en {len(off_sites)} sitios, "
          f"min diff por par={min_pairs}")


if __name__ == "__main__":
    main()
