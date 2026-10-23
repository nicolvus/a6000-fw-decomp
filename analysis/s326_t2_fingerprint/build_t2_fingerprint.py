#!/usr/bin/env python3
"""S326 - carril B: la tabla T2 (34 filas, una por modo) y la huella de 0x4e/0x4f.

S202/S204 describian una tabla de **34 columnas** con `0x4e`/`0x4f` en las posiciones
29/30 y una diferencia de **un registro** frente a `0x4c`/`0x4d`. S324 no la encontro
porque busco una tabla de 34 *columnas*; S317 ya habia medido tres tablas paralelas de
**34 filas** y stride `0x1c` indexadas por `obj+0x2b4`.

Esta sesion compara esas tres tablas (T1 `0x43bbeb70`, T3 `0x43bbef34`, T2 `0x43bbf2ec`)
fila a fila en el rango 27..32, usando el orden del array `u32[34]` de `0x43fee370`
(27..32 = `0x4c,0x4d,0x4e,0x4f,0x50,0x51`):

* **T2** es la unica que discrimina: `0x4c`/`0x4d` llevan `+0x14 = 0x3ff`; `0x4e` y `0x4f`
  llevan `+0x14 = 0` (un solo campo de diferencia) y `0x4f` sube `+0x18` de 2 a 3.
* `0x4e` es identico a `0x51` y `0x4f` a `0x50` (pares exactos).
* T1 y T3 son constantes en ese rango salvo `T1+0x00`, que vale 0 para `0x4c..0x4f` y 1
  para `0x50`/`0x51`.

No ejecuta firmware ni toca la camara: solo lectura de los blobs.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("t2_silent_fingerprint.json")

MODE_ARRAY = 0x43FEE370
TABLES = {"T1": 0x43BBEB70, "T3": 0x43BBEF34, "T2": 0x43BBF2EC}
STRIDE = 0x1C
FIELDS = 7
ROWS = 34
SILENT = [0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u32(blob: bytes, a: int) -> int:
    return struct.unpack_from("<I", blob, a - BASE)[0]


def row(blob: bytes, base: int, index: int) -> list[int]:
    return [u32(blob, base + STRIDE * index + 4 * j) for j in range(FIELDS)]


def compare(a: list[int], b: list[int]) -> list[dict]:
    return [{"field": j, "offset": f"+0x{4 * j:02x}", "a": a[j], "b": b[j]}
            for j in range(FIELDS) if a[j] != b[j]]


def main() -> None:
    a7s = A7S.read_bytes()
    a6 = A6000.read_bytes()
    codes = [u32(a7s, MODE_ARRAY + 4 * i) for i in range(ROWS)]
    pos = {c: i for i, c in enumerate(codes)}

    tables: dict[str, Any] = {}
    for name, base in TABLES.items():
        rows = [row(a7s, base, i) for i in range(ROWS)]
        tables[name] = {
            "base": f"0x{base:08x}",
            "stride": STRIDE,
            "rows": ROWS,
            "fields": FIELDS,
            "silent_rows": {f"0x{codes[i]:02x}": {"position": i,
                                                 "fields": [f"0x{x:08x}" for x in rows[i]]}
                            for i in range(26, 34)},
            "distinct_rows_in_26_33": len({tuple(r) for r in rows[26:34]}),
        }

    t2 = [row(a7s, TABLES["T2"], i) for i in range(ROWS)]
    f14 = [t2[i][5] for i in range(ROWS)]
    f18 = [t2[i][6] for i in range(ROWS)]

    def at(code: int) -> list[int]:
        return t2[pos[code]]

    cmp_4e_4c = compare(at(0x4E), at(0x4C))
    cmp_4f_4d = compare(at(0x4F), at(0x4D))
    cmp_4e_4f = compare(at(0x4E), at(0x4F))
    pairs = {
        "0x4e==0x51": at(0x4E) == at(0x51),
        "0x4f==0x50": at(0x4F) == at(0x50),
        "0x4c==0x4d": at(0x4C) == at(0x4D),
    }

    data: dict[str, Any] = {
        "milestone": "S326",
        "title": "T2 tiene 34 filas (una por modo) y es la unica que separa 0x4e/0x4f "
                 "de 0x4c/0x4d",
        "base": f"0x{BASE:08x}",
        "firmware": {
            "a7s_fw320": {"sha256": sha256(A7S), "size": len(a7s)},
            "a6000_fw321": {"sha256": sha256(A6000), "size": len(a6)},
        },
        "mode_order": [f"0x{c:02x}" for c in codes],
        "tables": tables,
        "t2_signature": {
            "field14_values": sorted(set(f14)),
            "field18_values": sorted(set(f18)),
            "field14_0x3ff_rows": [f"0x{codes[i]:02x}" for i in range(ROWS) if f14[i] == 0x3FF],
            "field14_zero_rows": [f"0x{codes[i]:02x}" for i in range(ROWS) if f14[i] == 0],
            "field18_3_rows": [f"0x{codes[i]:02x}" for i in range(ROWS) if f18[i] == 3],
        },
        "comparisons": {
            "0x4e_vs_0x4c": {"count": len(cmp_4e_4c), "diffs": cmp_4e_4c},
            "0x4f_vs_0x4d": {"count": len(cmp_4f_4d), "diffs": cmp_4f_4d},
            "0x4e_vs_0x4f": {"count": len(cmp_4e_4f), "diffs": cmp_4e_4f},
            "identical_pairs": pairs,
        },
        "s204_verdict": {
            "structure_reproduced": True,
            "one_field_for_0x4e": len(cmp_4e_4c) == 1,
            "one_field_for_0x4f": len(cmp_4f_4d) == 1,
            "numeric_labels_match": False,
            "note": "S204 da '1 registro (0x000c/0x000a)'; aqui el campo es +0x14 "
                    "(0x3ff -> 0) y, para 0x4f, tambien +0x18 (2 -> 3). La estructura "
                    "'minima diferencia' se reproduce; las etiquetas numericas no.",
            "table_identity": "T2 = 0x43bbf2ec, ya medida por S317 como tabla indexada "
                              "por obj+0x2b4 (34 filas, stride 0x1c)",
        },
        "scope_limit": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("Que el indice de fila sea la POSICION en 0x43fee370 es INFERENCIA: se apoya "
             "en las 34 filas de S317, en el orden de los codigos y en que reproduce la "
             "observacion independiente de S204."),
            "No se atribuye significado a los campos +0x14 (0x3ff/0) ni +0x18 (2/3).",
            "No se ha localizado el escritor de obj+0x2b4.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"escrito {OUT.name}: 0x4e vs 0x4c={len(cmp_4e_4c)} campo(s), "
          f"0x4f vs 0x4d={len(cmp_4f_4d)}, pares={pairs}")


if __name__ == "__main__":
    main()
