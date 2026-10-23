#!/usr/bin/env python3
"""S329 - verificacion independiente de `mode_timing.json` contra los bytes.

Re-decodifica TODO desde los blobs con rutas de codigo distintas a las del
``build``: el literal PIC se obtiene del operando de capstone (no enmascarando
el halfword) y el sesgo del ``add rX,pc`` se aplica como ``(addr+4)&~1``.

Uso: ``.venv/bin/python analysis/s329_mode_timing_tables/verify_mode_timing.py``
Devuelve 0 si todas las comprobaciones pasan.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
DATA = HERE / "mode_timing.json"
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = True

OK = 0
FAIL: list[str] = []


def check(cond: bool, msg: str) -> None:
    global OK
    if cond:
        OK += 1
    else:
        FAIL.append(msg)


def read(path: Path) -> bytes:
    return path.read_bytes()


def at(blob: bytes, addr: int, size: int) -> bytes:
    return blob[addr - BASE:addr - BASE + size]


def word(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def hword(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<H", blob, addr - BASE)[0]


def literal_of(blob: bytes, addr: int) -> int:
    """Direccion del literal de un `ldr rX,[pc,#imm]` leida del operando."""
    ins = next(iter(MD.disasm(at(blob, addr, 4), addr)))
    imm = ins.operands[1].mem.disp
    return ((addr + 4) & ~3) + imm


def add_pc_operand(blob: bytes, addr: int) -> str | None:
    """Registro destino si en `addr` hay `add rD,pc`; None en otro caso."""
    ins = next(iter(MD.disasm(at(blob, addr, 4), addr)))
    if ins.mnemonic != "add" or len(ins.operands) != 2:
        return None
    dst, src = ins.operands
    if src.type != 1 or src.reg != 11:              # ARM_REG_PC en capstone
        return None
    return ins.reg_name(dst.reg)


def nth_row(blob: bytes, base: int, index: int, stride: int = 0x1C) -> bytes:
    return at(blob, base + stride * index, stride)


def main() -> int:
    data: dict[str, Any] = json.loads(DATA.read_text(encoding="utf-8"))
    a7s, a6 = read(A7S), read(A6000)

    check(hashlib.sha256(a7s).hexdigest() == data["firmware"]["a7s_fw320"]["sha256"],
          "sha256 A7S")
    check(hashlib.sha256(a6).hexdigest() == data["firmware"]["a6000_fw321"]["sha256"],
          "sha256 A6000")
    check(len(a7s) == data["firmware"]["a7s_fw320"]["size"], "tamano A7S")

    # --- bases PIC -----------------------------------------------------------
    for name, info in data["bases_from_pic"].items():
        ldr = int(info["ldr"], 16)
        add = int(info["add"], 16)
        lit_addr = literal_of(a7s, ldr)
        check(lit_addr == int(info["literal_addr"], 16), f"{name}: dir literal")
        lit = word(a7s, lit_addr)
        check(lit == int(info["literal"], 16), f"{name}: valor literal")
        check(add_pc_operand(a7s, add) is not None, f"{name}: add pc en 0x{add:x}")
        base = (lit + ((add + 4) & ~1)) & 0xFFFFFFFF
        check(base == int(info["base"], 16), f"{name}: base {base:#x}")
        check(len(info["literal_hits"]) == 1, f"{name}: literal unico")

    # --- sesgo ---------------------------------------------------------------
    bias = data["bias_calibration"]
    check(bias["only_align4"] * 100 < bias["only_bit0_clear"],
          "sesgo: bit0_clear domina")

    def is_str_start(addr: int) -> bool:
        if not BASE <= addr < BASE + len(a7s):
            return False
        i = addr - BASE
        if i == 0 or a7s[i - 1] != 0 or not 32 <= a7s[i] < 127:
            return False
        n = 0
        while i + n < len(a7s) and 32 <= a7s[i + n] < 127:
            n += 1
        return n >= 6

    for ex in bias["examples"]:
        check(is_str_start(int(ex["bit0_clear"], 16)), "ejemplo bit0 es cadena")
    for ex in bias["align4_only"]:
        check(not is_str_start(int(ex["bit0_clear"], 16)), "align4-only: bit0 no es cadena")

    # --- tabla B -------------------------------------------------------------
    bdesc = data["descriptor_b"]
    bbase = int(bdesc["base"], 16)
    rows_b = [list(at(a7s, bbase + 12 * k, 12)) for k in range(2)]
    check([bytes(r).hex() for r in rows_b] == bdesc["rows_hex"], "B: filas")
    check(rows_b[0] == list(range(12)), "B: fila 0 identidad")
    check(rows_b[1] == bdesc["row1"], "B: fila 1 permutacion")
    check(at(a7s, bbase + 24, 32).hex() == bdesc["bytes_after_two_rows"],
          "B: cola")
    check(bdesc["bytes_after_two_rows_ascii"].startswith("GCS2RxLink"),
          "B: la cola es texto, no hay fila 2")

    # --- tablas T ------------------------------------------------------------
    for name, table in data["tables"].items():
        base = int(table["base"], 16)
        check(base == int(data["bases_from_pic"][name]["base"], 16),
              f"{name}: base coincide con PIC")
        for row in table["rows_data"]:
            addr = base + 0x1C * row["index"]
            check(at(a7s, addr, 0x1C).hex() == row["hex"], f"{name} f{row['index']}: hex")
            check(word(a7s, addr) == row["w0"], f"{name} f{row['index']}: w0")
            check(word(a7s, addr + 0x14) == row["index_field_14"],
                  f"{name} f{row['index']}: +0x14")
            check(hword(a7s, addr + 0x18) == row["mask_field_18"],
                  f"{name} f{row['index']}: +0x18")
        idx = sorted({r["index_field_14"] for r in table["rows_data"]})
        check([f"0x{v:x}" for v in idx] == table["field_stats"]["index_values"],
              f"{name}: indices")
        check(all(v <= 1 for v in idx), f"{name}: indice dentro de B (2 filas)")

    check(data["base_coherence"]["spacing"]["T3_to_T2_rows"] == 34, "espaciado T3->T2")
    gap = at(a7s, int(data["tables"]["T1"]["base"], 16) + 0x1C * 34, 8).hex()
    check(gap == data["base_coherence"]["spacing"]["gap_T1_T3"], "hueco T1->T3")

    # --- consumidor ----------------------------------------------------------
    cons = data["consumer"]
    check(int(cons["address"], 16) == 0x436F618C, "consumidor direccion")
    check(cons["disasm"][0]["address"] == "0x436f618c", "consumidor primer insn")
    for fr in cons["field_reads"]:
        addr = int(fr["addr"], 16)
        check(addr in (0x436F61AE, 0x436F61B0, 0x436F61C2, 0x436F61C4,
                       0x436F61DA, 0x436F61DC), f"lectura {fr['addr']}")
        ins = next(iter(MD.disasm(at(a7s, addr, 2), addr)))
        check(ins.mnemonic in ("ldr", "ldrh"), f"lectura {fr['addr']} es load")
        check("0x14" in ins.op_str or "0x18" in ins.op_str,
              f"lectura {fr['addr']} toca +0x14/+0x18")

    # --- matriz --------------------------------------------------------------
    mtx = data["matrix"]
    mbase = int(mtx["base"], 16)
    check(mbase == 0x43FEE598, "matriz base")
    check(mtx["stride"] == 0x14 and mtx["rows"] == 69, "matriz forma")
    check(word(a7s, int(mtx["terminator"], 16)) == 0, "matriz terminador")
    pool: dict[int, tuple[int, int]] = {}
    addr = int(mtx["pool"]["start"], 16)
    while addr <= int(mtx["pool"]["end"], 16):
        pool[addr + 4] = (hword(a7s, addr + 2), a7s[addr - BASE])
        addr += 6
    check(len(pool) == mtx["pool"]["count"] == 98, "pool 98 registros")
    for row in mtx["rows_data"]:
        dest = int(row["dest"], 16)
        check(dest in pool, f"fila {row['index']}: destino en pool")
        check(pool[dest][0] == row["reg"], f"fila {row['index']}: registro")
        values = list(at(a7s, mbase + 0x14 * row["index"] + 4, 16))
        check(values == row["values"], f"fila {row['index']}: valores")

    codes = [word(a7s, 0x43FEE370 + 4 * i) for i in range(34)]
    check([f"0x{c:02x}" for c in codes] == data["mode_codes"], "lista de codigos")
    colmap = list(at(a7s, 0x43C9C5B5, 34))
    check(colmap == data["position_map"], "mapa de columnas")

    pos = {c: i for i, c in enumerate(codes)}
    for code, meta in data["mode_vectors"]["by_code"].items():
        c = int(code, 16)
        col = colmap[pos[c]]
        check(meta["position"] == pos[c] and meta["column"] == col,
              f"{code}: posicion/columna")
        for reg, val in meta["values"].items():
            row = next(r for r in mtx["rows_data"] if f"0x{r['reg']:02x}" == reg)
            check(row["values"][col] == val, f"{code} reg {reg}")

    for pair in data["matrix_pair_diffs"]:
        a, b = int(pair["a"], 16), int(pair["b"], 16)
        va = {r["reg"]: r["values"][colmap[pos[a]]] for r in mtx["rows_data"]}
        vb = {r["reg"]: r["values"][colmap[pos[b]]] for r in mtx["rows_data"]}
        count = sum(1 for k in va if va[k] != vb[k])
        check(count == pair["count"], f"diff {pair['a']}/{pair['b']}")

    check(len(data["mode_vectors"]["exclusive_silent_values"]) == 0,
          "sin valor exclusivo de silent")
    check(data["mode_vectors"]["unique_column_vectors"] == 16,
          "16 columnas distintas")

    # --- pares de filas T ----------------------------------------------------
    for name, pairs in data["t_row_pairs"].items():
        rows = data["tables"][name]["rows_data"]
        for pair in pairs:
            ra = rows[pos[int(pair["a"], 16)]]
            rb = rows[pos[int(pair["b"], 16)]]
            same = all(ra[k] == rb[k] for k in ("w0", "w4", "index_field_14",
                                                "mask_field_18"))
            check(same == pair["identical"], f"{name} {pair['a']}/{pair['b']}")

    # --- setters -------------------------------------------------------------
    st = data["setters"]
    ins_a7s = next(iter(MD.disasm(at(a7s, int(st["a7s"]["addr"], 16) + 0x10, 4),
                                  int(st["a7s"]["addr"], 16) + 0x10)))
    check("#0x51" in ins_a7s.op_str, "A7S acepta hasta 0x51")
    ins_a6 = next(iter(MD.disasm(at(a6, 0x436D6B62, 4), 0x436D6B62)))
    check("#0x47" in ins_a6.op_str, "A6000 acepta hasta 0x47")

    # --- barrido -------------------------------------------------------------
    sw = data["timing_table_sweep"]
    check(sw["tablas_T"]["strict_time"] == [], "barrido T sin tabla de tiempos")
    for hit in sw["lista_y_matriz"]["strict_time"]:
        addr = int(hit["addr"], 16)
        vals = list(struct.unpack_from(f"<{hit['length']}H", a7s, addr - BASE))
        check(max(vals) == hit["max"] and len(set(vals)) == hit["distinct"],
              f"barrido {hit['addr']}")

    print(f"{OK} comprobaciones OK, {len(FAIL)} fallos")
    for msg in FAIL:
        print("  FALLO:", msg)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
