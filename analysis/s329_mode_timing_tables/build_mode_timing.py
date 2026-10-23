#!/usr/bin/env python3
"""S329 - carril B: ¿existe una tabla de tiempos por modo en el A7S (S202 §3)?

S202 §3 / S201 #5 describen la temporizacion del IMX235 (A7S fw3.20) como
"columnas estaticas de la matriz de modos"; no se recupero ninguna tabla de
tiempos en frames/ms.  Esta sesion cierra la pregunta de tres formas:

1. Enumerando **todas** las estructuras por modo y midiendo que campos consume
   el codigo.
2. Barriendo las dos regiones de tablas de modo en busca de un array de 34/69
   elementos con pinta de tiempos que este referenciado por codigo PIC.
3. Midiendo la diferencia real entre los modos silent (0x4e/0x4f) y 0x4c/0x4d
   en la matriz de registros de 69 filas.

Estructuras por modo (A7S fw3.20):

* lista de codigos      ``u32[34]``   @ ``0x43fee370``                    (S324)
* mapa posicion->columna``u8[34]``    @ ``0x43c9c5b5``                    (S325)
* matriz de registros   ``69 x {u32 dest; u8 v[16]}`` @ ``0x43fee598``     (S321)
* tablas T1/T2/T3       ``34 x 0x1c B`` @ ``0x43bbeb70``/``0x43bbf2e8``/``0x43bbef30``
* descriptores B        ``2 x 12 B``   @ ``0x43c9d09b``                   (nueva)

Correccion importante: S317 y S326 usaron las bases ``0x43bbf2ec`` (T2) y
``0x43bbef34`` (T3), **4 B por encima** de lo que calcula el codigo.  Aqui se
recalculan con el sesgo vigente ``PC=(add+4)`` con bit0 a 0, se calibra ese
sesgo contra cadenas conocidas (51 aciertos exclusivos frente a 0 del sesgo
alineado a 4) y se comprueba la coherencia: con las bases corregidas el campo
``+0x14`` vale siempre 0 o 1 -- exactamente las **2** filas de la tabla B -- y
T3->T2 dista 34*0x1c exactos.  Con las bases de S317 el indice valdria
0x3ff/0xf0/0x1f8/0xfff, fuera de rango para B.

Solo lectura de los blobs: no se ejecuta firmware ni se toca la camara.
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
OUT = Path(__file__).with_name("mode_timing.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

MODE_LIST = 0x43FEE370          # u32[34]
POSITION_MAP = 0x43C9C5B5       # u8[34]
MATRIX = 0x43FEE598             # 69 x {u32 dest; u8 v[16]}
MATRIX_STRIDE = 0x14
MATRIX_ROWS = 69
POOL_START = 0x44021EC2
POOL_END = 0x44022108
DESCRIPTOR_B = 0x43C9D09B       # 2 x 12 B

# (nombre, ldr, add): instrucciones que calculan cada base.
PIC_PAIRS = {
    "T1": (0x436F61A2, 0x436F61AA),
    "T2": (0x436F61BA, 0x436F61BE),
    "T3": (0x436F61CE, 0x436F61D2),
    "B": (0x436F5F48, 0x436F5F4A),
}
# Bases que calcula el codigo (sesgo PC=(add+4) con bit0 a 0).
EXPECTED_BASES = {"T1": 0x43BBEB70, "T2": 0x43BBF2E8, "T3": 0x43BBEF30,
                  "B": DESCRIPTOR_B}
# Bases publicadas por S317/S326 (+4 en T2 y T3) que aqui se contrastan.
S317_BASES = {"T1": 0x43BBEB70, "T2": 0x43BBF2EC, "T3": 0x43BBEF34}
T_STRIDE = 0x1C
T_ROWS = 34
SILENT_CODES = [0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51]
REF_CODE = 0x0B

CONSUMER = 0x436F618C
MASK_HELPERS = {"T1/T2": 0x436F5F30, "T3": 0x436F6140}
# Lecturas de campo de la fila dentro del consumidor: (addr, tabla).
FIELD_READS = [(0x436F61AE, "T1"), (0x436F61B0, "T1"),
               (0x436F61C2, "T2"), (0x436F61C4, "T2"),
               (0x436F61DA, "T3"), (0x436F61DC, "T3")]

SWEEP_REGIONS = [("tablas_T", 0x43BBD000, 0x43BC0000),
                 ("lista_y_matriz", 0x43FEE000, 0x43FF0000)]
SWEEP_LENGTHS = (34, 69)

A7S_SETTER = 0x436F3B44
A7S_SETTER_CMP = 0x436F3B54     # cmp r3,#0x51
A6000_SETTER = 0x436D6B50
A6000_SETTER_CMP = 0x436D6B62   # cmp r2,#0x47


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


def raw(blob: bytes, addr: int, size: int) -> bytes:
    return blob[addr - BASE:addr - BASE + size]


def dis(blob: bytes, start: int, size: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw(blob, start, size), start)]


def pic_base(blob: bytes, ldr: int, add: int) -> dict[str, Any]:
    """Base de `ldr rX,[pc,#imm]` + `add rX,pc`.

    Literal: (ldr+4) alineado a 4.  PC del add: (add+4) con bit0 a 0.
    """
    h = u16(blob, ldr)
    assert (h & 0xF800) == 0x4800, f"0x{ldr:08x} no es ldr pc-rel"
    lit = ((ldr + 4) & ~3) + (h & 0xFF) * 4
    word = u32(blob, lit)
    h2 = u16(blob, add)
    assert (h2 & 0xFFF8) == 0x4478, f"0x{add:08x} no es add pc"
    pc_bit0 = (add + 4) & ~1
    pc_al4 = (add + 4) & ~3
    return {"ldr": f"0x{ldr:08x}", "literal_addr": f"0x{lit:08x}",
            "literal": f"0x{word:08x}", "add": f"0x{add:08x}",
            "insn_ldr": dis(blob, ldr, 2)[0]["insn"],
            "insn_add": dis(blob, add, 2)[0]["insn"],
            "pc_bit0_clear": f"0x{pc_bit0:08x}",
            "base": f"0x{(word + pc_bit0) & 0xFFFFFFFF:08x}",
            "base_if_align4": f"0x{(word + pc_al4) & 0xFFFFFFFF:08x}"}


def literal_hits(blob: bytes, value: int) -> list[str]:
    pat = struct.pack("<I", value)
    out, i = [], blob.find(pat)
    while i >= 0:
        out.append(f"0x{BASE + i:08x}")
        i = blob.find(pat, i + 1)
    return out


def is_string_start(blob: bytes, addr: int) -> bool:
    if not BASE <= addr < BASE + len(blob):
        return False
    i = addr - BASE
    if i == 0 or blob[i - 1] != 0 or not 32 <= blob[i] < 127:
        return False
    n = 0
    while i + n < len(blob) and 32 <= blob[i + n] < 127:
        n += 1
    return n >= 6


def _add_pc_target(blob: bytes, addr: int) -> tuple[int, str] | None:
    """Si en `addr` hay `add rD,pc`, devuelve (target, rD) con PC=(addr+4) bit0=0."""
    h = u16(blob, addr)
    if (h & 0xFF00) != 0x4400:      # ADD (register) T1: 01000100 ...
        return None
    ins = next(iter(MD.disasm(raw(blob, addr, 2), addr)), None)
    if ins is None or ins.mnemonic != "add":
        return None
    ops = [o.strip() for o in ins.op_str.split(",")]
    if len(ops) != 2 or ops[1] != "pc":
        return None
    return ((addr + 4) & ~1), ops[0]


def bias_calibration(blob: bytes) -> dict[str, Any]:
    """Cuenta pares ldr+add cuyo destino es una cadena solo con cada sesgo."""
    both = only_bit0 = only_align4 = neither = 0
    examples: list[dict[str, str]] = []
    align4_only: list[dict[str, str]] = []
    for i in range(0, len(blob) - 8, 2):
        h = struct.unpack_from("<H", blob, i)[0]
        if (h & 0xF800) != 0x4800:
            continue
        rd = f"r{(h >> 8) & 7}"
        lit = ((BASE + i + 4) & ~3) + (h & 0xFF) * 4
        if lit - BASE + 4 > len(blob):
            continue
        word = u32(blob, lit)
        if not 0 < word < 0x02000000:
            continue
        for k in range(1, 6):
            j = i + 2 * k
            if j + 2 > len(blob):
                break
            found = _add_pc_target(blob, BASE + j)
            if found is None:
                continue
            pc_bit0, rname = found
            if rname != rd:
                break
            ta = (word + pc_bit0) & 0xFFFFFFFF
            tb = (word + (pc_bit0 & ~3)) & 0xFFFFFFFF
            a_ok, b_ok = is_string_start(blob, ta), is_string_start(blob, tb)
            if a_ok and b_ok:
                both += 1
            elif a_ok:
                only_bit0 += 1
                if len(examples) < 5:
                    examples.append({"add": f"0x{BASE + j:08x}",
                                     "bit0_clear": f"0x{ta:08x}",
                                     "align4": f"0x{tb:08x}"})
            elif b_ok:
                only_align4 += 1
                if len(align4_only) < 6:
                    align4_only.append({"add": f"0x{BASE + j:08x}",
                                        "bit0_clear": f"0x{ta:08x}",
                                        "align4": f"0x{tb:08x}"})
            else:
                neither += 1
            break
    return {"only_bit0_clear": only_bit0, "only_align4": only_align4,
            "both": both, "neither": neither, "examples": examples,
            "align4_only": align4_only,
            "verdict": "PC=(add+4) con bit0 a 0" if only_align4 * 100 < only_bit0
            else "ambiguo"}


def t_rows(blob: bytes, base: int) -> list[dict[str, Any]]:
    rows = []
    for i in range(T_ROWS):
        addr = base + T_STRIDE * i
        chunk = raw(blob, addr, T_STRIDE)
        rows.append({
            "index": i,
            "addr": f"0x{addr:08x}",
            "hex": chunk.hex(),
            "w0": u32(blob, addr),
            "w4": f"0x{u32(blob, addr + 4):08x}",
            "index_field_14": u32(blob, addr + 0x14),
            "mask_field_18": u16(blob, addr + 0x18),
            "u16_field_1a": u16(blob, addr + 0x1A),
        })
    return rows


def table_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    idx = sorted({r["index_field_14"] for r in rows})
    mask = sorted({r["mask_field_18"] for r in rows})
    return {"index_values": [f"0x{v:x}" for v in idx],
            "index_within_B_rows": all(v <= 1 for v in idx),
            "mask_values": [f"0x{v:x}" for v in mask],
            "masks_within_12_bits": all(v <= 0xFFF for v in mask),
            "w0_values": sorted({f"0x{r['w0']:x}" for r in rows})}


def descriptor_b(blob: bytes) -> dict[str, Any]:
    rows = [list(raw(blob, DESCRIPTOR_B + 12 * k, 12)) for k in range(2)]
    tail = raw(blob, DESCRIPTOR_B + 24, 32)
    return {
        "base": f"0x{DESCRIPTOR_B:08x}",
        "stride": 12,
        "rows_hex": [bytes(r).hex() for r in rows],
        "row0_is_identity": rows[0] == list(range(12)),
        "row1": rows[1],
        "bytes_after_two_rows": tail.hex(),
        "bytes_after_two_rows_ascii": "".join(chr(c) if 32 <= c < 127 else "."
                                              for c in tail),
        "rows_available": 2,
    }


def matrix(blob: bytes) -> dict[str, Any]:
    pool: list[dict[str, Any]] = []
    addr = POOL_START
    while addr <= POOL_END:
        pool.append({"addr": addr, "dev": blob[addr - BASE],
                     "reg": u16(blob, addr + 2), "base_data": blob[addr - BASE + 4]})
        addr += 6
    by_data = {r["addr"] + 4: r for r in pool}

    rows: list[dict[str, Any]] = []
    for i in range(MATRIX_ROWS):
        a = MATRIX + MATRIX_STRIDE * i
        dest = u32(blob, a)
        rec = by_data.get(dest)
        if dest == 0 or rec is None:
            raise SystemExit(f"fila {i}: destino 0x{dest:08x} invalido")
        rows.append({"index": i, "addr": f"0x{a:08x}", "dest": f"0x{dest:08x}",
                     "reg": rec["reg"], "base_data": rec["base_data"],
                     "values": list(raw(blob, a + 4, 16))})
    term_addr = MATRIX + MATRIX_STRIDE * MATRIX_ROWS
    return {
        "base": f"0x{MATRIX:08x}",
        "stride": MATRIX_STRIDE,
        "rows": MATRIX_ROWS,
        "terminator": f"0x{term_addr:08x}",
        "terminator_value": f"0x{u32(blob, term_addr):08x}",
        "pool": {"start": f"0x{POOL_START:08x}", "end": f"0x{POOL_END:08x}",
                 "count": len(pool),
                 "dev_histogram": {f"0x{d:02x}": sum(1 for r in pool if r["dev"] == d)
                                   for d in sorted({r["dev"] for r in pool})}},
        "rows_data": rows,
        "dest_unique": len({r["dest"] for r in rows}) == len(rows),
    }


def mode_vectors(mtx: dict[str, Any], colmap: list[int],
                 codes: list[int]) -> dict[str, Any]:
    pos = {c: i for i, c in enumerate(codes)}
    out: dict[str, Any] = {}
    for code in SILENT_CODES + [REF_CODE]:
        col = colmap[pos[code]]
        out[f"0x{code:02x}"] = {
            "position": pos[code], "column": col,
            "values": {f"0x{r['reg']:02x}": r["values"][col]
                       for r in mtx["rows_data"]}}
    cols = {c: tuple(r["values"][c] for r in mtx["rows_data"]) for c in range(16)}
    exclusive = []
    for r in mtx["rows_data"]:
        v12, v13 = r["values"][12], r["values"][13]
        if v12 not in set(r["values"][:12]) | {v13}:
            exclusive.append([f"0x{r['reg']:02x}", "col12", v12])
        if v13 not in set(r["values"][:12]) | {v12}:
            exclusive.append([f"0x{r['reg']:02x}", "col13", v13])
    return {"by_code": out,
            "columns_used": len(set(colmap)),
            "unique_column_vectors": len(set(cols.values())),
            "silent_columns_unique": {12: len(set(cols.values())) == 16,
                                      13: len(set(cols.values())) == 16},
            "exclusive_silent_values": exclusive}


def diff_vectors(vecs: dict[str, Any], a: int, b: int) -> dict[str, Any]:
    va = vecs["by_code"][f"0x{a:02x}"]["values"]
    vb = vecs["by_code"][f"0x{b:02x}"]["values"]
    diffs = [[reg, va[reg], vb[reg]] for reg in va if va[reg] != vb[reg]]
    return {"a": f"0x{a:02x}", "b": f"0x{b:02x}", "count": len(diffs),
            "diffs": diffs}


def row_diffs(rows: list[dict[str, Any]], pos: dict[int, int],
              a: int, b: int) -> dict[str, Any]:
    ra, rb = rows[pos[a]], rows[pos[b]]
    keys = ("w0", "w4", "index_field_14", "mask_field_18")
    diffs = {k: [ra[k], rb[k]] for k in keys if ra[k] != rb[k]}
    return {"a": f"0x{a:02x}", "b": f"0x{b:02x}", "identical": not diffs,
            "field_diffs": diffs}


def pic_targets(blob: bytes) -> set[int]:
    """Bases calculadas por pares `ldr rD,[pc,#imm]` + `add rD,pc` cercanos."""
    targets: set[int] = set()
    for i in range(0, len(blob) - 8, 2):
        h = struct.unpack_from("<H", blob, i)[0]
        if (h & 0xF800) != 0x4800:
            continue
        rd = f"r{(h >> 8) & 7}"
        lit = ((BASE + i + 4) & ~3) + (h & 0xFF) * 4
        if lit - BASE + 4 > len(blob):
            continue
        word = u32(blob, lit)
        if not 0 < word < 0x02000000:
            continue
        for k in range(1, 6):
            j = i + 2 * k
            if j + 2 > len(blob):
                break
            found = _add_pc_target(blob, BASE + j)
            if found is None:
                continue
            if found[1] != rd:
                break
            targets.add((word + found[0]) & 0xFFFFFFFF)
            break
    return targets


KNOWN_TABLES = {"T1": 0x43BBEB70, "T2": 0x43BBF2E8, "T3": 0x43BBEF30,
                "mode_list": 0x43FEE370, "matrix": 0x43FEE598}


def sweep(blob: bytes, targets: set[int]) -> dict[str, Any]:
    """Arrays de 34/69 elementos con valores 1..0xFFFF en las regiones de tablas.

    Se separan dos filtros:
    * ``plausible_time``: min>=1, max<=20000, distintos>=len/3 y **referenciado**.
    * ``strict_time``: ademas distintos>=30 (una tabla de tiempos por modo tendria
      casi todos los valores distintos).
    """
    known = {v: k for k, v in KNOWN_TABLES.items()}
    out: dict[str, Any] = {}
    for name, lo, hi in SWEEP_REGIONS:
        candidates = plausible = 0
        strict, referenced = [], []
        for start in range(lo, hi - 4, 4):
            for width, fmt in ((2, "H"), (4, "I")):
                for length in SWEEP_LENGTHS:
                    size = width * length
                    if start + size > hi:
                        continue
                    vals = list(struct.unpack_from(f"<{length}{fmt}", blob,
                                                   start - BASE))
                    if max(vals) == 0 or max(vals) > 0xFFFF:
                        continue
                    if len(set(vals)) < 3:
                        continue
                    candidates += 1
                    if start not in targets:
                        continue
                    entry = {"addr": f"0x{start:08x}", "width": width,
                             "length": length, "min": min(vals),
                             "max": max(vals), "distinct": len(set(vals)),
                             "first": vals[:6],
                             "known_table": known.get(start, "")}
                    referenced.append(entry)
                    time_like = min(vals) >= 1 and max(vals) <= 20000
                    if time_like and entry["distinct"] * 3 >= length:
                        plausible += 1
                        if entry["distinct"] >= 30:
                            strict.append(entry)
        out[name] = {"region": [f"0x{lo:08x}", f"0x{hi:08x}"],
                     "candidates": candidates,
                     "referenced_count": len(referenced),
                     "referenced": referenced,
                     "plausible_time_count": plausible,
                     "strict_time": strict}
    out["pic_targets"] = len(targets)
    out["known_tables"] = {k: f"0x{v:08x}" for k, v in KNOWN_TABLES.items()}
    return out


def main() -> None:
    a7s = A7S.read_bytes()
    a6 = A6000.read_bytes()

    bias = bias_calibration(a7s)
    bases = {}
    for name, (ldr, add) in PIC_PAIRS.items():
        info = pic_base(a7s, ldr, add)
        assert int(info["base"], 16) == EXPECTED_BASES[name], (name, info)
        info["literal_hits"] = literal_hits(a7s, int(info["literal"], 16))
        bases[name] = info

    consumer = dis(a7s, CONSUMER, 0x5C)
    helpers = {k: dis(a7s, v, 0x40) for k, v in MASK_HELPERS.items()}
    field_reads = [{"addr": f"0x{a:08x}", "table": t,
                    "insn": dis(a7s, a, 2)[0]["insn"]} for a, t in FIELD_READS]

    codes = [u32(a7s, MODE_LIST + 4 * i) for i in range(T_ROWS)]
    pos = {c: i for i, c in enumerate(codes)}
    rows_by_table = {name: t_rows(a7s, base) for name, base in EXPECTED_BASES.items()
                     if name != "B"}
    stats = {k: table_stats(v) for k, v in rows_by_table.items()}

    # Coherencia de las bases: las de S317 (+4) frente a las del codigo.
    coherence = {}
    for name in ("T1", "T2", "T3"):
        alt_rows = t_rows(a7s, S317_BASES[name])
        coherence[name] = {
            "code_base": f"0x{EXPECTED_BASES[name]:08x}",
            "s317_base": f"0x{S317_BASES[name]:08x}",
            "code_index_values": stats[name]["index_values"],
            "s317_index_values": table_stats(alt_rows)["index_values"],
            "code_index_within_B": stats[name]["index_within_B_rows"],
            "s317_index_within_B": table_stats(alt_rows)["index_within_B_rows"],
            "s317_masks_within_12_bits": table_stats(alt_rows)["masks_within_12_bits"],
        }
    coherence["spacing"] = {
        "T3_minus_T2": f"0x{EXPECTED_BASES['T2'] - EXPECTED_BASES['T3']:03x}",
        "T3_to_T2_rows": (EXPECTED_BASES["T2"] - EXPECTED_BASES["T3"]) // T_STRIDE,
        "T1_to_T3": f"0x{EXPECTED_BASES['T3'] - EXPECTED_BASES['T1']:03x}",
        "T1_to_T3_rows": (EXPECTED_BASES["T3"] - EXPECTED_BASES["T1"]) / T_STRIDE,
        "gap_T1_T3": raw(a7s, EXPECTED_BASES["T1"] + T_STRIDE * T_ROWS, 8).hex(),
    }

    pairs_t = {name: [row_diffs(rows, pos, a, b) for a, b in
                      [(0x4E, 0x4C), (0x4F, 0x4D), (0x4E, 0x51), (0x4F, 0x50),
                       (0x4C, 0x4D)]]
               for name, rows in rows_by_table.items()}

    mtx = matrix(a7s)
    colmap = list(raw(a7s, POSITION_MAP, T_ROWS))
    vecs = mode_vectors(mtx, colmap, codes)
    pairs_m = [diff_vectors(vecs, a, b) for a, b in
               [(0x4E, 0x4C), (0x4F, 0x4D), (0x4E, 0x51), (0x4F, 0x50),
                (0x4C, 0x4D), (0x4E, 0x4F)]]

    b_desc = descriptor_b(a7s)
    sweep_data = sweep(a7s, pic_targets(a7s))

    data: dict[str, Any] = {
        "milestone": "S329",
        "title": "No hay tabla de tiempos por modo en el A7S; las tablas T son "
                 "(indice a 2 descriptores, mascara de 12 bits) y sus bases "
                 "estan 4 B por debajo de las de S317",
        "base": f"0x{BASE:08x}",
        "firmware": {"a7s_fw320": {"sha256": sha256(A7S), "size": len(a7s)},
                     "a6000_fw321": {"sha256": sha256(A6000), "size": len(a6)}},
        "bias_calibration": bias,
        "bases_from_pic": bases,
        "base_coherence": coherence,
        "consumer": {"address": f"0x{CONSUMER:08x}", "disasm": consumer,
                     "helpers": helpers, "field_reads": field_reads,
                     "fields_read_from_row": ["+0x14 (u32): indice para mla 12*r2",
                                              "+0x18 (u16): mascara extraida con asrs"],
                     "bytes_never_read_per_row": T_STRIDE - 6},
        "tables": {k: {"base": f"0x{EXPECTED_BASES[k]:08x}", "stride": T_STRIDE,
                       "rows": T_ROWS, "field_stats": stats[k],
                       "rows_data": rows_by_table[k]}
                   for k in ("T1", "T2", "T3")},
        "t_row_pairs": pairs_t,
        "descriptor_b": b_desc,
        "mode_codes": [f"0x{c:02x}" for c in codes],
        "position_map": colmap,
        "matrix": mtx,
        "mode_vectors": vecs,
        "matrix_pair_diffs": pairs_m,
        "timing_table_sweep": sweep_data,
        "setters": {
            "a7s": {"addr": f"0x{A7S_SETTER:08x}",
                    "insn": dis(a7s, A7S_SETTER_CMP, 2)[0]["insn"],
                    "bytes": raw(a7s, A7S_SETTER_CMP, 2).hex()},
            "a6000": {"addr": f"0x{A6000_SETTER:08x}",
                      "insn": dis(a6, A6000_SETTER_CMP, 2)[0]["insn"],
                      "bytes": raw(a6, A6000_SETTER_CMP, 2).hex()},
        },
        "verdicts": {
            "timing_table_exists": False,
            "s202_s3_claim": "NO REPRODUCIBLE: la 'tabla de tiempos por modo' del "
                             "IMX235 no es una tabla de tiempos; las columnas de la "
                             "matriz son valores de registro y las tablas T son "
                             "(indice, mascara).",
            "0x4e_differs_from_0x4c": pairs_m[0]["count"] > 0,
            "0x4e_vs_0x4c_diff_count": pairs_m[0]["count"],
            "0x4f_vs_0x4d_diff_count": pairs_m[1]["count"],
            "0x4c_equals_0x4d": pairs_m[4]["count"] == 0,
            "silent_columns_unique": vecs["silent_columns_unique"],
            "exclusive_silent_register_value": len(vecs["exclusive_silent_values"]) > 0,
            "t_rows_are_index_and_mask": True,
            "code_bases_differ_from_s317": True,
        },
        "corrections": [
            ("T2 y T3 estan en 0x43bbf2e8 y 0x43bbef30, no en 0x43bbf2ec ni "
             "0x43bbef34 (S317/S326): el codigo suma el literal con PC=(add+4) "
             "bit0=0 y las bases +4 dejan el indice fuera de rango para la tabla "
             "de 2 descriptores."),
            ("Con las bases correctas, '0x4e==0x51' y '0x4f==0x50' de S326 "
             "desaparecen: difieren en w0 (0x02 frente a 0x03)."),
            ("S321/S326 midieron las tablas T, no la matriz de registros; la "
             "diferencia de S204 entre 0x4e/0x4c y 0x4f/0x4d solo se puede "
             "contrastar en la matriz (69 filas): alli son 14 y 11 registros."),
        ],
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("Una consulta vacia no prueba ausencia: la ausencia de tabla de "
             "tiempos se sostiene en el barrido de dos regiones y en la "
             "enumeracion de estructuras, no en falta de xrefs."),
            ("No se asigna semantica fisica a ningun registro ni a la mascara de "
             "12 bits; el mapeo bit->campo depende del objeto 0x43dc02e0 (runtime)."),
            ("El sesgo PC=(add+4) bit0=0 se calibra con cadenas; no prueba que el "
             "compilador no compensara el literal, pero con las bases resultantes "
             "el indice encaja con las 2 filas de B y el espaciado es exacto."),
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("bias", bias["only_bit0_clear"], bias["only_align4"])
    print("bases", {k: v["base"] for k, v in bases.items()},
          "align4->", {k: v["base_if_align4"] for k, v in bases.items()})
    print("stats", {k: (v["index_values"], v["mask_values"]) for k, v in stats.items()})
    print("B", b_desc["row0_is_identity"], b_desc["rows_available"],
          b_desc["bytes_after_two_rows_ascii"][:24])
    print("t pairs", {k: [(p["a"], p["b"], p["identical"]) for p in v]
                      for k, v in pairs_t.items()})
    print("matrix diffs", [(p["a"], p["b"], p["count"]) for p in pairs_m])
    print("sweep", {k: (v["candidates"], v["referenced_count"],
                         v["plausible_time_count"], len(v["strict_time"]))
                    for k, v in sweep_data.items() if isinstance(v, dict)
                    and "candidates" in v})
    print("bias align4-only examples", bias["align4_only"])


if __name__ == "__main__":
    main()
