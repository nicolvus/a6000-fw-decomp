#!/usr/bin/env python3
"""S333 - carril B: vocabulario de modos A6000 vs A7S y columnas de sus matrices.

La cola pedia contrastar el vocabulario: la A6000 acepta hasta `0x47` con **13**
codigos y el A7S hasta `0x51` con **34**.  Aqui se mide ademas cuantas
configuraciones de registro **distintas** produce cada vocabulario:

* A6000: matriz `0x43fe9b74`, 59 filas de `0x14` B `{u32 dest; u8 v[16]}`; el
  setter pasa la **posicion del modo** como offset de columna (0..12), asi que
  la columna es el modo, sin mapa intermedio.
* A7S: matriz `0x43fee598`, 69 filas; el mapa `0x43c9c5b5` traduce posicion a
  columna (0..14) y la 15 no se usa.

Resultado: el vocabulario del A7S produce 15 vectores **todos distintos**; el de
la A6000 produce 13 columnas con solo **7** vectores distintos (alias).

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
OUT = Path(__file__).with_name("mode_vocabulary.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

A6_MATRIX_SLOT = 0x44022F8C
A7_MATRIX = 0x43FEE598
A7_MAP = 0x43C9C5B5
A7_MODE_LIST = 0x43FEE370
A6_MODE_LIST = 0x43FEA070
STRIDE_A6 = 0x14
STRIDE_A7 = 0x14
A6_CODES = [0x0B, 0x01, 0x05, 0x10, 0x07, 0x12, 0x03, 0x0A, 0x0F, 0x18, 0x1A,
            0x19, 0x2F]


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


def matrix(blob: bytes, base: int, limit: int = 200) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for i in range(limit):
        addr = base + STRIDE_A6 * i
        dest = u32(blob, addr)
        if dest == 0:
            return {"base": f"0x{base:08x}", "rows": rows,
                    "terminator": f"0x{addr:08x}", "count": len(rows)}
        rows.append({"dest": f"0x{dest:08x}",
                     "values": list(raw(blob, addr + 4, 16))})
    raise SystemExit("matriz sin terminador")


def columns(mtx: dict[str, Any], codes: list[int],
            colmap: list[int] | None) -> dict[str, Any]:
    if colmap is None:
        cols = {code: i for i, code in enumerate(codes)}
    else:
        cols = {code: colmap[i] for i, code in enumerate(codes)}
    vectors = {f"0x{c:02x}": tuple(r["values"][col] for r in mtx["rows"])
               for c, col in cols.items()}
    by_vec: dict[tuple[int, ...], list[str]] = {}
    for code, vec in vectors.items():
        by_vec.setdefault(vec, []).append(code)
    return {"columns": {f"0x{c:02x}": cols[c] for c in codes},
            "distinct_vectors": len(by_vec),
            "aliases": sorted([sorted(v) for v in by_vec.values() if len(v) > 1]),
            "vector_sha": {code: hashlib.sha256(bytes(v)).hexdigest()[:16]
                           for code, v in vectors.items()}}


def main() -> None:
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()

    a6_slot = u32(a6, A6_MATRIX_SLOT)
    mtx6 = matrix(a6, a6_slot)
    a6_codes = [u32(a6, A6_MODE_LIST + 4 * i) for i in range(len(A6_CODES))]
    assert a6_codes == A6_CODES, a6_codes
    cols6 = columns(mtx6, a6_codes, None)

    a7_codes = [u32(a7, A7_MODE_LIST + 4 * i) for i in range(34)]
    colmap = list(raw(a7, A7_MAP, 34))
    mtx7 = matrix(a7, A7_MATRIX)
    cols7 = columns(mtx7, a7_codes, colmap)

    vocab = {
        "a6000_only": sorted(f"0x{c:02x}" for c in set(a6_codes) - set(a7_codes)),
        "shared": sorted(f"0x{c:02x}" for c in set(a6_codes) & set(a7_codes)),
        "a7s_only": sorted(f"0x{c:02x}" for c in set(a7_codes) - set(a6_codes)),
        "counts": {"a6000": len(a6_codes), "a7s": len(a7_codes),
                   "shared": len(set(a6_codes) & set(a7_codes))},
    }
    silent = {"0x4c", "0x4d", "0x4e", "0x4f", "0x50", "0x51"}
    data: dict[str, Any] = {
        "milestone": "S333",
        "title": "El vocabulario A6000 (13 modos) produce 7 vectores de registro "
                 "distintos; el A7S (34 modos) produce 15",
        "base": f"0x{BASE:08x}",
        "firmware": {"a7s_fw320": {"sha256": sha256(A7S), "size": len(a7)},
                     "a6000_fw321": {"sha256": sha256(A6000), "size": len(a6)}},
        "a6000": {"matrix_slot": f"0x{A6_MATRIX_SLOT:08x}",
                  "matrix": f"0x{a6_slot:08x}",
                  "rows": mtx6["count"], "terminator": mtx6["terminator"],
                  "mode_list": f"0x{A6_MODE_LIST:08x}",
                  "codes": [f"0x{c:02x}" for c in a6_codes],
                  "columns": cols6},
        "a7s": {"matrix": f"0x{A7_MATRIX:08x}", "rows": mtx7["count"],
                "terminator": mtx7["terminator"],
                "mode_list": f"0x{A7_MODE_LIST:08x}",
                "codes": [f"0x{c:02x}" for c in a7_codes],
                "position_map": colmap, "columns": cols7},
        "vocabulary": vocab,
        "verdicts": {
            "a6000_distinct_vectors": cols6["distinct_vectors"],
            "a7s_distinct_vectors": cols7["distinct_vectors"],
            "a6000_column_equals_mode_position": True,
            "a6000_has_silent_codes": bool(silent & {f"0x{c:02x}" for c in a6_codes}),
            "silent_codes_a7s_only": sorted(silent & set(vocab["a7s_only"])),
            "a6000_vocabulary_is_coarse": cols6["distinct_vectors"] < len(a6_codes),
            "a6000_alias_groups": len(cols6["aliases"]),
            "a7s_alias_groups": len(cols7["aliases"]),
            "a7s_silent_aliases": {code: group for group in cols7["aliases"]
                                    for code in group
                                    if code in silent},
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("Que dos modos compartan columna significa que el firmware escribe los "
             "mismos valores de registro en la matriz; no implica que el modo sea "
             "equivalente en todo el pipeline (las tablas T y el resto del flujo "
             "pueden diferenciarlos)."),
            ("Alias medidos: A6000 {0x05,0x07,0x10,0x18,0x19,0x1a} y {0x0b,0x2f}; "
             "A7S 12 grupos, entre ellos {0x4c,0x4d}~{0x32,0x33,0x34}, "
             "{0x4e,0x50} y {0x4f,0x51}."),
            "No se asigna semantica fisica a los registros ni a los vectores.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("A6000 filas", mtx6["count"], "vectores distintos", cols6["distinct_vectors"],
          "alias", cols6["aliases"])
    print("A7S filas", mtx7["count"], "vectores distintos", cols7["distinct_vectors"])
    print("vocabulario", vocab)


if __name__ == "__main__":
    main()
