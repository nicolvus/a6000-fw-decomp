#!/usr/bin/env python3
"""S315 - que listas de registros aplica el consumidor 0x436f44c4 y con que modo.

Continua S314: la tabla 0x43fee3f8 (95 registros) no es la unica. El consumidor
`0x436f44c4(obj, modo, lista)` recorre listas terminadas en NULL y aplica cada
registro. Se resuelven las tres llamadas y sus listas:

* 0x436f5422  modo 2  -> L1  = 0x43fee590 (1 registro, via GOT 0x440292b0)
* 0x436f5b32  modo 2  -> L95 = 0x43fee3f8 (95 registros, via getter 0x436f4588)
* 0x436f5b52  modo 0  -> L5  = 0x43fee578 (5 registros, via GOT 0x44025ec0)

Solo bytes. Sin firmware, sin camara.
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
OUT = Path(__file__).with_name("lists.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

CONSUMER = 0x436F44C4
GETTER_L95 = 0x436F4588
LISTS = {
    "L95": {"table": 0x43FEE3F8, "via": "getter 0x436f4588 -> GOT 0x4402c940"},
    "L5": {"table": 0x43FEE578, "via": "GOT 0x44025ec0"},
    "L1": {"table": 0x43FEE590, "via": "GOT 0x440292b0"},
}


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


def bl_calls(blob: bytes) -> list[tuple[int, int]]:
    out = []
    for off in range(0, len(blob) - 3, 2):
        h1, h2 = struct.unpack_from("<HH", blob, off)
        if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000:
            continue
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


def read_list(blob: bytes, table: int) -> dict:
    ptrs = []
    addr = table
    while u32(blob, addr) != 0:
        ptrs.append(u32(blob, addr))
        addr += 4
    records = []
    for p in ptrs:
        rec = blob[p - BASE:p - BASE + 6]
        records.append({"ptr": f"0x{p:08x}", "bytes": rec.hex(), "dev": rec[0],
                        "reg": struct.unpack_from("<H", rec, 2)[0], "data": rec[4]})
    return {"table": f"0x{table:08x}", "count": len(ptrs),
            "terminator": f"0x{addr:08x}", "records": records}


def signatures(blob: bytes) -> dict:
    a7 = A7S.read_bytes()
    out = {}
    for name, addr, n in [("consumer", CONSUMER, 24),
                          ("getter_L95", GETTER_L95, 16),
                          ("call_5422", 0x436F5422, 16),
                          ("call_5b32", 0x436F5B32, 16),
                          ("call_5b52", 0x436F5B52, 16)]:
        sig = a7[addr - BASE:addr - BASE + n]
        out[name] = {"address": f"0x{addr:08x}", "bytes": n,
                     "signature": sig.hex(), "a6000_hits": blob.count(sig)}
    return out


def main() -> None:
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()
    calls = [(a, t) for a, t in bl_calls(a7) if t == CONSUMER]
    call_sites = []
    for a, _ in calls:
        call_sites.append({"call": f"0x{a:08x}",
                           "context": insns(a7, a - 10, 14)})
    getter = insns(a7, GETTER_L95, 0x14)
    # GOT: base 0x44024540 + 0x8400 -> 0x4402c940 -> 0x43fee3f8
    got_l95 = {"base": "0x44024540", "offset": "0x8400", "slot": "0x4402c940",
               "value": f"0x{u32(a7, 0x4402C940):08x}"}
    got_l5 = {"slot": "0x44025ec0", "value": f"0x{u32(a7, 0x44025EC0):08x}"}
    got_l1 = {"slot": "0x440292b0", "value": f"0x{u32(a7, 0x440292B0):08x}"}
    decoded: dict = {}
    for name, meta in LISTS.items():
        table = meta["table"]
        assert isinstance(table, int)
        decoded[name] = {**meta, **read_list(a7, table)}
    data: dict = {
        "milestone": "S315",
        "title": "Tres listas de registros aplicadas por 0x436f44c4 segun el modo (L95/L5/L1)",
        "firmware": {"a7s": {"sha256": sha256(A7S), "size": len(a7)},
                     "a6000": {"sha256": sha256(A6000), "size": len(a6)}},
        "consumer": {"entry": f"0x{CONSUMER:08x}",
                     "signature": a7[CONSUMER - BASE:CONSUMER - BASE + 24].hex(),
                     "call_sites": call_sites,
                     "loop": insns(a7, 0x436F4526, 0x14),
                     "reads": "ldrb [r3] | ldrh [r3,#2] | ldrb [r3,#4]"},
        "getter_L95": {"entry": f"0x{GETTER_L95:08x}", "insn": getter, **got_l95},
        "lists": decoded,
        "got": {"L5": got_l5, "L1": got_l1},
        "modes": {"0x436f5422": 2, "0x436f5b32": 2, "0x436f5b52": 0},
        "a6000_presence": signatures(a6),
        "limits": [
            "Estatico: sin firmware ejecutado, sin camara, sin flasheo.",
            ("Modo 2 del consumidor NO es por si mismo el modo silent: es el argumento r1 "
             "de 0x436f44c4; el enlace con el selector 0x43826d58 queda NO_VERIFICADO."),
            "La semantica fisica de los registros (reg/data) sigue NO_VERIFICADA.",
            ("La identidad de las tres listas como 'full/subset' es INFERENCIA a partir de "
             "los modos de llamada, no una afirmacion de firmware."),
        ],
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print("callers consumidor:", [c["call"] for c in call_sites])
    for name in LISTS:
        lst = data["lists"][name]
        print(name, lst["count"], "terminador", lst["terminator"],
              [hex(r["reg"]) for r in lst["records"]][:8])
    print("A6000 hits:", {k: v["a6000_hits"] for k, v in data["a6000_presence"].items()})


if __name__ == "__main__":
    main()
