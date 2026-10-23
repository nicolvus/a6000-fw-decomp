#!/usr/bin/env python3
"""S325 - carril B: el mapa de columnas se indexa por POSICION, no por codigo de modo.

S302/S321 leyeron `0x43c9c5b5` como un mapa `modo -> columna` de 82 entradas y
concluyeron que `0x4e`/`0x4f` caen en la columna 1 (la misma que `0x4c`/`0x4d`),
por lo que la matriz no distinguiria el modo silent.

La re-decodificacion desde bytes muestra otra cosa:

1. El ayudante `0x43ada284` es una **busqueda lineal** sobre un array de `u32`:
   devuelve el **indice** del valor buscado (`0..r3-1`) o `0xff`.
2. En el setter de modo (`0x436f3b44`) el valor buscado (`0x44`) se busca en el
   array `u32[34]` de `0x43fee370`, y el **indice devuelto** (`0..33`) se pasa
   como `r1` al accesor de la matriz (slot 40), que hace `ldrb r1,[mapa,r1]`.
3. Por tanto el mapa es `posicion -> columna` y solo tiene **34 entradas**
   (todas `<= 14`); los 48 bytes siguientes pertenecen a otra tabla (periodica
   de 10: 7 unos + 3 ceros).
4. Consecuencia: `0x4e` (posicion 29) -> columna **12** y `0x4f` (posicion 30) ->
   columna **13**, mientras que `0x4c`/`0x4d` (27/28) -> columna **5**. La matriz
   **si** distingue el modo silent; difiere de `0x4c`/`0x4d` en 14 y 11 registros.
   `0x50`/`0x51` (31/32) comparten columnas con `0x4e`/`0x4f`.

No ejecuta firmware ni toca la camara: solo lectura de los blobs.
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
MATRIX = Path(__file__).resolve().parents[1] / "s321_matrix_rows/matrix_rows.json"
OUT = Path(__file__).with_name("position_map.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

HELPER = 0x43ADA284
MODE_ARRAY = 0x43FEE370
MAP = 0x43C9C5B5
ACCESSOR = 0x436F3928
SETTER = 0x436F3B44


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


def main() -> None:
    a7s = A7S.read_bytes()
    a6 = A6000.read_bytes()

    codes = [u32(a7s, MODE_ARRAY + 4 * i) for i in range(34)]
    map34 = list(raw(a7s, MAP, 34))
    tail = list(raw(a7s, MAP + 34, 48))

    rows = json.loads(MATRIX.read_text(encoding="utf-8"))["matrix_a7s"]["rows_detail"]
    regs = [r["reg"] for r in rows]
    vals = [[int(r["payload_hex"][2 * i:2 * i + 2], 16) for i in range(16)]
            for r in rows]

    def diff(a: int, b: int) -> list[dict]:
        return [{"row": i, "reg": regs[i], "a": vals[i][a], "b": vals[i][b]}
                for i in range(len(rows)) if vals[i][a] != vals[i][b]]

    mapping = [{"position": i, "code": f"0x{c:02x}", "column": map34[i]}
               for i, c in enumerate(codes)]
    pos_of = {c: i for i, c in enumerate(codes)}

    def by_code(code: int) -> dict:
        p = pos_of[code]
        return {"code": f"0x{code:02x}", "position": p, "column": map34[p]}

    silent = {
        "0x4c": by_code(0x4C), "0x4d": by_code(0x4D),
        "0x4e": by_code(0x4E), "0x4f": by_code(0x4F),
        "0x50": by_code(0x50), "0x51": by_code(0x51),
    }
    c4e = diff(map34[pos_of[0x4E]], map34[pos_of[0x4C]])
    c4f = diff(map34[pos_of[0x4F]], map34[pos_of[0x4D]])

    data: dict[str, Any] = {
        "milestone": "S325",
        "title": "El mapa de columnas 0x43c9c5b5 se indexa por posicion (34 entradas), "
                 "no por codigo de modo: 0x4e -> columna 12 y 0x4f -> 13",
        "base": f"0x{BASE:08x}",
        "firmware": {
            "a7s_fw320": {"sha256": sha256(A7S), "size": len(a7s)},
            "a6000_fw321": {"sha256": sha256(A6000), "size": len(a6)},
        },
        "helper": {
            "function": f"0x{HELPER:08x}",
            "instructions": dis(a7s, HELPER, 0x1C),
            "semantics": "busqueda lineal sobre u32[]: devuelve indice (0..r3-1) o 0xff",
            "returns_index": True,
        },
        "mode_array": {"addr": f"0x{MODE_ARRAY:08x}", "count": 34,
                       "codes": [f"0x{c:02x}" for c in codes]},
        "map": {
            "addr": f"0x{MAP:08x}",
            "entries_used": 34,
            "values": map34,
            "all_le_14": all(v <= 14 for v in map34),
            "tail_48_not_part_of_map": tail,
            "tail_is_periodic": tail[:10] == tail[10:20],
            "tail_period": 10,
        },
        "call_chain": {
            "setter": f"0x{SETTER:08x}",
            "instructions": dis(a7s, 0x436F3BA8, 0x30),
            "key_looked_up": 0x44,
            "count_register": 0x22,
            "index_stored_at": "+0x1b8",
            "index_passed_as_r1_to_slot40": True,
        },
        "accessor": {
            "function": f"0x{ACCESSOR:08x}",
            "map_load": "ldrb r1,[r2,r1] con r2=0x43c9c5b5",
            "column_source": "r1 = posicion (0..33)",
        },
        "mapping": mapping,
        "silent": silent,
        "diffs_vs_mechanical": {
            "0x4e_vs_0x4c": {"count": len(c4e), "regs": [f"0x{x['reg']:02x}" for x in c4e],
                             "detail": c4e},
            "0x4f_vs_0x4d": {"count": len(c4f), "regs": [f"0x{x['reg']:02x}" for x in c4f],
                             "detail": c4f},
            "0x4e_vs_0x4f": {"count": len(diff(map34[pos_of[0x4E]], map34[pos_of[0x4F]]))},
        },
        "pairs_share_column": {
            "col12_positions": [i for i, v in enumerate(map34) if v == 12],
            "col13_positions": [i for i, v in enumerate(map34) if v == 13],
        },
        "corrections": [
            {"supersedes": "S321 §4 y S302 §3 (mapa modo->columna)",
             "correct": "el mapa es posicion->columna con 34 entradas; 0x4e/0x4f usan "
                        "las columnas 12/13, no la 1"},
            {"supersedes": "S321 (no hay columna que distinga silent)",
             "correct": "las columnas 12/13 son distintas de la 5 de 0x4c/0x4d; la "
                        "matriz SI distingue el modo silent (14 y 11 registros)"},
            {"kept": "S321 (recuento 69 filas, destino de escritura, pool de 98 "
                     "registros, A6000 sin mapa) sigue vigente"},
        ],
        "scope_limit": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("No se atribuye significado fisico a los registros ni a sus valores; solo se "
             "constata que difieren."),
            ("No se verifica que la ruta del setter sea la unica que aplica la matriz: hay "
             "otros llamadores del slot 40 no atribuidos."),
            "La tabla de 34 columnas de S202/S204 sigue NO_VERIFICADA.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"escrito {OUT.name}: 0x4e->col {map34[pos_of[0x4E]]}, 0x4f->col "
          f"{map34[pos_of[0x4F]]}, 0x4c/0x4d->col {map34[pos_of[0x4C]]}; "
          f"diffs {len(c4e)}/{len(c4f)}")


if __name__ == "__main__":
    main()
