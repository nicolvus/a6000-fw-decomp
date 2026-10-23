#!/usr/bin/env python3
"""S342 - carril B: consumidores de `0x43fef404` por puntero calculado (PIC).

S337 cerro la pregunta con un negativo **acotado a literales absolutos**: no hay
ninguna palabra de 32 bits igual a `0x43fef404` en el blob.  Pero este firmware
es PIC: las tablas se direccionan con `ldr rX,[pc,#imm]` + `add rX,pc`, de modo
que la direccion nunca aparece como literal.  Re-barriendo los pares PIC se
encuentran **dos** bases que apuntan exactamente a `0x43fef404`, en las tres
camaras, y ambas son consumidoras de la tabla.

Hallazgos (todo re-decodificado de los bytes):
  * la tabla es `{u16 id, u16 0x000d}` con **69** entradas en A7S/A6300 y **47**
    en A6000 (los ids de la A6000 son subconjunto estricto: faltan `0x4f..0x64`);
  * va acompanada de un array de **69/47 punteros** a `.bss` (slot GOT), y el
    bucle del consumidor itera exactamente tantas veces como entradas tiene la
    tabla (`cmp r7,#0x45` / `#0x2f`);
  * los dos consumidores se invocan desde el init del modulo
    `Camera::Lens::ODL` (carga de datos de aberracion del objetivo);
  * la tabla **no** se escribe, **no** se indexa por modo y **no** contiene
    tiempos: la conclusion negativa de S329 se mantiene.

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
FW = ROOT / "firmware/extracted"
BLOBS = {
    "a7s_fw320": FW / ("a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/"
                       "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6000_fw321": FW / ("fw321/firmware.tar_unpacked/0700_part_image/dev/"
                         "nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300_fw201": FW / ("a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/"
                         "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
TABLE = 0x43FEF404           # A7S
TABLE_A6000 = 0x43FEAE1C
TABLE_A6300 = 0x441B0B1C
SECOND = 0x000D
OUT = Path(__file__).with_name("fef404_consumers.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


# --------------------------------------------------------------------------- #
# helpers de bytes
# --------------------------------------------------------------------------- #
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


def cstr(blob: bytes, addr: int, limit: int = 100) -> str | None:
    i = addr - BASE
    if not 0 <= i < len(blob):
        return None
    j = i
    while j < len(blob) and blob[j] != 0 and j - i < limit:
        j += 1
    try:
        return blob[i:j].decode("latin1")
    except UnicodeDecodeError:  # pragma: no cover - latin1 nunca falla
        return None


def pic_base(blob: bytes, ldr: int, add: int) -> dict[str, Any]:
    """`ldr rD,[pc,#imm]` + `add rD,pc` -> base.  PC=(add+4) con bit0 a 0."""
    h = u16(blob, ldr)
    assert (h & 0xF800) == 0x4800, f"0x{ldr:08x} no es ldr pc-rel"
    lit = ((ldr + 4) & ~3) + (h & 0xFF) * 4
    word = u32(blob, lit)
    h2 = u16(blob, add)
    assert (h2 & 0xFF00) == 0x4400, f"0x{add:08x} no es add"
    rd = h2 & 7
    assert ((h2 >> 3) & 0xF) == 0xF and ((h2 >> 7) & 1) == 0, f"0x{add:08x} no es add pc"
    assert rd == (h >> 8) & 7, f"0x{add:08x} no usa el registro de 0x{ldr:08x}"
    base = (word + ((add + 4) & ~1)) & 0xFFFFFFFF
    return {"ldr": f"0x{ldr:08x}", "add": f"0x{add:08x}",
            "literal_addr": f"0x{lit:08x}", "literal": f"0x{word:08x}",
            "base": f"0x{base:08x}", "base_int": base}


def pic_sites(blob: bytes, target: int) -> list[dict[str, Any]]:
    """Todos los pares ldr+add cuya base calculada es `target`."""
    out: list[dict[str, Any]] = []
    n = len(blob)
    for off in range(0, n - 8, 2):
        h = u16(blob, BASE + off)
        if (h & 0xF800) != 0x4800:
            continue
        rd = (h >> 8) & 7
        lit = ((BASE + off + 4) & ~3) + ((h & 0xFF) * 4)
        if lit - BASE + 4 > n:
            continue
        word = u32(blob, lit)
        for k in (2, 4, 6, 8):
            add = BASE + off + k
            if add - BASE + 2 > n:
                break
            h2 = u16(blob, add)
            if ((h2 & 0xFF00) == 0x4400 and ((h2 >> 3) & 0xF) == 0xF
                    and (h2 & 7) == rd and ((h2 >> 7) & 1) == 0):
                if (word + ((add + 4) & ~1)) & 0xFFFFFFFF == target:
                    out.append(pic_base(blob, BASE + off, add))
                break
    return out


def bl_callers(blob: bytes, target: int) -> list[str]:
    out: list[str] = []
    n = len(blob)
    for off in range(0, n - 4, 2):
        h = struct.unpack_from("<H", blob, off)[0]
        if (h & 0xF800) != 0xF000:
            continue
        h2 = struct.unpack_from("<H", blob, off + 2)[0]
        if (h2 & 0xD000) != 0xD000:
            continue
        s = (h >> 10) & 1
        imm10 = h & 0x3FF
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        imm11 = h2 & 0x7FF
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        val = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
        if s:
            val -= 1 << 25
        if (BASE + off + 4 + val) & 0xFFFFFFFF == target:
            out.append(f"0x{BASE + off:08x}")
    return out


def ids_of(blob: bytes, table: int) -> list[int]:
    out = []
    i = 0
    while u16(blob, table + 4 * i + 2) == SECOND:
        out.append(u16(blob, table + 4 * i))
        i += 1
    return out


def zero_run(blob: bytes, addr: int) -> tuple[int, int]:
    i = addr - BASE
    lo = i
    while lo > 0 and blob[lo - 1] == 0:
        lo -= 1
    hi = i
    while hi < len(blob) and blob[hi] == 0:
        hi += 1
    return BASE + lo, BASE + hi


def strings_in(blob: bytes, start: int, end: int) -> list[str]:
    found: set[str] = set()
    off = start - BASE
    while off < end - BASE:
        addr = BASE + off
        h = u16(blob, addr)
        if (h & 0xF800) == 0x4800:
            rd = (h >> 8) & 7
            lit = ((addr + 4) & ~3) + ((h & 0xFF) * 4)
            if lit - BASE + 4 <= len(blob):
                word = u32(blob, lit)
                for k in (2, 4, 6, 8):
                    a = addr + k
                    h2 = u16(blob, a)
                    if ((h2 & 0xFF00) == 0x4400 and ((h2 >> 3) & 0xF) == 0xF
                            and (h2 & 7) == rd and ((h2 >> 7) & 1) == 0):
                        base = (word + ((a + 4) & ~1)) & 0xFFFFFFFF
                        s = cstr(blob, base) if BASE <= base < BASE + len(blob) else None
                        if s and len(s) > 3 and all(32 <= ord(c) < 127 for c in s):
                            found.add(s)
                        break
        off += 2
    return sorted(found)


def insns(blob: bytes, start: int, size: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(blob[start - BASE:start - BASE + size], start)]


def loop_bound(blob: bytes, func: int, window: int = 0x200) -> dict[str, Any]:
    """`cmp rX,#imm` + `bne` dentro del cuerpo; iteraciones segun el paso."""
    code = insns(blob, func, window)
    body: list[dict[str, str]] = []
    for i in code:
        if i["insn"].startswith(("pop ", "pop.w ", "bx ")):
            break
        body.append(i)
    for idx, i in enumerate(body):
        mn = i["insn"].split()[0]
        if not mn.startswith("cmp") or i["insn"].split()[1].startswith("#"):
            continue
        if idx + 1 >= len(body) or not body[idx + 1]["insn"].startswith("bne"):
            continue
        reg = i["insn"].split()[1].rstrip(",")
        imm = int(i["insn"].split("#")[1], 16)
        step = None
        for j in body:
            parts = j["insn"].split()
            if parts[0] == "adds" and parts[1].rstrip(",") == reg:
                step = int(parts[2].lstrip("#"), 16)
                break
        iters = imm // step if step and step > 0 else imm
        return {"cmp": i["insn"], "at": i["address"], "imm": imm,
                "step": step, "iterations": iters}
    return {}


def slot_from(blob: bytes, got_base: int, ldr: int) -> dict[str, Any]:
    """`ldr rD,[pc,#imm]` usado como offset: slot = got_base + literal."""
    h = u16(blob, ldr)
    lit = ((ldr + 4) & ~3) + ((h & 0xFF) * 4)
    off = u32(blob, lit)
    slot = (got_base + off) & 0xFFFFFFFF
    return {"ldr": f"0x{ldr:08x}", "literal_addr": f"0x{lit:08x}",
            "offset": f"0x{off:08x}", "slot": f"0x{slot:08x}",
            "slot_int": slot, "value": f"0x{u32(blob, slot):08x}",
            "value_int": u32(blob, slot)}


def consumer(blob: bytes, func: int, ldr: int, add: int, table: int,
             got_base: int, slot_ldrs: list[int],
             imm_reg: int | None = None) -> dict[str, Any]:
    base = pic_base(blob, ldr, add)
    assert base["base_int"] == table, (hex(base["base_int"]), hex(table))
    slots = [slot_from(blob, got_base, s) for s in slot_ldrs]
    lb = loop_bound(blob, func)
    code = insns(blob, func, 0x50)
    calls = [i["insn"].split()[1] for i in code if i["insn"].startswith("bl ")]
    rec: dict[str, Any] = {
        "function": f"0x{func:08x}",
        "prologue": code[0]["insn"] if code else None,
        "pic": base,
        "got_base": f"0x{got_base:08x}",
        "slots": slots,
        "loop": lb,
        "loop_count": lb.get("iterations"),
        "calls": calls,
        "code": code,
    }
    if imm_reg is not None:
        rec["immediate_r0"] = imm_reg
    return rec


# --------------------------------------------------------------------------- #
def build_a7s(blob: bytes) -> dict[str, Any]:
    table = TABLE
    ids = ids_of(blob, table)
    end = table + 4 * len(ids)
    prefix_start = table - 0x400
    prefix = [u32(blob, prefix_start + 4 * i) for i in range(256)]
    run = 0
    back = table - 4
    while u32(blob, back) == 0x43F9C622:
        run += 1
        back -= 4
    bss_lo, bss_hi = zero_run(blob, 0x43F9C622)
    gap = [u32(blob, end + 4 * i) for i in range(2)]
    companion = u32(blob, 0x44028C78)
    comp_ptrs = [u32(blob, companion + 4 * i) for i in range(len(ids))]

    sites = pic_sites(blob, table)
    assert len(sites) == 2, sites
    cons_a = consumer(blob, 0x437056EC, 0x437056F8, 0x437056FC, table,
                      got_base=0x44024540, slot_ldrs=[0x43705708, 0x43705716])
    cons_b = consumer(blob, 0x43705748, 0x43705754, 0x43705756, table,
                      got_base=0x44024540, slot_ldrs=[0x43705750, 0x4370575E],
                      imm_reg=0x0D)
    comp_sites = pic_sites(blob, companion)
    # el array de 256 punteros (0x43fef004..0x43fef404) se usa con limite 0x100
    pfx_code = insns(blob, 0x4373F1D0, 0x30)
    pfx_slot = slot_from(blob, 0x44024540, 0x4373F1EA)
    pfx_cmps = [i["insn"] for i in pfx_code if i["insn"].startswith("cmp")]
    return {
        "table": {"address": f"0x{table:08x}", "entries": len(ids),
                  "entry_size": 4, "second_field": f"0x{SECOND:04x}",
                  "end": f"0x{end:08x}", "ids": ids,
                  "ids_unique": len(set(ids)),
                  "ids_range": [min(ids), max(ids)]},
        "prefix_array": {"start": f"0x{prefix_start:08x}", "entries": 256,
                         "ends_at": f"0x{table:08x}",
                         "count_43f9c622": prefix.count(0x43F9C622),
                         "contiguous_43f9c622_before_table": run,
                         "all_in_zero_run": all(bss_lo <= p < bss_hi for p in prefix)},
        "zero_run": {"start": f"0x{bss_lo:08x}", "end": f"0x{bss_hi:08x}",
                     "size": bss_hi - bss_lo},
        "gap": {"span": [f"0x{end:08x}", f"0x{end + 8:08x}"],
                "words": [f"0x{v:08x}" for v in gap]},
        "companion_array": {"address": f"0x{companion:08x}",
                            "entries": len(comp_ptrs),
                            "end": f"0x{companion + 4 * len(comp_ptrs):08x}",
                            "pic_sites": [s["base"] for s in comp_sites],
                            "all_in_zero_run": all(bss_lo <= p < bss_hi for p in comp_ptrs),
                            "first": [f"0x{p:08x}" for p in comp_ptrs[:8]]},
        "prefix_array_consumer": {
            "function": "0x4373f1d0",
            "slot": pfx_slot,
            "bounds": pfx_cmps,
            "code": pfx_code,
        },
        "pic_sites": sites,
        "consumers": {"A": cons_a, "B": cons_b},
        "callers": {"A": bl_callers(blob, 0x437056EC),
                    "B": bl_callers(blob, 0x43705748)},
        "module_strings": strings_in(blob, 0x4373C000, 0x4373E400),
    }


def build_other(blob: bytes, table: int, func_a: int, ldr_a: int, add_a: int,
                func_b: int, ldr_b: int, add_b: int, got_base: int,
                slots_a: list[int], slots_b: list[int]) -> dict[str, Any]:
    ids = ids_of(blob, table)
    sites = pic_sites(blob, table)
    assert len(sites) == 2, sites
    ca = consumer(blob, func_a, ldr_a, add_a, table, got_base, slots_a)
    cb = consumer(blob, func_b, ldr_b, add_b, table, got_base, slots_b, imm_reg=0x0D)
    return {"table": {"address": f"0x{table:08x}", "entries": len(ids),
                      "end": f"0x{table + 4 * len(ids):08x}",
                      "ids": ids, "ids_unique": len(set(ids))},
            "pic_sites": sites,
            "consumers": {"A": ca, "B": cb},
            "callers": {"A": bl_callers(blob, func_a),
                        "B": bl_callers(blob, func_b)}}


def main() -> None:
    blobs = {k: p.read_bytes() for k, p in BLOBS.items()}
    a7s = blobs["a7s_fw320"]
    a6 = blobs["a6000_fw321"]
    a63 = blobs["a6300_fw201"]

    d7 = build_a7s(a7s)
    d6 = build_other(a6, TABLE_A6000, 0x436EB2CC, 0x436EB2D8, 0x436EB2DC,
                     0x436EB328, 0x436EB334, 0x436EB336, 0x4401EEE4,
                     [0x436EB2E8, 0x436EB2F6], [0x436EB330, 0x436EB33E])
    d63 = build_other(a63, TABLE_A6300, 0x43734BD8, 0x43734BE4, 0x43734BE8,
                      0x43734C34, 0x43734C40, 0x43734C42, 0x441FA214,
                      [0x43734BF4, 0x43734C02], [0x43734C3C, 0x43734C4A])

    # referencia negativa: los ids de registro de la matriz 0x43fee598 son 0x81
    reg_ids = [u16(a7s, u32(a7s, 0x43FEE598 + 0x14 * i) - 4) for i in range(69)]
    matrix_regs = {"distinct": sorted(set(reg_ids)), "count": len(reg_ids)}
    modes_a7s = [u32(a7s, 0x43FEE370 + 4 * i) for i in range(34)]

    ids7 = d7["table"]["ids"]
    ids6 = d6["table"]["ids"]
    ids63 = d63["table"]["ids"]

    data: dict[str, Any] = {
        "milestone": "S342",
        "title": ("0x43fef404 tiene dos consumidores PIC y es la tabla de ids de "
                  "Camera::Lens::ODL, no una tabla de tiempos"),
        "base": f"0x{BASE:08x}",
        "firmware": {k: {"sha256": sha256(BLOBS[k]), "size": len(blobs[k])}
                     for k in BLOBS},
        "a7s": d7,
        "a6000": d6,
        "a6300": d63,
        "cross_model": {
            "entries": {"a7s": len(ids7), "a6000": len(ids6), "a6300": len(ids63)},
            "a6000_subset_of_a7s": set(ids6) <= set(ids7),
            "a6000_missing": [f"0x{x:02x}" for x in sorted(set(ids7) - set(ids6))],
            "a6300_equals_a7s": ids63 == ids7,
            "loop_bounds": {"a7s": d7["consumers"]["A"]["loop_count"],
                            "a6000": d6["consumers"]["A"]["loop_count"],
                            "a6300": d63["consumers"]["A"]["loop_count"]},
        },
        "negatives": {
            "absolute_literal_refs": len(
                [i for i in range(len(a7s) - 3)
                 if u32(a7s, BASE + i) == TABLE]),
            "matrix_register_ids": matrix_regs,
            "ids_equal_matrix_register_ids": set(ids7) == set(reg_ids),
            "mode_codes_intersect_ids": sorted(set(modes_a7s) & set(ids7)),
            "mode_codes_count": len(modes_a7s),
            "write_sites_to_table": 0,
        },
        "verdicts": {
            "is_timing_table": False,
            "has_static_consumers": True,
            "consumer_count_per_model": 2,
            "loop_iterations_equal_entry_count": True,
            "indexed_by_drive_mode": False,
            "written_at_runtime_in_image": False,
            "subsystem": "Camera::Lens::ODL (INFERENCIA ALTA)",
            "s337_literal_negative": "correcto pero incompleto (PIC por add pc)",
            "s329_negative": "se mantiene",
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("El literal absoluto de la tabla sigue siendo 0: el negativo de S337 "
             "es correcto para literales, no para bases PIC."),
            ("Que la tabla pertenezca a Camera::Lens::ODL es INFERENCIA a partir de "
             "los llamadores y de las cadenas del init; no hay simbolo que lo nombre."),
            ("Los 69/47 punteros apuntan a una region `.bss` (2.4 MB a cero en la "
             "imagen): no se puede saber que objeto vive en cada direccion."),
            "No se asigna significado al campo 0x000d ni a los ids.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("A7S tabla", len(ids7), "entradas; consumidores",
          d7["callers"], "bucle", d7["consumers"]["A"]["loop_count"])
    print("A6000 tabla", len(ids6), "bucle", d6["consumers"]["A"]["loop_count"])
    print("A6300 tabla", len(ids63), "bucle", d63["consumers"]["A"]["loop_count"])
    print("S337 literal:", data["negatives"]["absolute_literal_refs"])


if __name__ == "__main__":
    main()
