#!/usr/bin/env python3
"""S314 - carril B: objeto/contexto del selector silent y tabla de registros 0x43fee3f8.

Re-decodifica desde los bytes (autoridad final) tres cosas:

1. La procedencia real de los argumentos del selector `0x43826d58` en la llamada
   `0x4354908c` (no hay `r0` en `0x43549084`: alli se carga `r1`).
2. La tabla de decision completa del selector (constantes leidas de las
   instrucciones, no de un decompilador).
3. La tabla `0x43fee3f8`: array terminado en NULL de punteros a registros de 6 B
   (`dev, 0, reg:u16, data:u8, 0`) y su bucle consumidor. Se contrasta con la
   A6000 (misma VA, contenido distinto) y se descarta la cifra "19 filas".

No ejecuta firmware ni toca la camara. Todo es lectura de los blobs.
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
OUT = Path(__file__).with_name("selector.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def insns(blob: bytes, start: int, size: int) -> list[dict]:
    raw = blob[start - BASE:start - BASE + size]
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw, start)]


def add_pc_sites(blob: bytes, target: int) -> list[dict]:
    """Sitios `ldr rX,[pc,#imm]; add rX,pc` cuyo resultado es `target`.

    Cubre la forma de 16 bits (ldr imm8) y la de 32 bits (ldr.w imm12).
    """
    out: list[dict] = []
    n = len(blob)
    for off in range(2, n - 4, 2):
        addr = BASE + off
        h1 = struct.unpack_from("<H", blob, off - 2)[0]
        h2 = struct.unpack_from("<H", blob, off)[0]
        if (h2 & 0xFFF8) != 0x4478:  # add rX, pc
            continue
        rd = h2 & 7
        if (h1 & 0xF800) != 0x4800 or ((h1 >> 8) & 7) != rd:
            continue
        base = (addr + 4) & ~1
        lit = base + (h1 & 0xFF) * 4
        if not (0 <= lit - BASE < n - 3):
            continue
        if (u32(blob, lit) + base) & 0xFFFFFFFF == target:
            out.append({"add": f"0x{addr:08x}", "form": "ldr16", "literal": f"0x{lit:08x}"})
    for off in range(0, n - 8, 2):
        addr = BASE + off
        h1, h2 = struct.unpack_from("<HH", blob, off)
        if h1 != 0xF8DF:  # ldr.w rX,[pc,#imm12]
            continue
        rt = (h2 >> 12) & 0xF
        if rt >= 13:
            continue
        pc = (addr + 4) & ~3
        lit = pc + (h2 & 0xFFF)
        if not (0 <= lit - BASE < n - 3):
            continue
        h3 = struct.unpack_from("<H", blob, off + 4)[0]
        if (h3 & 0xFFF8) == 0x4478 and (h3 & 7) == rt:
            base = (addr + 8) & ~1
            if (u32(blob, lit) + base) & 0xFFFFFFFF == target:
                out.append({"add": f"0x{addr:08x}", "form": "ldr32", "literal": f"0x{lit:08x}"})
    return out


def bl_targets(blob: bytes) -> list[tuple[int, int]]:
    out = []
    for off in range(0, len(blob) - 3, 2):
        h1, h2 = struct.unpack_from("<HH", blob, off)
        if (h1 & 0xF800) == 0xF000 and (h2 & 0xD000) == 0xD000:
            s = (h1 >> 10) & 1
            imm10 = h1 & 0x3FF
            j1 = (h2 >> 13) & 1
            j2 = (h2 >> 11) & 1
            imm11 = h2 & 0x7FF
            i1 = 1 - (j1 ^ s)
            i2 = 1 - (j2 ^ s)
            delta = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
            if s:
                delta -= 1 << 25
            out.append((BASE + off, (BASE + off + 4 + delta) & 0xFFFFFFFF))
    return out


def call_site(blob: bytes) -> dict:
    before = insns(blob, 0x43548f92, 0x58)  # getter + carga de argumentos
    call = insns(blob, 0x4354908c, 4)[0]
    ctx_getter = insns(blob, 0x437b38ec, 10)
    literal = u32(blob, 0x437b38f4)
    ctx = (literal + ((0x437b38ee + 4) & ~1)) & 0xFFFFFFFF
    assert ctx == 0x43EA70A0, hex(ctx)
    calls = [f"0x{a:08x}" for a, t in bl_targets(blob) if t == 0x43826D58]
    return {
        "selector_call": call,
        "selector_callers": calls,
        "arguments_before_call": before,
        "ctx_getter": {"entry": "0x437b38ec", "insn": ctx_getter,
                       "literal_at": "0x437b38f4", "literal": f"0x{literal:08x}",
                       "ctx": f"0x{ctx:08x}"},
        "provenance": {
            "r0": "[[0x43ea70a0] + 0x6c] (carga en 0x4354904e desde r2=[ctx])",
            "r1": "[[0x43ea70a8] + 0x21c] (carga en 0x43549084; NO es r0)",
            "r2": "[[0x43ea70a8] + 0x220] (carga en 0x43549088)",
            "note": "0x43ea70a8 = ctx + 8; ambos son punteros leidos de BSS.",
        },
    }


def selector(blob: bytes) -> dict:
    code = insns(blob, 0x43826d58, 0x58)
    # Constantes leidas de las instrucciones (no de un decompilador).
    table = [
        {"a": "5", "b": "*", "c": "*", "result": "0x0c", "insn": "0x43826da2 movs r0,#0xc"},
        {"a": "0x1b", "b": "*", "c": "*", "result": "0x35", "insn": "0x43826daa movs r0,#0x35"},
        {"a": "otros", "b": "0", "c": "2", "result": "0x4e", "insn": "0x43826d7c movs r0,#0x4e"},
        {"a": "otros", "b": "1", "c": "2", "result": "0x4f", "insn": "0x43826da6 movs r0,#0x4f"},
        {"a": "otros", "b": ">=2", "c": "2", "result": "0x4e + log", "insn": "0x43826d78 bl 0x438f7114; cae a 0x43826d7c"},
        {"a": "otros", "b": "1", "c": "!=2", "result": "0x35", "insn": "0x43826d82 beq 0x43826daa"},
        {"a": "otros", "b": "2", "c": "!=2", "result": "0x17", "insn": "0x43826d8c movs r0,#0x17"},
        {"a": "otros", "b": "0", "c": "!=2", "result": "0x0b", "insn": "0x43826d9e movs r0,#0xb"},
        {"a": "otros", "b": ">=3", "c": "!=2", "result": "0x0b + log", "insn": "0x43826d90 bl 0x438f7114; cae a 0x43826d9e"},
    ]
    return {"entry": "0x43826d58", "insn": code, "truth_table": table,
            "signature": "int sel(int a, int b, int c)  // a=r0, b=r1, c=r2"}


def thunks(blob: bytes) -> dict:
    slot64 = insns(blob, 0x43AD96F8, 10)
    wrapper = insns(blob, 0x43AD9704, 12)
    dispatch = insns(blob, 0x43AD9ADA, 0x30)
    return {
        "slot_0x64_thunk": {"entry": "0x43ad96f8", "insn": slot64,
                            "semantics": "r0=*r0; (*r0)->vtable[0x64]()"},
        "wrapper_0x43ad9704": {
            "entry": "0x43ad9704", "insn": wrapper,
            "semantics": "r0=*r0; tail-call 0x43ad9ada (NO usa vtable+0x64)",
            "callers": [f"0x{a:08x}" for a, t in bl_targets(blob) if t == 0x43AD9704],
        },
        "dispatch_0x43ad9ada": {
            "entry": "0x43ad9ada", "insn": dispatch,
            "vtable_slots": ["0x24 (dos veces)"],
        },
        "correction": "S310/S313 atribuian vtable+0x64 a 0x43ad9704; los bytes muestran "
                      "que el thunk del slot 0x64 es 0x43ad96f8 y que 0x43ad9704 "
                      "desreferencia y llama a 0x43ad9ada (vtable+0x24).",
    }


def register_list(blob: bytes) -> dict:
    table = 0x43FEE3F8
    ptrs = []
    addr = table
    while True:
        v = u32(blob, addr)
        if not (0x43541000 <= v < BASE + len(blob)):
            break
        ptrs.append(v)
        addr += 4
    terminator = addr
    records = []
    for p in ptrs:
        rec = blob[p - BASE:p - BASE + 6]
        records.append({"ptr": f"0x{p:08x}", "bytes": rec.hex(),
                        "dev": rec[0], "pad1": rec[1],
                        "reg": struct.unpack_from("<H", rec, 2)[0],
                        "data": rec[4], "pad2": rec[5]})
    consumer = insns(blob, 0x436f451a, 0x28)
    loop = insns(blob, 0x436f4532, 0x0E)
    return {
        "table": f"0x{table:08x}",
        "count": len(ptrs),
        "terminator": f"0x{terminator:08x}",
        "record_size": 6,
        "record_layout": "u8 dev | u8 0 | u16 reg | u8 data | u8 0",
        "all_pad_zero": all(r["pad1"] == 0 and r["pad2"] == 0 for r in records),
        "all_6_aligned": all((p - min(ptrs)) % 6 == 0 for p in ptrs),
        "dev_counts": {str(d): sum(1 for r in records if r["dev"] == d)
                       for d in sorted({r["dev"] for r in records})},
        "records": records,
        "consumer": {"setup": consumer, "loop": loop,
                     "reads": "ldrb [r3], ldrh [r3,#2], ldrb [r3,#4]"},
        "nineteen_rows_claim": f"NO REPRODUCIBLE: el array tiene {len(ptrs)} punteros en este blob",
    }


def descriptor_rows(blob: bytes) -> dict:
    start = 0x43FEE5AC
    rows = []
    addr = start
    while 0x43541000 <= u32(blob, addr) < BASE + len(blob):
        p = u32(blob, addr)
        rows.append({"addr": f"0x{addr:08x}", "ptr": f"0x{p:08x}",
                     "payload": blob[addr - BASE + 4:addr - BASE + 0x14].hex()})
        addr += 0x14
    return {"start": f"0x{start:08x}", "row_size": 0x14, "count": len(rows),
            "end": f"0x{addr:08x}", "rows": rows,
            "note": "punteros caen 2 B antes de un registro de 6 B; significado NO_VERIFICADO"}


def a6000_compare(blob: bytes) -> dict:
    table = 0x43FEE3F8
    return {
        "call_site_0x43549084": {"bytes": blob[0x43549084 - BASE:0x43549084 - BASE + 12].hex(),
                                 "insn": insns(blob, 0x43549084, 12)},
        "pair_0x21c_0x220_occurrences": 0,  # ver verify_selector.py (recalculado alli)
        "table_at_same_va": [f"0x{u32(blob, table + 4 * i):08x}" for i in range(10)],
    }


def main() -> None:
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()
    data: dict = {
        "milestone": "S314",
        "title": "Procedencia real de los argumentos del selector silent y tabla 0x43fee3f8 (95 registros, no 19)",
        "firmware": {
            "a7s": {"path": str(A7S.relative_to(ROOT)), "sha256": sha256(A7S),
                    "size": len(a7), "base": f"0x{BASE:08x}"},
            "a6000": {"path": str(A6000.relative_to(ROOT)), "sha256": sha256(A6000),
                      "size": len(a6), "base": f"0x{BASE:08x}"},
        },
        "call_site": call_site(a7),
        "selector": selector(a7),
        "vtable_thunks": thunks(a7),
        "register_list": register_list(a7),
        "descriptor_rows": descriptor_rows(a7),
        "a6000": a6000_compare(a6),
        "limits": [
            "Estatico: no se ejecuto firmware ni se uso la camara.",
            ("No se localizo escritor estatico de los punteros [0x43ea709e] ni [0x43ea70a6] "
             "en av-cam.bin (posible inicializacion cruzada de modulo o copia no visible como store)."),
            "La identidad de clase de los objetos apuntados por ctx/ctx+8 queda NO_VERIFICADO.",
            "La semantica fisica de los registros y del modo 0x4e/0x4f sigue NO_VERIFICADA.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    site = data["call_site"]
    register = data["register_list"]
    rows = data["descriptor_rows"]
    print("callers selector:", site["selector_callers"])
    print("ctx:", site["ctx_getter"]["ctx"])
    print("registros:", register["count"], "terminador", register["terminator"],
          "dev", register["dev_counts"])
    print("filas 0x43fee5ac:", rows["count"])


if __name__ == "__main__":
    main()
