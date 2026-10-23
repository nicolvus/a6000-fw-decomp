#!/usr/bin/env python3
"""S337 - carril B: que es `0x43fef404` (candidato estricto del barrido de S329).

S329 lo marco como el unico array de 69 elementos con pinta de tiempo.  La
re-decodificacion muestra que **no** es `u16[69]`: es una tabla de pares
`{u16 codigo, u16 0x000d}` que empieza en `0x43fef404`, precedida de una ristra
de 32 bits constante `0x43f9c622`.  El «array de 69» era una ventana que cruzaba
las dos estructuras.

No hay ninguna referencia literal a `0x43fef404` en el blob (0 aciertos) ni
base PIC calculada hacia ella: no tiene consumidor estatico.

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
OUT = Path(__file__).with_name("fef404_table.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

TABLE = 0x43FEF404
SECOND = 0x000D


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


def main() -> None:
    blob = A7S.read_bytes()

    entries: list[dict[str, Any]] = []
    addr = TABLE
    while True:
        code = u16(blob, addr)
        second = u16(blob, addr + 2)
        if second != SECOND:
            break
        entries.append({"addr": f"0x{addr:08x}", "code": code, "second": second})
        addr += 4

    # ristra de 32 bits constante antes de la tabla
    prefix: list[str] = []
    back = TABLE - 4
    while back >= TABLE - 0x800 and u32(blob, back) == 0x43F9C622:
        prefix.append(f"0x{back:08x}")
        back -= 4

    hits = []
    pat = struct.pack("<I", TABLE)
    i = blob.find(pat)
    while i >= 0:
        hits.append(f"0x{BASE + i:08x}")
        i = blob.find(pat, i + 1)

    data: dict[str, Any] = {
        "milestone": "S337",
        "title": "0x43fef404 no es u16[69]: es una tabla de pares "
                 "{u16 codigo, u16 0x000d} sin consumidor estatico",
        "base": f"0x{BASE:08x}",
        "firmware": {"a7s_fw320": {"sha256": sha256(A7S), "size": len(blob)}},
        "table": {"address": f"0x{TABLE:08x}",
                  "entry_size": 4,
                  "entries": len(entries),
                  "second_field": f"0x{SECOND:04x}",
                  "all_second_equal": all(e["second"] == SECOND for e in entries),
                  "codes": [e["code"] for e in entries],
                  "codes_range": [min(e["code"] for e in entries),
                                  max(e["code"] for e in entries)],
                  "end": f"0x{addr:08x}"},
        "prefix_43f9c622": {"count": len(prefix), "start": prefix[-1] if prefix else None},
        "literal_references": hits,
        "verdicts": {
            "is_u16_69_timing_table": False,
            "entry_shape": "{u16 codigo, u16 0x000d}",
            "static_consumer": False,
            "s329_candidate": "falso positivo (ventana cruzada)",
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("Una lista vacia de referencias no prueba ausencia de uso indirecto: "
             "el consumidor podria llegar por un puntero calculado."),
            "No se asigna significado al campo 0x000d ni a los codigos.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("entradas", len(entries), "codigos", hex(min(e['code'] for e in entries)),
          "..", hex(max(e['code'] for e in entries)))
    print("prefijo 0x43f9c622:", len(prefix), "refs:", hits)


if __name__ == "__main__":
    main()
