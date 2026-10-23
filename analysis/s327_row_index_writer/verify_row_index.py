#!/usr/bin/env python3
"""S327 - verificador independiente de row_index_writer.json."""
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
JSON = Path(__file__).with_name("row_index_writer.json")

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


def main() -> None:
    d = json.loads(JSON.read_text(encoding="utf-8"))
    a7s = A7S.read_bytes()
    A6000.read_bytes()

    ok(sha256(A7S) == d["firmware"]["a7s_fw320"]["sha256"], "sha256 A7S")
    ok(sha256(A6000) == d["firmware"]["a6000_fw321"]["sha256"], "sha256 A6000")

    # --- exactamente dos escritores --------------------------------------
    ok(len(d["stores"]) == d["store_count"] == 2, "dos escritores")
    ok([s["address"] for s in d["stores"]] == ["0x436f2d74", "0x436f40fe"],
       "direcciones de los escritores")
    ok([s["insn"] for s in d["stores"]] == ["str.w r3, [r4, #0x2b4]",
                                           "str.w r6, [r4, #0x2b4]"], "instrucciones")
    # codificacion de un str.w con #0x2b4
    ok(u16(a7s, 0x436F40FE) == 0xF8C4 and u16(a7s, 0x436F4100) == 0x62B4,
       "bytes de str.w r6,[r4,#0x2b4]")

    # --- constructor parametrico -----------------------------------------
    entry = {i["address"]: i["insn"] for i in d["parametric_ctor"]["entry"]}
    ok(entry["0x436f3fc0"] == "push {r4, r5, r6, r7, lr}", "prologo")
    ok(entry["0x436f3fc6"] == "mov r4, r0", "obj en r4")
    ok(entry["0x436f3fc8"] == "mov r6, r1", "idx en r6")
    tail = {i["address"]: i["insn"] for i in d["parametric_ctor"]["tail"]}
    ok(tail["0x436f40fe"] == "str.w r6, [r4, #0x2b4]", "guarda r6 (idx)")
    ok(d["parametric_ctor"]["idx_register"] == "r6 = r1", "registro declarado")

    # --- constructor base: cero ------------------------------------------
    base = {i["address"]: i["insn"] for i in d["base_ctor_zero_init"]["instructions"]}
    ok(base["0x436f2d62"] == "movs r3, #0", "r3 = 0 antes del store")
    ok(base["0x436f2d74"] == "str.w r3, [r4, #0x2b4]", "init a cero")

    # --- llamador con idx = 0 --------------------------------------------
    call = {i["address"]: i["insn"] for i in d["caller"]["instructions"]}
    ok(call["0x436f2a7e"] == "movs r1, #0", "idx = 0")
    ok(call["0x436f2a8a"] == "bl #0x436f3fc0", "llamada al ctor")
    ok(d["caller"]["idx_value"] == 0, "idx declarado")

    # --- lectores ---------------------------------------------------------
    ok(len(d["loads"]) == d["load_count"] == 9, "9 lectores de campo")
    ok(all("[pc" not in x["insn"] for x in d["loads"]), "ninguno pc-relativo")
    ok(all(x["insn"].startswith("ldr") for x in d["loads"]), "todos lecturas")

    # --- veredicto --------------------------------------------------------
    v = d["verdict"]
    ok(v["rows_reached"] == [0], "solo fila 0")
    ok(v["silent_rows_29_30_reachable"] is False, "filas silent no alcanzadas")
    ok("NO_VERIFICADO" in v["s326_row_mode_mapping"], "S326 sin soporte")
    ok(any("dinamica" in x for x in d["scope_limit"]), "limite de invocacion dinamica")
    ok(any("S51" in x for x in d["scope_limit"]), "limite S51")

    print(f"OK S327: {checks} comprobaciones")


if __name__ == "__main__":
    main()
