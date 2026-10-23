#!/usr/bin/env python3
"""S321 - carril B: la "tabla de 68 filas" de 0x43fee5ac y su indice/consumidor.

Hipotesis de partida (cola S321): existe una tabla independiente de 68 filas
`{ptr, 16 B}` en `0x43fee5ac` relacionada con los drive modes.

La re-decodificacion desde bytes (autoridad final) muestra que **no** existe tal
tabla: `0x43fee5ac` es la fila 1 de la matriz de registros por modo que ya
documento S302, cuya base real es `0x43fee598` con 69 filas de 0x14 B
(`{u32 destino; u8 valores[16]}`) y terminador 0 en `0x43feeafc`.

Se verifica ademas:

* El campo de 4 B de cada fila es el **destino** del byte que se escribe, y
  apunta al campo `data` (offset +4) de un registro de 6 B
  `{dev, 0, reg:u16, data, 0}` del pool contiguo `0x44021ec2..0x44022108`
  (98 registros; 97 x `0x81` y 1 x `0x83`).
* El consumidor es el metodo virtual slot 40 de la clase con vtable
  `0x43fce050` (S316): `0x436f3928`. Traduce modo->columna con el mapa
  `0x43c9c5b5` (82 B) y escribe `fila[4+columna]` en el destino de cada fila.
  Un segundo bucle identico, con la puerta `[obj+0x2b0]`, aplica una segunda
  matriz desde el slot `0x44026088` (en el blob: ceros = runtime).
* La A6000 tiene la **misma clase** (vtable `0x43fcc090`, 45 entradas, misma
  disposicion), slot 40 = `0x436d6570`, matriz primaria `0x43fe9b74` (59 filas,
  slot `0x44022f8c`), segunda matriz en `0x44026694` (ceros) y puerta
  `[obj+0x266]`. **No tiene mapa modo->columna**: recibe la columna directa.

No ejecuta firmware ni toca la camara: solo lectura de los blobs.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("matrix_rows.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

# Direcciones ya fijadas por S302/S314/S315/S316 (se re-verifican aquí).
MATRIX_A7S = 0x43FEE598
MATRIX_68 = 0x43FEE5AC          # supuesta base de la cola S321
MATRIX_A6000 = 0x43FE9B74
MODE_MAP = 0x43C9C5B5
POOL_START = 0x44021EC2
VTABLE_A7S = 0x43FCE050
VTABLE_A6000 = 0x43FCC090
L95 = 0x43FEE3F8
L5 = 0x43FEE578
L1 = 0x43FEE590
MODE_CODES = [0x0B, 0x37, 0x35, 0x38, 0x13, 0x1F, 0x05, 0x18, 0x10, 0x1A, 0x07,
              0x19, 0x32, 0x34, 0x33, 0x46, 0x01, 0x30, 0x03, 0x31, 0x0A, 0x36,
              0x0F, 0x12, 0x3F, 0x44, 0x45, 0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51,
              0x08]
STRIDE = 0x14
PAYLOAD = 16


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


def dis(blob: bytes, start: int, size: int) -> list[dict]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw(blob, start, size), start)]


def ldr_literal(blob: bytes, addr: int) -> tuple[int, int]:
    """Direccion del literal de un `ldr rX,[pc,#imm]` de 16 bits."""
    h = u16(blob, addr)
    assert (h & 0xF800) == 0x4800, f"0x{addr:08x} no es ldr pc-rel"
    return ((addr + 4) & ~3) + (h & 0xFF) * 4, h & 0xFF


def add_pc_target(blob: bytes, addr: int) -> int:
    """Resultado de un `add rX,pc` de 16 bits: PC=(addr+4) bit1=0, bit0=0."""
    h = u16(blob, addr)
    assert (h & 0xFFF8) == 0x4478, f"0x{addr:08x} no es add pc"
    return (addr + 4) & ~1


def table_rows(blob: bytes, base: int, limit: int = 200) -> list[dict]:
    out: list[dict] = []
    for k in range(limit):
        addr = base + STRIDE * k
        header = u32(blob, addr)
        if header == 0:
            return out
        out.append({"index": k, "addr": f"0x{addr:08x}", "dest": f"0x{header:08x}",
                    "payload_hex": raw(blob, addr + 4, PAYLOAD).hex()})
    raise SystemExit("tabla sin terminador")


def pool_records(blob: bytes, start: int) -> list[dict]:
    out: list[dict] = []
    addr = start
    while True:
        b = raw(blob, addr, 6)
        if len(b) < 6 or b[0] not in (0x81, 0x83) or b[1] != 0:
            return out
        out.append({"addr": f"0x{addr:08x}", "dev": b[0],
                    "reg": u16(blob, addr + 2), "data": b[4]})
        addr += 6


def ptr_list(blob: bytes, base: int, limit: int = 200) -> list[str]:
    out: list[str] = []
    for k in range(limit):
        p = u32(blob, base + 4 * k)
        if p == 0:
            return out
        out.append(f"0x{p:08x}")
    raise SystemExit("lista sin terminador")


def refs_to(blob: bytes, value: int) -> list[str]:
    """Literales absolutos y `ldr/add pc` cuyo resultado es `value`."""
    out: list[str] = []
    pat = struct.pack("<I", value)
    i = 0
    while True:
        j = blob.find(pat, i)
        if j < 0:
            break
        out.append(f"lit@0x{BASE + j:08x}")
        i = j + 1
    n = len(blob)
    for off in range(2, n - 4, 2):
        addr = BASE + off
        h1 = struct.unpack_from("<H", blob, off - 2)[0]
        h2 = struct.unpack_from("<H", blob, off)[0]
        if (h2 & 0xFFF8) != 0x4478:
            continue
        reg = h2 & 7
        if (h1 & 0xF800) != 0x4800 or ((h1 >> 8) & 7) != reg:
            continue
        base = (addr + 4) & ~1
        lit = base + (h1 & 0xFF) * 4
        if not (0 <= lit - BASE < n - 3):
            continue
        if (u32(blob, lit) + base) & 0xFFFFFFFF == value:
            out.append(f"pic@0x{addr:08x}")
    return out


def main() -> None:
    a7s = A7S.read_bytes()
    a6 = A6000.read_bytes()

    # --- 1. La tabla de la cola: 68 filas vs base real ---------------------
    rows = table_rows(a7s, MATRIX_A7S)
    rows68 = table_rows(a7s, MATRIX_68)
    terminator = MATRIX_A7S + STRIDE * len(rows)
    dests = [int(r["dest"], 16) for r in rows]
    regs = [u16(a7s, d - 2) for d in dests]
    devs = [raw(a7s, d - 4, 1)[0] for d in dests]
    payloads = [bytes.fromhex(r["payload_hex"]) for r in rows]

    # --- 2. Pool de registros de 6 B --------------------------------------
    pool = pool_records(a7s, POOL_START)
    pool_addrs = {int(p["addr"], 16) for p in pool}
    targeted = {d - 4 for d in dests}

    # --- 3. Listas del mismo objeto (S315) --------------------------------
    l95 = ptr_list(a7s, L95)
    l5 = ptr_list(a7s, L5)
    l1 = ptr_list(a7s, L1)

    # --- 4. Consumidor A7S -------------------------------------------------
    body_a7s = dis(a7s, 0x436F3928, 0x3C)
    map_lit, _ = ldr_literal(a7s, 0x436F3928)
    map_base = add_pc_target(a7s, 0x436F392C)
    map_addr = (u32(a7s, map_lit) + map_base) & 0xFFFFFFFF

    slot_base_lit, _ = ldr_literal(a7s, 0x436F392A)
    slot_base = (u32(a7s, slot_base_lit) + add_pc_target(a7s, 0x436F392E)) & 0xFFFFFFFF
    slot1_off, _ = ldr_literal(a7s, 0x436F3932)
    slot1_off = u32(a7s, slot1_off)
    slot1 = slot_base + slot1_off

    gate_insn = dis(a7s, 0x436F394E, 4)[0]
    slot2_off, _ = ldr_literal(a7s, 0x436F394E)
    slot2_off = u32(a7s, slot2_off)
    slot2 = slot_base + slot2_off

    mode_map = raw(a7s, map_addr, 0x52)

    # --- 5. Consumidor A6000 ----------------------------------------------
    body_a6 = dis(a6, 0x436D6570, 0x3C)
    gbase_lit, _ = ldr_literal(a6, 0x436D6570)
    gbase = (u32(a6, gbase_lit) + add_pc_target(a6, 0x436D6574)) & 0xFFFFFFFF
    off1, _ = ldr_literal(a6, 0x436D6584)
    off1 = u32(a6, off1)
    slot1_a6 = gbase + off1
    off2, _ = ldr_literal(a6, 0x436D65A0)
    off2 = u32(a6, off2)
    slot2_a6 = gbase + off2
    rows_a6 = table_rows(a6, MATRIX_A6000)
    dests_a6 = [int(r["dest"], 16) for r in rows_a6]

    # --- 6. Vtables --------------------------------------------------------
    def vtable(blob: bytes, base: int, limit: int = 64) -> list[int | None]:
        out: list[int | None] = []
        for k in range(limit):
            e = u32(blob, base + 4 * k)
            if e == 0:
                out.append(None)
                return out
            out.append(e)
        return out

    vt_a7s = vtable(a7s, VTABLE_A7S)
    vt_a6 = vtable(a6, VTABLE_A6000)

    silent_cols = {hex(m): mode_map[m] for m in (0x4C, 0x4D, 0x4E, 0x4F)}
    col_modes: dict[int, list[int]] = {}
    for idx, col in enumerate(mode_map):
        col_modes.setdefault(col, []).append(idx)

    data = {
        "milestone": "S321",
        "title": "La 'tabla de 68 filas' de 0x43fee5ac es la fila 1 de la matriz "
                 "de 69 filas de 0x43fee598",
        "base": f"0x{BASE:08x}",
        "firmware": {
            "a7s_fw320": {"path": str(A7S.relative_to(ROOT)), "sha256": sha256(A7S),
                          "size": len(a7s)},
            "a6000_fw321": {"path": str(A6000.relative_to(ROOT)), "sha256": sha256(A6000),
                            "size": len(a6)},
        },
        "matrix_a7s": {
            "base": f"0x{MATRIX_A7S:08x}",
            "stride": STRIDE,
            "header_bytes": 4,
            "payload_bytes": PAYLOAD,
            "rows": len(rows),
            "terminator": f"0x{terminator:08x}",
            "terminator_value": u32(a7s, terminator),
            "queue_base_0x43fee5ac": {
                "addr": f"0x{MATRIX_68:08x}",
                "is_row_index": (MATRIX_68 - MATRIX_A7S) // STRIDE,
                "rows_from_there": len(rows68),
                "terminator": f"0x{MATRIX_A7S + STRIDE * (len(rows68) + 1):08x}",
                "literal_refs": refs_to(a7s, MATRIX_68),
            },
            "literal_refs_base": refs_to(a7s, MATRIX_A7S),
            "rows_detail": [
                {"index": r["index"], "addr": r["addr"], "dest": r["dest"],
                 "record": f"0x{d - 4:08x}", "dev": dv, "reg": rg,
                 "data_initial": raw(a7s, d, 1)[0],
                 "payload_hex": r["payload_hex"]}
                for r, d, dv, rg in zip(rows, dests, devs, regs)
            ],
            "unique_dests": len(set(dests)),
            "record_layout": {
                "size": 6,
                "fields": "dev:u8, 0, reg:u16, data:u8, 0",
                "dest_is": "&data (registro+4)",
                "dev_histogram": {hex(k): devs.count(k) for k in sorted(set(devs))},
                "alignment_mod6": sorted({(d - 4 - POOL_START) % 6 for d in dests}),
            },
            "payload_last_byte_all_zero": all(p[15] == 0 for p in payloads),
            "payload_columns_used": sorted({i for p in payloads for i in range(16)
                                            if p[i] != 0}),
        },
        "record_pool": {
            "start": f"0x{POOL_START:08x}",
            "end": f"0x{int(pool[-1]['addr'], 16):08x}",
            "count": len(pool),
            "dev_histogram": {hex(k): sum(1 for p in pool if p["dev"] == k)
                              for k in sorted({p["dev"] for p in pool})},
            "targeted_by_matrix": len(targeted),
            "not_targeted": [p["addr"] for p in pool if int(p["addr"], 16) not in targeted],
            "dev83_records": [p for p in pool if p["dev"] == 0x83],
            "all_targets_in_pool": targeted <= pool_addrs,
            "all_targets_aligned": sorted({(d - 4 - POOL_START) % 6 for d in dests}),
        },
        "register_lists": {
            "L95": {"addr": f"0x{L95:08x}", "count": len(l95), "first": l95[0]},
            "L5": {"addr": f"0x{L5:08x}", "count": len(l5), "ptrs": l5},
            "L1": {"addr": f"0x{L1:08x}", "count": len(l1), "ptrs": l1},
            "pool_not_in_L95": [p["addr"] for p in pool
                                if p["addr"] not in set(l95)],
            "matrix_targets_in_L95": len(targeted & {int(p, 16) for p in l95}),
            "matrix_targets_only_in_L5": sorted(
                f"0x{x:08x}" for x in targeted - {int(p, 16) for p in l95})
        },
        "consumer_a7s": {
            "function": "0x436f3928",
            "instructions": body_a7s,
            "map_addr": f"0x{map_addr:08x}",
            "map_len": len(mode_map),
            "map_hex": mode_map.hex(),
            "slot_base": f"0x{slot_base:08x}",
            "slot1_off": f"0x{slot1_off:x}",
            "slot1": f"0x{slot1:08x}",
            "slot1_value": f"0x{u32(a7s, slot1):08x}",
            "gate_field": "+0x2b0",
            "gate_insn": gate_insn["insn"],
            "slot2_off": f"0x{slot2_off:x}",
            "slot2": f"0x{slot2:08x}",
            "slot2_value": f"0x{u32(a7s, slot2):08x}",
            "slot2_bytes_nonzero": sum(1 for b in raw(a7s, u32(a7s, slot2), 0x40) if b),
            "vtable_entry": next((i for i, e in enumerate(vt_a7s)
                                  if e == 0x436F3928 + 1), None),
            "vtable_offset": hex(4 * next((i for i, e in enumerate(vt_a7s)
                                          if e == 0x436F3928 + 1), 0)),
        },
        "consumer_a6000": {
            "function": "0x436d6570",
            "instructions": body_a6,
            "slot_base": f"0x{gbase:08x}",
            "slot1_off": f"0x{off1:x}",
            "slot1": f"0x{slot1_a6:08x}",
            "slot1_value": f"0x{u32(a6, slot1_a6):08x}",
            "gate_field": "+0x266",
            "slot2_off": f"0x{off2:x}",
            "slot2": f"0x{slot2_a6:08x}",
            "slot2_value": f"0x{u32(a6, slot2_a6):08x}",
            "vtable_entry": next((i for i, e in enumerate(vt_a6)
                                  if e == 0x436D6570 + 1), None),
            "matrix_base": f"0x{MATRIX_A6000:08x}",
            "matrix_rows": len(rows_a6),
            "unique_dests": len(set(dests_a6)),
            "record_layout": {
                "size": 4,
                "fields": "reg:u16, data:u8, 0",
                "dest_is": "&data (registro+2)",
                "alignment_mod4": sorted({(d - 2) % 4 for d in dests_a6}),
                "regs": [u16(a6, d - 2) for d in dests_a6],
            },
            "has_mode_map": False,
            "map_insn_present": any("ldrb r1, [r2, r1]" in i["insn"] for i in body_a6),
        },
        "vtables": {
            "a7s": {"base": f"0x{VTABLE_A7S:08x}", "entries": len(vt_a7s) - 1},
            "a6000": {"base": f"0x{VTABLE_A6000:08x}", "entries": len(vt_a6) - 1},
            "same_length": len(vt_a7s) == len(vt_a6),
            "entry40_a7s": f"0x{vt_a7s[40]:08x}",
            "entry40_a6000": f"0x{vt_a6[40]:08x}",
        },
        "mode_columns": {
            "mode_codes": [f"0x{m:02x}" for m in MODE_CODES],
            "codes_to_column": {f"0x{m:02x}": mode_map[m] for m in MODE_CODES},
            "distinct_columns_for_34_codes": sorted({mode_map[m] for m in MODE_CODES}),
            "columns_in_map": sorted(set(mode_map)),
            "max_column": max(mode_map),
            "silent_columns": silent_cols,
            "modes_in_column_1": [f"0x{m:02x}" for m in col_modes[1]],
            "silent_shares_column_with": [f"0x{m:02x}" for m in col_modes[1]
                                          if m not in (0x4E, 0x4F)],
            "any_column_exclusive_to_silent": any(
                set(v) <= {0x4E, 0x4F} for v in col_modes.values()),
        },
        "scope_limit": [
            "Solo lectura estatica de los blobs; sin runtime, camara ni flasheo.",
            ("La segunda matriz (slot2) esta a cero en el blob: su contenido y su "
             "poblador son NO_VERIFICADOS."),
            ("No se atribuye significado fisico a ninguna columna ni a ningun "
             "registro; 'columna' es solo el indice del byte de payload."),
            "La equivalencia modo A7S <-> modo A6000 no se afirma.",
            "S51 (A/B/C) no cambia.",
        ],
    }

    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"escrito {OUT.name}: {len(rows)} filas, pool {len(pool)}, "
          f"slot1 0x{slot1:08x}->0x{u32(a7s, slot1):08x}, "
          f"vtable A7S {len(vt_a7s) - 1} / A6000 {len(vt_a6) - 1}")


if __name__ == "__main__":
    main()
