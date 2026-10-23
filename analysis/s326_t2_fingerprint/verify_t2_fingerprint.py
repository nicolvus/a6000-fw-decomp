#!/usr/bin/env python3
"""S326 - verificador independiente de t2_silent_fingerprint.json."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
JSON = Path(__file__).with_name("t2_silent_fingerprint.json")

checks = 0


def ok(cond: bool, msg: str) -> None:
    global checks
    if not cond:
        raise SystemExit(f"FALLO: {msg}")
    checks += 1


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def u32(b: bytes, a: int) -> int:
    return struct.unpack_from("<I", b, a - BASE)[0]


def main() -> None:
    d = json.loads(JSON.read_text(encoding="utf-8"))
    a7s = A7S.read_bytes()
    A6000.read_bytes()

    ok(sha256(A7S) == d["firmware"]["a7s_fw320"]["sha256"], "sha256 A7S")
    ok(sha256(A6000) == d["firmware"]["a6000_fw321"]["sha256"], "sha256 A6000")

    codes = [u32(a7s, 0x43FEE370 + 4 * i) for i in range(34)]
    ok([f"0x{c:02x}" for c in codes] == d["mode_order"], "orden de 34 modos")
    ok(codes[27:33] == [0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51], "27..32 = 0x4c..0x51")

    tables = {"T1": 0x43BBEB70, "T3": 0x43BBEF34, "T2": 0x43BBF2EC}
    for name, base in tables.items():
        ok(d["tables"][name]["base"] == f"0x{base:08x}", f"base {name}")
        rows = [[u32(a7s, base + 0x1C * i + 4 * j) for j in range(7)]
                for i in range(34)]
        for code in (0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51):
            p = codes.index(code)
            ok(d["tables"][name]["silent_rows"][f"0x{code:02x}"]["fields"] ==
               [f"0x{x:08x}" for x in rows[p]], f"{name} fila 0x{code:02x}")
        ok(d["tables"][name]["distinct_rows_in_26_33"] ==
           len({tuple(r) for r in rows[26:34]}), f"{name}: filas distintas 26..33")

    t2 = [[u32(a7s, 0x43BBF2EC + 0x1C * i + 4 * j) for j in range(7)] for i in range(34)]

    def at(code: int) -> list[int]:
        return t2[codes.index(code)]

    cmp_4e_4c = [j for j in range(7) if at(0x4E)[j] != at(0x4C)[j]]
    cmp_4f_4d = [j for j in range(7) if at(0x4F)[j] != at(0x4D)[j]]
    cmp_4e_4f = [j for j in range(7) if at(0x4E)[j] != at(0x4F)[j]]
    ok(cmp_4e_4c == [5], "0x4e vs 0x4c: solo +0x14")
    ok(cmp_4f_4d == [5, 6], "0x4f vs 0x4d: +0x14 y +0x18")
    ok(cmp_4e_4f == [6], "0x4e vs 0x4f: solo +0x18")
    ok((at(0x4C)[5], at(0x4E)[5]) == (0x3FF, 0), "0x3ff -> 0")
    ok((at(0x4D)[6], at(0x4F)[6]) == (2, 3), "2 -> 3")
    ok(at(0x4E) == at(0x51) and at(0x4F) == at(0x50) and at(0x4C) == at(0x4D),
       "pares identicos 0x4e/0x51, 0x4f/0x50, 0x4c/0x4d")
    ok(d["comparisons"]["identical_pairs"] ==
       {"0x4e==0x51": True, "0x4f==0x50": True, "0x4c==0x4d": True}, "pares en el JSON")

    f14 = [t2[i][5] for i in range(34)]
    f18 = [t2[i][6] for i in range(34)]
    ok(sorted(set(f14)) == [0, 0x3FF] == d["t2_signature"]["field14_values"],
       "solo dos valores en +0x14")
    ok(sorted(set(f18)) == [2, 3] == d["t2_signature"]["field18_values"],
       "solo dos valores en +0x18")
    ok(d["t2_signature"]["field14_0x3ff_rows"] ==
       [f"0x{codes[i]:02x}" for i in range(34) if f14[i] == 0x3FF],
       "filas con 0x3ff")
    ok(d["t2_signature"]["field14_0x3ff_rows"] == ["0x13", "0x1f", "0x4c", "0x4d"],
       "0x3ff solo en {0x13,0x1f,0x4c,0x4d}")
    ok(d["t2_signature"]["field18_3_rows"] ==
       [f"0x{codes[i]:02x}" for i in range(34) if f18[i] == 3], "filas con 3")
    ok(d["t2_signature"]["field18_3_rows"] == ["0x0b", "0x35", "0x4f", "0x50"],
       "3 solo en {0x0b,0x35,0x4f,0x50}")

    ok(d["s204_verdict"]["structure_reproduced"] is True, "S204: estructura")
    ok(d["s204_verdict"]["numeric_labels_match"] is False, "S204: etiquetas no")
    ok(any("INFERENCIA" in x for x in d["scope_limit"]), "limite de inferencia")
    ok(any("S51" in x for x in d["scope_limit"]), "limite S51")

    print(f"OK S326: {checks} comprobaciones")


if __name__ == "__main__":
    main()
