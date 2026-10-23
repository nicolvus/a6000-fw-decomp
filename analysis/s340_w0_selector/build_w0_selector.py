#!/usr/bin/env python3
"""S340 - carril B: `w0` es un selector de registro MMIO (6 canales, +0x30).

S334/S336 dejaron `w0` como "codigo de operacion" sin interpretar.  `0x43ada4d8`
es un tail-call a `0x436f74c0`, que hace `tbb [pc, r1]` con 6 casos y cada rama
lee `[base + 0x30]` de una base MMIO distinta:

* 0 -> `0xf3122300`, 1 -> `0xf3122200`, 2 -> `0xf3123300`, 3 -> `0xf3123200`,
  4 -> `0xfc0a3100`, 5 -> `0xfc0a4100`.

`0x436f605c` suma las lecturas seleccionadas por `w0` de T1 y de T2.  Los valores
medidos de `w0` son T1 {0,1}, T2 {2,3}, T3 4, de modo que T1 y T2 seleccionan
canales distintos y la suma combina dos lecturas.

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
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("w0_selector.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = True

SWITCH = 0x436F74C0
CASES = [(0x436F7734, 0xF3122300), (0x436F78E8, 0xF3122200),
         (0x436F7B20, 0xF3123300), (0x436F7CD4, 0xF3123200),
         (0x436F7F1C, 0xFC0A3100), (0x436F8164, 0xFC0A4100)]
SUM_FN = 0x436F605C
TABLES = {"T1": 0x43BBEB70, "T2": 0x43BBF2E8, "T3": 0x43BBEF30}
MODE_LIST = 0x43FEE370
CODES = [0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51, 0x0B]


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


def literal_value(blob: bytes, ldr: int) -> int:
    ins = next(iter(MD.disasm(raw(blob, ldr, 4), ldr)))
    lit = ((ldr + 4) & ~3) + ins.operands[1].mem.disp
    return u32(blob, lit)


def main() -> None:
    blob = A7S.read_bytes()
    switch = dis(blob, SWITCH, 0x40)
    table = list(raw(blob, 0x436F74CA, 6))
    cases = []
    for addr, expected in CASES:
        value = literal_value(blob, addr)
        load = next(iter(MD.disasm(raw(blob, addr + 2, 2), addr + 2)))
        offset = load.operands[1].mem.disp
        cases.append({"function": f"0x{addr:08x}", "literal": f"0x{value:08x}",
                      "matches": value == expected, "offset": f"0x{offset:x}",
                      "disasm": dis(blob, addr, 0x0A)})

    codes = [u32(blob, MODE_LIST + 4 * i) for i in range(34)]
    pos = {c: i for i, c in enumerate(codes)}
    per_code = {f"0x{c:02x}": {"position": pos[c],
                               "selectors": {name: u32(blob, base + 0x1C * pos[c])
                                             for name, base in TABLES.items()}}
                for c in CODES}

    data: dict[str, Any] = {
        "milestone": "S340",
        "title": "w0 es un selector de registro MMIO: tbb de 6 casos que leen "
                 "[base+0x30] (4) o [base+0x24] (2); T1/T2 eligen canales y "
                 "0x436f605c los suma",
        "base": f"0x{BASE:08x}",
        "firmware": {"a7s_fw320": {"sha256": sha256(A7S), "size": len(blob)}},
        "switch": {"address": f"0x{SWITCH:08x}", "disasm": switch,
                   "tbb_table": f"0x{0x436F74CA:08x}",
                   "tbb_bytes": table,
                   "case_count": 6,
                   "range_check": "cmp r1,#5; bhi -> log y 0"},
        "cases": cases,
        "sum": {"address": f"0x{SUM_FN:08x}", "disasm": dis(blob, SUM_FN, 0x40),
                "reads": "w0 de T1 y de T2", "combines": "suma"},
        "per_code": per_code,
        "verdicts": {
            "w0_is_mmio_selector": True,
            "selector_offsets": {"0x30": 4, "0x24": 2},
            "selector_bases": [f"0x{v:08x}" for _, v in CASES],
            "t1_channels": [0, 1],
            "t2_channels": [2, 3],
            "t3_selector": [4],
            "measured_quantity": "NO_VERIFICADO",
        },
        "corrections": [
            ("S334 etiqueto w0 como 'codigo de operacion'; es un selector de "
             "registro MMIO (0..5) y la rama lee [base+0x30]."),
        ],
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("No se sabe que mide cada canal (0xf3122200/2300/3200/3300, "
             "0xfc0a3100/4100) ni por que se suman dos lecturas."),
            "Los valores de w0 se miden en las tablas; su origen runtime no.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("tbb", [hex(x) for x in table])
    print("casos:", [(c["function"], c["literal"], c["matches"]) for c in cases])
    print("w0 por modo:", {k: v["selectors"] for k, v in per_code.items()})


if __name__ == "__main__":
    main()
