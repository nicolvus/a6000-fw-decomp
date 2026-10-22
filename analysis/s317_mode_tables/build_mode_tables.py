#!/usr/bin/env python3
"""S317 - el indice obj+0x2b4 y las tres tablas de 0x1c B por modo.

`0x436f618c(obj, idx, modo)` usa `idx` como indice (stride 0x1c) en tres tablas
paralelas y lee `u32 @+0x14` y `u16 @+0x18` de cada una:

* T1 0x43bbeb6e -> destino obj+0x16 (llama 0x436f5f30)
* T3 0x43bbef32 -> destino obj+0xa5 (tail-call 0x436f6140)
* T2 0x43bbf2ea -> destino obj+0x2e (llama 0x436f5f30)

T3->T2 dista exactamente 34*0x1c = 0x3b8 (34 filas). T1->T3 dista 0x3c4
(34 filas + 0xc de separacion). La base calculada por `add pc` cae 2 B antes
de la alineacion natural; se documentan ambas y NO se elige una sin runtime.

Solo bytes. Sin firmware ni camara.
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
OUT = Path(__file__).with_name("mode_tables.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

ENTRY = 0x436F618C
TABLES: dict = {
    "T1": {"computed": 0x43BBEB6E, "dest": "obj+0x16", "callee": "0x436f5f30"},
    "T3": {"computed": 0x43BBEF32, "dest": "obj+0xa5", "callee": "0x436f6140"},
    "T2": {"computed": 0x43BBF2EA, "dest": "obj+0x2e", "callee": "0x436f5f30"},
}
STRIDE = 0x1C


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(blob: bytes, a: int) -> int:
    return struct.unpack_from("<H", blob, a - BASE)[0]


def u32(blob: bytes, a: int) -> int:
    return struct.unpack_from("<I", blob, a - BASE)[0]


def insns(blob: bytes, start: int, size: int) -> list[dict]:
    raw = blob[start - BASE:start - BASE + size]
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw, start)]


def rows(blob: bytes, base: int, n: int) -> list[dict]:
    out = []
    for i in range(n):
        a = base + i * STRIDE
        out.append({"index": i, "addr": f"0x{a:08x}",
                    "w0": f"0x{u32(blob, a):08x}",
                    "w4": f"0x{u32(blob, a + 4):08x}",
                    "u32_14": f"0x{u32(blob, a + 0x14):08x}",
                    "u16_18": f"0x{u16(blob, a + 0x18):04x}",
                    "u16_1a": f"0x{u16(blob, a + 0x1a):04x}"})
    return out


def writers_2b4(blob: bytes) -> list[dict]:
    """Sitios `str* [rX,#0x2b4]` (codificacion Thumb2) en el blob."""
    out = []
    for i in range(len(blob) - 4):
        if blob[i + 1] != 0xF8 or blob[i + 2] != 0xB4 or (blob[i + 3] & 0xF0) != 0x20:
            continue
        a = BASE + i
        decoded = insns(blob, a, 4)
        if decoded and decoded[0]["insn"].startswith("str"):
            out.append({"addr": f"0x{a:08x}", "insn": decoded[0]["insn"]})
    return out


def main() -> None:
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()
    entry = insns(a7, ENTRY, 0x50)
    # recomputar las tres bases desde sus literales
    computed = {}
    for ldr, imm, add, name in [
            (0x436F61A2, 0x48, 0x436F61AA, "T1"),
            (0x436F61BA, 0x34, 0x436F61C2, "T2"),
            (0x436F61CE, 0x24, 0x436F61D6, "T3")]:
        la = ((ldr + 4) & ~3) + imm
        pc = (add + 4) & ~3
        computed[name] = (u32(a7, la) + pc) & 0xFFFFFFFF
    for name, base in computed.items():
        expected = TABLES[name]["computed"]
        assert isinstance(expected, int) and base == expected, (name, hex(base))
    tables = {}
    for name, meta in TABLES.items():
        base = meta["computed"]
        aligned = (base + 3) & ~3
        tables[name] = {**meta, "aligned_candidate": f"0x{aligned:08x}",
                        "rows_computed_base": rows(a7, base, 3),
                        "rows_aligned": rows(a7, aligned, 3)}
    data: dict = {
        "milestone": "S317",
        "title": "obj+0x2b4 indexa tres tablas paralelas de 0x1c B (34 filas)",
        "firmware": {"a7s": {"sha256": sha256(A7S), "size": len(a7)},
                     "a6000": {"sha256": sha256(A6000), "size": len(a6)}},
        "entry": {"address": f"0x{ENTRY:08x}", "insn": entry,
                  "signature": "0x436f618c(obj /*r0*/, idx /*r1*/, modo /*r2*/)",
                  "stride": f"0x{STRIDE:02x}",
                  "fields": {"u32": "+0x14", "u16": "+0x18"},
                  "note": "muls r5,r2,r5 con r2=0x1c en 0x436f61a6"},
        "tables": tables,
        "spacing": {"T3_to_T2": f"0x{0x43BBF2EA - 0x43BBEF32:03x}",
                    "T3_to_T2_rows": (0x43BBF2EA - 0x43BBEF32) // STRIDE,
                    "T1_to_T3": f"0x{0x43BBEF32 - 0x43BBEB6E:03x}",
                    "T1_to_T3_rows": (0x43BBEF32 - 0x43BBEB6E) / STRIDE},
        "writers_obj_2b4": writers_2b4(a7),
        "a6000_entry_hits": a6.count(a7[ENTRY - BASE:ENTRY - BASE + 24]),
        "limits": [
            "Estatico: sin firmware ejecutado, sin camara, sin flasheo.",
            ("La base calculada por add-pc cae 2 B antes de la alineacion natural; "
             "ambas lecturas se documentan y la correcta queda NO_VERIFICADA sin runtime."),
            ("No se atribuye el escritor de obj+0x2b4 a esta clase: hay varios str a +0x2b4 "
             "en el blob y la identidad del objeto no se puede resolver estaticamente aqui."),
            "La semantica de los campos +0x14/+0x18 y su relacion con el silent siguen NO_VERIFICADAS.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print("computed", {k: hex(v) for k, v in computed.items()})
    print("T3->T2 rows", data["spacing"]["T3_to_T2_rows"])
    print("T1->T3 rows", data["spacing"]["T1_to_T3_rows"])
    print("writers +0x2b4", len(data["writers_obj_2b4"]))
    print("A6000 entry hits", data["a6000_entry_hits"])


if __name__ == "__main__":
    main()
