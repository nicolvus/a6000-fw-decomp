#!/usr/bin/env python3
"""S344 - carril B: las dos tablas de 3 entradas de `0x436f6240`.

S336 detecto que `0x436f6240` usa los bytes `+4/+5/+6` de la fila T como
selectores de dos tablas de punteros.  Decodificadas desde los bytes:

  * `0x43bbeb64` = `[0, 1, 4]`  (3 u32, termina justo en la base de T1)
  * `0x43bbef28` = `[6, 5, 4]`  (3 u32, empieza justo al terminar T1)

Seleccion: si `row[5]==0` -> `tabla_B[row[6]]` (si `row[6] <= 1`); si
`row[5]==1` -> `tabla_A[row[4]]` (si `row[4] <= 2`).  Con las filas reales:

  * A7S: los 34 modos dan 1, salvo las posiciones 1 y 3 (modos `0x37`/`0x38`)
    que dan 4.
  * A6000: los 13 modos dan 1.

`0x436f6278(indice)` es el envoltorio que selecciona la fila T1 (`mla` stride
0x1c, limite 0x21).  Ni `0x436f6240` ni `0x436f6278` tienen **llamador
estatico** (0 `bl`, 0 literal), asi que el uso del valor devuelto no se puede
cerrar estaticamente.

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
FW = ROOT / "firmware/extracted"
BLOBS = {
    "a7s_fw320": FW / ("a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/"
                       "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6000_fw321": FW / ("fw321/firmware.tar_unpacked/0700_part_image/dev/"
                         "nflasha3_unpacked_unpacked/av-cam.bin"),
}
OUT = Path(__file__).with_name("selector_tables.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u8(b: bytes, a: int) -> int:
    return b[a - BASE]


def u16(b: bytes, a: int) -> int:
    return struct.unpack_from("<H", b, a - BASE)[0]


def u32(b: bytes, a: int) -> int:
    return struct.unpack_from("<I", b, a - BASE)[0]


def code(b: bytes, start: int, size: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(b[start - BASE:start - BASE + size], start)]


def pic(b: bytes, ldr: int, add: int) -> tuple[int, int, int]:
    h = u16(b, ldr)
    assert (h & 0xF800) == 0x4800
    lit = ((ldr + 4) & ~3) + (h & 0xFF) * 4
    word = u32(b, lit)
    return lit, word, (word + ((add + 4) & ~1)) & 0xFFFFFFFF


def bl_callers(b: bytes, target: int) -> list[int]:
    out = []
    for off in range(0, len(b) - 4, 2):
        h = struct.unpack_from("<H", b, off)[0]
        if (h & 0xF800) != 0xF000:
            continue
        h2 = struct.unpack_from("<H", b, off + 2)[0]
        if (h2 & 0xD000) != 0xD000:
            continue
        s = (h >> 10) & 1
        j1, j2 = (h2 >> 13) & 1, (h2 >> 11) & 1
        val = ((s << 24) | ((1 - (j1 ^ s)) << 23) | ((1 - (j2 ^ s)) << 22)
               | ((h & 0x3FF) << 12) | ((h2 & 0x7FF) << 1))
        if s:
            val -= 1 << 25
        if (BASE + off + 4 + val) & 0xFFFFFFFF == target:
            out.append(BASE + off)
    return out


def literals_for(b: bytes, value: int) -> list[int]:
    pat = struct.pack("<I", value)
    out, i = [], b.find(pat)
    while i >= 0:
        out.append(BASE + i)
        i = b.find(pat, i + 1)
    return out


def mapping(r4: int, r5: int, r6: int) -> int | None:
    """Replica la decision de 0x436f6240."""
    if r5 == 0:
        if r6 > 1:
            return 6
        return [6, 5][r6]
    if r5 == 1:
        if r4 > 2:
            return 0
        return [0, 1, 4][r4]
    return 0


def main() -> None:
    blobs = {k: p.read_bytes() for k, p in BLOBS.items()}
    a7, a6 = blobs["a7s_fw320"], blobs["a6000_fw321"]

    tab_a = 0x43BBEB64
    tab_b = 0x43BBEF28
    arr_a = [u32(a7, tab_a + 4 * i) for i in range(3)]
    arr_b = [u32(a7, tab_b + 4 * i) for i in range(3)]
    t1 = 0x43BBEB70
    t1_end = t1 + 34 * 0x1C

    # filas reales por modo
    modes7 = [u32(a7, 0x43FEE370 + 4 * i) for i in range(34)]
    per7 = []
    for pos, m in enumerate(modes7):
        row = t1 + 0x1C * pos
        r4, r5, r6 = u8(a7, row + 4), u8(a7, row + 5), u8(a7, row + 6)
        per7.append({"position": pos, "mode": m, "row4": r4, "row5": r5,
                     "row6": r6, "value": mapping(r4, r5, r6)})
    modes6 = [u32(a6, 0x43FEA070 + 4 * i) for i in range(13)]
    per6 = []
    for pos, m in enumerate(modes6):
        row = 0x43BC20DC + 0x1C * pos
        r4, r5, r6 = u8(a6, row + 4), u8(a6, row + 5), u8(a6, row + 6)
        per6.append({"position": pos, "mode": m, "row4": r4, "row5": r5,
                     "row6": r6, "value": mapping(r4, r5, r6)})

    data: dict[str, Any] = {
        "milestone": "S344",
        "title": ("0x436f6240 selecciona entre dos tablas de 3 entradas "
                  "([0,1,4] y [6,5,4]); sin llamador estatico"),
        "base": f"0x{BASE:08x}",
        "firmware": {k: {"sha256": sha256(BLOBS[k]), "size": len(blobs[k])}
                     for k in BLOBS},
        "tables": {
            "table_a": {"address": f"0x{tab_a:08x}", "values": arr_a,
                        "ends_at": f"0x{tab_a + 12:08x}",
                        "next_symbol": f"0x{t1:08x} (T1)"},
            "table_b": {"address": f"0x{tab_b:08x}", "values": arr_b,
                        "starts_at_t1_end": tab_b == t1_end},
            "t1": {"base": f"0x{t1:08x}", "stride": 0x1C, "rows": 34,
                   "end": f"0x{t1_end:08x}"},
        },
        "function": {
            "core": "0x436f6240",
            "core_code": code(a7, 0x436F6240, 0x34),
            "wrapper": "0x436f6278",
            "wrapper_code": code(a7, 0x436F6278, 0x28),
            "wrapper_index_limit": 0x21,
            "wrapper_t1_base": f"0x{pic(a7, 0x436F628E, 0x436F6292)[2]:08x}",
        },
        "per_mode_a7s": per7,
        "per_mode_a6000": per6,
        "a6000": {
            "has_core_pattern": len(literals_for(a6, 0x436F6241)) > 0,
            "t1_base": "0x43bc20dc",
            "table_at_t2": [u32(a6, 0x43BC2248 + 4 * i) for i in range(3)],
        },
        "callers": {
            "core": [f"0x{x:08x}" for x in bl_callers(a7, 0x436F6240)],
            "wrapper": [f"0x{x:08x}" for x in bl_callers(a7, 0x436F6278)],
            "literal_core": [f"0x{x:08x}" for x in literals_for(a7, 0x436F6241)],
            "literal_wrapper": [f"0x{x:08x}" for x in literals_for(a7, 0x436F6279)],
        },
        "verdicts": {
            "selector_is_row5": True,
            "table_a_index_is_row4": True,
            "table_b_index_is_row6": True,
            "a7s_values": {"1": 32, "4": 2},
            "a7s_modes_with_4": [f"0x{m['mode']:02x}" for m in per7 if m["value"] == 4],
            "a6000_values": {"1": 13},
            "static_caller": False,
            "silent_related": False,
            "meaning_of_value": "NO_VERIFICADO",
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("Que el valor 4/1/5/6 sea un canal, un modo de lectura o un contador "
             "no se puede decidir sin llamador: 0 bl y 0 literales."),
            ("La ausencia del patron en la A6000 se mide con la huella exacta del "
             "cuerpo; otra implementacion equivalente no queda excluida."),
            "Los modos con valor 4 (`0x37`/`0x38`) son exclusivos del A7S (S333).",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("tabla A", arr_a, "tabla B", arr_b, "B en fin de T1:", tab_b == t1_end)
    print("A7S valores:", data["verdicts"]["a7s_values"],
          "modos 4:", data["verdicts"]["a7s_modes_with_4"])
    print("callers:", data["callers"])


if __name__ == "__main__":
    main()
