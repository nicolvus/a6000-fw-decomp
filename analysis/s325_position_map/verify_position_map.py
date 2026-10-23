#!/usr/bin/env python3
"""S325 - verificador independiente de position_map.json (re-decodificado desde bytes)."""
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
JSON = Path(__file__).with_name("position_map.json")
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
    A6000.read_bytes()  # solo se comprueba el sha256

    ok(sha256(A7S) == d["firmware"]["a7s_fw320"]["sha256"], "sha256 A7S")
    ok(sha256(A6000) == d["firmware"]["a6000_fw321"]["sha256"], "sha256 A6000")

    # --- ayudante: busqueda lineal que devuelve indice --------------------
    h = {i["address"]: i["insn"] for i in d["helper"]["instructions"]}
    ok(h["0x43ada28a"] == "ldr r4, [r2], #4", "carga avanzando 4")
    ok(h["0x43ada28e"] == "cmp r1, r4", "compara el valor buscado")
    ok(h["0x43ada292"] == "uxtb r0, r0", "devuelve el indice en r0")
    ok(h["0x43ada296"] == "adds r0, #1", "incrementa indice")
    ok(h["0x43ada298"] == "cmp r0, r3", "limite = r3")
    ok(h["0x43ada29c"] == "movs r0, #0xff", "no encontrado -> 0xff")
    ok(u16(a7s, 0x43ADA28E) == 0x42A1, "bytes cmp r1,r4")
    ok(d["helper"]["returns_index"] is True, "semantica declarada")

    # --- cadena de llamada ------------------------------------------------
    c = {i["address"]: i["insn"] for i in d["call_chain"]["instructions"]}
    ok(c["0x436f3bbe"] == "movs r3, #0x22", "34 entradas")
    ok(c["0x436f3bc0"] == "bl #0x43ada284", "llama al ayudante")
    ok(c["0x436f3bc6"] == "mov r1, r0", "el indice va a r1")
    ok(c["0x436f3bc8"] == "strb.w r0, [r4, #0x1b8]", "indice guardado en +0x1b8")
    ok(c["0x436f3bd2"] == "ldr.w r3, [r3, #0xa0]", "slot 40")
    ok(c["0x436f3bd6"] == "blx r3", "llamada virtual con el indice")
    ok(u32(a7s, 0x43FEE370 + 4 * 22) == 0x0F, "0x0f ocupa la posicion 22")
    # el valor buscado esta en el array
    codes = [u32(a7s, 0x43FEE370 + 4 * i) for i in range(34)]
    ok(0x44 in codes and codes.index(0x44) == 25, "0x44 esta en la posicion 25")

    # --- mapa: 34 entradas, todas <= 14 -----------------------------------
    map34 = list(raw(a7s, 0x43C9C5B5, 34))
    ok(map34 == d["map"]["values"], "34 valores del mapa")
    ok(max(map34) == 14 and all(v <= 14 for v in map34), "todas <= 14")
    tail = list(raw(a7s, 0x43C9C5B5 + 34, 48))
    ok(tail == d["map"]["tail_48_not_part_of_map"], "cola de 48 B")
    ok(tail[:10] == tail[10:20] == tail[20:30] and
       d["map"]["tail_is_periodic"] is True and d["map"]["tail_period"] == 10,
       "la cola es periodica de 10 (otra tabla)")

    # --- mapeo posicion -> codigo -> columna ------------------------------
    ok(d["mapping"] == [{"position": i, "code": f"0x{c:02x}", "column": map34[i]}
                        for i, c in enumerate(codes)], "tabla de mapeo")
    ok([f"0x{c:02x}" for c in codes] == d["mode_array"]["codes"], "34 codigos")
    ok(codes[27] == 0x4C and codes[28] == 0x4D and codes[29] == 0x4E and
       codes[30] == 0x4F and codes[31] == 0x50 and codes[32] == 0x51,
       "posiciones 27..32")

    # --- columnas de silent ----------------------------------------------
    sil = d["silent"]
    ok((sil["0x4c"]["position"], sil["0x4c"]["column"]) == (27, 5), "0x4c -> col 5")
    ok((sil["0x4d"]["position"], sil["0x4d"]["column"]) == (28, 5), "0x4d -> col 5")
    ok((sil["0x4e"]["position"], sil["0x4e"]["column"]) == (29, 12), "0x4e -> col 12")
    ok((sil["0x4f"]["position"], sil["0x4f"]["column"]) == (30, 13), "0x4f -> col 13")
    ok((sil["0x50"]["column"], sil["0x51"]["column"]) == (12, 13),
       "0x50/0x51 comparten 12/13")
    ok(d["pairs_share_column"]["col12_positions"] == [29, 31], "col 12 en 29 y 31")
    ok(d["pairs_share_column"]["col13_positions"] == [30, 32], "col 13 en 30 y 32")

    # --- diferencias de registros ----------------------------------------
    rows = json.loads(MATRIX.read_text(encoding="utf-8"))["matrix_a7s"]["rows_detail"]
    regs = [r["reg"] for r in rows]
    vals = [[int(r["payload_hex"][2 * i:2 * i + 2], 16) for i in range(16)]
            for r in rows]

    def diff(a: int, b: int) -> list[int]:
        return [regs[i] for i in range(len(rows)) if vals[i][a] != vals[i][b]]

    d4e = diff(12, 5)
    d4f = diff(13, 5)
    ok(len(d4e) == d["diffs_vs_mechanical"]["0x4e_vs_0x4c"]["count"] == 14,
       "0x4e vs 0x4c: 14 registros")
    ok(len(d4f) == d["diffs_vs_mechanical"]["0x4f_vs_0x4d"]["count"] == 11,
       "0x4f vs 0x4d: 11 registros")
    ok([f"0x{x:02x}" for x in d4e] == d["diffs_vs_mechanical"]["0x4e_vs_0x4c"]["regs"],
       "lista de registros 0x4e")
    ok([f"0x{x:02x}" for x in d4f] == d["diffs_vs_mechanical"]["0x4f_vs_0x4d"]["regs"],
       "lista de registros 0x4f")
    ok(0x0C in d4e and 0x0A in d4e and 0x0C in d4f and 0x0A in d4f,
       "0x0c y 0x0a estan entre las diferencias")
    ok(len(diff(12, 13)) == d["diffs_vs_mechanical"]["0x4e_vs_0x4f"]["count"] == 4,
       "0x4e vs 0x4f: 4 registros")

    # --- correcciones declaradas -----------------------------------------
    text = " ".join(json.dumps(x) for x in d["corrections"])
    ok("S321" in text and "posicion->columna" in text, "correccion del mapa")
    ok("matriz SI distingue" in text, "correccion del veredicto silent")
    ok(any("S51" in x for x in d["scope_limit"]), "limite S51")

    print(f"OK S325: {checks} comprobaciones")


if __name__ == "__main__":
    main()
