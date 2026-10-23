#!/usr/bin/env python3
"""S324 - verificador independiente de columns_audit.json (re-decodificado desde bytes)."""
from __future__ import annotations

import hashlib
import itertools
import json
import struct
from pathlib import Path

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
JSON = Path(__file__).with_name("columns_audit.json")
MATRIX = Path(__file__).resolve().parents[1] / "s321_matrix_rows/matrix_rows.json"

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


def u16(b: bytes, a: int) -> int:
    return struct.unpack_from("<H", b, a - BASE)[0]


def u32(b: bytes, a: int) -> int:
    return struct.unpack_from("<I", b, a - BASE)[0]


def raw(b: bytes, a: int, n: int) -> bytes:
    return b[a - BASE:a - BASE + n]


def main() -> None:
    d = json.loads(JSON.read_text(encoding="utf-8"))
    a7s = A7S.read_bytes()
    a6 = A6000.read_bytes()

    ok(sha256(A7S) == d["firmware"]["a7s_fw320"]["sha256"], "sha256 A7S")
    ok(sha256(A6000) == d["firmware"]["a6000_fw321"]["sha256"], "sha256 A6000")

    # --- u32[34] ----------------------------------------------------------
    ma = d["mode_array"]
    codes = [u32(a7s, 0x43FEE370 + 4 * i) for i in range(34)]
    ok(ma["addr"] == "0x43fee370" and ma["kind"] == "u32[34]", "direccion y tipo")
    ok(ma["bytes"] == 136 and ma["end"] == "0x43fee3f8", "136 B hasta L95")
    ok(codes == [int(c, 16) for c in ma["codes"]], "34 codigos re-decodificados")
    ok(all(c < 0x100 for c in codes) and ma["high_bytes_all_zero"], "bytes altos a cero")
    ok(u32(a7s, 0x43FEE3F8) != 0, "0x43fee3f8 ya es L95 (puntero no nulo)")
    ok(codes[27] == 0x4C and codes[28] == 0x4D and codes[29] == 0x4E and
       codes[30] == 0x4F, "posiciones 27..30 = 0x4c..0x4f")
    ok(ma["index_of_0x4e"] == 29 and ma["index_of_0x4f"] == 30, "indices 29/30")
    ok(ma["index_of_0x4c"] == 27 and ma["index_of_0x4d"] == 28, "indices 27/28")
    ok(ma["literal_refs"] == ["lit@0x44027230"], "unico literal = su slot")
    ok(u32(a7s, 0x44027230) == 0x43FEE370, "slot 0x44027230 -> array")
    ok(d["slot"]["value"] == "0x43fee370", "valor del slot en el JSON")

    # --- offset 0x2cf0 ----------------------------------------------------
    sl = d["slot"]
    ok(sl["slot_base"] == "0x44024540" and sl["offset_le"] == "0x2cf0", "base y offset")
    ok(0x44024540 + 0x2CF0 == 0x44027230, "base + offset = slot")
    ok(set(sl["offset_le_sites"]) >= {"0x436f39b4", "0x436f3b12", "0x436f3bb4",
                                      "0x436f403a", "0x436f4468"},
       "los 5 sitios de la clase estan")
    for site in sl["offset_le_sites"]:
        a = int(site, 16)
        h = u16(a7s, a)
        ok((h & 0xF800) == 0x4800, f"{site} es ldr pc-rel")
        lit = ((a + 4) & ~3) + (h & 0xFF) * 4
        ok(u32(a7s, lit) == 0x2CF0, f"{site} carga 0x2cf0")

    # --- setter A7S -------------------------------------------------------
    sa = d["setter_a7s"]
    ok(u32(a7s, 0x43FCE050 + 32) == 0x436F3B45 and sa["vtable_slot"] == 8, "slot 8 A7S")
    ins = {i["address"]: i["insn"] for i in sa["instructions"]}
    ok(ins["0x436f3b54"] == "cmp r3, #0x51", "limite 0x51")
    ok(ins["0x436f3b5a"] == "str.w r3, [r0, #0x1ac]", "modo en +0x1ac")
    ok(ins["0x436f3b62"] == "strb.w r1, [r0, #0x2b0]", "sub en +0x2b0")
    ok(ins["0x436f3b60"] == "cmp r1, #1", "sub <= 1")
    ok(sa["mode_max"] == 0x51 and sa["sub_max"] == 1, "cotas del setter A7S")

    # --- setter A6000 -----------------------------------------------------
    sb = d["setter_a6000"]
    ok(u32(a6, 0x43FCC090 + 32) == 0x436D6B51 and sb["vtable_slot"] == 8, "slot 8 A6000")
    ins6 = {i["address"]: i["insn"] for i in sb["instructions"]}
    ok(ins6["0x436d6b62"] == "cmp r2, #0x47", "limite 0x47")
    ok(ins6["0x436d6b68"] == "str.w r2, [r0, #0x170]", "modo en +0x170")
    ok(ins6["0x436d6b70"] == "strb.w r1, [r0, #0x266]", "sub en +0x266")
    ok(sb["mode_max"] == 0x47, "A6000 rechaza 0x4e/0x4f")

    # --- censo de columnas (recalculado desde S321) -----------------------
    m = json.loads(MATRIX.read_text(encoding="utf-8"))
    rows = m["matrix_a7s"]["rows_detail"]
    regs = [r["reg"] for r in rows]
    vals = [[int(r["payload_hex"][2 * i:2 * i + 2], 16) for i in range(16)]
            for r in rows]
    counts = []
    for a, b in itertools.combinations(range(15), 2):
        counts.append(sum(1 for i in range(len(rows)) if vals[i][a] != vals[i][b]))
    cc = d["column_census"]
    ok(len(counts) == cc["pairs"] == 105, "105 pares de columnas")
    ok(min(counts) == cc["min_count"] == 2, "diferencia minima = 2 registros")
    ok(sum(1 for c in counts if c == 1) == cc["pairs_with_one_diff"] == 0,
       "ningun par difiere en un solo registro")
    ok(cc["min_pair"]["cols"] == [7, 9], "par minimo = columnas 7 y 9")
    ok([x["reg"] for x in cc["min_pair"]["diffs"]] == [0x00, 0x0E],
       "registros del par minimo (0x00 y 0x0e)")
    ok(len(regs) == cc["registers"] == 69, "69 registros escritos por aplicacion")
    ok(sorted((tuple(p["cols"]), p["count"]) for p in cc["all_pairs"]) ==
       sorted((pair, c) for pair, c in zip(itertools.combinations(range(15), 2),
                                           counts)), "tabla de pares (105)")

    # --- conclusiones -----------------------------------------------------
    ok(d["column_claim_s204"]["claimed_silent_columns"] == [29, 30], "S204: 29/30")
    ok(d["column_claim_s204"]["reproducible_with_this_matrix"] is False,
       "S204 no reproducible con esta matriz")
    ok(d["verdict"]["a6000_rejects_0x4e_0x4f"].startswith("VERIFICADO"), "veredicto A6000")
    ok("NO_VERIFICADO" in d["verdict"]["s204_34_columns"], "veredicto 34 columnas")
    ok(any("34 columnas" in x for x in d["scope_limit"]), "limite declarado")

    print(f"OK S324: {checks} comprobaciones")


if __name__ == "__main__":
    main()
